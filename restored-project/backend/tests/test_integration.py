# -*- coding: utf-8 -*-
"""اختبار Integration: Tools + Registry + PermissionManager + Context معاً."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def _setup(tmp_path):
    from core.context import ConversationContext
    from security.permissions import PermissionManager
    from tools.registry import get_registry, reset_registry_for_tests
    reset_registry_for_tests()
    reg = get_registry()
    pm = PermissionManager(mode="default")
    # Simulate the user approval that the production UI must obtain before
    # write/commit actions. Default mode must never auto-allow them.
    pm.grant("write_file", session=True)
    pm.grant("git_commit", session=True)
    reg.set_permission_manager(pm)
    ctx = ConversationContext(
        thread_id="t_int", project_dir=str(tmp_path), perm_mode="default",
    )
    return reg, ctx


def test_integration_read_then_write(tmp_path):
    reg, ctx = _setup(tmp_path)
    # 1) write
    r = reg.execute("write_file", ctx, path="hello.txt", content="ALI")
    assert r.ok, r.error
    assert (tmp_path / "hello.txt").exists()
    # 2) read back
    r = reg.execute("read_file", ctx, path="hello.txt")
    assert r.ok
    assert r.data["content"] == "ALI"


def test_integration_read_only_mode_blocks_write(tmp_path):
    reg, ctx = _setup(tmp_path)
    ctx.perm_mode = "read-only"
    r = reg.execute("write_file", ctx, path="x.txt", content="nope")
    assert not r.ok
    assert r.error_code == "DENIED"
    # لكن read مسموح
    (tmp_path / "x.txt").write_text("ok")
    r = reg.execute("read_file", ctx, path="x.txt")
    assert r.ok


def test_integration_path_blocked(tmp_path):
    reg, ctx = _setup(tmp_path)
    r = reg.execute("read_file", ctx, path="../../etc/passwd")
    assert not r.ok
    assert r.error_code == "PATH_BLOCKED"


def test_integration_dangerous_command(tmp_path):
    reg, ctx = _setup(tmp_path)
    r = reg.execute("run_command", ctx, command="rm -rf /")
    assert not r.ok
    assert r.error_code == "DENIED"


def test_integration_full_access_allows_all(tmp_path):
    reg, ctx = _setup(tmp_path)
    ctx.perm_mode = "full-access"
    r = reg.execute("write_file", ctx, path="ok.txt", content="ok")
    assert r.ok


def test_integration_git_tools(tmp_path):
    reg, ctx = _setup(tmp_path)
    # تهيئة git repo بسيط
    import subprocess
    subprocess.run(["git", "init"], cwd=str(tmp_path), capture_output=True,
                   creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
    subprocess.run(["git", "config", "user.email", "test@x"],
                   cwd=str(tmp_path), capture_output=True,
                   creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
    subprocess.run(["git", "config", "user.name", "test"],
                   cwd=str(tmp_path), capture_output=True,
                   creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
    (tmp_path / "f.txt").write_text("x")
    # status
    r = reg.execute("git_status", ctx)
    assert r.ok
    # commit
    r = reg.execute("git_commit", ctx, message="init", add_all=True)
    assert r.ok
    assert r.data["code"] == 0
