# -*- coding: utf-8 -*-
"""Install ALI Training Update v1 into this ALI project as a model candidate."""
from pathlib import Path
import hashlib,json,shutil,sys,argparse

def sha256(p):
    h=hashlib.sha256();
    with open(p,'rb') as f:
        for chunk in iter(lambda:f.read(1024*1024),b''): h.update(chunk)
    return h.hexdigest()

ap=argparse.ArgumentParser(); ap.add_argument('project',nargs='?',default=None); ap.add_argument('--promote',action='store_true'); args=ap.parse_args()
project=Path(args.project).resolve() if args.project else Path(__file__).resolve().parents[5]
pkg=Path(__file__).resolve().parents[1]
backend=project/'backend'
if not (backend/'models'/'models.sqlite3').exists(): raise SystemExit(f'ALI backend registry not found: {backend}')
merged=pkg/'weights'/'merged_hf'
adapter=pkg/'weights'/'adapter'
# Integrated project stores these under sibling folders rather than package wrappers.
if not merged.exists():
    merged=project/'backend'/'models'/'inbox'/'ALI-v1'
if not adapter.exists():
    adapter=project/'backend'/'models'/'adapters'/'pending'/'ALI-v1'
for f in ('config.json','model.safetensors','tokenizer.model','tokenizer_config.json','special_tokens_map.json'):
    if not (merged/f).exists(): raise SystemExit(f'missing merged artifact: {merged/f}')
if not (adapter/'adapter_model.safetensors').exists(): raise SystemExit('missing adapter_model.safetensors')
dst=backend/'models'/'merged'/'ALI'/'v1'; dst.parent.mkdir(parents=True,exist_ok=True)
if dst.exists(): shutil.rmtree(dst); shutil.copytree(merged,dst)
else: shutil.copytree(merged,dst)
adst=backend/'models'/'adapters'/'ALI'/'v1'; adst.parent.mkdir(parents=True,exist_ok=True)
if adst.exists(): shutil.rmtree(adst); shutil.copytree(adapter,adst)
else: shutil.copytree(adapter,adst)
# Register candidate with relative paths for portability.
sys.path.insert(0,str(backend)); from model.registry import ModelRegistry
reg=ModelRegistry(backend/'models'/'models.sqlite3')
manifest=json.loads((project/'backend'/'training'/'updates'/'v1'/'UPDATE_MANIFEST.json').read_text(encoding='utf-8')) if (project/'backend'/'training'/'updates'/'v1'/'UPDATE_MANIFEST.json').exists() else {}
reg.register('ALI','v1',artifact_type='merged',status='candidate',base_version='2.5.0-bootstrap-micro',checkpoint=str(Path('models/merged/ALI/v1')),hf_dir=str(Path('models/merged/ALI/v1')),adapter=str(Path('models/adapters/ALI/v1')),dataset_hash=sha256(project/'backend'/'training'/'updates'/'v1'/'data'/'train.jsonl'),train_config={'update':'v1','steps':200,'rank':16,'alpha':32},eval=json.loads((project/'backend'/'training'/'updates'/'v1'/'docs'/'EVALUATION.json').read_text()) if (project/'backend'/'training'/'updates'/'v1'/'docs'/'EVALUATION.json').exists() else {})
if args.promote:
    reg.promote('ALI','v1')
print(json.dumps({'ok':True,'version':'v1','promoted':args.promote,'candidate':not args.promote,'merged':str(dst),'adapter':str(adst)},ensure_ascii=False,indent=2))
