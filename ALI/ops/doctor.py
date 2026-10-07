from __future__ import annotations

import json
import platform
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]


def check_file(relative: str) -> dict[str, Any]:
    path = ROOT / relative
    return {"path": relative, "exists": path.exists(), "size": path.stat().st_size if path.exists() else 0}


def inspect() -> dict[str, Any]:
    checks = [
        check_file("backend/main.py"),
        check_file("backend/control_plane/runtime_facade.py"),
        check_file("restored-project/desktop/package.json"),
        check_file("restored-project/desktop/electron/main.cjs"),
        check_file("restored-project/desktop/node_modules"),
        check_file("restored-project/backend/models/active/README.md"),
    ]
    desktop_pkg = ROOT / "restored-project/desktop/package.json"
    desktop = {}
    if desktop_pkg.exists():
        try:
            desktop = json.loads(desktop_pkg.read_text(encoding="utf-8"))
        except Exception as exc:
            desktop = {"parse_error": f"{type(exc).__name__}: {exc}"}
    pending = []
    if not (ROOT / "restored-project/desktop/node_modules").exists():
        pending.append("desktop dependencies are not installed in the current checkout")
    if not (ROOT / "restored-project/desktop/release").exists():
        pending.append("Windows Electron release output is not present in the repository")
    return {
        "ok": True,
        "platform": platform.platform(),
        "repo_root": str(ROOT),
        "desktop_package": {"version": desktop.get("version"), "electron": desktop.get("main"), "build_targets": desktop.get("build", {}).get("win", {}).get("target")},
        "checks": checks,
        "pending_native_gates": pending,
        "note": "These checks are evidence of repository state; they do not claim a physical Windows/Electron/model run.",
    }
