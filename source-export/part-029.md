```markdown
# ALI imported-training regression bundle

`ALI_User_Understanding_Bundle_V4.md` is the user-supplied training bundle used for the 4.5.7 end-to-end regression test.

The file declares 50 conversations in its summary, but the actual document contains 216 conversation headings and one exact duplicate Q/A pair. The importer intentionally does not modify the source; it reports the metadata mismatch and accepts 215 unique samples for training.
```

---

### `71/588` `backend/data_engine/__init__.py`

- **المسار الكامل:** `F:\1f\p\ALI_Studio_Pro_Design4_4.6.0\04_Adaptive_Hybrid\backend/data_engine/__init__.py`
- **الحجم:** 1 بايت (0.0 KB)
- **الامتداد:** `.py`

```python

```

---

### `72/588` `backend/data_engine/dataset_builder.py`

- **المسار الكامل:** `F:\1f\p\ALI_Studio_Pro_Design4_4.6.0\04_Adaptive_Hybrid\backend/data_engine/dataset_builder.py`
- **الحجم:** 3176 بايت (3.1 KB)
- **الامتداد:** `.py`

```python
# -*- coding: utf-8 -*-
from __future__ import annotations
from pathlib import Path
import json, sqlite3, random
from typing import Dict, Any

def export_jsonl(db_path: str|Path, out_dir: str|Path, seed: int=42, train_ratio=.9, val_ratio=.05) -> Dict[str,Any]:
    con=sqlite3.connect(db_path); con.row_factory=sqlite3.Row
    rows=con.execute("SELECT sample_hash,normalized,quality FROM samples WHERE quality='ACCEPTED' ORDER BY id").fetchall(); con.close()
    data=[{'id':r['sample_hash'],'text':r['normalized']} for r in rows]
    rnd=random.Random(seed); rnd.shuffle(data)
    n=len(data); nt=int(n*train_ratio); nv=int(n*val_ratio)
    splits={'train':data[:nt],'validation':data[nt:nt+nv],'test':data[nt+nv:]}
    out=Path(out_dir); out.mkdir(parents=True,exist_ok=True)
    for name,items in splits.items():
        with (out/f'{name}.jsonl').open('w',encoding='utf-8') as f:
            for x in items: f.write(json.dumps(x,ensure_ascii=False)+'\n')
    return {'total':n, **{k:len(v) for k,v in splits.items()}, 'output':str(out)}


def export_incremental(db_path: str|Path, out_path: str|Path, after_id: int = 0) -> Dict[str,Any]:
    """Export only newly accepted conversation identities since a previous sample id."""
    con=sqlite3.connect(db_path); con.row_factory=sqlite3.Row
    rows=con.execute("SELECT id,sample_hash,normalized,quality FROM samples WHERE quality='ACCEPTED' AND id>? ORDER BY id",(int(after_id),)).fetchall(); con.close()
    out=Path(out_path); out.parent.mkdir(parents=True,exist_ok=True)
    seen=set(); written=0
    with out.open('w',encoding='utf-8') as f:
        for r in rows:
            h=r['sample_hash']
            if h in seen: continue
            seen.add(h); f.write(json.dumps({'id':h,'text':r['normalized']},ensure_ascii=False)+'\n'); written+=1
    return {'after_id':int(after_id),'samples':written,'output':str(out),'sample_hashes':sorted(seen)}


def export_conversation_incremental(db_path: str|Path, out_path: str|Path, after_ts: float = 0.0, min_quality: float = .6) -> Dict[str,Any]:
    """Export only new/high-quality conversation-memory pairs after a timestamp."""
    con=sqlite3.connect(db_path); con.row_factory=sqlite3.Row
    rows=con.execute("SELECT id,user_text,assistant_text,pair_hash,source,model_version,quality,updated_at FROM conversations WHERE quality>=? AND updated_at>? ORDER BY id",(float(min_quality),float(after_ts))).fetchall(); con.close()
    out=Path(out_path); out.parent.mkdir(parents=True,exist_ok=True)
    seen=set(); written=0; latest=float(after_ts)
    with out.open('w',encoding='utf-8') as f:
        for r in rows:
            h=str(r['pair_hash']); latest=max(latest,float(r['updated_at']))
            if h in seen: continue
            seen.add(h)
            text=(f"<|user|>\n{r['user_text'].strip()}\n<|eot|>\n<|assistant|>\n{r['assistant_text'].strip()}\n<|eot|>\n")
            f.write(json.dumps({'id':h,'text':text,'source':r['source'],'model_version':r['model_version'],'quality':float(r['quality'])},ensure_ascii=False)+'\n'); written+=1
    return {'after_ts':float(after_ts),'samples':written,'output':str(out),'latest_ts':latest,'sample_hashes':sorted(seen)}
```

---

### `73/588` `backend/data_engine/dedup.py`

- **المسار الكامل:** `F:\1f\p\ALI_Studio_Pro_Design4_4.6.0\04_Adaptive_Hybrid\backend/data_engine/dedup.py`
- **الحجم:** 1047 بايت (1.0 KB)
- **الامتداد:** `.py`

```python
# -*- coding: utf-8 -*-
"""Exact and near-duplicate detection using deterministic fingerprints and MinHash-like shingles."""
from __future__ import annotations
import hashlib, re
from collections import Counter
from typing import Iterable, Dict, Any

TOKEN_RE = re.compile(r'\w+', re.UNICODE)

def shingles(text: str, n: int = 5) -> set[str]:
    toks = TOKEN_RE.findall(text.lower())
    if len(toks) <= n: return {" ".join(toks)} if toks else set()
    return {" ".join(toks[i:i+n]) for i in range(len(toks)-n+1)}

def jaccard(a: set[str], b: set[str]) -> float:
    if not a and not b: return 1.0
    if not a or not b: return 0.0
    return len(a & b) / max(1, len(a | b))

def near_duplicate(candidate: str, existing: Iterable[str], threshold: float = 0.92) -> Dict[str, Any]:
    cs = shingles(candidate)
    best = (0.0, None)
    for idx, text in enumerate(existing):
        s = jaccard(cs, shingles(text))
        if s > best[0]: best = (s, idx)
    return {"is_near_duplicate": best[0] >= threshold, "score": best[0], "index": best[1]}
```

---

### `74/588` `backend/data_engine/harvester.py`

- **المسار الكامل:** `F:\1f\p\ALI_Studio_Pro_Design4_4.6.0\04_Adaptive_Hybrid\backend/data_engine/harvester.py`
- **الحجم:** 7802 بايت (7.6 KB)
- **الامتداد:** `.py`

```python
# -*- coding: utf-8 -*-
"""Recursive workspace/file harvesting with source provenance and deterministic dedup."""
from __future__ import annotations
from pathlib import Path
from typing import Iterable, List, Dict, Any
import json, re, sqlite3
from .parsers import parse_file
from .normalization import normalize_text, redact_secrets, normalized_hash
from .dedup import near_duplicate

TEXT_EXT={'.md','.txt','.json','.jsonl','.csv','.xml','.html','.htm','.pdf','.docx','.py','.js','.ts','.tsx','.jsx','.css','.log','.yaml','.yml','.toml'}
ARCHIVE_EXT={'.zip','.tar','.gz','.bz2','.xz','.tgz','.tbz2','.rar','.7z'}
MODEL_EXT={'.gguf','.safetensors','.bin','.pt','.pth','.onnx'}
SKIP_DIRS={'.git','.venv','venv','node_modules','__pycache__','dist','build','tmp','temp'}

def classify(path: Path) -> str:
    n=path.name.lower()
    if n=='adapter_config.json' or n=='adapter_model.safetensors': return 'adapter'
    if path.suffix.lower() in MODEL_EXT: return 'model'
    if path.suffix.lower() in ARCHIVE_EXT: return 'archive'
    if path.suffix.lower() in TEXT_EXT: return 'document'
    return 'other'

def extract_conversations(text: str) -> List[Dict[str,str]]:
    t=normalize_text(text)
    if not t: return []
    # JSON messages array
    try:
        obj=json.loads(t)
        candidates=[]
        if isinstance(obj,dict) and isinstance(obj.get('messages'),list): candidates=obj['messages']
        if isinstance(obj,list):
            for item in obj:
                if isinstance(item,dict) and isinstance(item.get('messages'),list): candidates.extend(item['messages'])
        if candidates:
            rows=[]
            for m in candidates:
                if isinstance(m,dict) and m.get('role') in {'user','assistant','system'} and isinstance(m.get('content'),str):
                    rows.append({'role':m['role'],'content':m['content']})
            return rows
    except Exception: pass
    # Labeled turns in Arabic/English.
    pat=re.compile(r'(?im)^\s*(User|Assistant|System|المستخدم|المساعد|النظام)\s*:\s*(.*?)(?=^\s*(?:User|Assistant|System|المستخدم|المساعد|النظام)\s*:|\Z)',re.S)
    rows=[]
    for m in pat.finditer(t):
        role=m.group(1).lower(); content=m.group(2).strip()
        role={'المستخدم':'user','المساعد':'assistant','النظام':'system'}.get(role,role)
        if content: rows.append({'role':role,'content':content})
    return rows

def to_training_sample(turns: List[Dict[str,str]]) -> str:
    return ''.join(f"<|{m['role']}|>\n{m['content']}\n<|eot|>\n" for m in turns if m.get('content'))

class Harvester:
    def __init__(self, db_path: str|Path):
        self.db=Path(db_path); self.db.parent.mkdir(parents=True,exist_ok=True)
        con=sqlite3.connect(self.db); con.executescript('''
        CREATE TABLE IF NOT EXISTS sources(id INTEGER PRIMARY KEY, path TEXT UNIQUE, kind TEXT, sha256 TEXT, size INTEGER, metadata TEXT, warning TEXT, added_at TEXT DEFAULT CURRENT_TIMESTAMP);
        CREATE TABLE IF NOT EXISTS samples(id INTEGER PRIMARY KEY, source_id INTEGER, sample_hash TEXT UNIQUE, normalized TEXT, role TEXT, quality TEXT, reason TEXT, created_at TEXT DEFAULT CURRENT_TIMESTAMP, FOREIGN KEY(source_id) REFERENCES sources(id));
        CREATE TABLE IF NOT EXISTS chunks(id INTEGER PRIMARY KEY, source_id INTEGER, chunk_hash TEXT UNIQUE, text TEXT, metadata TEXT, created_at TEXT DEFAULT CURRENT_TIMESTAMP, FOREIGN KEY(source_id) REFERENCES sources(id));
        CREATE INDEX IF NOT EXISTS idx_samples_role ON samples(role); CREATE INDEX IF NOT EXISTS idx_chunks_source ON chunks(source_id);
        '''); con.commit(); con.close()
    def scan(self, root: str|Path, max_file_mb: int=100, min_sample_chars:int=32, max_sample_chars:int=200000) -> Dict[str,Any]:
        root=Path(root).resolve(); stats={'files':0,'documents':0,'models':0,'archives':0,'other':0,'samples':0,'duplicates':0,'sensitive':0,'too_short':0,'errors':0}
        def keep(path):
            try: parts=path.resolve().relative_to(root).parts
            except ValueError: return False
            return not any(part in SKIP_DIRS for part in parts)
        queue=[p for p in root.rglob('*') if p.is_file() and keep(p)]
        seen=set(); con=sqlite3.connect(self.db); con.row_factory=sqlite3.Row
        while queue:
            p=queue.pop(0).resolve()
            if p in seen or not keep(p): continue
            seen.add(p)
            try:
                if p.stat().st_size > max_file_mb*1024*1024: continue
                kind=classify(p); stats['files']+=1; stats[kind+'s' if kind in {'document','model','archive'} else 'other']+=1
                pd=parse_file(p, self.db.parent/'extracted')
                raw=pd.text or ''; redacted,sensitive=redact_secrets(raw)
                h=normalized_hash(redacted) if redacted else normalized_hash(str(p))
                con.execute('INSERT OR IGNORE INTO sources(path,kind,sha256,size,metadata,warning) VALUES(?,?,?,?,?,?)',(str(p),kind,h,p.stat().st_size,json.dumps(pd.metadata,ensure_ascii=False),pd.warning))
                sid=con.execute('SELECT id FROM sources WHERE path=?',(str(p),)).fetchone()[0]
                if sensitive: stats['sensitive']+=1
                # Archive: add its extracted files to the same crawl queue.
                for ep in pd.extracted_files:
                    queue.append(Path(ep))
                if kind=='document' and redacted:
                    # Conversations become SFT data; ordinary documents become knowledge chunks.
                    turns=extract_conversations(redacted)
                    if turns:
                        sample=to_training_sample(turns); sh=normalized_hash(sample)
                        if len(sample)<min_sample_chars: q='TOO_SHORT'; stats['too_short']+=1
                        elif len(sample)>max_sample_chars: q='TOO_LONG'
                        elif sensitive: q='SENSITIVE'
                        elif any(m['role']=='assistant' and m['content'].strip() for m in turns): q='ACCEPTED'
                        else: q='REVIEW'
                        # Compare against prior accepted samples before inserting this candidate.
                        near_q=q
                        if q=='ACCEPTED':
                            existing=[r[0] for r in con.execute("SELECT normalized FROM samples WHERE quality='ACCEPTED' ORDER BY id DESC LIMIT 2000").fetchall()]
                            nd=near_duplicate(sample,existing,threshold=.94)
                            if nd['is_near_duplicate']:
                                near_q='NEAR_DUPLICATE'
                        before=con.total_changes; con.execute('INSERT OR IGNORE INTO samples(source_id,sample_hash,normalized,role,quality,reason) VALUES(?,?,?,?,?,?)',(sid,sh,sample,'conversation',near_q,'secret-redaction' if sensitive else ('near-duplicate' if near_q=='NEAR_DUPLICATE' else '')))
                        if con.total_changes==before:
                            stats['duplicates']+=1
                        elif near_q=='ACCEPTED':
                            stats['samples']+=1
                        elif near_q=='NEAR_DUPLICATE':
                            stats['duplicates']+=1
                    clean=redacted.strip()
                    for i in range(0,len(clean),1800):
                        chunk=clean[i:i+1800].strip()
                        if len(chunk)<80: continue
                        ch=normalized_hash(chunk)
                        con.execute('INSERT OR IGNORE INTO chunks(source_id,chunk_hash,text,metadata) VALUES(?,?,?,?)',(sid,ch,chunk,json.dumps({'offset':i,'source':str(p),'sensitive_redacted':sensitive},ensure_ascii=False)))
            except Exception:
                stats['errors']+=1
        con.commit(); con.close(); return stats
```

---

### `75/588` `backend/data_engine/kca_dataset.py`

- **المسار الكامل:** `F:\1f\p\ALI_Studio_Pro_Design4_4.6.0\04_Adaptive_Hybrid\backend/data_engine/kca_dataset.py`
- **الحجم:** 3605 بايت (3.5 KB)
- **الامتداد:** `.py`

```python
# -*- coding: utf-8 -*-
"""Build enriched KCA training records from approved conversation JSONL."""
from __future__ import annotations
from pathlib import Path
import hashlib, json
from typing import Any, Iterable

from data_engine.normalization import normalize_text, redact_secrets
from control_plane.router import KCARequestRouter
from control_plane.contracts import RequestEnvelope


def _digest(obj: Any) -> str:
    raw = json.dumps(obj, ensure_ascii=False, sort_keys=True, separators=(",", ":"), default=str).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def enrich_conversation(row: dict[str, Any], router: KCARequestRouter | None = None) -> dict[str, Any] | None:
    router = router or KCARequestRouter()
    messages = row.get("messages") or []
    user = next((m.get("content", "") for m in messages if m.get("role") == "user"), "")
    assistant = next((m.get("content", "") for m in reversed(messages) if m.get("role") == "assistant"), "")
    if not str(user).strip() or not str(assistant).strip():
        return None
    user, ru = redact_secrets(normalize_text(str(user)))
    assistant, ra = redact_secrets(normalize_text(str(assistant)))
    env = RequestEnvelope(raw_text=user)
    state = router.build_state(env)
    output = {
        "sample_id": str(row.get("id") or _digest([user, assistant])),
        "input": user,
        "context": row.get("context") or {},
        "entities": row.get("entities") or [],
        "state": {"intent": state.intent, "confidence": state.confidence},
        "goal": {"text": state.goal},
        "constraints": state.constraints,
        "implicit_intent": state.implicit_intent,
        "task_state": state.task_state,
        "candidate_actions": state.candidate_actions,
        "selected_action": state.selected_action,
        "observation": row.get("observation"),
        "error_state": row.get("error_state"),
        "correction": row.get("correction"),
        "verification": row.get("verification"),
        "uncertainty": row.get("uncertainty"),
        "final_output": assistant,
        "messages": [{"role": "user", "content": user}, {"role": "assistant", "content": assistant}],
        "source": row.get("source") or "conversation",
        "quality": float(row.get("quality", 0.0) or 0.0),
        "redacted": bool(ru or ra),
        "schema_version": "kca-3.0",
    }
    output["record_hash"] = _digest(output)
    return output


def build_kca_dataset(inputs: Iterable[str | Path], output: str | Path, min_quality: float = 0.6) -> dict[str, Any]:
    seen: set[str] = set()
    rows: list[dict[str, Any]] = []
    for raw_path in inputs:
        p = Path(raw_path)
        if not p.exists():
            continue
        for line in p.read_text(encoding="utf-8", errors="replace").splitlines():
            if not line.strip():
                continue
            try:
                row = json.loads(line)
            except Exception:
                continue
            if float(row.get("quality", 1.0) or 0.0) < min_quality:
                continue
            enriched = enrich_conversation(row)
            if not enriched or enriched["record_hash"] in seen:
                continue
            seen.add(enriched["record_hash"])
            rows.append(enriched)
    out = Path(output); out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", encoding="utf-8", newline="\n") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")
    return {"output": str(out), "samples": len(rows), "schema": "kca-3.0", "unique": len(seen)}

```

---

### `76/588` `backend/data_engine/ledger.py`

- **المسار الكامل:** `F:\1f\p\ALI_Studio_Pro_Design4_4.6.0\04_Adaptive_Hybrid\backend/data_engine/ledger.py`
- **الحجم:** 3742 بايت (3.7 KB)
- **الامتداد:** `.py`

```python
# -*- coding: utf-8 -*-
"""Persistent artifact ledger: one identity, one processing history.

Prevents re-ingesting or re-training the same normalized record and prevents a
GGUF snapshot from being rebuilt under the same model/data identity.
"""
from __future__ import annotations
from pathlib import Path
import hashlib, json, sqlite3, time
from typing import Any, Iterable

class ArtifactLedger:
    def __init__(self,path:str|Path):
        self.path=Path(path); self.path.parent.mkdir(parents=True,exist_ok=True)
        c=sqlite3.connect(self.path)
        c.executescript('''
        CREATE TABLE IF NOT EXISTS artifacts(
          identity TEXT PRIMARY KEY, kind TEXT NOT NULL, source TEXT, metadata TEXT,
          first_seen REAL NOT NULL, last_seen REAL NOT NULL, processed_count INTEGER DEFAULT 0);
        CREATE TABLE IF NOT EXISTS runs(
          id INTEGER PRIMARY KEY AUTOINCREMENT, identity TEXT NOT NULL, action TEXT NOT NULL,
          input_identity TEXT, output_identity TEXT, metadata TEXT, created_at REAL NOT NULL);
        CREATE INDEX IF NOT EXISTS idx_runs_identity ON runs(identity,action);
        '''); c.close()
    def seen(self,identity:str,kind:str|None=None)->bool:
        c=sqlite3.connect(self.path); row=c.execute('SELECT 1 FROM artifacts WHERE identity=?'+(' AND kind=?' if kind else ''),(identity,kind) if kind else (identity,)).fetchone(); c.close(); return bool(row)
    def record(self,identity:str,kind:str,source:str='',metadata:dict|None=None)->bool:
        now=time.time(); c=sqlite3.connect(self.path)
        cur=c.execute('INSERT OR IGNORE INTO artifacts(identity,kind,source,metadata,first_seen,last_seen) VALUES(?,?,?,?,?,?)',(identity,kind,source,json.dumps(metadata or {},ensure_ascii=False),now,now))
        if cur.rowcount==0:c.execute('UPDATE artifacts SET last_seen=?,processed_count=processed_count+1 WHERE identity=?',(now,identity))
        c.commit(); c.close(); return cur.rowcount==1
    def record_run(self,identity,action,input_identity='',output_identity='',metadata=None):
        c=sqlite3.connect(self.path); c.execute('INSERT INTO runs(identity,action,input_identity,output_identity,metadata,created_at) VALUES(?,?,?,?,?,?)',(identity,action,input_identity,output_identity,json.dumps(metadata or {},ensure_ascii=False),time.time())); c.commit(); c.close()
    def action_done(self,identity:str,action:str)->bool:
        c=sqlite3.connect(self.path); row=c.execute('SELECT 1 FROM runs WHERE identity=? AND action=? LIMIT 1',(identity,action)).fetchone(); c.close(); return bool(row)
    def status(self,identity:str)->dict[str,Any]:
        c=sqlite3.connect(self.path); c.row_factory=sqlite3.Row; a=c.execute('SELECT * FROM artifacts WHERE identity=?',(identity,)).fetchone(); runs=c.execute('SELECT action,output_identity,created_at FROM runs WHERE identity=? ORDER BY id',(identity,)).fetchall(); c.close(); return {'artifact':dict(a) if a else None,'runs':[dict(r) for r in runs]}

def canonical_json(obj:Any)->str:return json.dumps(obj,ensure_ascii=False,sort_keys=True,separators=(',',':'))
def identity_from_records(ids:Iterable[str],namespace:str='dataset')->str:
    h=hashlib.sha256(); h.update(namespace.encode('utf-8')); h.update(b'\0')
    for x in sorted(set(map(str,ids))):h.update(x.encode('utf-8'));h.update(b'\n')
    return h.hexdigest()
def file_identity(path:str|Path)->str:
    p=Path(path); h=hashlib.sha256()
    if p.is_file():
        with p.open('rb') as f:
            for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
        return h.hexdigest()
    for f in sorted(x for x in p.rglob('*') if x.is_file()):
        h.update(str(f.relative_to(p)).encode('utf-8')); h.update(file_identity(f).encode('ascii'))
    return h.hexdigest()
```

---

### `77/588` `backend/data_engine/normalization.py`

- **المسار الكامل:** `F:\1f\p\ALI_Studio_Pro_Design4_4.6.0\04_Adaptive_Hybrid\backend/data_engine/normalization.py`
- **الحجم:** 1213 بايت (1.2 KB)
- **الامتداد:** `.py`

```python
# -*- coding: utf-8 -*-
"""Text normalization, secret redaction and stable hashes."""
from __future__ import annotations
import hashlib, re, unicodedata
from typing import Tuple

SECRET_PATTERNS = [
    re.compile(r'(?i)\b(api[_-]?key|secret|token|password|passwd|access[_-]?token)\s*[:=]\s*["\']?[^\s"\']{8,}["\']?'),
    re.compile(r'-----BEGIN [A-Z ]+ PRIVATE KEY-----.*?-----END [A-Z ]+ PRIVATE KEY-----', re.S),
    re.compile(r'(?i)\bsk-[A-Za-z0-9_-]{20,}\b'),
    re.compile(r'(?i)\bgh[pousr]_[A-Za-z0-9_]{20,}\b'),
]

def normalize_text(text: str) -> str:
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = unicodedata.normalize("NFKC", text)
    text = re.sub(r'[ \t]+', ' ', text)
    text = re.sub(r'\n{3,}', '\n\n', text)
    return text.strip()

def redact_secrets(text: str) -> Tuple[str, bool]:
    changed = False
    out = text
    for p in SECRET_PATTERNS:
        out2, n = p.subn('[REDACTED_SECRET]', out)
        if n: changed = True; out = out2
    return out, changed

def normalized_hash(text: str) -> str:
    return hashlib.sha256(normalize_text(text).encode('utf-8')).hexdigest()

def fingerprint_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()
```

---

### `78/588` `backend/data_engine/ocr.py`

- **المسار الكامل:** `F:\1f\p\ALI_Studio_Pro_Design4_4.6.0\04_Adaptive_Hybrid\backend/data_engine/ocr.py`
- **الحجم:** 756 بايت (0.7 KB)
- **الامتداد:** `.py`

```python
# -*- coding: utf-8 -*-
"""Optional real OCR adapter. It never silently invents OCR text."""
from __future__ import annotations
from pathlib import Path
import shutil


def available() -> bool:
    try:
        import pytesseract  # noqa: F401
        return bool(shutil.which("tesseract"))
    except Exception:
        return False


def image_to_text(path: str | Path, lang: str = "ara+eng") -> str:
    try:
        import pytesseract
        from PIL import Image
    except Exception as e:
        raise RuntimeError("OCR requires Pillow + pytesseract") from e
    if not shutil.which("tesseract"):
        raise RuntimeError("Tesseract executable is not installed or not on PATH")
    return pytesseract.image_to_string(Image.open(path), lang=lang)
```

---

### `79/588` `backend/data_engine/parsers.py`

- **المسار الكامل:** `F:\1f\p\ALI_Studio_Pro_Design4_4.6.0\04_Adaptive_Hybrid\backend/data_engine/parsers.py`
- **الحجم:** 8854 بايت (8.6 KB)
- **الامتداد:** `.py`

```python
# -*- coding: utf-8 -*-
"""Real parsers for documents and archives. Optional heavy readers degrade gracefully."""
from __future__ import annotations
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Any, Dict, List, Optional
import csv, io, json, tarfile, zipfile, gzip, bz2, lzma, xml.etree.ElementTree as ET
import re

@dataclass
class ParsedDocument:
    path: str
    kind: str
    text: str
    metadata: Dict[str, Any]
    tables: List[List[List[str]]]
    extracted_files: List[str]
    warning: Optional[str] = None
    def to_dict(self): return asdict(self)

def _read_text(path: Path) -> str:
    data = path.read_bytes()
    for enc in ('utf-8','utf-8-sig','utf-16','cp1256','cp1252','latin-1'):
        try: return data.decode(enc)
        except Exception: pass
    return data.decode('utf-8','replace')

def _parse_json(path: Path) -> str:
    obj = json.loads(_read_text(path))
    return json.dumps(obj, ensure_ascii=False, indent=2)

def _parse_csv(path: Path) -> tuple[str, List[List[List[str]]]]:
    text = _read_text(path)
    rows = list(csv.reader(io.StringIO(text)))
    return '\n'.join(' | '.join(r) for r in rows), [rows]

def _parse_pdf(path: Path) -> tuple[str, List[List[List[str]]], Dict[str,Any], Optional[str]]:
    tables = []; meta={}; warnings=[]
    try:
        import fitz
        doc = fitz.open(str(path))
        parts=[]
        meta.update({"page_count": doc.page_count, "metadata": doc.metadata})
        for page in doc:
            parts.append(page.get_text("text"))
            try:
                tf = page.find_tables()
                for table in tf.tables:
                    tables.append(table.extract())
            except Exception:
                pass
        text='\n\n'.join(parts)
        # OCR only when the PDF appears scanned and a real Tesseract stack is available.
        if len(text.strip()) < max(40, doc.page_count * 20):
            try:
                import pytesseract
                from PIL import Image
                ocr_parts=[]
                for page in doc:
                    pix=page.get_pixmap(matrix=fitz.Matrix(1.5,1.5), alpha=False)
                    img=Image.frombytes('RGB',[pix.width,pix.height],pix.samples)
                    ocr_parts.append(pytesseract.image_to_string(img,lang='ara+eng'))
                ocr_text='\n\n'.join(ocr_parts).strip()
                if ocr_text:
                    text=ocr_text; meta['ocr']=True
                else: warnings.append('PDF scan detected but OCR returned no text')
            except Exception:
                warnings.append('PDF has little/no selectable text; install Tesseract + pytesseract for OCR')
        return text,tables,meta,'; '.join(warnings) or None
    except Exception:
        try:
            from pypdf import PdfReader
            reader=PdfReader(str(path))
            parts=[p.extract_text() or '' for p in reader.pages]
            return '\n\n'.join(parts),tables,{"page_count":len(reader.pages)},None
        except Exception as e:
            return '',[],{},f'PDF parser unavailable: {e}'

def _parse_docx(path: Path) -> tuple[str,List[List[List[str]]],Dict[str,Any]]:
    from docx import Document
    doc=Document(str(path)); parts=[p.text for p in doc.paragraphs if p.text.strip()]; tables=[]
    for t in doc.tables:
        rows=[]
        for r in t.rows: rows.append([c.text for c in r.cells])
        tables.append(rows)
    return '\n'.join(parts), tables, {"paragraphs":len(doc.paragraphs),"tables":len(doc.tables)}

def _parse_html(path: Path) -> str:
    from bs4 import BeautifulSoup
    soup=BeautifulSoup(_read_text(path),'html.parser')
    for tag in soup(['script','style','noscript']): tag.decompose()
    return soup.get_text('\n')

def _xml_text(path: Path) -> str:
    root=ET.fromstring(_read_text(path)); return '\n'.join(t.strip() for t in root.itertext() if t.strip())

def safe_extract_zip(path: Path, dest: Path) -> List[str]:
    out=[]; dest=dest.resolve(); dest.mkdir(parents=True,exist_ok=True)
    with zipfile.ZipFile(path) as z:
        for info in z.infolist():
            target=(dest/info.filename).resolve()
            if dest not in target.parents and target != dest: raise ValueError(f'archive path traversal blocked: {info.filename}')
        for info in z.infolist():
            if info.is_dir(): continue
            target=(dest/info.filename).resolve(); target.parent.mkdir(parents=True,exist_ok=True)
            with z.open(info) as src, open(target,'wb') as dst: dst.write(src.read())
            out.append(str(target))
    return out

def safe_extract_tar(path: Path, dest: Path) -> List[str]:
    out=[]; dest=dest.resolve(); dest.mkdir(parents=True,exist_ok=True)
    with tarfile.open(path) as t:
        members=[]
        for m in t.getmembers():
            target=(dest/m.name).resolve()
            if dest not in target.parents and target != dest: raise ValueError(f'archive path traversal blocked: {m.name}')
            if m.isdir() or m.isfile(): members.append(m)
        t.extractall(dest, members=members)
        out=[str((dest/m.name).resolve()) for m in members if m.isfile()]
    return out


def safe_extract_optional(path: Path, dest: Path) -> List[str]:
    ext=path.suffix.lower(); dest=dest.resolve(); dest.mkdir(parents=True,exist_ok=True)
    if ext=='.rar':
        try:
            import rarfile
            with rarfile.RarFile(path) as rf:
                for info in rf.infolist():
                    target=(dest/info.filename).resolve()
                    if dest not in target.parents and target!=dest: raise ValueError(f'archive path traversal blocked: {info.filename}')
                rf.extractall(dest)
            return [str(p) for p in dest.rglob('*') if p.is_file()]
        except ImportError:
            import shutil, subprocess
            exe=shutil.which('7z') or shutil.which('7zz') or shutil.which('7za') or shutil.which('unrar')
            if not exe: raise RuntimeError('RAR support needs rarfile or a 7-Zip/unrar executable on PATH')
            subprocess.run([exe,'x','-y',str(path),f'-o{dest}'],check=True,capture_output=True,text=True,timeout=600)
            return [str(p) for p in dest.rglob('*') if p.is_file()]
    if ext=='.7z':
        try:
            import py7zr
            with py7zr.SevenZipFile(path,'r') as z: z.extractall(dest)
            return [str(p) for p in dest.rglob('*') if p.is_file()]
        except ImportError:
            import shutil, subprocess
            exe=shutil.which('7z') or shutil.which('7zz') or shutil.which('7za')
            if not exe: raise RuntimeError('7z support needs py7zr or a 7-Zip executable on PATH')
            subprocess.run([exe,'x','-y',str(path),f'-o{dest}'],check=True,capture_output=True,text=True,timeout=600)
            return [str(p) for p in dest.rglob('*') if p.is_file()]
    raise RuntimeError(f'unsupported archive: {path.suffix}')

def parse_file(path: str|Path, extract_root: str|Path|None=None) -> ParsedDocument:
    p=Path(path); ext=p.suffix.lower(); kind=ext.lstrip('.') or 'unknown'
    metadata={"name":p.name,"size":p.stat().st_size}
    text=''; tables=[]; extracted=[]; warning=None
    try:
        if ext in {'.txt','.md','.py','.js','.ts','.tsx','.jsx','.css','.jsonl','.log','.ini','.yaml','.yml','.toml'}:
            text=_read_text(p)
        elif ext=='.json': text=_parse_json(p); kind='json'
        elif ext=='.csv': text,tables=_parse_csv(p); kind='csv'
        elif ext=='.xml': text=_xml_text(p); kind='xml'
        elif ext in {'.html','.htm'}: text=_parse_html(p); kind='html'
        elif ext=='.pdf': text,tables,meta2,warning=_parse_pdf(p); metadata.update(meta2); kind='pdf'
        elif ext=='.docx': text,tables,meta2=_parse_docx(p); metadata.update(meta2); kind='docx'
        elif ext=='.zip' and extract_root:
            extracted=safe_extract_zip(p,Path(extract_root)/p.stem); text='\n'.join(extracted); kind='archive'
        elif ext in {'.rar','.7z'} and extract_root:
            extracted=safe_extract_optional(p,Path(extract_root)/p.stem); text='\n'.join(extracted); kind='archive'
        elif ext in {'.tar','.gz','.bz2','.xz','.tgz','.tbz2'} and extract_root:
            if tarfile.is_tarfile(p): extracted=safe_extract_tar(p,Path(extract_root)/p.stem); kind='archive'; text='\n'.join(extracted)
            elif ext=='.gz': text=gzip.decompress(p.read_bytes()).decode('utf-8','replace')
            elif ext=='.bz2': text=bz2.decompress(p.read_bytes()).decode('utf-8','replace')
            elif ext=='.xz': text=lzma.decompress(p.read_bytes()).decode('utf-8','replace')
        else:
            warning='Unsupported or binary format; file indexed by metadata only'
    except Exception as e:
        warning=str(e)
    return ParsedDocument(str(p),kind,text,metadata,tables,extracted,warning)
```

---

### `80/588` `backend/data_engine/review.py`

- **المسار الكامل:** `F:\1f\p\ALI_Studio_Pro_Design4_4.6.0\04_Adaptive_Hybrid\backend/data_engine/review.py`
- **الحجم:** 830 بايت (0.8 KB)
- **الامتداد:** `.py`

```python
# -*- coding: utf-8 -*-
"""Human-review queue for training samples."""
from __future__ import annotations
from pathlib import Path
import sqlite3

class DatasetReview:
    def __init__(self, db_path: str | Path): self.path=Path(db_path)
    def pending(self, limit=100):
        c=sqlite3.connect(self.path); c.row_factory=sqlite3.Row
        rows=[dict(r) for r in c.execute("SELECT * FROM samples WHERE quality='REVIEW' ORDER BY id LIMIT ?",(limit,)).fetchall()]
        c.close(); return rows
    def decide(self, sample_id:int, quality:str, reason:str=''):
        quality=quality.upper()
        if quality not in {'ACCEPTED','REJECTED','REVIEW'}: raise ValueError(quality)
        c=sqlite3.connect(self.path); c.execute("UPDATE samples SET quality=?, reason=? WHERE id=?",(quality,reason,sample_id)); c.commit(); c.close()
```

---

### `81/588` `backend/database/__init__.py`

- **المسار الكامل:** `F:\1f\p\ALI_Studio_Pro_Design4_4.6.0\04_Adaptive_Hybrid\backend/database/__init__.py`
- **الحجم:** 49 بايت (0.0 KB)
- **الامتداد:** `.py`

```python
# -*- coding: utf-8 -*-
"""حزمة database."""
```

---

### `82/588` `backend/database/database.py`

- **المسار الكامل:** `F:\1f\p\ALI_Studio_Pro_Design4_4.6.0\04_Adaptive_Hybrid\backend/database/database.py`
- **الحجم:** 16280 بايت (15.9 KB)
- **الامتداد:** `.py`

```python
# -*- coding: utf-8 -*-
"""طبقة قاعدة البيانات V0.2.

- SQLite + WAL للسرعة على Windows.
- thread-safe عبر check_same_thread=False + per-thread connection + lock.
- Migrations حقيقية مسجلة في database.schema.
- جداول: projects, threads, messages, tool_calls, settings, logs, sessions.
- Repositories بسيطة (ProjectRepo, ThreadRepo, MessageRepo).
"""

from __future__ import annotations

import sqlite3
import threading
import time
import uuid
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Iterable, List, Optional, Sequence

from config.paths import APP_PATHS
from core.logger import get_logger
from database.schema import ALL_MIGRATIONS, SCHEMA_VERSION

log = get_logger("db")

# قفل عام لتأمين كتابة schema مرة واحدة.
_BOOTSTRAP_LOCK = threading.Lock()
_BOOTSTRAPPED: set = set()


# ---------------------------------------------------------------------------
# Database core
# ---------------------------------------------------------------------------
class Database:
    """طبقة قاعدة بيانات بسيطة. Singleton داخل العملية."""

    _instance: "Optional[Database]" = None
    _instance_lock = threading.Lock()

    def __init__(self, db_path: Optional[Path] = None):
        self.db_path = db_path or (APP_PATHS.user_data_dir() / "ali.db")
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._local = threading.local()
        # أول thread يبدأ الـ bootstrap.
        self._bootstrap()

    # --------------------------------------------------------------- singleton
    @classmethod
    def instance(cls) -> "Database":
        with cls._instance_lock:
            if cls._instance is None:
                cls._instance = Database()
            return cls._instance

    # --------------------------------------------------------------- connection
    def _conn(self) -> sqlite3.Connection:
        c = getattr(self._local, "conn", None)
        if c is None:
            c = sqlite3.connect(
                str(self.db_path),
                check_same_thread=False,
                isolation_level=None,
                timeout=5.0,
            )
            c.row_factory = sqlite3.Row
            c.execute("PRAGMA journal_mode=WAL;")
            c.execute("PRAGMA synchronous=NORMAL;")
            c.execute("PRAGMA foreign_keys=ON;")
            self._local.conn = c
        return c

    @contextmanager
    def tx(self):
        c = self._conn()
        c.execute("BEGIN;")
        try:
            yield c
            c.execute("COMMIT;")
        except Exception:
            c.execute("ROLLBACK;")
            raise

    @contextmanager
    def cursor(self):
        c = self._conn()
        cur = c.cursor()
        try:
            yield cur
        finally:
            cur.close()

    # --------------------------------------------------------------- bootstrap
    def _bootstrap(self) -> None:
        """إنشاء جدول meta + تشغيل migrations."""
        # أول bootstrap فقط في العالم (لكل db_path)
        key = str(self.db_path)
        if key in _BOOTSTRAPPED:
            return
        with _BOOTSTRAP_LOCK:
            if key in _BOOTSTRAPPED:
                return
            c = self._conn()
            c.execute("""
                CREATE TABLE IF NOT EXISTS meta (
                    key   TEXT PRIMARY KEY,
                    value TEXT NOT NULL
                );
            """)
            c.execute(
                "INSERT OR IGNORE INTO meta(key, value) "
                "VALUES('schema_version', '0');"
            )
            current = int(c.execute(
                "SELECT value FROM meta WHERE key='schema_version';"
            ).fetchone()[0])
            log.info("DB bootstrap at %s (current schema_version=%d)",
                     self.db_path, current)
            for v, fn in ALL_MIGRATIONS:
                if v > current:
                    log.info("Applying migration %d", v)
                    c.execute("BEGIN;")
                    try:
                        fn(c)
                        c.execute(
                            "INSERT OR REPLACE INTO meta(key, value) "
                            "VALUES('schema_version', ?);",
                            (str(v),),
                        )
                        c.execute("COMMIT;")
                    except Exception as e:
                        c.execute("ROLLBACK;")
                        log.error("Migration %d failed: %s", v, e)
                        raise
            _BOOTSTRAPPED.add(key)

    # --------------------------------------------------------------- helpers
    def get_meta(self, key: str, default: Optional[str] = None) -> Optional[str]:
        with self.cursor() as cur:
            row = cur.execute(
                "SELECT value FROM meta WHERE key=?;", (key,)
            ).fetchone()
            return row["value"] if row else default

    def set_meta(self, key: str, value: str) -> None:
        with self.tx() as c:
            c.execute(
                "INSERT INTO meta(key, value) VALUES(?, ?) "
                "ON CONFLICT(key) DO UPDATE SET value=excluded.value;",
                (key, value),
            )

    def healthcheck(self) -> dict:
        with self.cursor() as cur:
            row = cur.execute("PRAGMA journal_mode;").fetchone()
            row2 = cur.execute("PRAGMA foreign_keys;").fetchone()
            sv = cur.execute(
                "SELECT value FROM meta WHERE key='schema_version';"
            ).fetchone()
            return {
                "path": str(self.db_path),
                "journal_mode": row[0] if row else "?",
                "foreign_keys": bool(row2[0]) if row2 else False,
                "schema_version": int(sv[0]) if sv else 0,
            }


def get_db() -> Database:
    return Database.instance()


def reset_database_for_tests() -> None:
    """إعادة تعيين الـ singleton (للاختبارات فقط)."""
    global _BOOTSTRAPPED
    Database._instance = None
    _BOOTSTRAPPED.clear()


# ---------------------------------------------------------------------------
# Repository: projects
# ---------------------------------------------------------------------------
class ProjectRepo:
    def __init__(self, db: Database):
        self.db = db

    def create(self, name: str, root_path: str) -> str:
        pid = "p_" + uuid.uuid4().hex[:12]
        now = time.time()
        with self.db.tx() as c:
            c.execute(
                "INSERT INTO projects(id, name, root_path, "
                "created_at, updated_at) VALUES(?, ?, ?, ?, ?);",
                (pid, name, root_path, now, now),
            )
        return pid

    def get(self, pid: str) -> Optional[dict]:
        with self.db.cursor() as cur:
            row = cur.execute(
                "SELECT * FROM projects WHERE id=?;", (pid,)
            ).fetchone()
            return dict(row) if row else None

    def by_path(self, root_path: str) -> Optional[dict]:
        with self.db.cursor() as cur:
            row = cur.execute(
                "SELECT * FROM projects WHERE root_path=? "
                "ORDER BY updated_at DESC LIMIT 1;",
                (root_path,),
            ).fetchone()
            return dict(row) if row else None

    def touch(self, pid: str) -> None:
        with self.db.tx() as c:
            c.execute(
                "UPDATE projects SET updated_at=? WHERE id=?;",
                (time.time(), pid),
            )

    def list_recent(self, limit: int = 20) -> List[dict]:
        with self.db.cursor() as cur:
            rows = cur.execute(
                "SELECT * FROM projects ORDER BY updated_at DESC LIMIT ?;",
                (limit,),
            ).fetchall()
            return [dict(r) for r in rows]


# ---------------------------------------------------------------------------
# Repository: threads
# ---------------------------------------------------------------------------
class ThreadRepo:
    def __init__(self, db: Database):
        self.db = db

    def create(self, project_id: Optional[str], title: str = "New thread") -> str:
        tid = "t_" + uuid.uuid4().hex[:12]
        now = time.time()
        with self.db.tx() as c:
            c.execute(
                "INSERT INTO threads(id, project_id, title, "
                "created_at, updated_at) VALUES(?, ?, ?, ?, ?);",
                (tid, project_id, title, now, now),
            )
        return tid

    def rename(self, tid: str, title: str) -> None:
        with self.db.tx() as c:
            c.execute(
                "UPDATE threads SET title=?, updated_at=? WHERE id=?;",
                (title, time.time(), tid),
            )

    def get(self, tid: str) -> Optional[dict]:
        with self.db.cursor() as cur:
            row = cur.execute(
                "SELECT * FROM threads WHERE id=?;", (tid,)
            ).fetchone()
            return dict(row) if row else None

    def list_for_project(self, project_id: str, limit: int = 50) -> List[dict]:
        with self.db.cursor() as cur:
            rows = cur.execute(
                "SELECT * FROM threads WHERE project_id=? "
                "ORDER BY updated_at DESC LIMIT ?;",
                (project_id, limit),
            ).fetchall()
            return [dict(r) for r in rows]

    def list_all(self, limit: int = 50) -> List[dict]:
        with self.db.cursor() as cur:
            rows = cur.execute(
                "SELECT * FROM threads ORDER BY updated_at DESC LIMIT ?;",
                (limit,),
            ).fetchall()
            return [dict(r) for r in rows]

    def touch(self, tid: str) -> None:
        with self.db.tx() as c: