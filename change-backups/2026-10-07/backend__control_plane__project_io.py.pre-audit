from __future__
from pathlib import Path
from difflib import unified_diff
from zipfile import ZipFile, ZIP_DEFLATED
import uuid, hashlib, time
class Workspace:
    def __init__(self,root): self.root=Path(root).resolve(); self.root.mkdir(parents=True,exist_ok=True)
    def resolve(self,relative):
        p=(self.root/relative).resolve()
        try:p.relative_to(self.root)
        except ValueError: raise PermissionError("path escapes workspace")
        return p
    def read(self,relative): return self.resolve(relative).read_text(encoding="utf-8",errors="replace")
    def write(self,relative,text,expected_sha256=None):
        p=self.resolve(relative); old=p.read_text(encoding="utf-8",errors="replace") if p.exists() else ""
        if expected_sha256 is not None and hashlib.sha256(old.encode("utf-8")).hexdigest()!=expected_sha256: raise ValueError("file changed since plan; refusing stale write")
        created = not p.exists()
        p.parent.mkdir(parents=True,exist_ok=True); p.write_text(str(text),encoding="utf-8")
        return {"path":str(p.relative_to(self.root)),"sha256":hashlib.sha256(str(text).encode("utf-8")).hexdigest(),"created":created}
    def patch(self,relative,old_text,new_text,expected_count=1):
        current=self.read(relative); count=current.count(old_text)
        if count!=expected_count: raise ValueError(f"patch precondition failed: found {count}, expected {expected_count}")
        return self.write(relative,current.replace(old_text,new_text,expected_count))
    def diff_text(self,relative,before,after): return "".join(unified_diff(before.splitlines(True),after.splitlines(True),fromfile=f"a/{relative}",tofile=f"b/{relative}"))
    def snapshot(self,label="snapshot"):
        ts=time.strftime("%Y%m%d-%H%M%S"); dest=self.root.parent/f".{self.root.name}-{label}-{ts}-{uuid.uuid4().hex[:8]}.zip"
        with ZipFile(dest,"w",ZIP_DEFLATED) as z:
            for p in self.root.rglob("*"):
                if p.is_file() and ".git" not in p.parts:z.write(p,p.relative_to(self.root))
        return str(dest)
    def delete(self,relative):
        p=self.resolve(relative)
        if not p.exists(): return {"path":relative,"deleted":False,"reason":"not_found"}
        if p.is_dir(): raise IsADirectoryError(relative)
        data=p.read_bytes(); p.unlink(); return {"path":relative,"deleted":True,"sha256":hashlib.sha256(data).hexdigest()}
    def restore(self,archive):
        archive=Path(archive).resolve()
        with ZipFile(archive) as z:
            for info in z.infolist():
                target=(self.root/info.filename).resolve()
                try: target.relative_to(self.root)
                except ValueError: raise PermissionError("snapshot contains path outside workspace")
            z.extractall(self.root)
        return str(self.root)
