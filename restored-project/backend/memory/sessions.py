# -*- coding: utf-8 -*-
"""Persistent chat sessions: new conversations, history, rename and delete."""
from __future__ import annotations
from pathlib import Path
from typing import Any
import sqlite3, time, uuid, re


def _title(text: str) -> str:
    s = re.sub(r"\s+", " ", str(text or "").strip())
    return s[:54] + ("…" if len(s) > 54 else "") or "محادثة جديدة"


class ConversationSessionStore:
    def __init__(self, path: str | Path):
        self.path = Path(path); self.path.parent.mkdir(parents=True, exist_ok=True)
        with self._connect() as c:
            c.executescript("""
            CREATE TABLE IF NOT EXISTS sessions(
              id TEXT PRIMARY KEY,
              title TEXT NOT NULL,
              created_at REAL NOT NULL,
              updated_at REAL NOT NULL,
              model_version TEXT DEFAULT '',
              archived INTEGER NOT NULL DEFAULT 0
            );
            CREATE TABLE IF NOT EXISTS session_messages(
              id INTEGER PRIMARY KEY AUTOINCREMENT,
              session_id TEXT NOT NULL,
              seq INTEGER NOT NULL,
              role TEXT NOT NULL,
              content TEXT NOT NULL,
              created_at REAL NOT NULL,
              model_version TEXT DEFAULT '',
              meta_json TEXT DEFAULT '{}',
              UNIQUE(session_id, seq)
            );
            CREATE INDEX IF NOT EXISTS idx_session_updated ON sessions(updated_at DESC);
            CREATE INDEX IF NOT EXISTS idx_session_messages ON session_messages(session_id, seq);
            """)
            try:
                c.execute("ALTER TABLE session_messages ADD COLUMN meta_json TEXT DEFAULT '{}'")
            except sqlite3.OperationalError:
                pass


    def _connect(self):
        c = sqlite3.connect(self.path, timeout=30)
        c.row_factory = sqlite3.Row
        return c

    def create(self, title: str = "محادثة جديدة", model_version: str = "") -> dict[str, Any]:
        sid = f"chat-{uuid.uuid4().hex}"
        now = time.time()
        with self._connect() as c:
            c.execute("INSERT INTO sessions(id,title,created_at,updated_at,model_version) VALUES(?,?,?,?,?)", (sid, _title(title), now, now, model_version))
        return self.get(sid)

    def list(self, limit: int = 100) -> list[dict[str, Any]]:
        with self._connect() as c:
            rows = c.execute("SELECT * FROM sessions WHERE archived=0 ORDER BY updated_at DESC LIMIT ?", (max(1, min(500, int(limit))),)).fetchall()
        return [dict(r) for r in rows]

    def get(self, session_id: str) -> dict[str, Any] | None:
        with self._connect() as c:
            s = c.execute("SELECT * FROM sessions WHERE id=?", (str(session_id),)).fetchone()
            if not s: return None
            msgs = c.execute("SELECT id,session_id,seq,role,content,created_at,model_version,meta_json FROM session_messages WHERE session_id=? ORDER BY seq", (str(session_id),)).fetchall()
        out = dict(s); out['messages'] = [dict(m) for m in msgs]; return out

    def append(self, session_id: str, role: str, content: str, model_version: str = "", meta: dict[str, Any] | None = None) -> dict[str, Any]:
        sid = str(session_id); role = str(role).strip().lower(); content = str(content or '').strip()
        if role not in {'system','user','assistant','tool'}: raise ValueError('invalid role')
        if not content: raise ValueError('content is empty')
        now = time.time()
        with self._connect() as c:
            if not c.execute("SELECT 1 FROM sessions WHERE id=?", (sid,)).fetchone(): raise KeyError('conversation not found')
            seq = int(c.execute("SELECT COALESCE(MAX(seq),0)+1 FROM session_messages WHERE session_id=?", (sid,)).fetchone()[0])
            meta_json = __import__('json').dumps(meta or {}, ensure_ascii=False, sort_keys=True)
            c.execute("INSERT INTO session_messages(session_id,seq,role,content,created_at,model_version,meta_json) VALUES(?,?,?,?,?,?,?)", (sid,seq,role,content,now,model_version,meta_json))
            if role == 'user':
                existing = c.execute("SELECT title FROM sessions WHERE id=?", (sid,)).fetchone()
                title = _title(content) if existing and str(existing['title']) == 'محادثة جديدة' else None
                if title:
                    c.execute("UPDATE sessions SET title=?,updated_at=?,model_version=COALESCE(NULLIF(?,''),model_version) WHERE id=?", (title,now,model_version,sid))
                else:
                    c.execute("UPDATE sessions SET updated_at=?,model_version=COALESCE(NULLIF(?,''),model_version) WHERE id=?", (now,model_version,sid))
            else:
                c.execute("UPDATE sessions SET updated_at=?,model_version=COALESCE(NULLIF(?,''),model_version) WHERE id=?", (now,model_version,sid))
        return {'ok': True, 'session_id': sid, 'seq': seq}

    def rename(self, session_id: str, title: str) -> dict[str, Any] | None:
        with self._connect() as c:
            c.execute("UPDATE sessions SET title=?,updated_at=? WHERE id=?", (_title(title), time.time(), str(session_id)))
        return self.get(session_id)

    def delete(self, session_id: str) -> bool:
        with self._connect() as c:
            cur = c.execute("UPDATE sessions SET archived=1,updated_at=? WHERE id=?", (time.time(), str(session_id)))
            return cur.rowcount > 0

    def clear(self, session_id: str) -> None:
        with self._connect() as c:
            c.execute("DELETE FROM session_messages WHERE session_id=?", (str(session_id),))
            c.execute("UPDATE sessions SET title='محادثة جديدة',updated_at=? WHERE id=?", (time.time(), str(session_id)))
