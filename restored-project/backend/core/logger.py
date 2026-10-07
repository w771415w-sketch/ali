# -*- coding: utf-8 -*-
"""طبقة الـ logging الموحدة.

- log إلى ملف يومي داخل APPDATA\\ALI-Agent\\logs\\.
- log إلى stderr أيضاً عند الحاجة.
- thread-safe.
- لا أسرار في الـ logs (token redaction بسيطة).
"""

from __future__ import annotations

import logging
import os
import re
import sys
import threading
from logging.handlers import RotatingFileHandler
from pathlib import Path

_LOCK = threading.Lock()
_INITIALIZED = False
_TOKEN_RE = re.compile(r"(token[\"'\\s:=]+)([A-Za-z0-9]{8,})", re.I)


class _RedactFilter(logging.Filter):
    """إخفاء أي token طويل يظهر في الرسالة."""

    def filter(self, record: logging.LogRecord) -> bool:
        try:
            msg = record.getMessage()
            msg = _TOKEN_RE.sub(r"\1***REDACTED***", msg)
            record.msg = msg
            record.args = ()
        except Exception:
            pass
        return True


def _init_once() -> None:
    global _INITIALIZED
    if _INITIALIZED:
        return
    with _LOCK:
        if _INITIALIZED:
            return
        from config.paths import APP_PATHS
        logs_dir = APP_PATHS.user_logs_dir()
        log_file = logs_dir / "ali_studio.log"

        root = logging.getLogger("ali")
        root.setLevel(logging.INFO)
        # تفادي تكرار handlers عند إعادة التحميل.
        root.handlers.clear()

        fmt = logging.Formatter(
            "%(asctime)s [%(levelname)s] %(name)s: %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        redactor = _RedactFilter()

        fh = RotatingFileHandler(
            str(log_file), maxBytes=1_000_000, backupCount=3,
            encoding="utf-8",
        )
        fh.setFormatter(fmt)
        fh.addFilter(redactor)
        root.addHandler(fh)

        if "--verbose" in sys.argv or os.environ.get("ALI_VERBOSE"):
            sh = logging.StreamHandler(sys.stderr)
            sh.setFormatter(fmt)
            sh.addFilter(redactor)
            root.addHandler(sh)

        _INITIALIZED = True


def get_logger(name: str) -> logging.Logger:
    """نقطة الدخول الموحدة للـ logger."""
    _init_once()
    return logging.getLogger("ali." + name)
