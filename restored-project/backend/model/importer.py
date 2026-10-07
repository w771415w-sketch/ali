# -*- coding: utf-8 -*-
"""Inspect/import real ALI-compatible weight files.

This module deliberately refuses to pretend that an arbitrary checkpoint is an ALI
model. It validates tensor names/shapes before accepting a state dict. Compatible
state dicts can then be loaded into ALIForCausalLM and registered with provenance.
"""
from __future__ import annotations

from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Any, Dict, Mapping
import hashlib
import json
import shutil
import torch

from model.ali_lm import AliConfig, ALIForCausalLM, load_state

@dataclass
class WeightReport:
    path: str
    kind: str
    compatible: bool
    tensor_count: int = 0
    total_parameters: int = 0
    missing: list[str] | None = None
    unexpected: list[str] | None = None
    shape_mismatch: list[str] | None = None
    metadata: Dict[str, Any] | None = None
    error: str = ""

    def to_dict(self):
        return asdict(self)

def _load_state_dict(path: Path) -> tuple[Mapping[str, torch.Tensor], Dict[str, Any]]:
    if path.is_dir():
        for name in ("checkpoint.pt", "model.safetensors", "pytorch_model.bin"):
            candidate = path / name
            if candidate.exists():
                return _load_state_dict(candidate)
        raise FileNotFoundError(f"No supported checkpoint file in {path}")
    if path.suffix.lower() == ".safetensors":
        from safetensors.torch import load_file
        return load_file(str(path), device="cpu"), {}
    blob = torch.load(path, map_location="cpu", weights_only=False)
    if isinstance(blob, Mapping) and "model" in blob and isinstance(blob["model"], Mapping):
        return blob["model"], {k: blob.get(k) for k in ("global_step", "best_val", "train_config", "config")}
    if isinstance(blob, Mapping):
        return blob, {}
    raise ValueError("Unsupported checkpoint payload; expected a state dict")

def inspect_weights(path: str | Path, config: AliConfig | None = None) -> WeightReport:
    p = Path(path).resolve()
    kind = p.suffix.lower().lstrip(".") if p.is_file() else "checkpoint_dir"
    try:
        sd, meta = _load_state_dict(p)
        if config is not None:
            cfg = config
        else:
            embedded_cfg = meta.get("config") if isinstance(meta, dict) else None
            cfg = AliConfig.from_dict(embedded_cfg) if isinstance(embedded_cfg, dict) else AliConfig()
            cfg_file = (p / "config.json") if p.is_dir() else (p.parent / "config.json")
            if cfg_file.exists():
                try:
                    cfg = AliConfig.from_dict(json.loads(cfg_file.read_text(encoding="utf-8")))
                except Exception:
                    pass
        expected = ALIForCausalLM(cfg).state_dict()
        # Support HF-exported state dicts with model.* prefix.
        normalized: dict[str, torch.Tensor] = {}
        for k, v in sd.items():
            nk = k[6:] if k.startswith("model.") else k
            normalized[nk] = v
        missing = [k for k in expected if k not in normalized]
        unexpected = [k for k in normalized if k not in expected]
        shape_mismatch = [f"{k}: {tuple(normalized[k].shape)} != {tuple(expected[k].shape)}"
                          for k in expected if k in normalized and tuple(normalized[k].shape) != tuple(expected[k].shape)]
        total = sum(int(v.numel()) for v in normalized.values() if torch.is_tensor(v))
        compatible = not missing and not shape_mismatch
        return WeightReport(str(p), kind, compatible, len(normalized), total, missing[:40], unexpected[:40], shape_mismatch[:40], meta)
    except Exception as e:
        return WeightReport(str(p), kind, False, error=str(e))

def sha256(path: str | Path) -> str:
    p = Path(path)
    h = hashlib.sha256()
    if p.is_file():
        with p.open("rb") as f:
            for chunk in iter(lambda: f.read(1024 * 1024), b""):
                h.update(chunk)
    else:
        for f in sorted(x for x in p.rglob("*") if x.is_file()):
            h.update(str(f.relative_to(p)).encode("utf-8"))
            with f.open("rb") as fh:
                for chunk in iter(lambda: fh.read(1024 * 1024), b""):
                    h.update(chunk)
    return h.hexdigest()

def import_compatible(path: str | Path, destination: str | Path, config: AliConfig | None = None) -> Dict[str, Any]:
    """Copy a validated ALI checkpoint into the model registry area."""
    report = inspect_weights(path, config)
    if not report.compatible:
        raise ValueError("Weights are not compatible with the active ALI architecture: " + json.dumps(report.to_dict(), ensure_ascii=False))
    src = Path(path).resolve()
    dst = Path(destination).resolve()
    if src.is_dir():
        if dst.exists(): shutil.rmtree(dst)
        shutil.copytree(src, dst)
    else:
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)
    return {"report": report.to_dict(), "destination": str(dst), "sha256": sha256(src)}

def load_into(model: ALIForCausalLM, path: str | Path, device: str = "cpu") -> WeightReport:
    report = inspect_weights(path, model.config)
    if not report.compatible:
        raise ValueError("Incompatible weights")
    file_path = Path(path)
    if file_path.is_dir():
        for name in ("model.safetensors", "checkpoint.pt", "pytorch_model.bin"):
            if (file_path / name).exists():
                file_path = file_path / name
                break
    if file_path.name == "checkpoint.pt":
        blob = torch.load(file_path, map_location=device, weights_only=False)
        model.load_state_dict(blob["model"], strict=True)
    else:
        load_state(model, file_path, device)
    return report
