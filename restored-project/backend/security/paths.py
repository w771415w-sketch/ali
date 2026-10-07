# -*- coding: utf-8 -*-
"""Workspace containment and sensitive-path policy."""
from __future__ import annotations
from pathlib import Path
import os
SENSITIVE_NAMES={".env",".envrc","credentials","credentials.json","id_rsa","id_ed25519"}
SENSITIVE_PARTS={".ssh",".aws",".gnupg"}
def safe_project_path(project_dir,rel):
    base=Path(project_dir).resolve()
    if not base.exists(): raise PermissionError(f"project_dir does not exist: {base}")
    candidate=(Path(rel).resolve() if os.path.isabs(str(rel)) else (base/str(rel or ".")).resolve())
    try: candidate.relative_to(base)
    except ValueError: raise PermissionError(f"path escapes workspace: {rel}")
    parts={p.lower() for p in candidate.parts}
    if candidate.name.lower() in SENSITIVE_NAMES or parts & SENSITIVE_PARTS: raise PermissionError(f"sensitive path denied: {candidate}")
    if os.name=="nt":
        s=str(candidate).replace("/","\\").lower()
        if s.startswith(r"c:\windows") or s.startswith(r"c:\program files") or s.startswith(r"c:\programdata"):
            raise PermissionError(f"system path denied: {candidate}")
    return candidate
