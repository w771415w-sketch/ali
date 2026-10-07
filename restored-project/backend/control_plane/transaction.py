from __future__ import annotations
class Transaction:
    def __init__(self,agent):self.agent=agent;self.ops=[];self.prepared=False;self.result=None
    def add(self,operation):self.ops.append(dict(operation));return self
    def prepare(self):
        self.result=self.agent.plan_changes(self.ops);self.prepared=True;return self.result
    def commit(self,approved=False):
        if not self.prepared:self.prepare()
        if not approved:return {"ok":False,"status":"approval_required","plan":self.result}
        return self.agent.apply_changes(self.ops,approved=True)
    def rollback(self,archive):
        return {"ok":bool(self.agent.workspace.restore(archive)),"status":"restored","archive":archive}
