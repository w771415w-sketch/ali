from __future__ import annotations

import json
import threading
import urllib.parse
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Any

from ..core.config import RuntimeConfig
from ..core.contracts import ExecutionRequest, Operation
from ..core.security import RateLimiter, TokenAuth, remote_address_allowed, redact
from ..core.orchestrator import Orchestrator


class ALIServer:
    """Hardened loopback-first JSON API for the ALI runtime."""

    def __init__(self, runtime: Orchestrator, config: RuntimeConfig):
        self.runtime = runtime
        self.config = config
        self.auth = TokenAuth(config.api_token)
        self.rate = RateLimiter(config.rate_limit, config.rate_window_seconds)
        self.server = ThreadingHTTPServer((config.host, config.port), self._handler())
        self.server.daemon_threads = True

    def _handler(self):
        runtime = self.runtime
        config = self.config
        auth = self.auth
        limiter = self.rate

        class Handler(BaseHTTPRequestHandler):
            server_version = "ALI/1.0"

            def _send(self, status: int, data: dict[str, Any]) -> None:
                raw = json.dumps(redact(data), ensure_ascii=False).encode("utf-8")
                self.send_response(status)
                self.send_header("Content-Type", "application/json; charset=utf-8")
                self.send_header("Cache-Control", "no-store")
                self.send_header("X-Content-Type-Options", "nosniff")
                self.send_header("Content-Length", str(len(raw)))
                self.end_headers()
                self.wfile.write(raw)

            def _authorized(self) -> bool:
                client = self.client_address[0] if self.client_address else ""
                if not remote_address_allowed(client):
                    return False
                if client not in {"127.0.0.1", "::1", "localhost"} and not config.allow_remote:
                    return False
                if self.command == "GET" and self.path == "/health":
                    return True
                auth_header = self.headers.get("Authorization", "")
                supplied = auth_header[7:].strip() if auth_header.lower().startswith("bearer ") else None
                return auth.verify(supplied)

            def _rate_ok(self) -> bool:
                client = self.client_address[0] if self.client_address else "unknown"
                return limiter.allow(client)

            def _json_body(self) -> dict[str, Any]:
                length = int(self.headers.get("Content-Length", "0") or 0)
                if length <= 0:
                    return {}
                if length > config.max_body_bytes:
                    raise ValueError("request body too large")
                return json.loads(self.rfile.read(length).decode("utf-8"))

            def do_GET(self) -> None:
                if not self._rate_ok():
                    self._send(429, {"ok": False, "status": "rate_limited"})
                    return
                if not self._authorized():
                    self._send(401, {"ok": False, "status": "unauthorized"})
                    return
                path = urllib.parse.urlparse(self.path).path
                if path == "/health":
                    self._send(200, runtime.health())
                elif path == "/config":
                    self._send(200, runtime.config_public())
                else:
                    self._send(404, {"ok": False, "status": "not_found"})

            def do_POST(self) -> None:
                if not self._rate_ok():
                    self._send(429, {"ok": False, "status": "rate_limited"})
                    return
                if not self._authorized():
                    self._send(401, {"ok": False, "status": "unauthorized"})
                    return
                try:
                    path = urllib.parse.urlparse(self.path).path
                    payload = self._json_body()
                    if path == "/prepare":
                        self._send(200, runtime.prepare(str(payload.get("text", "")), payload.get("project_id")))
                        return
                    if path == "/execute":
                        operations = [
                            Operation(
                                action=str(item.get("action", "write")),
                                path=str(item.get("path", "")),
                                content=item.get("content"),
                                expected_sha256=item.get("expected_sha256"),
                            )
                            for item in payload.get("operations", [])
                        ]
                        request = ExecutionRequest(
                            text=str(payload.get("text", "")),
                            project_id=payload.get("project_id"),
                            operations=operations,
                            checks=[str(x) for x in payload.get("checks", [])],
                            approved=bool(payload.get("approved", False)),
                            dry_run=bool(payload.get("dry_run", False)),
                            idempotency_key=payload.get("idempotency_key"),
                        )
                        result = runtime.execute(request)
                        self._send(200 if result.get("ok") or result.get("status") in {"approval_required", "dry_run"} else 422, result)
                        return
                    if path.startswith("/diagnose/"):
                        kind = path.rsplit("/", 1)[-1]
                        self._send(200, runtime.diagnose(kind, str(payload.get("path", ""))))
                        return
                    self._send(404, {"ok": False, "status": "not_found"})
                except Exception as exc:
                    self._send(400, {"ok": False, "status": "bad_request", "error": f"{type(exc).__name__}: {exc}"})

            def log_message(self, fmt: str, *args: object) -> None:
                return

        return Handler

    def serve_forever(self) -> None:
        self.server.serve_forever()

    def shutdown(self) -> None:
        self.server.shutdown()
        self.server.server_close()


def serve(runtime: Orchestrator, config: RuntimeConfig) -> ALIServer:
    server = ALIServer(runtime, config)
    thread = threading.Thread(target=server.serve_forever, name="ali-http", daemon=True)
    thread.start()
    return server
