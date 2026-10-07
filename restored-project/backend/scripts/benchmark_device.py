# -*- coding: utf-8 -*-
"""Small deterministic ALI device benchmark. No model training/downloads."""
from __future__ import annotations
import json, time, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT))
from runtime.hardware import detect, training_profile, model_profile

def main():
    import torch
    h=detect(); tp=training_profile(h)
    torch.set_num_threads(int(tp.get('cpu_threads', max(1,h.cpu_cores-2))))
    x=torch.randn(256,256); y=torch.randn(256,256)
    for _ in range(3): _=x@y
    t=time.perf_counter();
    for _ in range(20): _=x@y
    elapsed=time.perf_counter()-t
    print(json.dumps({'hardware':h.to_dict(),'training_profile':tp,'model_profile':model_profile(h),'matmul_256x256_20_iters_sec':round(elapsed,4),'notes':['Micro benchmark only; not a language-model throughput measurement.']},ensure_ascii=False,indent=2))
if __name__=='__main__': main()
