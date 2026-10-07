# -*- coding: utf-8 -*-
"""Persistent error-learning queue.

Errors are never trained blindly. Bad outputs create incidents; a human- or
rule-verified correction creates an APPROVED training example that can be
included in the next generation's delta dataset.
"""
from __future__ import annotations

from pathlib import Path
import hashlib
import json
import sqlite3
import time
from typing import Any


class ErrorLearningStore:
    def __init__(self, db: str | Path, root: str | Path | None = None):
        self.db = Path(db)
        self.db.parent.mkdir(parents=True, exist_ok=True)
        self.root = Path(root).resolve() if root else self.db.parent.parent.resolve()
        self.queue_dir = self.root / "artifacts" / "error_learning"
        self.queue_dir.mkdir(parents=True, exist_ok=True)
        self.approved_jsonl = self.queue_dir / "approved_corrections.jsonl"
        self._bootstrap()

    def _connect(self):
        c = sqlite3.connect(self.db, timeout=30)
        c.row_factory = sqlite3.Row
        return c

    def _bootstrap(self):
        with self._connect() as c:
            c.execute(
                """CREATE TABLE IF NOT EXISTS incidents(
                    id INTEGER PRIMARY KEY,
                    fingerprint TEXT UNIQUE NOT NULL,
                    component TEXT NOT NULL,
                    user_text TEXT DEFAULT '',
                    bad_output TEXT NOT NULL,
                    reason TEXT DEFAULT '',
                    recovery TEXT DEFAULT '',
                    recovered INTEGER NOT NULL DEFAULT 0,
                    status TEXT NOT NULL DEFAULT 'open',
                    created_at REAL NOT NULL,
                    updated_at REAL NOT NULL
                )"""
            )
            cols = {r["name"] for r in c.execute("PRAGMA table_info(incidents)").fetchall()}
            for name, typ, default in (
                ("user_text", "TEXT", "''"),
                ("reason", "TEXT", "''"),
                ("status", "TEXT", "'open'"),
                ("updated_at", "REAL", "0"),
            ):
                if name not in cols:
                    c.execute(f"ALTER TABLE incidents ADD COLUMN {name} {typ} NOT NULL DEFAULT {default}")
            c.execute(
                """CREATE TABLE IF NOT EXISTS corrections(
                    id INTEGER PRIMARY KEY,
                    fingerprint TEXT NOT NULL,
                    sample_id TEXT UNIQUE NOT NULL,
                    user_text TEXT NOT NULL,
                    bad_output TEXT NOT NULL,
                    corrected_output TEXT NOT NULL,
                    source TEXT NOT NULL DEFAULT 'user',
                    status TEXT NOT NULL DEFAULT 'approved',
                    created_at REAL NOT NULL,
                    FOREIGN KEY(fingerprint) REFERENCES incidents(fingerprint)
                )"""
            )

    @staticmethod
    def _fingerprint(component: str, user_text: str, message: str, reason: str = "") -> str:
        # The incident identity must remain stable even when the diagnostic reason changes.
        raw = "\n".join([component, user_text, message]).encode("utf-8")
        return hashlib.sha256(raw).hexdigest()

    @staticmethod
    def _sample_id(user_text: str, corrected_output: str) -> str:
        raw = json.dumps(
            {
                "messages": [
                    {"role": "user", "content": user_text.strip()},
                    {"role": "assistant", "content": corrected_output.strip()},
                ]
            },
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
        ).encode("utf-8")
        return hashlib.sha256(raw).hexdigest()

    def record(
        self,
        component: str,
        message: str,
        recovery: str = "",
        recovered: bool = False,
        *,
        user_text: str = "",
        reason: str = "",
    ) -> str:
        now = time.time()
        fp = self._fingerprint(component, user_text, message, reason)
        with self._connect() as c:
            c.execute(
                """INSERT INTO incidents(
                    fingerprint,component,user_text,bad_output,reason,recovery,
                    recovered,status,created_at,updated_at
                ) VALUES(?,?,?,?,?,?,?,?,?,?)
                ON CONFLICT(fingerprint) DO UPDATE SET
                    recovery=excluded.recovery,
                    recovered=excluded.recovered,
                    reason=excluded.reason,
                    status=CASE WHEN excluded.recovered=1 THEN 'recovered' ELSE incidents.status END,
                    updated_at=excluded.updated_at""",
                (
                    fp,
                    component,
                    user_text,
                    str(message),
                    reason,
                    recovery,
                    int(recovered),
                    "recovered" if recovered else "open",
                    now,
                    now,
                ),
            )
        return fp

    def add_correction(
        self,
        user_text: str,
        bad_output: str,
        corrected_output: str,
        *,
        component: str = "chat",
        reason: str = "user_correction",
        source: str = "user",
    ) -> dict[str, Any]:
        user_text = str(user_text or "").strip()
        bad_output = str(bad_output or "").strip()
        corrected_output = str(corrected_output or "").strip()
        if not user_text:
            raise ValueError("user_text is required")
        if not corrected_output:
            raise ValueError("corrected_output is required")
        fp = self.record(component, bad_output, user_text=user_text, reason=reason)
        sid = self._sample_id(user_text, corrected_output)
        now = time.time()
        row = {
            "id": sid,
            "sample_id": sid,
            "messages": [
                {"role": "user", "content": user_text},
                {"role": "assistant", "content": corrected_output},
            ],
            "text": f"<|user|>\n{user_text}<|eot|>\n<|assistant|>\n{corrected_output}<|eot|>\n",
            "provenance": {
                "source": "error-learning",
                "component": component,
                "reason": reason,
                "verified": True,
                "created_at": now,
            },
            "source_hash": fp,
            "content_hash": sid,
        }
        with self._connect() as c:
            c.execute(
                """INSERT OR IGNORE INTO corrections(
                    fingerprint,sample_id,user_text,bad_output,corrected_output,
                    source,status,created_at
                ) VALUES(?,?,?,?,?,?,?,?)""",
                (fp, sid, user_text, bad_output, corrected_output, source, "approved", now),
            )
        if not any(
            line.get("sample_id") == sid
            for line in self._iter_approved_jsonl()
        ):
            with self.approved_jsonl.open("a", encoding="utf-8") as f:
                f.write(json.dumps(row, ensure_ascii=False) + "\n")
        return {"ok": True, "sample_id": sid, "fingerprint": fp, "status": "approved", "row": row}

    def _iter_approved_jsonl(self):
        if not self.approved_jsonl.exists():
            return
        with self.approved_jsonl.open("r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    row = json.loads(line)
                    if isinstance(row, dict):
                        yield row
                except json.JSONDecodeError:
                    continue

    def pending(self, limit: int = 100) -> list[dict[str, Any]]:
        with self._connect() as c:
            rows = c.execute(
                "SELECT * FROM incidents WHERE status IN ('open','recovered') ORDER BY updated_at DESC LIMIT ?",
                (max(1, int(limit)),),
            ).fetchall()
        return [dict(r) for r in rows]

    def corrections(self, status: str = "approved", limit: int = 1000) -> list[dict[str, Any]]:
        with self._connect() as c:
            rows = c.execute(
                "SELECT * FROM corrections WHERE status=? ORDER BY id ASC LIMIT ?",
                (status, max(1, int(limit))),
            ).fetchall()
        out = []
        for row in rows:
            r = dict(row)
            sid = r["sample_id"]
            r["messages"] = [
                {"role": "user", "content": r["user_text"]},
                {"role": "assistant", "content": r["corrected_output"]},
            ]
            r["id"] = sid
            r["provenance"] = {"source": "error-learning", "verified": True}
            out.append(r)
        return out

    def mark_trained(self, sample_ids: list[str], generation: str):
        ids = [str(x) for x in sample_ids if x]
        if not ids:
            return 0
        with self._connect() as c:
            c.executemany(
                "UPDATE corrections SET status=? WHERE sample_id=? AND status='approved'",
                [(f"trained:{generation}", sid) for sid in ids],
            )
        return len(ids)

    def stats(self) -> dict[str, Any]:
        with self._connect() as c:
            incidents = c.execute("SELECT status,COUNT(*) n FROM incidents GROUP BY status").fetchall()
            corrections = c.execute("SELECT status,COUNT(*) n FROM corrections GROUP BY status").fetchall()
        return {
            "incidents": {str(r["status"]): int(r["n"]) for r in incidents},
            "corrections": {str(r["status"]): int(r["n"]) for r in corrections},
            "approved_corrections": len(self.corrections("approved", 100000)),
            "approved_jsonl": str(self.approved_jsonl),
        }

    def known(self, component: str, message: str, user_text: str = ""):
        fp = self._fingerprint(component, user_text, message)
        with self._connect() as c:
            row = c.execute("SELECT * FROM incidents WHERE fingerprint=?", (fp,)).fetchone()
        return dict(row) if row else None
