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
    if not state:
        return
    random.setstate(state["python"])
    torch.set_rng_state(state["torch"])
    if torch.cuda.is_available() and "cuda" in state:
        torch.cuda.set_rng_state_all(state["cuda"])


def _configure_cpu(cfg: TrainConfig):
    if cfg.device != "cpu":
        return
    cores = os.cpu_count() or 4
    threads = int(cfg.cpu_threads) if cfg.cpu_threads and cfg.cpu_threads > 0 else max(1, cores - 2)
    torch.set_num_threads(max(1, threads))
    try:
        torch.set_num_interop_threads(1)
    except Exception:
        pass
    try:
        torch.set_float32_matmul_precision("high")
    except Exception:
        pass


def _unwrap(model):
    return model.module if hasattr(model, "module") else model


class Trainer:
    def __init__(
        self,
        model: ALIForCausalLM,
        tokenizer,
        train_path,
        val_path=None,
        cfg: TrainConfig | None = None,
        output_dir="checkpoints",
    ):
        self.cfg = cfg or TrainConfig()
        _configure_cpu(self.cfg)
        self.stop_event = threading.Event()
        self.output = Path(output_dir)
        self.output.mkdir(parents=True, exist_ok=True)

        ds_cls = JsonlChatDataset if self.cfg.dataset_mode.lower() == "chat" else JsonlTextDataset
        self.train_ds = ds_cls(train_path, tokenizer, self.cfg.max_seq_len)
        self.val_ds = None
        if val_path and Path(val_path).exists():
            self.val_ds = ds_cls(val_path, tokenizer, self.cfg.max_seq_len)

        self.device = torch.device(self.cfg.device)
        self.tokenizer = tokenizer
        self.distributed = False
        self.rank = 0
        self.world_size = 1
        self._init_distributed()
        self.model = model.to(self.device)
        self.model.gradient_checkpointing = self.cfg.gradient_checkpointing

        self.adapter_modules: list[str] = []
        if self.cfg.train_mode.lower() == "lora":
            from training.lora import apply_lora, lora_parameters
            self.adapter_modules = apply_lora(
                self.model,
                self.cfg.lora_rank,
                self.cfg.lora_alpha,
                self.cfg.lora_dropout,
            )
            trainable = lora_parameters(self.model)
        else:
            trainable = [p for p in self.model.parameters() if p.requires_grad]
        if not trainable:
            raise ValueError("No trainable parameters selected")

        if self.world_size > 1:
            if self.device.type != "cuda" or not self.distributed:
                raise RuntimeError("world_size > 1 currently requires initialized CUDA DDP")
            from torch.nn.parallel import DistributedDataParallel as DDP
            self.model = DDP(self.model, device_ids=[self.device.index], output_device=self.device.index)

        base_model = _unwrap(self.model)
        trainable = [p for p in base_model.parameters() if p.requires_grad]
        self.optimizer = torch.optim.AdamW(
            trainable,
            lr=self.cfg.learning_rate,
            weight_decay=self.cfg.weight_decay,
            foreach=(self.device.type == "cpu"),
        )

        estimated_updates = math.ceil(len(self.train_ds) / max(1, self.cfg.batch_size * self.cfg.grad_accum))
        self.total_updates = max(1, self.cfg.max_steps or estimated_updates * max(1, self.cfg.epochs))

        def lr_lambda(step):
            if self.cfg.warmup_steps and step < self.cfg.warmup_steps:
                return max(1e-6, (step + 1) / self.cfg.warmup_steps)
            progress = min(
                1.0,
                max(0.0, (step - self.cfg.warmup_steps) / max(1, self.total_updates - self.cfg.warmup_steps)),
            )
            return 0.5 * (1 + math.cos(math.pi * progress))

        self.scheduler = torch.optim.lr_scheduler.LambdaLR(self.optimizer, lr_lambda)
        self.global_step = 0
        self.micro_step = 0
        self.tokens_seen = 0
        self.samples_seen = 0
        self.best_val = float("inf")
        self.history: list[dict[str, Any]] = []

        if self.cfg.use_compile and hasattr(torch, "compile") and self.device.type == "cuda" and self.world_size == 1:
            try:
                self.model = torch.compile(self.model)
            except Exception:
                self.cfg.use_compile = False

    def _init_distributed(self):
        if self.cfg.world_size <= 1:
            return
        if not torch.distributed.is_available() or not torch.distributed.is_initialized():
            if not torch.cuda.is_available():
                raise RuntimeError("DDP requires CUDA in ALI AI 2.0")
            backend = self.cfg.distributed_backend
            if backend == "auto":
                backend = "nccl"
            if backend not in {"nccl", "gloo"}:
                raise ValueError(f"Unsupported distributed backend: {backend}")
            torch.distributed.init_process_group(backend=backend)
        self.distributed = True
        self.rank = int(os.environ.get("RANK", 0))
        self.world_size = int(os.environ.get("WORLD_SIZE", self.cfg.world_size))
        local_rank = int(os.environ.get("LOCAL_RANK", self.rank))
        if self.cfg.device == "cuda":
            torch.cuda.set_device(local_rank)
            self.cfg.device = f"cuda:{local_rank}"
            self.device = torch.device(self.cfg.device)

    def is_main_process(self) -> bool:
        return self.rank == 0

    def stop(self):
        self.stop_event.set()

    def _loader(self, ds, shuffle=True, indices=None):
        target = Subset(ds, indices) if indices is not None else ds
        sampler = None
        if self.distributed:
            sampler = DistributedSampler(target, num_replicas=self.world_size, rank=self.rank, shuffle=shuffle)
            shuffle = False
        return DataLoader(
            target,
            batch_size=self.cfg.batch_size,
            shuffle=shuffle,
            sampler=sampler,
            collate_fn=lambda b: collate(b, self.tokenizer.pad_id),
            num_workers=0,
            pin_memory=(self.device.type == "cuda"),
        )

    @torch.no_grad()
    def evaluate(self) -> float:
        if not self.val_ds:
            return float("nan")
        self.model.eval()
        total, count = 0.0, 0
        for batch in self._loader(self.val_ds, shuffle=False):
            batch = {k: v.to(self.device) for k, v in batch.items()}
            loss = self.model(**batch)["loss"]
            if loss is not None:
                total += float(loss.item())
                count += 1
        self.model.train()
        return total / max(1, count)

    def save_checkpoint(self, tag: str, run_meta: Optional[Dict[str, Any]] = None) -> Path:
        p = self.output / tag
        if p.exists() and self.is_main_process():
            # Never silently replace a completed checkpoint.
            if (p / "checkpoint.pt").exists():
                tag = f"{tag}-{int(time.time())}"
                p = self.output / tag
        if not self.is_main_process():
            return p
        p.mkdir(parents=True, exist_ok=True)

        model_state = {k: v.detach().cpu().contiguous() for k, v in _unwrap(self.model).state_dict().items()}
        payload = {
            "model": model_state,
            "optimizer": self.optimizer.state_dict(),
            "scheduler": self.scheduler.state_dict(),
            "rng": _rng_state(),
            "global_step": self.global_step,
            "micro_step": self.micro_step,
            "best_val": self.best_val,
            "tokens_seen": self.tokens_seen,
            "samples_seen": self.samples_seen,
            "history": self.history[-100:],
            "config": _unwrap(self.model).config.to_dict(),
            "train_config": self.cfg.to_dict(),
            "meta": run_meta or {},
        }
        torch.save(payload, p / "checkpoint.pt")

        try:
            from safetensors.torch import save_file
            save_file(
                model_state,
                str(p / "model.safetensors"),
                metadata={
                    "format": "pt",
                    "step": str(self.global_step),
                    "source": "ALI AI 2.0",
                    "train_mode": self.cfg.train_mode,
                },
            )
        except Exception:
            pass

        if self.cfg.train_mode.lower() == "lora":
            try:
                from training.lora import save_lora_adapter
                save_lora_adapter(
                    _unwrap(self.model),
                    p / "adapter",
                    {
                        "rank": self.cfg.lora_rank,
                        "alpha": self.cfg.lora_alpha,
                        "target_modules": self.adapter_modules,
                        "base_config": _unwrap(self.model).config.to_dict(),
                    },
                )
            except Exception:
                pass

        (p / "trainer_state.json").write_text(
            json.dumps(
                {
                    "global_step": self.global_step,
                    "micro_step": self.micro_step,
                    "best_val": self.best_val,
                    "tokens_seen": self.tokens_seen,
                    "samples_seen": self.samples_seen,
                    "config": self.cfg.to_dict(),
                    "meta": run_meta or {},
                },
                ensure_ascii=False,
                indent=2,
            ),
            encoding="utf-8",
        )
        return p

    def resume(self, checkpoint_dir: str | Path) -> None:
        p = Path(checkpoint_dir)
        blob = torch.load(p / "checkpoint.pt", map_location=self.device, weights_only=False)
        checkpoint_cfg = blob.get("config") or {}
        active_cfg = _unwrap(self.model).config.to_dict()
        for key in ("vocab_size", "hidden_size", "intermediate_size", "num_hidden_layers",
                    "num_attention_heads", "num_key_value_heads", "max_position_embeddings"):
            if key in checkpoint_cfg and checkpoint_cfg.get(key) != active_cfg.get(key):
                raise ValueError(f"checkpoint architecture mismatch for {key}: {checkpoint_cfg.get(key)} != {active_cfg.get(key)}")
        _unwrap(self.model).load_state_dict(blob["model"], strict=True)
        self.optimizer.load_state_dict(blob["optimizer"])
        self.scheduler.load_state_dict(blob["scheduler"])
        self.global_step = int(blob.get("global_step", 0))
        self.micro_step = int(blob.get("micro_step", 0))
        self.best_val = float(blob.get("best_val", float("inf")))
        self.tokens_seen = int(blob.get("tokens_seen", 0))
        self.samples_seen = int(blob.get("samples_seen", 0))
        self.history = list(blob.get("history", []))
        _restore_rng(blob.get("rng"))

    def _autocast(self):
        if self.device.type == "cuda" and self.cfg.amp:
            dtype = torch.bfloat16 if str(self.cfg.dtype).lower() in {"bfloat16", "bf16"} else torch.float16
            return torch.autocast(device_type="cuda", dtype=dtype, enabled=True)
        if (
            self.device.type == "cpu"
            and self.cfg.cpu_amp
            and hasattr(torch.backends.cpu, "is_bf16_supported")
            and torch.backends.cpu.is_bf16_supported()
        ):
            return torch.autocast(device_type="cpu", dtype=torch.bfloat16)
        return torch.autocast(device_type=self.device.type, dtype=torch.float32, enabled=False)

    def train(self, progress=None) -> dict[str, Any]:
        if self.global_step == 0 and self.micro_step == 0:
            _set_seed(self.cfg.seed)

        self.model.train()
        start = time.time()
        accum = 0
        last_loss = None
        last_eval = None
        self.optimizer.zero_grad(set_to_none=True)
        epoch = self.global_step // max(1, math.ceil(len(self.train_ds) / max(1, self.cfg.batch_size * self.cfg.grad_accum)))

        target_steps = self.cfg.max_steps or self.total_updates
        while epoch < max(1, self.cfg.epochs) or self.global_step < target_steps:
            if self.stop_event.is_set() or self.global_step >= target_steps:
                break

            indices = None
            if self.cfg.curriculum:
                sched = CurriculumSchedule(self.train_ds.rows)
                indices = sched.indices_for_epoch(epoch, max(1, self.cfg.epochs))

            loader = self._loader(self.train_ds, shuffle=True, indices=indices)
            if self.distributed and hasattr(loader.sampler, "set_epoch"):
                loader.sampler.set_epoch(epoch)

            for batch in loader:
                if self.stop_event.is_set() or self.global_step >= target_steps:
                    break

                batch = {k: v.to(self.device) for k, v in batch.items()}
                self.tokens_seen += int(batch["attention_mask"].sum().item())
                self.samples_seen += int(batch["input_ids"].shape[0])

                with self._autocast():
                    raw_loss = self.model(**batch)["loss"]
                if raw_loss is None or not torch.isfinite(raw_loss):
                    raise FloatingPointError(
                        f"Non-finite training loss at micro_step={self.micro_step}"
                    )

                (raw_loss / self.cfg.grad_accum).backward()
                accum += 1
                self.micro_step += 1
                last_loss = float(raw_loss.item())

                if accum >= self.cfg.grad_accum:
                    trainable = [p for p in _unwrap(self.model).parameters() if p.requires_grad]
                    torch.nn.utils.clip_grad_norm_(trainable, self.cfg.max_grad_norm)
                    self.optimizer.step()
                    self.scheduler.step()
                    self.optimizer.zero_grad(set_to_none=True)
                    accum = 0
                    self.global_step += 1

                    elapsed = max(1e-6, time.time() - start)
                    ev = {
                        "step": self.global_step,
                        "total_steps": self.total_updates,
                        "epoch": epoch + 1,
                        "loss": last_loss,
                        "lr": self.optimizer.param_groups[0]["lr"],
                        "tokens_seen": self.tokens_seen,
                        "tokens_per_sec": round(self.tokens_seen / elapsed, 2),
                        "samples_seen": self.samples_seen,
                        "total_samples": len(self.train_ds),
                        "elapsed_sec": round(elapsed, 2),
                        "eta_sec": round(max(0.0, elapsed * (self.total_updates - self.global_step) / max(1, self.global_step)), 2),
                        "rank": self.rank,
                        "world_size": self.world_size,
                    }
                    if self.cfg.eval_every and self.global_step % self.cfg.eval_every == 0 and self.val_ds:
                        last_eval = self.evaluate()
                        ev["val_loss"] = last_eval
                        self.best_val = min(self.best_val, last_eval)

                    self.history.append(ev)
                    if progress and self.is_main_process():
                        progress(ev)
                    if self.cfg.save_every and self.global_step % self.cfg.save_every == 0 and self.is_main_process():
                        self.save_checkpoint(f"step-{self.global_step:06d}", ev)

                    if self.global_step >= target_steps:
                        break

            epoch += 1
            if self.global_step >= target_steps:
                break

        if accum and self.global_step < target_steps:
            trainable = [p for p in _unwrap(self.model).parameters() if p.requires_grad]
            torch.nn.utils.clip_grad_norm_(trainable, self.cfg.max_grad_norm)
            self.optimizer.step()
            self.scheduler.step()
            self.optimizer.zero_grad(set_to_none=True)
            self.global_step += 1

        if self.val_ds:
            last_eval = self.evaluate()
            self.best_val = min(self.best_val, last_eval)

        if self.stop_event.is_set():
            final = self.save_checkpoint(
                f"paused-{self.global_step:06d}",
                {"paused": True, "last_loss": last_loss, "val_loss": last_eval},
            )
            return {
                "checkpoint": str(final),
                "status": "paused",
                "global_step": self.global_step,
                "loss": last_loss,
                "val_loss": last_eval,
                "tokens_seen": self.tokens_seen,
                "samples_seen": self.samples_seen,
                "history": self.history[-20:],
            }

        final = self.save_checkpoint(
            f"final-{self.global_step:06d}",
            {"last_loss": last_loss, "val_loss": last_eval},
        )
        return {
            "checkpoint": str(final),
            "global_step": self.global_step,
            "steps": self.global_step,
            "loss": last_loss,
            "val_loss": last_eval,
            "best_val": self.best_val,
            "tokens_seen": self.tokens_seen,
            "tokens_per_sec": round(self.tokens_seen / max(1e-6, time.time() - start), 2),
            "history": self.history[-20:],
        }


__all__ = [
    "TrainConfig",
    "JsonlTextDataset",
    "JsonlChatDataset",
    "collate",
    "Trainer",
]
