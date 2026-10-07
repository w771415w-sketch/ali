from __future__ import annotations
import ast,json,hashlib,tarfile,zipfile
from pathlib import Path
class DiagnosticsEngine:
    def __init__(self,max_archive_files=10000,max_archive_bytes=2*1024**3,max_compression_ratio=200):
        self.max_archive_files=int(max_archive_files);self.max_archive_bytes=int(max_archive_bytes);self.max_compression_ratio=float(max_compression_ratio)
    @staticmethod
    def sha256(path):
        h=hashlib.sha256()
        with Path(path).open("rb") as f:
            for chunk in iter(lambda:f.read(1024*1024),b""):h.update(chunk)
        return h.hexdigest()
    def file_type(self,path):
        p=Path(path);suffix=p.suffix.lower()
        if p.is_file():
            head=p.read_bytes()[:16]
            if head.startswith(b"PK\x03\x04"):return "zip"
            if head.startswith(b"\x1f\x8b"):return "gzip"
            if head.startswith(b"7z"):return "7z"
        return {".py":"python",".json":"json",".md":"markdown",".txt":"text",".zip":"zip",".tar":"tar",".gz":"gzip"}.get(suffix,"unknown")
    def inspect_file(self,path):
        p=Path(path);out={"path":str(p),"exists":p.is_file(),"type":self.file_type(p),"errors":[]}
        if not out["exists"]:out["errors"].append("file_not_found");return out
        out["bytes"]=p.stat().st_size;out["sha256"]=self.sha256(p)
        try:
            if out["type"]=="python":ast.parse(p.read_text(encoding="utf-8",errors="replace"),filename=str(p))
            elif out["type"]=="json":json.loads(p.read_text(encoding="utf-8"))
        except Exception as e:out["errors"].append({"kind":"parse_error","message":str(e)})
        return out
    @staticmethod
    def _safe_member(name,root):
        (root/Path(name)).resolve().relative_to(root.resolve())
    def inspect_archive(self,path):
        p=Path(path);out={"path":str(p),"exists":p.is_file(),"safe":True,"errors":[],"members":[]}
        if not p.is_file():out["safe"]=False;out["errors"].append("archive_not_found");return out
        try:
            if zipfile.is_zipfile(p):
                with zipfile.ZipFile(p) as z:
                    infos=z.infolist();total=sum(i.file_size for i in infos)
                    if len(infos)>self.max_archive_files:raise ValueError("archive_file_count_limit")
                    if total>self.max_archive_bytes:raise ValueError("archive_uncompressed_size_limit")
                    if total/max(1,p.stat().st_size)>self.max_compression_ratio:raise ValueError("archive_compression_ratio_limit")
                    for i in infos:
                        try:self._safe_member(i.filename,p.parent);out["members"].append({"name":i.filename,"bytes":i.file_size,"compressed":i.compress_size})
                        except ValueError:out["safe"]=False;out["errors"].append({"kind":"zip_slip","member":i.filename})
                    return out
            if tarfile.is_tarfile(p):
                with tarfile.open(p) as t:
                    members=t.getmembers();total=sum(max(0,m.size) for m in members)
                    if len(members)>self.max_archive_files:raise ValueError("archive_file_count_limit")
                    if total>self.max_archive_bytes:raise ValueError("archive_uncompressed_size_limit")
                    for m in members:
                        if m.issym() or m.islnk():out["safe"]=False;out["errors"].append({"kind":"tar_link_member","member":m.name});continue
                        try:self._safe_member(m.name,p.parent);out["members"].append({"name":m.name,"bytes":max(0,m.size),"type":str(m.type)})
                        except ValueError:out["safe"]=False;out["errors"].append({"kind":"tar_slip","member":m.name})
                    return out
            out["safe"]=False;out["errors"].append("unsupported_archive")
        except Exception as e:out["safe"]=False;out["errors"].append(str(e))
        return out
    def extract_archive(self,path,destination,approved=False):
        if not approved:return {"ok":False,"status":"approval_required"}
        p=Path(path);dest=Path(destination).resolve();dest.mkdir(parents=True,exist_ok=True);inspection=self.inspect_archive(p)
        if not inspection["safe"]:return {"ok":False,"status":"blocked","inspection":inspection}
        try:
            if zipfile.is_zipfile(p):
                with zipfile.ZipFile(p) as z:
                    for item in inspection["members"]:
                        target=(dest/Path(item["name"])).resolve();target.parent.mkdir(parents=True,exist_ok=True)
                        with z.open(item["name"]) as src,target.open("wb") as dst:dst.write(src.read())
            elif tarfile.is_tarfile(p):
                with tarfile.open(p) as t:
                    for item in inspection["members"]:
                        member=t.getmember(item["name"]);target=(dest/Path(item["name"])).resolve();target.parent.mkdir(parents=True,exist_ok=True)
                        if member.isfile():
                            src=t.extractfile(member)
                            if src:
                                with src,target.open("wb") as dst:dst.write(src.read())
            else:return {"ok":False,"status":"unsupported_archive","inspection":inspection}
            return {"ok":True,"status":"extracted","destination":str(dest),"files":len(inspection["members"])}
        except Exception as e:return {"ok":False,"status":"extract_failed","error":str(e),"inspection":inspection}
    def diagnose_project(self,root):
        root=Path(root).resolve();findings=[];py=0
        for p in root.rglob("*"):
            if not p.is_file() or ".git" in p.parts or "__pycache__" in p.parts:continue
            if p.suffix.lower()==".py":
                py+=1
                try:ast.parse(p.read_text(encoding="utf-8",errors="replace"),filename=str(p))
                except Exception as e:findings.append({"path":str(p.relative_to(root)),"severity":"error","kind":"python_syntax","message":str(e)})
            elif p.suffix.lower()==".json":
                try:json.loads(p.read_text(encoding="utf-8"))
                except Exception as e:findings.append({"path":str(p.relative_to(root)),"severity":"error","kind":"json_parse","message":str(e)})
        return {"root":str(root),"python_files":py,"findings":findings,"ok":not any(x["severity"]=="error" for x in findings)}
