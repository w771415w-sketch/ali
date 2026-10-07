# -*- coding: utf-8 -*-
"""ALI AI 2.5 reusable professional shell reference; business logic stays in ali_ai.py."""
from __future__ import annotations
import tkinter as tk
from tkinter import ttk
from dataclasses import dataclass
from typing import Callable, Optional
from config.app_config import PALETTE

@dataclass
class ShellCallbacks:
    new_chat:Callable[[],None]=lambda:None; open_project:Callable[[],None]=lambda:None; open_models:Callable[[],None]=lambda:None; open_jobs:Callable[[],None]=lambda:None; send:Callable[[str],None]=lambda _text:None; stop:Callable[[],None]=lambda:None

class ALIProfessionalShell:
    """Presentation-only reference shell used by downstream UI experiments."""
    def __init__(self,root:tk.Tk,callbacks:Optional[ShellCallbacks]=None):
        self.root=root; self.cb=callbacks or ShellCallbacks(); self._build()
    def _build(self):
        self.root.title('ALI AI'); self.root.geometry('1480x920'); self.root.minsize(1120,720); self.root.configure(bg=PALETTE['BG'])
        tk.Label(self.root,text='ALI AI',bg=PALETTE['BG'],fg=PALETTE['INK'],font=('Segoe UI Semibold',15)).pack(anchor='w',padx=18,pady=12)
        body=tk.Frame(self.root,bg=PALETTE['BG']); body.pack(fill='both',expand=True)
        rail=tk.Frame(body,width=205,bg=PALETTE['RAIL']); rail.pack(fill='y',side='left'); rail.pack_propagate(False)
        for label,fn in (('＋ New chat',self.cb.new_chat),('Projects',self.cb.open_project),('Models',self.cb.open_models),('Jobs',self.cb.open_jobs)):
            tk.Button(rail,text=label,command=fn,bg=PALETTE['RAIL'],fg=PALETTE['INK'],relief='flat').pack(fill='x',padx=8,pady=4)
        center=tk.Frame(body,bg=PALETTE['BG']); center.pack(fill='both',expand=True,side='left')
        self.chat=tk.Text(center,bg=PALETTE['BG'],fg=PALETTE['INK'],relief='flat',wrap='word',font=('Segoe UI',10)); self.chat.pack(fill='both',expand=True,padx=18,pady=18)
        composer=tk.Frame(center,bg=PALETTE['BG']); composer.pack(fill='x',padx=18,pady=12)
        self.input=tk.Text(composer,height=4,bg=PALETTE['SOFT'],fg=PALETTE['INK'],relief='flat'); self.input.pack(fill='x',side='left',expand=True)
        tk.Button(composer,text='إرسال',command=self._send,bg=PALETTE['INK'],fg=PALETTE['BG'],relief='flat').pack(side='left',padx=8)
        tk.Button(composer,text='إيقاف',command=self.cb.stop,bg=PALETTE['RAIL'],fg=PALETTE['RED'],relief='flat').pack(side='left')
        right=tk.Frame(body,width=310,bg=PALETTE['SOFT']); right.pack(fill='y',side='right'); right.pack_propagate(False)
        tk.Label(right,text='Execution / Health',bg=PALETTE['SOFT'],fg=PALETTE['INK'],font=('Segoe UI Semibold',11)).pack(anchor='w',padx=14,pady=14)
        self.status=tk.Label(right,text='Ready',bg=PALETTE['SOFT'],fg=PALETTE['MUTED']); self.status.pack(anchor='w',padx=14)
    def _send(self):
        value=self.input.get('1.0','end').strip();
        if value: self.input.delete('1.0','end'); self.chat.insert('end',f'\nUSER\n{value}\n'); self.cb.send(value)
