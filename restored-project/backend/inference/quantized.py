# -*- coding: utf-8 -*-
"""Real PyTorch CPU quantization helpers for ALI.

Dynamic int8 quantization targets Linear modules and is suitable for CPU inference
on the user's 32GB-RAM machine. GGUF remains the preferred disk/runtime format when
llama.cpp tooling is installed.
"""
from __future__ import annotations
from pathlib import Path
import torch
from torch import nn
from typing import Any

def quantize_cpu_int8(model: nn.Module) -> nn.Module:
    model=model.cpu().eval()
    try:
        return torch.ao.quantization.quantize_dynamic(model,{nn.Linear},dtype=torch.qint8)
    except Exception:
        return model

def save_quantized(model: nn.Module, path: str|Path) -> Path:
    p=Path(path); p.parent.mkdir(parents=True,exist_ok=True)
    # Save the quantized state plus a small descriptor so loading can recreate
    # the same dynamic-quantization wrapper around a fresh ALI architecture.
    torch.save({'format':'torch_dynamic_int8_v1','state_dict':model.state_dict()},p)
    return p

def load_quantized(model: nn.Module, path: str|Path, device: str='cpu')->nn.Module:
    p=Path(path); blob=torch.load(p,map_location=device,weights_only=False)
    if isinstance(blob,dict) and blob.get('format')=='torch_dynamic_int8_v1':
        model=quantize_cpu_int8(model)
        model.load_state_dict(blob['state_dict'],strict=False)
        return model
    if isinstance(blob,dict) and 'state_dict' in blob:
        blob=blob['state_dict']
    model.load_state_dict(blob,strict=False); return model

def inspect_quantized(path: str|Path)->dict[str,Any]:
    p=Path(path); info={'path':str(p),'exists':p.exists(),'size_bytes':p.stat().st_size if p.exists() else 0,'format':'unknown'}
    if not p.exists(): return info
    try:
        blob=torch.load(p,map_location='cpu',weights_only=False)
        info['format']=blob.get('format','torch_state_dict') if isinstance(blob,dict) else 'torch_object'
        info['tensor_count']=len(blob.get('state_dict',{})) if isinstance(blob,dict) and isinstance(blob.get('state_dict'),dict) else None
    except Exception as e: info['error']=str(e)
    return info
