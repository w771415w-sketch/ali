# -*- coding: utf-8 -*-
"""فلتر الأوامر الخطيرة.

القواعد دفاعية وليست sandbox: أي أمر مطلوب للحماية يُرفض بشكل صريح،
مع تغطية أوسع لـ Windows + Unix + سلاسل تشغيل أوامر/سكربتات غير آمنة.
"""

from __future__ import annotations

import re
from typing import List, Tuple


# (regex pattern, reason)
# الترتيب غير مهم — أي تطابق = رفض.
_BLACKLIST: List[Tuple[re.Pattern, str]] = [
    # Unix / Linux destructive operations
    (re.compile(r"\brm\s+-[-a-z]*r[-a-z]*f\s+(?:--\s*)?(?:/|~)(?:\s|$)", re.I),
                                                     "recursive root/home delete"),
    (re.compile(r"\bdd\s+if=.*\s+of=/dev/(?:sd[a-z]+|nvme\d+n\d+|hd[a-z]+)", re.I),
                                                     "dd overwrite disk"),
    (re.compile(r"\b(?:mkfs|fdisk|parted)\b", re.I), "partition tool"),
    (re.compile(r":\(\)\s*\{\s*:\s*\|\s*:\s*&\s*\}\s*;\s*:", re.I),
                                                     "fork bomb"),

    # Windows destructive / persistence operations
    (re.compile(r"\bformat\s+[a-zA-Z]:", re.I), "format drive"),
    (re.compile(r"\b(?:del|erase)\s+/[sq].*[a-zA-Z]:\\", re.I),
                                                     "recursive drive delete"),
    (re.compile(r"\b(?:rd|rmdir)\s+/[sq].*[a-zA-Z]:\\", re.I),
                                                     "recursive directory delete"),
    (re.compile(r"\bdiskpart\b", re.I), "diskpart"),
    (re.compile(r"\bbcdedit\b", re.I), "bcdedit"),
    (re.compile(r"\bregedit\b", re.I), "regedit"),
    (re.compile(r"\breg\s+(?:delete|import)\b", re.I), "reg destructive"),
    (re.compile(r"\bnetsh\s+(?:advfirewall|firewall)\s+delete\b", re.I),
                                                     "netsh delete"),
    (re.compile(r"\bcipher\s+/w\b", re.I), "cipher wipe"),
    (re.compile(r"\b(?:shutdown|logoff)\b", re.I), "session shutdown"),
    (re.compile(r"\bwevtutil\s+cl\b", re.I), "event log clear"),
    (re.compile(r"\bschtasks\s+/delete\b", re.I), "scheduled task delete"),

    # Script / binary execution patterns commonly used to bypass intent boundaries
    (re.compile(r"\bpowershell(?:\.exe)?\b.*(?:-encodedcommand|-enc\b)", re.I),
                                                     "encoded PowerShell"),
    (re.compile(r"\b(?:powershell|pwsh)(?:\.exe)?\b.*\binvoke-expression\b", re.I),
                                                     "PowerShell Invoke-Expression"),
    (re.compile(r"\b(?:powershell|pwsh)(?:\.exe)?\b.*\bstart-process\b", re.I),
                                                     "PowerShell Start-Process"),
    (re.compile(r"\b(?:powershell|pwsh)(?:\.exe)?\b.*\bremove-item\b.*-recurse\b", re.I),
                                                     "PowerShell recursive delete"),
    (re.compile(r"\b(?:mshta|rundll32|regsvr32|wscript|cscript)(?:\.exe)?\b", re.I),
                                                     "script host / binary launcher"),

    # Download-and-execute / pipe-to-shell patterns
    (re.compile(r"\b(?:curl|wget)\b.*\|\s*(?:bash|sh|zsh|fish|pwsh|powershell)\b", re.I),
                                                     "download pipe shell"),
    (re.compile(r"\b(?:iwr|irm|invoke-webrequest|invoke-restmethod)\b.*\|.*\b(?:iex|invoke-expression)\b", re.I),
                                                     "PowerShell download execute"),

    # Explicit shell nesting / command interpreter jumps
    (re.compile(r"\b(?:cmd|command)\.exe\s+/c\s+.*\b(?:powershell|pwsh)\b", re.I),
                                                     "nested PowerShell"),
]

def is_command_safe(cmd: str) -> bool:
    """يرجع True إذا كان الأمر غير مطابق لأي نمط خطير معروف."""
    if not isinstance(cmd, str) or not cmd.strip():
        return False
    normalized = cmd.replace("\u00a0", " ").strip()
    for pat, _reason in _BLACKLIST:
        if pat.search(normalized):
            return False
    return True


__all__ = ["is_command_safe"]
