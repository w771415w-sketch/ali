import tempfile
import unittest
from pathlib import Path

from ALI.core.health import snapshot


class HealthTests(unittest.TestCase):
    def test_health_contains_workspace_and_backend(self):
        with tempfile.TemporaryDirectory() as td:
            data = snapshot(Path(td), "missing.module", "Missing", {"profile": "test"})
            self.assertTrue(data["ok"])
            self.assertIn("workspace", data)
            self.assertFalse(data["backend"]["available"])


if __name__ == "__main__":
    unittest.main()
