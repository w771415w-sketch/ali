# -*- coding: utf-8 -*-
"""حماية المسارات — Workspace Containment.

`safe_project_path(project_dir, rel)` يحل المسار النسبي إلى Path مطلق.
يرفع PermissionError إذا:
- rel فارغ أو خارج project_dir (محاولة escape).
- rel يلامس مسارات حساسة معروفة (SystemRoot, ProgramFiles, .ssh, .aws,
  APPDATA, إلخ).

هذه الطبقة هي خط الدفاع الأول قبل أي ملف I/O.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path
from typing import Iterable


# مسارات Windows الحساسة التي لا يُسمح للـ Agent بلمسها مطلقاً.
_WINDOWS_SENSITIVE = (
    r"C:\Windows",
    r"C:\Windows\System32",
    r"C:\Program Files",
    r"C:\Program Files (x86)",
    r"C:\ProgramData",
)

# مكونات أسماء يجب رفضها أينما ظهرت.
_SENSITIVE_NAME_PARTS = (
    ".ssh", ".aws", ".gnupg", "credentials", ".env", "id_rsa",
)

# ملفات حساسة بأسماء محددة (case-insensitive).
_SENSITIVE_FILES = (
    ".env", ".envrc", "credentials", "credentials.json",
    "id_rsa", "id_ed25519",
)


def _is_windows_sensitive(p: Path) -> bool:
    s = str(p).replace("/", "\\")
    for prefix in _WINDOWS_SENSITIVE:
        if s.startswith(prefix):
            return True
    return False


def _has_sensitive_component(p: Path) -> bool:
    parts_lower = {part.lower() for part in p.parts}
    for part in _SENSITIVE_NAME_PARTS:
        if part in parts_lower:
            return True
    name = p.name.lower()
    if name in _SENSITIVE_FILES:
        return True
    return False


def safe_project_path(project_dir: str | os.PathLike,
                      rel: str) -> Path:
    """حلّ rel داخل project_dir.

    - rel=""  → project_dir نفسه.
    - rel="sub/file.py" → project_dir/sub/file.py.
    - محاولات escape (rel يبدأ بـ ../) → PermissionError.
    - لمس path حساس (system/.ssh/.aws/.env) → PermissionError.
    """
    base = Path(project_dir).resolve()
    if not base.exists():
        raise PermissionError("project_dir does not exist: " + str(base))

    if not rel:
        rel = "."

    # حلّ المسار بشكل صريح لرفض escape.
    # نقبل rel المطلق فقط إذا كان داخل base.
    if os.path.isabs(rel):
        candidate = Path(rel).resolve()
    else:
        candidate = (base / rel).resolve()

    # يجب أن يكون داخل base (أو هو نفسه).
    try:
        candidate.relative_to(base)
    except ValueError:
        raise PermissionError(
            f"path escapes workspace: {rel} -> {candidate}"
        )

    # رفض المسارات الحساسة.
    if _is_windows_sensitive(candidate):
        raise PermissionError(
            f"access denied (sensitive windows path): {candidate}"
        )
    if _has_sensitive_component(candidate):
        raise PermissionError(
            f"access denied (sensitive file/path component): {candidate}"
        )

    return candidate


__all__ = ["safe_project_path"]
