from __future__ import annotations
import hashlib,json,time
from pathlib import Path
from .agent_loop import AgentLoop
from .training_bridge import TrainingBridge
from .hardware_bridge import HardwareBridge
from .project_agent import ProjectAgent
from .requirements import extract_contract,clarification_questions
from .planner import Planner
from .reliability import Budget,RateLimiter,CircuitBreaker,IdempotencyLedger,RetryPolicy
from .lineage import LineageRegistry
from .knowledge_graph import KnowledgeGraph
from .release import ReleaseManager
from .provenance import ProvenanceTracker
from .scheduler import PriorityScheduler
from .cache import TTLCache
from .capabilities import CapabilityInspector
from .observability import Metrics,EventLog\nfrom config.settings_service import ProjectSettingsService\nfrom conversation_intelligence.language_adapter import ArabicLanguageAdapter\nfrom diagnostics.engine import DiagnosticsEngine
class ProfessionalRuntime:
    def __init__(self,root,hardware=None,max_workers=1):
        self.root=Path(root);self.root.mkdir(parents=True,exist_ok=True);self.loop=AgentLoop(self.root/"agent",hardware_policy=hardware or {});self.agent=ProjectAgent(self.root/"project",self.loop.store);self.planner=Planner()
        self.rate=RateLimiter(30,60);self.idempotency=IdempotencyLedger(self.root/"runtime.db");self.retry=RetryPolicy();self.breakers={};self.lineage=LineageRegistry(self.root/"registry");self.graph=KnowledgeGraph(self.root/"knowledge_graph.json");self.release=ReleaseManager(self.root/"registry");self.provenance=ProvenanceTracker(self.root/"provenance.json");self.scheduler=PriorityScheduler(max_workers);self.cache=TTLCache();self.capabilities=CapabilityInspector();self.metrics=Metrics();self.events=EventLog(self.root/"runtime-events.jsonl");self.hardware=hardware or {}
        self.training=TrainingBridge(self.root/"training-jobs.json");self.hardware_bridge=HardwareBridge();self.settings=ProjectSettingsService();self.language=ArabicLanguageAdapter(profile=self.settings.language.current_id());self.diagnostics=DiagnosticsEngine()
    def prepare(self,text,project_id=None):
        prev=None
        if project_id:
            row=self.loop.store.get_project(project_id)
            if row and row["data"].get("contract"):from .schemas import ProjectContract;prev=ProjectContract.from_dict(row["data"]["contract"])
        c=extract_contract(text,prev);pid=project_id or self.loop._new_project(c);tasks=self.planner.build(c) if c.complete else []
        return {"project_id":pid,"contract":c.to_dict(),"questions":clarification_questions(c),"tasks":[t.to_dict() for t in tasks]}
    def execute(self,text,project_id=None,operations=None,checks=None,approved=False,dry_run=False,idempotency_key=None):
        payload={"project_id":project_id,"text":text,"operations":operations or [],"checks":checks or [],"approved":approved,"dry_run":dry_run}; key=idempotency_key or hashlib.sha256(json.dumps(payload,ensure_ascii=False,sort_keys=True).encode()).hexdigest()
        if not self.rate.allow(key):return {"ok":False,"status":"rate_limited"}
        old=self.idempotency.get(key)
        if old and old["status"]=="complete":return {"ok":True,"status":"idempotent_replay","result":old["result"]}
        if not self.idempotency.claim(key):return {"ok":False,"status":"already_running"}
        try:
            p=self.prepare(text,project_id);c=p["contract"]
            if c["conflicts"]:out={"ok":False,"status":"clarify","project_id":p["project_id"],"conflicts":c["conflicts"]}
            elif c["missing"]:out={"ok":False,"status":"clarify","project_id":p["project_id"],"questions":p["questions"]}
            elif dry_run:out={"ok":True,"status":"dry_run","project_id":p["project_id"],"contract":c,"tasks":p["tasks"],"operations":operations or []}
            elif operations and not approved:out={"ok":False,"status":"approval_required","project_id":p["project_id"],"planned_operations":self.agent.plan_changes(operations)}
            elif not operations:out={"ok":False,"status":"awaiting_operations","project_id":p["project_id"],"message":"No concrete operations supplied; planning is complete but execution is not claimed."}
            else:
                applied=self.agent.apply_changes(operations,approved=True)
                if not applied["ok"]:out={"ok":False,"status":"rolled_back","project_id":p["project_id"],"details":applied}
                else:
                    check={"passed":True,"results":[]}
                    if checks:check=self.agent.run_checks(checks,approved=True)
                    passed=bool(check["passed"])
                    out={"ok":passed,"status":"verified" if passed else "verification_failed","project_id":p["project_id"],"contract":c,"changes":applied,"checks":check}
                    if passed:
                        backup=applied.get("backup")
                        if backup:out["lineage"]=self.lineage.register("artifact",p["project_id"],"snapshot",{"path":backup,"verified":True})
            self.idempotency.complete(key,out);return out
        except Exception as exc:
            self.idempotency.fail(key,str(exc));self.events.emit("runtime_failure",{"error":str(exc)});return {"ok":False,"status":"failed","error":str(exc)}
    def training_preflight(self,scale="small",steps=0):
        snap=self.hardware_bridge.snapshot()
        if not snap["admission"]["allowed"]:return {"ok":False,"status":"training_blocked","hardware":snap}
        return {**self.training.plan(snap["hardware"],scale,steps),"hardware":snap}
    def create_training_job(self,name,scale="small",steps=0):
        pre=self.training_preflight(scale,steps)
        if not pre["ok"]:return pre
        return {"ok":True,"status":"queued","job":self.training.create_job(name),"preflight":pre}
    def settings_snapshot(self,model_metadata=None):
        return self.settings.snapshot(self.hardware_bridge.snapshot()["hardware"],model_metadata)
    def save_language_profile(self,profile_id):
        saved=self.settings.save_language(profile_id);self.language=ArabicLanguageAdapter(profile=profile_id);return saved
    def save_training_selection(self,method_id,conversion_id,model_metadata=None):
        return self.settings.save_training(self.hardware_bridge.snapshot()["hardware"],method_id,conversion_id,model_metadata)
    def adapt_language(self,text,preferred_profile=None):return self.language.adapt(text,preferred_profile)
    def diagnose_file(self,path):return self.diagnostics.inspect_file(path)
    def diagnose_archive(self,path):return self.diagnostics.inspect_archive(path)
    def diagnose_project(self,path):return self.diagnostics.diagnose_project(path)
    def impact(self,changed_files):return self.agent.changes.analyze(self.agent.workspace.root,changed_files)
    def health(self):return {"capabilities":self.capabilities.inspect(),"hardware":self.hardware,"pending_jobs":self.scheduler.pending(),"training_jobs":self.training.snapshot(),"metrics":self.metrics.snapshot()}
    def close(self):self.loop.store.close();self.idempotency.close()
