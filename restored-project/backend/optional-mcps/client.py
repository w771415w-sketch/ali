# -*- coding: utf-8 -*-
"""Minimal optional MCP stdio client.

It implements JSON-RPC initialization, tools/list and tools/call. It is opt-in and never starts
an untrusted server automatically; callers must supply an executable from the local allowlist.
"""
from __future__ import annotations
import json, subprocess, threading
from pathlib import Path

class MCPClient:
    def __init__(self, command:list[str], cwd:str|Path|None=None, timeout:float=20):
        if not command: raise ValueError('command required')
        self.command=[str(x) for x in command]; self.cwd=str(cwd) if cwd else None; self.timeout=timeout; self.p=None; self._id=0
    def start(self):
        if self.p: return
        self.p=subprocess.Popen(self.command,cwd=self.cwd,stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True,encoding='utf-8',bufsize=1,creationflags=getattr(subprocess,'CREATE_NO_WINDOW',0))
        self.request('initialize',{'protocolVersion':'2025-06-18','capabilities':{},'clientInfo':{'name':'ALI Studio','version':'3.0.0'}})
        self.notify('notifications/initialized',{})
    def _write(self,obj):
        assert self.p and self.p.stdin; self.p.stdin.write(json.dumps(obj,ensure_ascii=False)+'\n'); self.p.stdin.flush()
    def notify(self,method,params): self._write({'jsonrpc':'2.0','method':method,'params':params})
    def request(self,method,params):
        self._id+=1; rid=self._id; self._write({'jsonrpc':'2.0','id':rid,'method':method,'params':params})
        assert self.p and self.p.stdout
        while True:
            line=self.p.stdout.readline()
            if not line: raise RuntimeError('MCP server closed stdout')
            try: msg=json.loads(line)
            except Exception: continue
            if msg.get('id')==rid:
                if 'error' in msg: raise RuntimeError(json.dumps(msg['error'],ensure_ascii=False))
                return msg.get('result',{})
    def tools(self): self.start(); return self.request('tools/list',{}).get('tools',[])
    def call(self,name:str,arguments:dict|None=None): self.start(); return self.request('tools/call',{'name':name,'arguments':arguments or {}})
    def close(self):
        if self.p:
            try:self.p.terminate()
            except Exception:pass
            self.p=None
