# -*- coding: utf-8 -*-
"""Permission gate: read-only, default-with-approval and full-access."""
from __future__ import annotations
from dataclasses import dataclass
from enum import Enum
class PermMode(str,Enum): READ_ONLY="read-only"; DEFAULT="default"; FULL_ACCESS="full-access"
RANK={PermMode.READ_ONLY.value:0,PermMode.DEFAULT.value:1,PermMode.FULL_ACCESS.value:2}
@dataclass(frozen=True)
class Decision:
    allowed:bool; needs_ask:bool=False; reason:str=""
    @classmethod
    def allow(cls,reason="allowed"): return cls(True,False,reason)
    @classmethod
    def ask(cls,reason): return cls(False,True,reason)
    @classmethod
    def deny(cls,reason): return cls(False,False,reason)
class PermissionManager:
    def __init__(self,mode="default"):
        self._always_allow=set(); self.mode=mode if mode in RANK else PermMode.DEFAULT.value
    def set_mode(self,mode):
        if mode not in RANK: raise ValueError(f"invalid permission mode: {mode}")
        self.mode=mode
    def grant(self,tool_name,session=True): self._always_allow.add(tool_name)
    def revoke(self,tool_name): self._always_allow.discard(tool_name)
    def check(self,tool_name,permission,ctx=None,kwargs=None,user=None):
        p=permission.value if hasattr(permission,"value") else str(permission); mode=getattr(ctx,"perm_mode",None) or self.mode
        if p not in RANK: return Decision.deny(f"invalid tool permission: {p}")
        if mode not in RANK: return Decision.deny(f"invalid permission mode: {mode}")
        if mode==PermMode.READ_ONLY.value and RANK[p]>RANK[mode]: return Decision.deny(f"read-only mode forbids '{tool_name}'")
        if tool_name in self._always_allow and mode==PermMode.FULL_ACCESS.value: return Decision.allow("always_allow")
        if mode==PermMode.FULL_ACCESS.value: return Decision.allow("full-access")
        if p==PermMode.READ_ONLY.value: return Decision.allow("mode permits")
        return Decision.ask(f"tool '{tool_name}' requires '{p}' in '{mode}' mode")
