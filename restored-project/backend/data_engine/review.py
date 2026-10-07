# -*- coding: utf-8 -*-
"""Human-review queue for training samples."""
from __future__ import annotations
from pathlib import Path
import sqlite3

class DatasetReview:
    def __init__(self, db_path: str | Path): self.path=Path(db_path)
    def pending(self, limit=100):
        c=sqlite3.connect(self.path); c.row_factory=sqlite3.Row
        rows=[dict(r) for r in c.execute("SELECT * FROM samples WHERE quality='REVIEW' ORDER BY id LIMIT ?",(limit,)).fetchall()]
        c.close(); return rows
    def decide(self, sample_id:int, quality:str, reason:str=''):
        quality=quality.upper()
        if quality not in {'ACCEPTED','REJECTED','REVIEW'}: raise ValueError(quality)
        c=sqlite3.connect(self.path); c.execute("UPDATE samples SET quality=?, reason=? WHERE id=?",(quality,reason,sample_id)); c.commit(); c.close()
