# -*- coding: utf-8 -*-
from __future__ import annotations
import importlib.util
import platform
import sys

REQUIRED = {
    "torch": "torch",
    "numpy": "numpy",
    "psutil": "psutil",
    "safetensors": "safetensors",
    "sentencepiece": "sentencepiece",
    "pytest": "pytest",
    "tkinterdnd2": "tkinterdnd2",
}

missing = [name for name, mod in REQUIRED.items() if importlib.util.find_spec(mod) is None]
print(f"[PREFLIGHT] Python: {platform.python_version()} ({platform.architecture()[0]})")
print(f"[PREFLIGHT] Missing: {', '.join(missing) if missing else 'none'}")
if missing:
    print("[PREFLIGHT] Dependency environment is incomplete.")
    raise SystemExit(2)

try:
    import torch
    print(f"[PREFLIGHT] torch={torch.__version__}")
    print(f"[PREFLIGHT] cuda_available={torch.cuda.is_available()}")
except Exception as exc:
    print(f"[PREFLIGHT] torch import failed: {exc}")
    raise SystemExit(3)

print("[PREFLIGHT] PASS")
