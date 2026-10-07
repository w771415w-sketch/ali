from __future__ import annotations
from http.server import BaseHTTPRequestHandler,ThreadingHTTPServer
import json
from .runtime_facade import ProfessionalRuntime
class Gateway:
    def __init__(self,runtime): self.runtime=runtime
    def handle(self,path,payload):
        if path=="/health": return 200,self.runtime.health()
        if path=="/prepare": return 200,self.runtime.prepare(str(payload.get("text","")),payload.get("project_id"))
        if path=="/execute": return 200,self.runtime.execute(str(payload.get("text","")),project_id=payload.get("project_id"),operations=payload.get("operations"),checks=payload.get("checks"),approved=bool(payload.get("approved")),dry_run=bool(payload.get("dry_run")),idempotency_key=payload.get("idempotency_key"))
        if path=="/settings": return 200,self.runtime.settings_snapshot(payload.get("model_metadata"))
        if path=="/language/profile":
            return 200,self.runtime.save_language_profile(str(payload.get("profile_id","")))
        if path=="/language/adapt":
            return 200,self.runtime.adapt_language(str(payload.get("text","")),payload.get("preferred_profile"))
        if path=="/training/preflight":
            return 200,self.runtime.training_preflight(payload.get("scale","small"),int(payload.get("steps",0) or 0))
        if path=="/training/options":
            return 200,self.runtime.settings_snapshot(payload.get("model_metadata"))
        if path=="/training/create":
            return 200,self.runtime.create_training_job(str(payload.get("name","training")),payload.get("scale","small"),int(payload.get("steps",0) or 0))
        if path=="/diagnose/file": return 200,self.runtime.diagnose_file(str(payload.get("path","")))
        if path=="/diagnose/archive": return 200,self.runtime.diagnose_archive(str(payload.get("path","")))
        if path=="/diagnose/project": return 200,self.runtime.diagnose_project(str(payload.get("path","")))
        return 404,{"ok":False,"error":"not_found"}
def serve(runtime,host="127.0.0.1",port=8765):
    gateway=Gateway(runtime)
    class Handler(BaseHTTPRequestHandler):
        def _json(self,status,data):
            raw=json.dumps(data,ensure_ascii=False).encode("utf-8");self.send_response(status);self.send_header("Content-Type","application/json; charset=utf-8");self.send_header("Content-Length",str(len(raw)));self.end_headers();self.wfile.write(raw)
        def do_GET(self):
            status,data=gateway.handle(self.path,{}) if self.path in {"/health","/settings"} else (404,{"ok":False,"error":"not_found"});self._json(status,data)
        def do_POST(self):
            try:
                n=int(self.headers.get("Content-Length","0"));payload=json.loads(self.rfile.read(n) or b"{}");status,data=gateway.handle(self.path,payload);self._json(status,data)
            except Exception as e:self._json(400,{"ok":False,"error":str(e)})
        def log_message(self,*args): return
    server=ThreadingHTTPServer((host,int(port)),Handler)
    try: server.serve_forever()
    finally: server.server_close()
