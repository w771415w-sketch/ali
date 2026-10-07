# -*- coding: utf-8 -*-
"""Structured tool-calling protocol used by ALI's agent loop."""
from __future__ import annotations

from typing import Any, Dict, List, Mapping
import json
import re

TAGGED = re.compile(r"<tool_call>\s*(.*?)\s*</tool_call>", re.S | re.I)
FENCE = re.compile(r"```(?:json)?\s*(\{.*?\}|\[.*?\])\s*```", re.S | re.I)


def _decode_candidate(raw: str) -> list[dict[str, Any]]:
    try:
        obj = json.loads(raw)
    except Exception:
        return []
    if isinstance(obj, dict):
        obj = [obj]
    if not isinstance(obj, list):
        return []

    out = []
    for item in obj:
        if not isinstance(item, dict):
            continue
        name = item.get("tool") or item.get("name")
        args = item.get("arguments", item.get("args", {}))
        if isinstance(name, str) and name.strip() and isinstance(args, Mapping):
            out.append({"tool": name.strip(), "arguments": dict(args)})
    return out


def validate_tool_calls(calls: List[Dict[str, Any]], tools: Mapping[str, Any] | None = None) -> tuple[bool, str]:
    if not calls:
        return False, "no_tool_calls"
    for call in calls:
        name = str(call.get("tool", ""))
        if tools is not None and name not in tools:
            return False, f"unknown_tool:{name}"
        args = call.get("arguments")
        if not isinstance(args, dict):
            return False, f"invalid_arguments:{name}"
        tool = tools.get(name) if tools else None
        schema = getattr(tool, "input_schema", None) if tool else None
        if isinstance(schema, dict):
            required = schema.get("required", [])
            for key in required:
                if key not in args:
                    return False, f"missing_required:{name}:{key}"
    return True, ""


def validate_tool_call(call: Dict[str, Any], tools: Mapping[str, Any] | None = None) -> tuple[bool, str]:
    """Validate one structured tool call; convenience wrapper for UI/tests."""
    return validate_tool_calls([call], tools)


def parse_tool_calls(text: str, tools: Mapping[str, Any] | None = None) -> List[Dict[str, Any]]:
    """Parse tagged, fenced or raw JSON tool calls; reject unknown tools."""
    raw = str(text or "").strip()
    candidates: list[str] = []

    candidates.extend(m.group(1).strip() for m in TAGGED.finditer(raw))
    candidates.extend(m.group(1).strip() for m in FENCE.finditer(raw))
    if raw.startswith("{") and raw.endswith("}"):
        candidates.append(raw)
    if raw.startswith("[") and raw.endswith("]"):
        candidates.append(raw)

    seen: set[str] = set()
    for candidate in candidates:
        if candidate in seen:
            continue
        seen.add(candidate)
        calls = _decode_candidate(candidate)
        ok, _ = validate_tool_calls(calls, tools)
        if ok:
            return calls
    return []


def tool_prompt(tools: List[Dict[str, Any]]) -> str:
    return (
        "You are ALI's local tool-calling layer. "
        "When a computer action is required, emit exactly one <tool_call> JSON block "
        "or a JSON array of tool calls, then stop generation. "
        'Schema: <tool_call>{"tool":"name","arguments":{...}}</tool_call>\n'
        "Never invent tool results. Available tools:\n" +
        json.dumps(tools, ensure_ascii=False, indent=2)
    )


__all__ = ["parse_tool_calls", "validate_tool_call", "validate_tool_calls", "tool_prompt"]
