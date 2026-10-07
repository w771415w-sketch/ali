# -*- coding: utf-8 -*-
"""Structured audit records with credential redaction."""
from __future__ import annotations
from datetime import datetime,timezone
import json,re
from pathlib import Path
SENSITIVE=re.compile(r"(?:password|passwd|secret|token|api[_-]?key|authorization|cookie|private[_-]?key)",re.I)
BEARER=re.compile(r"(?i)(bearer\s+)[A-Za-z0-9._~+/=-]+")
FLAG=re.compile(r"(?i)(--?(?:password|token|api[-_]?key|secret)=)\S+")
def redact_value(key,value):
    if SENSITIVE.search(str(key)): return "[REDACTED]"
    if isinstance(value,str): return FLAG.sub(r"\1[REDACTED]",BEARER.sub(r"\1[REDACTED]",value))
    return value
def redact(mapping): return {k:redact_value(k,v) for k,v in dict(mapping or {}).items()}
class AuditLog:
    def __init__(self,path): self.path=Path(path); self.path.parent.mkdir(parents=True,exist_ok=True)
    def write(self,event):
        record={"timestamp":datetime.now(timezone.utc).isoformat(),**dict(event or {})}
        if "kwargs" in record: record["kwargs"]=redact(record["kwargs"])
        with self.path.open("a",encoding="utf-8") as f: f.write(json.dumps(record,ensure_ascii=False)+"\n")
