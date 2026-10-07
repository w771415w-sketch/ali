from __future__ import annotations
from dataclasses import dataclass
import time

@dataclass
class AgentMessage:
    task_id:str; sender:str; recipient:str; status:str; output:object=None; evidence:list=None; error:str|None=None; dependencies:list[str]|None=None

class AgentRegistry:
    ROLES={"manager","researcher","developer","tester","reviewer","documenter"}
    def __init__(self): self.handlers={}
    def register(self,role,handler):
        if role not in self.ROLES: raise ValueError("unsupported agent role")
        self.handlers[role]=handler
    def has(self,role): return role in self.handlers

class SupervisedMultiAgent:
    def __init__(self,registry=None,max_handoffs=12): self.registry=registry or AgentRegistry(); self.max_handoffs=max_handoffs
    def run(self,task_id,steps,timeout_s=30):
        start=time.time(); seen=set(); messages=[]
        for role,input_data in steps:
            if time.time()-start>timeout_s: return {"ok":False,"status":"timeout","messages":[m.__dict__ for m in messages]}
            key=(role,str(input_data))
            if key in seen: return {"ok":False,"status":"loop_detected","messages":[m.__dict__ for m in messages]}
            seen.add(key)
            handler=self.registry.handlers.get(role)
            if not handler:
                messages.append(AgentMessage(task_id,role,"manager","escalated",error="handler not registered")); continue
            try:
                out=handler(input_data); messages.append(AgentMessage(task_id,role,"manager","done",output=out,evidence=[]))
            except Exception as e:
                messages.append(AgentMessage(task_id,role,"manager","failed",error=str(e)))
                return {"ok":False,"status":"failed","messages":[m.__dict__ for m in messages]}
            if len(messages)>=self.max_handoffs:return {"ok":False,"status":"handoff_limit","messages":[m.__dict__ for m in messages]}
        return {"ok":True,"status":"complete","messages":[m.__dict__ for m in messages]}
