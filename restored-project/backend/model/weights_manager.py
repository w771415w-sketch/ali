# -*- coding: utf-8 -*-
"""Real model/weight lifecycle for ALI AI 2.0.

Users drop checkpoints/adapters/GGUF files into the UI or ``models/inbox``.
ALI validates them, assigns a deterministic destination, writes a manifest and
registers the artifact. It never fabricates weights and never overwrites an
active model in place.
"""
from __future__ import annotations

from pathlib import Path
from typing import Any, Iterable
import json
import shutil
import time
import uuid

from model.artifacts import ArtifactManifest, atomic_json_write, sha256_path
from model.ali_lm import AliConfig
from model.importer import inspect_weights, import_compatible
from model.registry import ModelRegistry


class WeightsManager:
    """Centralized artifact store.

    Layout:
        models/
          inbox/
          quarantine/
          base/<name>/<version>/
          adapters/<name>/<version>/
          merged/<name>/<version>/
          gguf/<name>/<version>/
          tokenizers/<name>/<version>/
    """

    TYPES = ("base", "adapter", "merged", "gguf")

    def __init__(self, root: str | Path, registry: ModelRegistry | None = None):
        self.root = Path(root)
        self.models_root = self.root / "models"
        self.registry = registry or ModelRegistry(self.models_root / "models.sqlite3")
        for rel in ("inbox", "quarantine", "base", "adapters", "merged", "gguf", "tokenizers"):
            (self.models_root / rel).mkdir(parents=True, exist_ok=True)

    # Backward-compatible helpers
    def list_models(self):
        return [x["version"] for x in self.registry.list("ALI")]

    def get_model_info(self, model_name):
        rows = self.registry.list("ALI")
        return next((r for r in rows if r["version"] == model_name), None)

    def inspect(self, source: str | Path, config: AliConfig | None = None) -> dict[str, Any]:
        p = Path(source).resolve()
        if p.is_file() and p.suffix.lower() == ".gguf":
            from tools.gguf import GGUFManager
            validation = GGUFManager().validate(p)
            return {
                "kind": "gguf",
                "path": str(p),
                "compatible": bool(validation.get("valid")),
                "size": p.stat().st_size,
                "validation": validation,
                "sha256": sha256_path(p),
            }
        if self._looks_like_adapter(p):
            return self._inspect_adapter(p)
        report = inspect_weights(p, config)
        data = report.to_dict()
        data["kind"] = "base"
        data["sha256"] = sha256_path(p)
        return data

    def install(
        self,
        source: str | Path,
        *,
        artifact_type: str | None = None,
        name: str = "ALI",
        version: str | None = None,
        config: AliConfig | None = None,
        base_version: str = "",
        dataset_hash: str = "",
        tokenizer_hash: str = "",
        training: dict[str, Any] | None = None,
        evaluation: dict[str, Any] | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        src = Path(source).resolve()
        if not src.exists():
            raise FileNotFoundError(src)

        info = self.inspect(src, config)
        kind = artifact_type or info["kind"]
        if kind not in self.TYPES:
            raise ValueError(f"Unsupported artifact type: {kind}")

        if not info.get("compatible", False):
            raise ValueError("Artifact is not compatible with the active ALI architecture: " +
                             json.dumps(info, ensure_ascii=False)[:6000])

        safe_name = self._safe(name or "ALI")
        ver = version or time.strftime("%Y%m%d-%H%M%S") + "-" + uuid.uuid4().hex[:6]
        destination = self.models_root / {
            "base": "base",
            "adapter": "adapters",
            "merged": "merged",
            "gguf": "gguf",
        }[kind] / safe_name / ver
        destination.parent.mkdir(parents=True, exist_ok=True)

        staging = destination.with_name(destination.name + ".staging")
        if staging.exists():
            shutil.rmtree(staging)
        if src.is_dir():
            shutil.copytree(src, staging)
        else:
            staging.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, staging / src.name)

        manifest = ArtifactManifest(
            artifact_id=f"{safe_name}:{ver}",
            artifact_type=kind,
            name=safe_name,
            version=ver,
            source="user-import",
            lineage={
                "base_version": base_version,
                "dataset_hash": dataset_hash,
                "tokenizer_hash": tokenizer_hash,
            },
            training=training or {},
            evaluation=evaluation or {},
            compatibility={
                "report": info,
            },
            metadata=metadata or {},
        )
        manifest.finalize(staging)
        manifest.write(staging / "manifest.json")

        if destination.exists():
            shutil.rmtree(destination)
        staging.replace(destination)

        manifest.path = str(destination.resolve())
        # The manifest contains its pre-move hash, which is fine for contents;
        # rewrite after the atomic move so path/sha are canonical.
        manifest.finalize(destination)
        manifest.write(destination / "manifest.json")

        reg_name = safe_name if kind in {"base", "merged"} else f"{safe_name}-{kind}"
        reg_meta = {
            "artifact_type": kind,
            "status": "candidate",
            "base_version": base_version,
            "checkpoint": str(destination if kind != "gguf" else ""),
            "hf_dir": str(destination if kind in {"base", "merged"} else ""),
            "gguf": str(destination) if kind == "gguf" else "",
            "adapter": str(destination) if kind == "adapter" else "",
            "dataset_hash": dataset_hash,
            "tokenizer_hash": tokenizer_hash,
            "artifact_hash": manifest.sha256,
            "train_config": training or {},
            "eval": evaluation or {},
        }
        self.registry.register(reg_name, ver, **reg_meta)
        return {
            "installed": True,
            "type": kind,
            "version": ver,
            "path": str(destination),
            "manifest": manifest.to_dict(),
            "registry": reg_meta,
        }

    def verify(self, path: str | Path) -> dict[str, Any]:
        p = Path(path).resolve()
        m = p / "manifest.json"
        if not m.exists():
            return {"valid": False, "reason": "manifest_missing", "path": str(p)}
        return ArtifactManifest.load(m).verify()

    def quarantine(self, source: str | Path, reason: str) -> dict[str, Any]:
        src = Path(source).resolve()
        dest = self.models_root / "quarantine" / f"{src.stem}-{time.strftime('%Y%m%d-%H%M%S')}"
        dest.parent.mkdir(parents=True, exist_ok=True)
        if src.is_dir():
            shutil.copytree(src, dest)
        else:
            shutil.copy2(src, dest)
        atomic_json_write(dest.with_suffix(".reason.json"), {
            "source": str(src), "reason": reason, "sha256": sha256_path(src),
            "created_at": time.time(),
        })
        return {"quarantined": True, "path": str(dest), "reason": reason}

    def scan_inbox(self) -> list[dict[str, Any]]:
        inbox = self.models_root / "inbox"
        rows = []
        for p in sorted(inbox.iterdir()):
            try:
                rows.append(self.inspect(p))
            except Exception as exc:
                rows.append({"path": str(p), "compatible": False, "error": str(exc)})
        return rows

    @staticmethod
    def _safe(value: str) -> str:
        clean = "".join(ch if ch.isalnum() or ch in "._-" else "_" for ch in value.strip())
        return clean or "ALI"

    @staticmethod
    def _looks_like_adapter(path: Path) -> bool:
        if path.is_dir():
            return any((path / n).exists() for n in ("adapter_config.json", "adapter_model.safetensors", "adapter_model.pt"))
        return "adapter" in path.name.lower()

    @staticmethod
    def _inspect_adapter(path: Path) -> dict[str, Any]:
        if path.is_dir():
            cfg = path / "adapter_config.json"
            data = json.loads(cfg.read_text(encoding="utf-8")) if cfg.exists() else {}
            tensors = path / "adapter_model.safetensors"
            if not tensors.exists():
                tensors = path / "adapter_model.pt"
            if not tensors.exists():
                raise FileNotFoundError("adapter_model.safetensors/pt not found")
            return {
                "kind": "adapter",
                "path": str(path),
                "compatible": True,
                "config": data,
                "sha256": sha256_path(path),
                "size": tensors.stat().st_size,
            }
        return {
            "kind": "adapter",
            "path": str(path),
            "compatible": False,
            "error": "A standalone adapter file needs its adapter directory/config.",
        }
