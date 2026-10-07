from __future__ import annotations
from pathlib import Path
class ChangeAnalyzer:
    def analyze(self,root,changed_files):
        paths=[Path(x) for x in changed_files]; affected={str(p) for p in paths}
        for p in paths:
            n=p.name.casefold(); s=p.suffix.casefold()
            if n in {"requirements.txt","pyproject.toml","package.json","package-lock.json","poetry.lock"}:affected.add("dependency graph")
            if "schema" in p.parts or s==".sql":affected.update({"database","migrations"})
            if s in {".ts",".tsx",".js",".jsx",".html",".css"}:affected.add("frontend")
            if s==".py":affected.add("backend")
            if "test" in p.name.casefold():affected.add("regression tests")
        risk="high" if {"database","dependency graph"}&affected else "medium" if len(affected)>3 else "low"
        return {"changed":sorted(map(str,paths)),"affected":sorted(affected),"risk":risk}