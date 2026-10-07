from __future__
import re
class MemoryManager:
    def __init__(self,store): self.store=store
    def add(self,scope,kind,text,importance=0.5,source="user",version=None):
        return self.store.memory(scope,kind,text,{"importance":float(importance),"source":source,"version":version})
    def validate(self,item,current_version=None):
        d=item.get("data",{}); importance=float(d.get("importance",0.0)); version=d.get("version")
        current=True if version is None or current_version is None else str(version)==str(current_version)
        return {"relevant":importance>0.2,"current":current,"trustworthy":d.get("source") in {"user","verified","system"},"usable":importance>0.2 and current}
    def retrieve(self,scope,query,limit=8,current_version=None):
        q=set(re.findall(r"[\w\u0600-\u06ff]+",query.casefold())); rows=self.store.memories(scope,limit=100); scored=[]
        for r in rows:
            words=set(re.findall(r"[\w\u0600-\u06ff]+",r["text"].casefold())); overlap=len(q & words); meta=self.validate(r,current_version)
            if overlap and meta["usable"]: scored.append((overlap+float(r["data"].get("importance",0))*2,r))
        return [x[1] for x in sorted(scored,key=lambda x:-x[0])[:limit]]
    def consolidate(self,scope,items):
        useful=[x for x in items if self.validate(x).get("usable")]
        for x in useful:self.add(scope,"consolidated",x["text"],importance=max(.5,float(x["data"].get("importance",.5))),source="system")
        return len(useful)
