from __future__ import annotations
from .project_io import Workspace
from .command_runner import CommandRunner
from .acceptance import AcceptanceRunner, AcceptanceCheck
from .vcs import GitRepo
from .change import ChangeAnalyzer
from .artifacts import ArtifactRegistry
from .governance import DataGovernance
from .policy import Policy
class ProjectAgent:
    """Concrete project executor. All writes are workspace-scoped and report evidence."""
    def __init__(self,workspace,state_store):
        self.workspace=Workspace(workspace); self.policy=Policy(self.workspace.root); self.runner=CommandRunner(self.workspace.root,self.policy); self.acceptance=AcceptanceRunner(self.runner); self.git=GitRepo(self.workspace.root); self.changes=ChangeAnalyzer(); self.artifacts=ArtifactRegistry(state_store); self.governance=DataGovernance()
    def plan_changes(self,operations): return {"files":[str(x.get("path")) for x in operations],"count":len(operations),"risk":"medium" if operations else "low"}
    def apply_changes(self,operations,approved=False):
        if not approved:return {"ok":False,"status":"approval_required"}
        backup=self.workspace.snapshot("pre-change"); results=[]
        try:
            for op in operations:
                path=op["path"]; typ=op.get("type","write")
                if typ=="write":results.append(self.workspace.write(path,op.get("content",""),op.get("expected_sha256")))
                elif typ=="patch":results.append(self.workspace.patch(path,op["old"],op["new"],op.get("expected_count",1)))
                elif typ=="delete":results.append(self.workspace.delete(path))
                else:raise ValueError(f"unsupported operation: {typ}")
            return {"ok":True,"status":"applied","backup":backup,"changes":results}
        except Exception as e:
            self.workspace.restore(backup); return {"ok":False,"status":"rolled_back","backup":backup,"error":str(e)}
    def run_checks(self,commands,approved=True): return self.acceptance.run([AcceptanceCheck(f"check_{i}",cmd,cmd) for i,cmd in enumerate(commands)],approved=approved)
    def git_checkpoint(self,message,approved=False): return self.git.checkpoint_commit(message,approved=approved)
    def git_rollback(self,commit,approved=False): return self.git.rollback(commit,approved=approved)
