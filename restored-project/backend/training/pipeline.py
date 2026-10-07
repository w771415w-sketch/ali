# -*- coding: utf-8 -*-
"""ALI AI 2.0 progressive training pipeline.

One stable control plane exposes explicit stages:
    tokenizer -> base -> sft -> lora -> evaluate/export

Each run keeps lineage (base checkpoint, dataset, tokenizer), so a model trained
on a stronger workstation can be loaded by the same registry/UI later.
"""
from __future__ import annotations

from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Any, Callable
import json
import os
import time
import uuid
import hashlib

from model.ali_lm import AliConfig, ALIForCausalLM, load_state, save_hf_checkpoint
from model.registry import ModelRegistry
from model.artifacts import ArtifactManifest, sha256_path
from tokenizer.manager import TokenizerManager
from tokenizer.spm import AliTokenizer
from training.trainer import Trainer, TrainConfig
from training.evaluator import evaluate_model
from training.scaling import get as get_scale


@dataclass
class PipelineConfig:
    name: str = "ALI"
    stage: str = "base"  # base | sft | lora
    scale: str = "micro"
    train_path: str = ""
    validation_path: str = ""
    tokenizer_inputs: list[str] | None = None
    tokenizer_vocab_size: int = 4096
    base_checkpoint: str = ""
    resume_checkpoint: str = ""
    max_steps: int = 0
    epochs: int = 1
    max_seq_len: int = 256
    batch_size: int = 1
    grad_accum: int = 16
    learning_rate: float = 3e-4
    device: str = "cpu"
    lora_rank: int = 8
    lora_alpha: float = 16.0
    lora_dropout: float = .05
    curriculum: bool = True
    distributed_backend: str = "auto"
    world_size: int = 1

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class TrainingPipeline:
    VALID_STAGES = {"base", "sft", "lora"}

    def __init__(self, root: str | Path, hardware: Any | None = None):
        self.root = Path(root)
        self.registry = ModelRegistry(self.root / "models" / "models.sqlite3")
        self.tokenizers = TokenizerManager(self.root)
        self.runs = self.root / "models" / "runs"
        self.runs.mkdir(parents=True, exist_ok=True)
        self.hardware = hardware

    def prepare_tokenizer(self, cfg: PipelineConfig, *, force: bool = False) -> dict[str, Any]:
        inputs = cfg.tokenizer_inputs or [cfg.train_path]
        return self.tokenizers.train(inputs, vocab_size=cfg.tokenizer_vocab_size, name=cfg.name, force=force)

    def _config_from_checkpoint(self, checkpoint: Path) -> AliConfig | None:
        candidate = checkpoint / "config.json" if checkpoint.is_dir() else checkpoint.parent / "config.json"
        if not candidate.exists():
            return None
        try:
            return AliConfig.from_dict(json.loads(candidate.read_text(encoding="utf-8")))
        except Exception:
            return None

    def new_model(self, cfg: PipelineConfig, tokenizer_vocab_size: int) -> ALIForCausalLM:
        if cfg.base_checkpoint:
            base = Path(cfg.base_checkpoint)
            if not base.is_absolute():
                base = (self.root / base).resolve()
            else:
                base = base.resolve()
            if base.is_dir() and (base / "checkpoint.pt").exists():
                blob = __import__("torch").load(base / "checkpoint.pt", map_location="cpu", weights_only=False)
                model = ALIForCausalLM(AliConfig.from_dict(blob["config"]))
                model.load_state_dict(blob["model"], strict=True)
                return model
            hf = base / "model.safetensors" if base.is_dir() else base
            config = self._config_from_checkpoint(base)
            if config is None:
                raise ValueError("base_checkpoint must contain config.json")
            model = ALIForCausalLM(config)
            if hf.exists():
                load_state(model, hf, "cpu")
                return model
            raise FileNotFoundError(f"No model weights found in {base}")

        p = get_scale(cfg.scale)
        context = min(int(cfg.max_seq_len), int(p.context))
        model_cfg = AliConfig(
            vocab_size=int(tokenizer_vocab_size),
            hidden_size=p.hidden_size,
            intermediate_size=p.intermediate_size,
            num_hidden_layers=p.layers,
            num_attention_heads=p.heads,
            num_key_value_heads=p.heads,
            max_position_embeddings=context,
        )
        return ALIForCausalLM(model_cfg)

    def run(self, cfg: PipelineConfig, progress: Callable[[dict[str, Any]], None] | None = None) -> dict[str, Any]:
        if cfg.stage not in self.VALID_STAGES:
            raise ValueError(f"unknown training stage: {cfg.stage}")
        train_path = Path(cfg.train_path)
        if not train_path.is_absolute():
            train_path = (self.root / train_path).resolve()
        if not train_path.exists():
            raise FileNotFoundError(str(train_path))
        cfg = PipelineConfig(**{**cfg.to_dict(), "train_path": str(train_path)})
        if cfg.validation_path:
            validation_path = Path(cfg.validation_path)
            if not validation_path.is_absolute():
                validation_path = (self.root / validation_path).resolve()
            cfg = PipelineConfig(**{**cfg.to_dict(), "validation_path": str(validation_path)})
        if cfg.stage in {"sft", "lora"} and not cfg.base_checkpoint:
            raise ValueError(f"{cfg.stage} requires base_checkpoint so the lineage stays explicit")

        rank = int(os.environ.get("RANK", "0"))
        world = int(os.environ.get("WORLD_SIZE", str(max(1, int(cfg.world_size)))))
        run_id = time.strftime("%Y%m%d-%H%M%S") + "-" + uuid.uuid4().hex[:6]
        if world > 1:
            # Derive one stable run id from the distributed job configuration so
            # independently spawned ranks never create different run folders.
            seed = json.dumps({
                "stage": cfg.stage, "scale": cfg.scale, "train": str(Path(cfg.train_path).resolve()),
                "validation": str(Path(cfg.validation_path).resolve()) if cfg.validation_path else "",
                "base": str(((self.root / Path(cfg.base_checkpoint)).resolve() if not Path(cfg.base_checkpoint).is_absolute() else Path(cfg.base_checkpoint).resolve())) if cfg.base_checkpoint else "",
                "master": os.environ.get("MASTER_ADDR", ""), "port": os.environ.get("MASTER_PORT", ""),
            }, sort_keys=True, ensure_ascii=False)
            run_id = "dist-" + hashlib.sha256(seed.encode("utf-8")).hexdigest()[:14]
        run_dir = self.runs / run_id
        run_dir.mkdir(parents=True, exist_ok=True)

        def emit(stage: str, status: str, **extra: Any) -> None:
            payload = {"run_id": run_id, "stage": stage, "status": status, **extra}
            if rank == 0:
                (run_dir / "latest_event.json").write_text(
                    json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8"
                )
                if progress:
                    progress(payload)

        if cfg.stage in {"sft", "lora"} and cfg.base_checkpoint:
            # Continuation training must use the tokenizer that produced the base model.
            # Re-training a tokenizer here can change vocab IDs and break embedding compatibility.
            base = Path(cfg.base_checkpoint)
            if not base.is_absolute():
                base = (self.root / base).resolve()
            else:
                base = base.resolve()
            tokenizer_candidates = [
                base / "tokenizer.model",
                base / "hf" / "tokenizer.model",
                base / "merged_hf" / "tokenizer.model",
                base.parent / "tokenizer.model",
            ]
            tok_model = next((p for p in tokenizer_candidates if p.exists()), None)
            if tok_model is not None:
                tokenizer_dir = tok_model.parent
                tok = {
                    "reused": True,
                    "name": cfg.name,
                    "version": tokenizer_dir.name,
                    "path": str(tokenizer_dir),
                    "tokenizer": str(tok_model),
                    "vocab_size": AliTokenizer(tok_model).vocab_size,
                    "source": "base-checkpoint",
                }
            elif world > 1 and rank != 0:
                raise FileNotFoundError("Continuation training requires the base tokenizer artifact")
            else:
                tok = self.prepare_tokenizer(cfg)
                tokenizer_dir = Path(tok["path"])
        elif world > 1 and rank != 0:
            deadline = time.time() + 900
            tok = None
            while time.time() < deadline:
                tok = self.tokenizers.find_by_corpus(self.tokenizers.corpus_hash([cfg.train_path]), cfg.name)
                if tok:
                    break
                time.sleep(0.5)
            if not tok:
                raise TimeoutError("Timed out waiting for rank 0 to publish the tokenizer artifact")
            tokenizer_dir = Path(tok["path"])
        else:
            tok = self.prepare_tokenizer(cfg)
            tokenizer_dir = Path(tok["path"])
        tokenizer = AliTokenizer(tokenizer_dir / "tokenizer.model")
        emit("tokenizer", "ready", result=tok)

        model = self.new_model(cfg, tokenizer.vocab_size)
        dataset_mode = "chat" if cfg.stage in {"sft", "lora"} else "causal"
        train_mode = "lora" if cfg.stage == "lora" else "full"

        train_cfg = TrainConfig(
            epochs=max(1, int(cfg.epochs)),
            batch_size=max(1, int(cfg.batch_size)),
            grad_accum=max(1, int(cfg.grad_accum)),
            learning_rate=float(cfg.learning_rate),
            max_steps=max(0, int(cfg.max_steps)),
            max_seq_len=min(int(cfg.max_seq_len), model.config.max_position_embeddings),
            device=cfg.device,
            train_mode=train_mode,
            lora_rank=int(cfg.lora_rank),
            lora_alpha=float(cfg.lora_alpha),
            lora_dropout=float(cfg.lora_dropout),
            dataset_mode=dataset_mode,
            curriculum=bool(cfg.curriculum),
            distributed_backend=cfg.distributed_backend,
            world_size=max(1, int(cfg.world_size)),
        )
        emit("training", "started", train_config=train_cfg.to_dict(), training_stage=cfg.stage, scale=cfg.scale)

        trainer = Trainer(
            model,
            tokenizer,
            cfg.train_path,
            cfg.validation_path or None,
            train_cfg,
            run_dir / "checkpoints",
        )
        if cfg.resume_checkpoint:
            emit("training", "resume", checkpoint=cfg.resume_checkpoint)
            trainer.resume(cfg.resume_checkpoint)

        result = trainer.train(lambda ev: emit("training", "progress", event=ev))
        final = Path(result["checkpoint"])
        if trainer.distributed:
            import torch
            torch.distributed.barrier()
        if trainer.distributed and rank != 0:
            runtime_hf = final / ("merged_hf" if cfg.stage == "lora" else "hf")
            return {
                "run_id": run_id, "rank": rank, "checkpoint": str(final),
                "hf_dir": str(runtime_hf), "adapter": str(final / "adapter") if cfg.stage == "lora" else "",
                "training": result, "status": "worker_complete",
            }

        unwrapped = trainer.model.module if hasattr(trainer.model, "module") else trainer.model
        hf_dir = final / "hf"
        adapter_dir = final / "adapter"
        merged_hf_dir = final / "merged_hf"
        emit("export", "started", checkpoint=str(final))
        kca_registry_path = self.root / "control_plane" / "function_registry.json"
        export_meta = {
            "run_id": run_id,
            "stage": cfg.stage,
            "dataset_hash": sha256_path(cfg.train_path),
            "tokenizer_hash": sha256_path(tokenizer_dir),
            "pipeline_config": cfg.to_dict(),
            "kca_schema": "3.0",
            "kca_registry_hash": sha256_path(kca_registry_path) if kca_registry_path.exists() else None,
            "result": result,
        }
        if cfg.stage != "lora":
            save_hf_checkpoint(unwrapped, tokenizer_dir, hf_dir, export_meta)
            hf_manifest = ArtifactManifest(
                artifact_id=f"{cfg.name}:hf:{run_id}", artifact_type="base",
                name=cfg.name, version=run_id, source="training-export", path=str(hf_dir),
                lineage={"base_checkpoint": cfg.base_checkpoint, "dataset_hash": sha256_path(cfg.train_path), "tokenizer_hash": sha256_path(tokenizer_dir), "stage": cfg.stage},
                training=train_cfg.to_dict(), metadata={"run_id": run_id, "stage": cfg.stage},
            )
            hf_manifest.finalize(hf_dir); hf_manifest.write(hf_dir / "manifest.json")
        else:
            # Preserve both useful LoRA forms: a lightweight adapter and a
            # merged, ordinary ALI model that the current inference runtime can load.
            from training.lora import merge_lora, save_lora_adapter
            if adapter_dir.exists():
                save_lora_adapter(unwrapped, adapter_dir, {
                    **export_meta,
                    "rank": cfg.lora_rank,
                    "alpha": cfg.lora_alpha,
                    "dropout": cfg.lora_dropout,
                })
            merged_count = merge_lora(unwrapped)
            save_hf_checkpoint(unwrapped, tokenizer_dir, merged_hf_dir, {
                **export_meta,
                "merged_lora_layers": merged_count,
            })
            # Write the runtime-facing manifest inside the actual HF artifact.
            # The hash function excludes manifest.json, so verification is stable.
            merged_runtime_manifest = ArtifactManifest(
                artifact_id=f"{cfg.name}:hf-merged:{run_id}", artifact_type="merged",
                name=cfg.name, version=f"{run_id}-merged", source="lora-merge",
                path=str(merged_hf_dir),
                lineage={"base_checkpoint": cfg.base_checkpoint, "dataset_hash": sha256_path(cfg.train_path), "tokenizer_hash": sha256_path(tokenizer_dir), "stage": "lora"},
                training=train_cfg.to_dict(), metadata={"run_id": run_id, "merged_lora_layers": merged_count},
            )
            merged_runtime_manifest.finalize(merged_hf_dir); merged_runtime_manifest.write(merged_hf_dir / "manifest.json")

        evaluation: dict[str, Any] = {"loss": result.get("val_loss")}
        if cfg.validation_path and Path(cfg.validation_path).exists():
            try:
                evaluation = evaluate_model(
                    unwrapped,
                    tokenizer,
                    cfg.validation_path,
                    cfg.device,
                )
            except Exception as exc:
                evaluation = {**evaluation, "error": str(exc)}

        lineage = {
            "base_checkpoint": cfg.base_checkpoint,
            "resume_checkpoint": cfg.resume_checkpoint,
            "dataset_hash": sha256_path(cfg.train_path),
            "tokenizer_hash": sha256_path(tokenizer_dir),
            "scale": cfg.scale,
            "stage": cfg.stage,
        }
        artifact = ArtifactManifest(
            artifact_id=f"{cfg.name}:candidate:{run_id}",
            artifact_type="adapter" if cfg.stage == "lora" else "base",
            name=cfg.name,
            version=run_id,
            source="training-pipeline",
            path=str(final),
            lineage=lineage,
            training=train_cfg.to_dict(),
            evaluation=evaluation,
            compatibility={
                "hf_dir": str(hf_dir) if hf_dir.exists() else "",
                "merged_hf_dir": str(merged_hf_dir) if merged_hf_dir.exists() else "",
                "adapter_dir": str(adapter_dir) if adapter_dir.exists() else "",
            },
            metadata={"result": result, "stage": cfg.stage},
        )
        artifact.finalize(final)
        artifact.write(final / "manifest.json")

        if cfg.stage == "lora":
            self.registry.register(
                f"{cfg.name}-adapter", run_id,
                artifact_type="adapter", status="candidate",
                base_version=cfg.base_checkpoint,
                checkpoint=str(final),
                adapter=str(adapter_dir) if adapter_dir.exists() else "",
                dataset_hash=lineage["dataset_hash"],
                tokenizer_hash=lineage["tokenizer_hash"],
                artifact_hash=artifact.sha256,
                train_config=train_cfg.to_dict(), eval=evaluation,
            )
            if merged_hf_dir.exists():
                merged_manifest = ArtifactManifest(
                    artifact_id=f"{cfg.name}:merged:{run_id}",
                    artifact_type="merged", name=cfg.name, version=f"{run_id}-merged",
                    source="lora-merge", path=str(merged_hf_dir),
                    lineage={**lineage, "adapter_artifact": str(adapter_dir)},
                    training=train_cfg.to_dict(), evaluation=evaluation,
                    compatibility={"hf_dir": str(merged_hf_dir)},
                    metadata={"merged_lora_layers": True},
                )
                merged_manifest.finalize(merged_hf_dir)
                merged_manifest.write(merged_hf_dir / "manifest.json")
                self.registry.register(
                    cfg.name, f"{run_id}-merged",
                    artifact_type="merged", status="candidate",
                    base_version=cfg.base_checkpoint, checkpoint=str(final),
                    hf_dir=str(merged_hf_dir), dataset_hash=lineage["dataset_hash"],
                    tokenizer_hash=lineage["tokenizer_hash"], artifact_hash=merged_manifest.sha256,
                    train_config=train_cfg.to_dict(), eval=evaluation,
                )
        else:
            self.registry.register(
                cfg.name, run_id, artifact_type="base", status="candidate",
                base_version=cfg.base_checkpoint, checkpoint=str(final), hf_dir=str(hf_dir),
                dataset_hash=lineage["dataset_hash"], tokenizer_hash=lineage["tokenizer_hash"],
                artifact_hash=artifact.sha256, train_config=train_cfg.to_dict(), eval=evaluation,
            )

        runtime_hf = hf_dir if hf_dir.exists() else merged_hf_dir
        emit("complete", "success", checkpoint=str(final), hf_dir=str(runtime_hf) if runtime_hf.exists() else "", adapter=str(adapter_dir) if adapter_dir.exists() else "", evaluation=evaluation)
        return {
            "run_id": run_id,
            "checkpoint": str(final),
            "hf_dir": str(runtime_hf) if runtime_hf.exists() else "",
            "adapter": str(adapter_dir) if adapter_dir.exists() else "",
            "tokenizer": tok,
            "training": result,
            "evaluation": evaluation,
            "manifest": artifact.to_dict(),
        }
