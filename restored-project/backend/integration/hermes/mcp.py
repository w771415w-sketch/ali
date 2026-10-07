from __future__ import annotations
"""MCP configuration boundary for a future Hermes MCP endpoint."""
from dataclasses import dataclass

@dataclass
class HermesMcpBridge:
    enabled: bool = False
    endpoint: str = ""

    def status(self):
        return {"enabled":self.enabled,"endpoint":self.endpoint,"configured":bool(self.endpoint) and self.enabled}
