# -*- coding: utf-8 -*-
"""Verify that the included ALI bootstrap model is present and loadable."""
from __future__ import annotations
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from model.registry import ModelRegistry
from model.manager import ModelManager


def main() -> int:
    registry = ModelRegistry(ROOT / "models" / "models.sqlite3")
    row = registry.active("ALI")
    if not row:
        print("ERROR: no active ALI model is registered")
        return 1
    manager = ModelManager(ROOT, registry)
    discovered = manager.discover_active("ALI")
    if not discovered:
        print("ERROR: registered active model is not loadable")
        return 1
    engine, _ = manager.load(discovered)
    sample = engine.complete("Hello ALI", max_new_tokens=8, temperature=0.0, context_size=128)
    print("[OK] Active model:", discovered.get("version"))
    print("[OK] HF model:", discovered.get("hf_dir"))
    print("[OK] Inference smoke completed; generated characters:", len(sample))
    print("NOTE: the bundled bootstrap model is a functional micro checkpoint, not a production-scale assistant.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
