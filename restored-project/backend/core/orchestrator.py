# -*- coding: utf-8 -*-
"""High-level request orchestration: intent -> plan -> tools -> verify -> recover."""
from __future__ import annotations
from dataclasses import dataclass, asdict
from typing import Any, Callable, Dict, List
import re, time

@dataclass
class PlanStep:
    step_id: int
    title: str
    action: str
    requires_confirmation: bool = False
    status: str = "pending"
    result: Any = None

@dataclass
class OrchestrationPlan:
    request: str
    intent: str
    confidence: float
    steps: List[PlanStep]
    created_at: float

    def to_dict(self): return asdict(self)

class Orchestrator:
    """Deterministic front-controller around the existing ALI runtime.

    Model reasoning can still be used for the natural-language answer, while this
    layer makes computer actions explicit, auditable and recoverable.
    """
    def __init__(self, runtime, verifier: Callable[[str, Dict[str, Any]], Dict[str, Any]] | None = None):
        self.runtime = runtime
        self.verifier = verifier

    def classify(self, text: str) -> tuple[str, float]:
        t = (text or "").strip().lower()
        rules = [
            (r"^(read_file|اقرأ\s+ملف|افتح\s+ملف)\s+", "read_file", .98),
            (r"^(write_file|أنشئ\s+ملف|اكتب\s+في\s+ملف)\s+", "write_file", .98),
            (r"^(list_dir|ls|استعرض\s+المجلد)", "list_dir", .96),
            (r"^(search_files|search|ابحث\s+في\s+الملفات)", "search_files", .94),
            (r"^(run_command|run|شغّل\s+الأمر)", "run_command", .96),
            (r"^git\s+(status|diff|log|branch|commit)", "git", .99),
            (r"(درّب|تدريب|train|fine.?tun|lora)", "training", .82),
            (r"(gguf|quantiz|حوّل.*gguf|تكميم)", "gguf", .90),
            (r"(افحص|حلل|analy[sz]e).*project|حلل المشروع", "analyze_project", .88),
        ]
        for pat, intent, conf in rules:
            if re.search(pat, t, re.I): return intent, conf
        return ("question", .70 if t else 0.0)

    def make_plan(self, request: str) -> OrchestrationPlan:
        intent, confidence = self.classify(request)
        steps: List[PlanStep] = []
        if intent in {"read_file","list_dir","search_files","run_command"}:
            steps = [PlanStep(1, f"Execute {intent}", intent, intent == "run_command")]
            if intent == "run_command": steps.append(PlanStep(2, "Verify command result", "verify_command"))
        elif intent == "git":
            steps = [PlanStep(1, "Inspect Git state", "git_inspect")]
        elif intent == "analyze_project":
            steps = [PlanStep(1,"Map project", "list_dir"), PlanStep(2,"Inspect entrypoints", "search_files"), PlanStep(3,"Summarize risks", "verify")]
        elif intent == "training":
            steps = [PlanStep(1,"Validate dataset", "validate_dataset"), PlanStep(2,"Start training", "training", True), PlanStep(3,"Evaluate checkpoint", "evaluate")]
        elif intent == "gguf":
            steps = [PlanStep(1,"Locate HF checkpoint", "locate_model"), PlanStep(2,"Convert to GGUF", "gguf_convert", True), PlanStep(3,"Validate artifact", "gguf_validate")]
        return OrchestrationPlan(request, intent, confidence, steps, time.time())

    def execute(self, plan: OrchestrationPlan, context, tool_runner: Callable[[str, Dict[str,Any]], Dict[str,Any]] | None = None) -> Dict[str,Any]:
        runner = tool_runner or (lambda name, kwargs: self.runtime._tool(name, context, **kwargs))
        results=[]
        for step in plan.steps:
            step.status="running"
            if step.requires_confirmation:
                step.status="blocked_confirmation"
                results.append({"step":step.step_id,"ok":False,"needs_confirmation":True,"action":step.action})
                break
            if step.action in {"read_file","list_dir","search_files","run_command"}:
                kwargs=self._arguments(plan.intent,plan.request)
                res=runner(step.action, kwargs); step.result=res
                ok=bool(res.get("ok") or res.get("success"))
                step.status="completed" if ok else "failed"
                results.append({"step":step.step_id,"tool":step.action,"result":res})
                if not ok and step.action != "run_command":
                    break
            else:
                step.status="skipped"
        return {"ok": not any(r.get("result",{}).get("ok") is False for r in results) and not any(r.get("needs_confirmation") for r in results), "plan":plan.to_dict(), "results":results}

    def _arguments(self, intent: str, text: str) -> Dict[str,Any]:
        parts=text.strip().split(maxsplit=1); rest=parts[1] if len(parts)>1 else ""
        if intent in {"read_file","list_dir"}: return {"path":rest}
        if intent=="search_files": return {"pattern":rest}
        if intent=="run_command": return {"command":rest}
        return {}
