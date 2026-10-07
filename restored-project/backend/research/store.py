# -*- coding: utf-8 -*-
from __future__ import annotations
from pathlib import Path
from knowledge.store import KnowledgeStore

def store_documents(store: KnowledgeStore, documents: list[dict], query: str='') -> dict:
    stored=0; skipped=0; rows=[]
    for d in documents or []:
        url=str(d.get('url') or '').strip(); text=str(d.get('text') or '').strip()
        if not text or not url: skipped+=1; continue
        title=str(d.get('title') or url); did=store.add_document(url,title,'web',{'url':url,'query':query,'retrieved_at':__import__('time').time(),'source_type':'web_research','eligible_for_training':False},[text[i:i+1800] for i in range(0,len(text),1800)])
        rows.append({'document_id':did,'url':url,'title':title}); stored+=1
    return {'stored':stored,'skipped':skipped,'documents':rows}
