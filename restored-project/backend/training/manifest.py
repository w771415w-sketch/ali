# -*- coding: utf-8 -*-
from __future__ import annotations
from pathlib import Path
import hashlib,json,time
def sha256_file(path:str|Path,chunk:int=1024*1024)->str:
    h=hashlib.sha256(); p=Path(path)
    with p.open('rb') as f:
        while True:
            b=f.read(chunk)
            if not b: break
            h.update(b)
    return h.hexdigest()
def dataset_manifest(paths,extra=None):
    items=[]
    for raw in paths:
        p=Path(raw)
        if p.exists() and p.is_file(): items.append({"path":str(p),"size":p.stat().st_size,"sha256":sha256_file(p)})
    return {"kind":"dataset","created_at":time.time(),"files":items,"extra":extra or {}}
def write_manifest(path,data):
    p=Path(path); p.parent.mkdir(parents=True,exist_ok=True); p.write_text(json.dumps(data,ensure_ascii=False,indent=2,sort_keys=True),encoding='utf-8'); return p
