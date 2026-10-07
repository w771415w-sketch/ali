from __future__ import annotations

import importlib
import os
import platform
import shutil
import sys
from pathlib import Path
from typing import Any


def backend_status(module: str, class_name: str) -> dict[str, Any]:
    try:
        mod = importlib.import_module(module)
        cls = getattr(mod, class_name)
        return {"available": True, "module": module, "class": class_name, "qualified": f"{mod.__name__}.{cls.__name__}"}
    except Exception as exc:
        return {"available": False, "module": module, "class": class_name, "error": f"{type(exc).__name__}: {exc}"}


def snapshot(workspace: Path, backend_module: str, backend_class: str, hardware: dict[str, Any]) -> dict[str, Any]:
    total, used, free = shutil.disk_usage(workspace)
    return {
        "ok": True,
        "application": {"python": sys.version.split()[0], "platform": platform.platform(), "machine": platform.machine()},
        "process": {"pid": os.getpid(), "cpu_count": os.cpu_count()},
        "workspace": {"path": str(workspace), "exists": workspace.exists(), "disk_free_gb": round(free / (1024**3), 2), "disk_used_gb": round(used / (1024**3), 2), "disk_total_gb": round(total / (1024**3), 2)},
        "backend": backend_status(backend_module, backend_class),
        "hardware_policy": hardware,
    }
