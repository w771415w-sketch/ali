from __future__ import annotations
from dataclasses import dataclass,field
from typing import Any,Protocol
@dataclass
class AssistantRequest: text:str; conversation_id:str; project_id:str|None=None; effort:str='AUTO'; attachments:list[dict[str,Any]]=field(default_factory=list)
@dataclass
class AssistantPlan: intent:str; steps:list[str]; model:str; effort:str; needs_web:bool=False; needs_tools:bool=False; needs_rag:bool=False
@dataclass
class AssistantResult: ok:bool; text:str; plan:AssistantPlan; sources:list[dict[str,Any]]=field(default_factory=list); tools:list[dict[str,Any]]=field(default_factory=list); verification:dict[str,Any]=field(default_factory=dict); duration_ms:int=0
class Router(Protocol):
    def plan(self,request:AssistantRequest,context:dict[str,Any])->AssistantPlan: ...
class AssistantOrchestrator:
    def __init__(self,*,router:Router,context_manager:Any,executor:Any,verifier:Any,memory:Any,audit:Any): self.router=router; self.context_manager=context_manager; self.executor=executor; self.verifier=verifier; self.memory=memory; self.audit=audit
    def handle(self,request:AssistantRequest)->AssistantResult:
        import time; start=time.perf_counter(); context=self.context_manager.build(request); plan=self.router.plan(request,context); execution=self.executor.run(plan,request,context); verification=self.verifier.verify(execution,plan,request); text=self.executor.compose_response(execution,verification,request); self.audit.record(request,plan,execution,verification);
        if verification.get('ok'): self.memory.consider(request,text,verification)
        return AssistantResult(bool(verification.get('ok')),text,plan,execution.get('sources',[]),execution.get('tools',[]),verification,int((time.perf_counter()-start)*1000))
