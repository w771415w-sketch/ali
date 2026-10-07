# -*- coding: utf-8 -*-
"""Safe, checkpointed agent execution spine."""
from __future__ import annotations
from dataclasses import dataclass
from typing import Callable,Any
from core.state_machine import AgentState,Stage
@dataclass
class Action:
    name:str; run:Callable[[],Any]; verify:Callable[[Any],Any]; requires_confirmation:bool=False; reversible:bool=True
class AgentExecutor:
    def __init__(self,state,permission_gate=None,resource_gate=None): self.state=state; self.permission_gate=permission_gate; self.resource_gate=resource_gate
    def execute(self,action,confirmed=False):
        if self.resource_gate is not None:
            admission=self.resource_gate()
            if not admission.get("allowed",False):
                self.state.stage=Stage.CLARIFY.value; return {"ok":False,"status":"blocked","reasons":admission.get("reasons",[])}
        if action.requires_confirmation and not confirmed:
            self.state.pending_confirmation=action.name; self.state.pending_tool_action=action.name; return {"ok":False,"status":"confirmation_required"}
        self.state.stage=Stage.EXECUTE.value
        try: result=action.run()
        except Exception as exc:
            self.state.stage=Stage.RECOVER.value; self.state.checkpoint(f"failed:{action.name}",str(exc))
            return {"ok":False,"status":"failed","error":str(exc)}
        self.state.stage=Stage.VERIFY.value; check=action.verify(result)
        self.state.checkpoint(action.name,{"result":result,"verification":getattr(check,"__dict__",str(check))})
        if not check.passed:
            self.state.stage=Stage.RECOVER.value; return {"ok":False,"status":"verification_failed","verification":check.__dict__}
        self.state.pending_confirmation=None; self.state.pending_tool_action=None; self.state.last_verified_result=str(check.evidence)
        return {"ok":True,"status":"verified","result":result,"verification":check.__dict__}
