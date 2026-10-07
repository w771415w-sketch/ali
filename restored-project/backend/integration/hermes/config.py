from __future__ import annotations
from dataclasses import dataclass, asdict
from pathlib import Path
import json, os

DEFAULT_HERMES_ROOT = Path(r"D:\AI ALI\Hermes")

@dataclass
class HermesConfig:
    enabled: bool = True
    root: str = str(DEFAULT_HERMES_ROOT)
    read_only: bool = True
    max_file_bytes: int = 2_000_000
    max_context_chars: int = 8_000
    allow_database_reads: bool = True
    allow_api: bool = False
    allow_mcp: bool = False

    def to_dict(self):
        return asdict(self)

def load_config(path: str | Path | None = None) -> HermesConfig:
    p = Path(path) if path else Path(__file__).resolve().parents[2] / "config" / "hermes_integration.json"
    data = {}
    try:
        if p.exists():
            data = json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        data = {}
    env_root = os.environ.get("ALI_HERMES_ROOT", "").strip()
    if env_root:
        data["root"] = env_root
    return HermesConfig(**{k:v for k,v in data.items() if k in HermesConfig.__dataclass_fields__})
