# -*- coding: utf-8 -*-
from __future__ import annotations
from pathlib import Path
import json, sqlite3, random
from typing import Dict, Any

def export_jsonl(db_path: str|Path, out_dir: str|Path, seed: int=42, train_ratio=.9, val_ratio=.05) -> Dict[str,Any]:
    con=sqlite3.connect(db_path); con.row_factory=sqlite3.Row
    rows=con.execute("SELECT sample_hash,normalized,quality FROM samples WHERE quality='ACCEPTED' ORDER BY id").fetchall(); con.close()
    data=[{'id':r['sample_hash'],'text':r['normalized']} for r in rows]
    rnd=random.Random(seed); rnd.shuffle(data)
    n=len(data); nt=int(n*train_ratio); nv=int(n*val_ratio)
    splits={'train':data[:nt],'validation':data[nt:nt+nv],'test':data[nt+nv:]}
    out=Path(out_dir); out.mkdir(parents=True,exist_ok=True)
    for name,items in splits.items():
        with (out/f'{name}.jsonl').open('w',encoding='utf-8') as f:
            for x in items: f.write(json.dumps(x,ensure_ascii=False)+'\n')
    return {'total':n, **{k:len(v) for k,v in splits.items()}, 'output':str(out)}


def export_incremental(db_path: str|Path, out_path: str|Path, after_id: int = 0) -> Dict[str,Any]:
    """Export only newly accepted conversation identities since a previous sample id."""
    con=sqlite3.connect(db_path); con.row_factory=sqlite3.Row
    rows=con.execute("SELECT id,sample_hash,normalized,quality FROM samples WHERE quality='ACCEPTED' AND id>? ORDER BY id",(int(after_id),)).fetchall(); con.close()
    out=Path(out_path); out.parent.mkdir(parents=True,exist_ok=True)
    seen=set(); written=0
    with out.open('w',encoding='utf-8') as f:
        for r in rows:
            h=r['sample_hash']
            if h in seen: continue
            seen.add(h); f.write(json.dumps({'id':h,'text':r['normalized']},ensure_ascii=False)+'\n'); written+=1
    return {'after_id':int(after_id),'samples':written,'output':str(out),'sample_hashes':sorted(seen)}


def export_conversation_incremental(db_path: str|Path, out_path: str|Path, after_ts: float = 0.0, min_quality: float = .6) -> Dict[str,Any]:
    """Export only new/high-quality conversation-memory pairs after a timestamp."""
    con=sqlite3.connect(db_path); con.row_factory=sqlite3.Row
    rows=con.execute("SELECT id,user_text,assistant_text,pair_hash,source,model_version,quality,updated_at FROM conversations WHERE quality>=? AND updated_at>? ORDER BY id",(float(min_quality),float(after_ts))).fetchall(); con.close()
    out=Path(out_path); out.parent.mkdir(parents=True,exist_ok=True)
    seen=set(); written=0; latest=float(after_ts)
    with out.open('w',encoding='utf-8') as f:
        for r in rows:
            h=str(r['pair_hash']); latest=max(latest,float(r['updated_at']))
            if h in seen: continue
            seen.add(h)
            text=(f"<|user|>\n{r['user_text'].strip()}\n<|eot|>\n<|assistant|>\n{r['assistant_text'].strip()}\n<|eot|>\n")
            f.write(json.dumps({'id':h,'text':text,'source':r['source'],'model_version':r['model_version'],'quality':float(r['quality'])},ensure_ascii=False)+'\n'); written+=1
    return {'after_ts':float(after_ts),'samples':written,'output':str(out),'latest_ts':latest,'sample_hashes':sorted(seen)}
