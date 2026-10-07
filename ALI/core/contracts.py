from __future__ import annotations

import hashlib
import json
import uuid
from dataclasses import dataclass, field, asdict
from typing import Any

from .security import safe_relative_path


@dataclass(frozen=True)
class Operation:
    action: str
    path: str
    content: str | None = None
    expected_sha256: str | None = None

    def validate(self) -> None:
        if self.action not in {"write", "delete", "mkdir"}:
            raise ValueError(f"unsupported action: {self.action}")
        safe_relative_path(self.path)
        if self.action == "write" and self.content is None:
            raise ValueError("write operation requires content")
        if self.expected_sha256 and len(self.expected_sha256) != 64:
            raise ValueError("expected_sha256 must be a sha256 hex digest")

    def to_backend_dict(self) -> dict[str, Any]:
        self.validate()
        payload = {"action": self.action, "path": self.path}
        if self.content is not None:
            payload["content"] = self.content
        if self.expected_sha256:
            payload["expected_sha256"] = self.expected_sha256
        return payload


@dataclass
class ExecutionRequest:
    text: str
    project_id: str | None = None
    operations: list[Operation] = field(default_factory=list)
    checks: list[str] = field(default_factory=list)
    approved: bool = False
    dry_run: bool = False
    idempotency_key: str | None = None
    request_id: str = field(default_factory=lambda: f"req_{uuid.uuid4().hex[:12]}")

    def validate(self) -> None:
        if not self.text.strip() and not self.operations:
            raise ValueError("text or operations are required")
        if len(self.text) > 100_000:
            raise ValueError("request text is too large")
        if len(self.operations) > 50:
            raise ValueError("too many operations")
        if len(self.checks) > 50:
            raise ValueError("too many checks")
        for operation in self.operations:
            operation.validate()

    def idempotency(self) -> str:
        if self.idempotency_key:
            return self.idempotency_key
        payload = {
            "project_id": self.project_id,
            "text": self.text,
            "operations": [asdict(o) for o in self.operations],
            "checks": self.checks,
            "approved": self.approved,
            "dry_run": self.dry_run,
        }
        return hashlib.sha256(json.dumps(payload, sort_keys=True, ensure_ascii=False).encode("utf-8")).hexdigest()
