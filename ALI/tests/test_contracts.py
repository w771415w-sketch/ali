import unittest

from ALI.core.contracts import ExecutionRequest, Operation


class ContractTests(unittest.TestCase):
    def test_idempotency_is_stable(self):
        a = ExecutionRequest("hello", operations=[Operation("write", "a.txt", "x")])
        b = ExecutionRequest("hello", operations=[Operation("write", "a.txt", "x")])
        self.assertEqual(a.idempotency(), b.idempotency())

    def test_invalid_action_rejected(self):
        with self.assertRaises(ValueError):
            Operation("shell", "a.txt", "x").validate()


if __name__ == "__main__":
    unittest.main()
