# -*- coding: utf-8 -*-
"""Build enriched KCA training records from approved conversation JSONL."""
from __future__ import annotations
from pathlib import Path
import hashlib, json
from typing import Any, Iterable

from data_engine.normalization import normalize_text, redact_secrets
from control_plane.router import KCARequestRouter
from control_plane.contracts import RequestEnvelope


def _digest(obj: Any) -> str:
    raw = json.dumps(obj, ensure_ascii=False, sort_keys=True, separators=(",", ":"), default=str).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def enrich_conversation(row: dict[str, Any], router: KCARequestRouter | None = None) -> dict[str, Any] | None:
    router = router or KCARequestRouter()
    messages = row.get("messages") or []
    user = next((m.get("content", "") for m in messages if m.get("role") == "user"), "")
    assistant = next((m.get("content", "") for m in reversed(messages) if m.get("role") == "assistant"), "")
    if not str(user).strip() or not str(assistant).strip():
        return None
    user, ru = redact_secrets(normalize_text(str(user)))
    assistant, ra = redact_secrets(normalize_text(str(assistant)))
    env = RequestEnvelope(raw_text=user)
    state = router.build_state(env)
    output = {
        "sample_id": str(row.get("id") or _digest([user, assistant])),
        "input": user,
        "context": row.get("context") or {},
        "entities": row.get("entities") or [],
        "state": {"intent": state.intent, "confidence": state.confidence},
        "goal": {"text": state.goal},
        "constraints": state.constraints,
        "implicit_intent": state.implicit_intent,
        "task_state": state.task_state,
        "candidate_actions": state.candidate_actions,
        "selected_action": state.selected_action,
        "observation": row.get("observation"),
        "error_state": row.get("error_state"),
        "correction": row.get("correction"),
        "verification": row.get("verification"),
        "uncertainty": row.get("uncertainty"),
        "final_output": assistant,
        "messages": [{"role": "user", "content": user}, {"role": "assistant", "content": assistant}],
        "source": row.get("source") or "conversation",
        "quality": float(row.get("quality", 0.0) or 0.0),
        "redacted": bool(ru or ra),
        "schema_version": "kca-3.0",
    }
    output["record_hash"] = _digest(output)
    return output


def build_kca_dataset(inputs: Iterable[str | Path], output: str | Path, min_quality: float = 0.6) -> dict[str, Any]:
    seen: set[str] = set()
    rows: list[dict[str, Any]] = []
    for raw_path in inputs:
        p = Path(raw_path)
        if not p.exists():
            continue
        for line in p.read_text(encoding="utf-8", errors="replace").splitlines():
            if not line.strip():
                continue
            try:
                row = json.loads(line)
            except Exception:
                continue
            if float(row.get("quality", 1.0) or 0.0) < min_quality:
                continue
            enriched = enrich_conversation(row)
            if not enriched or enriched["record_hash"] in seen:
                continue
            seen.add(enriched["record_hash"])
            rows.append(enriched)
    out = Path(output); out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", encoding="utf-8", newline="\n") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")
    return {"output": str(out), "samples": len(rows), "schema": "kca-3.0", "unique": len(seen)}
