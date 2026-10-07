from __future__ import annotations

import json
import tempfile
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from ALI.core.config import load_config
from ALI.core.contracts import ExecutionRequest, Operation
from ALI.core.orchestrator import Orchestrator
from ALI.core.security import SecurityError, safe_relative_path


def run() -> dict[str, object]:
    with tempfile.TemporaryDirectory(prefix="ali-check-") as td:
        cfg_file = Path(td) / "config.json"
        cfg_file.write_text(
            json.dumps(
                {
                    "schema_version": 1,
                    "server": {"host": "127.0.0.1", "port": 8787, "max_body_bytes": 1048576, "request_rate_limit": 60, "request_rate_window_seconds": 60, "remote_access": False},
                    "backend": {"module": "definitely.missing", "class": "Missing"},
                    "hardware": {"profile": "test"},
                }
            ),
            encoding="utf-8",
        )
        old = __import__("os").environ.get("ALI_WORKSPACE")
        __import__("os").environ["ALI_WORKSPACE"] = td
        try:
            cfg = load_config(cfg_file)
            runtime = Orchestrator(cfg, Path(td))
            approval = runtime.execute(ExecutionRequest("build", operations=[Operation("write", "hello.txt", "ALI")]))
            approval_ok = approval["status"] == "approval_required"
            dry = runtime.execute(ExecutionRequest("build", operations=[Operation("write", "hello.txt", "ALI")], dry_run=True))
            dry_ok = dry["status"] in {"dry_run", "control_plane_unavailable"}
            try:
                safe_relative_path("../escape")
                traversal_ok = False
            except SecurityError:
                traversal_ok = True
            runtime.close()
            return {"approval_gate": approval_ok, "dry_run_boundary": dry_ok, "path_traversal_blocked": traversal_ok, "checks_passed": all([approval_ok, dry_ok, traversal_ok])}
        finally:
            if old is None:
                __import__("os").environ.pop("ALI_WORKSPACE", None)
            else:
                __import__("os").environ["ALI_WORKSPACE"] = old


if __name__ == "__main__":
    result = run()
    print(json.dumps(result, ensure_ascii=False, indent=2))
    raise SystemExit(0 if result["checks_passed"] else 1)
