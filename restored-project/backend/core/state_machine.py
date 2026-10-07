# -*- coding: utf-8 -*-
"""Explicit Agent/Project state machine for resumable work."""
from __future__ import annotations
from dataclasses import dataclass,field
from enum import Enum
from typing import Any
class Stage(str,Enum): DISCOVER="discover"; CLARIFY="clarify"; PLAN="plan"; EXECUTE="execute"; VERIFY="verify"; RECOVER="recover"; COMPLETE="complete"; CANCELLED="cancelled"
@dataclass
class AgentState:
    active_goal:str|None=None; active_domain:str|None=None; stage:str=Stage.DISCOVER.value
    subgoals:list[str]=field(default_factory=list); known_requirements:list[str]=field(default_factory=list)
    missing_requirements:list[str]=field(default_factory=list); constraints:list[str]=field(default_factory=list)
    decisions:list[dict[str,Any]]=field(default_factory=list); pending_confirmation:str|None=None
    pending_tool_action:str|None=None; last_verified_result:str|None=None; unresolved_risks:list[str]=field(default_factory=list)
    checkpoints:list[dict[str,Any]]=field(default_factory=list)
    def checkpoint(self,label,result=None): self.checkpoints.append({"label":label,"result":result,"stage":self.stage,"index":len(self.checkpoints)})
    def mark_complete(self,result): self.stage=Stage.COMPLETE.value; self.last_verified_result=str(result)
    def cancel(self): self.stage=Stage.CANCELLED.value; self.pending_confirmation=None; self.pending_tool_action=None
