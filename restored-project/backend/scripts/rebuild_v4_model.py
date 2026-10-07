# -*- coding: utf-8 -*-
"""Rebuild an independent V4 model from the verified cumulative dataset available in the source bundle."""
from __future__ import annotations
from pathlib import Path
import json, hashlib, shutil, sys, time

ROOT = Path(__file__).resolve().parents[1]   # backend
PROJECT = ROOT.parent
sys.path.insert(0, str(ROOT))

from model.registry import ModelRegistry, file_hash
from training.pipeline import TrainingPipeline, PipelineConfig
from tokenizer.manager import TokenizerManager
from training.generation_lineage import sha256_file


def make_eval_set(src: Path, out: Path, limit: int = 60):
    rows=[]
    with src.open('r',encoding='utf-8') as f:
        for line in f:
            if line.strip():
                try:
                    o=json.loads(line)
                except Exception: continue
                if isinstance(o,dict): rows.append(o)
    rows=rows[-limit:] if len(rows)>limit else rows
    out.parent.mkdir(parents=True,exist_ok=True)
    with out.open('w',encoding='utf-8') as f:
        for r in rows: f.write(json.dumps(r,ensure_ascii=False,sort_keys=True)+'\n')
    return len(rows)


def main():
    cumulative = ROOT/'models/generations/v4/cumulative/train.jsonl'
    if not cumulative.exists(): raise SystemExit(f'missing cumulative dataset: {cumulative}')
    generation_dir = ROOT/'models/generations/v4'
    eval_path = generation_dir/'evaluation'/'diagnostic_validation.jsonl'
    n_eval=make_eval_set(cumulative, eval_path)
    tokenizer = TokenizerManager(ROOT)
    tok_info = tokenizer.train([cumulative], vocab_size=2048, name='ALI', version='v4-rebuilt', force=False)
    hw = None
    from runtime.hardware import detect, training_profile
    hw = detect(probe_torch=True, force=True)
    profile = training_profile(hw, mode='cpu')
    cfg = PipelineConfig(
        name='ALI', stage='base', scale='small',
        train_path=str(cumulative), validation_path=str(eval_path),
        tokenizer_vocab_size=2048,
        max_steps=100, epochs=1, max_seq_len=256, batch_size=1,
        grad_accum=8, learning_rate=3e-4, device='cpu',
        curriculum=True, world_size=1,
    )
    pipeline=TrainingPipeline(ROOT, hardware=hw)
    result=pipeline.run(cfg)
    run_id=result['run_id']
    checkpoint=Path(result['checkpoint'])
    hf_dir=Path(result['hf_dir'])
    # Create the stable deployment copy inside the generation directory; it is independent of run paths.
    stable_hf=generation_dir/'artifacts'/'merged_hf'
    if stable_hf.exists(): shutil.rmtree(stable_hf)
    shutil.copytree(hf_dir, stable_hf)
    manifest_hash=file_hash(stable_hf)
    dataset_hash=sha256_file(cumulative)
    report={
      'generation':'v4','status':'rebuilt','reconstruction':'from_verified_source_datasets',
      'historical_model_weights_available':False,'source_dataset':str(cumulative),
      'cumulative_dataset_hash':dataset_hash,'cumulative_samples':sum(1 for _ in cumulative.open(encoding='utf-8')),
      'tokenizer':tok_info,'hardware':hw.to_dict(),'training_profile':profile,
      'training_config':cfg.to_dict(),'run_id':run_id,'checkpoint':str(checkpoint),
      'merged_hf':str(stable_hf),'merged_hf_hash':manifest_hash,'evaluation':result.get('evaluation',{}),
      'diagnostic_validation_samples':n_eval,'created_at':time.time(),
      'gguf':{'status':'pending_converter','reason':'llama.cpp Windows converter binary not included in source bundle'}
    }
    (generation_dir/'rebuild_report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(report,ensure_ascii=False,indent=2))

if __name__=='__main__': raise SystemExit(main())
