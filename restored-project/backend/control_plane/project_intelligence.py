from __future__ import annotations
import json
from pathlib import Path
from .code_intelligence import CodeIntelligence
class ProjectIntelligence:
    def __init__(self):self.code=CodeIntelligence()
    def analyze(self,root):
        root=Path(root); inventory=self.code.inventory(root)
        manifests=[x["path"] for x in inventory if x["path"].split("/")[-1] in {"pyproject.toml","requirements.txt","package.json","package-lock.json","Cargo.toml","go.mod","pom.xml"}]
        tests=[x["path"] for x in inventory if "test" in Path(x["path"]).name.casefold()]
        code=self.code.parse_project(root)
        return {"root":str(root),"file_count":len(inventory),"manifests":manifests,"test_files":tests,"python_symbols":sum(len(x["symbols"]) for x in code["python"]),"parse_errors":code["errors"]}
    def dependency_manifest(self,root):
        root=Path(root);out={}
        for name in ["requirements.txt","pyproject.toml","package.json","Cargo.toml","go.mod"]:
            p=root/name
            if p.exists():out[name]=p.read_text(encoding="utf-8",errors="replace")
        return out
