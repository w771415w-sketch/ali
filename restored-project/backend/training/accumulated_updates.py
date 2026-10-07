# -*- coding: utf-8 -*-
"""ALI AI 2.5 accumulated Markdown training update manager."""
from __future__ import annotations
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Any, Iterable
import hashlib, json, re, shutil, sqlite3, time, uuid
from data_engine.normalization import normalize_text, redact_secrets, normalized_hash
from training.pipeline import PipelineConfig, TrainingPipeline
from training.lora import apply_lora, load_lora_adapter, merge_lora
from model.ali_lm import save_hf_checkpoint
from tokenizer.spm import AliTokenizer

MD_LIMIT_BYTES=20*1024*1024
ALLOWED_SUFFIXES={'.md','.markdown'}
DEFAULT_MERGE_THRESHOLD=4
REQUIRED_ROLE_MARKERS=(('<|user|>','<|assistant|>'),('## user','## assistant'),('### user','### assistant'),('**user:**','**assistant:**'),('User:','Assistant:'))

@dataclass
class MDValidation:
    path:str; accepted:bool; size_bytes:int; sha256:str; content_hash:str; samples:int; characters:int; secret_redacted:bool
    duplicate:bool=False; reason:str=''; warnings:list[str]|None=None
    def to_dict(self)->dict[str,Any]: return asdict(self)

class AccumulatedTrainingManager:
    def __init__(self,root:str|Path,*,merge_threshold:int=DEFAULT_MERGE_THRESHOLD):
        self.root=Path(root).resolve(); self.merge_threshold=max(1,int(merge_threshold))
        self.updates=self.root/'training'/'updates'; self.inbox=self.updates/'inbox'; self.validated=self.updates/'validated'; self.batches=self.updates/'batches'
        self.adapters=self.root/'models'/'adapters'; self.pending=self.adapters/'pending'; self.adapter_archive=self.adapters/'archive'; self.model_archive=self.root/'models'/'archive'
        for p in (self.inbox,self.validated,self.batches,self.pending,self.adapter_archive,self.model_archive): p.mkdir(parents=True,exist_ok=True)
        self.db_path=self.root/'artifacts'/'accumulated_training.sqlite3'; self.db_path.parent.mkdir(parents=True,exist_ok=True); self._init_db()
    def _connect(self):
        c=sqlite3.connect(self.db_path); c.row_factory=sqlite3.Row; return c
    def _init_db(self):
        with self._connect() as c:
            c.execute("CREATE TABLE IF NOT EXISTS sources(id INTEGER PRIMARY KEY,source_hash TEXT UNIQUE NOT NULL,original_name TEXT NOT NULL,stored_path TEXT NOT NULL,content_hash TEXT NOT NULL,status TEXT NOT NULL,samples INTEGER DEFAULT 0,characters INTEGER DEFAULT 0,secret_redacted INTEGER DEFAULT 0,reason TEXT DEFAULT '',created_at REAL NOT NULL)")
            c.execute("CREATE TABLE IF NOT EXISTS adapters(id INTEGER PRIMARY KEY,adapter_id TEXT UNIQUE NOT NULL,path TEXT NOT NULL,base_version TEXT NOT NULL,dataset_hash TEXT NOT NULL,status TEXT NOT NULL,created_at REAL NOT NULL,merged_into TEXT DEFAULT '')")
            c.execute("CREATE TABLE IF NOT EXISTS merges(id INTEGER PRIMARY KEY,merge_id TEXT UNIQUE NOT NULL,adapter_ids_json TEXT NOT NULL,base_version TEXT NOT NULL,output_path TEXT NOT NULL,status TEXT NOT NULL,created_at REAL NOT NULL,verification_json TEXT DEFAULT '{}')")
    @staticmethod
    def _sha256(path:Path)->str:
        h=hashlib.sha256();
        with path.open('rb') as f:
            for b in iter(lambda:f.read(1024*1024),b''): h.update(b)
        return h.hexdigest()
    @staticmethod
    def _count_samples(text:str)->int:
        markers=sum(text.lower().count(x) for pair in REQUIRED_ROLE_MARKERS for x in pair)
        return max(1,markers//2) if markers>=2 else (1 if len(text.strip())>=80 else 0)
    @staticmethod
    def _extract_training_text(text:str)->str:
        text=re.sub(r'^\ufeff','',text); text=re.sub(r'^---\s*\n.*?\n---\s*\n','',text,flags=re.S); return text.strip()
    def validate_md(self,path:str|Path)->MDValidation:
        p=Path(path).resolve(); w=[]
        if not p.exists() or not p.is_file(): return MDValidation(str(p),False,0,'','',0,0,False,reason='file_not_found',warnings=w)
        if p.suffix.lower() not in ALLOWED_SUFFIXES: return MDValidation(str(p),False,p.stat().st_size,'','',0,0,False,reason='only .md/.markdown files are accepted',warnings=w)
        size=p.stat().st_size; sha=self._sha256(p)
        if size<=0: return MDValidation(str(p),False,0,sha,'',0,0,False,reason='empty_file',warnings=w)
        if size>MD_LIMIT_BYTES: return MDValidation(str(p),False,size,sha,'',0,0,False,reason=f'file_too_large>{MD_LIMIT_BYTES}',warnings=w)
        raw=p.read_text(encoding='utf-8',errors='replace'); text=normalize_text(self._extract_training_text(raw)); safe,changed=redact_secrets(text)
        if changed: w.append('secrets_redacted')
        chars=len(safe); samples=self._count_samples(safe); chash=normalized_hash(safe)
        with self._connect() as c: dup=bool(c.execute('SELECT 1 FROM sources WHERE content_hash=? LIMIT 1',(chash,)).fetchone())
        if chars<80: return MDValidation(str(p),False,size,sha,chash,samples,chars,changed,reason='content_too_short',warnings=w)
        if dup: return MDValidation(str(p),False,size,sha,chash,samples,chars,changed,duplicate=True,reason='duplicate_content',warnings=w)
        return MDValidation(str(p),True,size,sha,chash,samples,chars,changed,warnings=w)
    def add_files(self,paths:Iterable[str|Path])->list[dict[str,Any]]:
        out=[]
        for raw in paths:
            p=Path(raw); rep=self.validate_md(p)
            if not rep.accepted: out.append(rep.to_dict()); continue
            stored=self.validated/f'{rep.content_hash[:16]}_{p.name}'; shutil.copy2(p,stored)
            text=normalize_text(p.read_text(encoding='utf-8',errors='replace')); text,_=redact_secrets(text)
            batch_id=f'update-{time.strftime("%Y%m%d-%H%M%S")}-{uuid.uuid4().hex[:8]}'; jsonl=self.batches/f'{batch_id}.jsonl'
            row={'id':rep.content_hash,'messages':[{'role':'system','content':'You are ALI. Use the supplied approved training material faithfully.'},{'role':'user','content':'Learn from this approved training material.'},{'role':'assistant','content':text}], 'source':str(stored),'source_hash':rep.sha256,'content_hash':rep.content_hash,'provenance':{'format':'markdown','approved_by':'user','redacted_secrets':rep.secret_redacted}}
            jsonl.write_text(json.dumps(row,ensure_ascii=False)+'\n',encoding='utf-8')
            with self._connect() as c:
                c.execute('INSERT INTO sources(source_hash,original_name,stored_path,content_hash,status,samples,characters,secret_redacted,reason,created_at) VALUES(?,?,?,?,?,?,?,?,?,?)',(rep.sha256,p.name,str(stored),rep.content_hash,'validated',rep.samples,rep.characters,int(rep.secret_redacted),'',time.time()))
            d=rep.to_dict(); d.update({'stored_path':str(stored),'batch_id':batch_id,'jsonl':str(jsonl),'status':'validated'}); out.append(d)
        return out
    def pending_batch_paths(self)->list[Path]:
        with self._connect() as c: rows=c.execute("SELECT content_hash FROM sources WHERE status='validated' ORDER BY id").fetchall()
        wanted={str(r['content_hash']) for r in rows}; paths=[]
        for p in sorted(self.batches.glob('*.jsonl')):
            try:
                obj=json.loads(p.read_text(encoding='utf-8').splitlines()[0]); cid=str(obj.get('content_hash') or obj.get('id') or '')
                if cid in wanted: paths.append(p)
            except Exception: continue
        return paths
    def mark_sources_as_adapterized(self,paths:Iterable[str|Path])->int:
        hashes=set()
        for raw in paths:
            p=Path(raw)
            try:
                for line in p.read_text(encoding='utf-8').splitlines():
                    o=json.loads(line); h=str(o.get('content_hash') or o.get('id') or '')
                    if h: hashes.add(h)
            except Exception: continue
        if not hashes: return 0
        with self._connect() as c:
            for h in hashes: c.execute("UPDATE sources SET status='adapter_pending' WHERE content_hash=? AND status='validated'",(h,))
        return len(hashes)
    def status(self)->dict[str,Any]:
        with self._connect() as c:
            pending=c.execute("SELECT * FROM adapters WHERE status='pending' ORDER BY id").fetchall(); validated=c.execute("SELECT COUNT(*) n FROM sources WHERE status='validated'").fetchone()['n']; consumed=c.execute("SELECT COUNT(*) n FROM sources WHERE status='adapter_pending'").fetchone()['n']
        return {'validated_sources':int(validated),'adapterized_sources':int(consumed),'pending_adapters':len(pending),'merge_threshold':self.merge_threshold,'merge_ready':len(pending)>=self.merge_threshold,'pending':[dict(x) for x in pending]}
    def register_adapter(self,path:str|Path,*,base_version:str,dataset_hash:str,metadata:dict[str,Any]|None=None)->str:
        adapter_id=f'adapter-{time.strftime("%Y%m%d-%H%M%S")}-{uuid.uuid4().hex[:8]}'; dest=self.pending/adapter_id; shutil.copytree(Path(path),dest)
        meta=dict(metadata or {}); meta.update({'adapter_id':adapter_id,'base_version':base_version,'dataset_hash':dataset_hash,'status':'pending','created_at':time.time()})
        (dest/'accumulated_manifest.json').write_text(json.dumps(meta,ensure_ascii=False,indent=2),encoding='utf-8')
        with self._connect() as c: c.execute('INSERT INTO adapters(adapter_id,path,base_version,dataset_hash,status,created_at) VALUES(?,?,?,?,?,?)',(adapter_id,str(dest),base_version,dataset_hash,'pending',time.time()))
        return adapter_id
    def _load_model_for_merge(self,base_path:Path):
        pipeline=TrainingPipeline(self.root); cfg=PipelineConfig(stage='lora',base_checkpoint=str(base_path),scale='micro',train_path='',device='cpu')
        candidates=[base_path/'tokenizer.model',base_path/'hf'/'tokenizer.model',base_path/'merged_hf'/'tokenizer.model',base_path.parent/'tokenizer.model']; tok_model=next((p for p in candidates if p.exists()),None)
        if tok_model is None: raise FileNotFoundError('base tokenizer.model not found')
        tokenizer=AliTokenizer(tok_model); model=pipeline.new_model(cfg,tokenizer.vocab_size); return model,tokenizer,tok_model.parent
    def merge_pending(self,active:dict[str,Any],*,keep_archives:bool=True)->dict[str,Any]:
        with self._connect() as c: rows=c.execute("SELECT * FROM adapters WHERE status='pending' ORDER BY id LIMIT ?",(self.merge_threshold,)).fetchall()
        if len(rows)<self.merge_threshold: return {'ok':True,'status':'waiting','reason':'merge_threshold_not_reached','pending':len(rows),'threshold':self.merge_threshold}
        base_raw=active.get('hf_dir') or active.get('checkpoint');
        if not base_raw: raise ValueError('active model has no HF/checkpoint path')
        base=Path(base_raw).resolve(); merge_id=f'merge-{time.strftime("%Y%m%d-%H%M%S")}-{uuid.uuid4().hex[:8]}'; out=self.root/'models'/'merged'/'ALI'/merge_id; out.mkdir(parents=True,exist_ok=True)
        model,tokenizer,tokenizer_dir=self._load_model_for_merge(base); applied=[]
        try:
            for row in rows:
                adapter_path=Path(row['path']); apply_lora(model,rank=8,alpha=16.0,dropout=.05); load_lora_adapter(model,adapter_path); merge_lora(model); applied.append(row['adapter_id'])
            save_hf_checkpoint(model,tokenizer_dir,out,{'accumulated_merge_id':merge_id,'base_version':active.get('version',''),'adapter_ids':applied,'adapter_count':len(applied),'created_at':time.time()})
            manifest={'merge_id':merge_id,'base_version':active.get('version',''),'adapter_ids':applied,'adapter_count':len(applied),'output':str(out),'status':'candidate'}; (out/'accumulated_merge_manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8')
            with self._connect() as c:
                c.execute('INSERT INTO merges(merge_id,adapter_ids_json,base_version,output_path,status,created_at,verification_json) VALUES(?,?,?,?,?,?,?)',(merge_id,json.dumps(applied),active.get('version',''),str(out),'candidate',time.time(),'{}'))
                for aid in applied: c.execute("UPDATE adapters SET status='merged_candidate',merged_into=? WHERE adapter_id=?",(merge_id,aid))
            if keep_archives:
                for row in rows:
                    src=Path(row['path']);
                    if src.exists(): shutil.move(str(src),str(self.adapter_archive/row['adapter_id']))
            return {'ok':True,'status':'candidate','merge_id':merge_id,'output':str(out),'adapter_ids':applied}
        except Exception: raise
