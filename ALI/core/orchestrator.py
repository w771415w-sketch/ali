from __future__ import annotations

from pathlib import Path
from typing import Any

from .config import RuntimeConfig
from .contracts import ExecutionRequest
from .health import snapshot
from .storage import AuditStore
from ..integrations.control_plane import ControlPlaneAdapter


class Orchestrator:
    """Single public runtime facade for UI, CLI and local HTTP clients."""

    def __init__(self, config: RuntimeConfig, repo_root: Path):
        self.config = config
        self.repo_root = repo_root.resolve()
        self.store = AuditStore(config.workspace)
        self.backend = ControlPlaneAdapter(
            self.repo_root,
            config.backend_module,
            config.backend_class,
            config.workspace,
            hardware=config.hardware,
        )

    def health(self) -> dict[str, Any]:
        base = snapshot(self.config.workspace, self.config.backend_module, self.config.backend_class, self.config.hardware)
        base["control_plane"] = self.backend.health()
        return base

    def config_public(self) -> dict[str, Any]:
        return self.config.to_public_dict()

    def prepare(self, text: str, project_id: str | None = None) -> dict[str, Any]:
        result = self.backend.prepare(text, project_id)
        self.store.audit("prepare", "prepare", result.get("status", "ok"), {"project_id": result.get("project_id")})
        return result

    def execute(self, request: ExecutionRequest) -> dict[str, Any]:
        request.validate()
        key = request.idempotency()
        state, cached = self.store.begin(key)
        if state == "complete" and cached is not None:
            return {"ok": True, "status": "idempotent_replay", "result": cached}
        if state == "running":
            return {"ok": False, "status": "already_running"}
        if request.operations and not request.approved and not request.dry_run:
            result = {
                "ok": False,
                "status": "approval_required",
                "request_id": request.request_id,
                "planned_operations": [op.to_backend_dict() for op in request.operations],
            }
            self.store.complete(key, result)
            self.store.audit(request.request_id, "execute", "approval_required")
            return result
        result = self.backend.execute(
            text=request.text,
            project_id=request.project_id,
            operations=[op.to_backend_dict() for op in request.operations],
            checks=request.checks,
            approved=request.approved,
            dry_run=request.dry_run,
            idempotency_key=key,
        )
        self.store.complete(key, result, status="complete" if result.get("ok") else "failed")
        self.store.audit(request.request_id, "execute", result.get("status", "unknown"), {"ok": result.get("ok")})
        return result

    def diagnose(self, kind: str, path: str) -> dict[str, Any]:
        if kind not in {"file", "archive", "project"}:
            raise ValueError("unsupported diagnosis kind")
        return self.backend.diagnose(kind, path)

    def close(self) -> None:
        self.backend.close()
        self.store.close()
