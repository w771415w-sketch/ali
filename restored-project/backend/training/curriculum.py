# -*- coding: utf-8 -*-
"""Deterministic curriculum scheduling for ALI training.

Samples receive a reproducible difficulty score from length, tool depth, code
complexity and language balance. The scheduler gradually exposes harder samples.
"""
from __future__ import annotations
from dataclasses import dataclass
from typing import Sequence, Mapping, Any
import hashlib, math, re

_AR=re.compile(r'[\u0600-\u06ff]')
_CODE=re.compile(r'(```|\b(def|class|import|SELECT|CREATE|function|const|try|except)\b)',re.I)
_TOOL=re.compile(r'"tool"\s*:|<tool_call>|<function_call>',re.I)

@dataclass(frozen=True)
class CurriculumConfig:
    warmup_fraction: float = 0.20
    mid_fraction: float = 0.55
    hard_fraction: float = 0.85
    min_score: float = 0.0
    max_score: float = 1.0

def score_record(row: Mapping[str, Any]) -> float:
    text=str(row.get('text') or '')
    words=max(1,len(text.split()))
    length=min(1.0, math.log1p(words)/math.log1p(600))
    turns=len(re.findall(r'<\|(?:system|user|assistant)\|>',text))
    tools=min(1.0, len(_TOOL.findall(text))/4.0)
    code=min(1.0, len(_CODE.findall(text))/8.0)
    arabic=1.0 if _AR.search(text) else 0.0
    # Blend breadth and complexity; avoid making very long noisy rows dominate.
    return round(min(1.0, 0.30*length+0.20*min(1.0,turns/8)+0.20*tools+0.20*code+0.10*arabic),6)

class CurriculumSchedule:
    def __init__(self, rows: Sequence[Mapping[str,Any]], cfg: CurriculumConfig|None=None):
        self.cfg=cfg or CurriculumConfig()
        enriched=[]
        for i,row in enumerate(rows):
            rid=str(row.get('id') or hashlib.sha256(str(row.get('text','')).encode('utf-8')).hexdigest())
            enriched.append((score_record(row),rid,i))
        enriched.sort(key=lambda x:(x[0],x[1]))
        self.indices=[x[2] for x in enriched]
        self.scores=[x[0] for x in enriched]

    def indices_for_epoch(self, epoch:int, epochs:int) -> list[int]:
        n=len(self.indices)
        if not n:return []
        progress=(epoch+1)/max(1,epochs)
        if progress <= self.cfg.warmup_fraction: frac=0.45
        elif progress <= self.cfg.mid_fraction: frac=0.70
        elif progress <= self.cfg.hard_fraction: frac=0.88
        else: frac=1.0
        take=max(1,int(n*frac))
        return self.indices[:take]
