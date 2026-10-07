# -*- coding: utf-8 -*-
from __future__ import annotations
from pathlib import Path
import json, hashlib
from typing import Dict,Any

def fingerprint_dataset(paths)->str:
    h=hashlib.sha256()
    for p in sorted(map(str,paths)):
        q=Path(p); h.update(q.name.encode()); h.update(q.read_bytes())
    return h.hexdigest()

def manifest(path:str|Path, **kwargs)->Path:
    p=Path(path); p.parent.mkdir(parents=True,exist_ok=True); p.write_text(json.dumps(kwargs,ensure_ascii=False,indent=2,default=str),encoding='utf-8'); return p

def list_checkpoints(root:str|Path):
    root=Path(root); return sorted([p for p in root.iterdir() if p.is_dir() and (p/'checkpoint.pt').exists()],key=lambda x:x.name)
