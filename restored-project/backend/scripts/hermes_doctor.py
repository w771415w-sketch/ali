from __future__ import annotations
from pathlib import Path
import json
from integration.hermes.config import load_config
from integration.hermes.adapter import HermesAdapter

root=Path(__file__).resolve().parents[1]
cfg=load_config(root/'config'/'hermes_integration.json')
a=HermesAdapter(cfg)
report={'hermes':a.status(), 'blocked': ['.env','auth.json','credentials.json','*.key','*.pem']}
print(json.dumps(report,ensure_ascii=False,indent=2))
raise SystemExit(0 if (not cfg.enabled or report['hermes']['exists']) else 2)
