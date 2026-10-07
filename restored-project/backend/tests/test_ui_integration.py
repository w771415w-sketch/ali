# -*- coding: utf-8 -*-
"""اختبار V0.6 — ربط الواجهة بالـ Tools والـ PermissionManager.

يختبر منطق الـ dispatch + run_tool_with_ui عبر تشغيل الـ App في وضع headless
وفحص:
- dispatcher يختار الأداة الصحيحة.
- permission dialog يُسأل عند الحاجة (في الاختبار نتجاوزه مباشرة).
- tool يُنفّذ فعلياً.
- audit row يُكتب في DB.
- reply string يحتوي على علامة النجاح أو الفشل.
"""

from __future__ import annotations

import sys
import os
import pytest
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

pytestmark = pytest.mark.skipif(os.name != "nt" and os.environ.get("ALI_GUI_TESTS") != "1", reason="Desktop GUI unavailable in headless environment")
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def _make_app_with_workdir():
    """يبني App مع مجلد عمل مؤقت + APPDATA معزولة."""
    try:
        import tkinter as tk
    except Exception:
        import pytest
        pytest.skip("tkinter unavailable")

    # إعادة تعيين singletons لأنهم قد يحتفظون بـ db_path من تشغيل سابق.
    from tools.registry import reset_registry_for_tests
    from security.permissions import reset_permission_manager_for_tests
    reset_registry_for_tests()
    reset_permission_manager_for_tests()

    tmp = Path(tempfile.mkdtemp(prefix="ali_v06_"))
    proj = tmp / "workspace"
    proj.mkdir()
    (proj / "hello.txt").write_text("ali", encoding="utf-8")

    import os
    appdata = tmp / "appdata"
    appdata.mkdir()
    os.environ["APPDATA"] = str(appdata)

    from database.database import reset_database_for_tests
    reset_database_for_tests()

    # لا حاجة لإنشاء Tk root فعلي لاختبارات dispatcher — الـ App
    # تلامس tk widgets فقط عند build()، والـ dispatcher لا يحتاج Tk.
    # لكن `_db()` يستخدم lazy import، و App.perm_mode يحتاج StringVar (Tk).
    # لذلك نستخدم Tk() ونلتقط أي خطأ Tcl متأخر.
    from ali_agent import App
    try:
        root = tk.Tk()
        app = App(root)
    except Exception:
        # بعض بيئات الاختبار (Hermes) تكسر Tcl عند إعادة التهيئة.
        import pytest as _pt
        _pt.skip("Tcl/Tk init failed in this environment")
    app.project_dir = str(proj)
    app.cfg["last_dir"] = str(proj)
    return app, root, proj


def test_dispatcher_routes_read_file():
    from ali_agent import App
    app, root, _ = _make_app_with_workdir()
    try:
        d = app._dispatch_tool("read_file hello.txt")
        assert d is not None
        name, kwargs, _ = d
        assert name == "read_file"
        assert kwargs["path"] == "hello.txt"
    finally:
        root.destroy()


def test_dispatcher_routes_git_status():
    from ali_agent import App
    app, root, _ = _make_app_with_workdir()
    try:
        d = app._dispatch_tool("git status")
        assert d[0] == "git_status"
    finally:
        root.destroy()


def test_dispatcher_routes_run_command():
    from ali_agent import App
    app, root, _ = _make_app_with_workdir()
    try:
        d = app._dispatch_tool("run_command echo ali")
        assert d is not None
        assert d[0] == "run_command"
        assert d[1]["command"] == "echo ali"
    finally:
        root.destroy()


def test_dispatcher_no_match():
    from ali_agent import App
    app, root, _ = _make_app_with_workdir()
    try:
        assert app._dispatch_tool("hello how are you") is None
    finally:
        root.destroy()


def test_local_reply_routes_to_tool():
    """اكتب read_file داخل workspace → يجب أن يعرض رسالة نجاح وأداة."""
    from ali_agent import App
    app, root, proj = _make_app_with_workdir()
    try:
        app.perm_mode.set("full-access")    # لتجاوز الـ dialog
        root.update_idletasks()
        reply = app._local_reply("read_file hello.txt")
        assert "نجح" in reply or "✅" in reply, reply
        # تأكد من كتابة audit row
        from database.database import get_db, ToolCallRepo
        repo = ToolCallRepo(get_db())
        rows = repo.recent(limit=5)
        assert any(r["tool_name"] == "read_file" for r in rows), rows
    finally:
        root.destroy()


def test_local_reply_shows_tool_list_when_no_match():
    from ali_agent import App
    app, root, _ = _make_app_with_workdir()
    try:
        reply = app._local_reply("hello there")
        assert "read_file" in reply and "git_status" in reply
    finally:
        root.destroy()


def test_local_reply_blocks_dangerous_command():
    from ali_agent import App
    app, root, _ = _make_app_with_workdir()
    try:
        app.perm_mode.set("full-access")   # حتى full-access لا يتجاوز command blacklist
        reply = app._local_reply("run_command rm -rf /")
        assert "فشل" in reply or "⚠" in reply
    finally:
        root.destroy()


def test_local_reply_read_only_blocks_write():
    """write_file بصلاحية default في read-only → رفض."""
    from ali_agent import App
    app, root, _ = _make_app_with_workdir()
    try:
        app.perm_mode.set("read-only")
        reply = app._local_reply("write_file out.txt")
        # dispatcher يحتاج مسار، نعطيه مساراً
        reply = app._local_reply("write_file sub/x.txt")
        assert "فشل" in reply or "رفض" in reply or "⚠" in reply
    finally:
        root.destroy()
