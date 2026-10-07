from __future__ import annotations
from dataclasses import dataclass
from urllib.parse import urlparse
import re
@dataclass(frozen=True)
class Principal:
    subject:str; roles:frozenset[str]; tenant:str="local"
class RBAC:
    ROLE_PERMISSIONS={"viewer":frozenset({"read"}),"developer":frozenset({"read","write","execute"}),"operator":frozenset({"read","write","execute","deploy"}),"admin":frozenset({"read","write","execute","deploy","manage"})}
    def allowed(self,principal,permission): return any(permission in self.ROLE_PERMISSIONS.get(r,frozenset()) for r in principal.roles)
class NetworkPolicy:
    def __init__(self,allowlist=()): self.allowlist={str(x).casefold().strip(".") for x in allowlist}
    def allowed(self,url):
        host=(urlparse(url).hostname or "").casefold().strip(".")
        return bool(host and host in self.allowlist)
class TenantScope:
    def path(self,root,tenant):
        if not re.fullmatch(r"[A-Za-z0-9._-]{1,64}",str(tenant)): raise ValueError("invalid tenant id")
        from pathlib import Path
        base=Path(root).resolve(); p=(base/tenant).resolve(); p.relative_to(base); p.mkdir(parents=True,exist_ok=True); return p
