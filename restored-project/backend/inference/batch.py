# -*- coding: utf-8 -*-
"""Bounded batch inference for offline evaluation and data generation."""
from __future__ import annotations
from typing import Iterable

def batch_complete(engine, prompts: Iterable[str], batch_size: int = 1, **kwargs) -> list[str]:
    prompts=list(prompts); out=[]
    for i in range(0,len(prompts),max(1,int(batch_size))):
        for p in prompts[i:i+max(1,int(batch_size))]: out.append(engine.complete(p,**kwargs))
    return out
