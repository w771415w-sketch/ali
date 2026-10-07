# -*- coding: utf-8 -*-
from __future__ import annotations
from pathlib import Path
import json
class PluginRegistry:
    def __init__(self,root):self.root=Path(root)
    def discover(self):
        out=[]
        for p in self.root.glob('*/plugin.json'):
            try:d=json.loads(p.read_text(encoding='utf-8')); d['path']=str(p.parent); out.append(d)
            except Exception:pass
        return out
