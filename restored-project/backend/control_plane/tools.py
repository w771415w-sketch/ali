from __future__ import annotations
from dataclasses import dataclass,field
from typing import Callable,Any
import time,inspect
@dataclass
class ToolSpec:
    name:str; version:str; description:str; handler:Callable[[dict[str,Any]],Any]
    permissions:set[str]=field(default_factory=set); reversible:bool=True; timeout_s:float=30.0; risk:str="low"
class ToolRegistry:
    def __init__(self):self.tools={}
    def register(self,spec):
        if spec.name in self.tools and self.tools[spec.name].version!=spec.version:raise ValueError("tool version conflict")
        self.tools[spec.name]=spec
    def discover(self,query): 
        q=query.casefold().split(); return [s for s in self.tools.values() if all(any(x in (s.name+" "+s.description).casefold() for x in q) for _ in [0])]
    def get(self,name):return self.tools.get(name)
    def call(self,name,args,granted=None,timeout_s=None):
        spec=self.get(name)
        if not spec:return {"ok":False,"error":"tool_not_found"}
        granted=granted or set(); missing=spec.permissions-granted
        if missing:return {"ok":False,"error":"permission_denied","missing":sorted(missing)}
        started=time.monotonic()
        try:
            if inspect.iscoroutinefunction(spec.handler):return {"ok":False,"error":"async_handler_requires_async_runner"}
            out=spec.handler(args)
            elapsed=time.monotonic()-started
            limit=float(timeout_s or spec.timeout_s)
            if elapsed>limit:return {"ok":False,"error":"timeout","elapsed_s":elapsed}
            return {"ok":True,"tool":name,"version":spec.version,"result":out,"elapsed_s":elapsed,"risk":spec.risk,"reversible":spec.reversible}
        except Exception as exc:return {"ok":False,"tool":name,"error":str(exc),"elapsed_s":time.monotonic()-started}