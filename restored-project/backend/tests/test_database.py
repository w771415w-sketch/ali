# -*- coding: utf-8 -*-
"""اختبار V0.2 Database: migrations + repos."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import pytest

import database.database as db_mod
import database.schema as schema_mod


@pytest.fixture
def fresh_db(tmp_path):
    """يوفّر instance معزولة من Database لكل اختبار."""
    p = tmp_path / "ali.db"
    db = db_mod.Database.__new__(db_mod.Database)
    db.__init__(p)
    yield db


def test_bootstrap_creates_schema(fresh_db):
    h = fresh_db.healthcheck()
    assert h["schema_version"] == schema_mod.SCHEMA_VERSION
    assert h["journal_mode"].lower() == "wal"
    assert h["foreign_keys"] is True


def test_required_tables_exist(fresh_db):
    required = {
        "meta", "projects", "threads", "messages",
        "settings", "logs", "tool_calls", "sessions",
    }
    with fresh_db.cursor() as cur:
        rows = cur.execute(
            "SELECT name FROM sqlite_master WHERE type='table';"
        ).fetchall()
        names = {r["name"] for r in rows}
    missing = required - names
    assert not missing, "missing tables: " + str(missing)


def test_indexes_exist(fresh_db):
    with fresh_db.cursor() as cur:
        rows = cur.execute(
            "SELECT name FROM sqlite_master WHERE type='index';"
        ).fetchall()
        names = {r["name"] for r in rows}
    for idx in ("idx_threads_project", "idx_messages_thread",
                "idx_tool_calls_thread", "idx_logs_ts"):
        assert idx in names, "missing index: " + idx


def test_project_repo_crud(fresh_db):
    repo = db_mod.ProjectRepo(fresh_db)
    pid = repo.create("ALI", str(ROOT))
    assert pid.startswith("p_")
    p = repo.get(pid)
    assert p["name"] == "ALI"
    assert repo.by_path(str(ROOT)) is not None
    repo.touch(pid)
    assert repo.list_recent()[0]["id"] == pid


def test_thread_repo_lifecycle(fresh_db):
    projects = db_mod.ProjectRepo(fresh_db)
    pid = projects.create("ALI", str(ROOT))
    threads = db_mod.ThreadRepo(fresh_db)
    tid = threads.create(pid, "Test")
    threads.rename(tid, "Renamed")
    t = threads.get(tid)
    assert t["title"] == "Renamed"
    threads.touch(tid)


def test_message_repo(fresh_db):
    projects = db_mod.ProjectRepo(fresh_db)
    threads = db_mod.ThreadRepo(fresh_db)
    messages = db_mod.MessageRepo(fresh_db)
    pid = projects.create("ALI", str(ROOT))
    tid = threads.create(pid)
    messages.add(tid, "user", "hi")
    messages.add(tid, "assistant", "hello")
    msgs = messages.list_for_thread(tid)
    assert len(msgs) == 2
    assert msgs[0]["role"] == "user"
    assert msgs[1]["role"] == "assistant"
    assert messages.count(tid) == 2


def test_settings_repo(fresh_db):
    s = db_mod.SettingsRepo(fresh_db)
    s.set("perm_mode", "default")
    assert s.get("perm_mode") == "default"
    s.set("perm_mode", "read-only")
    assert s.get("perm_mode") == "read-only"
    assert s.all()["perm_mode"] == "read-only"


def test_tool_call_repo(fresh_db):
    tc = db_mod.ToolCallRepo(fresh_db)
    cid = tc.start(None, None, "read_file", {"path": "x.py"})
    tc.finish(cid, "ok", {"content": "hello"})
    rows = tc.recent()
    assert rows[0]["status"] == "ok"
    assert rows[0]["tool_name"] == "read_file"


def test_log_repo(fresh_db):
    lr = db_mod.LogRepo(fresh_db)
    lr.add("INFO", "test", "hello")
    lr.add("ERROR", "test", "boom")
    rows = lr.recent()
    assert len(rows) == 2
    # حذف كل ما عمره أقل من ثانية واحدة (يضمن حذف السجلات التي أُضيفت الآن)
    deleted = lr.prune_older_than(-1)
    assert deleted >= 2


def test_migration_is_idempotent(tmp_path):
    """فتح نفس DB مرتين يجب ألا يعيد تشغيل migrations."""
    p = tmp_path / "ali.db"
    db1 = db_mod.Database.__new__(db_mod.Database)
    db1.__init__(p)
    v1 = db1.get_meta("schema_version")
    # إعادة الفتح على نفس المسار
    db_mod._BOOTSTRAPPED.discard(str(p))
    db2 = db_mod.Database.__new__(db_mod.Database)
    db2.__init__(p)
    v2 = db2.get_meta("schema_version")
    assert v1 == v2
    assert int(v1) == schema_mod.SCHEMA_VERSION
