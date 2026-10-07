# -*- coding: utf-8 -*-
from __future__ import annotations
from pathlib import Path
import json, importlib.util

def discover(root:str|Path='plugins'):
    root=Path(root); out=[]
    for p in root.glob('*/plugin.json'):
        try:o=json.loads(p.read_text(encoding='utf-8')); o['_path']=str(p.parent); out.append(o)
        except Exception: pass
    return out

def load_python_plugin(path:str|Path):
    p=Path(path); spec=importlib.util.spec_from_file_location('ali_plugin_'+p.stem,p); mod=importlib.util.module_from_spec(spec); assert spec.loader; spec.loader.exec_module(mod); return mod
