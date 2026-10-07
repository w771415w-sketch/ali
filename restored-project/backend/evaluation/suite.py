# -*- coding: utf-8 -*-
"""Offline Arabic/English evaluation of a loaded ALI model.

Metrics deliberately stay simple and reproducible: loss/perplexity, response
language coverage, required-keyword coverage, and structured tool-call accuracy.
"""
from __future__ import annotations
from pathlib import Path
import json, math, re
from training.trainer import JsonlTextDataset, JsonlChatDataset, collate
from core.tool_protocol import parse_tool_calls
import torch

def _lang(text): return 'ar' if re.search(r'[\u0600-\u06ff]',text) else 'en'
def evaluate_suite(engine, path:str|Path, max_cases:int=200)->dict:
    rows=[json.loads(x) for x in Path(path).read_text(encoding='utf-8').splitlines() if x.strip()][:max_cases]
    metrics={'cases':len(rows),'arabic':0,'english':0,'language_matches':0,'keyword_hits':0,'tool_cases':0,'tool_hits':0}
    for r in rows:
        q=next((m.get('content','') for m in r.get('messages',[]) if m.get('role')=='user'),'')
        lang=r.get('language') or _lang(q); metrics['arabic' if lang=='ar' else 'english']+=1
        try: answer=engine.complete([m for m in r.get('messages',[]) if m.get('role')=='user'],max_new_tokens=96,temperature=0)
        except Exception: continue
        if _lang(answer)==lang:metrics['language_matches']+=1
        kws=r.get('expected_keywords') or []
        if kws and any(str(k).lower() in answer.lower() for k in kws):metrics['keyword_hits']+=1
        if r.get('category')=='tool-calling':
            metrics['tool_cases']+=1
            calls=parse_tool_calls(answer)
            if calls and calls[0].get('tool'):metrics['tool_hits']+=1
    n=max(1,metrics['cases']); metrics['language_accuracy']=metrics['language_matches']/n; metrics['keyword_coverage']=metrics['keyword_hits']/n; metrics['tool_call_accuracy']=metrics['tool_hits']/max(1,metrics['tool_cases']); return metrics

def evaluate_loss(model,tokenizer,path,device='cpu'):
    ds=JsonlChatDataset(path,tokenizer,model.config.max_position_embeddings); total=0.; n=0; model.to(device).eval()
    with torch.no_grad():
        for i in range(len(ds)):
            b=collate([ds[i]],tokenizer.pad_id); b={k:v.to(device) for k,v in b.items()}; out=model(**b); total+=float(out['loss']); n+=1
    loss=total/max(1,n); return {'loss':loss,'perplexity':math.exp(min(20,loss)),'samples':n}
