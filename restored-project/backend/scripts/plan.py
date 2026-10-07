# -*- coding: utf-8 -*-
from __future__ import annotations
import argparse,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent; sys.path.insert(0,str(ROOT))
from core.orchestrator import Orchestrator
from runtime.hardware import detect
from training.scaling import build_training_plan
class DummyRuntime: pass

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('request'); ap.add_argument('--scale',default='small'); args=ap.parse_args()
    o=Orchestrator(DummyRuntime()); plan=o.make_plan(args.request); out={'orchestration':plan.to_dict()}
    if plan.intent=='training': out['training_plan']=build_training_plan(args.scale,detect())
    print(json.dumps(out,ensure_ascii=False,indent=2))
if __name__=='__main__':main()
