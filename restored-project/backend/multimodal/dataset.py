# -*- coding: utf-8 -*-
"""Manifest format for multimodal alignment examples."""
from __future__ import annotations
from pathlib import Path
import json

def write_manifest(rows,out):
    p=Path(out); p.parent.mkdir(parents=True,exist_ok=True)
    with p.open('w',encoding='utf-8') as f:
        for r in rows:f.write(json.dumps(r,ensure_ascii=False)+'\n')
    return p
