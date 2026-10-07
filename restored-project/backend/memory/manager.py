# -*- coding: utf-8 -*-
"""Typed persistent memory with provenance."""
from __future__ import annotations
from pathlib import Path
import json, sqlite3
from typing import List, Dict, Any, Optional
from data_engine.normalization import normalized_hash

class MemoryManager:
    TYPES={'short_term','long_term','episodic','semantic','project','user'}
    def __init__(self, db_path: str|Path):
        self.path=Path(db_path); self.path.parent.mkdir(parents=True,exist_ok=True)
        c=sqlite3.connect(self.path); c.execute('''CREATE TABLE IF NOT EXISTS memories(id INTEGER PRIMARY KEY, type TEXT, key TEXT, content TEXT, source TEXT, confidence REAL DEFAULT 1.0, hash TEXT UNIQUE, created_at TEXT DEFAULT CURRENT_TIMESTAMP, updated_at TEXT DEFAULT CURRENT_TIMESTAMP)'''); c.execute('CREATE INDEX IF NOT EXISTS idx_memory_type ON memories(type)'); c.close()
    def put(self, type_:str, key:str, content:str, source:str='user', confidence:float=1.0)->int:
        if type_ not in self.TYPES: raise ValueError('invalid memory type')
        h=normalized_hash(f'{type_}\n{key}\n{content}')
        c=sqlite3.connect(self.path); c.execute('INSERT OR REPLACE INTO memories(type,key,content,source,confidence,hash,updated_at) VALUES(?,?,?,?,?,?,CURRENT_TIMESTAMP)',(type_,key,content,source,max(0,min(1,confidence)),h)); c.commit(); mid=c.execute('SELECT id FROM memories WHERE hash=?',(h,)).fetchone()[0]; c.close(); return mid
    def search(self, query:str, limit:int=10, type_:Optional[str]=None)->List[Dict[str,Any]]:
        c=sqlite3.connect(self.path); c.row_factory=sqlite3.Row
        args=[]; sql='SELECT * FROM memories';
        if type_: sql+=' WHERE type=?'; args.append(type_)
        sql+=' ORDER BY updated_at DESC LIMIT 500'
        rows=c.execute(sql,args).fetchall(); c.close(); q=query.lower(); scored=[]
        for r in rows:
            hay=(r['key']+' '+r['content']).lower(); score=sum(1 for word in q.split() if word in hay)/(len(q.split()) or 1); scored.append((score,r))
        scored.sort(key=lambda x:x[0],reverse=True); return [dict(r) for s,r in scored[:limit] if s>0 or not q]
    def delete(self, memory_id:int)->None:
        c=sqlite3.connect(self.path); c.execute('DELETE FROM memories WHERE id=?',(memory_id,)); c.commit(); c.close()
