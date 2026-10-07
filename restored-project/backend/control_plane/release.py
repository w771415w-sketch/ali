from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
import json,time

@dataclass
class QualityGate:
    thresholds:dict|None=None
    def __post_init__(self):
        self.thresholds=self.thresholds or {"coding":0.80,"arabic":0.80,"tool_use":0.80,"safety":0.95,"regression":1.0}
    def check(self,scores):
        results={k:float(scores.get(k,0))>=float(v) for k,v in self.thresholds.items()}
        return {"passed":all(results.values()),"results":results,"scores":scores,"thresholds":self.thresholds}

class ReleaseManager:
    def __init__(self,root):
        self.root=Path(root);self.root.mkdir(parents=True,exist_ok=True);self.log=self.root/"releases.jsonl"
    def record(self,name,version,stage,quality,artifacts=None):
        row={"name":name,"version":str(version),"stage":stage,"quality":quality,"artifacts":artifacts or [],"created_at":time.time()}
        with self.log.open("a",encoding="utf-8") as f:f.write(json.dumps(row,ensure_ascii=False)+"\n")
        return row
    def promote(self,name,version,quality,approved=False):
        gate=QualityGate().check(quality)
        if not approved:return {"ok":False,"status":"approval_required","gate":gate}
        if not gate["passed"]:return {"ok":False,"status":"quality_gate_failed","gate":gate}
        return {"ok":True,"status":"promoted","release":self.record(name,version,"production",quality)}
    def rollback(self,name,version,approved=False):
        if not approved:return {"ok":False,"status":"approval_required"}
        row=self.record(name,version,"rollback",{"rollback":True})
        return {**row,"ok":True,"status":"rolled_back"}
