# -*- coding: utf-8 -*-
"""Safe public download helper. Files are kept in ALI's dedicated downloads directory."""
from __future__ import annotations
from pathlib import Path
from urllib.request import Request, urlopen
import hashlib, json, ssl, time
from research.web import _safe_public_url

def download(url: str, root: str|Path='downloads', max_mb:int=200) -> dict:
    _safe_public_url(url); root=Path(root); root.mkdir(parents=True,exist_ok=True)
    name=Path(url.split('?',1)[0]).name or ('download-'+hashlib.sha256(url.encode()).hexdigest()[:12])
    out=root/name
    req=Request(url,headers={'User-Agent':'ALI-Studio/3.0'})
    h=hashlib.sha256(); total=0
    with urlopen(req,timeout=30,context=ssl.create_default_context()) as r, out.open('wb') as f:
        while True:
            b=r.read(1024*1024)
            if not b: break
            total += len(b)
            if total > max_mb*1024*1024: raise ValueError('download exceeds configured size limit')
            h.update(b); f.write(b)
    meta={'url':url,'path':str(out.resolve()),'sha256':h.hexdigest(),'size':total,'downloaded_at':time.time()}
    out.with_suffix(out.suffix+'.json').write_text(json.dumps(meta,ensure_ascii=False,indent=2),encoding='utf-8')
    return meta
