# -*- coding: utf-8 -*-
"""Versioned model/artifact registry with immutable lineage metadata."""
from __future__ import annotations

from pathlib import Path
import hashlib
import json
import sqlite3
import time
from typing import Any


class ModelRegistry:
    def __init__(self, db_path: str | Path):
        self.path = Path(db_path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._bootstrap()

    def _connect(self):
        c = sqlite3.connect(self.path, timeout=10)
        c.row_factory = sqlite3.Row
        return c

    def _bootstrap(self):
        c = self._connect()
        c.execute(
            """
            CREATE TABLE IF NOT EXISTS model_versions(
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                version TEXT NOT NULL,
                artifact_type TEXT NOT NULL DEFAULT 'base',
                status TEXT NOT NULL,
                base_version TEXT,
                checkpoint TEXT,
                hf_dir TEXT,
                gguf TEXT,
                adapter TEXT,
                quantized TEXT,
                dataset_hash TEXT,
                tokenizer_hash TEXT,
                artifact_hash TEXT,
                train_config TEXT,
                eval_json TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                parent_generation TEXT NOT NULL DEFAULT '',
                cumulative_dataset_hash TEXT NOT NULL DEFAULT '',
                UNIQUE(name,version)
            )
            """
        )
        cols = {r["name"] for r in c.execute("PRAGMA table_info(model_versions)").fetchall()}
        if "artifact_type" not in cols:
            c.execute("ALTER TABLE model_versions ADD COLUMN artifact_type TEXT NOT NULL DEFAULT 'base'")
        for name, typ in (("adapter", "TEXT"), ("quantized", "TEXT"), ("artifact_hash", "TEXT"), ("parent_generation", "TEXT NOT NULL DEFAULT ''"), ("cumulative_dataset_hash", "TEXT NOT NULL DEFAULT ''")):
            if name not in cols:
                c.execute(f"ALTER TABLE model_versions ADD COLUMN {name} {typ}")
        c.commit()
        c.close()

    def register(self, name: str, version: str, **meta):
        payload = (
            name,
            version,
            str(meta.get("artifact_type", "base")),
            str(meta.get("status", "candidate")),
            str(meta.get("base_version", "")),
            str(meta.get("checkpoint", "")),
            str(meta.get("hf_dir", "")),
            str(meta.get("gguf", "")),
            str(meta.get("adapter", "")),
            str(meta.get("quantized", "")),
            str(meta.get("dataset_hash", "")),
            str(meta.get("tokenizer_hash", "")),
            str(meta.get("artifact_hash", "")),
            json.dumps(meta.get("train_config", {}), ensure_ascii=False),
            json.dumps(meta.get("eval", {}), ensure_ascii=False),
            str(meta.get("parent_generation", "")),
            str(meta.get("cumulative_dataset_hash", "")),
        )
        c = self._connect()
        c.execute(
            """
            INSERT OR REPLACE INTO model_versions(
                name,version,artifact_type,status,base_version,checkpoint,hf_dir,gguf,
                adapter,quantized,dataset_hash,tokenizer_hash,artifact_hash,train_config,eval_json,parent_generation,cumulative_dataset_hash
            ) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
            """,
            payload,
        )
        c.commit()
        c.close()


    def update_artifacts(self, name: str, version: str, **fields) -> None:
        """Attach post-promotion artifacts such as GGUF without changing lifecycle status."""
        allowed = {"checkpoint", "hf_dir", "gguf", "adapter", "quantized", "artifact_hash", "eval_json"}
        updates = {k: v for k, v in fields.items() if k in allowed}
        if not updates:
            return
        parts = []
        values = []
        for k, v in updates.items():
            parts.append(f"{k}=?")
            if k == "eval_json" and not isinstance(v, str):
                v = json.dumps(v, ensure_ascii=False)
            values.append(v)
        values.extend([name, version])
        c = self._connect()
        c.execute(f"UPDATE model_versions SET {', '.join(parts)} WHERE name=? AND version=?", tuple(values))
        c.commit()
        c.close()

    def promote(self, name: str, version: str) -> None:
        c = self._connect()
        row = c.execute(
            "SELECT artifact_type,hf_dir,checkpoint FROM model_versions WHERE name=? AND version=?",
            (name, version),
        ).fetchone()
        if not row:
            c.close()
            raise KeyError(f"model version not found: {name}:{version}")
        if row["artifact_type"] not in {"base", "merged"} or not (row["hf_dir"] or row["checkpoint"]):
            c.close()
            raise ValueError("only base/merged model artifacts with a loadable checkpoint can become active")
        c.execute(
            "UPDATE model_versions SET status='archived' WHERE name=? AND status='active'",
            (name,),
        )
        c.execute(
            "UPDATE model_versions SET status='active' WHERE name=? AND version=?",
            (name, version),
        )
        c.commit()
        c.close()
        try:
            active_dir = self.path.parent / "active"
            active_dir.mkdir(parents=True, exist_ok=True)
            active_row = self.active(name)
            if active_row:
                (active_dir / "current.json").write_text(
                    json.dumps({
                        "model": name,
                        "active_generation": active_row.get("version", ""),
                        "hf_dir": active_row.get("hf_dir", ""),
                        "checkpoint": active_row.get("checkpoint", ""),
                        "gguf": active_row.get("gguf", ""),
                        "updated_at": time.time() if "time" in globals() else 0,
                    }, ensure_ascii=False, indent=2) + "\n",
                    encoding="utf-8",
                )
        except Exception:
            pass

    def active(self, name: str = "ALI") -> dict[str, Any] | None:
        c = self._connect()
        row = c.execute(
            "SELECT * FROM model_versions WHERE name=? AND status='active' ORDER BY id DESC LIMIT 1",
            (name,),
        ).fetchone()
        c.close()
        return dict(row) if row else None

    def list(self, name: str = "ALI") -> list[dict[str, Any]]:
        c = self._connect()
        rows = c.execute(
            "SELECT * FROM model_versions WHERE name=? ORDER BY id DESC",
            (name,),
        ).fetchall()
        c.close()
        return [dict(x) for x in rows]

    def list_loadable(self, name: str = "ALI") -> list[dict[str, Any]]:
        return [
            r for r in self.list(name)
            if r.get("artifact_type") in {"base", "merged"} and (r.get("hf_dir") or r.get("checkpoint"))
        ]

    def find_dataset(self, dataset_hash: str, name: str = "ALI"):
        c = self._connect()
        c.row_factory = sqlite3.Row
        row = c.execute(
            "SELECT * FROM model_versions WHERE name=? AND dataset_hash=? ORDER BY id DESC LIMIT 1",
            (name, dataset_hash),
        ).fetchone()
        c.close()
        return dict(row) if row else None


def file_hash(path: str | Path) -> str:
    p = Path(path)
    h = hashlib.sha256()
    if p.is_file():
        with p.open("rb") as f:
            for b in iter(lambda: f.read(1024 * 1024), b""):
                h.update(b)
        return h.hexdigest()
    for f in sorted(x for x in p.rglob("*") if x.is_file()):
        h.update(str(f.relative_to(p)).encode("utf-8"))
        h.update(file_hash(f).encode("ascii"))
    return h.hexdigest()


__all__ = ["ModelRegistry", "file_hash"]
