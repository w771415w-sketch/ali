READABLE_DB = {"kanban.db", "projects.db"}

def safe_root(path: str | Path) -> Path:
    return Path(path).expanduser().resolve()

def inside(root: Path, candidate: Path) -> bool:
    try:
        candidate.resolve().relative_to(root.resolve())
        return True
    except ValueError:
        return False

def guard_file(root: Path, path: str | Path, *, allow_db=False) -> Path:
    p = (root / path).resolve() if not Path(path).is_absolute() else Path(path).resolve()
    if not inside(root, p):
        raise PermissionError("Hermes path escapes configured root")
    if p.name.lower() in BLOCKED_NAMES or p.suffix.lower() in {".key", ".pem", ".p12", ".pfx"}:
        raise PermissionError(f"Blocked sensitive Hermes file: {p.name}")
    rel = p.relative_to(root).as_posix()
    if allow_db and p.name in READABLE_DB:
        return p
    if rel in READABLE_FILES or rel.startswith("memories/") or rel.startswith("skills/"):
        return p
    raise PermissionError(f"Hermes path is not in the read-only allowlist: {rel}")
```

---

### `142/588` `backend/knowledge/__init__.py`

- **المسار الكامل:** `F:\1f\p\ALI_Studio_Pro_Design4_4.6.0\04_Adaptive_Hybrid\backend/knowledge/__init__.py`
- **الحجم:** 1 بايت (0.0 KB)
- **الامتداد:** `.py`

```python

```

---

### `143/588` `backend/knowledge/embeddings.py`

- **المسار الكامل:** `F:\1f\p\ALI_Studio_Pro_Design4_4.6.0\04_Adaptive_Hybrid\backend/knowledge/embeddings.py`
- **الحجم:** 3527 بايت (3.4 KB)
- **الامتداد:** `.py`

```python
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
```

---

### `144/588` `backend/knowledge/ingest.py`

- **المسار الكامل:** `F:\1f\p\ALI_Studio_Pro_Design4_4.6.0\04_Adaptive_Hybrid\backend/knowledge/ingest.py`
- **الحجم:** 1743 بايت (1.7 KB)
- **الامتداد:** `.py`

```python
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
```

---

### `145/588` `backend/knowledge/rag.py`

- **المسار الكامل:** `F:\1f\p\ALI_Studio_Pro_Design4_4.6.0\04_Adaptive_Hybrid\backend/knowledge/rag.py`
- **الحجم:** 740 بايت (0.7 KB)
- **الامتداد:** `.py`

```python
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
```

---

### `146/588` `backend/knowledge/store.py`

- **المسار الكامل:** `F:\1f\p\ALI_Studio_Pro_Design4_4.6.0\04_Adaptive_Hybrid\backend/knowledge/store.py`
- **الحجم:** 9168 بايت (9.0 KB)
- **الامتداد:** `.py`

```python
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
```

---

### `147/588` `backend/knowledge_seed/ALI_4_5_2_KNOWLEDGE_INDEX.md`

- **المسار الكامل:** `F:\1f\p\ALI_Studio_Pro_Design4_4.6.0\04_Adaptive_Hybrid\backend/knowledge_seed/ALI_4_5_2_KNOWLEDGE_INDEX.md`
- **الحجم:** 1101 بايت (1.1 KB)
- **الامتداد:** `.md`

```markdown
# ALI 4.5.2 Knowledge & Training Index

## Authoritative local knowledge
1. `THINKPAD_P50_COMPLETE_USER_PROFILE.md` — user-provided hardware/system profile.
2. `ALI_V4_4_COMPLETE_REPORT.md` — prior project audit, implementation history, known defects and evidence.
3. `THINKPAD_P50_USER_PROFILE.md` — compact engineering profile.

## Curated behavior/training
1. `../training/examples/ALI_MASTER_TRAINING_4.5.2.md`
2. `../training/examples/ALI_Professional_QA_P50_V2.md`
3. root/import packs `ALI_Conversation_Training_Core_V2.md` and `ALI_Conversation_Training_V1.md`

## Routing rule
- Device/project facts and long documents -> RAG/Knowledge.
- Mutable user preferences -> Memory.
- General behavioral patterns, tool-use patterns, verification discipline and stable task procedures -> Training/LoRA.
- GGUF -> local inference artifact; it is never treated as a training source by itself.

## Truthfulness rule
The UI must distinguish imported, validated, trained, evaluated, promoted and runtime-loaded states. A progress bar or registry flag alone is not evidence of behavioral improvement.
```

---

### `148/588` `backend/knowledge_seed/ALI_CORE_QA_AR.md`

- **المسار الكامل:** `F:\1f\p\ALI_Studio_Pro_Design4_4.6.0\04_Adaptive_Hybrid\backend/knowledge_seed/ALI_CORE_QA_AR.md`
- **الحجم:** 4333 بايت (4.2 KB)
- **الامتداد:** `.md`

```markdown
# ALI — أسئلة وأجوبة تشغيلية أساسية

هذه أمثلة مرجعية قصيرة تساعد ALI على الإجابة عن الأسئلة المتكررة الخاصة بالمشروع.

## السؤال: ما الفرق بين Memory وRAG وTraining؟
**User:** ما الفرق بين الذاكرة وRAG والتدريب؟
**Assistant:** الذاكرة تحفظ معلومات وسياقاً قابلاً للتحديث، وRAG يسترجع معلومات من مصادر عند الإجابة دون تغيير الأوزان، أما التدريب فيحدث الأوزان أو الـadapter. لا تعتبر الوصول إلى ملف عبر RAG دليلاً على أن النموذج تعلم الملف داخل الأوزان.

## السؤال: كيف أضيف ملف MD للتدريب؟
**User:** كيف أضيف ملف MD؟
**Assistant:** اسحب ملف Markdown إلى مركز التدريب أو اختره من زر ملفات Windows. يفحصه ALI ويزيل التكرار ويستخرج أزواج User/Assistant ثم ينشئ Dataset جديداً. إذا لم يجد أزواج محادثة صريحة يبقي الملف كمعرفة RAG بدلاً من إنشاء تدريب وهمي.

## السؤال: متى يصبح الإصدار الجديد Active؟
**User:** متى يصبح النموذج الجديد Active؟
**Assistant:** بعد اكتمال التدريب وصحة الـartifact واجتياز Evaluation وRegression وبوابة Promotion. قبل ذلك يبقى Candidate ويظل الإصدار السابق متاحاً للرجوع.

## السؤال: كيف يتطور v1 إلى v2؟
**User:** كيف يعمل التدريب التراكمي؟
**Assistant:** يبدأ الإصدار التالي من Active السابق ويستخدم البيانات الجديدة فقط بعد منع التكرار، ثم يُنتج Candidate جديداً ويخضع للتقييم والترقية. المسار هو v1 ثم v2 ثم v3 وهكذا مع الاحتفاظ بالإصدارات السابقة.

## السؤال: ما مواصفات جهاز ALI المستهدف؟
**User:** ما مواصفات جهازي؟
**Assistant:** الجهاز المستهدف هو Lenovo ThinkPad P50 بمعالج Intel Core i7-6820HQ، و32 GB DDR4، وبطاقة NVIDIA Quadro M1000M بذاكرة 2 GB GDDR5، مع شاشة 1920×1080.

## السؤال: ماذا يفعل ALI عند فشل اختبار؟
**User:** ماذا تفعل إذا فشل اختبار بعد تعديل؟
**Assistant:** لا أعتبر المهمة ناجحة. أقرأ الخطأ والنتيجة، أحدد السبب، أصلح التغيير، ثم أعيد الاختبار والتحقق من الانحدار. إذا فشلت دورة تدريب، تبقى بياناتها قابلة لإعادة المحاولة ولا يتم اعتماد الإصدار الفاشل.

## السؤال: هل 100% في شريط التدريب يعني أن النموذج جيد؟
**User:** هل اكتمال شريط التدريب يعني أن النموذج أصبح جيداً؟
**Assistant:** لا. 100% يعني اكتمال العملية فقط. يجب تقييم النموذج على Validation/Test وأسئلة جديدة والتحقق من أن Runtime يستخدم الإصدار الجديد فعلياً.

## السؤال: كيف يستخدم ALI GPU؟
**User:** كيف تستخدم GPU وVRAM؟
**Assistant:** في Auto يختبر ALI CUDA فعلياً ويقيس الذاكرة الحرة ثم يختار حمولة متناسبة. إذا كانت VRAM غير معروفة أو غير كافية، يعود إلى CPU بدلاً من المخاطرة بتجميد الجهاز. وعلى Quadro M1000M ذات 2 GB يمكن استخدام offload جزئي في llama.cpp عند توفر مساحة حرة كافية.

## السؤال: هل يمكن لـALI تنفيذ مشروع؟
**User:** هل يستطيع ALI إنشاء أو تعديل مشروع؟
**Assistant:** نعم من ناحية المعمارية: يفهم الطلب ويحدد النية ويبني خطة ثم يستخدم الأدوات المصرح بها لإنشاء أو تعديل الملفات، وبعد التنفيذ يقرأ النتائج ويجري الاختبارات والتحقق قبل إعلان النجاح.
```

---

### `149/588` `backend/knowledge_seed/ALI_CURRENT_STATUS_4.5.2.md`

- **المسار الكامل:** `F:\1f\p\ALI_Studio_Pro_Design4_4.6.0\04_Adaptive_Hybrid\backend/knowledge_seed/ALI_CURRENT_STATUS_4.5.2.md`
- **الحجم:** 1720 بايت (1.7 KB)
- **الامتداد:** `.md`

```markdown
# ALI Studio Pro 4.5.2 — Current Authoritative Status

This document overrides historical claims in earlier audit reports when they conflict. It describes the intended and tested state of the 4.5.2 rebuild.

## Target machine
Lenovo ThinkPad P50, Intel i7-6820HQ, 32 GB RAM, NVIDIA Quadro M1000M 2 GB GDDR5 (Maxwell), Windows 11 Pro x64.

## Runtime architecture
C#/.NET 8 launcher → Electron 40.10.2 → React 19 → localhost Python 3.11.9 backend. Terminal uses node-pty/ConPTY on Windows.

## AI architecture
The bootstrap ALI model is retained as a small, trainable diagnostic/base artifact. For stronger local chat, the release provides a setup path for Qwen2.5-0.5B-Instruct Q4_K_M through llama.cpp. RAG and Memory remain separate from learned weights.

## Continuous learning
Dropped Markdown/JSON/JSONL/text/document sources are validated, de-duplicated, indexed into RAG, and eligible chat pairs are used for incremental LoRA training. Each generation is versioned (v1, v2, v3, ...). Candidate models are evaluated before promotion; the previous active generation remains available for rollback.

## GPU/VRAM policy
Auto mode uses a real CUDA kernel self-test plus current free VRAM. A 2 GB GPU is never assumed to be completely free. llama.cpp inference uses adaptive layer offload; training uses conservative batch/sequence/gradient-accumulation settings and falls back to CPU in Auto mode if CUDA or memory allocation is not safe.

## Known environment limitation
The current build container is Linux, so Windows-native Electron production build, .NET publish, ConPTY, and real Maxwell CUDA execution cannot be marked as executed here. Windows scripts are included to perform those final native gates.
```

---

### `150/588` `backend/knowledge_seed/ALI_DETERMINISTIC_FAQ_AR.md`

- **المسار الكامل:** `F:\1f\p\ALI_Studio_Pro_Design4_4.6.0\04_Adaptive_Hybrid\backend/knowledge_seed/ALI_DETERMINISTIC_FAQ_AR.md`
- **الحجم:** 6009 بايت (5.9 KB)
- **الامتداد:** `.md`

```markdown
# ALI — أسئلة وأجوبة موثوقة محلياً

هذا الملف مخصص لإجابات الحقائق المحلية الثابتة التي يجب ألا تعتمد على توليد نموذج صغير غير موثوق.

## الجهاز

**User:** ما هو معالج جهازي؟
**Assistant:** المعالج هو Intel Core i7-6820HQ من الجيل السادس (Skylake)، بأربع أنوية فعلية وثمانية خيوط، والتردد الأساسي 2.70 GHz.

**User:** كم عدد أنوية المعالج؟
**Assistant:** لديك 4 أنوية فعلية و8 خيوط معالجة.

**User:** ما هي بطاقة الرسومات لدي؟
**Assistant:** بطاقة الرسومات المنفصلة هي NVIDIA Quadro M1000M بمعمارية Maxwell GM107 وذاكرة 2 GB GDDR5.

**User:** كم VRAM لدي؟
**Assistant:** ذاكرة VRAM المخصصة في Quadro M1000M هي 2 GB GDDR5. في وضع Auto يجب على ALI الاعتماد على الذاكرة الحرة الفعلية وليس على السعة الكاملة.

**User:** كم RAM لدي؟
**Assistant:** لديك 32 GB DDR4 بسرعة 2133 MHz، على وحدتين 16+16 GB.

**User:** ما نظام التشغيل لدي؟
**Assistant:** Windows 11 Pro، إصدار 10.0.26200، بنظام 64-bit.

**User:** ما هو طراز الجهاز؟
**Assistant:** Lenovo ThinkPad P50، الموديل 20EQS2L900.

## ALI

**User:** ما هو RAG؟
**Assistant:** RAG هو الاسترجاع المعزز بالتوليد: يبحث ALI في المعرفة المحلية أو المصادر المتاحة، ثم يضع المقاطع ذات الصلة في سياق الإجابة دون تغيير أوزان النموذج.


**User:** ما الفرق بين Memory وRAG وTraining؟
**Assistant:** Memory تحفظ معلومات وسياقاً قابلاً للتحديث، وRAG يسترجع معلومات من المصادر المحلية أثناء الإجابة، بينما Training يغير سلوك النموذج أو الـadapter. الوصول إلى مستند عبر RAG لا يثبت أن الأوزان تعلمته.

**User:** كيف يعمل التدريب التراكمي؟
**Assistant:** يبدأ الإصدار الجديد من الإصدار النشط السابق، يستخدم البيانات الجديدة بعد التحقق ومنع التكرار، ينشئ Candidate، ثم Evaluation وRegression وPromotion قبل أن يصبح Active.

**User:** هل 100% في شريط التدريب يعني أن النموذج أصبح جيداً؟
**Assistant:** لا. 100% تعني اكتمال العملية الزمنية. جودة النموذج تحتاج Validation وTest واختبارات سلوكية وأسئلة غير مرئية والتحقق من الإصدار المحمل فعلياً.

**User:** كيف أعرف أن Runtime يستخدم النموذج الجديد؟
**Assistant:** يجب التحقق من version المحمل فعلياً في Runtime، ومسار artifact والـadapter وسجل التحميل، وليس اسم النموذج الظاهر في الواجهة فقط.

**User:** ماذا تفعل إذا فشل التدريب؟
**Assistant:** لا أعتمد الإصدار الجديد، ولا أستهلك مؤشر البيانات الناجحة، وأحتفظ بالإصدار السابق لإعادة المحاولة أو Rollback.


**User:** ما المعالج الرسومي؟
**Assistant:** بطاقة الرسومات المنفصلة هي NVIDIA Quadro M1000M بمعمارية Maxwell GM107 وذاكرة 2 GB GDDR5. هذه البطاقة مخصصة لمحطات العمل وتدعم OpenGL 4.5 وCUDA 5.0.

**User:** ما المعالج المركزي؟
**Assistant:** المعالج المركزي (CPU) هو Intel Core i7-6820HQ من الجيل السادس (Skylake)، بأربع أنوية فعلية وثمانية خيوط معالجة، وتردد أساسي 2.70 GHz.

**User:** كم ذاكرة الوصول العشوائي (RAM)؟
**Assistant:** لديك 32 GB DDR4 بسرعة 2133 MHz، على وحدتين SODIMM سعة كل واحدة 16 GB (إجمالي 32 GB) من نوع SK Hynix.

**User:** كم الرام؟
**Assistant:** الذاكرة العشوائية (RAM) هي 32 GB DDR4 بسرعة 2133 MHz، موزعة على وحدتين 16+16 GB.

**User:** كم مساحة التخزين؟
**Assistant:** القرص الرئيسي SSD NVMe سعة 512 GB من طراز WDC PC SN720 (C: 152 GB و D: 322 GB). يوجد أيضاً قرص HDD ثاني سعة 2 TB.

**User:** ما حجم البطارية؟
**Assistant:** البطارية 90 Wh بست خلايا (Cells: 6) من طراز Lenovo 00NY493. في وقت التقرير كان الشحن عند 38% ومتبقي 42 دقيقة.

**User:** ما طراز الجهاز؟
**Assistant:** Lenovo ThinkPad P50، رقم الموديل 20EQS2L900، مع BIOS إصدار N1EETA2W (1.75).

**User:** ما المعالج المستخدم في التدريب؟
**Assistant:** المشروع يستخدم PyTorch CPU (torch==2.14.0+cpu) للتدريب على هذا الجهاز بسبب VRAM المحدود (2GB) وغياب CUDA الحديث. الـinference يستخدم نفس النموذج.


**User:** كم VRAM لدي؟
**Assistant:** ذاكرة VRAM المخصصة لبطاقة الرسومات Quadro M1000M هي 2 GB GDDR5. هذه مخصصة للنموذج الرسومي فقط، وتختلف عن ذاكرة النظام RAM.

**User:** ما الفرق بين RAM و VRAM؟
**Assistant:** RAM (ذاكرة النظام) هي 32 GB DDR4 وتستخدمها المعالجات والتطبيقات. VRAM (ذاكرة الفيديو) هي 2 GB GDDR5 وتستخدمها بطاقة الرسومات Quadro M1000M للمعالجة الرسومية. VRAM لا تتوسع من RAM.

**User:** كم مساحة القرص؟
**Assistant:** القرص الرئيسي SSD NVMe سعة 512 GB (C: 152 GB، D: 322 GB). يوجد قرص HDD إضافي 2 TB.
```

---

### `151/588` `backend/knowledge_seed/ALI_RUNTIME_FAQ_AR_V1.md`

- **المسار الكامل:** `F:\1f\p\ALI_Studio_Pro_Design4_4.6.0\04_Adaptive_Hybrid\backend/knowledge_seed/ALI_RUNTIME_FAQ_AR_V1.md`
- **الحجم:** 10677 بايت (10.4 KB)
- **الامتداد:** `.md`

```markdown
# ALI Runtime FAQ V1 — Grounded Local Answers

هذه الأسئلة والأجوبة مرجع محلي موثوق. يستخدمها ALI قبل التوليد العام عندما يكون السؤال مطابقاً أو قريباً بما يكفي، وذلك لتجنب اعتماد الحقائق المحلية أو حالة المشروع على نموذج صغير غير موثوق.

## الهوية
**User:** ما اسمك؟
**Assistant:** اسمي ALI Studio Pro، وأنا المساعد المحلي داخل مشروع ALI AI.

**User:** من أنت؟
**Assistant:** أنا ALI، مساعد محلي يعمل فوق Runtime Python مع واجهة Electron/React، ويدعم الذاكرة وRAG والأدوات والتدريب التراكمي.

**User:** ما اسم المشروع؟
**Assistant:** اسم المشروع هو ALI Studio Pro.

**User:** ما هو اسم المشروع؟
**Assistant:** اسم المشروع هو ALI Studio Pro.

**User:** ما اسم البرنامج؟
**Assistant:** اسم البرنامج هو ALI Studio Pro.

## الجهاز
**User:** ما هو طراز جهازي؟
**Assistant:** جهازك Lenovo ThinkPad P50، الموديل 20EQS2L900.

**User:** ما هو معالج جهازي؟
**Assistant:** المعالج Intel Core i7-6820HQ من الجيل السادس (Skylake)، بأربع أنوية فعلية وثمانية خيوط، والتردد الأساسي 2.70 GHz.

**User:** كم نواة في المعالج؟
**Assistant:** لديك 4 أنوية فعلية و8 خيوط معالجة.

**User:** كم RAM لدي؟
**Assistant:** لديك 32 GB DDR4 بسرعة 2133 MHz، مكوّنة من وحدتين 16+16 GB.

**User:** ما سعة RAM لدي؟
**Assistant:** سعة الذاكرة RAM لديك هي 32 GB DDR4 بسرعة 2133 MHz، مكوّنة من وحدتين 16+16 GB.

**User:** ما سعة الذاكرة؟
**Assistant:** سعة الذاكرة RAM لديك هي 32 GB.

**User:** ما هي بطاقة الرسومات؟
**Assistant:** البطاقة المنفصلة NVIDIA Quadro M1000M بمعمارية Maxwell GM107 وذاكرة 2 GB GDDR5.

**User:** كم VRAM لدي؟
**Assistant:** لديك 2 GB GDDR5 مخصصة في NVIDIA Quadro M1000M. أثناء التشغيل يجب استخدام الذاكرة الحرة الفعلية وليس افتراض أن 2 GB كلها متاحة.

**User:** ما نظام التشغيل؟
**Assistant:** Windows 11 Pro بإصدار 10.0.26200 وبنظام 64-bit وفق ملف الجهاز المرجعي.

**User:** ما دقة الشاشة؟
**Assistant:** 1920×1080 بمعدل 60 Hz مع لوحة IPS FlexView.

## المعمارية
**User:** ما هي بنية ALI Studio Pro؟
**Assistant:** C#/.NET 8 للمشغّل، Electron 40.10.2 مع Chromium وNode، React 19 للواجهة، Python 3.11.9 للـBackend/Agent، وxterm.js مع node-pty/ConPTY للطرفية على Windows.

**User:** ماذا يفعل Launcher؟
**Assistant:** يجهز البيئة ويتحقق من Runtime ويشغل المكونات ويراقبها؛ منطق الذكاء والتنفيذ يبقى في Python Runtime.

**User:** هل الواجهة هي التي تنفذ الأوامر الحساسة مباشرة؟
**Assistant:** لا. الطلب يمر عبر طبقة Backend/Agent والأدوات والصلاحيات والتدقيق.

## RAG / Memory / Training
**User:** ما الفرق بين Memory وRAG وTraining؟
**Assistant:** Memory تحفظ معلومات وسياقاً قابلاً للتحديث، وRAG يسترجع معلومات من المصادر أثناء الإجابة دون تغيير الأوزان، أما Training فيغير سلوك النموذج أو الـadapter.

**User:** هل إضافة ملف إلى RAG تعني أن النموذج تعلمه داخل الأوزان؟
**Assistant:** لا. يمكن أن يجيب ALI من الملف المسترجع دون أن تكون معلومات الملف قد أصبحت جزءاً من الأوزان.

**User:** متى تصبح معلومات الملف جزءاً من التدريب؟
**Assistant:** عندما تحتوي بيانات صالحة للتدريب أو يتم اعتماد أمثلة User/Assistant منها، ثم تدخل Dataset وتنجح دورة التدريب والتقييم والترقية.

**User:** كيف يعمل التدريب التراكمي؟
**Assistant:** يبدأ الإصدار الجديد من Active السابق، يضيف البيانات الجديدة فقط بعد التحقق ومنع التكرار، ثم ينشئ Candidate ويجري Evaluation وRegression قبل Promotion.

**User:** ماذا يحدث عند فشل التدريب؟
**Assistant:** يبقى الإصدار السابق Active، ولا تُستهلك بيانات الدورة كأنها نجحت، ويمكن إعادة المحاولة بعد إصلاح السبب.

**User:** هل 100% في شريط التدريب تعني أن النموذج أصبح جيداً؟
**Assistant:** لا. 100% تعني اكتمال العملية الزمنية فقط؛ جودة السلوك تحتاج Validation وTest وأسئلة جديدة والتحقق من الإصدار المستخدم فعلياً.

## المحادثات
**User:** كيف أنشئ محادثة جديدة؟
**Assistant:** اضغط «محادثة جديدة» في شريط الجلسات. ينشئ ALI جلسة مستقلة ويحفظها في قاعدة المحادثات.

**User:** كيف أفتح محادثة سابقة؟
**Assistant:** افتح «المحادثات السابقة»، اختر الجلسة المطلوبة، وسيتم تحميل رسائلها من التخزين المحلي.

**User:** هل يمكن إعادة تسمية المحادثة؟
**Assistant:** نعم، من قائمة المحادثات السابقة اختر إعادة التسمية.

## التنفيذ والمشاريع
**User:** هل يستطيع ALI إنشاء مشروع؟
**Assistant:** نعم من ناحية المعمارية: يحلل الطلب، يحدد الخطة، يستخدم أدوات الملفات/المشروع المصرح بها، ثم يتحقق من الناتج.

**User:** ماذا تفعل قبل تعديل مشروع قائم؟
**Assistant:** أفحص البنية والملفات المرتبطة والقيود، أحدد التغيير المطلوب، ثم أنفذ وأختبر وأراجع الانحدار قبل إعلان النجاح.

**User:** ماذا تفعل إذا فشل الاختبار؟
**Assistant:** أقرأ نتيجة الفشل، أحدد السبب، أصلح أقل تغيير مناسب، ثم أعيد الاختبار والتحقق.

**User:** هل تستطيع القول إن العملية نجحت دون تشغيلها؟
**Assistant:** لا. أميز بين المخطط والمحاولة والتنفيذ والتحقق، ولا أدعي نتيجة لم أتحقق منها.

## GPU / VRAM
**User:** كيف تستخدم ALI الـGPU؟
**Assistant:** في Auto يختبر ALI CUDA فعلياً عندما تكون بيئة CUDA قابلة للاستخدام، ويقيس VRAM الحرة، ثم يختار حمولة مناسبة. إذا لم يكن GPU آمناً أو كانت الذاكرة غير كافية يعود إلى CPU.

**User:** هل يجب على ALI استخدام كامل VRAM؟
**Assistant:** لا. يجب ترك headroom للنظام والتطبيقات الأخرى، ويُخفض الحمل أو offload عند انخفاض VRAM الحرة.

**User:** ماذا يحدث إذا كان GPU مشغولاً؟
**Assistant:** يستخدم فقط الجزء الذي تسمح به سياسة الذاكرة الحرة. إذا لم يكن هناك هامش آمن، يستخدم CPU في Auto بدلاً من تجميد الجهاز.

**User:** هل GPU = 0% يعني دائماً أن GPU لا يعمل؟
**Assistant:** ليس بالضرورة؛ يجب فحص CUDA self-test والذاكرة وعملية التنفيذ الفعلية، وليس نسبة الاستخدام اللحظية وحدها.

## النماذج
**User:** ما الفرق بين Base Model وLoRA؟
**Assistant:** Base Model هو النموذج الأساسي، بينما LoRA تعديلات منخفضة الرتبة تتعلم سلوكاً أو تخصيصاً بتكلفة أقل من إعادة تدريب النموذج كله.

**User:** متى يصبح Candidate Active؟
**Assistant:** بعد سلامة الـartifact واجتياز Evaluation وRegression وبوابة Promotion، ثم إعادة تحميله فعلياً في Runtime.

**User:** هل نجاح checkpoint يعني أن Runtime يستخدمه؟
**Assistant:** لا. يجب تحميل الإصدار في Runtime أو ترقيته إليه والتحقق من version والمسار وسجل التحميل.

**User:** هل GGUF هو Dataset؟
**Assistant:** لا. GGUF هو artifact للاستدلال المحلي، وليس مصدراً تدريبياً بحد ذاته.

## الاستيراد والتدريب
**User:** ماذا يحدث عندما أسحب ملف MD إلى مركز التدريب؟
**Assistant:** يتحقق ALI من الملف، يحسب الهاش، يمنع التكرار، يستخرج المحادثات الصريحة، يفهرس المعرفة في RAG، ثم يضع العينات الجديدة في دورة التدريب إذا كانت صالحة.

**User:** ماذا لو كان ملف MD وثيقة فقط ولا يحتوي User/Assistant؟
**Assistant:** يستخدم كمعرفة RAG ولا يحوله النظام إلى محادثات تدريبية وهمية.

**User:** كيف أعرف أن التدريب بدأ؟
**Assistant:** يجب أن تتغير حالة الدورة إلى RUNNING وتظهر الخطوة والإجمالي والنسبة والعينات والوقت المنقضي وETA وLoss وTokens/s.

**User:** كيف أعرف أن التدريب انتهى فعلاً؟
**Assistant:** يجب أن تظهر حالة COMPLETED مع نتيجة Evaluation وPromotion، ثم يجب أن يثبت Runtime أنه حمّل الإصدار الجديد.

## الأمان
**User:** هل ينفذ ALI أوامر حساسة دون ضوابط؟
**Assistant:** لا. التنفيذ يمر عبر Permission Manager وسياسات الأدوات، وبعض العمليات تتطلب تأكيداً قبل السماح بها.

**User:** هل يحذف ALI الملفات تلقائياً أثناء إصلاح المشروع؟
**Assistant:** لا ينبغي أن يحذف عمليات واسعة أو خطرة دون سياسة وصلاحية مناسبة ونقطة رجوع عند الحاجة.
```

---

### `152/588` `backend/knowledge_seed/ALI_V4_4_COMPLETE_REPORT.md`

- **المسار الكامل:** `F:\1f\p\ALI_Studio_Pro_Design4_4.6.0\04_Adaptive_Hybrid\backend/knowledge_seed/ALI_V4_4_COMPLETE_REPORT.md`
- **الحجم:** 1119 بايت (1.1 KB)
- **الامتداد:** `.md`

```markdown
# 📚 ALI Studio Pro v4.4.0 — التقرير الكامل والشامل

> **المشروع**: `D:\AI ALI\new\4\ALI_Studio_Pro_Windows_v4.4.0_Complete\ALI_Studio_Pro_Windows_v4.3_project`
> **الإصدار**: 4.4.0
> **التاريخ**: 2026-10-04
> **الحالة النهائية**: ✅ يعمل بشكل كامل (Backend + Vite + Electron + Model v4 active)

---

# 📑 جدول المحتويات

1. [خريطة المشروع الكاملة](#1)
2. [إحصائيات الكود](#2)
3. [شرح جميع عمليات المشروع](#3)
4. [جميع الـ API Endpoints](#4)
5. [التدريب - Training Pipeline](#5)
6. [نظام RAG والذاكرة](#6)
7. [Response Guard](#7)
8. [Hardware Detection](#8)
9. [مشاكل المشروع الحالية](#9)
10. [ما قمت به من البداية](#10)
11. [جميع الملفات التي أنشأتها / عدلتها](#11)
12. [الأخطاء المتبقية](#12)
13. [ما يحتاجه المشروع](#13)
14. [الخلاصة النهائية](#14)

---

# 1. 🗺️ خريطة المشروع الكاملة

## 1.1 البنية العامة
```

---

### `153/588` `backend/knowledge_seed/ALI_V4_5_REBUILD_REFERENCE.md`

- **المسار الكامل:** `F:\1f\p\ALI_Studio_Pro_Design4_4.6.0\04_Adaptive_Hybrid\backend/knowledge_seed/ALI_V4_5_REBUILD_REFERENCE.md`
- **الحجم:** 992 بايت (1.0 KB)
- **الامتداد:** `.md`

```markdown
# ALI Studio Pro 4.5.0 Rebuild Reference

The previous report documented a functioning architecture but also listed 10 remaining issues: tiny 30 MB bootstrap model with 0/8 model-only answers, only 1566 new samples, heavy RAG reliance, garbled Arabic generation, unreliable nvidia-smi, unstable Electron backend URL detection, JSONL conversation/messages mismatch, incomplete production dist, Windows/GPU skipped tests, and a missing memory alias endpoint.

## Rebuild goals
1. Make the reported limitations explicit in the UI and Doctor.
2. Keep training Base Model separate from inference GGUF.
3. Make Markdown ingestion tolerant of common exporter wrappers.
4. Preserve chat sessions with explicit create/list/open/rename/delete operations.
5. Make GPU use adaptive and evidence-based for 2 GB VRAM.
6. Fall back to CPU safely in Auto mode on CUDA errors.
7. Never promote an unverified artifact.
8. Provide RAG-grounded fallback text when the tiny bootstrap model emits unusable output.
```

---

### `154/588` `backend/knowledge_seed/manifest.json`

- **المسار الكامل:** `F:\1f\p\ALI_Studio_Pro_Design4_4.6.0\04_Adaptive_Hybrid\backend/knowledge_seed/manifest.json`
- **الحجم:** 254 بايت (0.2 KB)
- **الامتداد:** `.json`

```json
{
  "files": [
    "ALI_CURRENT_STATUS_4.5.2.md",
    "THINKPAD_P50_COMPLETE_USER_PROFILE.md",
    "THINKPAD_P50_USER_PROFILE.md",
    "ALI_V4_4_COMPLETE_REPORT.md",
    "ALI_V4_5_REBUILD_REFERENCE.md"
  ],
  "policy": "seed-on-startup-if-not-present"
}
```

---

### `155/588` `backend/knowledge_seed/THINKPAD_P50_ARABIC_REFERENCE.md`

- **المسار الكامل:** `F:\1f\p\ALI_Studio_Pro_Design4_4.6.0\04_Adaptive_Hybrid\backend/knowledge_seed/THINKPAD_P50_ARABIC_REFERENCE.md`
- **الحجم:** 2429 بايت (2.4 KB)
- **الامتداد:** `.md`

```markdown
# ملف مرجعي عربي — Lenovo ThinkPad P50

هذا الملف مبني على مواصفات قدمها المستخدم. يستخدمه ALI كمرجع محلي، ولا يُعامل ما فيه كبيانات متغيرة تلقائياً.

## الجهاز
- الشركة: LENOVO
- الطراز: ThinkPad P50 — 20EQS2L900
- نوع الجهاز: Mobile Workstation — x64
- BIOS: LENOVO N1EETA2W — الإصدار 1.75

## نظام التشغيل
- Windows 11 Pro
- الإصدار: 10.0.26200 — 64-bit
- اللغة/الإدخال: العربية — السعودية (ar-SA)

## المعالج
- Intel Core i7-6820HQ — Skylake
- 4 أنوية فعلية / 8 خيوط
- التردد الأساسي: 2.70 GHz
- VT-x: مفعّل
- L1: 128 KB لكل نواة
- L2: 1 MB
- L3: 8 MB
- درجة الحرارة المذكورة في التقرير: 41.05°C
- القراءة الخام: 3142 (Kelvin × 10)

## الذاكرة
- 32 GB DDR4 (2×16 GB)
- 2133 MHz — PC4-17000
- SK Hynix HMA82GS6AFR8N-UH
- SODIMM — Dual Channel

## التخزين
- SSD: WDC PC SN720 SDAPNTW-512G-1006 — 512 GB NVMe
- تقسيم SSD: GPT
- الأقسام المذكورة: C: 152 GB، D: 322 GB
- HDD: WDC WD20SPZX-22UA7T0 — 2 TB SATA 5400 RPM
- تقسيم HDD: MBR
- الأقسام المذكورة: F: 1.67 TB، G: 194 GB

## الرسوميات
- NVIDIA Quadro M1000M — Maxwell GM107
- VRAM: 2 GB GDDR5
- PCI: VEN_10DE & DEV_13B1
- Compute Capability المستخدمة في سياسة ALI: 5.0
- Intel HD Graphics 530 مدمجة
- ذاكرة مشتركة مذكورة: 1 GB

## الشاشة والصوت والإدخال
- 1920×1080 @ 60 Hz
- IPS FlexView — LEN40BA
- Realtek High Definition Audio
- لوحة مفاتيح عربية Enhanced 101/102
- Synaptics TrackPoint + Touchpad

## الشبكة والطاقة
- Intel Dual Band Wireless-AC 8260
- السرعة المذكورة أثناء القياس: 72.2 Mbps
- الحد الأقصى المذكور: 867 Mbps
- Intel I219-LM Ethernet
- Bluetooth متاح
- البطارية: Lenovo 00NY493 — 90 Wh
- الشحن المذكور في التقرير: 38%
- الزمن المتبقي المذكور: قرابة 42 دقيقة

## قاعدة مهمة
إذا تعارضت قراءة runtime الحالية مع هذه القيم، يقدّم ALI القراءة الحية التي تم التحقق منها ويعامل الملف كمعلومة مرجعية سابقة.
```

---

### `156/588` `backend/knowledge_seed/THINKPAD_P50_COMPLETE_USER_PROFILE.md`

- **المسار الكامل:** `F:\1f\p\ALI_Studio_Pro_Design4_4.6.0\04_Adaptive_Hybrid\backend/knowledge_seed/THINKPAD_P50_COMPLETE_USER_PROFILE.md`
- **الحجم:** 2632 بايت (2.6 KB)
- **الامتداد:** `.md`

```markdown
# ALI Target Hardware — Lenovo ThinkPad P50 (User-provided profile)

## System
- Manufacturer: LENOVO
- Model: ThinkPad P50 — 20EQS2L900
- Chassis serial: L1HF6CH036A
- Product ID: PC0J8H3F
- System UUID: DFBD464C-2222-11B2-A85C-ED47CEA099E4
- Device type: Mobile Workstation, x64
- Motherboard: LENOVO 20EQS2L900 — SDK0J40697 WIN
- BIOS: LENOVO N1EETA2W, version 1.75 (18 Mar 2024)

## Operating system
- Windows 11 Pro, build 10.0.26200, 64-bit
- UI/input locale: ar-SA
- User report installation date: 27 Jul 2026
- User report last boot: 30 Sep 2026, 19:39

## CPU
- Intel Core i7-6820HQ, Skylake
- 4 physical cores / 8 logical threads
- Base 2.70 GHz; reported current 1.51 GHz
- VT-x enabled
- L1 128 KB/core, L2 1 MB, L3 8 MB
- Processor ID: BFEBFBFF000506E3
- Socket: U3E1
- Reported CPU temperature: 41.05 C
- Raw temperature reading: 3142 in Kelvin x10; 314.2 K -> 41.05 C

## RAM
- 32 GB DDR4, 2 x 16 GB
- 2133 MHz PC4-17000
- SK Hynix HMA82GS6AFR8N-UH
- SODIMM, dual channel

## Storage
- SSD: WDC PC SN720 SDAPNTW-512G-1006, 512 GB NVMe, GPT
- User report partitions: C 152 GB, D 322 GB
- SSD health: reported Healthy
- HDD: WDC WD20SPZX-22UA7T0, 2 TB SATA 5400 RPM, MBR
- User report partitions: F 1.67 TB, G 194 GB
- HDD health: reported Healthy

## GPU
- NVIDIA Quadro M1000M, Maxwell GM107
- 2 GB GDDR5
- PCI: VEN_10DE & DEV_13B1
- User report driver: 31.0.15.3818
- Compute capability used by ALI policy: 5.0
- Intel HD Graphics 530 integrated GPU
- Intel iGPU shared memory: reported 1 GB

## Display / I/O / Network
- 1920x1080 @ 60 Hz, IPS FlexView
- Lenovo display model LEN40BA
- Realtek High Definition Audio
- Arabic Enhanced 101/102 keyboard
- Synaptics TrackPoint + Touchpad
- Intel Wireless-AC 8260; reported active speed 72.2 Mbps; max 867 Mbps
- Intel I219-LM Ethernet
- Bluetooth available

## Power
- Lenovo battery 00NY493, reported 90 Wh original
- User report at measurement: 38%, about 42 minutes remaining

## Engineering policy
- Auto compute mode must never assume the entire 2 GB VRAM is free.
- Probe actual CUDA operation and free VRAM before GPU training.
- When VRAM is shared, select a smaller workload rather than stealing all memory.
- On 2 GB-class GPUs use batch 1, bounded sequence length, gradient accumulation and memory headroom.
- If CUDA or memory allocation fails in Auto mode, fall back to CPU and report the reason.

## Measurement limits
The following are not to be invented from this report alone: Intel iGPU VRAM type, SSD TBW/SMART endurance, exact battery cell count, and exact CUDA-core count from WMI alone. Dedicated tools are required for those measurements.
```

---

### `157/588` `backend/knowledge_seed/THINKPAD_P50_FULL_USER_REPORT.md`

- **المسار الكامل:** `F:\1f\p\ALI_Studio_Pro_Design4_4.6.0\04_Adaptive_Hybrid\backend/knowledge_seed/THINKPAD_P50_FULL_USER_REPORT.md`
- **الحجم:** 2743 بايت (2.7 KB)
- **الامتداد:** `.md`

```markdown
# Lenovo ThinkPad P50 — User Hardware Report (authoritative local reference)

## System
- Manufacturer: LENOVO
- Model: ThinkPad P50 — 20EQS2L900
- Chassis serial: L1HF6CH036A
- Product Identifying Number: PC0J8H3F
- System UUID: DFBD464C-2222-11B2-A85C-ED47CEA099E4
- Device type: Mobile Workstation — x64 PC
- Motherboard: LENOVO 20EQS2L900 — SDK0J40697 WIN
- BIOS: LENOVO N1EETA2W — version 1.75 (18 March 2024)

## OS
- Microsoft Windows 11 Pro
- Build 10.0.26200 (64-bit)
- Language/input: Arabic — Saudi Arabia (ar-SA)
- Install date: 27 July 2026
- Last boot in report: 30 September 2026 — 7:39 PM

## CPU
- Intel Core i7-6820HQ, Skylake, 4 cores / 8 threads
- Base/max reported: 2.70 GHz / 2.71 GHz