from __future__ import annotations

import hashlib
import hmac
import ipaddress
import threading
import time
from collections import deque
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


class SecurityError(ValueError):
    pass


def safe_relative_path(path: str) -> str:
    """Validate a repository/workspace-relative path and normalize separators."""
    raw = str(path).replace("\\", "/").strip()
    if not raw or raw.startswith("/"):
        raise SecurityError("path must be relative")
    if len(raw) >= 2 and raw[1] == ":":
        raise SecurityError("drive-qualified paths are not allowed")
    parts = [p for p in raw.split("/") if p not in {""}]
    if any(p in {".", ".."} for p in parts) or ".." in raw:
        raise SecurityError("path traversal is not allowed")
    if any(ord(ch) < 32 for ch in raw):
        raise SecurityError("control characters are not allowed in paths")
    return "/".join(parts)


def inside(root: Path, relative: str) -> Path:
    rel = safe_relative_path(relative)
    base = root.resolve()
    target = (base / rel).resolve()
    try:
        target.relative_to(base)
    except ValueError as exc:
        raise SecurityError("resolved path escapes workspace") from exc
    return target


class TokenAuth:
    def __init__(self, token: str):
        self._digest = hashlib.sha256(token.encode("utf-8")).digest() if token else None

    @property
    def enabled(self) -> bool:
        return self._digest is not None

    def verify(self, supplied: str | None) -> bool:
        if not self._digest:
            return True
        if not supplied:
            return False
        digest = hashlib.sha256(supplied.encode("utf-8")).digest()
        return hmac.compare_digest(self._digest, digest)


@dataclass
class RateLimitState:
    hits: deque[float]


class RateLimiter:
    def __init__(self, limit: int, window_seconds: int):
        self.limit = max(1, int(limit))
        self.window_seconds = max(1, int(window_seconds))
        self._states: dict[str, RateLimitState] = {}
        self._lock = threading.Lock()

    def allow(self, key: str) -> bool:
        now = time.monotonic()
        with self._lock:
            state = self._states.setdefault(key, RateLimitState(deque()))
            while state.hits and now - state.hits[0] >= self.window_seconds:
                state.hits.popleft()
            if len(state.hits) >= self.limit:
                return False
            state.hits.append(now)
            return True


def remote_address_allowed(address: str) -> bool:
    """Reject malformed addresses before any policy decision is made."""
    try:
        ipaddress.ip_address(address)
        return True
    except ValueError:
        return False


def redact(value: object, sensitive_keys: Iterable[str] = ("token", "password", "secret", "authorization")) -> object:
    if isinstance(value, dict):
        keys = {k.casefold() for k in sensitive_keys}
        return {k: ("[REDACTED]" if str(k).casefold() in keys else redact(v, sensitive_keys)) for k, v in value.items()}
    if isinstance(value, list):
        return [redact(v, sensitive_keys) for v in value]
    return value
