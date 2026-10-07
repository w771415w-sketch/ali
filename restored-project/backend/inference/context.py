# -*- coding: utf-8 -*-
"""Context budgeting for low-memory ALI inference."""
from __future__ import annotations
from dataclasses import dataclass
from typing import Any

@dataclass
class ContextBudget:
    max_tokens: int
    reserved_output_tokens: int
    prompt_tokens: int
    kept_messages: int
    truncated: bool


def fit_messages(messages: list[dict[str, Any]], tokenizer, max_context: int, reserved_output: int = 128) -> tuple[list[dict[str, Any]], ContextBudget]:
    max_context = max(64, int(max_context))
    reserved_output = max(8, min(int(reserved_output), max_context // 2))
    budget = max_context - reserved_output
    kept: list[dict[str, Any]] = []
    total = 0
    truncated = False
    # System stays first; then keep newest turns that fit.
    system = [m for m in messages if m.get("role") == "system"][:1]
    rest = [m for m in messages if m.get("role") != "system"]
    base = system
    if base:
        total = len(tokenizer.encode(base[0].get("content", ""), add_bos=False, add_eos=False))
    for msg in reversed(rest):
        n = len(tokenizer.encode(str(msg.get("content", "")), add_bos=False, add_eos=False)) + 4
        if total + n > budget:
            truncated = True
            break
        kept.append(msg)
        total += n
    kept.reverse()
    final = base + kept
    return final, ContextBudget(max_context, reserved_output, total, len(final), truncated)
