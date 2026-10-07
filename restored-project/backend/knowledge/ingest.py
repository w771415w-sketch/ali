# -*- coding: utf-8 -*-
"""Bridge harvested/remote documents into the persistent RAG knowledge store."""
from __future__ import annotations
from pathlib import Path
import json, sqlite3
from knowledge.store import KnowledgeStore
from data_engine.normalization import redact_secrets, normalized_hash


def ingest_harvest(harvest_db: str | Path, knowledge_db: str | Path) -> dict:
    src=Path(harvest_db); store=KnowledgeStore(knowledge_db); c=sqlite3.connect(src); c.row_factory=sqlite3.Row
    rows=c.execute('SELECT id,path,kind,sha256,metadata,warning FROM sources WHERE kind="document"').fetchall(); docs=chunks=0
    for r in rows:
        cr=c.execute('SELECT text,metadata FROM chunks WHERE source_id=? ORDER BY id',(r['id'],)).fetchall()
        if not cr: continue
        texts=[x['text'] for x in cr if x['text'].strip()]
        title=Path(r['path']).name
        meta=json.loads(r['metadata'] or '{}') if r['metadata'] else {}
        did=store.add_document(r['path'],title,r['kind'],{**meta,'source_hash':r['sha256'],'warning':r['warning']},texts); docs+=1; chunks+=len(texts)
    c.close(); return {'documents':docs,'chunks':chunks,'knowledge_db':str(knowledge_db)}


def ingest_web_documents(result:dict, knowledge_db: str | Path) -> dict:
    store=KnowledgeStore(knowledge_db); docs=chunks=0
    for d in result.get('documents',[]):
        text,_=redact_secrets(str(d.get('text','')))
        if not text.strip(): continue
        parts=[text[i:i+1800] for i in range(0,len(text),1800)]
        store.add_document(d.get('url',''),d.get('title',''), 'web', {'url':d.get('url',''),'query':result.get('query',''),'source':'web_research'},parts)
        docs+=1; chunks+=len(parts)
    return {'documents':docs,'chunks':chunks}
