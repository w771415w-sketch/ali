from __future__ import annotations

import importlib
import sys
from pathlib import Path
from typing import Any


class ControlPlaneAdapter:
    """Lazy bridge to the repository's existing professional control plane."""

    def __init__(self, repo_root: Path, module: str, class_name: str, workspace: Path, hardware: dict[str, Any] | None = None):
        self.repo_root = repo_root.resolve()
        self.module = module
        self.class_name = class_name
        self.workspace = workspace.resolve()
        self.hardware = hardware or {}
        self.runtime = None
        self.error: str | None = None

    def connect(self) -> bool:
        if self.runtime is not None:
            return True
        if str(self.repo_root) not in sys.path:
            sys.path.insert(0, str(self.repo_root))
        try:
            mod = importlib.import_module(self.module)
            cls = getattr(mod, self.class_name)
            try:
                self.runtime = cls(self.workspace, hardware=self.hardware)
            except TypeError:
                self.runtime = cls(self.workspace)
            return True
        except Exception as exc:
            self.error = f"{type(exc).__name__}: {exc}"
            return False

    @property
    def available(self) -> bool:
        return self.runtime is not None or self.connect()

    def health(self) -> dict[str, Any]:
        if not self.connect():
            return {"available": False, "error": self.error, "repo_root": str(self.repo_root)}
        try:
            return {"available": True, "runtime": self.runtime.health()}
        except Exception as exc:
            return {"available": False, "error": f"health:{type(exc).__name__}: {exc}"}

    def prepare(self, text: str, project_id: str | None = None) -> dict[str, Any]:
        if not self.connect():
            return {"ok": False, "status": "control_plane_unavailable", "error": self.error}
        return self.runtime.prepare(text, project_id)

    def execute(self, *, text: str, project_id: str | None, operations: list[dict[str, Any]], checks: list[str], approved: bool, dry_run: bool, idempotency_key: str) -> dict[str, Any]:
        if not self.connect():
            return {"ok": False, "status": "control_plane_unavailable", "error": self.error}
        return self.runtime.execute(
            text,
            project_id=project_id,
            operations=operations,
            checks=checks,
            approved=approved,
            dry_run=dry_run,
            idempotency_key=idempotency_key,
        )

    def diagnose(self, kind: str, path: str) -> dict[str, Any]:
        if not self.connect():
            return {"ok": False, "status": "control_plane_unavailable", "error": self.error}
        funcs = {"file": "diagnose_file", "archive": "diagnose_archive", "project": "diagnose_project"}
        fn = getattr(self.runtime, funcs[kind])
        return fn(path)

    def close(self) -> None:
        if self.runtime is not None and hasattr(self.runtime, "close"):
            self.runtime.close()
