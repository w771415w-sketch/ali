# -*- coding: utf-8 -*-
from pathlib import Path
import sys,json,argparse
ROOT=Path(__file__).resolve().parent.parent; sys.path.insert(0,str(ROOT))
from inference.engine import LocalInference
from training.evaluator import evaluate_model
ap=argparse.ArgumentParser(); ap.add_argument('--model-dir',required=True); ap.add_argument('--test',required=True); ap.add_argument('--tokenizer-dir',default='weights/tokenizer'); ap.add_argument('--device',default='auto'); args=ap.parse_args()
dev='cuda' if args.device=='auto' else args.device; e=LocalInference(args.model_dir,args.tokenizer_dir,device=dev); print(json.dumps(evaluate_model(e.model,e.tokenizer,args.test,dev),ensure_ascii=False,indent=2))
