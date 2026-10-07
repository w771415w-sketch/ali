# -*- coding: utf-8 -*-
"""Small persistent background job manager used by the desktop UI and scripts."""
from __future__ import annotations
from dataclasses import dataclass, asdict
from pathlib import Path
import json, threading, time, traceback, uuid
from typing import Any, Callable, Dict, Optional

@dataclass
class Job:
    id: str
    name: str
    kind: str = "task"
    status: str = "queued"
    progress: float = 0.0
    message: str = ""
    created_at: float = 0.0
    started_at: float = 0.0
    finished_at: float = 0.0
    result: Any = None
    error: str = ""

class JobManager:
    def __init__(self, state_file: str | Path):
        self.path = Path(state_file)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._jobs: Dict[str, Job] = {}
        self._lock = threading.RLock()
        self._load()

    def _load(self):
        if not self.path.exists(): return
        try:
            raw = json.loads(self.path.read_text(encoding="utf-8"))
            for item in raw[-100:]:
                j = Job(**{k:item.get(k) for k in Job.__dataclass_fields__})
                self._jobs[j.id] = j
        except Exception:
            pass

    def _persist(self):
        with self._lock:
            data = [asdict(j) for j in list(self._jobs.values())[-100:]]
            self.path.write_text(json.dumps(data, ensure_ascii=False, indent=2, default=str), encoding="utf-8")

    def create(self, name: str, kind: str = "task") -> Job:
        j = Job(str(uuid.uuid4()), name, kind, "queued", 0.0, "queued", time.time())
        with self._lock: self._jobs[j.id] = j
        self._persist(); return j

    def update(self, job_id: str, **fields) -> Job:
        with self._lock:
            j = self._jobs[job_id]
            for k,v in fields.items():
                if hasattr(j,k): setattr(j,k,v)
        self._persist(); return j

    def snapshot(self):
        with self._lock: return [asdict(j) for j in list(self._jobs.values())[-100:]]

    def run(self, name: str, fn: Callable[[Callable[..., None]], Any], kind: str = "task") -> Job:
        job = self.create(name, kind)
        def progress(message: str = "", value: Optional[float] = None, **extra):
            fields = {"message": message, **extra}
            if value is not None: fields["progress"] = max(0.0, min(1.0, float(value)))
            self.update(job.id, **fields)
        def worker():
            self.update(job.id, status="running", started_at=time.time(), message="started")
            try:
                result = fn(progress)
                self.update(job.id, status="completed", progress=1.0, finished_at=time.time(), result=result, message="completed")
            except Exception as exc:
                err = "".join(traceback.format_exception(type(exc), exc, exc.__traceback__))[-12000:]
                self.update(job.id, status="failed", finished_at=time.time(), error=err, message=str(exc))
        threading.Thread(target=worker, name=f"ALI-{kind}-{job.id[:8]}", daemon=True).start()
        return job

    def get(self, job_id: str) -> Optional[Job]:
        with self._lock: return self._jobs.get(job_id)
