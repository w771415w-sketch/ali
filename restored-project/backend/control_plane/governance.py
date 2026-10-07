from __future__ import annotations
from pathlib import Path
import time
class DataGovernance:
    SENSITIVE_WORDS=("password","token","secret","api_key","apikey","private_key","serial","uuid","mac","credential")
    def classify(self,key,value):
        k=str(key).casefold(); return "sensitive" if any(x in k for x in self.SENSITIVE_WORDS) else "normal"
    def scrub(self,obj):
        if isinstance(obj,dict): return {k:("[REDACTED]" if self.classify(k,v)=="sensitive" else self.scrub(v)) for k,v in obj.items()}
        if isinstance(obj,list): return [self.scrub(x) for x in obj]
        return obj
    def retention_prune(self,folder,older_than_s):
        root=Path(folder); now=time.time(); removed=[]
        for p in root.rglob("*"):
            if p.is_file() and now-p.stat().st_mtime>older_than_s: p.unlink(); removed.append(str(p))
        return removed
    def export_policy(self): return {"sensitive_keys":list(self.SENSITIVE_WORDS),"default_retention_days":30,"memory_requires_explicit_value":True}
