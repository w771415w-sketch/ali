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
