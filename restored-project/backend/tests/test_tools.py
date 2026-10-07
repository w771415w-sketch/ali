# -*- coding: utf-8 -*-
"""اختبارات V0.4 — Tools + ToolRegistry."""

from __future__ import annotations

import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def _make_ctx(tmpdir: Path, perm_mode: str = "default"):
    from core.context import ConversationContext
    return ConversationContext(
        thread_id="t_test",
        project_dir=str(tmpdir),
        perm_mode=perm_mode,
    )


def test_registry_default_set():
    from tools.registry import get_registry, reset_registry_for_tests
    reset_registry_for_tests()
    reg = get_registry()
    names = reg.names()
    # يجب أن تكون كل الأدوات الأساسية موجودة
    for required in ("read_file", "list_dir", "write_file", "search_files",
                     "run_command", "git_status", "git_diff", "git_commit"):
        assert required in names, f"missing tool: {required}"


def test_read_file_tool(tmp_path):
    (tmp_path / "hello.txt").write_text("مرحبا ALI", encoding="utf-8")
    from tools.filesystem import ReadFileTool
    ctx = _make_ctx(tmp_path)
    res = ReadFileTool().execute(ctx, path="hello.txt")
    assert res.ok
    assert "مرحبا ALI" in res.data["content"]


def test_read_file_blocks_escape(tmp_path):
    from tools.filesystem import ReadFileTool
    ctx = _make_ctx(tmp_path)
    res = ReadFileTool().execute(ctx, path="../../../etc/passwd")
    assert not res.ok
    assert res.error_code == "PATH_BLOCKED"


def test_write_file_tool(tmp_path):
    from tools.filesystem import WriteFileTool
    ctx = _make_ctx(tmp_path)
    res = WriteFileTool().execute(
        ctx, path="out.py", content="print('ok')\n"
    )
    assert res.ok
    assert (tmp_path / "out.py").exists()
    assert "print" in (tmp_path / "out.py").read_text(encoding="utf-8")


def test_list_dir_tool(tmp_path):
    (tmp_path / "a.txt").write_text("a")
    (tmp_path / "sub").mkdir()
    from tools.filesystem import ListDirTool
    ctx = _make_ctx(tmp_path)
    res = ListDirTool().execute(ctx, path="")
    assert res.ok
    names = {e["name"] for e in res.data["entries"]}
    assert "a.txt" in names
    assert "sub" in names


def test_search_files_tool(tmp_path):
    (tmp_path / "a.py").write_text("hello world\nimport os\n")
    (tmp_path / "b.py").write_text("hello there\n")
    from tools.filesystem import SearchFilesTool
    ctx = _make_ctx(tmp_path)
    res = SearchFilesTool().execute(ctx, pattern=r"import os")
    assert res.ok
    assert any("a.py" in m["path"] for m in res.data["matches"])


def test_run_command_blocks_dangerous(tmp_path):
    from tools.terminal import RunShellTool
    ctx = _make_ctx(tmp_path)
    res = RunShellTool().execute(ctx, command="rm -rf /")
    assert not res.ok
    assert res.error_code == "DENIED"


def test_run_command_denied_in_read_only(tmp_path):
    from tools.terminal import RunShellTool
    ctx = _make_ctx(tmp_path, perm_mode="read-only")
    res = RunShellTool().execute(ctx, command="echo hi")
    assert not res.ok
    assert res.error_code == "DENIED"


def test_run_command_safe_executes(tmp_path):
    from tools.terminal import RunShellTool
    ctx = _make_ctx(tmp_path)
    res = RunShellTool().execute(ctx, command="echo hello")
    assert res.ok
    assert "hello" in res.data["stdout"]


def test_registry_unknown_tool(tmp_path):
    from tools.registry import get_registry, reset_registry_for_tests
    reset_registry_for_tests()
    reg = get_registry()
    res = reg.execute("nonexistent", _make_ctx(tmp_path))
    assert not res.ok
    assert res.error_code == "UNKNOWN_TOOL"


def test_registry_executes_through_pm(tmp_path):
    """Tool بصلاحية READ_ONLY يعمل في default بدون سؤال."""
    from tools.registry import get_registry, reset_registry_for_tests
    from security.permissions import PermissionManager
    reset_registry_for_tests()
    reg = get_registry()
    reg.set_permission_manager(PermissionManager(mode="default"))
    (tmp_path / "x.txt").write_text("ok")
    res = reg.execute("read_file", _make_ctx(tmp_path), path="x.txt")
    assert res.ok
