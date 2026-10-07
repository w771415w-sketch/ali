# -*- coding: utf-8 -*-
"""Compact live execution telemetry panel for ALI AI desktop."""
from __future__ import annotations
import tkinter as tk
from tkinter import ttk
from collections import deque
from config.app_config import PALETTE

class ActivityCenter:
    def __init__(self,parent,rtl=False):
        self.parent=parent; self.rtl=rtl; self.events=deque(maxlen=160); self.current={}; self.context={}; self._last_job_signature=None
        self._build()
    def _build(self):
        p=PALETTE; self.frame=tk.Frame(self.parent,bg=p['WHITE'],highlightbackground=p['LINE'],highlightthickness=1); self.frame.pack(fill='both',expand=True)
        head=tk.Frame(self.frame,bg=p['WHITE']); head.pack(fill='x',padx=8,pady=(7,4))
        tk.Label(head,text='النشاط والتنفيذ' if self.rtl else 'Execution Monitor',bg=p['WHITE'],fg=p['INK'],font=('Segoe UI Semibold',10)).pack(side='left')
        self.state=tk.Label(head,text='جاهز' if self.rtl else 'Ready',bg=p['SOFT'],fg=p['GREEN'],font=('Segoe UI Semibold',8),padx=8,pady=3); self.state.pack(side='right')
        self.progress=ttk.Progressbar(self.frame,mode='determinate',maximum=100,length=100); self.progress.pack(fill='x',padx=10,pady=(0,6))
        cards=tk.Frame(self.frame,bg=p['WHITE']); cards.pack(fill='x',padx=8,pady=(0,5))
        self.task=self._mini(cards,'المهمة' if self.rtl else 'TASK'); self.phase=self._mini(cards,'المرحلة' if self.rtl else 'PHASE'); self.detail=self._mini(cards,'التفاصيل' if self.rtl else 'DETAIL')
        wrap=tk.Frame(self.frame,bg=p['EDITOR']); wrap.pack(fill='both',expand=True,padx=8,pady=6)
        self.log=tk.Text(wrap,bg=p['EDITOR'],fg=p['INK'],insertbackground=p['INK'],relief='flat',font=('Consolas',7),wrap='word',height=7); self.log.pack(side='left',fill='both',expand=True)
        sb=ttk.Scrollbar(wrap,orient='vertical',command=self.log.yview); sb.pack(side='right',fill='y'); self.log.configure(yscrollcommand=sb.set)
    def _mini(self,parent,title):
        p=PALETTE; f=tk.Frame(parent,bg=p['SOFT'],highlightbackground=p['LINE'],highlightthickness=1); f.pack(side='left',fill='x',expand=True,padx=2); tk.Label(f,text=title,bg=p['SOFT'],fg=p['MUTED'],font=('Segoe UI',7)).pack(anchor='w',padx=6,pady=(4,0)); v=tk.Label(f,text='—',bg=p['SOFT'],fg=p['INK'],font=('Segoe UI Semibold',8),anchor='w'); v.pack(fill='x',padx=6,pady=(0,4)); return v
    def event(self,message,phase='',progress=None,status=None):
        self.events.append(message)
        self.log.configure(state='normal'); self.log.insert('end',message.rstrip()+'\n'); self.log.see('end'); self.log.configure(state='disabled')
        if phase: self.phase.configure(text=phase[:60])
        if progress is not None:
            try:self.progress['value']=max(0,min(100,float(progress)*100))
            except Exception:pass
        if status: self.state.configure(text=str(status)[:28],fg=PALETTE['GREEN'] if status in {'running','completed','Ready','جاهز'} else PALETTE['RED'])
    def update_job(self,job):
        if not job: return
        pct=float(job.get('progress',0))*100; name=str(job.get('name','—')); message=str(job.get('message',''))
        self.task.configure(text=name[:42]); self.detail.configure(text=message[:50] or '—')
        signature=(str(job.get('id','')),str(job.get('status','')),round(float(job.get('progress',0)),3),message)
        if signature != self._last_job_signature:
            self._last_job_signature=signature
            self.event(f"[{job.get('status','?')}] {name} · {pct:.1f}% · {message}",phase=job.get('kind','task'),progress=job.get('progress',0),status=job.get('status',''))
        else:
            try: self.progress['value']=max(0,min(100,pct))
            except Exception: pass
    def set_context(self,**values):
        self.context.update(values)
    def clear(self): self._last_job_signature=None; self.log.configure(state='normal'); self.log.delete('1.0','end'); self.log.configure(state='disabled'); self.events.clear(); self.progress['value']=0; self.state.configure(text='جاهز' if self.rtl else 'Ready',fg=PALETTE['GREEN'])
