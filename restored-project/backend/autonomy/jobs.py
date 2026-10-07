# -*- coding: utf-8 -*-
"""Persistent local job scheduler for safe self-training/improvement."""
from __future__ import annotations
from pathlib import Path
import sqlite3, json, datetime
from typing import Any

class JobStore:
    def __init__(self, db_path: str | Path):
        self.path = Path(db_path); self.path.parent.mkdir(parents=True, exist_ok=True)
        c=sqlite3.connect(self.path); c.execute("""CREATE TABLE IF NOT EXISTS jobs(
            id INTEGER PRIMARY KEY, kind TEXT NOT NULL, status TEXT NOT NULL,
            payload TEXT NOT NULL, result TEXT, created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            started_at TEXT, finished_at TEXT, error TEXT)"""); c.commit(); c.close()
    def add(self, kind: str, payload: dict[str,Any]) -> int:
        c=sqlite3.connect(self.path); cur=c.execute("INSERT INTO jobs(kind,status,payload) VALUES(?,?,?)",(kind,'queued',json.dumps(payload,ensure_ascii=False))); c.commit(); jid=int(cur.lastrowid); c.close(); return jid
    def claim_next(self):
        c=sqlite3.connect(self.path); c.row_factory=sqlite3.Row
        row=c.execute("SELECT * FROM jobs WHERE status='queued' ORDER BY id LIMIT 1").fetchone()
        if not row: c.close(); return None
        c.execute("UPDATE jobs SET status='running', started_at=? WHERE id=?",(datetime.datetime.utcnow().isoformat(),row['id'])); c.commit(); c.close(); return dict(row)
    def finish(self, job_id:int, result:dict[str,Any]|None=None, error:str=''):
        c=sqlite3.connect(self.path); status='failed' if error else 'completed'; c.execute("UPDATE jobs SET status=?,result=?,error=?,finished_at=? WHERE id=?",(status,json.dumps(result or {},ensure_ascii=False),error,datetime.datetime.utcnow().isoformat(),job_id)); c.commit(); c.close()
    def list(self, limit=100):
        c=sqlite3.connect(self.path); c.row_factory=sqlite3.Row; rows=[dict(r) for r in c.execute("SELECT * FROM jobs ORDER BY id DESC LIMIT ?",(limit,)).fetchall()]; c.close(); return rows
