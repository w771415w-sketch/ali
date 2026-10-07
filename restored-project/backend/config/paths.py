# -*- coding: utf-8 -*-
"""طبقة المسارات المركزية. أي مسار يجب أن يمر من هنا."""

from __future__ import annotations

import os
import sys
from pathlib import Path


def _project_root() -> Path:
    """Project data root for source runs and frozen Windows builds."""
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent
    return Path(__file__).resolve().parent.parent


def _user_data_dir() -> Path:
    """Return persistent data path; portable mode keeps all app data inside the project."""
    if os.environ.get("ALI_PORTABLE_MODE", "0") == "1":
        root = _project_root()
        p = root / "runtime" / "user_data"
    else:
        base = os.environ.get("APPDATA") or str(Path.home())
        p = Path(base) / "ALI-AI"
    p.mkdir(parents=True, exist_ok=True)
    return p


class AppPaths:
    """نقطة مركزية لكل مسارات ALI AI."""

    def __init__(self):
        self._root = _project_root()
        self._user = _user_data_dir()

    # -------- project root
    def project_root(self) -> Path:
        return self._root

    # -------- user appdata
    def user_data_dir(self) -> Path:
        return self._user

    def user_config(self) -> Path:
        return self._user / "config.json"

    def user_threads(self) -> Path:
        return self._user / "threads.json"

    def user_logs_dir(self) -> Path:
        p = self._user / "logs"
        p.mkdir(parents=True, exist_ok=True)
        return p

    # -------- local under project root
    def local_config(self) -> Path:
        return self._root / "config" / "default_config.json"

    def local_config_candidates(self) -> list:
        """مرشحات للـ config عند الإقلاع: الجذر أولاً ثم project root."""
        return [
            self._root / "config" / "config.json",
            self._root / "config.json",
        ]

    def checkpoints_dir(self) -> Path:
        p = self._root / "checkpoints"
        p.mkdir(parents=True, exist_ok=True)
        return p

    def weights_dir(self) -> Path:
        p = self._root / "weights"
        p.mkdir(parents=True, exist_ok=True)
        return p

    def data_dir(self) -> Path:
        p = self._root / "data"
        return p

    def tests_dir(self) -> Path:
        return self._root / "tests"

    def models_dir(self) -> Path:
        p = self._root / "models"
        p.mkdir(parents=True, exist_ok=True)
        return p

    def model_inbox_dir(self) -> Path:
        p = self.models_dir() / "inbox"
        p.mkdir(parents=True, exist_ok=True)
        return p

    def model_archive_dir(self) -> Path:
        p = self.models_dir() / "archive"
        p.mkdir(parents=True, exist_ok=True)
        return p

    # -------- default config (no secrets, no Lovable)
    def default_config(self) -> dict:
        return {
            "name": "Windows PC",
            "model": "ALI-local",
            "app": "ALI AI",
            "version": "4.5.2",
            "ai_mode": "professional",
            "perm_mode": "default",
            "last_dir": str(self._root),
            "threads": {},
            "always_allow": [],
        }


APP_PATHS = AppPaths()
