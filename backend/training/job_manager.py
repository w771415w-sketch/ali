# -*- coding: utf-8 -*-
from __future__ import annotations
from dataclasses import dataclass,asdict
from pathlib import Path
import json,threading,uuid
@dataclass
class Job:
    id:str; name:str; status:str="queued"; progress:float=0.0; stage:str="queued"; error:str=""; checkpoint:str=""
class JobManager:
    def __init__(self,path,max_concurrent=1):
        self.path=Path(path); self.path.parent.mkdir(parents=True,exist_ok=True); self.max_concurrent=max(1,int(max_concurrent)); self._lock=threading.Lock(); self._jobs=self._load()
    def _load(self):
        try: return [Job(**x) for x in json.loads(self.path.read_text(encoding="utf-8"))]
        except Exception: return []
    def _save(self): self.path.write_text(json.dumps([asdict(x) for x in self._jobs],ensure_ascii=False,indent=2),encoding="utf-8")
    def snapshot(self):
        with self._lock: return [asdict(x) for x in self._jobs]
    def create(self,name):
        with self._lock:
            active=sum(j.status in {"queued","running"} for j in self._jobs)
            status="queued" if active>=self.max_concurrent else "running"
            j=Job(uuid.uuid4().hex[:12],name,status=status,stage="preflight" if status=="running" else "queued"); self._jobs.append(j); self._save(); return asdict(j)
    def update(self,job_id,**fields):
        with self._lock:
            for j in self._jobs:
                if j.id==job_id:
                    for k,v in fields.items():
                        if hasattr(j,k): setattr(j,k,v)
                    self._save(); return asdict(j)
        raise KeyError(job_id)
