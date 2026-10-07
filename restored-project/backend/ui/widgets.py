# -*- coding: utf-8 -*-
"""Reusable ALI AI widgets with live Arabic RTL / English LTR behavior."""
from __future__ import annotations
import tkinter as tk
from config.app_config import PALETTE
from config.i18n import tr
from ui.rtl import direction_for, start_side, end_side, anchor_start, justify


class ScrollableFrame(tk.Frame):
    def __init__(self, parent, *, bg=None, **kwargs):
        c = PALETTE
        super().__init__(parent, bg=bg or c["BG"], **kwargs)
        rtl = direction_for(parent.winfo_toplevel())
        self.canvas = tk.Canvas(self, bg=bg or c["BG"], highlightthickness=0, bd=0)
        self.scrollbar = tk.Scrollbar(self, orient="vertical", command=self.canvas.yview, bd=0, highlightthickness=0)
        self.body = tk.Frame(self.canvas, bg=bg or c["BG"])
        self.window_id = self.canvas.create_window((1 if rtl else 0, 0), window=self.body, anchor="ne" if rtl else "nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        self.canvas.pack(side=end_side(parent.winfo_toplevel()), fill="both", expand=True)
        self.scrollbar.pack(side=start_side(parent.winfo_toplevel()), fill="y")
        self.body.bind("<Configure>", self._update_scroll)
        self.canvas.bind("<Configure>", self._resize_window)
        self.canvas.bind_all("<MouseWheel>", self._wheel, add="+")

    def _update_scroll(self, _=None):
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def _resize_window(self, event):
        self.canvas.itemconfigure(self.window_id, width=event.width)

    def _wheel(self, event):
        try:
            self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
        except Exception:
            pass


class ChatBubble(tk.Frame):
    """Readable ChatGPT-like bubble for the Tk fallback UI.

    The bubble supports streamed text plus safe execution summaries and web source
    cards without exposing hidden reasoning or raw event JSON.
    """
    def __init__(self, parent, role: str, text: str, *, meta: str = "", on_copy=None):
        c = PALETTE
        super().__init__(parent, bg=c["BG"])
        root = self.winfo_toplevel()
        rtl = direction_for(root)
        self.role = role
        self.on_copy = on_copy
        self._raw_text = str(text)
        self._card_bg = "#eef3ff" if role == "user" else c["WHITE"]
        self._accent = c["BLUE"] if role == "user" else c["GREEN"]
        is_user = role == "user"
        name = (
            "أنت" if role == "user" and rtl
            else "You" if role == "user"
            else "ALI" if role == "assistant"
            else role.upper()
        )
        shell = tk.Frame(
            self, bg=self._card_bg,
            highlightbackground=c["LINE"], highlightthickness=1,
        )
        shell.pack(
            anchor="e" if is_user else "w",
            fill="x", padx=(70 if is_user else 10, 10), pady=5,
        )
        self.shell = shell

        head = tk.Frame(shell, bg=self._card_bg)
        head.pack(fill="x", padx=12, pady=(9, 3))
        self.name_label = tk.Label(
            head, text=name, bg=self._card_bg, fg=self._accent,
            font=("Segoe UI Semibold", 8),
        )
        self.name_label.pack(side=start_side(root))
        self.meta_label = tk.Label(
            head, text=meta, bg=self._card_bg, fg=c["MUTED"],
            font=("Segoe UI", 7),
        )
        self.meta_label.pack(side=end_side(root))

        self.text = tk.Text(
            shell, bg=self._card_bg, fg=c["INK"], relief="flat", bd=0,
            wrap="word", font=("Segoe UI", 10),
            height=max(1, min(24, max(1, self._raw_text.count("\n") + 2))),
            padx=12, pady=2,
        )
        self.text.tag_configure("__ali_direction", justify=justify(root))
        self.text.tag_configure("__ali_heading", font=("Segoe UI Semibold", 11), spacing1=6, spacing3=3)
        self.text.tag_configure("__ali_code", font=("Consolas", 9), background="#f4f6f8", lmargin1=10, lmargin2=10)
        self.text.tag_configure("__ali_quote", foreground=c["MUTED"], lmargin1=14)
        self._render_text(self._raw_text)
        self.text.configure(state="disabled")
        self.text.pack(fill="x", padx=1, pady=(0, 4))

        self.trace_frame = tk.Frame(shell, bg=self._card_bg)
        self.trace_label = tk.Label(
            self.trace_frame, text="", bg=self._card_bg, fg=c["MUTED"],
            justify=justify(root), anchor=anchor_start(root),
            font=("Segoe UI", 8), wraplength=820,
        )
        self.trace_label.pack(fill="x", padx=12, pady=(0, 4))

        self.sources_frame = tk.Frame(shell, bg=self._card_bg)

        if on_copy:
            btn = tk.Button(
                shell, text=tr("copy", getattr(root, "_ali_language", "ar")),
                command=lambda: on_copy(self._raw_text), bg=self._card_bg,
                fg=c["MUTED"], activebackground=c["LINE"],
                activeforeground=c["INK"], relief="flat", bd=0,
                font=("Segoe UI", 8), cursor="hand2",
            )
            btn.pack(anchor=anchor_start(root), padx=9, pady=(2, 7))

    def _render_text(self, value: str):
        self.text.delete("1.0", "end")
        lines = str(value).splitlines()
        in_code = False
        for i, line in enumerate(lines):
            suffix = "\n" if i < len(lines) - 1 else ""
            stripped = line.strip()
            if stripped.startswith("```"):
                in_code = not in_code
                continue
            tag = "__ali_direction"
            if in_code:
                tag = "__ali_code"
            elif stripped.startswith(("# ", "## ", "### ")):
                tag = "__ali_heading"
            elif stripped.startswith(">"):
                tag = "__ali_quote"
            self.text.insert("end", line + suffix, (tag,))
        if not lines and not value:
            self.text.insert("1.0", "", "__ali_direction")
        self.text.configure(height=max(1, min(24, str(value).count("\n") + 2)))

    def set_text(self, value: str):
        self._raw_text = str(value)
        self.text.configure(state="normal")
        self._render_text(self._raw_text)
        self.text.configure(state="disabled")

    def set_meta(self, value: str):
        self.meta_label.configure(text=str(value))

    def set_trace(self, lines: list[str] | None):
        clean = [str(x).strip() for x in (lines or []) if str(x).strip()]
        if not clean:
            self.trace_frame.pack_forget()
            return
        self.trace_label.configure(text="\n".join(f"• {x}" for x in clean[-6:]))
        if not self.trace_frame.winfo_ismapped():
            self.trace_frame.pack(fill="x", before=self.sources_frame, padx=1, pady=(0, 1))

    def add_web_sources(self, documents: list[dict] | None):
        c = PALETTE
        root = self.winfo_toplevel()
        docs = [d for d in (documents or []) if d.get("url")]
        for child in self.sources_frame.winfo_children():
            child.destroy()
        if not docs:
            self.sources_frame.pack_forget()
            return
        title = tk.Label(
            self.sources_frame, text=f"مصادر الإنترنت · {len(docs)}",
            bg=self._card_bg, fg=c["BLUE"], font=("Segoe UI Semibold", 8),
        )
        title.pack(anchor=anchor_start(root), padx=12, pady=(2, 3))
        import webbrowser
        for idx, doc in enumerate(docs[:5], 1):
            title_text = str(doc.get("title") or doc.get("source") or doc.get("url") or f"Source {idx}").strip()
            snippet = " ".join(str(doc.get("snippet") or "").split())[:180]
            row = tk.Frame(self.sources_frame, bg=self._card_bg)
            row.pack(fill="x", padx=10, pady=2)
            btn = tk.Button(
                row, text=f"W{idx} · {title_text[:80]}",
                command=lambda u=str(doc.get("url")): webbrowser.open(u),
                bg=self._card_bg, fg=c["BLUE"], activebackground=c["LINE"],
                relief="flat", bd=0, cursor="hand2", anchor=anchor_start(root),
                font=("Segoe UI Semibold", 8),
            )
            btn.pack(fill="x")
            if snippet:
                tk.Label(
                    row, text=snippet, bg=self._card_bg, fg=c["MUTED"],
                    font=("Segoe UI", 7), wraplength=820,
                    justify=justify(root), anchor=anchor_start(root),
                ).pack(fill="x", padx=4, pady=(0, 2))
        self.sources_frame.pack(fill="x", before=self.trace_frame if self.trace_frame.winfo_ismapped() else None, padx=1, pady=(0, 5))


class ChatView(ScrollableFrame):
    def __init__(self, parent):
        super().__init__(parent, bg=PALETTE["BG"])
        self.bubbles: list[ChatBubble] = []

    def clear(self):
        for item in self.bubbles:
            item.destroy()
        self.bubbles.clear()

    def add_message(self, role: str, text: str, *, meta: str = "", on_copy=None) -> ChatBubble:
        bubble = ChatBubble(self.body, role, text, meta=meta, on_copy=on_copy)
        bubble.pack(fill="x")
        self.bubbles.append(bubble)
        self.after_idle(lambda: self.canvas.yview_moveto(1.0))
        return bubble


class LineNumberedEditor(tk.Frame):
    def __init__(self, parent):
        c = PALETTE
        root = parent.winfo_toplevel()
        rtl = direction_for(root)
        super().__init__(parent, bg=c["EDITOR"])
        self.lines = tk.Text(self, width=5, bg=c["SOFT"], fg=c["MUTED"], relief="flat", state="disabled", takefocus=0, font=("Consolas", 9), padx=7, pady=7)
        self.text = tk.Text(self, bg=c["EDITOR"], fg=c["INK"], insertbackground=c["INK"], selectbackground="#eaf0ff", relief="flat", bd=0, wrap="none", font=("Consolas", 9), undo=True, padx=8, pady=7)
        self.text.tag_configure("__ali_direction", justify="right" if rtl else "left")
        self.scroll = tk.Scrollbar(self, command=self._yview, bd=0, highlightthickness=0)
        self.text.configure(yscrollcommand=self._yscroll)
        if rtl:
            self.scroll.pack(side="left", fill="y")
            self.text.pack(side="left", fill="both", expand=True)
            self.lines.pack(side="right", fill="y")
        else:
            self.lines.pack(side="left", fill="y")
            self.text.pack(side="left", fill="both", expand=True)
            self.scroll.pack(side="right", fill="y")
        self.text.bind("<KeyRelease>", lambda _e: self.refresh_lines(), add="+")
        self.text.bind("<MouseWheel>", lambda _e: self.after_idle(self.refresh_lines), add="+")
        self.refresh_lines()

    def _yview(self, *args):
        self.text.yview(*args)
        self.lines.yview_moveto(self.text.yview()[0])
    def _yscroll(self, first, last):
        self.scroll.set(first, last); self.lines.yview_moveto(first)
    def refresh_lines(self):
        count = int(self.text.index("end-1c").split(".")[0])
        self.lines.configure(state="normal"); self.lines.delete("1.0", "end"); self.lines.insert("1.0", "\n".join(str(i) for i in range(1, count + 1))); self.lines.configure(state="disabled")
    def get(self) -> str: return self.text.get("1.0", "end-1c")
    def set(self, value: str): self.text.delete("1.0", "end"); self.text.insert("1.0", value, "__ali_direction"); self.refresh_lines()
    def clear(self): self.set("")

__all__ = ["ScrollableFrame", "ChatBubble", "ChatView", "LineNumberedEditor"]
