from __future__ import annotations
from pathlib import Path

BLOCKED_NAMES = {".env", "auth.json", "credentials.json", "token.json", "secrets.json"}
READABLE_FILES = {"SOUL.md", "MEMORY.md", "USER.md", "config.yaml", "skills/.bundled_manifest"}
READABLE_DB = {"kanban.db", "projects.db"}

def safe_root(path: str | Path) -> Path:
    return Path(path).expanduser().resolve()

def inside(root: Path, candidate: Path) -> bool:
    try:
        candidate.resolve().relative_to(root.resolve())
        return True
    except ValueError:
        return False

def guard_file(root: Path, path: str | Path, *, allow_db=False) -> Path:
    p = (root / path).resolve() if not Path(path).is_absolute() else Path(path).resolve()
    if not inside(root, p):
        raise PermissionError("Hermes path escapes configured root")
    if p.name.lower() in BLOCKED_NAMES or p.suffix.lower() in {".key", ".pem", ".p12", ".pfx"}:
        raise PermissionError(f"Blocked sensitive Hermes file: {p.name}")
    rel = p.relative_to(root).as_posix()
    if allow_db and p.name in READABLE_DB:
        return p
    if rel in READABLE_FILES or rel.startswith("memories/") or rel.startswith("skills/"):
        return p
    raise PermissionError(f"Hermes path is not in the read-only allowlist: {rel}")
