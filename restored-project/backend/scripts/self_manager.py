# -*- coding: utf-8 -*-
from pathlib import Path
import argparse,json,sys
ROOT=Path(__file__).resolve().parent.parent; sys.path.insert(0,str(ROOT))
from autonomy.self_manager import SelfManager

def main():
    ap=argparse.ArgumentParser(description='Show ALI self-training readiness.'); ap.add_argument('--db',default='artifacts/harvest.sqlite3'); ap.add_argument('--conversation-db',default='runtime_conversations.sqlite3'); ap.add_argument('--min-new',type=int,default=32); ap.add_argument('--auto',action='store_true',help='run one gated self-learning cycle when enough approved samples exist'); ap.add_argument('--force',action='store_true'); ap.add_argument('--steps',type=int,default=1); args=ap.parse_args()
    sm=SelfManager(ROOT,args.min_new)
    if args.auto:
        result=sm.autonomous_cycle(ROOT/args.db, ROOT/args.conversation_db, scale='micro', steps=max(1,args.steps), device='cpu', force=args.force)
        print(json.dumps(result,ensure_ascii=False,indent=2))
    else:
        print(json.dumps(sm.status(ROOT/args.db, ROOT/args.conversation_db),ensure_ascii=False,indent=2))
if __name__=='__main__': main()
