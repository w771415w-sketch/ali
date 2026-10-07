# -*- coding: utf-8 -*-
"""Versioned tokenizer lifecycle for ALI AI 2.0."""
from __future__ import annotations

from pathlib import Path
from typing import Iterable, Any
import json
import time
import hashlib
import shutil

from tokenizer.spm import train_sentencepiece, AliTokenizer
from model.artifacts import ArtifactManifest, sha256_path


class TokenizerManager:
    def __init__(self, root: str | Path):
        self.root = Path(root)
        self.dir = self.root / "models" / "tokenizers"
        self.dir.mkdir(parents=True, exist_ok=True)

    def corpus_hash(self, inputs: Iterable[str | Path]) -> str:
        h = hashlib.sha256()
        for raw in sorted(str(Path(x).resolve()) for x in inputs):
            p = Path(raw)
            h.update(raw.encode("utf-8")); h.update(b"\0")
            h.update(p.read_bytes())
            h.update(b"\0")
        return h.hexdigest()

    def train(
        self,
        inputs: list[str | Path],
        *,
        vocab_size: int = 4096,
        name: str = "ALI",
        version: str | None = None,
        force: bool = False,
    ) -> dict[str, Any]:
        if not inputs:
            raise ValueError("tokenizer inputs are empty")
        paths = [Path(x).resolve() for x in inputs]
        for p in paths:
            if not p.exists():
                raise FileNotFoundError(p)
        chash = self.corpus_hash(paths)
        existing = self.find_by_corpus(chash, name)
        if existing and not force:
            return {"reused": True, **existing}

        ver = version or time.strftime("%Y%m%d-%H%M%S")
        safe = "".join(c if c.isalnum() or c in "._-" else "_" for c in name) or "ALI"
        out = self.dir / safe / ver
        out.parent.mkdir(parents=True, exist_ok=True)

        # SentencePiece works from real corpus files. JSONL is converted to a
        # deterministic plain-text corpus first.
        corpus_files = []
        work = out / "_corpus"
        work.mkdir(parents=True, exist_ok=True)
        for idx, p in enumerate(paths):
            if p.suffix.lower() in {".jsonl", ".json"}:
                target = work / f"{idx:03d}-{p.stem}.txt"
                with p.open(encoding="utf-8", errors="replace") as fh, target.open("w", encoding="utf-8") as out_f:
                    for line in fh:
                        try:
                            obj = json.loads(line)
                        except Exception:
                            continue
                        if isinstance(obj, dict) and isinstance(obj.get("messages"), list):
                            for m in obj["messages"]:
                                if isinstance(m, dict):
                                    out_f.write(str(m.get("content", "")) + "\n")
                        elif isinstance(obj, dict):
                            out_f.write(str(obj.get("text", "")) + "\n")
                        else:
                            out_f.write(str(obj) + "\n")
                corpus_files.append(str(target))
            else:
                corpus_files.append(str(p))

        tokenizer_file = train_sentencepiece(corpus_files, out, vocab_size=vocab_size)
        tok = AliTokenizer(tokenizer_file)
        manifest = ArtifactManifest(
            artifact_id=f"{safe}:tokenizer:{ver}",
            artifact_type="tokenizer",
            name=safe,
            version=ver,
            source="local-training",
            lineage={"corpus_hash": chash, "inputs": [str(p) for p in paths]},
            compatibility={"vocab_size": tok.vocab_size},
            metadata={"requested_vocab_size": vocab_size, "actual_vocab_size": tok.vocab_size},
        )
        # Temporary corpus is implementation detail, remove before final hash.
        if work.exists():
            shutil.rmtree(work)
        manifest.finalize(out)
        manifest.write(out / "manifest.json")
        return {
            "reused": False,
            "name": safe,
            "version": ver,
            "path": str(out),
            "tokenizer": str(tokenizer_file),
            "vocab_size": tok.vocab_size,
            "corpus_hash": chash,
            "hash": manifest.sha256,
        }

    def find_by_corpus(self, corpus_hash: str, name: str = "ALI") -> dict[str, Any] | None:
        safe = "".join(c if c.isalnum() or c in "._-" else "_" for c in name) or "ALI"
        base = self.dir / safe
        if not base.exists():
            return None
        for version_dir in sorted((p for p in base.iterdir() if p.is_dir()), reverse=True):
            m = version_dir / "manifest.json"
            if not m.exists():
                continue
            data = json.loads(m.read_text(encoding="utf-8"))
            if data.get("lineage", {}).get("corpus_hash") == corpus_hash:
                return {
                    "name": data.get("name", safe),
                    "version": data.get("version", version_dir.name),
                    "path": str(version_dir),
                    "tokenizer": str(version_dir / "tokenizer.model"),
                    "vocab_size": data.get("compatibility", {}).get("vocab_size", 0),
                    "corpus_hash": corpus_hash,
                    "hash": data.get("sha256", ""),
                }
        return None

    def list(self, name: str = "ALI") -> list[dict[str, Any]]:
        safe = "".join(c if c.isalnum() or c in "._-" else "_" for c in name) or "ALI"
        base = self.dir / safe
        if not base.exists():
            return []
        result = []
        for p in sorted((x for x in base.iterdir() if x.is_dir()), reverse=True):
            m = p / "manifest.json"
            if m.exists():
                result.append(json.loads(m.read_text(encoding="utf-8")))
        return result
