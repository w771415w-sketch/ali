# -*- coding: utf-8 -*-
"""Incremental multilingual hybrid embeddings.

Vector = normalized(concat(ALi learned token embedding, hashed character n-gram signal)).
The character branch keeps retrieval useful before ALI's language model has learned
strong semantic geometry; the learned branch improves as ALI training improves.
"""
from __future__ import annotations
from pathlib import Path
import hashlib, re, sqlite3, numpy as np
TOK=re.compile(r'\w+',re.UNICODE)

def _char_features(text:str,dim:int=256)->np.ndarray:
    s=' '+text.lower()+' '; v=np.zeros(dim,np.float32)
    for n in (2,3,4):
        for i in range(max(0,len(s)-n+1)):
            gram=s[i:i+n]; h=int.from_bytes(hashlib.blake2b(gram.encode('utf-8'),digest_size=4).digest(),'little')%dim; v[h]+=1.0
    norm=np.linalg.norm(v); return v/norm if norm else v

def _learned(model,tokenizer,text:str)->np.ndarray:
    ids=tokenizer.encode(text,add_bos=False,add_eos=False)[:model.config.max_position_embeddings]
    if not ids:return np.zeros(model.config.hidden_size,np.float32)
    import torch
    with torch.no_grad():
        dev=next(model.parameters()).device; x=torch.tensor(ids,dtype=torch.long,device=dev); e=model.embed_tokens(x).mean(0).detach().float().cpu().numpy()
    n=np.linalg.norm(e); return e/n if n else e.astype(np.float32)

def _version(model)->str:
    cfg=getattr(model,'config',None); raw=str(cfg.to_dict() if cfg else '')
    return hashlib.sha256(raw.encode()).hexdigest()[:16]

def embed_text(model,tokenizer,text:str)->np.ndarray:
    a=_learned(model,tokenizer,text); b=_char_features(text); v=np.concatenate([a,b]).astype(np.float32); n=np.linalg.norm(v); return v/n if n else v

def index_store(db_path:str|Path,model,tokenizer,force:bool=False)->dict:
    db=Path(db_path); c=sqlite3.connect(db); c.row_factory=sqlite3.Row
    cols={r[1] for r in c.execute('PRAGMA table_info(chunks)').fetchall()}
    if 'embedding_version' not in cols:c.execute('ALTER TABLE chunks ADD COLUMN embedding_version TEXT')
    ver=_version(model); rows=c.execute('SELECT id,text,embedding,embedding_version FROM chunks ORDER BY id').fetchall(); n=0; skipped=0
    for r in rows:
        if not force and r['embedding'] is not None and r['embedding_version']==ver: skipped+=1; continue
        vec=embed_text(model,tokenizer,r['text']); c.execute('UPDATE chunks SET embedding=?,embedding_version=? WHERE id=?',(vec.astype(np.float16).tobytes(),ver,r['id'])); n+=1
    c.commit(); c.close(); return {'indexed':n,'skipped':skipped,'version':ver,'dimension':int(model.config.hidden_size+256)}

def semantic_search(db_path:str|Path,model,tokenizer,query:str,limit:int=8)->list[dict]:
    q=embed_text(model,tokenizer,query); c=sqlite3.connect(db_path); c.row_factory=sqlite3.Row; rows=c.execute('SELECT c.id,c.text,c.metadata,d.path,d.title,c.embedding FROM chunks c JOIN documents d ON d.id=c.document_id WHERE c.embedding IS NOT NULL').fetchall(); scored=[]; qwords=set(TOK.findall(query.lower()))
    for r in rows:
        try:v=np.frombuffer(r['embedding'],dtype=np.float16).astype(np.float32)
        except Exception:continue
        if v.size!=q.size:continue
        semantic=float(np.dot(q,v)); words=set(TOK.findall(r['text'].lower())); lexical=len(qwords&words)/(len(qwords) or 1); score=.82*semantic+.18*lexical; scored.append((score,r))
    scored.sort(key=lambda x:x[0],reverse=True); out=[]
    for score,r in scored[:limit]:
        d=dict(r); d.pop('embedding',None); d['hybrid_score']=score; out.append(d)
    c.close(); return out
