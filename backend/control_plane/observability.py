from __future__
from collections import Counter
import json,time
from pathlib import Path
class Metrics:
    def __init__(self): self.c=Counter(); self.values={}
    def inc(self,key,n=1): self.c[key]+=n
    def observe(self,key,v): self.values.setdefault(key,[]).append(float(v))
    def snapshot(self): return {"counters":dict(self.c),"values":{k:{"count":len(v),"avg":sum(v)/len(v) if v else 0,"last":v[-1] if v else None} for k,v in self.values.items()}}
class EventLog:
    def __init__(self,path): self.path=Path(path); self.path.parent.mkdir(parents=True,exist_ok=True)
    def emit(self,kind,data):
        with self.path.open("a",encoding="utf-8") as f:f.write(json.dumps({"ts":time.time(),"kind":kind,"data":data},ensure_ascii=False)+"\n")
