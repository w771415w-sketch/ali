    out = []
    seen = set()
    for p in paths:
        if p.exists():
            key = str(p.resolve())
            if key not in seen:
                seen.add(key)
                out.append(p)
    return out


def build_cumulative_dataset(
    models_root: str | Path,
    generation: str,
    delta_path: str | Path | None,
    output_path: str | Path | None = None,
    parent_generation: str | None = None,
) -> dict[str, Any]:
    root = Path(models_root)
    if output_path is None:
        output_path = root / "generations" / generation / "cumulative" / "train.jsonl"

    # For a brand-new generation the manifest may not exist yet. In that case
    # the caller can supply the active parent explicitly, which makes V5/V6
    # creation deterministic instead of depending on a pre-created manifest.
    historical: list[Path] = []
    parent = parent_generation
    if not parent:
        manifest = load_generation_manifest(root, generation)
        parent = _parent_from_manifest(manifest or {})
    if parent:
        parent_path = generation_train_path(root, parent)
        if parent_path and parent_path.exists():
            historical = [parent_path]
        else:
            historical = build_ancestor_train_paths(root, parent)

    historical = [p for p in historical if Path(p).resolve() != Path(output_path).resolve()]
    deltas = discover_delta_paths(root, generation)
    if delta_path:
        deltas.append(Path(delta_path))
    inputs: list[Path] = []
    seen_paths: set[str] = set()
    for p in [*historical, *deltas]:
        p = Path(p)
        key = str(p.resolve())
        if key not in seen_paths and p.exists():
            seen_paths.add(key)
            inputs.append(p)
    return merge_jsonl_unique(inputs, output_path)


@dataclass
class GenerationLineage:
    generation: str
    parent_generation: str
    ancestors: list[str]
    delta_dataset: str
    cumulative_dataset: str
    delta_dataset_hash: str
    cumulative_dataset_hash: str
    parent_checkpoint: str
    parent_checkpoint_hash: str
    merged_hf: str
    gguf: str
    run_id: str
    created_at: float
    schema_version: int = SCHEMA_VERSION

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def verify_lineage(models_root: str | Path, generation: str) -> dict[str, Any]:
    root = Path(models_root)
    manifest = load_generation_manifest(root, generation)
    errors: list[str] = []
    warnings: list[str] = []
    if not manifest:
        return {"generation": generation, "valid": False, "errors": ["generation_manifest_missing"]}
    parent = str(manifest.get("parent_generation") or manifest.get("base_version") or "")
    ancestors = build_ancestors(root, generation)
    if parent and parent not in ancestors:
        errors.append("parent_not_in_ancestor_chain")
    delta = manifest.get("delta_dataset") or {}
    cumulative = manifest.get("cumulative_dataset") or {}
    delta_path = _resolve_manifest_path(root, str(delta.get("path", ""))) if isinstance(delta, dict) and delta.get("path") else Path("")
    cumulative_path = _resolve_manifest_path(root, str(cumulative.get("path", ""))) if isinstance(cumulative, dict) and cumulative.get("path") else Path("")
    if not delta_path.exists():
        alt = discover_delta_paths(root, generation)
        if alt:
            delta_path = alt[0]
        else:
            warnings.append("delta_dataset_not_present")
    if not cumulative_path.exists():
        alt = generation_train_path(root, generation)
        if alt:
            cumulative_path = alt
        else:
            errors.append("cumulative_dataset_missing")
    if cumulative_path.exists() and cumulative.get("sha256"):
        actual = sha256_file(cumulative_path)
        if actual != str(cumulative.get("sha256")):
            errors.append("cumulative_dataset_hash_mismatch")
    artifact = manifest.get("artifacts") or {}
    hf_raw = artifact.get("merged_hf") or manifest.get("hf_dir") or ""
    hf = _resolve_manifest_path(root, str(hf_raw)) if hf_raw else Path("")
    if not hf.exists():
        errors.append("merged_hf_missing")
    gguf_raw = artifact.get("gguf_q4_k_m") or ""
    gguf = _resolve_manifest_path(root, str(gguf_raw)) if gguf_raw else Path("")
    if artifact.get("gguf_q4_k_m") and not gguf.exists():
        errors.append("gguf_missing")
    return {
        "generation": generation,
        "parent_generation": parent,
        "ancestors": ancestors,
        "delta_dataset": str(delta_path),
        "cumulative_dataset": str(cumulative_path),
        "merged_hf": str(hf),
        "gguf": str(gguf) if gguf_raw else "",
        "valid": not errors,
        "lineage_valid": bool(parent == "" or (parent in ancestors and len(ancestors) >= 2)),
        "dataset_valid": cumulative_path.exists() and not any("dataset" in e for e in errors),
        "errors": errors,
        "warnings": warnings,
    }
```

---

### `450/588` `backend/training/lora.py`

- **المسار الكامل:** `F:\1f\p\ALI_Studio_Pro_Design4_4.6.0\04_Adaptive_Hybrid\backend/training/lora.py`
- **الحجم:** 4454 بايت (4.3 KB)
- **الامتداد:** `.py`

```python
# -*- coding: utf-8 -*-
"""Small dependency-free LoRA implementation for ALI continued training.

LoRA is optional: ALI can train all parameters from scratch, or freeze the base
checkpoint and learn low-rank adapters for inexpensive incremental updates.
"""
from __future__ import annotations
from pathlib import Path
from typing import Iterable
import json
import torch
from torch import nn

class LoRALinear(nn.Module):
    def __init__(self, base: nn.Linear, rank: int = 8, alpha: float = 16.0, dropout: float = 0.0):
        super().__init__()
        if rank < 1: raise ValueError("LoRA rank must be >= 1")
        self.base = base
        self.rank = int(rank)
        self.alpha = float(alpha)
        self.scale = self.alpha / self.rank
        self.dropout = nn.Dropout(dropout)
        self.lora_A = nn.Parameter(torch.empty(self.rank, base.in_features))
        self.lora_B = nn.Parameter(torch.zeros(base.out_features, self.rank))
        nn.init.kaiming_uniform_(self.lora_A, a=5**0.5)
        for p in self.base.parameters(): p.requires_grad = False
    def forward(self, x):
        y = self.base(x)
        update = self.dropout(x) @ self.lora_A.t() @ self.lora_B.t()
        return y + update * self.scale
    def merge(self):
        with torch.no_grad():
            self.base.weight.add_(self.lora_B @ self.lora_A * self.scale)
        return self.base

def apply_lora(model: nn.Module, rank: int = 8, alpha: float = 16.0, dropout: float = 0.05,
               targets: Iterable[str] = ("q_proj", "k_proj", "v_proj", "o_proj", "gate_proj", "up_proj", "down_proj")) -> list[str]:
    targets = tuple(targets)
    replaced = []
    for parent_name, parent in list(model.named_modules()):
        for child_name, child in list(parent.named_children()):
            if isinstance(child, nn.Linear) and (child_name in targets or any(child_name.endswith(t) for t in targets)):
                wrapped = LoRALinear(child, rank, alpha, dropout)
                setattr(parent, child_name, wrapped)
                replaced.append((f"{parent_name}.{child_name}" if parent_name else child_name))
    if not replaced: raise ValueError("No target Linear layers found for LoRA")
    # Keep embeddings and lm_head frozen by default as part of the base model.
    for n,p in model.named_parameters():
        if "lora_A" not in n and "lora_B" not in n: p.requires_grad = False
    return replaced

def lora_parameters(model: nn.Module):
    return [p for n,p in model.named_parameters() if ("lora_A" in n or "lora_B" in n) and p.requires_grad]

def save_lora_adapter(model: nn.Module, out_dir: str | Path, metadata: dict | None = None) -> Path:
    out=Path(out_dir); out.mkdir(parents=True,exist_ok=True)
    state={n:p.detach().cpu().contiguous() for n,p in model.state_dict().items() if "lora_A" in n or "lora_B" in n}
    if not state: raise ValueError("model has no LoRA adapter parameters")
    try:
        from safetensors.torch import save_file
        save_file(state,str(out/'adapter_model.safetensors'),metadata={'format':'pt','source':'ALI Studio LoRA'})
    except Exception:
        torch.save(state,out/'adapter_model.pt')
    (out/'adapter_config.json').write_text(json.dumps(metadata or {},ensure_ascii=False,indent=2),encoding='utf-8')
    return out

def merge_lora(model: nn.Module) -> int:
    merged=0
    def rec(parent):
        nonlocal merged
        for name, child in list(parent.named_children()):
            if isinstance(child,LoRALinear):
                setattr(parent,name,child.merge()); merged+=1
            else: rec(child)
    rec(model)
    return merged

def load_lora_adapter(model: nn.Module, adapter_dir: str | Path) -> nn.Module:
    """Load previously trained ALI LoRA tensors into an already-wrapped model."""
    p=Path(adapter_dir)
    state_path=p/'adapter_model.safetensors'
    if state_path.exists():
        from safetensors.torch import load_file
        state=load_file(str(state_path),device='cpu')
    elif (p/'adapter_model.pt').exists():
        state=torch.load(p/'adapter_model.pt',map_location='cpu',weights_only=False)
    else:
        raise FileNotFoundError(f'LoRA adapter not found in {p}')
    current=model.state_dict()
    missing=[]
    for k,v in state.items():
        if k in current: current[k].copy_(v)
        else: missing.append(k)
    if missing: raise ValueError(f'Unknown LoRA keys: {missing[:5]}')
    model.load_state_dict(current,strict=False)
    return model
```

---

### `451/588` `backend/training/manifest.py`

- **المسار الكامل:** `F:\1f\p\ALI_Studio_Pro_Design4_4.6.0\04_Adaptive_Hybrid\backend/training/manifest.py`
- **الحجم:** 851 بايت (0.8 KB)
- **الامتداد:** `.py`

```python
# -*- coding: utf-8 -*-
from __future__ import annotations
from pathlib import Path
import hashlib,json,time
def sha256_file(path:str|Path,chunk:int=1024*1024)->str:
    h=hashlib.sha256(); p=Path(path)
    with p.open('rb') as f:
        while True:
            b=f.read(chunk)
            if not b: break
            h.update(b)
    return h.hexdigest()
def dataset_manifest(paths,extra=None):
    items=[]
    for raw in paths:
        p=Path(raw)
        if p.exists() and p.is_file(): items.append({"path":str(p),"size":p.stat().st_size,"sha256":sha256_file(p)})
    return {"kind":"dataset","created_at":time.time(),"files":items,"extra":extra or {}}
def write_manifest(path,data):
    p=Path(path); p.parent.mkdir(parents=True,exist_ok=True); p.write_text(json.dumps(data,ensure_ascii=False,indent=2,sort_keys=True),encoding='utf-8'); return p
```

---

### `452/588` `backend/training/pipeline.py`

- **المسار الكامل:** `F:\1f\p\ALI_Studio_Pro_Design4_4.6.0\04_Adaptive_Hybrid\backend/training/pipeline.py`
- **الحجم:** 18863 بايت (18.4 KB)
- **الامتداد:** `.py`

```python
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
```

---

### `453/588` `backend/training/scaling.py`

- **المسار الكامل:** `F:\1f\p\ALI_Studio_Pro_Design4_4.6.0\04_Adaptive_Hybrid\backend/training/scaling.py`
- **الحجم:** 2869 بايت (2.8 KB)
- **الامتداد:** `.py`

```python
# -*- coding: utf-8 -*-
"""Model-size registry and hardware-neutral training estimates."""
from __future__ import annotations
from dataclasses import dataclass, asdict
from typing import Dict, Any

@dataclass(frozen=True)
class ScaleProfile:
    name: str
    hidden_size: int
    intermediate_size: int
    layers: int
    heads: int
    vocab_size: int
    context: int
    target_params: int
    note: str

PROFILES = {
    "micro": ScaleProfile("micro", 192, 768, 4, 6, 4096, 256, 1_000_000, "P50 smoke tests and tokenizer/bootstrap validation"),
    "small": ScaleProfile("small", 256, 1024, 6, 8, 8192, 384, 10_000_000, "P50 local research model"),
    "medium": ScaleProfile("medium", 512, 2048, 12, 8, 16000, 1024, 100_000_000, "strong workstation / server"),
    "large": ScaleProfile("large", 1024, 4096, 24, 16, 32000, 2048, 500_000_000, "multi-GPU target"),
    "xlarge": ScaleProfile("xlarge", 2048, 8192, 32, 32, 64000, 4096, 2_000_000_000, "cluster-scale research target"),
}

def get(name: str) -> ScaleProfile:
    if name not in PROFILES:
        raise KeyError(f"unknown scale profile: {name}")
    return PROFILES[name]

def estimated_param_count(p: ScaleProfile) -> int:
    h, i, l, v = p.hidden_size, p.intermediate_size, p.layers, p.vocab_size
    return int(v*h*2 + l*(4*h*h + 3*h*i + 4*h))

def estimate_memory_gb(params: int, dtype_bytes: float = 4.0, optimizer_multiplier: float = 8.0,
                       gradients: bool = True, activation_factor: float = 1.5) -> float:
    """Conservative planning estimate; not a profiler measurement."""
    base = params * (dtype_bytes + (dtype_bytes if gradients else 0) + optimizer_multiplier) / (1024**3)
    return base * activation_factor

def build_training_plan(name: str, hardware: Any) -> Dict[str, Any]:
    p = get(name)
    params = estimated_param_count(p)
    ram = float(getattr(hardware, "ram_gb", 0) or 0)
    vram = float(getattr(hardware, "vram_gb", 0) or 0)
    cpu_threads = int(getattr(hardware, "cpu_cores", 1) or 1)
    legacy = bool(getattr(hardware, "cuda_capability", None) and tuple(hardware.cuda_capability) < (6, 0))
    fits_ram = estimate_memory_gb(params) <= max(0.5, ram * 0.55)
    fits_vram = estimate_memory_gb(params, dtype_bytes=2.0) <= max(0.5, vram * 0.65) if vram else False
    return {
        "profile": asdict(p),
        "estimated_parameters": params,
        "estimated_training_memory_gb": round(estimate_memory_gb(params), 2),
        "hardware_ram_gb": ram,
        "hardware_vram_gb": vram,
        "fits_2gb_vram": bool(fits_vram and vram <= 2.1),
        "fits_ram_estimate": fits_ram,
        "strategy": "CPU-first" if vram < 3 or legacy else "GPU/CPU adaptive",
        "recommended_cpu_threads": min(6, max(1, cpu_threads - 2)),
        "recommendation": "usable-bootstrap" if fits_ram else "requires-more-memory-or-smaller-profile",
    }
```

---

### `454/588` `backend/training/tool_calling.py`

- **المسار الكامل:** `F:\1f\p\ALI_Studio_Pro_Design4_4.6.0\04_Adaptive_Hybrid\backend/training/tool_calling.py`
- **الحجم:** 1849 بايت (1.8 KB)
- **الامتداد:** `.py`

```python
# -*- coding: utf-8 -*-
"""Build deterministic tool-calling SFT examples from ALI's registered tools."""
from __future__ import annotations
from pathlib import Path
import json, hashlib
from typing import Iterable, Mapping, Any

def _hash(obj: Any) -> str:
    raw=json.dumps(obj,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode('utf-8')
    return hashlib.sha256(raw).hexdigest()

def build_tool_calling_dataset(tools: Iterable[Mapping[str,Any]], out: str|Path, bilingual: bool=True)->dict:
    rows=[]
    for tool in tools:
        name=str(tool.get('name') or '')
        if not name: continue
        schema=tool.get('input_schema') or {'type':'object','properties':{}}
        description=str(tool.get('description') or '')
        prompts=[f"Use the {name} tool when appropriate.",f"How should ALI call {name}?" if bilingual else f"Call {name} when needed."]
        if bilingual:
            prompts += [f"استخدم أداة {name} عندما تكون مطلوبة.",f"متى يستدعي ALI الأداة {name}؟"]
        for prompt in prompts:
            answer=json.dumps({'tool':name,'arguments':{}},ensure_ascii=False,separators=(',',':'))
            row={'id':_hash([name,prompt]),'messages':[{'role':'system','content':'You are ALI. Use tools only when needed and follow their schemas.'},{'role':'user','content':prompt},{'role':'assistant','content':answer}], 'tool_name':name,'tool_schema':schema,'description':description}
            rows.append(row)
    p=Path(out); p.parent.mkdir(parents=True,exist_ok=True)
    seen=set(); kept=[]
    with p.open('w',encoding='utf-8') as f:
        for r in rows:
            if r['id'] in seen: continue
            seen.add(r['id']); kept.append(r); f.write(json.dumps(r,ensure_ascii=False)+'\n')
    return {'output':str(p),'records':len(kept),'unique_ids':len(seen)}
```

---

### `455/588` `backend/training/trainer.py`

- **المسار الكامل:** `F:\1f\p\ALI_Studio_Pro_Design4_4.6.0\04_Adaptive_Hybrid\backend/training/trainer.py`
- **الحجم:** 24220 بايت (23.7 KB)
- **الامتداد:** `.py`

```python
# -*- coding: utf-8 -*-
"""Real PyTorch trainer for ALI AI 2.0.

Supports:
- causal pretraining and assistant-only chat SFT
- dependency-light LoRA
- deterministic checkpoints + RNG state
- safe resume with compatibility checks
- optional CUDA AMP
- optional torch.distributed/DDP when launched by torchrun
- CPU-first operation for legacy/P50 hardware
"""
from __future__ import annotations

from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Optional, Dict, Any
import json
import math
import os
import random
import threading
import time
import re

import torch
from torch.utils.data import Dataset, DataLoader, Subset
try:
    from torch.utils.data.distributed import DistributedSampler
except Exception:
    DistributedSampler = None

from model.ali_lm import ALIForCausalLM
from training.curriculum import CurriculumSchedule


@dataclass
class TrainConfig:
    epochs: int = 1
    batch_size: int = 1
    grad_accum: int = 16
    learning_rate: float = 3e-4
    weight_decay: float = 0.1
    warmup_steps: int = 20
    max_steps: int = 0
    save_every: int = 100
    eval_every: int = 100
    max_seq_len: int = 512
    seed: int = 42
    device: str = "cpu"
    gradient_checkpointing: bool = True
    max_grad_norm: float = 1.0
    train_mode: str = "full"
    lora_rank: int = 8
    lora_alpha: float = 16.0
    lora_dropout: float = 0.05
    amp: bool = True
    dtype: str = "float16"  # float16 | bfloat16 (CUDA)
    cpu_amp: bool = False
    cpu_threads: int = 0
    use_compile: bool = False
    dataset_mode: str = "causal"
    curriculum: bool = True
    distributed_backend: str = "auto"  # auto | none | gloo | nccl
    world_size: int = 1

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class JsonlTextDataset(Dataset):
    def __init__(self, path: str | Path, tokenizer, max_seq_len: int):
        self.rows: list[dict[str, str]] = []
        self.tok = tokenizer
        self.max_len = int(max_seq_len)
        self.path = Path(path)
        if not self.path.exists():
            raise FileNotFoundError(self.path)
        with self.path.open(encoding="utf-8", errors="replace") as fh:
            for line in fh:
                try:
                    x = json.loads(line)
                except Exception:
                    continue
                if isinstance(x, dict):
                    text = x.get("text", "")
                    if not text and isinstance(x.get("messages"), list):
                        parts = []
                        for m in x["messages"]:
                            if not isinstance(m, dict):
                                continue
                            role = str(m.get("role", "user"))
                            content = str(m.get("content", ""))
                            parts.append(f"<|{role}|>\n{content}<|eot|>\n")
                        text = "".join(parts)
                    rid = str(x.get("id", ""))
                else:
                    text, rid = str(x), ""
                if str(text).strip():
                    self.rows.append({"id": rid, "text": str(text)})
        if not self.rows:
            raise ValueError(f"empty dataset: {self.path}")

    def __len__(self):
        return len(self.rows)

    def text_row(self, i: int):
        return self.rows[i]

    def __getitem__(self, i: int):
        ids = self.tok.encode(self.rows[i]["text"], add_bos=True, add_eos=True)[:self.max_len]
        x = torch.tensor(ids, dtype=torch.long)
        return {"input_ids": x, "labels": x.clone()}


class JsonlChatDataset(JsonlTextDataset):
    """Assistant-only SFT labels; prompt/context tokens are ignored by CE."""

    _ROLE_RE = re.compile(
        r"<\|(?P<role>system|user|assistant|tool)\|>\n"
        r"(?P<content>.*?)(?=\n<\|(?:system|user|assistant|tool)\|>|\n<\|eot\|>|\Z)",
        re.S,
    )

    def __getitem__(self, i: int):
        text = self.rows[i]["text"]
        matches = list(self._ROLE_RE.finditer(text))
        if not matches:
            ids = self.tok.encode(text, add_bos=True, add_eos=True)[:self.max_len]
            x = torch.tensor(ids, dtype=torch.long)
            return {"input_ids": x, "labels": x.clone()}

        input_ids = [self.tok.bos_id]
        labels = [-100]
        eot_ids = self.tok.encode("<|eot|>\n", add_bos=False, add_eos=False)

        for match in matches:
            role = match.group("role")
            content = match.group("content").strip("\n")
            head = self.tok.encode(f"<|{role}|>\n", add_bos=False, add_eos=False)
            body = self.tok.encode((content + "\n") if content else "", add_bos=False, add_eos=False)
            input_ids.extend(head); labels.extend([-100] * len(head))
            input_ids.extend(body); labels.extend(body if role == "assistant" else [-100] * len(body))
            input_ids.extend(eot_ids); labels.extend(eot_ids if role == "assistant" else [-100] * len(eot_ids))

        labeled = [i for i, v in enumerate(labels) if v != -100]
        if not labeled:
            ids = self.tok.encode(text, add_bos=True, add_eos=True)[:self.max_len]
            return {"input_ids": torch.tensor(ids), "labels": torch.tensor(ids)}

        if len(input_ids) > self.max_len:
            end = min(len(input_ids), labeled[-1] + 1)
            start = max(0, end - self.max_len)
            input_ids, labels = input_ids[start:end], labels[start:end]

        # Keep a target whenever possible.
        if not any(v != -100 for v in labels):
            ids = self.tok.encode(text, add_bos=True, add_eos=True)[:self.max_len]
            input_ids, labels = ids, ids

        return {
            "input_ids": torch.tensor(input_ids[:self.max_len], dtype=torch.long),
            "labels": torch.tensor(labels[:self.max_len], dtype=torch.long),
        }


def collate(batch, pad_id: int):
    n = max(x["input_ids"].numel() for x in batch)
    ids, labels, masks = [], [], []
    for item in batch:
        k = item["input_ids"]
        pad = n - k.numel()
        ids.append(torch.cat([k, torch.full((pad,), pad_id, dtype=torch.long)]))
        labels.append(torch.cat([item["labels"], torch.full((pad,), -100, dtype=torch.long)]))
        masks.append(torch.cat([torch.ones(k.numel(), dtype=torch.long), torch.zeros(pad, dtype=torch.long)]))
    return {
        "input_ids": torch.stack(ids),
        "labels": torch.stack(labels),
        "attention_mask": torch.stack(masks),
    }


def _set_seed(seed: int):
    random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)


def _rng_state():
    state = {"python": random.getstate(), "torch": torch.get_rng_state()}
    if torch.cuda.is_available():
        state["cuda"] = torch.cuda.get_rng_state_all()
    return state


def _restore_rng(state):