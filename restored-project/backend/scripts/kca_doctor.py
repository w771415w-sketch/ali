#!/usr/bin/env python
from __future__ import annotations
from pathlib import Path
import json, sys
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from control_plane import summary
from control_plane.kca_registry import FUNCTIONS

def main() -> int:
    result = {
        "kca": summary(),
        "registry_file": str((ROOT / "control_plane" / "function_registry.json").resolve()),
        "master_document": str((ROOT / "docs" / "AI_KCA_MASTER.md").resolve()),
        "count_ok": len(FUNCTIONS) == 100,
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["count_ok"] else 1
if __name__ == "__main__":
    raise SystemExit(main())
