# -*- coding: utf-8 -*-
"""UI direction controller for Arabic RTL and English LTR."""
from __future__ import annotations
import tkinter as tk
from config.i18n import is_rtl, normalize_language


def direction_for(root_or_language) -> bool:
    if isinstance(root_or_language, str):
        return is_rtl(root_or_language)
    return bool(getattr(root_or_language, "_ali_rtl", False))


def start_side(root_or_language) -> str:
    return "right" if direction_for(root_or_language) else "left"


def end_side(root_or_language) -> str:
    return "left" if direction_for(root_or_language) else "right"


def anchor_start(root_or_language) -> str:
    return "e" if direction_for(root_or_language) else "w"


def justify(root_or_language) -> str:
    return "right" if direction_for(root_or_language) else "left"


def apply_text_widget(widget, root_or_language=None):
    target = root_or_language if root_or_language is not None else widget.winfo_toplevel()
    rtl = direction_for(target)
    try:
        widget.configure(justify="right" if rtl else "left")
    except tk.TclError:
        pass
    return widget


def configure_root(root: tk.Tk, language: str) -> None:
    lang = normalize_language(language)
    root._ali_language = lang
    root._ali_rtl = is_rtl(lang)
    root.option_add("*Entry.justify", "right" if root._ali_rtl else "left")
