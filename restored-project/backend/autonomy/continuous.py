# -*- coding: utf-8 -*-
"""Incremental learning planner with identities across harvested data and conversations."""
from __future__ import annotations
from pathlib import Path
import json, sqlite3, hashlib, time
from typing import Any

class ContinuousLearning:
    def __init__(self, root:str|Path, min_new_samples:int=24):
        self.root=Path(root); self.min_new_samples=max(1,int(min_new_samples)); self.state=self.root/'artifacts'/'continuous_state.json'; self.state.parent.mkdir(parents=True,exist_ok=True)
    def _read(self):
        try:return json.loads(self.state.read_text(encoding='utf-8'))
        except Exception:return {'dataset_identity':'','trained_count':0,'last_trained_sample_id':0,'conversation_trained_at':0.0,'gguf_identity':'','gguf_checkpoint_hash':''}
    def accepted_rows(self,db:str|Path):
        p=Path(db)
        if not p.exists(): return []
        c=sqlite3.connect(p); rows=c.execute("SELECT id,sample_hash FROM samples WHERE quality='ACCEPTED' ORDER BY id").fetchall(); c.close(); return rows
    def conversation_rows(self,db:str|Path):
        p=Path(db)
        if not p.exists(): return []
        c=sqlite3.connect(p); rows=c.execute("SELECT id,pair_hash,updated_at FROM conversations WHERE quality>=0.6 ORDER BY id").fetchall(); c.close(); return rows
    def accepted_identity(self, db:str|Path, conversation_db:str|Path|None=None)->tuple[str,int,int,float]:
        h=hashlib.sha256(); count=0; last_id=0; conv_latest=0.0
        for rid,x in self.accepted_rows(db):
            h.update(b'H:'); h.update(str(x).encode('utf-8')); h.update(b'\n'); count+=1; last_id=max(last_id,int(rid))
        if conversation_db:
            for rid,x,ts in self.conversation_rows(conversation_db):
                h.update(b'C:'); h.update(str(x).encode('utf-8')); h.update(b'\n'); count+=1; conv_latest=max(conv_latest,float(ts))
        return h.hexdigest(),count,last_id,conv_latest
    def plan(self,db:str|Path, conversation_db:str|Path|None=None)->dict[str,Any]:
        ident,count,last_id,conv_latest=self.accepted_identity(db,conversation_db); st=self._read(); prior=int(st.get('trained_count',0));
        # Counts are additive across both sources, while the identity remains the authoritative gate.
        new=max(0,count-prior); changed=bool(ident and ident!=st.get('dataset_identity'))
        return {'dataset_identity':ident,'accepted':count,'new_samples':new,'last_sample_id':last_id,'conversation_latest_ts':conv_latest,'train_needed':bool(changed and count>0 and (new>=self.min_new_samples or not st.get('dataset_identity'))),'new_since_gguf':bool(ident and ident!=st.get('gguf_identity')),'duplicate_safe':True}
    def record_training(self,db:str|Path,checkpoint:str|Path,metrics:dict|None=None,conversation_db:str|Path|None=None):
        ident,count,last_id,conv_latest=self.accepted_identity(db,conversation_db); st=self._read(); st.update({'dataset_identity':ident,'trained_count':count,'last_trained_sample_id':last_id,'conversation_trained_at':conv_latest,'last_checkpoint':str(checkpoint),'last_metrics':metrics or {},'trained_at':time.time()}); self.state.write_text(json.dumps(st,ensure_ascii=False,indent=2),encoding='utf-8')
    def record_gguf(self,db:str|Path,gguf:str|Path,checkpoint_hash:str='',conversation_db:str|Path|None=None):
        ident,count,last_id,conv_latest=self.accepted_identity(db,conversation_db); st=self._read(); st.update({'gguf_identity':ident,'gguf_path':str(gguf),'gguf_checkpoint_hash':checkpoint_hash,'gguf_at':time.time(),'gguf_count':count,'gguf_last_sample_id':last_id,'conversation_gguf_at':conv_latest}); self.state.write_text(json.dumps(st,ensure_ascii=False,indent=2),encoding='utf-8')
    def status(self,db:str|Path,conversation_db:str|Path|None=None):
        ident,count,last_id,conv_latest=self.accepted_identity(db,conversation_db); st=self._read(); return {**st,'accepted':count,'dataset_identity':ident,'last_sample_id':last_id,'conversation_latest_ts':conv_latest,'new_samples':max(0,count-int(st.get('trained_count',0))),'gguf_current':bool(ident and st.get('gguf_identity')==ident)}
