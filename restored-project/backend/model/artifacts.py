# -*- coding: utf-8 -*-
"""Immutable artifact manifests and deterministic hashing for ALI AI 2.0.

The artifact layer is deliberately independent from model inference/training.
Every installed weight, adapter, tokenizer or GGUF file receives a manifest
containing hashes, lineage and provenance so a later machine can reproduce the
same promotion decision without rewriting the control plane.
"""
from __future__ import annotations

from dataclasses import dataclass, asdict, field
from pathlib import Path
from typing import Any, Iterable
import hashlib
import json
import os
import tempfile
import time


CHUNK = 1024 * 1024


def sha256_file(path: str | Path) -> str:
    p = Path(path)
    h = hashlib.sha256()
    with p.open("rb") as fh:
        while True:
            data = fh.read(CHUNK)
            if not data:
                break
            h.update(data)
    return h.hexdigest()


def sha256_path(path: str | Path) -> str:
    """Stable hash for a file or directory, including relative filenames."""
    p = Path(path).resolve()
    if p.is_file():
        return sha256_file(p)

    h = hashlib.sha256()
    for child in sorted(x for x in p.rglob("*") if x.is_file() and x.name != "manifest.json"):
        rel = child.relative_to(p).as_posix()
        h.update(rel.encode("utf-8"))
        h.update(b"\0")
        h.update(sha256_file(child).encode("ascii"))
        h.update(b"\0")
    return h.hexdigest()


def collect_files(root: str | Path) -> list[dict[str, Any]]:
    p = Path(root).resolve()
    files = [p] if p.is_file() else sorted(x for x in p.rglob("*") if x.is_file() and x.name != "manifest.json")
    result = []
    for child in files:
        rel = child.name if p.is_file() else child.relative_to(p).as_posix()
        result.append({
            "path": rel,
            "size": child.stat().st_size,
            "sha256": sha256_file(child),
        })
    return result


def atomic_json_write(path: str | Path, payload: Any) -> Path:
    """Write metadata atomically so a crash cannot leave a half manifest."""
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp_name = tempfile.mkstemp(prefix=target.name + ".", dir=str(target.parent))
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as fh:
            json.dump(payload, fh, ensure_ascii=False, indent=2, sort_keys=True)
            fh.write("\n")
            fh.flush()
            os.fsync(fh.fileno())
        os.replace(tmp_name, target)
    finally:
        try:
            os.unlink(tmp_name)
        except FileNotFoundError:
            pass
    return target


@dataclass
class ArtifactManifest:
    schema_version: int = 2
    artifact_id: str = ""
    artifact_type: str = ""  # base | adapter | merged | tokenizer | gguf | checkpoint
    name: str = ""
    version: str = ""
    created_at: float = field(default_factory=time.time)
    source: str = "local"
    path: str = ""
    sha256: str = ""
    files: list[dict[str, Any]] = field(default_factory=list)
    lineage: dict[str, Any] = field(default_factory=dict)
    training: dict[str, Any] = field(default_factory=dict)
    evaluation: dict[str, Any] = field(default_factory=dict)
    compatibility: dict[str, Any] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    def finalize(self, path: str | Path) -> "ArtifactManifest":
        p = Path(path).resolve()
        self.path = str(p)
        self.sha256 = sha256_path(p)
        self.files = collect_files(p)
        return self

    def write(self, path: str | Path | None = None) -> Path:
        target = Path(path) if path else Path(self.path) / "manifest.json"
        return atomic_json_write(target, self.to_dict())

    @classmethod
    def load(cls, path: str | Path) -> "ArtifactManifest":
        data = json.loads(Path(path).read_text(encoding="utf-8"))
        return cls(**data)

    def verify(self) -> dict[str, Any]:
        p = Path(self.path)
        if not p.exists():
            return {"valid": False, "reason": "artifact_missing", "path": str(p)}
        actual = sha256_path(p)
        return {
            "valid": actual == self.sha256,
            "expected": self.sha256,
            "actual": actual,
            "path": str(p),
        }
