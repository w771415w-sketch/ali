# -*- coding: utf-8 -*-
"""Persistent artifact ledger: one identity, one processing history.

Prevents re-ingesting or re-training the same normalized record and prevents a
GGUF snapshot from being rebuilt under the same model/data identity.
"""
from __future__ import annotations
from pathlib import Path
import hashlib, json, sqlite3, time
from typing import Any, Iterable

class ArtifactLedger:
    def __init__(self,path:str|Path):
        self.path=Path(path); self.path.parent.mkdir(parents=True,exist_ok=True)
        c=sqlite3.connect(self.path)
        c.executescript('''
        CREATE TABLE IF NOT EXISTS artifacts(
          identity TEXT PRIMARY KEY, kind TEXT NOT NULL, source TEXT, metadata TEXT,
          first_seen REAL NOT NULL, last_seen REAL NOT NULL, processed_count INTEGER DEFAULT 0);
        CREATE TABLE IF NOT EXISTS runs(
          id INTEGER PRIMARY KEY AUTOINCREMENT, identity TEXT NOT NULL, action TEXT NOT NULL,
          input_identity TEXT, output_identity TEXT, metadata TEXT, created_at REAL NOT NULL);
        CREATE INDEX IF NOT EXISTS idx_runs_identity ON runs(identity,action);
        '''); c.close()
    def seen(self,identity:str,kind:str|None=None)->bool:
        c=sqlite3.connect(self.path); row=c.execute('SELECT 1 FROM artifacts WHERE identity=?'+(' AND kind=?' if kind else ''),(identity,kind) if kind else (identity,)).fetchone(); c.close(); return bool(row)
    def record(self,identity:str,kind:str,source:str='',metadata:dict|None=None)->bool:
        now=time.time(); c=sqlite3.connect(self.path)
        cur=c.execute('INSERT OR IGNORE INTO artifacts(identity,kind,source,metadata,first_seen,last_seen) VALUES(?,?,?,?,?,?)',(identity,kind,source,json.dumps(metadata or {},ensure_ascii=False),now,now))
        if cur.rowcount==0:c.execute('UPDATE artifacts SET last_seen=?,processed_count=processed_count+1 WHERE identity=?',(now,identity))
        c.commit(); c.close(); return cur.rowcount==1
    def record_run(self,identity,action,input_identity='',output_identity='',metadata=None):
        c=sqlite3.connect(self.path); c.execute('INSERT INTO runs(identity,action,input_identity,output_identity,metadata,created_at) VALUES(?,?,?,?,?,?)',(identity,action,input_identity,output_identity,json.dumps(metadata or {},ensure_ascii=False),time.time())); c.commit(); c.close()
    def action_done(self,identity:str,action:str)->bool:
        c=sqlite3.connect(self.path); row=c.execute('SELECT 1 FROM runs WHERE identity=? AND action=? LIMIT 1',(identity,action)).fetchone(); c.close(); return bool(row)
    def status(self,identity:str)->dict[str,Any]:
        c=sqlite3.connect(self.path); c.row_factory=sqlite3.Row; a=c.execute('SELECT * FROM artifacts WHERE identity=?',(identity,)).fetchone(); runs=c.execute('SELECT action,output_identity,created_at FROM runs WHERE identity=? ORDER BY id',(identity,)).fetchall(); c.close(); return {'artifact':dict(a) if a else None,'runs':[dict(r) for r in runs]}

def canonical_json(obj:Any)->str:return json.dumps(obj,ensure_ascii=False,sort_keys=True,separators=(',',':'))
def identity_from_records(ids:Iterable[str],namespace:str='dataset')->str:
    h=hashlib.sha256(); h.update(namespace.encode('utf-8')); h.update(b'\0')
    for x in sorted(set(map(str,ids))):h.update(x.encode('utf-8'));h.update(b'\n')
    return h.hexdigest()
def file_identity(path:str|Path)->str:
    p=Path(path); h=hashlib.sha256()
    if p.is_file():
        with p.open('rb') as f:
            for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
        return h.hexdigest()
    for f in sorted(x for x in p.rglob('*') if x.is_file()):
        h.update(str(f.relative_to(p)).encode('utf-8')); h.update(file_identity(f).encode('ascii'))
    return h.hexdigest()
