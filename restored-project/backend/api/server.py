# -*- coding: utf-8 -*-
"""Local HTTP API; binds to localhost only."""
from __future__ import annotations
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler
from pathlib import Path
import json, threading, urllib.parse
from core.runtime import ALIRuntime

class _Handler(BaseHTTPRequestHandler):
    runtime: ALIRuntime=None; project_dir:Path=Path('.')
    def _json(self,status,obj):
        data=json.dumps(obj,ensure_ascii=False).encode('utf-8'); self.send_response(status); self.send_header('Content-Type','application/json; charset=utf-8'); self.send_header('Content-Length',str(len(data))); self.end_headers(); self.wfile.write(data)
    def do_GET(self):
        if self.path=='/health': return self._json(200,{'ok':True,'service':'ALI Studio','version':'3.0.0'})
        if self.path=='/api/hardware':
            from runtime.hardware import detect,training_profile,model_profile; h=detect(); return self._json(200,{'hardware':h.to_dict(),'training':training_profile(h),'model':model_profile(h)})
        return self._json(404,{'ok':False,'error':'not found'})
    def do_POST(self):
        n=int(self.headers.get('Content-Length','0')); raw=self.rfile.read(n)
        try: body=json.loads(raw.decode('utf-8'))
        except Exception: return self._json(400,{'ok':False,'error':'invalid json'})
        if self.path=='/api/chat':
            return self._json(200,self.runtime.answer(body.get('messages',[]),body.get('project_dir',str(self.project_dir)),body.get('system','')))
        if self.path=='/api/ingest':
            from data_engine.harvester import Harvester
            h=Harvester(self.project_dir/'harvest.sqlite3'); return self._json(200,h.scan(body.get('root',str(self.project_dir))))
        if self.path=='/api/research':
            if not self.runtime.allow_internet: return self._json(403,{'ok':False,'error':'internet research disabled'})
            from research.web import research; return self._json(200,research(body.get('query',''),int(body.get('limit',5))))
        return self._json(404,{'ok':False,'error':'not found'})
    def log_message(self,*a): pass

def serve(runtime:ALIRuntime,host='127.0.0.1',port=8765,project_dir='.'):
    _Handler.runtime=runtime; _Handler.project_dir=Path(project_dir).resolve(); server=ThreadingHTTPServer((host,port),_Handler); server.serve_forever()
