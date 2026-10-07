# -*- coding: utf-8 -*-
"""Load the source-derived 100-function AI-KCA registry without hard-coding it in UI code."""
from __future__ import annotations
from pathlib import Path
import json
from typing import Any

ROOT = Path(__file__).resolve().parent
REGISTRY_PATH = ROOT / "function_registry.json"


def load_function_registry(path: str | Path = REGISTRY_PATH) -> dict[str, dict[str, Any]]:
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    rows = data.get("functions") or []
    return {str(row["id"]): row for row in rows if row.get("id")}


FUNCTIONS = load_function_registry()
BY_NAME = {row["name"]: row for row in FUNCTIONS.values()}


def function_by_name(name: str) -> dict[str, Any] | None:
    return BY_NAME.get(str(name))


def summary() -> dict[str, Any]:
    domains: dict[str, int] = {}
    for row in FUNCTIONS.values():
        d = str(row.get("domain") or "unknown")
        domains[d] = domains.get(d, 0) + 1
    return {"version": "3.0", "functions": len(FUNCTIONS), "domains": domains}
