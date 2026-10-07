# -*- coding: utf-8 -*-
from __future__ import annotations
from pathlib import Path
from typing import Dict,Any
import json, math
import torch
from training.trainer import JsonlChatDataset, collate

def evaluate_model(model, tokenizer, path, device='cpu')->Dict[str,Any]:
    ds=JsonlChatDataset(path,tokenizer,model.config.max_position_embeddings); total=0.; n=0; model.to(device); model.eval()
    with torch.no_grad():
        for i in range(len(ds)):
            b=collate([ds[i]],tokenizer.pad_id); b={k:v.to(device) for k,v in b.items()}; out=model(**b); total+=float(out['loss'].item()); n+=1
    loss=total/max(1,n); return {'loss':loss,'perplexity':float(math.exp(min(20,loss))),'samples':n}

def promotion_gate(candidate:Dict[str,Any],baseline:Dict[str,Any]|None,regressions:Dict[str,Any],min_improvement:float=0.002)->Dict[str,Any]:
    tests_ok=bool(regressions.get('passed',False)); c=float(candidate.get('loss',float('inf'))); b=float((baseline or {}).get('loss',float('inf')))
    if not tests_ok: return {'promote':False,'reason':'regression tests failed'}
    if not math.isfinite(b): return {'promote':math.isfinite(c),'reason':'no baseline'}
    improved=c <= b*(1-min_improvement); return {'promote':improved,'reason':'validation loss improved' if improved else 'validation loss did not improve','candidate_loss':c,'baseline_loss':b}
