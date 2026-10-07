# -*- coding: utf-8 -*-
"""Optional llama-server bridge using only the Python standard library."""
from __future__ import annotations
from pathlib import Path
import json,subprocess,time,urllib.request,urllib.error
class LlamaServer:
    def __init__(self,executable:str|Path,model:str|Path,port:int=8080,context:int=2048): self.executable=Path(executable); self.model=Path(model); self.port=int(port); self.context=int(context); self.proc=None
    @property
    def base_url(self): return f"http://127.0.0.1:{self.port}"
    def start(self):
        if self.proc and self.proc.poll() is None:return
        if not self.executable.exists():raise FileNotFoundError(self.executable)
        if not self.model.exists():raise FileNotFoundError(self.model)
        self.proc=subprocess.Popen([str(self.executable),"-m",str(self.model),"-c",str(self.context),"--host","127.0.0.1","--port",str(self.port)],stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True)
        for _ in range(80):
            try:
                with urllib.request.urlopen(self.base_url+"/health",timeout=1) as r:
                    if r.status<500:return
            except Exception:time.sleep(.25)
        raise RuntimeError("llama-server did not become ready")
    def stop(self):
        if self.proc and self.proc.poll() is None:self.proc.terminate()
        self.proc=None
    def chat(self,messages,max_tokens=256,temperature=.7):
        body=json.dumps({"messages":messages,"max_tokens":int(max_tokens),"temperature":float(temperature)}).encode()
        req=urllib.request.Request(self.base_url+"/v1/chat/completions",data=body,headers={"Content-Type":"application/json"},method="POST")
        try:
            with urllib.request.urlopen(req,timeout=1800) as r:data=json.loads(r.read().decode())
        except urllib.error.HTTPError as e:raise RuntimeError(e.read().decode(errors="replace")[-4000:])
        choices=data.get("choices") or []; text=choices[0].get("message",{}).get("content","") if choices else ""
        return {"text":text,"raw":data}
