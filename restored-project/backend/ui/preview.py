# -*- coding: utf-8 -*-
"""Project preview panel with safe HTML/text rendering and optional browser handoff."""
from __future__ import annotations
from pathlib import Path
import html, webbrowser
import tkinter as tk

class PreviewPanel:
    def __init__(self,parent,colors):
        self.parent=parent; self.colors=colors; self.path=None
        self.frame=tk.Frame(parent,bg=colors['editor'])
        bar=tk.Frame(self.frame,bg=colors['panel']); bar.pack(fill='x')
        self.path_var=tk.StringVar(); tk.Entry(bar,textvariable=self.path_var,bg=colors['panel2'],fg=colors['text'],insertbackground=colors['text'],relief='flat').pack(side='left',fill='x',expand=True,padx=6,pady=6)
        tk.Label(bar,text='Preview',bg=colors['panel'],fg=colors['muted']).pack(side='left',padx=8)
        self.view=tk.Text(self.frame,wrap='word',bg=colors['editor'],fg=colors['text'],insertbackground=colors['text'],font=('Segoe UI',9),relief='flat')
        self.view.pack(fill='both',expand=True,padx=6,pady=6)
    def show(self,path:str|Path):
        p=Path(path); self.path=p; self.path_var.set(str(p)); self.view.delete('1.0','end')
        if not p.exists() or not p.is_file(): self.view.insert('1.0','Preview target not found.'); return
        ext=p.suffix.lower()
        if ext in {'.png','.jpg','.jpeg','.gif','.webp','.bmp'}:
            try:
                from PIL import Image,ImageTk
                im=Image.open(p); im.thumbnail((650,520)); self._photo=ImageTk.PhotoImage(im); self.view.image_create('end',image=self._photo); return
            except Exception as e:self.view.insert('1.0',f'Image preview unavailable: {e}'); return
        try:text=p.read_text(encoding='utf-8',errors='replace')
        except Exception as e:text=f'Cannot preview: {e}'
        if ext in {'.html','.htm'}:
            from html.parser import HTMLParser
            class P(HTMLParser):
                def __init__(self):super().__init__();self.out=[]
                def handle_data(self,data):
                    x=' '.join(data.split());
                    if x:self.out.append(x)
            parser=P(); parser.feed(text); text='\n\n'.join(parser.out) or '(empty HTML)'
        self.view.insert('1.0',text[:500_000])
    def open_browser(self):
        if self.path and self.path.exists():webbrowser.open(self.path.as_uri())
