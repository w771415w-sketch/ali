from __future__ import annotations

import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CONFIG = ROOT / "config" / "default.json"


def _as_bool(value: str | None, default: bool) -> bool:
    if value is None:
        return default
    return value.strip().casefold() in {"1", "true", "yes", "on"}


def _as_int(value: str | None, default: int) -> int:
    try:
        return int(value) if value is not None else default
    except ValueError:
        return default


def default_workspace() -> Path:
    """Return an OS-appropriate persistent ALI runtime directory."""
    if os.name == "nt":
        root = os.getenv("LOCALAPPDATA") or os.getenv("APPDATA")
        if root:
            return Path(root) / "ALI Studio Pro" / "workspace"
    root = os.getenv("XDG_STATE_HOME")
    if root:
        return Path(root) / "ali-studio-pro" / "workspace"
    return Path.home() / ".local" / "state" / "ali-studio-pro" / "workspace"


@dataclass(frozen=True)
class RuntimeConfig:
    host: str
    port: int
    allow_remote: bool
    api_token: str
    workspace: Path
    max_body_bytes: int
    rate_limit: int
    rate_window_seconds: int
    backend_module: str
    backend_class: str
    hardware: dict[str, Any]

    @property
    def is_loopback(self) -> bool:
        return self.host in {"127.0.0.1", "localhost", "::1"}

    def to_public_dict(self) -> dict[str, Any]:
        return {
            "host": self.host,
            "port": self.port,
            "allow_remote": self.allow_remote,
            "api_token_configured": bool(self.api_token),
            "workspace": str(self.workspace),
            "max_body_bytes": self.max_body_bytes,
            "rate_limit": self.rate_limit,
            "rate_window_seconds": self.rate_window_seconds,
            "backend": {"module": self.backend_module, "class": self.backend_class},
            "hardware": self.hardware,
        }


def load_config(path: str | Path | None = None) -> RuntimeConfig:
    config_path = Path(path) if path else DEFAULT_CONFIG
    data = json.loads(config_path.read_text(encoding="utf-8"))
    server = data["server"]
    backend = data["backend"]
    workspace_value = os.getenv("ALI_WORKSPACE", "").strip()
    workspace = Path(workspace_value) if workspace_value else default_workspace()
    workspace = workspace.expanduser().resolve()
    cfg = RuntimeConfig(
        host=os.getenv("ALI_HOST", server["host"]),
        port=_as_int(os.getenv("ALI_PORT"), int(server["port"])),
        allow_remote=_as_bool(os.getenv("ALI_ALLOW_REMOTE"), bool(server["remote_access"])),
        api_token=os.getenv("ALI_API_TOKEN", "").strip(),
        workspace=workspace,
        max_body_bytes=max(4096, _as_int(os.getenv("ALI_MAX_BODY_BYTES"), int(server["max_body_bytes"]))),
        rate_limit=max(1, _as_int(os.getenv("ALI_RATE_LIMIT"), int(server["request_rate_limit"]))),
        rate_window_seconds=max(1, _as_int(os.getenv("ALI_RATE_WINDOW_SECONDS"), int(server["request_rate_window_seconds"]))),
        backend_module=str(backend["module"]),
        backend_class=str(backend["class"]),
        hardware=dict(data.get("hardware", {})),
    )
    if not cfg.is_loopback and not cfg.allow_remote:
        raise ValueError("Non-loopback ALI API binding requires ALI_ALLOW_REMOTE=true")
    if not cfg.is_loopback and not cfg.api_token:
        raise ValueError("Remote ALI API binding requires ALI_API_TOKEN")
    cfg.workspace.mkdir(parents=True, exist_ok=True)
    return cfg
