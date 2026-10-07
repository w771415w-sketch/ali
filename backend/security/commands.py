# -*- coding: utf-8 -*-
"""Defensive command screening. This is not a sandbox replacement."""
from __future__ import annotations
import re
_BLACKLIST=[
 (r"\brm\s+-[-a-z]*r[-a-z]*f\s+(?:--\s*)?(?:/|~)(?:\s|$)","recursive root/home delete"),
 (r"\bdd\s+if=.*\s+of=/dev/(?:sd[a-z]+|nvme\d+n\d+|hd[a-z]+)","disk overwrite"),
 (r"\b(?:mkfs|fdisk|parted)\b","partition tool"),
 (r":\(\)\s*\{\s*:\s*\|\s*:\s*&\s*\}\s*;\s*:","fork bomb"),
 (r"\bformat\s+[a-z]:","format drive"),
 (r"\b(?:del|erase|rd|rmdir)\s+/[sq].*[a-z]:\\","recursive drive delete"),
 (r"\bdiskpart\b","diskpart"),(r"\bbcdedit\b","bcdedit"),(r"\bregedit\b","regedit"),
 (r"\breg\s+(?:delete|import)\b","registry mutation"),(r"\b(?:shutdown|logoff)\b","session shutdown"),
 (r"\bwevtutil\s+cl\b","event log clear"),(r"\bschtasks\s+/delete\b","scheduled task delete"),
 (r"\bpowershell(?:\.exe)?\b.*(?:-encodedcommand|-enc\b)","encoded PowerShell"),
 (r"\b(?:powershell|pwsh)(?:\.exe)?\b.*\b(?:invoke-expression|iex)\b","PowerShell dynamic execution"),
 (r"\b(?:mshta|rundll32|regsvr32|wscript|cscript)(?:\.exe)?\b","script host / launcher"),
 (r"\b(?:curl|wget)\b.*\|\s*(?:bash|sh|zsh|fish|pwsh|powershell)\b","download pipe shell"),
 (r"\b(?:iwr|irm|invoke-webrequest|invoke-restmethod)\b.*\|.*\b(?:iex|invoke-expression)\b","download execute")
]
_COMPILED=[(re.compile(p,re.I),r) for p,r in _BLACKLIST]
def command_risk(command:str)->str|None:
    if not isinstance(command,str) or not command.strip(): return "empty command"
    c=command.replace("\u00a0"," ").strip()
    for rx,reason in _COMPILED:
        if rx.search(c): return reason
    return None
def is_command_safe(command:str)->bool: return command_risk(command) is None
