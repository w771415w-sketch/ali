from __future__ import annotations
import json,time
from pathlib import Path
class ImprovementManager:
    def __init__(self,path): self.path=Path(path); self.path.parent.mkdir(parents=True,exist_ok=True); self.rows=self._load()
    def _load(self):
        try:return json.loads(self.path.read_text(encoding="utf-8"))
        except (FileNotFoundError,json.JSONDecodeError):return []
    def _save(self): self.path.write_text(json.dumps(self.rows,ensure_ascii=False,indent=2),encoding="utf-8")
    def candidate(self,problem,root_cause,lesson,evidence=None):
        r={"id":f"imp_{time.time_ns()}","problem":problem,"root_cause":root_cause,"lesson":lesson,"evidence":evidence or [],"status":"candidate","created_at":time.time()}; self.rows.append(r); self._save(); return r
    def evaluate(self,imp_id,score,regression_passed):
        for r in self.rows:
            if r["id"]==imp_id:r.update(status="evaluated",score=float(score),regression_passed=bool(regression_passed)); self._save(); return r
        return None
    def approve(self,imp_id,approved=False):
        if not approved:return {"ok":False,"status":"approval_required"}
        for r in self.rows:
            if r["id"]==imp_id:
                if r.get("status")!="evaluated" or not r.get("regression_passed") or float(r.get("score",0))<.8:return {"ok":False,"status":"gate_failed"}
                r["status"]="approved"; self._save(); return {"ok":True,"status":"approved","candidate":r}
        return {"ok":False,"status":"not_found"}