from __future__ import annotations
from pathlib import Path
from training.scaling import build_training_plan
from training.job_manager import JobManager

class TrainingBridge:
    """Connect training requests to the existing hardware-aware P50 policy and persistent JobManager."""
    def __init__(self, state_path):
        self.jobs=JobManager(Path(state_path),max_concurrent=1)
    def plan(self,hardware,scale="small",steps=0):
        plan=build_training_plan(hardware,requested_scale=scale,steps=steps)
        return {"ok":True,"plan":plan,"admission_required":True}
    def create_job(self,name):
        return self.jobs.create(name)
    def update(self,job_id,**fields):
        return self.jobs.update(job_id,**fields)
    def snapshot(self):
        return self.jobs.snapshot()
