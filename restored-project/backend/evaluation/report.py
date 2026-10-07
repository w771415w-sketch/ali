# -*- coding: utf-8 -*-
from __future__ import annotations
from pathlib import Path
import json,time
def compare(baseline:dict|None,candidate:dict|None)->dict:
    a=baseline or {}; b=candidate or {}; out={"created_at":time.time(),"baseline":a,"candidate":b,"deltas":{}}
    for k in set(a)|set(b):
        if isinstance(a.get(k),(int,float)) and isinstance(b.get(k),(int,float)): out["deltas"][k]=b[k]-a[k]
    return out
def save_report(path,report):
    p=Path(path); p.parent.mkdir(parents=True,exist_ok=True); p.write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8'); return p
