from __future__ import annotations
from pathlib import Path
import json,sys,tempfile
try:
    from .runtime_facade import ProfessionalRuntime
    from .knowledge_graph import KnowledgeGraph
    from .release import QualityGate
    from .security_ext import RBAC,Principal,NetworkPolicy
except ImportError:
    sys.path.insert(0,str(Path(__file__).parents[1]))
    from control_plane.runtime_facade import ProfessionalRuntime
    from control_plane.knowledge_graph import KnowledgeGraph
    from control_plane.release import QualityGate
    from control_plane.security_ext import RBAC,Principal,NetworkPolicy

def run():
    with tempfile.TemporaryDirectory(prefix="ali-professional-") as td:
        root=Path(td);rt=ProfessionalRuntime(root)
        prep=rt.prepare("أريد برنامج مخزن على ويندوز Python فيه مخزون ومبيعات")
        dry=rt.execute("أريد برنامج مخزن على ويندوز Python فيه مخزون ومبيعات",project_id=prep["project_id"],dry_run=True)
        gate=rt.execute("أريد برنامج مخزن على ويندوز Python فيه مخزون ومبيعات",project_id=prep["project_id"],operations=[{"path":"main.py","content":"print('ALI_OK')\n"}],approved=False)
        real=rt.execute("أريد برنامج مخزن على ويندوز Python فيه مخزون ومبيعات",project_id=prep["project_id"],operations=[{"path":"main.py","content":"print('ALI_OK')
"}],checks=[f"{sys.executable} main.py"],approved=True,idempotency_key="confirmed")
        replay=rt.execute("أريد برنامج مخزن على ويندوز Python فيه مخزون ومبيعات",project_id=prep["project_id"],operations=[{"path":"main.py","content":"print('ALI_OK')
"}],checks=[f"{sys.executable} main.py"],approved=True,idempotency_key="confirmed")
        kg=KnowledgeGraph(root/"kg.json");kg.upsert_entity("project","Project",{"version":"1"},source="user");kg.upsert_entity("backend","Backend",{"version":"2"},source="system");kg.relate("project","contains","backend",source="user")
        out={"prepared":bool(prep["tasks"]),"dry_run":dry["ok"],"approval_gate":gate["status"]=="approval_required","real_execution":real["ok"],"idempotent_replay":replay["status"]=="idempotent_replay","kg_relation":len(kg.neighbors("project"))==1,"quality_gate":QualityGate().check({"coding":.9,"arabic":.9,"tool_use":.9,"safety":.99,"regression":1.0})["passed"],"rbac":RBAC().allowed(Principal("u",frozenset({"developer"})),"write"),"network_allowlist":NetworkPolicy(["example.com"]).allowed("https://example.com/api")}
        rt.close();out["checks_passed"]=all(out.values());return out
if __name__=="__main__":
    result=run();print(json.dumps(result,ensure_ascii=False,indent=2));raise SystemExit(0 if result["checks_passed"] else 1)
