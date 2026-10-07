# -*- coding: utf-8 -*-
from __future__ import annotations
import argparse,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent; sys.path.insert(0,str(ROOT))
from tools.gguf import GGUFManager
from inference.gguf_runtime import LlamaServer

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('model'); ap.add_argument('--port',type=int,default=8080); ap.add_argument('--context',type=int,default=2048); ap.add_argument('--llama-dir',default='vendor/llama.cpp'); args=ap.parse_args()
    mgr=GGUFManager(ROOT/args.llama_dir); exe=mgr.root/'build'/'bin'/'llama-server.exe'
    if not exe.exists(): exe=mgr.root/'build'/'bin'/'llama-server'
    server=LlamaServer(exe,Path(args.model),args.port,args.context); server.start(); print(f'ALI AI GGUF server: {server.base_url}\nPress Ctrl+C to stop.')
    try:
        while True: input()
    except KeyboardInterrupt: server.stop()
if __name__=='__main__':main()
