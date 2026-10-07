from __future__ import annotations
from pathlib import Path
import hashlib,json
class Verifier:
    def file_exists(self,path):return {"passed":Path(path).is_file(),"path":str(path)}
    def file_sha256(self,path,expected): 
        p=Path(path); actual=hashlib.sha256(p.read_bytes()).hexdigest() if p.is_file() else None
        return {"passed":actual==expected,"expected":expected,"actual":actual}
    def text_contains(self,path,needle):
        p=Path(path); actual=p.read_text(encoding="utf-8",errors="replace") if p.is_file() else ""
        return {"passed":needle in actual,"needle":needle}
    def json_valid(self,path):
        try:json.loads(Path(path).read_text(encoding="utf-8"));return {"passed":True}
        except Exception as e:return {"passed":False,"error":str(e)}
    def all(self,checks):return {"passed":all(x.get("passed") for x in checks),"checks":checks}
