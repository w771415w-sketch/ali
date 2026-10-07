# -*- coding: utf-8 -*-
"""Bounded local agent loop: plan -> tool call -> result -> verify -> answer."""
from __future__ import annotations

from typing import Dict, Any

from core.tool_protocol import parse_tool_calls, tool_prompt


class AgentLoop:
    def __init__(self, runtime, max_steps: int = 8, max_calls_per_step: int = 4):
        self.runtime = runtime
        self.max_steps = max(1, int(max_steps))
        self.max_calls_per_step = max(1, int(max_calls_per_step))

    def run(self, messages, ctx, tools_desc) -> Dict[str, Any]:
        if self.runtime.model_engine is None:
            return {
                "ok": False,
                "text": "ALI model is not loaded. Train or load a checkpoint first.",
                "steps": [],
            }

        tool_map = {d["name"]: self.runtime.registry.get(d["name"]) for d in tools_desc}
        working = list(messages)
        system = tool_prompt(tools_desc)
        trace = []

        for step in range(self.max_steps):
            answer = self.runtime.model_engine.complete(
                working,
                system=system,
                max_new_tokens=384,
                temperature=.2,
            )
            calls = parse_tool_calls(answer, tool_map)

            if not calls:
                return {"ok": True, "text": answer, "steps": trace, "finished": True}

            if len(calls) > self.max_calls_per_step:
                return {
                    "ok": False,
                    "text": "تم رفض سلسلة الأدوات لأنها تجاوزت الحد الآمن للاستدعاءات في خطوة واحدة.",
                    "steps": trace,
                    "error": "tool_call_limit",
                }

            working.append({"role": "assistant", "content": answer})
            for call in calls:
                name = call["tool"]
                args = call.get("arguments", {})
                result = self.runtime._tool(name, ctx, **args)
                trace.append({"step": step + 1, "tool": name, "arguments": args, "result": result})
                working.append({
                    "role": "tool",
                    "content": __import__("json").dumps(result, ensure_ascii=False),
                    "meta": {"tool": name},
                })
                if result.get("needs_confirmation"):
                    return {
                        "ok": False,
                        "text": result.get("error", "Confirmation required."),
                        "steps": trace,
                        "needs_confirmation": True,
                    }

        return {
            "ok": False,
            "text": "Reached the tool-step limit without a final answer.",
            "steps": trace,
            "error": "max_steps",
        }


__all__ = ["AgentLoop"]
