# -*- coding: utf-8 -*-
"""Stable typed contracts for the ALI KCA control plane."""
from __future__ import annotations
from dataclasses import dataclass, field, asdict
from typing import Any
import time
import uuid


def _id(prefix: str) -> str:
    return f"{prefix}-{uuid.uuid4().hex[:12]}"


@dataclass
class RequestEnvelope:
    raw_text: str
    project_dir: str = ""
    session_id: str = ""
    language: str = "auto"
    channel: str = "desktop"
    request_id: str = field(default_factory=lambda: _id("req"))
    created_at: float = field(default_factory=time.time)
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class TaskState:
    request_id: str
    intent: str = "unknown"
    confidence: float = 0.0
    goal: str = ""
    constraints: list[str] = field(default_factory=list)
    entities: list[dict[str, Any]] = field(default_factory=list)
    implicit_intent: str | None = None
    knowledge_state: dict[str, Any] = field(default_factory=dict)
    task_state: dict[str, Any] = field(default_factory=dict)
    candidate_actions: list[dict[str, Any]] = field(default_factory=list)
    selected_action: dict[str, Any] | None = None
    tool_state: dict[str, Any] = field(default_factory=dict)
    observation: dict[str, Any] | None = None
    error_state: dict[str, Any] | None = None
    correction: dict[str, Any] | None = None
    verification: dict[str, Any] | None = None
    final_output: Any = None
    uncertainty: dict[str, Any] | None = None
    provenance: list[dict[str, Any]] = field(default_factory=list)
    updated_at: float = field(default_factory=time.time)

    def touch(self) -> None:
        self.updated_at = time.time()

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class PlanStep:
    step_id: str
    title: str
    action: str
    tool_name: str | None = None
    kwargs: dict[str, Any] = field(default_factory=dict)
    requires_confirmation: bool = False
    verify: bool = True
    status: str = "pending"
    result: Any = None

    @classmethod
    def make(cls, title: str, action: str, **kwargs: Any) -> "PlanStep":
        return cls(step_id=_id("step"), title=title, action=action, **kwargs)


@dataclass
class ExecutionTrace:
    operation_id: str = field(default_factory=lambda: _id("op"))
    tool_call_id: str | None = None
    observation_id: str | None = None
    state_transition_id: str | None = None
    started_at: float = field(default_factory=time.time)
    finished_at: float | None = None
    events: list[dict[str, Any]] = field(default_factory=list)
    status: str = "created"

    def add(self, event: str, **data: Any) -> None:
        self.events.append({"event": event, "ts": time.time(), **data})

    def finish(self, status: str) -> None:
        self.status = status
        self.finished_at = time.time()

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
