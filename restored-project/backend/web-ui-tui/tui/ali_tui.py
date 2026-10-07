#!/usr/bin/env python
from __future__ import annotations
from pathlib import Path
import argparse, json, sys, urllib.request
ROOT=Path(__file__).resolve().parents[2]
def main():
 ap=argparse.ArgumentParser(); ap.add_argument('prompt',nargs='*'); ap.add_argument('--host',default='127.0.0.1'); ap.add_argument('--port',default=8765,type=int); a=ap.parse_args(); q=' '.join(a.prompt).strip() or input('ALI> ')
 data=json.dumps({'messages':[{'role':'user','content':q}]}).encode(); req=urllib.request.Request(f'http://{a.host}:{a.port}/api/chat',data=data,headers={'Content-Type':'application/json'})
 try:
  with urllib.request.urlopen(req,timeout=120) as r: x=json.loads(r.read().decode())
  print('ALI:',x.get('text',''))
 except Exception as e: print('ALI TUI error:',e)
if __name__=='__main__': main()
