# -*- coding: utf-8 -*-
"""Small dependency-free LoRA implementation for ALI continued training.

LoRA is optional: ALI can train all parameters from scratch, or freeze the base
checkpoint and learn low-rank adapters for inexpensive incremental updates.
"""
from __future__ import annotations
from pathlib import Path
from typing import Iterable
import json
import torch
from torch import nn

class LoRALinear(nn.Module):
    def __init__(self, base: nn.Linear, rank: int = 8, alpha: float = 16.0, dropout: float = 0.0):
        super().__init__()
        if rank < 1: raise ValueError("LoRA rank must be >= 1")
        self.base = base
        self.rank = int(rank)
        self.alpha = float(alpha)
        self.scale = self.alpha / self.rank
        self.dropout = nn.Dropout(dropout)
        self.lora_A = nn.Parameter(torch.empty(self.rank, base.in_features))
        self.lora_B = nn.Parameter(torch.zeros(base.out_features, self.rank))
        nn.init.kaiming_uniform_(self.lora_A, a=5**0.5)
        for p in self.base.parameters(): p.requires_grad = False
    def forward(self, x):
        y = self.base(x)
        update = self.dropout(x) @ self.lora_A.t() @ self.lora_B.t()
        return y + update * self.scale
    def merge(self):
        with torch.no_grad():
            self.base.weight.add_(self.lora_B @ self.lora_A * self.scale)
        return self.base

def apply_lora(model: nn.Module, rank: int = 8, alpha: float = 16.0, dropout: float = 0.05,
               targets: Iterable[str] = ("q_proj", "k_proj", "v_proj", "o_proj", "gate_proj", "up_proj", "down_proj")) -> list[str]:
    targets = tuple(targets)
    replaced = []
    for parent_name, parent in list(model.named_modules()):
        for child_name, child in list(parent.named_children()):
            if isinstance(child, nn.Linear) and (child_name in targets or any(child_name.endswith(t) for t in targets)):
                wrapped = LoRALinear(child, rank, alpha, dropout)
                setattr(parent, child_name, wrapped)
                replaced.append((f"{parent_name}.{child_name}" if parent_name else child_name))
    if not replaced: raise ValueError("No target Linear layers found for LoRA")
    # Keep embeddings and lm_head frozen by default as part of the base model.
    for n,p in model.named_parameters():
        if "lora_A" not in n and "lora_B" not in n: p.requires_grad = False
    return replaced

def lora_parameters(model: nn.Module):
    return [p for n,p in model.named_parameters() if ("lora_A" in n or "lora_B" in n) and p.requires_grad]

def save_lora_adapter(model: nn.Module, out_dir: str | Path, metadata: dict | None = None) -> Path:
    out=Path(out_dir); out.mkdir(parents=True,exist_ok=True)
    state={n:p.detach().cpu().contiguous() for n,p in model.state_dict().items() if "lora_A" in n or "lora_B" in n}
    if not state: raise ValueError("model has no LoRA adapter parameters")
    try:
        from safetensors.torch import save_file
        save_file(state,str(out/'adapter_model.safetensors'),metadata={'format':'pt','source':'ALI Studio LoRA'})
    except Exception:
        torch.save(state,out/'adapter_model.pt')
    (out/'adapter_config.json').write_text(json.dumps(metadata or {},ensure_ascii=False,indent=2),encoding='utf-8')
    return out

def merge_lora(model: nn.Module) -> int:
    merged=0
    def rec(parent):
        nonlocal merged
        for name, child in list(parent.named_children()):
            if isinstance(child,LoRALinear):
                setattr(parent,name,child.merge()); merged+=1
            else: rec(child)
    rec(model)
    return merged

def load_lora_adapter(model: nn.Module, adapter_dir: str | Path) -> nn.Module:
    """Load previously trained ALI LoRA tensors into an already-wrapped model."""
    p=Path(adapter_dir)
    state_path=p/'adapter_model.safetensors'
    if state_path.exists():
        from safetensors.torch import load_file
        state=load_file(str(state_path),device='cpu')
    elif (p/'adapter_model.pt').exists():
        state=torch.load(p/'adapter_model.pt',map_location='cpu',weights_only=False)
    else:
        raise FileNotFoundError(f'LoRA adapter not found in {p}')
    current=model.state_dict()
    missing=[]
    for k,v in state.items():
        if k in current: current[k].copy_(v)
        else: missing.append(k)
    if missing: raise ValueError(f'Unknown LoRA keys: {missing[:5]}')
    model.load_state_dict(current,strict=False)
    return model
