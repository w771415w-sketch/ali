from __future__ import annotations
import json
from typing import Any
from .adapter import HermesAdapter
from .config import HermesConfig

class HermesContextRouter:
    """Deterministic routing: Hermes is consulted only when the request is relevant."""
    KEYWORDS = (
        "hermes", "ذاكرة hermes", "ذكريات hermes", "مشاريع hermes", "مهام hermes",
        "بيانات hermes", "skills hermes", "مهارات hermes", "memory.md", "soul.md", "user.md",
        "hermes memory", "hermes project", "hermes skills"
    )
    def __init__(self, config: HermesConfig | None = None):
        self.adapter=HermesAdapter(config)
        self.last={"used":False,"reason":"not-routed","context":{}}
    def route(self, query: str) -> dict[str, Any]:
        text=str(query or "").strip()
        low=text.lower()
        relevant=any(k in low for k in self.KEYWORDS)
        if not relevant:
            self.last={"used":False,"reason":"no-hermes-intent","context":{}}
            return self.last
        ctx=self.adapter.context_snapshot(text)
        compact=json.dumps(ctx,ensure_ascii=False,indent=2)
        self.last={"used":True,"reason":"hermes-intent","context":ctx,"prompt_context":compact[:self.adapter.config.max_context_chars]}
        return self.last
    def status(self):
        s=self.adapter.status(); s["last_used"]=self.last.get("used",False); s["last_reason"]=self.last.get("reason"); return s
