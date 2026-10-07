from __future__ import annotations
import json,time
from pathlib import Path
class KnowledgeGraph:
    def __init__(self,path):
        self.path=Path(path); self.path.parent.mkdir(parents=True,exist_ok=True)
        try:self.data=json.loads(self.path.read_text(encoding="utf-8"))
        except Exception:self.data={"entities":{},"relations":[],"observations":[]}
    def _save(self): self.path.write_text(json.dumps(self.data,ensure_ascii=False,indent=2),encoding="utf-8")
    def upsert_entity(self,eid,label,attributes=None,source=None,valid_from=None,valid_to=None,version=None):
        row={"id":eid,"label":label,"attributes":attributes or {},"source":source,"valid_from":valid_from,"valid_to":valid_to,"version":version,"updated_at":time.time()}
        self.data["entities"][eid]=row; self._save(); return row
    def observe(self,eid,attribute,value,source=None,version=None):
        obs={"entity":eid,"attribute":attribute,"value":value,"source":source,"version":version,"created_at":time.time()}; self.data.setdefault("observations",[]).append(obs); self._save(); return obs
    def relate(self,src,relation,dst,source=None,valid_from=None,valid_to=None):
        edge={"source":src,"relation":relation,"target":dst,"source_ref":source,"valid_from":valid_from,"valid_to":valid_to,"created_at":time.time()}
        if edge not in self.data["relations"]: self.data["relations"].append(edge); self._save()
        return edge
    def get(self,eid): return self.data["entities"].get(eid)
    def neighbors(self,eid,relation=None): return [r for r in self.data["relations"] if (r["source"]==eid or r["target"]==eid) and (relation is None or r["relation"]==relation)]
    def search(self,query,limit=10):
        q=set(str(query).casefold().split()); out=[]
        for e in self.data["entities"].values():
            txt=(e["label"]+" "+" ".join(str(v) for v in e.get("attributes",{}).values())).casefold(); score=sum(1 for x in q if x in txt)
            if score: out.append((score,e))
        return [e for _,e in sorted(out,key=lambda x:-x[0])[:limit]]
    def conflicts(self,eid,attribute):
        values={o["value"] for o in self.data.get("observations",[]) if o["entity"]==eid and o["attribute"]==attribute}
        if not values:
            values={self.data["entities"].get(eid,{}).get("attributes",{}).get(attribute)}; values.discard(None)
        return len(values)>1
    def resolve(self,eid,attribute,preferred_source=None):
        obs=[o for o in self.data.get("observations",[]) if o["entity"]==eid and o["attribute"]==attribute]
        if preferred_source:
            obs=[o for o in obs if o.get("source")==preferred_source] or obs
        return sorted(obs,key=lambda x:(x.get("version") is not None,x.get("created_at",0)))[-1] if obs else None
