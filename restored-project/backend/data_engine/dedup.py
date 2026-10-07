# -*- coding: utf-8 -*-
"""Exact and near-duplicate detection using deterministic fingerprints and MinHash-like shingles."""
from __future__ import annotations
import hashlib, re
from collections import Counter
from typing import Iterable, Dict, Any

TOKEN_RE = re.compile(r'\w+', re.UNICODE)

def shingles(text: str, n: int = 5) -> set[str]:
    toks = TOKEN_RE.findall(text.lower())
    if len(toks) <= n: return {" ".join(toks)} if toks else set()
    return {" ".join(toks[i:i+n]) for i in range(len(toks)-n+1)}

def jaccard(a: set[str], b: set[str]) -> float:
    if not a and not b: return 1.0
    if not a or not b: return 0.0
    return len(a & b) / max(1, len(a | b))

def near_duplicate(candidate: str, existing: Iterable[str], threshold: float = 0.92) -> Dict[str, Any]:
    cs = shingles(candidate)
    best = (0.0, None)
    for idx, text in enumerate(existing):
        s = jaccard(cs, shingles(text))
        if s > best[0]: best = (s, idx)
    return {"is_near_duplicate": best[0] >= threshold, "score": best[0], "index": best[1]}
