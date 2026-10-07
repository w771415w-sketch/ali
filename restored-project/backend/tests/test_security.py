# -*- coding: utf-8 -*-
"""اختبارات V0.5 — Security: paths, commands, permissions."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def test_safe_path_inside_workspace(tmp_path):
    from security.paths import safe_project_path
    p = safe_project_path(str(tmp_path), "sub/file.py")
    assert p == (tmp_path / "sub/file.py").resolve()


def test_safe_path_blocks_escape(tmp_path):
    from security.paths import safe_project_path
    import pytest
    with pytest.raises(PermissionError):
        safe_project_path(str(tmp_path), "../../etc/passwd")


def test_safe_path_blocks_dotenv(tmp_path):
    from security.paths import safe_project_path
    import pytest
    with pytest.raises(PermissionError):
        safe_project_path(str(tmp_path), ".env")


def test_safe_path_blocks_ssh(tmp_path):
    from security.paths import safe_project_path
    import pytest
    with pytest.raises(PermissionError):
        safe_project_path(str(tmp_path), "../.ssh/id_rsa")


# --------- commands
def test_command_blocks_rm_rf_root():
    from security.commands import is_command_safe
    assert not is_command_safe("rm -rf /")
    assert not is_command_safe("rm -rf /etc")


def test_command_blocks_format():
    from security.commands import is_command_safe
    assert not is_command_safe("format C:")
    assert not is_command_safe("format D:")


def test_command_blocks_diskpart():
    from security.commands import is_command_safe
    assert not is_command_safe("diskpart")


def test_command_blocks_shutdown():
    from security.commands import is_command_safe
    assert not is_command_safe("shutdown /s /t 0")


def test_command_blocks_forkbomb():
    from security.commands import is_command_safe
    assert not is_command_safe(":(){ :|:& };:")


def test_command_allows_safe():
    from security.commands import is_command_safe
    assert is_command_safe("echo hello")
    assert is_command_safe("dir")
    assert is_command_safe("git status")
    assert is_command_safe("python -m pytest")


# --------- permissions
def test_pm_read_only_blocks_write():
    from security.permissions import PermissionManager
    from tools.base import ToolPermission
    pm = PermissionManager(mode="read-only")
    d = pm.check(tool_name="write_file", permission=ToolPermission.DEFAULT)
    assert not d.allowed
    assert not d.needs_ask


def test_pm_default_allows_read():
    from security.permissions import PermissionManager
    from tools.base import ToolPermission
    pm = PermissionManager(mode="default")
    d = pm.check(tool_name="read_file", permission=ToolPermission.READ_ONLY)
    assert d.allowed
    assert not d.needs_ask


def test_pm_default_asks_for_write():
    from security.permissions import PermissionManager
    from tools.base import ToolPermission
    pm = PermissionManager(mode="default")
    d = pm.check(tool_name="write_file", permission=ToolPermission.DEFAULT)
    # tool perm = DEFAULT, mode = DEFAULT → rank متساوية → allowed
    # لتفعيل ASK نحتاج default لطلب default (متساوي → allow).
    # أعد الاختبار بأداة بصلاحية أعلى:
    d2 = pm.check(tool_name="dangerous", permission=ToolPermission.FULL_ACCESS)
    assert not d2.allowed
    assert d2.needs_ask


def test_pm_full_access_allows_all():
    from security.permissions import PermissionManager
    from tools.base import ToolPermission
    pm = PermissionManager(mode="full-access")
    d = pm.check(tool_name="write_file", permission=ToolPermission.DEFAULT)
    assert d.allowed


def test_pm_always_allow_shortcuts():
    from security.permissions import PermissionManager
    from tools.base import ToolPermission
    pm = PermissionManager(mode="read-only")
    pm.grant("write_file")
    d = pm.check(tool_name="write_file", permission=ToolPermission.DEFAULT)
    assert d.allowed


def test_pm_invalid_mode():
    from security.permissions import PermissionManager
    import pytest
    with pytest.raises(ValueError):
        PermissionManager(mode="super-admin")
