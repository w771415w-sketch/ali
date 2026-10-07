# -*- coding: utf-8 -*-
"""Persistent conversation-learning memory with deterministic identity and fuzzy lookup.

This is deliberately separate from model weights: new conversations are remembered immediately,
while retraining is scheduled only when the deduplicated training ledger says it is needed.
"""
from __future__ import annotations
from pathlib import Path
import re, sqlite3, time, hashlib
from difflib import SequenceMatcher
from typing import Any

_ROLE_RE = re.compile(r"\s+", re.UNICODE)

def normalize_query(text: str) -> str:
    text = str(text or "").strip().lower()
    text = text.replace("\u0640", "")
    text = _ROLE_RE.sub(" ", text)
    return text

def identity(user: str, assistant: str) -> str:
    raw = normalize_query(user) + "\n" + str(assistant or "").strip()
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()

class ConversationMemory:
    def __init__(self, path: str | Path):
        self.path = Path(path); self.path.parent.mkdir(parents=True, exist_ok=True)
        c = sqlite3.connect(self.path)
        c.execute("""CREATE TABLE IF NOT EXISTS conversations(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_text TEXT NOT NULL,
            assistant_text TEXT NOT NULL,
            user_norm TEXT NOT NULL,
            pair_hash TEXT UNIQUE NOT NULL,
            source TEXT NOT NULL,
            model_version TEXT,
            quality REAL DEFAULT 0.5,
            created_at REAL NOT NULL,
            updated_at REAL NOT NULL
        )""")
        c.execute("CREATE INDEX IF NOT EXISTS idx_conv_norm ON conversations(user_norm)")
        c.execute("CREATE INDEX IF NOT EXISTS idx_conv_quality ON conversations(quality)")
        c.commit(); c.close()

    def put(self, user_text: str, assistant_text: str, source: str = "chat", model_version: str = "", quality: float = .5) -> dict[str, Any]:
        user_text, assistant_text = str(user_text).strip(), str(assistant_text).strip()
        if not user_text or not assistant_text:
            return {"stored": False, "reason": "empty"}
        h = identity(user_text, assistant_text); now = time.time()
        c = sqlite3.connect(self.path)
        c.execute("""INSERT INTO conversations(user_text,assistant_text,user_norm,pair_hash,source,model_version,quality,created_at,updated_at)
                     VALUES(?,?,?,?,?,?,?,?,?) ON CONFLICT(pair_hash) DO UPDATE SET updated_at=excluded.updated_at""",
                  (user_text, assistant_text, normalize_query(user_text), h, source, model_version, max(0,min(1,float(quality))), now, now))
        c.commit(); c.close()
        return {"stored": True, "hash": h}

    def _rows(self, limit: int = 2000):
        c = sqlite3.connect(self.path); c.row_factory = sqlite3.Row
        rows = c.execute("SELECT * FROM conversations ORDER BY quality DESC, updated_at DESC LIMIT ?", (limit,)).fetchall(); c.close()
        return [dict(r) for r in rows]

    def search(self, query: str, limit: int = 5, min_score: float = 0.0, min_quality: float = .6) -> list[dict[str, Any]]:
        q = normalize_query(query)
        if not q: return []
        q_words = set(q.split())
        out = []
        for r in self._rows():
            if float(r.get('quality',0.0)) < float(min_quality):
                continue
            cand = r["user_norm"]
            if cand == q:
                score = 1.0
            else:
                seq = SequenceMatcher(None, q, cand).ratio()
                cw = set(cand.split())
                overlap = len(q_words & cw) / max(1, len(q_words | cw))
                score = .70 * seq + .30 * overlap
            if score >= min_score:
                out.append((score, r))
        out.sort(key=lambda x: (x[0], x[1]["quality"]), reverse=True)
        for score, r in out[:limit]: r["score"] = round(float(score), 4)
        return [r for _, r in out[:limit]]

    def exact(self, query: str) -> dict[str, Any] | None:
        hits = self.search(query, 1, .999999, .6)
        return hits[0] if hits else None


    def feedback(self, user_text: str, assistant_text: str, accepted: bool, source: str = "user-feedback") -> dict[str, Any]:
        """Record explicit human feedback without allowing rejected replies into training search."""
        q=.95 if accepted else .1
        return self.put(user_text,assistant_text,source=source,model_version="human-reviewed",quality=q)

    def export_training(self, out: str | Path, min_quality: float = .6) -> dict[str, Any]:
        out = Path(out); out.parent.mkdir(parents=True, exist_ok=True)
        rows = [r for r in self._rows(100000) if float(r["quality"]) >= min_quality]
        written = 0
        with out.open("w", encoding="utf-8") as f:
            for r in rows:
                obj = {"id": r["pair_hash"], "messages": [
                    {"role": "user", "content": r["user_text"]},
                    {"role": "assistant", "content": r["assistant_text"]}
                ], "source": r["source"], "model_version": r["model_version"], "quality": r["quality"]}
                f.write(__import__("json").dumps(obj, ensure_ascii=False) + "\n"); written += 1
        return {"output": str(out), "samples": written}
