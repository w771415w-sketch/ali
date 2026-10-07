# -*- coding: utf-8 -*-
"""Deterministic KCA request router: normalize -> intent -> capabilities -> plan."""
from __future__ import annotations
from dataclasses import dataclass, asdict
from typing import Any
import re

from control_plane.contracts import RequestEnvelope, TaskState, PlanStep
from control_plane.kca_registry import function_by_name

_AR = re.compile(r"[\u0600-\u06ff]")


@dataclass(frozen=True)
class RouteResult:
    intent: str
    confidence: float
    language: str
    goal: str
    constraints: tuple[str, ...] = ()


class KCARequestRouter:
    """Small deterministic router intended as the stable front-controller.

    Learned routing can be plugged in later; the output contract stays unchanged.
    """

    RULES = [
        (re.compile(r"^(read_file|read|اقرأ\s+ملف|افتح\s+ملف)\s+", re.I), "read_file", .98),
        (re.compile(r"^(write_file|write|أنشئ\s+ملف|اكتب\s+في\s+ملف)\s+", re.I), "write_file", .98),
        (re.compile(r"^(list_dir|ls|استعرض\s+المجلد)(?:\s+.*)?$", re.I), "list_dir", .96),
        (re.compile(r"^(search_files|search|ابحث\s+في\s+الملفات)\s+", re.I), "search_files", .94),
        (re.compile(r"^(run_command|run|شغّل\s+الأمر)\s+", re.I), "run_command", .96),
        (re.compile(r"^git\s+(status|diff|log|branch|commit)", re.I), "git", .99),
        (re.compile(r"(درّب|تدريب|train|fine.?tun|lora)", re.I), "training", .82),
        (re.compile(r"(gguf|quantiz|حوّل.*gguf|تكميم)", re.I), "gguf", .90),
        (re.compile(r"(حلل\s+المشروع|analy[sz]e\s+project)", re.I), "analyze_project", .88),
    ]

    def route(self, envelope: RequestEnvelope) -> RouteResult:
        text = (envelope.raw_text or "").strip()
        language = envelope.language if envelope.language != "auto" else ("ar" if _AR.search(text) else "en")
        for rule, intent, conf in self.RULES:
            if rule.search(text):
                return RouteResult(intent, conf, language, text)
        return RouteResult("question", .70 if text else 0.0, language, text)

    def build_state(self, envelope: RequestEnvelope) -> TaskState:
        routed = self.route(envelope)
        rest = envelope.raw_text.strip()
        params: dict[str, Any] = {}
        parts = rest.split(maxsplit=1)
        tail = parts[1] if len(parts) > 1 else ""
        if routed.intent == "read_file" and tail.startswith(("ملف ", "file ")):
            tail = tail.split(" ", 1)[1]
        if routed.intent in {"read_file", "list_dir"}:
            params["path"] = tail
        elif routed.intent == "search_files":
            params["pattern"] = tail
        elif routed.intent == "run_command":
            params["command"] = tail
        state = TaskState(
            request_id=envelope.request_id,
            intent=routed.intent,
            confidence=routed.confidence,
            goal=routed.goal,
            implicit_intent=self._implicit_intent(envelope.raw_text),
        )
        state.task_state["language"] = routed.language
        state.task_state["params"] = params
        state.candidate_actions = self.candidates(routed.intent, params)
        if state.candidate_actions:
            state.selected_action = state.candidate_actions[0]
        return state

    def candidates(self, intent: str, params: dict[str, Any]) -> list[dict[str, Any]]:
        mapping = {
            "read_file": ["read_file", "CONTEXT_ASSEMBLER", "VERIFICATION_ENGINE"],
            "write_file": ["write_file", "RISK_GATE", "VERIFICATION_ENGINE", "REPAIR_ENGINE"],
            "list_dir": ["list_dir", "VERIFICATION_ENGINE"],
            "search_files": ["search_files", "CONTEXT_ASSEMBLER"],
            "run_command": ["run_command", "RISK_GATE", "VERIFICATION_ENGINE"],
            "git": ["git_status", "VERIFICATION_ENGINE"],
            "training": ["DATA_PROVENANCE_TRACKER", "PLAN_BUILDER", "EXECUTION_ENGINE", "VERIFICATION_ENGINE"],
            "gguf": ["GGUF_CONVERSION", "VERIFICATION_ENGINE"],
            "analyze_project": ["CONTEXT_ASSEMBLER", "PLAN_BUILDER", "VERIFICATION_ENGINE"],
            "question": ["SOURCE_ROUTER", "FINAL_RESPONSE_BUILDER"],
        }
        out = []
        for name in mapping.get(intent, ["FINAL_RESPONSE_BUILDER"]):
            row = function_by_name(name)
            if row:
                out.append({"id": row["id"], "name": row["name"], "purpose": row["purpose"], "params": params})
            else:
                out.append({"id": None, "name": name, "params": params})
        return out

    def function_count(self) -> int:
        from control_plane.kca_registry import FUNCTIONS
        return len(FUNCTIONS)

    @staticmethod
    def _implicit_intent(text: str) -> str | None:
        low = (text or "").lower()
        if any(x in low for x in ("professional", "احترافي", "بدون أخطاء", "without errors")):
            return "deliver verified, production-oriented result"
        if any(x in low for x in ("compare", "قارن", "مقارنة")):
            return "compare alternatives with evidence"
        if any(x in low for x in ("explain", "اشرح", "وضح")):
            return "understand and learn"
        return None


__all__ = ["KCARequestRouter", "RouteResult"]
