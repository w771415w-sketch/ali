# -*- coding: utf-8 -*-
"""Declarative local skill registry. Skills are capability instructions, not arbitrary executables."""
from __future__ import annotations
from pathlib import Path
import json
class SkillRegistry:
    def __init__(self,root):self.root=Path(root)
    def discover(self):
        rows=[]
        for p in list(self.root.glob('*/skill.json'))+list(self.root.glob('*/SKILL.md'))+list(self.root.glob('**/skill.json')):
            try:
                if p.suffix=='.json': rows.append(json.loads(p.read_text(encoding='utf-8')))
                else: rows.append({'name':p.parent.name,'path':str(p),'type':'instruction'})
            except Exception:pass
        uniq={r.get('name',r.get('path')):r for r in rows}; return list(uniq.values())
    def get(self,name):return next((x for x in self.discover() if x.get('name')==name),None)
