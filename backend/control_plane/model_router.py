from __future__ import annotations
from dataclasses import dataclass
@dataclass
class ModelEndpoint:
    name:str; role:str; healthy:bool=True; max_context:int=4096; cost_per_token:float=0.0
class ModelRouter:
    def __init__(self,endpoints=None):
        self.endpoints=endpoints or [ModelEndpoint("local-default","general",True),ModelEndpoint("local-coding","coding",True),ModelEndpoint("local-vision","vision",False)]
    def route(self,intent,domain,context_tokens=0):
        role="general"
        if domain in {"software","ai","data","git"} or intent in {"coding","debugging","project_analysis"}: role="coding"
        if intent in {"vision","image_analysis"}: role="vision"
        candidates=[e for e in self.endpoints if e.healthy and e.role==role and context_tokens<=e.max_context]
        if not candidates: candidates=[e for e in self.endpoints if e.healthy and e.role=="general" and context_tokens<=e.max_context]
        if not candidates:return {"ok":False,"reason":"no_healthy_model"}
        pick=min(candidates,key=lambda e:e.cost_per_token); return {"ok":True,"model":pick.name,"role":pick.role,"context_limit":pick.max_context}
