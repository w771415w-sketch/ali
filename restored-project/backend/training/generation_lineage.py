# -*- coding: utf-8 -*-
"""General cumulative-generation dataset and lineage engine for ALI."""
from __future__ import annotations

from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Any, Iterable
import hashlib
import json
import time

SCHEMA_VERSION = 2


def canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def sha256_file(path: str | Path) -> str:
    p = Path(path)
    h = hashlib.sha256()
    with p.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def sample_id(row: dict[str, Any]) -> str:
    for key in ("sample_id", "content_hash", "sample_hash", "id"):
        value = row.get(key)
        if value:
            return str(value)
    return hashlib.sha256(canonical_json(row.get("messages", row)).encode("utf-8")).hexdigest()


def iter_jsonl(path: str | Path) -> Iterable[dict[str, Any]]:
    p = Path(path)
    if not p.exists():
        return
    with p.open("r", encoding="utf-8") as fh:
        for line_no, line in enumerate(fh, 1):
            raw = line.strip()
            if not raw:
                continue
            try:
                obj = json.loads(raw)
            except json.JSONDecodeError as exc:
                raise ValueError(f"Invalid JSONL at {p}:{line_no}: {exc}") from exc
            if isinstance(obj, dict):
                yield obj


def count_jsonl(path: str | Path) -> int:
    return sum(1 for _ in iter_jsonl(path))


def merge_jsonl_unique(input_paths: Iterable[str | Path], output_path: str | Path) -> dict[str, Any]:
    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    seen: set[str] = set()
    input_rows = 0
    duplicates = 0
    written = 0
    source_files: list[str] = []
    with output.open("w", encoding="utf-8") as out:
        for raw in input_paths:
            p = Path(raw)
            if not p.exists():
                continue
            source_files.append(str(p))
            for row in iter_jsonl(p):
                input_rows += 1
                sid = sample_id(row)
                if sid in seen:
                    duplicates += 1
                    continue
                seen.add(sid)
                record = dict(row)
                record.setdefault("sample_id", sid)
                out.write(json.dumps(record, ensure_ascii=False, sort_keys=True) + "\n")
                written += 1
    return {
        "input_rows": input_rows,
        "written_rows": written,
        "duplicates_removed": duplicates,
        "dataset_hash": sha256_file(output) if output.exists() else "",
        "output": str(output),
        "source_files": source_files,
        "created_at": time.time(),
    }


def generation_manifest_path(models_root: str | Path, generation: str) -> Path:
    return Path(models_root) / "generations" / generation / "generation.json"


def load_generation_manifest(models_root: str | Path, generation: str) -> dict[str, Any] | None:
    path = generation_manifest_path(models_root, generation)
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None


def _resolve_manifest_path(models_root: Path, value: str | Path) -> Path:
    p = Path(str(value))
    if p.is_absolute():
        return p
    return (models_root.parent / p).resolve() if str(p).startswith('models' + __import__('os').sep) or str(p).startswith('models/') else (models_root / p).resolve()


def generation_train_path(models_root: str | Path, generation: str) -> Path | None:
    manifest = load_generation_manifest(models_root, generation)
    if not manifest:
        return None
    for key in ("cumulative_dataset", "cumulative_train_path", "train_path"):
        value = manifest.get(key)
        if isinstance(value, dict):
            value = value.get("path")
        if value:
            p = _resolve_manifest_path(Path(models_root), str(value))
            if p.exists():
                return p
    # New layout fallback.
    candidate = Path(models_root) / "generations" / generation / "cumulative" / "train.jsonl"
    return candidate if candidate.exists() else None


def _parent_from_manifest(manifest: dict[str, Any]) -> str:
    parent = manifest.get("parent_generation")
    if parent:
        return str(parent)
    legacy = manifest.get("base_version")
    if legacy and str(legacy).startswith("v"):
        return str(legacy)
    return ""


def build_chain(models_root: str | Path, generation: str) -> list[str]:
    """Return the complete chain including the requested generation."""
    result: list[str] = []
    seen: set[str] = set()
    current = str(generation)
    while current and current not in seen:
        seen.add(current)
        result.append(current)
        manifest = load_generation_manifest(models_root, current)
        if not manifest:
            break
        current = _parent_from_manifest(manifest)
    result.reverse()
    return result


def build_ancestors(models_root: str | Path, generation: str) -> list[str]:
    """Return parent generations only; never include the requested generation itself."""
    chain = build_chain(models_root, generation)
    return chain[:-1] if chain and chain[-1] == str(generation) else chain


def build_ancestor_train_paths(models_root: str | Path, generation: str) -> list[Path]:
    result: list[Path] = []
    for gen in build_ancestors(models_root, generation):
        p = generation_train_path(models_root, gen)
        if p is not None:
            result.append(p)
    return result


def discover_delta_paths(models_root: str | Path, generation: str) -> list[Path]:
    models_root = Path(models_root)
    root = models_root / "generations" / generation
    paths = [root / "delta" / "train.jsonl", root / "delta.jsonl"]
    manifest = load_generation_manifest(models_root, generation) or {}
    value = manifest.get("delta_dataset")
    if isinstance(value, dict):
        value = value.get("path")
    if value:
        p = _resolve_manifest_path(models_root, str(value))
        paths.insert(0, p)
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
