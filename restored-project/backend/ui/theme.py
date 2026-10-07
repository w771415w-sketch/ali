# -*- coding: utf-8 -*-
"""ALI AI 2.5 light Windows theme matching the supplied UI reference."""
from __future__ import annotations
from config.app_config import PALETTE


def configure(root) -> None:
    from tkinter import ttk
    style = ttk.Style(root)
    try:
        style.theme_use("clam")
    except Exception:
        pass
    c = PALETTE
    style.configure(".", background=c["BG"], foreground=c["INK"], font=("Segoe UI", 9))
    style.configure("TFrame", background=c["BG"])
    style.configure("Panel.TFrame", background=c["BG"])
    style.configure("Rail.TFrame", background=c["RAIL"])
    style.configure("Card.TFrame", background=c["PANEL_2"])
    style.configure("TLabel", background=c["BG"], foreground=c["INK"])
    style.configure("Rail.TLabel", background=c["RAIL"], foreground=c["INK"])
    style.configure("Muted.TLabel", background=c["BG"], foreground=c["MUTED"])
    style.configure("Title.TLabel", background=c["BG"], foreground=c["INK"], font=("Segoe UI Semibold", 15))
    style.configure("Section.TLabel", background=c["BG"], foreground=c["MUTED"], font=("Segoe UI Semibold", 8))
    style.configure("Badge.TLabel", background=c["SOFT"], foreground=c["BLUE"], padding=(8, 4))
    style.configure("Accent.TButton", background=c["BLUE"], foreground=c["WHITE"], padding=(12, 7), borderwidth=0)
    style.map("Accent.TButton", background=[("active", c["BLUE"])], foreground=[("disabled", c["MUTED"])])
    style.configure("Ghost.TButton", background=c["SOFT"], foreground=c["INK"], padding=(9, 6), borderwidth=0)
    style.map("Ghost.TButton", background=[("active", c["RAIL_HOVER"])])
    style.configure("Danger.TButton", background=c["SOFT"], foreground=c["RED"], padding=(9, 6), borderwidth=0)
    style.configure("TNotebook", background=c["BG"], borderwidth=0, tabmargins=0)
    style.configure("TNotebook.Tab", background=c["SOFT"], foreground=c["MUTED"], padding=(10, 7), borderwidth=0)
    style.map("TNotebook.Tab", background=[("selected", c["WHITE"])], foreground=[("selected", c["INK"])])
    style.configure("Treeview", background=c["WHITE"], fieldbackground=c["WHITE"], foreground=c["INK"], rowheight=26, borderwidth=0)
    style.map("Treeview", background=[("selected", "#eef3ff")], foreground=[("selected", c["INK"])])
    style.configure("Vertical.TScrollbar", troughcolor=c["BG"], background=c["LINE"], borderwidth=0, arrowsize=10)
    style.configure("Horizontal.TScrollbar", troughcolor=c["BG"], background=c["LINE"], borderwidth=0, arrowsize=10)
    style.configure("TCombobox", fieldbackground=c["WHITE"], background=c["WHITE"], foreground=c["INK"])
    style.configure("TProgressbar", troughcolor=c["SOFT"], background=c["BLUE"], borderwidth=0)
