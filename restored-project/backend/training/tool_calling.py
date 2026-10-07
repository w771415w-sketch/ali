# -*- coding: utf-8 -*-
"""Build deterministic tool-calling SFT examples from ALI's registered tools."""
from __future__ import annotations
from pathlib import Path
import json, hashlib
from typing import Iterable, Mapping, Any

def _hash(obj: Any) -> str:
    raw=json.dumps(obj,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode('utf-8')
    return hashlib.sha256(raw).hexdigest()

def build_tool_calling_dataset(tools: Iterable[Mapping[str,Any]], out: str|Path, bilingual: bool=True)->dict:
    rows=[]
    for tool in tools:
        name=str(tool.get('name') or '')
        if not name: continue
        schema=tool.get('input_schema') or {'type':'object','properties':{}}
        description=str(tool.get('description') or '')
        prompts=[f"Use the {name} tool when appropriate.",f"How should ALI call {name}?" if bilingual else f"Call {name} when needed."]
        if bilingual:
            prompts += [f"استخدم أداة {name} عندما تكون مطلوبة.",f"متى يستدعي ALI الأداة {name}؟"]
        for prompt in prompts:
            answer=json.dumps({'tool':name,'arguments':{}},ensure_ascii=False,separators=(',',':'))
            row={'id':_hash([name,prompt]),'messages':[{'role':'system','content':'You are ALI. Use tools only when needed and follow their schemas.'},{'role':'user','content':prompt},{'role':'assistant','content':answer}], 'tool_name':name,'tool_schema':schema,'description':description}
            rows.append(row)
    p=Path(out); p.parent.mkdir(parents=True,exist_ok=True)
    seen=set(); kept=[]
    with p.open('w',encoding='utf-8') as f:
        for r in rows:
            if r['id'] in seen: continue
            seen.add(r['id']); kept.append(r); f.write(json.dumps(r,ensure_ascii=False)+'\n')
    return {'output':str(p),'records':len(kept),'unique_ids':len(seen)}
