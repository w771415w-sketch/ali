import tempfile
import unittest
from pathlib import Path

from ALI.core.storage import AuditStore


class StorageTests(unittest.TestCase):
    def test_idempotency_lifecycle(self):
        with tempfile.TemporaryDirectory() as td:
            store = AuditStore(Path(td))
            self.assertEqual(store.begin("x")[0], "claimed")
            result = {"ok": True}
            store.complete("x", result)
            state, cached = store.begin("x")
            self.assertEqual(state, "complete")
            self.assertEqual(cached, result)
            store.close()


if __name__ == "__main__":
    unittest.main()
