from __future__ import annotations
import hashlib,json,time
from pathlib import Path
from .schemas import new_id
class FailureManager:
    def __init__(self,store): self.store=store
    def classify(self,error):
        t=str(error).casefold()
        if "permission" in t or "access denied" in t:return "permission"
        if "timeout" in t:return "timeout"
        if "not found" in t or "no such file" in t:return "missing_resource"
        if "syntaxerror" in t or "parse" in t or "compile" in t:return "syntax"
        if "memoryerror" in t or "out of memory" in t:return "resource"
        if "network" in t or "connection" in t:return "network"
        return "unknown"
    def record(self,error,context):
        category=self.classify(error); sig=hashlib.sha256((category+"|"+str(error)).encode()).hexdigest()[:20]
        self.store.failure(new_id("failure"),sig,str(error),{"category":category,"context":context}); return {"category":category,"signature":sig}
    def known(self,error):
        c=self.classify(error); s=hashlib.sha256((c+"|"+str(error)).encode()).hexdigest()[:20]; return self.store.failures(s)
class CheckpointManager:
    def __init__(self,root): self.root=Path(root); self.root.mkdir(parents=True,exist_ok=True)
    def save(self,label,payload):
        p=self.root/f"{time.time_ns()}_{label}.json"; p.write_text(json.dumps(payload,ensure_ascii=False,indent=2),encoding="utf-8"); return str(p)
    def latest(self):
        xs=sorted(self.root.glob("*.json")); return str(xs[-1]) if xs else None
    def load(self,path): return json.loads(Path(path).read_text(encoding="utf-8"))