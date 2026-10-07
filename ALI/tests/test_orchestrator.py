import tempfile
import unittest
from pathlib import Path

from ALI.core.config import RuntimeConfig
from ALI.core.contracts import ExecutionRequest, Operation
from ALI.core.orchestrator import Orchestrator


class OrchestratorTests(unittest.TestCase):
    def _runtime(self, td):
        cfg = RuntimeConfig(
            host="127.0.0.1", port=8787, allow_remote=False, api_token="", workspace=Path(td),
            max_body_bytes=1048576, rate_limit=60, rate_window_seconds=60,
            backend_module="missing.module", backend_class="Missing", hardware={"profile": "test"},
        )
        return Orchestrator(cfg, Path(td))

    def test_approval_boundary(self):
        with tempfile.TemporaryDirectory() as td:
            rt = self._runtime(td)
            result = rt.execute(ExecutionRequest("change", operations=[Operation("write", "x.txt", "x")]))
            self.assertEqual(result["status"], "approval_required")
            rt.close()

    def test_idempotency_key_is_stable_for_retries(self):
        a = ExecutionRequest("inspect", dry_run=True, idempotency_key="same")
        b = ExecutionRequest("inspect", dry_run=True, idempotency_key="same")
        self.assertEqual(a.idempotency(), b.idempotency())


if __name__ == "__main__":
    unittest.main()
