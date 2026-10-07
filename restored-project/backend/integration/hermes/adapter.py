from __future__ import annotations
from pathlib import Path
import sqlite3, json, re
from typing import Any
from .config import HermesConfig, load_config
from .security import safe_root, guard_file, READABLE_DB

class HermesAdapter:
    """Safe, read-oriented bridge to an external Hermes installation.

    It never copies Hermes into ALI and it never exposes .env/auth.json contents.
    """
    def __init__(self, config: HermesConfig | None = None):
        self.config = config or load_config()
        self.root = safe_root(self.config.root)

    def status(self) -> dict[str, Any]:
        exists = self.root.exists() and self.root.is_dir()
        return {
            "enabled": self.config.enabled, "root": str(self.root),
            "exists": exists, "mode": "read-only" if self.config.read_only else "write-enabled",
            "database_reads": bool(self.config.allow_database_reads),
            "api": bool(self.config.allow_api), "mcp": bool(self.config.allow_mcp),
        }

    def read_text(self, relative: str) -> str:
        if not self.config.enabled:
            raise RuntimeError("Hermes integration is disabled")
        p = guard_file(self.root, relative)
        if not p.exists():
            raise FileNotFoundError(str(p))
        if p.stat().st_size > self.config.max_file_bytes:
            raise ValueError("Hermes file exceeds configured read limit")
        return p.read_text(encoding="utf-8", errors="replace")[: self.config.max_context_chars]

    def list_memories(self, limit: int = 12) -> list[dict[str, str]]:
        out=[]
        mem = self.root / "memories"
        if not mem.exists(): return out
        for p in sorted(mem.rglob("*.md"))[:max(1,int(limit))]:
            try:
                guard_file(self.root, p)
                out.append({"name": p.name, "path": p.relative_to(self.root).as_posix()})
            except Exception:
                continue
        return out

    def list_skills(self, limit: int = 100) -> list[dict[str, str]]:
        out=[]; skills=self.root/'skills'
        if not skills.exists(): return out
        for p in sorted(skills.rglob('SKILL.md'))[:max(1,int(limit))]:
            try:
                guard_file(self.root,p); out.append({"name":p.parent.name,"path":p.relative_to(self.root).as_posix()})
            except Exception: continue
        return out

    def read_database(self, db_name: str, query: str, params: tuple = (), limit: int = 100) -> list[dict[str, Any]]:
        if not self.config.allow_database_reads:
            raise PermissionError("Hermes database reads are disabled")
        if db_name not in READABLE_DB:
            raise PermissionError("Database is not in Hermes read-only allowlist")
        p=guard_file(self.root, db_name, allow_db=True)
        if not p.exists(): raise FileNotFoundError(str(p))
        if not re.match(r"^\s*(SELECT|PRAGMA)\b", query, re.I):
            raise PermissionError("Hermes database adapter only accepts SELECT/PRAGMA")
        query = query.rstrip(' ;') + f" LIMIT {max(1,min(int(limit),1000))}" if re.match(r"^\s*SELECT\b",query,re.I) and ' limit ' not in query.lower() else query
        uri=f"file:{p.as_posix()}?mode=ro"
        con=sqlite3.connect(uri, uri=True); con.row_factory=sqlite3.Row
        try:
            rows=con.execute(query, params).fetchall()
            return [dict(r) for r in rows]
        finally:
            con.close()

    def context_snapshot(self, query: str = "") -> dict[str, Any]:
        q=query.lower()
        data: dict[str, Any] = {"status": self.status()}
        if not data["status"]["exists"]:
            return data
        wants_memory=any(k in q for k in ["memory","ذاكرة","ذكريات","user.md","soul.md","المعلومات المحفوظة"])
        wants_project=any(k in q for k in ["project","projects","مشروع","مشاريع","kanban","tasks","مهام"])
        if wants_memory:
            for rel,key in [("memories/MEMORY.md","memory"),("memories/USER.md","user_profile"),("SOUL.md","soul")]:
                try: data[key]=self.read_text(rel)
                except Exception as e: data[key+"_error"]=str(e)
            data["memory_index"]=self.list_memories()
        if wants_project and self.config.allow_database_reads:
            for db in ("projects.db","kanban.db"):
                try:
                    tables=self.read_database(db,"SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")
                    data[db]={"tables":tables}
                except Exception as e: data[db]={"error":str(e)}
        if "skill" in q or "مهار" in q or "skills" in q:
            data["skills"]=self.list_skills()
        return data
