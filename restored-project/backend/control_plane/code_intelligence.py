from __future__ import annotations
import ast,json,os
from pathlib import Path
class CodeIntelligence:
    PY_EXT={".py"}
    def inventory(self,root):
        root=Path(root); files=[] 
        for p in root.rglob("*"):
            if p.is_file() and ".git" not in p.parts and "__pycache__" not in p.parts:
                files.append({"path":str(p.relative_to(root)),"suffix":p.suffix.lower(),"bytes":p.stat().st_size})
        return sorted(files,key=lambda x:x["path"])
    def python_symbols(self,path):
        p=Path(path)
        tree=ast.parse(p.read_text(encoding="utf-8",errors="replace"),filename=str(p));symbols=[];imports=[]
        for n in ast.walk(tree):
            if isinstance(n,(ast.FunctionDef,ast.AsyncFunctionDef,ast.ClassDef)):symbols.append({"name":n.name,"kind":type(n).__name__,"line":n.lineno})
            elif isinstance(n,ast.Import):imports.extend(x.name for x in n.names)
            elif isinstance(n,ast.ImportFrom):imports.append(n.module or "")
        return {"path":str(p),"symbols":symbols,"imports":sorted(set(imports))}
    def parse_project(self,root):
        out=[]; errors=[] 
        for p in self.inventory(root):
            if p["suffix"]==".py":
                try:out.append(self.python_symbols(Path(root)/p["path"]))
                except Exception as e:errors.append({"path":p["path"],"error":str(e)})
        return {"files":self.inventory(root),"python":out,"errors":errors}
    def search(self,root,pattern,limit=50):
        hits=[] 
        for item in self.inventory(root):
            p=Path(root)/item["path"]
            if item["bytes"]>2_000_000:continue
            try:
                if pattern.casefold() in p.read_text(encoding="utf-8",errors="replace").casefold():hits.append(item["path"])
            except Exception:pass
            if len(hits)>=limit:break
        return hits
