# -*- coding: utf-8 -*-
"""Schema versioning + migration registry.

كل migration هي دالة تأخذ cursor وتنفّذ تغييرات schema.
تُسجَّل بالترتيب. عند بدء التطبيق تُنفّذ التي لم تُنفَّذ بعد.
"""

from __future__ import annotations

import sqlite3
from typing import Callable, List, Tuple

Migration = Callable[[sqlite3.Cursor], None]

SCHEMA_VERSION = 2   # V0.2


# ---------------------------------------------------------------------------
# Migration 1: جداول core (projects, threads, messages, settings, logs)
# ---------------------------------------------------------------------------
def m1_initial_core(cursor: sqlite3.Cursor) -> None:
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS projects (
            id           TEXT PRIMARY KEY,
            name         TEXT NOT NULL,
            root_path    TEXT NOT NULL,
            created_at   REAL NOT NULL,
            updated_at   REAL NOT NULL,
            meta_json    TEXT
        );
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS threads (
            id           TEXT PRIMARY KEY,
            project_id   TEXT REFERENCES projects(id) ON DELETE CASCADE,
            title        TEXT NOT NULL,
            created_at   REAL NOT NULL,
            updated_at   REAL NOT NULL,
            meta_json    TEXT
        );
    """)
    cursor.execute(
        "CREATE INDEX IF NOT EXISTS idx_threads_project "
        "ON threads(project_id);"
    )
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS messages (
            id           INTEGER PRIMARY KEY AUTOINCREMENT,
            thread_id    TEXT NOT NULL REFERENCES threads(id) ON DELETE CASCADE,
            role         TEXT NOT NULL CHECK(role IN ('user','assistant','system','tool')),
            content      TEXT NOT NULL,
            ts           REAL NOT NULL,
            meta_json    TEXT
        );
    """)
    cursor.execute(
        "CREATE INDEX IF NOT EXISTS idx_messages_thread "
        "ON messages(thread_id, ts);"
    )
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS settings (
            key          TEXT PRIMARY KEY,
            value        TEXT NOT NULL,
            updated_at   REAL NOT NULL
        );
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS logs (
            id           INTEGER PRIMARY KEY AUTOINCREMENT,
            level        TEXT NOT NULL,
            logger       TEXT NOT NULL,
            message      TEXT NOT NULL,
            ts           REAL NOT NULL
        );
    """)
    cursor.execute(
        "CREATE INDEX IF NOT EXISTS idx_logs_ts "
        "ON logs(ts);"
    )


# ---------------------------------------------------------------------------
# Migration 2: tool_calls + project memory + sessions
# ---------------------------------------------------------------------------
def m2_tool_calls_and_sessions(cursor: sqlite3.Cursor) -> None:
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tool_calls (
            id           INTEGER PRIMARY KEY AUTOINCREMENT,
            thread_id    TEXT REFERENCES threads(id) ON DELETE CASCADE,
            message_id   INTEGER REFERENCES messages(id) ON DELETE CASCADE,
            tool_name    TEXT NOT NULL,
            input_json   TEXT NOT NULL,
            output_json  TEXT,
            status       TEXT NOT NULL,
            started_at   REAL NOT NULL,
            finished_at  REAL,
            error        TEXT
        );
    """)
    cursor.execute(
        "CREATE INDEX IF NOT EXISTS idx_tool_calls_thread "
        "ON tool_calls(thread_id);"
    )
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS sessions (
            id           TEXT PRIMARY KEY,
            started_at   REAL NOT NULL,
            ended_at     REAL,
            hostname     TEXT,
            app_version  TEXT
        );
    """)


# الترتيب مهم. لا تغيّر الأرقام.
ALL_MIGRATIONS: List[Tuple[int, Migration]] = [
    (1, m1_initial_core),
    (2, m2_tool_calls_and_sessions),
]
