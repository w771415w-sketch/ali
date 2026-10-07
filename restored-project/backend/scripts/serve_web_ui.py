#!/usr/bin/env python
from http.server import ThreadingHTTPServer,SimpleHTTPRequestHandler
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]/'web-ui-tui'/'web'
if __name__=='__main__':
 import os
 os.chdir(ROOT); print('ALI Web UI: http://127.0.0.1:8090'); ThreadingHTTPServer(('127.0.0.1',8090),SimpleHTTPRequestHandler).serve_forever()
