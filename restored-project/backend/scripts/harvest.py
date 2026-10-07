# -*- coding: utf-8 -*-
from pathlib import Path
import argparse,sys,json
ROOT=Path(__file__).resolve().parent.parent; sys.path.insert(0,str(ROOT))
from data_engine.harvester import Harvester
from training.dataset import build_chat_dataset,build_causal_dataset

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('root'); ap.add_argument('--db',default='artifacts/harvest.sqlite3'); ap.add_argument('--export',default='data/train'); args=ap.parse_args()
    h=Harvester(ROOT/args.db); s=h.scan(args.root); print(json.dumps(s,ensure_ascii=False,indent=2)); print(build_chat_dataset(ROOT/args.db,ROOT/args.export)); print(build_causal_dataset(ROOT/args.db,ROOT/args.export))
if __name__=='__main__': main()
