# -*- coding: utf-8 -*-
"""Append-only local audit log in SQLite."""
from __future__ import annotations
from pathlib import Path
import sqlite3, json, time

class AuditLog:
    def __init__(self, db_path: str | Path):
        self.path=Path(db_path); self.path.parent.mkdir(parents=True,exist_ok=True)
        c=sqlite3.connect(self.path); c.execute("CREATE TABLE IF NOT EXISTS audit(id INTEGER PRIMARY KEY, ts REAL, event TEXT NOT NULL)"); c.commit(); c.close()
    def write(self,event:dict):
        c=sqlite3.connect(self.path); c.execute("INSERT INTO audit(ts,event) VALUES(?,?)",(time.time(),json.dumps(event,ensure_ascii=False))); c.commit(); c.close()
    def recent(self,limit=200):
        c=sqlite3.connect(self.path); c.row_factory=sqlite3.Row; r=[dict(x) for x in c.execute("SELECT * FROM audit ORDER BY id DESC LIMIT ?",(limit,)).fetchall()]; c.close(); return r
