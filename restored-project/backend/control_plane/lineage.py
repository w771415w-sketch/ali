from __future__ import annotations
import hashlib,json
from .registry import Registry
class LineageRegistry:
    def __init__(self,root): self.registry=Registry(root)
    def register(self,kind,name,version,metadata=None,parents=None,active=False):
        md=dict(metadata or {}); md["parents"]=list(parents or []); md["lineage_hash"]=hashlib.sha256(json.dumps(md,sort_keys=True,ensure_ascii=False).encode()).hexdigest()
        return self.registry.put(kind,name,version,md,active)
    def get(self,kind,name,version=None): return self.registry.get(kind,name,version)
    def promote(self,kind,name,version,quality,approved=False):
        if not approved:return {"ok":False,"status":"approval_required"}
        if not bool((quality or {}).get("passed")):return {"ok":False,"status":"quality_gate_failed"}
        return {"ok":self.registry.activate(kind,name,version),"status":"promoted"}