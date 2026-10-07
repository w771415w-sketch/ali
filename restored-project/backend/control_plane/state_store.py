# -*- coding: utf-8 -*-
"""SQLite trace/state store for the unified KCA control plane."""
from __future__ import annotations
import json, sqlite3, time
from pathlib import Path
from typing import Any


class KCAStateStore:
    def __init__(self, path: str | Path):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with sqlite3.connect(self.path) as c:
            c.execute("PRAGMA journal_mode=WAL")
            c.execute("""
                CREATE TABLE IF NOT EXISTS kca_operations(
                    operation_id TEXT PRIMARY KEY,
                    request_id TEXT NOT NULL,
                    status TEXT NOT NULL,
                    intent TEXT,
                    state_json TEXT NOT NULL,
                    trace_json TEXT,
                    created_at REAL NOT NULL,
                    updated_at REAL NOT NULL
                )
            """)
            c.execute("CREATE INDEX IF NOT EXISTS idx_kca_request ON kca_operations(request_id)")
            c.execute("CREATE INDEX IF NOT EXISTS idx_kca_status ON kca_operations(status)")

    def upsert(self, operation_id: str, request_id: str, status: str, state: dict[str, Any], trace: dict[str, Any] | None = None) -> None:
        now = time.time()
        with sqlite3.connect(self.path) as c:
            c.execute("""
                INSERT INTO kca_operations(operation_id,request_id,status,intent,state_json,trace_json,created_at,updated_at)
                VALUES(?,?,?,?,?,?,?,?)
                ON CONFLICT(operation_id) DO UPDATE SET status=excluded.status,intent=excluded.intent,
                    state_json=excluded.state_json,trace_json=excluded.trace_json,updated_at=excluded.updated_at
            """, (operation_id, request_id, status, state.get("intent", ""), json.dumps(state, ensure_ascii=False),
                  json.dumps(trace, ensure_ascii=False) if trace is not None else None, now, now))

    def recent(self, limit: int = 50) -> list[dict[str, Any]]:
        with sqlite3.connect(self.path) as c:
            c.row_factory = sqlite3.Row
            rows = c.execute("SELECT * FROM kca_operations ORDER BY updated_at DESC LIMIT ?", (max(1, int(limit)),)).fetchall()
        return [dict(row) for row in rows]
