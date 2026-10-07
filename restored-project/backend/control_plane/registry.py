from __future__ import annotations
import json,time,threading
from pathlib import Path
class Registry:
    def __init__(self,root): self.root=Path(root); self.root.mkdir(parents=True,exist_ok=True); self._lock=threading.Lock()
    def _path(self,kind): return self.root/f"{kind}.json"
    def _load(self,kind):
        p=self._path(kind)
        try:return json.loads(p.read_text(encoding="utf-8"))
        except (FileNotFoundError,json.JSONDecodeError):return []
    def _save(self,kind,rows):
        p=self._path(kind); tmp=p.with_suffix(".tmp"); tmp.write_text(json.dumps(rows,ensure_ascii=False,indent=2),encoding="utf-8"); tmp.replace(p)
    def put(self,kind,name,version,metadata=None,active=False):
        with self._lock:
            rows=[x for x in self._load(kind) if not(x["name"]==name and x["version"]==str(version))]
            rec={"name":name,"version":str(version),"metadata":metadata or {},"active":bool(active),"created_at":time.time()}; rows.append(rec); self._save(kind,rows); return rec
    def get(self,kind,name,version=None):
        rows=self._load(kind); xs=[x for x in rows if x["name"]==name and (version is None or x["version"]==str(version))]; return xs[-1] if xs else None
    def activate(self,kind,name,version):
        with self._lock:
            rows=self._load(kind); found=False
            for x in rows:
                if x["name"]==name:x["active"]=x["version"]==str(version); found|=x["active"]
            self._save(kind,rows); return found
    def list(self,kind): return self._load(kind)