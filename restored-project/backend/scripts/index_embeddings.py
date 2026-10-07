# -*- coding: utf-8 -*-
from pathlib import Path
import sys,json,argparse
ROOT=Path(__file__).resolve().parent.parent; sys.path.insert(0,str(ROOT))
from model.registry import ModelRegistry
from inference.engine import LocalInference
from knowledge.embeddings import index_store
ap=argparse.ArgumentParser(); ap.add_argument('--model-dir',required=True); ap.add_argument('--tokenizer-dir',default='weights/tokenizer'); ap.add_argument('--db',default='runtime_knowledge.sqlite3'); ap.add_argument('--device',default='auto'); args=ap.parse_args()
dev='cuda' if args.device=='auto' else args.device; e=LocalInference(args.model_dir,args.tokenizer_dir,device=dev); print(json.dumps({'indexed':index_store(ROOT/args.db,e.model,e.tokenizer)},ensure_ascii=False,indent=2))
