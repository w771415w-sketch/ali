#!/usr/bin/env python
"""Prepare a duplicate-safe incremental dataset from harvested data + new conversations."""
from __future__ import annotations
from pathlib import Path
import argparse,json,sys,time
ROOT=Path(__file__).resolve().parents[1]; sys.path.insert(0,str(ROOT))

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--db',default='artifacts/harvest.sqlite3'); ap.add_argument('--conversation-db',default='runtime_conversations.sqlite3'); ap.add_argument('--min-new',type=int,default=24); args=ap.parse_args()
    from autonomy.continuous import ContinuousLearning
    from data_engine.dataset_builder import export_incremental,export_conversation_incremental
    cl=ContinuousLearning(ROOT,args.min_new); plan=cl.plan(ROOT/args.db,ROOT/args.conversation_db)
    print(json.dumps(plan,ensure_ascii=False,indent=2))
    if not plan['train_needed']: return 0
    st=cl._read(); after_id=int(st.get('last_trained_sample_id',0)); after_ts=float(st.get('conversation_trained_at',0.0))
    parts=[]
    a=ROOT/'data/training/incremental/harvest.jsonl'; b=ROOT/'data/training/incremental/conversations.jsonl'
    if Path(args.db).exists(): parts.append(export_incremental(ROOT/args.db,a,after_id))
    if Path(args.conversation_db).exists(): parts.append(export_conversation_incremental(ROOT/args.conversation_db,b,after_ts,min_quality=.6))
    # Merge by stable sample hash so the same conversation cannot be trained twice.
    merged=ROOT/'data/training/incremental/current.jsonl'; merged.parent.mkdir(parents=True,exist_ok=True); seen=set(); written=0
    with merged.open('w',encoding='utf-8') as out:
        for part in parts:
            p=Path(part['output'])
            if not p.exists(): continue
            for line in p.read_text(encoding='utf-8').splitlines():
                if not line.strip(): continue
                obj=json.loads(line); h=str(obj.get('id',''))
                if not h or h in seen: continue
                seen.add(h); out.write(json.dumps(obj,ensure_ascii=False)+'\n'); written+=1
    manifest={'plan':plan,'parts':parts,'incremental':{'samples':written,'output':str(merged),'ids':sorted(seen)},'resume_checkpoint':st.get('last_checkpoint',''),'operator_action':'train-candidate'}
    out=ROOT/'artifacts/continuous_plan.json'; out.parent.mkdir(parents=True,exist_ok=True); out.write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8'); print(json.dumps(manifest,ensure_ascii=False,indent=2)); return 0
if __name__=='__main__': raise SystemExit(main())
