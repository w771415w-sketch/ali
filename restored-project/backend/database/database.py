# -*- coding: utf-8 -*-
"""طبقة قاعدة البيانات V0.2.

- SQLite + WAL للسرعة على Windows.
- thread-safe عبر check_same_thread=False + per-thread connection + lock.
- Migrations حقيقية مسجلة في database.schema.
- جداول: projects, threads, messages, tool_calls, settings, logs, sessions.
- Repositories بسيطة (ProjectRepo, ThreadRepo, MessageRepo).
"""

from __future__ import annotations

import sqlite3
import threading
import time
import uuid
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Iterable, List, Optional, Sequence

from config.paths import APP_PATHS
from core.logger import get_logger
from database.schema import ALL_MIGRATIONS, SCHEMA_VERSION

log = get_logger("db")

# قفل عام لتأمين كتابة schema مرة واحدة.
_BOOTSTRAP_LOCK = threading.Lock()
_BOOTSTRAPPED: set = set()


# ---------------------------------------------------------------------------
# Database core
# ---------------------------------------------------------------------------
class Database:
    """طبقة قاعدة بيانات بسيطة. Singleton داخل العملية."""

    _instance: "Optional[Database]" = None
    _instance_lock = threading.Lock()

    def __init__(self, db_path: Optional[Path] = None):
        self.db_path = db_path or (APP_PATHS.user_data_dir() / "ali.db")
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._local = threading.local()
        # أول thread يبدأ الـ bootstrap.
        self._bootstrap()

    # --------------------------------------------------------------- singleton
    @classmethod
    def instance(cls) -> "Database":
        with cls._instance_lock:
            if cls._instance is None:
                cls._instance = Database()
            return cls._instance

    # --------------------------------------------------------------- connection
    def _conn(self) -> sqlite3.Connection:
        c = getattr(self._local, "conn", None)
        if c is None:
            c = sqlite3.connect(
                str(self.db_path),
                check_same_thread=False,
                isolation_level=None,
                timeout=5.0,
            )
            c.row_factory = sqlite3.Row
            c.execute("PRAGMA journal_mode=WAL;")
            c.execute("PRAGMA synchronous=NORMAL;")
            c.execute("PRAGMA foreign_keys=ON;")
            self._local.conn = c
        return c

    @contextmanager
    def tx(self):
        c = self._conn()
        c.execute("BEGIN;")
        try:
            yield c
            c.execute("COMMIT;")
        except Exception:
            c.execute("ROLLBACK;")
            raise

    @contextmanager
    def cursor(self):
        c = self._conn()
        cur = c.cursor()
        try:
            yield cur
        finally:
            cur.close()

    # --------------------------------------------------------------- bootstrap
    def _bootstrap(self) -> None:
        """إنشاء جدول meta + تشغيل migrations."""
        # أول bootstrap فقط في العالم (لكل db_path)
        key = str(self.db_path)
        if key in _BOOTSTRAPPED:
            return
        with _BOOTSTRAP_LOCK:
            if key in _BOOTSTRAPPED:
                return
            c = self._conn()
            c.execute("""
                CREATE TABLE IF NOT EXISTS meta (
                    key   TEXT PRIMARY KEY,
                    value TEXT NOT NULL
                );
            """)
            c.execute(
                "INSERT OR IGNORE INTO meta(key, value) "
                "VALUES('schema_version', '0');"
            )
            current = int(c.execute(
                "SELECT value FROM meta WHERE key='schema_version';"
            ).fetchone()[0])
            log.info("DB bootstrap at %s (current schema_version=%d)",
                     self.db_path, current)
            for v, fn in ALL_MIGRATIONS:
                if v > current:
                    log.info("Applying migration %d", v)
                    c.execute("BEGIN;")
                    try:
                        fn(c)
                        c.execute(
                            "INSERT OR REPLACE INTO meta(key, value) "
                            "VALUES('schema_version', ?);",
                            (str(v),),
                        )
                        c.execute("COMMIT;")
                    except Exception as e:
                        c.execute("ROLLBACK;")
                        log.error("Migration %d failed: %s", v, e)
                        raise
            _BOOTSTRAPPED.add(key)

    # --------------------------------------------------------------- helpers
    def get_meta(self, key: str, default: Optional[str] = None) -> Optional[str]:
        with self.cursor() as cur:
            row = cur.execute(
                "SELECT value FROM meta WHERE key=?;", (key,)
            ).fetchone()
            return row["value"] if row else default

    def set_meta(self, key: str, value: str) -> None:
        with self.tx() as c:
            c.execute(
                "INSERT INTO meta(key, value) VALUES(?, ?) "
                "ON CONFLICT(key) DO UPDATE SET value=excluded.value;",
                (key, value),
            )

    def healthcheck(self) -> dict:
        with self.cursor() as cur:
            row = cur.execute("PRAGMA journal_mode;").fetchone()
            row2 = cur.execute("PRAGMA foreign_keys;").fetchone()
            sv = cur.execute(
                "SELECT value FROM meta WHERE key='schema_version';"
            ).fetchone()
            return {
                "path": str(self.db_path),
                "journal_mode": row[0] if row else "?",
                "foreign_keys": bool(row2[0]) if row2 else False,
                "schema_version": int(sv[0]) if sv else 0,
            }


def get_db() -> Database:
    return Database.instance()


def reset_database_for_tests() -> None:
    """إعادة تعيين الـ singleton (للاختبارات فقط)."""
    global _BOOTSTRAPPED
    Database._instance = None
    _BOOTSTRAPPED.clear()


# ---------------------------------------------------------------------------
# Repository: projects
# ---------------------------------------------------------------------------
class ProjectRepo:
    def __init__(self, db: Database):
        self.db = db

    def create(self, name: str, root_path: str) -> str:
        pid = "p_" + uuid.uuid4().hex[:12]
        now = time.time()
        with self.db.tx() as c:
            c.execute(
                "INSERT INTO projects(id, name, root_path, "
                "created_at, updated_at) VALUES(?, ?, ?, ?, ?);",
                (pid, name, root_path, now, now),
            )
        return pid

    def get(self, pid: str) -> Optional[dict]:
        with self.db.cursor() as cur:
            row = cur.execute(
                "SELECT * FROM projects WHERE id=?;", (pid,)
            ).fetchone()
            return dict(row) if row else None

    def by_path(self, root_path: str) -> Optional[dict]:
        with self.db.cursor() as cur:
            row = cur.execute(
                "SELECT * FROM projects WHERE root_path=? "
                "ORDER BY updated_at DESC LIMIT 1;",
                (root_path,),
            ).fetchone()
            return dict(row) if row else None

    def touch(self, pid: str) -> None:
        with self.db.tx() as c:
            c.execute(
                "UPDATE projects SET updated_at=? WHERE id=?;",
                (time.time(), pid),
            )

    def list_recent(self, limit: int = 20) -> List[dict]:
        with self.db.cursor() as cur:
            rows = cur.execute(
                "SELECT * FROM projects ORDER BY updated_at DESC LIMIT ?;",
                (limit,),
            ).fetchall()
            return [dict(r) for r in rows]


# ---------------------------------------------------------------------------
# Repository: threads
# ---------------------------------------------------------------------------
class ThreadRepo:
    def __init__(self, db: Database):
        self.db = db

    def create(self, project_id: Optional[str], title: str = "New thread") -> str:
        tid = "t_" + uuid.uuid4().hex[:12]
        now = time.time()
        with self.db.tx() as c:
            c.execute(
                "INSERT INTO threads(id, project_id, title, "
                "created_at, updated_at) VALUES(?, ?, ?, ?, ?);",
                (tid, project_id, title, now, now),
            )
        return tid

    def rename(self, tid: str, title: str) -> None:
        with self.db.tx() as c:
            c.execute(
                "UPDATE threads SET title=?, updated_at=? WHERE id=?;",
                (title, time.time(), tid),
            )

    def get(self, tid: str) -> Optional[dict]:
        with self.db.cursor() as cur:
            row = cur.execute(
                "SELECT * FROM threads WHERE id=?;", (tid,)
            ).fetchone()
            return dict(row) if row else None

    def list_for_project(self, project_id: str, limit: int = 50) -> List[dict]:
        with self.db.cursor() as cur:
            rows = cur.execute(
                "SELECT * FROM threads WHERE project_id=? "
                "ORDER BY updated_at DESC LIMIT ?;",
                (project_id, limit),
            ).fetchall()
            return [dict(r) for r in rows]

    def list_all(self, limit: int = 50) -> List[dict]:
        with self.db.cursor() as cur:
            rows = cur.execute(
                "SELECT * FROM threads ORDER BY updated_at DESC LIMIT ?;",
                (limit,),
            ).fetchall()
            return [dict(r) for r in rows]

    def touch(self, tid: str) -> None:
        with self.db.tx() as c:
            c.execute(
                "UPDATE threads SET updated_at=? WHERE id=?;",
                (time.time(), tid),
            )

    def delete(self, tid: str) -> None:
        with self.db.tx() as c:
            c.execute("DELETE FROM threads WHERE id=?;", (tid,))


# ---------------------------------------------------------------------------
# Repository: messages
# ---------------------------------------------------------------------------
class MessageRepo:
    VALID_ROLES = ("user", "assistant", "system", "tool")

    def __init__(self, db: Database):
        self.db = db

    def add(self, thread_id: str, role: str, content: str,
            meta: Optional[dict] = None) -> int:
        if role not in self.VALID_ROLES:
            raise ValueError("invalid role: " + role)
        meta_json = _json_dumps(meta) if meta else None
        with self.db.tx() as c:
            cur = c.execute(
                "INSERT INTO messages(thread_id, role, content, ts, meta_json) "
                "VALUES(?, ?, ?, ?, ?);",
                (thread_id, role, content, time.time(), meta_json),
            )
            c.execute(
                "UPDATE threads SET updated_at=? WHERE id=?;",
                (time.time(), thread_id),
            )
            return cur.lastrowid

    def list_for_thread(self, thread_id: str,
                        limit: int = 500) -> List[dict]:
        with self.db.cursor() as cur:
            rows = cur.execute(
                "SELECT * FROM messages WHERE thread_id=? "
                "ORDER BY ts ASC, id ASC LIMIT ?;",
                (thread_id, limit),
            ).fetchall()
            return [dict(r) for r in rows]

    def delete_for_thread(self, thread_id: str) -> int:
        with self.db.tx() as c:
            cur = c.execute(
                "DELETE FROM messages WHERE thread_id=?;", (thread_id,)
            )
            return cur.rowcount

    def count(self, thread_id: str) -> int:
        with self.db.cursor() as cur:
            row = cur.execute(
                "SELECT COUNT(*) AS c FROM messages WHERE thread_id=?;",
                (thread_id,),
            ).fetchone()
            return int(row["c"]) if row else 0


# ---------------------------------------------------------------------------
# Repository: settings
# ---------------------------------------------------------------------------
class SettingsRepo:
    def __init__(self, db: Database):
        self.db = db

    def get(self, key: str, default: Optional[str] = None) -> Optional[str]:
        with self.db.cursor() as cur:
            row = cur.execute(
                "SELECT value FROM settings WHERE key=?;", (key,)
            ).fetchone()
            return row["value"] if row else default

    def set(self, key: str, value: str) -> None:
        with self.db.tx() as c:
            c.execute(
                "INSERT INTO settings(key, value, updated_at) VALUES(?, ?, ?) "
                "ON CONFLICT(key) DO UPDATE SET value=excluded.value, "
                "updated_at=excluded.updated_at;",
                (key, value, time.time()),
            )

    def all(self) -> dict:
        with self.db.cursor() as cur:
            rows = cur.execute("SELECT key, value FROM settings;").fetchall()
            return {r["key"]: r["value"] for r in rows}


# ---------------------------------------------------------------------------
# Repository: tool_calls
# ---------------------------------------------------------------------------
class ToolCallRepo:
    def __init__(self, db: Database):
        self.db = db

    def start(self, thread_id: Optional[str], message_id: Optional[int],
              tool_name: str, input_data: dict) -> int:
        with self.db.tx() as c:
            cur = c.execute(
                "INSERT INTO tool_calls(thread_id, message_id, tool_name, "
                "input_json, status, started_at) VALUES(?, ?, ?, ?, ?, ?);",
                (thread_id, message_id, tool_name,
                 _json_dumps(input_data), "running", time.time()),
            )
            return cur.lastrowid

    def finish(self, call_id: int, status: str, output: Any = None,
               error: Optional[str] = None) -> None:
        with self.db.tx() as c:
            c.execute(
                "UPDATE tool_calls SET status=?, output_json=?, error=?, "
                "finished_at=? WHERE id=?;",
                (status, _json_dumps(output), error, time.time(), call_id),
            )

    def recent(self, limit: int = 50) -> List[dict]:
        with self.db.cursor() as cur:
            rows = cur.execute(
                "SELECT * FROM tool_calls ORDER BY id DESC LIMIT ?;",
                (limit,),
            ).fetchall()
            return [dict(r) for r in rows]


# ---------------------------------------------------------------------------
# Repository: logs
# ---------------------------------------------------------------------------
class LogRepo:
    def __init__(self, db: Database):
        self.db = db

    def add(self, level: str, logger: str, message: str) -> None:
        # Logs: لا transaction لتفادي overhead.
        c = self.db._conn()
        c.execute(
            "INSERT INTO logs(level, logger, message, ts) VALUES(?, ?, ?, ?);",
            (level, logger, message, time.time()),
        )

    def recent(self, limit: int = 200) -> List[dict]:
        with self.db.cursor() as cur:
            rows = cur.execute(
                "SELECT * FROM logs ORDER BY id DESC LIMIT ?;",
                (limit,),
            ).fetchall()
            return [dict(r) for r in rows]

    def prune_older_than(self, days: int = 30) -> int:
        cutoff = time.time() - days * 86400
        with self.db.tx() as c:
            cur = c.execute("DELETE FROM logs WHERE ts < ?;", (cutoff,))
            return cur.rowcount


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def _json_dumps(obj: Any) -> str:
    import json
    return json.dumps(obj, ensure_ascii=False, separators=(",", ":"))


def json_loads(s: Optional[str]) -> Any:
    if not s:
        return None
    import json
    try:
        return json.loads(s)
    except Exception:
        return None


__all__ = [
    "Database",
    "get_db",
    "ProjectRepo",
    "ThreadRepo",
    "MessageRepo",
    "SettingsRepo",
    "ToolCallRepo",
    "LogRepo",
    "json_loads",
]
