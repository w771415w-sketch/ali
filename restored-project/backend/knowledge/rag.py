# -*- coding: utf-8 -*-
from __future__ import annotations
from typing import List, Dict, Any
from .store import KnowledgeStore

def build_context(store: KnowledgeStore, query: str, limit:int=5, max_chars:int=7000)->Dict[str,Any]:
    hits=store.search(query,limit=limit); used=0; blocks=[]
    for i,h in enumerate(hits,1):
        t=h.get('text','').strip()
        if not t: continue
        remain=max_chars-used
        if remain<=0: break
        t=t[:remain]
        blocks.append(f"[S{i}] {h.get('title') or h.get('path')}\n{t}")
        used += len(t)
    return {'context':'\n\n'.join(blocks),'sources':[{'id':f'S{i+1}','path':h.get('path'),'title':h.get('title'),'score':h.get('score')} for i,h in enumerate(hits)],'chars':used}
