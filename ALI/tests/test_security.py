import unittest
from pathlib import Path

from ALI.core.security import SecurityError, inside, safe_relative_path


class SecurityTests(unittest.TestCase):
    def test_traversal_rejected(self):
        with self.assertRaises(SecurityError):
            safe_relative_path("../secret.txt")

    def test_windows_absolute_rejected(self):
        with self.assertRaises(SecurityError):
            safe_relative_path("C:/secret.txt")

    def test_inside_workspace(self):
        root = Path.cwd() / "test-workspace"
        self.assertEqual(inside(root, "a/b.txt"), (root.resolve() / "a/b.txt").resolve())


if __name__ == "__main__":
    unittest.main()
