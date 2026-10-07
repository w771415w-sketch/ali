# -*- coding: utf-8 -*-
"""Thin session facade over the existing SQLite conversation database."""
from __future__ import annotations

from pathlib import Path
from typing import Any

from database.database import Database, ProjectRepo, ThreadRepo, MessageRepo


class SessionStore:
    def __init__(self, db_path: str | Path):
        self.db = Database(Path(db_path))
        self.projects = ProjectRepo(self.db)
        self.threads = ThreadRepo(self.db)
        self.messages = MessageRepo(self.db)

    def ensure_project(self, root_path: str, name: str = "Workspace") -> str:
        row = self.projects.by_path(root_path)
        if row:
            return row["id"]
        return self.projects.create(name, root_path)

    def new_thread(self, project_id: str | None, title: str = "New conversation") -> str:
        return self.threads.create(project_id, title)

    def latest_thread(self, project_id: str | None = None) -> dict[str, Any] | None:
        rows = self.list_threads(project_id, 1)
        return rows[0] if rows else None

    def save_message(self, thread_id: str, role: str, content: str, meta: dict[str, Any] | None = None) -> int:
        return int(self.messages.add(thread_id, role, content, meta))

    def load_messages(self, thread_id: str, limit: int = 500) -> list[dict[str, Any]]:
        return self.messages.list_for_thread(thread_id, limit)

    def list_threads(self, project_id: str | None = None, limit: int = 50) -> list[dict[str, Any]]:
        return self.threads.list_for_project(project_id, limit) if project_id else self.threads.list_all(limit)
