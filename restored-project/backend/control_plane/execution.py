# -*- coding: utf-8 -*-
"""Observation, verification and bounded recovery for KCA plans."""
from __future__ import annotations
from typing import Any, Callable
import hashlib
import json

from control_plane.contracts import ExecutionTrace, PlanStep, TaskState


class KCAExecutionEngine:
    def __init__(self, tool_runner: Callable[[str, dict[str, Any]], dict[str, Any]]):
        self.tool_runner = tool_runner

    def execute(self, state: TaskState, steps: list[PlanStep]) -> dict[str, Any]:
        trace = ExecutionTrace()
        results: list[dict[str, Any]] = []
        trace.add("request_state", state=state.to_dict())
        for step in steps:
            step.status = "running"
            trace.add("step_started", step_id=step.step_id, action=step.action)
            if step.requires_confirmation:
                step.status = "blocked_confirmation"
                result = {"ok": False, "needs_confirmation": True, "action": step.action}
                results.append(result)
                trace.add("confirmation_required", step_id=step.step_id)
                break
            if not step.tool_name:
                step.status = "completed"
                continue
            result = self.tool_runner(step.tool_name, step.kwargs)
            step.result = result
            ok = bool(result.get("ok") or result.get("success"))
            step.status = "completed" if ok else "failed"
            results.append({"step_id": step.step_id, "tool": step.tool_name, "result": result})
            trace.add("observation", step_id=step.step_id, tool=step.tool_name, result=result)
            if not ok:
                state.error_state = {"step_id": step.step_id, "tool": step.tool_name, "result": result}
                trace.add("failure", **state.error_state)
                break
            if step.verify:
                verification = self.verify_result(step.tool_name, result)
                state.verification = verification
                trace.add("verification", verification=verification)
                if not verification["ok"]:
                    state.error_state = {"type": "verification_failed", "verification": verification}
                    break
        state.observation = {"results": results}
        state.touch()
        trace.finish("completed" if not state.error_state else "failed")
        return {"ok": trace.status == "completed", "results": results, "state": state.to_dict(), "trace": trace.to_dict()}

    @staticmethod
    def verify_result(tool_name: str, result: dict[str, Any]) -> dict[str, Any]:
        ok = bool(result.get("ok") or result.get("success"))
        payload = result.get("data")
        digest = hashlib.sha256(json.dumps(payload, ensure_ascii=False, sort_keys=True, default=str).encode("utf-8")).hexdigest() if payload is not None else ""
        return {"ok": ok, "tool": tool_name, "result_digest": digest, "reason": "tool reported success" if ok else str(result.get("error") or "unknown failure")}


__all__ = ["KCAExecutionEngine"]
