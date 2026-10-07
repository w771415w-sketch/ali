# -*- coding: utf-8 -*-
"""Conservative, autonomous model-improvement control for ALI.

The service never mutates source code blindly. It can automatically build an
incremental dataset from approved data/conversations, train a candidate, run
regression/evaluation, and promote only a verified candidate. Source-code
changes remain behind the existing improvement/promotion gate.
"""
from __future__ import annotations
from pathlib import Path
import json, sqlite3, hashlib, time
from typing import Any

class SelfManager:
    def __init__(self, root: str|Path, min_new_samples: int = 32):
        self.root=Path(root); self.min_new_samples=max(1,int(min_new_samples))
        self.state_path=self.root/'artifacts'/'self_manager.json'; self.state_path.parent.mkdir(parents=True,exist_ok=True)

    def _state(self)->dict[str,Any]:
        try:return json.loads(self.state_path.read_text(encoding='utf-8'))
        except Exception:return {'trained_sample_count':0,'trained_dataset_hash':'','last_run':0,'last_status':'never','last_candidate':'','last_error':''}

    def _accepted(self,db: str|Path, conversation_db: str|Path|None=None)->tuple[int,str]:
        h=hashlib.sha256(); count=0
        p=Path(db)
        if p.exists():
            c=sqlite3.connect(p);
            try: rows=c.execute("SELECT sample_hash FROM samples WHERE quality='ACCEPTED' ORDER BY id").fetchall()
            except sqlite3.Error: rows=[]
            c.close()
            for (x,) in rows:h.update(b'H:'); h.update(str(x).encode('utf-8')); h.update(b'\n'); count+=1
        cp=Path(conversation_db) if conversation_db else None
        if cp and cp.exists():
            c=sqlite3.connect(cp);
            try: rows=c.execute("SELECT pair_hash FROM conversations WHERE quality>=0.6 ORDER BY id").fetchall()
            except sqlite3.Error: rows=[]
            c.close()
            for (x,) in rows:h.update(b'C:'); h.update(str(x).encode('utf-8')); h.update(b'\n'); count+=1
        return count,h.hexdigest()

    def status(self,db: str|Path, conversation_db: str|Path|None=None)->dict[str,Any]:
        count,digest=self._accepted(db,conversation_db); st=self._state(); new=max(0,count-int(st.get('trained_sample_count',0)))
        return {**st,'accepted_samples':count,'new_samples':new,'dataset_hash':digest,'last_trained_count':int(st.get('trained_sample_count',0)),'ready':new>=self.min_new_samples}

    def should_schedule(self,db: str|Path, conversation_db: str|Path|None=None)->bool:
        return bool(self.status(db,conversation_db)['ready'])

    def mark_trained(self,db: str|Path, conversation_db: str|Path|None=None, **extra)->dict[str,Any]:
        count,digest=self._accepted(db,conversation_db); st=self._state();
        st.update({'trained_sample_count':count,'trained_dataset_hash':digest,'last_run':time.time(),**extra})
        self.state_path.write_text(json.dumps(st,ensure_ascii=False,indent=2),encoding='utf-8'); return st

    def autonomous_cycle(
        self,
        db: str|Path,
        conversation_db: str|Path|None=None,
        validation_path: str|Path|None=None,
        *,
        scale: str='micro',
        steps: int=1,
        device: str='cpu',
        force: bool=False,
        progress=None,
    )->dict[str,Any]:
        """Run one complete self-learning cycle and return an auditable report."""
        def emit(message, value=None, **extra):
            if progress:
                progress(message, value, **extra)

        from autonomy.continuous import ContinuousLearning
        from data_engine.dataset_builder import export_incremental, export_conversation_incremental
        from model.registry import ModelRegistry
        from training.pipeline import TrainingPipeline, PipelineConfig
        from autonomy.improvement import ImprovementLoop
        from training.evaluator import promotion_gate

        cl=ContinuousLearning(self.root, self.min_new_samples)
        plan=cl.plan(self.root/db, self.root/conversation_db if conversation_db else None)
        emit('checking learning gate', .05, plan=plan)
        if not force and not plan['train_needed']:
            return {'ok':True,'status':'idle','reason':'learning gate not reached','plan':plan}

        st=cl._read(); after_id=int(st.get('last_trained_sample_id',0)); after_ts=float(st.get('conversation_trained_at',0.0))
        parts=[]
        a=self.root/'data/training/incremental/harvest.jsonl'; b=self.root/'data/training/incremental/conversations.jsonl'
        if Path(self.root/db).exists(): parts.append(export_incremental(self.root/db,a,after_id))
        if conversation_db and Path(self.root/conversation_db).exists(): parts.append(export_conversation_incremental(self.root/conversation_db,b,after_ts,min_quality=.6))
        merged=self.root/'data/training/incremental/current.jsonl'; merged.parent.mkdir(parents=True,exist_ok=True)
        seen=set(); written=0
        with merged.open('w',encoding='utf-8') as out:
            for part in parts:
                pp=Path(part['output'])
                if not pp.exists(): continue
                for line in pp.read_text(encoding='utf-8',errors='replace').splitlines():
                    if not line.strip(): continue
                    try: obj=json.loads(line)
                    except Exception: continue
                    ident=str(obj.get('id',''))
                    if not ident or ident in seen: continue
                    seen.add(ident); out.write(json.dumps(obj,ensure_ascii=False)+'\n'); written+=1
        if written == 0 and not force:
            return {'ok':True,'status':'idle','reason':'no new deduplicated samples','plan':plan,'parts':parts}

        registry=ModelRegistry(self.root/'models/models.sqlite3')
        active=registry.active('ALI')
        stage='lora' if active else 'base'
        base=(active or {}).get('hf_dir') or (active or {}).get('checkpoint') or ''
        val=Path(validation_path) if validation_path else self.root/'data/training/bootstrap/chat_validation.jsonl'
        if not val.exists(): val=self.root/'data/training/curriculum/chat_validation.jsonl'
        emit('training candidate', .2, stage=stage, samples=written, base_checkpoint=base)
        cfg=PipelineConfig(
            stage=stage, scale=scale, train_path=str(merged.resolve()),
            validation_path=str(val.resolve()) if val.exists() else '', base_checkpoint=str(Path(base).resolve()) if base else '',
            max_steps=max(1,int(steps)), epochs=1, max_seq_len=192, batch_size=1, grad_accum=1,
            learning_rate=1e-4 if stage=='lora' else 3e-4, device=device, lora_rank=8, lora_alpha=16.0,
            lora_dropout=.05, curriculum=True, world_size=1, distributed_backend='none',
        )
        try:
            result=TrainingPipeline(self.root).run(cfg, progress=lambda ev: emit(f"{ev.get('stage')} · {ev.get('status')}", .25 if ev.get('status')!='progress' else .55, event=ev))
            candidate_version=result['run_id'] if stage!='lora' else result['run_id']+'-merged'
            emit('candidate ready', .72, version=candidate_version)
            rows=registry.list('ALI'); candidate=next((r for r in rows if r.get('version')==candidate_version),None)
            if not candidate:
                raise RuntimeError(f'candidate registry row not found: {candidate_version}')
            regressions=ImprovementLoop(self.root).run_tests()
            ce=json.loads(candidate.get('eval_json') or '{}')
            baseline=registry.active('ALI')
            be=json.loads(baseline.get('eval_json') or '{}') if baseline and baseline.get('version') != candidate_version else None
            gate=promotion_gate(ce,be,regressions)
            promoted=False
            if gate.get('promote'):
                registry.promote('ALI',candidate_version)
                promoted=True
            cl.record_training(self.root/db,result['checkpoint'],result.get('evaluation') or {},self.root/conversation_db if conversation_db else None)
            self.mark_trained(self.root/db,self.root/conversation_db if conversation_db else None,last_status='promoted' if promoted else 'candidate_rejected',last_candidate=candidate_version,last_error='')
            emit('learning cycle complete',1.0,promoted=promoted,gate=gate)
            return {'ok':True,'status':'promoted' if promoted else 'candidate_rejected','plan':plan,'incremental_samples':written,'dataset':str(merged),'training':result,'candidate':candidate,'regressions':regressions,'gate':gate}
        except Exception as exc:
            # A failed run must remain retryable: never advance the trained-data cursor on failure.
            st=self._state()
            st.update({'last_run':time.time(),'last_status':'failed','last_error':str(exc)})
            self.state_path.write_text(json.dumps(st,ensure_ascii=False,indent=2),encoding='utf-8')
            emit('learning cycle failed',1.0,error=str(exc))
            raise
