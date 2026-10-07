from __future__ import annotations

import json
import sqlite3
import threading
import time
from pathlib import Path
from typing import Any


class AuditStore:
    """Small WAL-backed store for idempotency and audit records."""

    def __init__(self, workspace: Path):
        self.path = workspace / "runtime.db"
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._lock = threading.Lock()
        self.db = sqlite3.connect(self.path, check_same_thread=False)
        self.db.execute("PRAGMA journal_mode=WAL")
        self.db.execute("PRAGMA synchronous=NORMAL")
        self.db.executescript(
            """
            CREATE TABLE IF NOT EXISTS idempotency (
                key TEXT PRIMARY KEY,
                status TEXT NOT NULL,
                response TEXT,
                created REAL NOT NULL,
                updated REAL NOT NULL
            );
            CREATE TABLE IF NOT EXISTS audit (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                request_id TEXT NOT NULL,
                action TEXT NOT NULL,
                status TEXT NOT NULL,
                detail TEXT,
                created REAL NOT NULL
            );
            """
        )
        self.db.commit()

    def begin(self, key: str) -> tuple[str, dict[str, Any] | None]:
        now = time.time()
        with self._lock:
            row = self.db.execute("SELECT status,response FROM idempotency WHERE key=?", (key,)).fetchone()
            if row:
                return row[0], None if row[1] is None else json.loads(row[1])
            self.db.execute(
                "INSERT INTO idempotency(key,status,response,created,updated) VALUES(?,?,?,?,?)",
                (key, "running", None, now, now),
            )
            self.db.commit()
            return "claimed", None

    def complete(self, key: str, response: dict[str, Any], status: str = "complete") -> None:
        with self._lock:
            self.db.execute(
                "UPDATE idempotency SET status=?,response=?,updated=? WHERE key=?",
                (status, json.dumps(response, ensure_ascii=False), time.time(), key),
            )
            self.db.commit()

    def audit(self, request_id: str, action: str, status: str, detail: object = None) -> None:
        with self._lock:
            self.db.execute(
                "INSERT INTO audit(request_id,action,status,detail,created) VALUES(?,?,?,?,?)",
                (request_id, action, status, json.dumps(detail, ensure_ascii=False) if detail is not None else None, time.time()),
            )
            self.db.commit()

    def close(self) -> None:
        self.db.close()
