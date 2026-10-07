from __future__ import annotations
from dataclasses import dataclass,asdict
from pathlib import Path
import subprocess,sys,time
from .schemas import ProjectContract,new_id
from .requirements import extract_contract,clarification_questions
from .planner import Planner
from .store import StateStore
from .memory import MemoryManager
from .knowledge import KnowledgeBase
from .recovery import FailureManager,CheckpointManager
from .model_router import ModelRouter
from .observability import Metrics,EventLog
from .policy import Policy
@dataclass
class ExecutionResult:
    ok:bool;status:str;project_id:str;stage:str;message:str;evidence:list;contract:dict;metrics:dict
    def to_dict(self):return asdict(self)
class AgentLoop:
    def __init__(self,root,hardware_policy=None,model=None):
        self.root=Path(root);self.root.mkdir(parents=True,exist_ok=True);self.store=StateStore(self.root/"state.db");self.memory=MemoryManager(self.store);self.kb=KnowledgeBase(self.root/"knowledge");self.failure=FailureManager(self.store);self.checkpoints=CheckpointManager(self.root/"checkpoints");self.planner=Planner();self.router=ModelRouter();self.metrics=Metrics();self.events=EventLog(self.root/"events.jsonl");self.hardware_policy=hardware_policy or {};self.model=model;self.policy=Policy(self.root)
    def _new_project(self,contract):
        pid=new_id("project");self.store.put_project(pid,1,contract.goal,"discover",{"contract":contract.to_dict(),"tasks":[],"decisions":[],"acceptance":[],"artifacts":[]});self.memory.add(pid,"task","Goal: "+contract.goal,1.0);return pid
    def prepare(self,user_text,project_id=None):
        prev=None
        if project_id:
            row=self.store.get_project(project_id)
            if row and row["data"].get("contract"):prev=ProjectContract.from_dict(row["data"]["contract"])
        c=extract_contract(user_text,prev);pid=project_id or self._new_project(c);self.events.emit("requirements_extracted",{"project_id":pid,"missing":c.missing,"conflicts":c.conflicts});return pid,c
    def execute(self,user_text,project_id=None,dry_run=False,approved=False,command=None):
        pid,c=self.prepare(user_text,project_id);self.metrics.inc("requests")
        if c.conflicts:return ExecutionResult(False,"clarify",pid,"clarify","conflicting requirements",[],c.to_dict(),self.metrics.snapshot())
        if not c.complete:return ExecutionResult(False,"clarify",pid,"clarify","missing requirements: "+"; ".join(clarification_questions(c)),[],c.to_dict(),self.metrics.snapshot())
        route=self.router.route("project","software")
        if not route.get("ok"):return ExecutionResult(False,"blocked",pid,"clarify","no healthy model route",[route],c.to_dict(),self.metrics.snapshot())
        tasks=self.planner.build(c)
        if dry_run:return ExecutionResult(True,"dry_run",pid,"plan","plan_ready",[t.to_dict() for t in tasks],c.to_dict(),self.metrics.snapshot())
        if command:
            if not approved:return ExecutionResult(False,"approval_required",pid,"clarify","command requires explicit approval",[],c.to_dict(),self.metrics.snapshot())
            if not self.policy.command_allowed(command):return ExecutionResult(False,"blocked",pid,"clarify","command blocked by safety policy",[],c.to_dict(),self.metrics.snapshot())
            try:
                r=subprocess.run(command,shell=True,cwd=str(self.root),capture_output=True,text=True,timeout=60)
                passed=r.returncode==0
                return ExecutionResult(passed,"verified" if passed else "failed",pid,"complete" if passed else "recover","command executed and exit code verified" if passed else "command failed",[{"kind":"command","returncode":r.returncode,"stdout":r.stdout,"stderr":r.stderr,"verified":passed}],c.to_dict(),self.metrics.snapshot())
            except subprocess.TimeoutExpired:
                return ExecutionResult(False,"timeout",pid,"recover","command timeout",[],c.to_dict(),self.metrics.snapshot())
        self.checkpoints.save("plan",{"project_id":pid,"contract":c.to_dict(),"tasks":[t.to_dict() for t in tasks],"stage":"execute"})
        return ExecutionResult(False,"awaiting_operations",pid,"plan","planning completed; no concrete operation was supplied",[{"kind":"plan","task_count":len(tasks),"verified":True}],c.to_dict(),self.metrics.snapshot())
