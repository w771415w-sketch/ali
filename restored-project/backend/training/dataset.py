# -*- coding: utf-8 -*-
from __future__ import annotations
from pathlib import Path
import json, sqlite3, hashlib
from typing import Dict, Any

def _write(rows, path):
    path=Path(path); path.parent.mkdir(parents=True,exist_ok=True)
    with path.open('w',encoding='utf-8') as f:
        for r in rows: f.write(json.dumps(r,ensure_ascii=False)+'\n')

def build_chat_dataset(db_path:str|Path,out_dir:str|Path)->Dict[str,Any]:
    c=sqlite3.connect(db_path); c.row_factory=sqlite3.Row
    rows=c.execute("SELECT sample_hash,normalized FROM samples WHERE quality='ACCEPTED' AND role='conversation' ORDER BY id").fetchall(); c.close()
    out=Path(out_dir); n=len(rows); train_n=max(1,int(n*.9)) if n else 0; val_n=max(1,int(n*.05)) if n>=3 else max(0,n-train_n); train=rows[:train_n]; val=rows[train_n:train_n+val_n]; test=rows[train_n+val_n:]
    for name,part in [('train',train),('validation',val),('test',test)]: _write([{'id':r['sample_hash'],'text':r['normalized']} for r in part],out/f'chat_{name}.jsonl')
    return {'mode':'chat_sft','total':len(rows),'train':len(train),'validation':len(val),'test':len(test)}

def build_causal_dataset(db_path:str|Path,out_dir:str|Path)->Dict[str,Any]:
    c=sqlite3.connect(db_path); c.row_factory=sqlite3.Row
    rows=c.execute('SELECT chunk_hash,text FROM chunks ORDER BY id').fetchall(); c.close()
    data=[{'id':r['chunk_hash'],'text':r['text']} for r in rows if r['text'].strip()]
    out=Path(out_dir); n=len(data); nt=max(1,int(n*.9)) if n else 0; nv=max(1,int(n*.05)) if n else 0
    for name,part in [('train',data[:nt]),('validation',data[nt:nt+nv]),('test',data[nt+nv:])]: _write(part,out/f'cpt_{name}.jsonl')
    return {'mode':'continued_pretraining','total':n,'train':len(data[:nt]),'validation':len(data[nt:nt+nv]),'test':len(data[nt+nv:])}
