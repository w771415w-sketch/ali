# -*- coding: utf-8 -*-
"""Evidence-driven project agent helpers: inspect, snapshot, test and verify."""
from __future__ import annotations
from pathlib import Path
import hashlib, json, subprocess, time
from typing import Any
from core.workflow import ChangeWorkflow,Phase
SKIP={'.git','.venv','__pycache__','node_modules','dist','build'}
class ProjectOrchestrator:
    def __init__(self,root:str|Path):self.root=Path(root).resolve()
    def inventory(self,max_files:int=4000)->dict[str,Any]:
        rows=[]
        for p in self.root.rglob('*'):
            if p.is_file() and not any(x in p.parts for x in SKIP):
                try: rows.append({'path':str(p.relative_to(self.root)),'size':p.stat().st_size})
                except OSError: continue
                if len(rows)>=max_files: break
        return {'root':str(self.root),'files':rows,'count':len(rows)}
    def fingerprint(self)->str:
        h=hashlib.sha256()
        for row in sorted(self.inventory()['files'],key=lambda x:x['path']):
            h.update(row['path'].encode()); h.update(str(row['size']).encode()); p=self.root/row['path']
            try: h.update(hashlib.sha256(p.read_bytes()).digest() if row['size']<=2_000_000 else str(p.stat().st_mtime_ns).encode())
            except OSError: pass
        return h.hexdigest()
    def snapshot(self,dst:str|Path)->Path:
        dst=Path(dst); dst.mkdir(parents=True,exist_ok=True)
        (dst/'manifest.json').write_text(json.dumps({'fingerprint':self.fingerprint(),'created_at':time.time()},indent=2),encoding='utf-8'); return dst
    def run_tests(self,timeout:int=900)->dict[str,Any]:
        try:p=subprocess.run(['python','-m','pytest','tests','-q'],cwd=self.root,capture_output=True,text=True,timeout=timeout)
        except Exception as e:return {'passed':False,'returncode':-1,'stdout':'','stderr':str(e)}
        return {'passed':p.returncode==0,'returncode':p.returncode,'stdout':p.stdout[-10000:],'stderr':p.stderr[-10000:]}
    def verify_paths(self,expected:list[str])->dict[str,Any]:
        missing=[x for x in expected if not (self.root/x).exists()]; return {'verified':not missing,'missing':missing}
    def workflow(self,task:str,approved:bool=False)->dict[str,Any]:
        wf=ChangeWorkflow(task); wf.transition(Phase.PLAN,notes='plan created'); wf.transition(Phase.SNAPSHOT,notes='fingerprint='+self.fingerprint()); wf.state.approved=approved; return wf.state.to_dict()
