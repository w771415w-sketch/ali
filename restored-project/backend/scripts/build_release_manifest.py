# -*- coding: utf-8 -*-
from __future__ import annotations
from pathlib import Path
import hashlib,json,time
ROOT=Path(__file__).resolve().parent.parent
SKIP={'.git','.pytest_cache','__pycache__','.venv','checkpoints','weights'}
TEXT_EXT={'.py','.pyw','.bat','.cmd','.ps1','.json','.jsonl','.md','.txt','.toml','.ini','.cfg','.yaml','.yml','.html','.css','.js','.legacy'}
def sha(p):
    h=hashlib.sha256()
    with p.open('rb') as f:
        for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
    return h.hexdigest()
rows=[]
for p in sorted(ROOT.rglob('*')):
    if not p.is_file() or any(x in SKIP for x in p.parts):continue
    if p.name.endswith('.pyc') or p.suffix.lower() not in TEXT_EXT:continue
    if p.name == 'RELEASE_MANIFEST.json':continue
    rows.append({'path':str(p.relative_to(ROOT)).replace('\\','/'),'size':p.stat().st_size,'sha256':sha(p)})
out={'name':'ALI AI','version':'2.5.0','codename':'Unified-KCA-P50','generated_at':time.time(),'files':rows}
(ROOT/'RELEASE_MANIFEST.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'files':len(rows),'manifest':str(ROOT/'RELEASE_MANIFEST.json')},ensure_ascii=False,indent=2))
