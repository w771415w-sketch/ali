# -*- coding: utf-8 -*-
"""Persistent local knowledge store with provenance and hybrid retrieval."""
from __future__ import annotations
import json, math, re, sqlite3
from pathlib import Path
from typing import List, Dict, Any
from data_engine.normalization import normalized_hash

TOK=re.compile(r"\w+", re.UNICODE)
_AR_DIACRITICS = re.compile(r"[\u064B-\u065F\u0670\u06D6-\u06ED]")

def _norm_token(token: str) -> str:
    t = _AR_DIACRITICS.sub("", str(token).lower().replace("ـ", ""))
    t = t.translate(str.maketrans({"أ":"ا", "إ":"ا", "آ":"ا", "ى":"ي"}))
    return t

def token_variants(token: str) -> set[str]:
    t = _norm_token(token)
    out = {t}
    if len(t) > 4 and t.startswith("ال"):
        out.add(t[2:])
    if len(t) > 5 and t.startswith(("وال", "بال", "كال", "فال")):
        out.add(t[2:])
        if t.startswith("وال"):
            out.add(t[3:])
    return {x for x in out if x}

def tokens(s:str)->List[str]: return [_norm_token(x) for x in TOK.findall(str(s).lower())]

class KnowledgeStore:
    def __init__(self, db_path: str|Path):
        self.path=Path(db_path); self.path.parent.mkdir(parents=True,exist_ok=True)
        c=sqlite3.connect(self.path)
        c.executescript('''
        CREATE TABLE IF NOT EXISTS documents(id INTEGER PRIMARY KEY, path TEXT UNIQUE, title TEXT, kind TEXT, sha256 TEXT, metadata TEXT, created_at TEXT DEFAULT CURRENT_TIMESTAMP, updated_at TEXT DEFAULT CURRENT_TIMESTAMP);
        CREATE TABLE IF NOT EXISTS chunks(id INTEGER PRIMARY KEY, document_id INTEGER, chunk_hash TEXT UNIQUE, text TEXT, metadata TEXT, embedding BLOB, FOREIGN KEY(document_id) REFERENCES documents(id));
        CREATE VIRTUAL TABLE IF NOT EXISTS chunks_fts USING fts5(text, content='chunks', content_rowid='id');
        '''); c.close()
    def add_document(self,path,title,kind,metadata,chunks,chunk_metadata=None):
        """Upsert a document without breaking chunk foreign keys.

        SQLite INSERT OR REPLACE deletes the old row before inserting a new one;
        that is unsafe here because chunks reference the document id. We therefore
        update an existing document in place and rebuild its chunks transactionally.
        """
        con=sqlite3.connect(self.path); con.execute('PRAGMA foreign_keys=ON')
        try:
            path_s=str(path); chunk_list=[str(t) for t in chunks if str(t).strip()]
            chunk_meta_list=list(chunk_metadata or [])
            sha=normalized_hash('\n'.join(chunk_list)); meta=json.dumps(metadata,ensure_ascii=False)
            row=con.execute('SELECT id FROM documents WHERE path=?',(path_s,)).fetchone()
            if row:
                did=int(row[0])
                # Remove old FTS rows before deleting chunks for this document.
                ids=[r[0] for r in con.execute('SELECT id FROM chunks WHERE document_id=?',(did,)).fetchall()]
                if ids:
                    con.executemany('DELETE FROM chunks_fts WHERE rowid=?',((i,) for i in ids))
                    con.execute('DELETE FROM chunks WHERE document_id=?',(did,))
                con.execute('UPDATE documents SET title=?,kind=?,sha256=?,metadata=?,updated_at=CURRENT_TIMESTAMP WHERE id=?',(title,kind,sha,meta,did))
            else:
                cur=con.execute('INSERT INTO documents(path,title,kind,sha256,metadata,updated_at) VALUES(?,?,?,?,?,CURRENT_TIMESTAMP)',(path_s,title,kind,sha,meta))
                did=int(cur.lastrowid)
            for idx,t in enumerate(chunk_list):
                ch=normalized_hash(t)
                md={'index':idx}
                if idx < len(chunk_meta_list) and isinstance(chunk_meta_list[idx], dict):
                    md.update(chunk_meta_list[idx])
                cur=con.execute('INSERT OR IGNORE INTO chunks(document_id,chunk_hash,text,metadata) VALUES(?,?,?,?)',(did,ch,t,json.dumps(md,ensure_ascii=False)))
                if cur.rowcount:
                    con.execute('INSERT INTO chunks_fts(rowid,text) VALUES(?,?)',(cur.lastrowid,t))
            con.commit(); return did
        except Exception:
            con.rollback(); raise
        finally:
            con.close()

    def training_qa_match(self, query: str, threshold: float = 0.80) -> Dict[str, Any] | None:
        """Match an imported training question against chunk-level Q/A metadata.

        Imported conversation bundles are indexed one Q/A pair per chunk. This gives
        exact/fuzzy question matching a deterministic path before a tiny local model
        or generic project FAQ can produce an unrelated response.
        """
        qn = ' '.join(tokens(query))
        if not qn:
            return None
        con=sqlite3.connect(self.path); con.row_factory=sqlite3.Row
        rows=con.execute("SELECT c.text,c.metadata,d.path,d.title,d.metadata AS document_metadata FROM chunks c JOIN documents d ON d.id=c.document_id WHERE c.metadata LIKE '%training_question%'").fetchall()
        con.close()
        best=None
        from difflib import SequenceMatcher
        qnorm=' '.join(_norm_token(x) for x in TOK.findall(str(query).lower()))
        for r in rows:
            try: md=json.loads(r['metadata'] or '{}')
            except Exception: md={}
            tq=str(md.get('training_question') or '').strip()
            if not tq: continue
            tnorm=' '.join(_norm_token(x) for x in TOK.findall(tq.lower()))
            qvars=set()
            tvars=set()
            for x in TOK.findall(str(query).lower()): qvars.update(token_variants(x))
            for x in TOK.findall(tq.lower()): tvars.update(token_variants(x))
            if not tvars: continue
            inter=len(qvars & tvars); union=max(1,len(qvars | tvars))
            j=inter/union
            seq=SequenceMatcher(None,qnorm,tnorm).ratio()
            containment=sum(1 for x in qvars if len(x)>=3 and any(x in y or y in x for y in tvars))/max(1,len(qvars))
            score=.45*seq+.40*j+.15*containment
            if qnorm==tnorm: score=1.0
            if best is None or score>best[0]:
                best=(score,r,md)
        if not best or best[0] < threshold:
            return None
        score,r,md=best
        return {
            'score': round(float(score),4),
            'question': str(md.get('training_question') or ''),
            'answer': str(md.get('training_answer') or '').strip(),
            'path': str(r['path'] or ''),
            'title': str(r['title'] or r['path'] or ''),
            'sample_id': str(md.get('training_sample_id') or ''),
            'source': 'imported-training-qa',
        }

    def search(self, query:str, limit:int=8)->List[Dict[str,Any]]:
        q=' '.join(tokens(query)); con=sqlite3.connect(self.path); con.row_factory=sqlite3.Row
        rows=[]
        if q:
            try:
                rows=con.execute('SELECT c.id,c.text,c.metadata,d.path,d.title,bm25(chunks_fts) score FROM chunks_fts JOIN chunks c ON c.id=chunks_fts.rowid JOIN documents d ON d.id=c.document_id WHERE chunks_fts MATCH ? ORDER BY score LIMIT ?', (q,limit*4)).fetchall()
            except Exception:
                rows=[]
        # Always retain a normalized lexical fallback. This handles Arabic morphology
        # and mixed punctuation better than SQLite FTS MATCH alone.
        cand=con.execute('SELECT c.id,c.text,c.metadata,d.path,d.title,d.metadata AS document_metadata FROM chunks c JOIN documents d ON d.id=c.document_id ORDER BY c.id DESC LIMIT 4000').fetchall()
        qt=set()
        for x in TOK.findall(str(query).lower()): qt.update(token_variants(x))
        if qt:
            scored=[]
            for r in cand:
                ct=set()
                for x in tokens(r['text']): ct.update(token_variants(x))
                overlap=len(qt & ct)
                partial=sum(1 for qx in qt if any((qx in tx or tx in qx) and min(len(qx),len(tx))>=3 for tx in ct))
                score=(overlap*2 + partial) / max(1, len(qt))
                try:
                    md = json.loads(r['document_metadata'] or '{}') if r['document_metadata'] else {}
                except Exception:
                    md = {}
                score += float(md.get('priority', 0) or 0) / 20.0
                title = str(r['title'] or '').lower()
                qtext = str(query or '').lower()
                if ('thinkpad' in qtext or 'جهاز' in qtext or 'معالج' in qtext or 'ram' in qtext or 'gpu' in qtext or 'vram' in qtext) and ('thinkpad' in title or 'user_profile' in title or 'arabic_reference' in title):
                    score += 0.75
                if 'deterministic_faq' in title:
                    score += 5.0
                if score>0:
                    scored.append((score,r))
            scored.sort(key=lambda x:x[0], reverse=True)
            lexical=[]
            for score, r in scored[:limit]:
                item=dict(r)
                item['score']=round(float(score), 4)
                lexical.append(item)
            # Prefer lexical hits when they have meaningful overlap. Otherwise keep FTS results.
            if lexical:
                rows=lexical
        out=[dict(r) for r in rows[:limit]]; con.close()
        return out
