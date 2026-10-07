from __future__ import annotations
"""Optional future API bridge. No Hermes endpoint is assumed without explicit configuration."""
from dataclasses import dataclass
import urllib.request, json

@dataclass
class HermesApiBridge:
    base_url: str = ""
    enabled: bool = False

    def health(self):
        if not (self.enabled and self.base_url):
            return {"enabled":False,"status":"not-configured"}
        req=urllib.request.Request(self.base_url.rstrip('/') + "/health", method="GET")
        try:
            with urllib.request.urlopen(req, timeout=3) as r:
                body=r.read().decode('utf-8','replace')[:4000]
            try: return {"enabled":True,"status":"ok","data":json.loads(body)}
            except Exception: return {"enabled":True,"status":"ok","data":body}
        except Exception as e:
            return {"enabled":True,"status":"unavailable","error":str(e)}
