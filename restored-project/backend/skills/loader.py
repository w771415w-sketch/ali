# -*- coding: utf-8 -*-
from __future__ import annotations
from pathlib import Path
import json,re

def discover(root:str|Path='skills'):
    root=Path(root); out=[]
    for p in sorted(list(root.rglob('*.md'))+list(root.rglob('skill.json'))):
        if p.name=='skill.json':
            try:o=json.loads(p.read_text(encoding='utf-8')); o['_path']=str(p); out.append(o)
            except Exception: pass
        else:
            text=p.read_text(encoding='utf-8',errors='ignore'); m=re.search(r'^#\s+(.+)$',text,re.M); out.append({'name':m.group(1).strip() if m else p.stem,'path':str(p),'type':'markdown'})
    return out
