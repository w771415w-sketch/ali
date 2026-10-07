# -*- coding: utf-8 -*-
"""Install an ALI Training Update v1 into an existing ALI Studio project.
Default behavior is candidate-only. Use --promote only after verifying the artifact.
"""
from pathlib import Path
import argparse, hashlib, json, shutil, sys

def sha256(p):
    h=hashlib.sha256();
    with open(p,'rb') as f:
        for chunk in iter(lambda:f.read(1024*1024),b''): h.update(chunk)
    return h.hexdigest()

ap=argparse.ArgumentParser(); ap.add_argument('project'); ap.add_argument('--promote',action='store_true'); args=ap.parse_args()
root=Path(args.project).resolve(); pkg=Path(__file__).resolve().parents[1]
backend=root/'backend'
if not (backend/'models'/'models.sqlite3').exists(): raise SystemExit('ALI project backend/model registry not found')
# validate model files
for f in ['config.json','model.safetensors','tokenizer.model','tokenizer_config.json','special_tokens_map.json']:
    p=pkg/'weights'/'merged_hf'/f
    if not p.exists(): raise SystemExit(f'missing artifact: {p}')
# Copy into a versioned inbox path.
dst=backend/'models'/'inbox'/'ALI-v1'
if dst.exists(): shutil.rmtree(dst)
shutil.copytree(pkg/'weights'/'merged_hf',dst)
adst=backend/'models'/'adapters'/'pending'/'ALI-v1'
adst.mkdir(parents=True,exist_ok=True)
shutil.copy2(pkg/'weights'/'adapter'/'adapter_model.safetensors',adst/'adapter_model.safetensors')
shutil.copy2(pkg/'weights'/'adapter'/'adapter_config.json',adst/'adapter_config.json')
# Register candidate in the existing registry.
sys.path.insert(0,str(backend)); from model.registry import ModelRegistry
reg=ModelRegistry(backend/'models'/'models.sqlite3')
train_hash=sha256(pkg/'data'/'train.jsonl')
reg.register('ALI','v1',artifact_type='merged',status='candidate',base_version='2.5.0-bootstrap-micro',checkpoint=str(dst),hf_dir=str(dst),adapter=str(adst),dataset_hash=train_hash,train_config={'source':'ALI_training_update_v1'},eval=json.loads((pkg/'docs'/'EVALUATION_REPORT.json').read_text()) if (pkg/'docs'/'EVALUATION_REPORT.json').exists() else {})
if args.promote:
    reg.promote('ALI','v1')
print(json.dumps({'ok':True,'version':'v1','candidate':not args.promote,'promoted':args.promote,'hf_dir':str(dst),'adapter':str(adst)},ensure_ascii=False,indent=2))
