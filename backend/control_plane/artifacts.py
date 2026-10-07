from __future__ import annotations
from pathlib import Path
import hashlib, json, time

class ArtifactRegistry:
    def __init__(self,store): self.store=store
    def register_file(self,kind,path,version,metadata=None):
        p=Path(path); data=p.read_bytes(); sha=hashlib.sha256(data).hexdigest()
        aid=f"art_{sha[:16]}"
        self.store.cx.execute("INSERT OR REPLACE INTO artifacts(id,kind,path,sha256,version,metadata,created_at) VALUES(?,?,?,?,?,?,?)",(aid,kind,str(p),sha,str(version),json.dumps(metadata or {},ensure_ascii=False),time.time())); self.store.cx.commit()
        return {"id":aid,"kind":kind,"path":str(p),"sha256":sha,"version":str(version),"metadata":metadata or {}}
    def lineage(self,artifact_id):
        row=self.store.cx.execute("SELECT id,kind,path,sha256,version,metadata,created_at FROM artifacts WHERE id=?",(artifact_id,)).fetchone()
        if not row:return None
        return {"id":row[0],"kind":row[1],"path":row[2],"sha256":row[3],"version":row[4],"metadata":json.loads(row[5]),"created_at":row[6]}
