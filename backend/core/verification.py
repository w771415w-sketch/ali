# -*- coding: utf-8 -*-
"""Postcondition verification primitives; execution is never self-certified."""
from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
from typing import Callable,Any
@dataclass(frozen=True)
class Verification:
    passed:bool; name:str; evidence:str; reason:str=""
def file_exists(path,label="file exists"):
    p=Path(path); ok=p.exists(); return Verification(ok,label,str(p),"missing" if not ok else "")
def predicate(name,fn,evidence=""):
    try:
        value=bool(fn()); return Verification(value,name,evidence or str(value),"" if value else "predicate returned false")
    except Exception as exc: return Verification(False,name,evidence,str(exc))
def all_pass(checks): return all(c.passed for c in checks)
