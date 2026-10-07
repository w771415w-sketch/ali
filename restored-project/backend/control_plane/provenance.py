from __future__ import annotations
from pathlib import Path
import hashlib,json,time
class ProvenanceTracker:
    def __init__(self,path): self.path=Path(path); self.path.parent.mkdir(parents=True,exist_ok=True); self.rows=self._load()
    def _load(self):
        try:return json.loads(self.path.read_text(encoding="utf-8"))
        except (FileNotFoundError,json.JSONDecodeError):return []
    def record(self,artifact,origin,transformations=None,source_refs=None,license_ref=None):
        p=Path(artifact); sha=hashlib.sha256(p.read_bytes()).hexdigest() if p.exists() else None
        row={"artifact":str(p),"sha256":sha,"origin":origin,"transformations":transformations or [],"source_refs":source_refs or [],"license_ref":license_ref,"created_at":time.time()}
        self.rows.append(row); self.path.write_text(json.dumps(self.rows,ensure_ascii=False,indent=2),encoding="utf-8"); return row
    def latest(self,artifact):
        xs=[x for x in self.rows if x["artifact"]==str(artifact)]; return xs[-1] if xs else None