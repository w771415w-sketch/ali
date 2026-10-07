# -*- coding: utf-8 -*-
"""Local llama-server bridge with adaptive GPU offload and streaming-safe calls."""
from __future__ import annotations
from pathlib import Path
import json, subprocess, time, urllib.request, urllib.error, socket, os

class LlamaServer:
    def __init__(self, executable: str|Path, model: str|Path, port: int=0, context: int=2048, n_gpu_layers: int=0):
        self.executable=Path(executable).resolve(); self.model=Path(model).resolve()
        self.port=int(port); self.context=int(context); self.n_gpu_layers=max(0,int(n_gpu_layers)); self.proc=None

    def _pick_port(self):
        if self.port > 0:
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as probe:
                    probe.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                    probe.bind(('127.0.0.1', self.port))
                return self.port
            except OSError:
                pass
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as probe:
            probe.bind(('127.0.0.1', 0))
            return int(probe.getsockname()[1])

    @property
    def base_url(self): return f'http://127.0.0.1:{self.port}'

    def start(self):
        if self.proc and self.proc.poll() is None: return
        if not self.executable.exists(): raise FileNotFoundError(self.executable)
        if not self.model.exists(): raise FileNotFoundError(self.model)
        preferred = self.port
        self.port = self._pick_port()
        cmd=[str(self.executable),'-m',str(self.model),'-c',str(self.context),'--host','127.0.0.1','--port',str(self.port),'-ngl',str(self.n_gpu_layers)]
        env=dict(os.environ)
        self.proc=subprocess.Popen(cmd,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True,errors='replace',env=env)
        for _ in range(120):
            try:
                with urllib.request.urlopen(self.base_url+'/health',timeout=1) as r:
                    if r.status<500: return
            except Exception: time.sleep(.25)
        self.stop(); raise RuntimeError('llama-server did not become ready')

    def stop(self):
        if self.proc and self.proc.poll() is None:
            try: self.proc.terminate(); self.proc.wait(timeout=3)
            except Exception:
                try: self.proc.kill()
                except Exception: pass
        self.proc=None

    def chat(self,messages,max_tokens=256,temperature=.7):
        body=json.dumps({'messages':messages,'max_tokens':int(max_tokens),'temperature':float(temperature),'stream':False}).encode()
        req=urllib.request.Request(self.base_url+'/v1/chat/completions',data=body,headers={'Content-Type':'application/json'},method='POST')
        try:
            with urllib.request.urlopen(req,timeout=1800) as r: data=json.loads(r.read().decode('utf-8','replace'))
        except urllib.error.HTTPError as e: raise RuntimeError(e.read().decode(errors='replace')[-4000:])
        choices=data.get('choices') or []
        text=choices[0].get('message',{}).get('content','') if choices else ''
        return {'text':text,'raw':data}

    def stream_chat(self,messages,max_tokens=256,temperature=.7):
        body=json.dumps({'messages':messages,'max_tokens':int(max_tokens),'temperature':float(temperature),'stream':True}).encode()
        req=urllib.request.Request(self.base_url+'/v1/chat/completions',data=body,headers={'Content-Type':'application/json'},method='POST')
        with urllib.request.urlopen(req,timeout=1800) as r:
            for raw in r:
                line=raw.decode('utf-8','replace').strip()
                if not line.startswith('data:'): continue
                payload=line[5:].strip()
                if payload=='[DONE]': break
                try:
                    data=json.loads(payload); delta=((data.get('choices') or [{}])[0].get('delta') or {}).get('content')
                    if delta: yield delta
                except Exception: continue
