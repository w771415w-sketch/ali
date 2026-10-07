# -*- coding: utf-8 -*-
"""ALI AI 2.5 — single source of truth for identity, UI palette and user-facing modes."""
from __future__ import annotations

APP = "ALI AI"
VERSION = "4.4.0"
CODENAME = "Professional Assistant · P50"
LEGACY_APP = "ALI Studio"

# Visual baseline derived from the supplied ali_agent_ui.py reference.
# Do not silently replace these with a dark theme in the production build.
PALETTE = {
    "BG": "#ffffff",
    "RAIL": "#f4f4f6",
    "RAIL_HOVER": "#e9e9ed",
    "LINE": "#e3e3e8",
    "INK": "#1a1a1f",
    "MUTED": "#8a8a94",
    "SOFT": "#f7f7f9",
    "PANEL": "#ffffff",
    "PANEL_2": "#f7f7f9",
    "ACCENT": "#1a1a1f",
    "BLUE": "#3b6ef5",
    "GREEN": "#1a7f45",
    "RED": "#c0392b",
    "AMBER": "#9a6700",
    "EDITOR": "#fbfbfc",
    "WHITE": "#ffffff",
}

PERM_MODES = [
    ("read-only", "Read only", "قراءة فقط"),
    ("default", "Ask before sensitive actions", "يسأل قبل التعديل والأوامر الحساسة"),
    ("full-access", "Full access", "تنفيذ مباشر للأدوات المسموح بها"),
]

AI_MODES = ["auto", "professional", "agent", "chat", "tools", "research"]
MODELS = ["Auto", "ALI-local", "ALI-candidate", "ALI-GGUF"]
EFFORTS = ["AUTO", "LOW", "MEDIUM", "HIGH", "ULTRA"]

SENSITIVE = {
    "write_file": "تعديل / إنشاء ملف",
    "run_command": "تشغيل أمر على الجهاز",
    "git_commit": "إنشاء commit",
    "delete": "حذف عنصر",
    "install": "تثبيت مكوّن",
}

__all__ = [
    "APP", "VERSION", "CODENAME", "LEGACY_APP", "PALETTE", "PERM_MODES",
    "AI_MODES", "MODELS", "EFFORTS", "SENSITIVE",
]
