        print(json.dumps(check, ensure_ascii=False, indent=2))
        return 2
    manifest_path = generation_manifest_path(ROOT / 'models', generation)
    data = json.loads(manifest_path.read_text(encoding='utf-8'))
    out = Path(args.output) if args.output else ROOT / 'releases' / f'ALI-{generation}-Package'
    if not out.is_absolute():
        out = ROOT / out
    if out.exists():
        shutil.rmtree(out)
    for directory in ('model', 'manifests', 'datasets', 'evaluation'):
        (out / directory).mkdir(parents=True, exist_ok=True)
    artifacts = data.get('artifacts') or {}
    copied = []
    for key in ('gguf_q4_k_m', 'gguf_f16', 'merged_hf'):
        src = resolve_path(artifacts.get(key))
        if src and src.exists():
            dest = out / 'model' / src.name
            copy_path(src, dest)
            copied.append({'kind': key, 'source': str(src), 'destination': str(dest.relative_to(out))})
            if key == 'gguf_q4_k_m':
                break
    for source, target in (
        (manifest_path, out / 'manifests' / 'generation.json'),
        (manifest_path.parent / 'lineage.json', out / 'manifests' / 'lineage.json'),
        (manifest_path.parent / 'cumulative_report.json', out / 'datasets' / 'cumulative_report.json'),
    ):
        if source.exists():
            shutil.copy2(source, target)
    for key, target in (('cumulative_dataset', 'cumulative_train.jsonl'), ('delta_dataset', 'delta_train.jsonl')):
        value = data.get(key) or {}
        value = value.get('path') if isinstance(value, dict) else value
        src = resolve_path(value)
        if src and src.exists():
            shutil.copy2(src, out / 'datasets' / target)
    eval_dir = manifest_path.parent / 'evaluation'
    if eval_dir.exists():
        for src in eval_dir.glob('*.jsonl'):
            shutil.copy2(src, out / 'evaluation' / src.name)
    checksums = {}
    for file in sorted(out.rglob('*')):
        if file.is_file():
            checksums[str(file.relative_to(out)).replace('\\', '/')] = file_hash(file)
    (out / 'manifests' / 'checksums.json').write_text(json.dumps(checksums, ensure_ascii=False, indent=2, sort_keys=True) + '\n', encoding='utf-8')
    parent = data.get('parent_generation', '')
    samples = (data.get('cumulative_dataset') or {}).get('samples', 0)
    (out / 'README.md').write_text(
        '# ALI {} Package\n\nIndependent ALI generation package.\n\nGeneration: {}\nParent: {}\nCumulative samples: {}\n\nArchived generations are not runtime dependencies.\n'.format(generation, generation, parent, samples),
        encoding='utf-8',
    )
    print(json.dumps({'ok': True, 'generation': generation, 'output': str(out), 'files': len(checksums), 'copied': copied, 'created_at': time.time()}, ensure_ascii=False, indent=2))
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
```

---

### `346/588` `backend/scripts/plan.py`

- **المسار الكامل:** `F:\1f\p\ALI_Studio_Pro_Design4_4.6.0\04_Adaptive_Hybrid\backend/scripts/plan.py`
- **الحجم:** 761 بايت (0.7 KB)
- **الامتداد:** `.py`

```python
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
```

---

### `347/588` `backend/scripts/rebuild_cumulative_generation.py`

- **المسار الكامل:** `F:\1f\p\ALI_Studio_Pro_Design4_4.6.0\04_Adaptive_Hybrid\backend/scripts/rebuild_cumulative_generation.py`
- **الحجم:** 1042 بايت (1.0 KB)
- **الامتداد:** `.py`

```python
# -*- coding: utf-8 -*-
from __future__ import annotations
import argparse
import json
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from training.generation_lineage import build_cumulative_dataset

ap = argparse.ArgumentParser()
ap.add_argument('--generation', required=True)
ap.add_argument('--delta', default='')
ap.add_argument('--output', default='')
ap.add_argument('--parent', default='')
ap.add_argument('--dry-run', action='store_true')
args = ap.parse_args()
models_root = ROOT / 'models'
out = Path(args.output) if args.output else models_root / 'generations' / args.generation / 'cumulative' / 'train.jsonl'
if args.dry_run:
    print(json.dumps({'ok': True, 'dry_run': True, 'generation': args.generation, 'output': str(out)}, ensure_ascii=False, indent=2))
    raise SystemExit(0)
result = build_cumulative_dataset(models_root, args.generation, args.delta or None, out, parent_generation=args.parent or None)
print(json.dumps(result, ensure_ascii=False, indent=2))
```

---

### `348/588` `backend/scripts/rebuild_v4_model.py`

- **المسار الكامل:** `F:\1f\p\ALI_Studio_Pro_Design4_4.6.0\04_Adaptive_Hybrid\backend/scripts/rebuild_v4_model.py`
- **الحجم:** 3655 بايت (3.6 KB)
- **الامتداد:** `.py`

```python
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
```

---

### `349/588` `backend/scripts/release_check.py`

- **المسار الكامل:** `F:\1f\p\ALI_Studio_Pro_Design4_4.6.0\04_Adaptive_Hybrid\backend/scripts/release_check.py`
- **الحجم:** 4357 بايت (4.3 KB)
- **الامتداد:** `.py`

```python
#!/usr/bin/env python
"""Source/release gate for ALI AI 2.5.

The checker is valid for a source-only bundle: large binary checkpoints are optional.
Set ALI_REQUIRE_ARTIFACTS=1 when a deployment package is expected to carry trained artifacts.
"""
from __future__ import annotations

import hashlib
import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def sha_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def main() -> int:
    report = {"ok": True, "checks": []}

    def check(name: str, ok: bool, detail: str = "", *, required: bool = True) -> None:
        entry = {"name": name, "ok": bool(ok), "detail": detail, "required": required}
        if not required and not ok:
            entry["status"] = "skipped"
            entry["ok"] = True
        report["checks"].append(entry)
        if required and not ok:
            report["ok"] = False

    required = [
        "model/ali_lm.py", "training/trainer.py", "training/pipeline.py",
        "tokenizer/manager.py", "model/artifacts.py", "model/weights_manager.py",
        "inference/engine.py", "knowledge/rag.py", "memory/conversations.py",
        "core/runtime.py", "core/tool_protocol.py", "core/session_store.py",
        "ui/theme.py", "ui/widgets.py", "ali_ai.py", "tools/gguf.py", "training/accumulated_updates.py", "ui/activity.py",
    ]
    for rel in required:
        check("file:" + rel, (ROOT / rel).exists())

    try:
        project = json.loads((ROOT / "PROJECT_VERSION.json").read_text(encoding="utf-8"))
        check("project version", project.get("version") == "2.5.0", json.dumps(project, ensure_ascii=False))
        check("previous project", project.get("previous_project") == "ALI Studio Pro 3.0.0")
        check("previous release", project.get("previous_release") == "2.0.0")
    except Exception as exc:
        check("project identity", False, repr(exc))

    # Validate the dataset uniqueness contract without requiring model binaries.
    corpus = ROOT / "data/seed/conversations_curriculum.jsonl"
    if corpus.exists():
        try:
            rows = [json.loads(x) for x in corpus.read_text(encoding="utf-8").splitlines() if x.strip()]
            ids = [r.get("id") for r in rows]
            hashes = [sha_text("\n".join(
                f"{m.get('role','')}:{str(m.get('content','')).strip()}"
                for m in r.get('messages', []) if isinstance(m, dict)
            )) for r in rows]
            check("conversation corpus nonempty", bool(rows), str(len(rows)))
            check("conversation ids unique", len(ids) == len(set(ids)))
            check("conversation content unique", len(hashes) == len(set(hashes)))
        except Exception as exc:
            check("conversation dataset validation", False, repr(exc))
    else:
        check("conversation corpus optional", True, "large training datasets are excluded from the Markdown source bundle", required=False)

    try:
        from runtime.hardware import detect, model_profile, training_profile
        hw = detect(); mp = model_profile(hw); tp = training_profile(hw)
        check("hardware detector", hw.cpu_cores >= 1)
        check("2GB-safe profile", mp["layers"] <= 8 and mp["hidden"] <= 320)
        check("CPU-safe training", tp["batch_size"] == 1)
    except Exception as exc:
        check("hardware detector", False, repr(exc))

    # Large trained artifacts are intentionally optional in a source bundle.
    artifact_paths = {
        "conversation checkpoint": ROOT / "models/checkpoints/ALI-Conversation-v0.4",
        "model registry": ROOT / "artifacts/models.sqlite3",
        "LoRA adapter": ROOT / "models/lora/ALI-Conversation-v0.4-corrected/adapter_model.safetensors",
    }
    require_artifacts = os.environ.get("ALI_REQUIRE_ARTIFACTS") == "1"
    for name, path in artifact_paths.items():
        check(name, path.exists(), str(path), required=require_artifacts)

    out = ROOT / "artifacts/release_check.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if report["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
```

---

### `350/588` `backend/scripts/resume_conversation_v0_4.py`

- **المسار الكامل:** `F:\1f\p\ALI_Studio_Pro_Design4_4.6.0\04_Adaptive_Hybrid\backend/scripts/resume_conversation_v0_4.py`
- **الحجم:** 1957 بايت (1.9 KB)
- **الامتداد:** `.py`

```python
#!/usr/bin/env python
from __future__ import annotations
from pathlib import Path
import json, sys, time
ROOT=Path(__file__).resolve().parents[1]; sys.path.insert(0,str(ROOT))

def main():
    from model.ali_lm import AliConfig,ALIForCausalLM,save_hf_checkpoint
    from tokenizer.spm import AliTokenizer
    from training.trainer import Trainer,TrainConfig
    from training.evaluator import evaluate_model
    data=ROOT/'data/training/curriculum'; tokdir=ROOT/'models/base/ALI-Conversation-v0.4/tokenizer'; tok=AliTokenizer(tokdir/'tokenizer.model')
    cfg=AliConfig(vocab_size=tok.vocab_size,hidden_size=256,intermediate_size=1024,num_hidden_layers=4,num_attention_heads=8,num_key_value_heads=8,max_position_embeddings=256,use_sdpa=True)
    model=ALIForCausalLM(cfg); tc=TrainConfig(epochs=10,batch_size=1,grad_accum=2,learning_rate=1.5e-4,warmup_steps=30,max_steps=500,save_every=100,eval_every=100,max_seq_len=192,device='cpu',gradient_checkpointing=True,dataset_mode='chat',curriculum=True,cpu_threads=2)
    out=ROOT/'models/checkpoints/ALI-Conversation-v0.4'; tr=Trainer(model,tok,data/'chat_train.jsonl',data/'chat_validation.jsonl',tc,out)
    tr.resume(out/'step-000200')
    print('resumed',tr.global_step)
    res=tr.train(lambda e: print(json.dumps(e,ensure_ascii=False),flush=True) if e['step']%25==0 or 'val_loss' in e else None)
    final=Path(res['checkpoint']); hf=final/'hf'; save_hf_checkpoint(model,tokdir,hf,{'training_result':res,'specialization':'conversation-curriculum-v0.4','resumed_from':'step-000200'})
    ev=evaluate_model(model,tok,data/'chat_validation.jsonl','cpu')
    rep={'training':res,'validation':ev,'hf':str(hf),'created_at':time.time()}; (ROOT/'evaluation/artifacts').mkdir(parents=True,exist_ok=True); (ROOT/'evaluation/artifacts/conversation_v0.4.json').write_text(json.dumps(rep,ensure_ascii=False,indent=2),encoding='utf-8'); print(json.dumps(rep,ensure_ascii=False,indent=2))
if __name__=='__main__':main()
```

---

### `351/588` `backend/scripts/run_server.py`

- **المسار الكامل:** `F:\1f\p\ALI_Studio_Pro_Design4_4.6.0\04_Adaptive_Hybrid\backend/scripts/run_server.py`
- **الحجم:** 283 بايت (0.3 KB)
- **الامتداد:** `.py`

```python
# -*- coding: utf-8 -*-
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT))
from api.server import serve
from core.runtime import ALIRuntime
serve(ALIRuntime(ROOT,ROOT/'runtime.sqlite3',allow_internet=False),project_dir=ROOT)
```

---

### `352/588` `backend/scripts/self_manager.py`

- **المسار الكامل:** `F:\1f\p\ALI_Studio_Pro_Design4_4.6.0\04_Adaptive_Hybrid\backend/scripts/self_manager.py`
- **الحجم:** 1130 بايت (1.1 KB)
- **الامتداد:** `.py`

```python
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
```

---

### `353/588` `backend/scripts/serve_web_ui.py`

- **المسار الكامل:** `F:\1f\p\ALI_Studio_Pro_Design4_4.6.0\04_Adaptive_Hybrid\backend/scripts/serve_web_ui.py`
- **الحجم:** 354 بايت (0.3 KB)
- **الامتداد:** `.py`

```python
#!/usr/bin/env python
from http.server import ThreadingHTTPServer,SimpleHTTPRequestHandler
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]/'web-ui-tui'/'web'
if __name__=='__main__':
 import os
 os.chdir(ROOT); print('ALI Web UI: http://127.0.0.1:8090'); ThreadingHTTPServer(('127.0.0.1',8090),SimpleHTTPRequestHandler).serve_forever()
```

---

### `354/588` `backend/scripts/train_ali.py`

- **المسار الكامل:** `F:\1f\p\ALI_Studio_Pro_Design4_4.6.0\04_Adaptive_Hybrid\backend/scripts/train_ali.py`
- **الحجم:** 4280 بايت (4.2 KB)
- **الامتداد:** `.py`

```python
# -*- coding: utf-8 -*-
"""Real ALI AI training entry point: from-scratch or verified continuation."""
from __future__ import annotations
import argparse,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent; sys.path.insert(0,str(ROOT))
from runtime.hardware import detect,training_profile,model_profile
from config.device_profiles import recommend_for_hardware
from training.scaling import PROFILES, get as get_scale
from tokenizer.spm import train_sentencepiece,AliTokenizer
from model.ali_lm import AliConfig,ALIForCausalLM,save_hf_checkpoint
from training.trainer import Trainer,TrainConfig
from model.registry import ModelRegistry

def main():
    ap=argparse.ArgumentParser(description='Train ALI AI from scratch or resume a checkpoint')
    ap.add_argument('--train',default='data/training/curriculum/chat_train.jsonl'); ap.add_argument('--validation',default='data/training/curriculum/chat_validation.jsonl')
    ap.add_argument('--tokenizer',default='weights/tokenizer'); ap.add_argument('--output',default='training/runs'); ap.add_argument('--epochs',type=int,default=1); ap.add_argument('--steps',type=int,default=0)
    ap.add_argument('--device',default='auto',choices=['auto','cpu','cuda']); ap.add_argument('--resume',default=''); ap.add_argument('--scale',default='small',choices=list(PROFILES)); ap.add_argument('--vocab-size',type=int,default=0)
    ap.add_argument('--seq-len',type=int,default=0); ap.add_argument('--train-mode',choices=['full','lora'],default='full'); ap.add_argument('--dataset-mode',choices=['causal','chat'],default='chat'); ap.add_argument('--registry',default='artifacts/models.sqlite3')
    args=ap.parse_args(); h=detect(); tp=training_profile(h); mp=model_profile(h); device_profile=recommend_for_hardware(h); scale_name=args.scale or tp.get('scale','micro'); scale=get_scale(scale_name); device=tp['device'] if args.device=='auto' else args.device
    train=Path(args.train); val=Path(args.validation); train=train if train.is_absolute() else ROOT/train; val=val if val.is_absolute() else ROOT/val
    if not train.exists(): raise SystemExit(f'Train dataset not found: {train}')
    tokdir=Path(args.tokenizer); tokdir=tokdir if tokdir.is_absolute() else ROOT/tokdir; tok=tokdir/'tokenizer.model'
    if not tok.exists(): train_sentencepiece([str(train)],tokdir,vocab_size=args.vocab_size or scale.vocab_size)
    tokenizer=AliTokenizer(tok)
    if args.resume:
        ck=Path(args.resume)/'checkpoint.pt';
        if not ck.exists(): raise SystemExit(f'Resume checkpoint not found: {ck}')
        import torch
        blob=torch.load(ck,map_location='cpu',weights_only=False); cfg=AliConfig.from_dict(blob['config'])
    else:
        seq=args.seq_len or min(tp['seq_len'], scale.context)
        cfg=AliConfig(vocab_size=tokenizer.vocab_size,hidden_size=scale.hidden_size,intermediate_size=scale.intermediate_size,num_hidden_layers=scale.layers,num_attention_heads=scale.heads,num_key_value_heads=scale.heads,max_position_embeddings=seq)
    seq=args.seq_len or min(tp['seq_len'],cfg.max_position_embeddings)
    tc=TrainConfig(epochs=args.epochs,max_steps=args.steps,max_seq_len=seq,batch_size=tp['batch_size'],grad_accum=tp['grad_accum'],device=device,gradient_checkpointing=True,train_mode=args.train_mode,dataset_mode=args.dataset_mode,amp=bool(tp.get('amp',False)),cpu_threads=int(tp.get('cpu_threads',device_profile['training'].get('recommended_torch_threads',max(1,(h.cpu_cores or 4)-2)))))
    model=ALIForCausalLM(cfg); tr=Trainer(model,tokenizer,train,val if val.exists() else None,tc,ROOT/args.output)
    if args.resume: tr.resume(args.resume)
    res=tr.train(lambda e: print(json.dumps(e,ensure_ascii=False),flush=True)); final=Path(res['checkpoint']); hf=final/'hf'; save_hf_checkpoint(model,tokdir,hf,{'training_result':res,'scale':scale_name,'train_mode':args.train_mode})
    ver='v'+__import__('time').strftime('%Y%m%d-%H%M%S'); ModelRegistry(ROOT/args.registry).register('ALI',ver,status='candidate',checkpoint=str(final),hf_dir=str(hf),train_config=tc.to_dict(),eval={'loss':res.get('val_loss')})
    print(json.dumps({'registry_version':ver,'hf_dir':str(hf),'device_profile':device_profile['id'],'scale':scale_name,**res},ensure_ascii=False,indent=2))
if __name__=='__main__': main()
```

---

### `355/588` `backend/scripts/train_conversation_lora_v0_4.py`

- **المسار الكامل:** `F:\1f\p\ALI_Studio_Pro_Design4_4.6.0\04_Adaptive_Hybrid\backend/scripts/train_conversation_lora_v0_4.py`
- **الحجم:** 1772 بايت (1.7 KB)
- **الامتداد:** `.py`

```python
#!/usr/bin/env python
from __future__ import annotations
from pathlib import Path
import json,sys
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))

def main():
 import torch
 from tokenizer.spm import AliTokenizer
 from model.ali_lm import AliConfig,ALIForCausalLM,load_state
 from training.trainer import Trainer,TrainConfig
 tokdir=ROOT/'models/base/ALI-Conversation-v0.4/tokenizer'; tok=AliTokenizer(tokdir/'tokenizer.model')
 base=ROOT/'models/checkpoints/ALI-Conversation-v0.4/final-000500'; blob=json.loads((base/'trainer_state.json').read_text(encoding='utf-8')); cfg=AliConfig.from_dict(json.loads((base/'hf'/'config.json').read_text(encoding='utf-8'))); model=ALIForCausalLM(cfg); load_state(model,base/'model.safetensors','cpu')
 out=ROOT/'models/lora/ALI-Conversation-v0.4'; out.parent.mkdir(parents=True,exist_ok=True)
 tc=TrainConfig(epochs=3,batch_size=1,grad_accum=2,learning_rate=8e-5,warmup_steps=8,max_steps=80,save_every=40,eval_every=40,max_seq_len=192,device='cpu',gradient_checkpointing=True,dataset_mode='chat',train_mode='lora',lora_rank=8,lora_alpha=16,lora_dropout=.05,cpu_threads=2,curriculum=True)
 tr=Trainer(model,tok,ROOT/'data/training/curriculum/chat_train.jsonl',ROOT/'data/training/curriculum/chat_validation.jsonl',tc,ROOT/'models/checkpoints/ALI-Conversation-v0.4-lora'); r=tr.train(lambda e: print(json.dumps(e,ensure_ascii=False),flush=True) if 'val_loss' in e or e['step']%20==0 else None)
 # save adapter from final wrapped model
 from training.lora import save_lora_adapter
 save_lora_adapter(model,out,{'base_checkpoint':str(base),'training_result':r,'specialization':'conversation-lora-v0.4'})
 print(json.dumps({'training':r,'adapter':str(out)},ensure_ascii=False,indent=2))
if __name__=='__main__':main()
```

---

### `356/588` `backend/scripts/train_conversation_quality.py`

- **المسار الكامل:** `F:\1f\p\ALI_Studio_Pro_Design4_4.6.0\04_Adaptive_Hybrid\backend/scripts/train_conversation_quality.py`
- **الحجم:** 1895 بايت (1.9 KB)
- **الامتداد:** `.py`

```python
#!/usr/bin/env python
from __future__ import annotations
from pathlib import Path
import json,sys,time,shutil
ROOT=Path(__file__).resolve().parents[1]; sys.path.insert(0,str(ROOT))
def main():
 import torch
 from model.ali_lm import AliConfig,ALIForCausalLM,save_hf_checkpoint
 from tokenizer.spm import AliTokenizer
 from training.trainer import Trainer,TrainConfig
 from training.evaluator import evaluate_model
 tokdir=ROOT/'models/base/ALI-Conversation-v0.1/tokenizer'; tok=AliTokenizer(tokdir/'tokenizer.model')
 train=ROOT/'data/training/bootstrap/chat_train.jsonl'; val=ROOT/'data/training/bootstrap/chat_validation.jsonl'; out=ROOT/'models/checkpoints/ALI-Conversation-v0.2'
 cfg=AliConfig(vocab_size=tok.vocab_size,hidden_size=160,intermediate_size=640,num_hidden_layers=3,num_attention_heads=4,num_key_value_heads=4,max_position_embeddings=256,use_sdpa=True)
 model=ALIForCausalLM(cfg)
 tc=TrainConfig(epochs=20,batch_size=1,grad_accum=2,learning_rate=3e-4,warmup_steps=20,max_steps=500,save_every=100,eval_every=50,max_seq_len=192,device='cpu',gradient_checkpointing=True,dataset_mode='chat',curriculum=True,cpu_threads=max(1,(torch.get_num_threads() or 2)))
 tr=Trainer(model,tok,train,val,tc,out); res=tr.train(lambda e: print(json.dumps(e,ensure_ascii=False),flush=True) if e['step']%25==0 else None)
 final=Path(res['checkpoint']); hf=final/'hf'; save_hf_checkpoint(model,tokdir,hf,{'training_result':res,'specialization':'conversation-quality-v0.2'})
 ev=evaluate_model(model,tok,val,'cpu'); (ROOT/'evaluation/artifacts').mkdir(parents=True,exist_ok=True); report={'training':res,'validation':ev,'hf':str(hf),'created_at':time.time()}; (ROOT/'evaluation/artifacts/conversation_v0.2.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8'); print(json.dumps(report,ensure_ascii=False,indent=2)); return 0
if __name__=='__main__':raise SystemExit(main())
```

---

### `357/588` `backend/scripts/train_conversation_v0_3.py`

- **المسار الكامل:** `F:\1f\p\ALI_Studio_Pro_Design4_4.6.0\04_Adaptive_Hybrid\backend/scripts/train_conversation_v0_3.py`
- **الحجم:** 1869 بايت (1.8 KB)
- **الامتداد:** `.py`

```python
#!/usr/bin/env python
from pathlib import Path
import sys,json,time
ROOT=Path(__file__).resolve().parents[1]; sys.path.insert(0,str(ROOT))
def main():
 import torch
 from model.ali_lm import AliConfig,ALIForCausalLM,save_hf_checkpoint
 from tokenizer.spm import AliTokenizer
 from training.trainer import Trainer,TrainConfig
 from training.evaluator import evaluate_model
 tokdir=ROOT/'models/base/ALI-Conversation-v0.1/tokenizer'; tok=AliTokenizer(tokdir/'tokenizer.model')
 cfg=AliConfig(vocab_size=tok.vocab_size,hidden_size=160,intermediate_size=640,num_hidden_layers=3,num_attention_heads=4,num_key_value_heads=4,max_position_embeddings=256,use_sdpa=True)
 model=ALIForCausalLM(cfg)
 tc=TrainConfig(epochs=12,batch_size=1,grad_accum=2,learning_rate=3e-4,warmup_steps=15,max_steps=220,save_every=55,eval_every=55,max_seq_len=192,device='cpu',gradient_checkpointing=True,dataset_mode='chat',curriculum=True,cpu_threads=2)
 out=ROOT/'models/checkpoints/ALI-Conversation-v0.3'; tr=Trainer(model,tok,ROOT/'data/training/bootstrap/chat_train.jsonl',ROOT/'data/training/bootstrap/chat_validation.jsonl',tc,out); res=tr.train(lambda e:print(json.dumps(e,ensure_ascii=False),flush=True) if e['step']%25==0 else None)
 final=Path(res['checkpoint']); hf=final/'hf'; save_hf_checkpoint(model,tokdir,hf,{'training_result':res,'specialization':'conversation-rope-fixed-v0.3'})
 ev=__import__('training.evaluator',fromlist=['evaluate_model']).evaluate_model(model,tok,ROOT/'data/training/bootstrap/chat_validation.jsonl','cpu')
 rep={'training':res,'validation':ev,'hf':str(hf),'created_at':time.time()}; (ROOT/'evaluation/artifacts').mkdir(parents=True,exist_ok=True); (ROOT/'evaluation/artifacts/conversation_v0.3.json').write_text(json.dumps(rep,ensure_ascii=False,indent=2),encoding='utf-8'); print(json.dumps(rep,ensure_ascii=False,indent=2))
if __name__=='__main__':main()
```

---

### `358/588` `backend/scripts/train_conversation_v0_4.py`

- **المسار الكامل:** `F:\1f\p\ALI_Studio_Pro_Design4_4.6.0\04_Adaptive_Hybrid\backend/scripts/train_conversation_v0_4.py`
- **الحجم:** 2225 بايت (2.2 KB)
- **الامتداد:** `.py`

```python
#!/usr/bin/env python
from __future__ import annotations
from pathlib import Path
import json, sys, time, shutil
ROOT=Path(__file__).resolve().parents[1]; sys.path.insert(0,str(ROOT))

def main():
    import torch
    from tokenizer.spm import train_sentencepiece, AliTokenizer
    from model.ali_lm import AliConfig, ALIForCausalLM, save_hf_checkpoint
    from training.trainer import Trainer, TrainConfig
    from training.evaluator import evaluate_model
    data=ROOT/'data/training/curriculum'; base=ROOT/'models/base/ALI-Conversation-v0.4'; tokdir=base/'tokenizer'; tokdir.mkdir(parents=True,exist_ok=True)
    # train tokenizer only from ALI's own curated conversation corpus
    model_path=train_sentencepiece([str(data/'chat_train.jsonl')],tokdir,vocab_size=1024)
    tok=AliTokenizer(model_path)
    cfg=AliConfig(vocab_size=tok.vocab_size,hidden_size=256,intermediate_size=1024,num_hidden_layers=4,num_attention_heads=8,num_key_value_heads=8,max_position_embeddings=256,use_sdpa=True)
    model=ALIForCausalLM(cfg)
    tc=TrainConfig(epochs=8,batch_size=1,grad_accum=2,learning_rate=1.5e-4,warmup_steps=30,max_steps=500,save_every=100,eval_every=100,max_seq_len=192,device='cpu',gradient_checkpointing=True,dataset_mode='chat',curriculum=True,cpu_threads=2)
    out=ROOT/'models/checkpoints/ALI-Conversation-v0.4'; out.mkdir(parents=True,exist_ok=True)
    tr=Trainer(model,tok,data/'chat_train.jsonl',data/'chat_validation.jsonl',tc,out)
    res=tr.train(lambda e: print(json.dumps(e,ensure_ascii=False),flush=True) if e['step']%25==0 or 'val_loss' in e else None)
    final=Path(res['checkpoint']); hf=final/'hf'; save_hf_checkpoint(model,tokdir,hf,{'training_result':res,'specialization':'conversation-curriculum-v0.4','corpus':str(ROOT/'data/seed/conversations_curriculum.jsonl')})
    ev=evaluate_model(model,tok,data/'chat_validation.jsonl','cpu')
    rep={'training':res,'validation':ev,'hf':str(hf),'created_at':time.time()};
    (ROOT/'evaluation/artifacts').mkdir(parents=True,exist_ok=True); (ROOT/'evaluation/artifacts/conversation_v0.4.json').write_text(json.dumps(rep,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps(rep,ensure_ascii=False,indent=2))
if __name__=='__main__':main()
```

---

### `359/588` `backend/scripts/train_pipeline.py`

- **المسار الكامل:** `F:\1f\p\ALI_Studio_Pro_Design4_4.6.0\04_Adaptive_Hybrid\backend/scripts/train_pipeline.py`
- **الحجم:** 2924 بايت (2.9 KB)
- **الامتداد:** `.py`

```python
#!/usr/bin/env python
"""CLI for the same progressive training pipeline used by the desktop UI."""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from runtime.hardware import detect, training_profile
from training.pipeline import PipelineConfig, TrainingPipeline


def main(argv=None) -> int:
    p = argparse.ArgumentParser(prog="ali-train", description="ALI AI 2.0 progressive training")
    p.add_argument("--stage", choices=("base", "sft", "lora"), default="base")
    p.add_argument("--scale", default="micro")
    p.add_argument("--train", required=True)
    p.add_argument("--validation", default="")
    p.add_argument("--base", default="")
    p.add_argument("--resume", default="")
    p.add_argument("--steps", type=int, default=0)
    p.add_argument("--epochs", type=int, default=1)
    p.add_argument("--seq", type=int, default=256)
    p.add_argument("--batch", type=int, default=1)
    p.add_argument("--accum", type=int, default=16)
    p.add_argument("--lr", type=float, default=3e-4)
    p.add_argument("--device", default="auto", help="auto, cpu, cuda, cuda:N")
    p.add_argument("--vocab-size", type=int, default=4096)
    p.add_argument("--lora-rank", type=int, default=8)
    p.add_argument("--lora-alpha", type=float, default=16.0)
    p.add_argument("--lora-dropout", type=float, default=.05)
    p.add_argument("--distributed-backend", default="auto")
    p.add_argument("--world-size", type=int, default=int(os.environ.get("WORLD_SIZE", "1")))
    args = p.parse_args(argv)

    device = args.device
    if device == "auto":
        hw = detect()
        device = training_profile(hw).get("device", "cpu")

    cfg = PipelineConfig(
        stage=args.stage, scale=args.scale,
        train_path=str(Path(args.train).resolve()),
        validation_path=str(Path(args.validation).resolve()) if args.validation else "",
        base_checkpoint=str(Path(args.base).resolve()) if args.base else "",
        resume_checkpoint=str(Path(args.resume).resolve()) if args.resume else "",
        max_steps=max(0, args.steps), epochs=max(1, args.epochs),
        max_seq_len=max(32, args.seq), batch_size=max(1, args.batch),
        grad_accum=max(1, args.accum), learning_rate=args.lr,
        device=device, tokenizer_vocab_size=max(128, args.vocab_size),
        lora_rank=max(1, args.lora_rank), lora_alpha=args.lora_alpha,
        lora_dropout=max(0.0, min(.99, args.lora_dropout)),
        distributed_backend=args.distributed_backend,
        world_size=max(1, args.world_size),
    )

    pipe = TrainingPipeline(ROOT, detect())
    result = pipe.run(cfg, progress=lambda ev: print(json.dumps(ev, ensure_ascii=False), flush=True))
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
```

---

### `360/588` `backend/scripts/verify_generation_lineage.py`

- **المسار الكامل:** `F:\1f\p\ALI_Studio_Pro_Design4_4.6.0\04_Adaptive_Hybrid\backend/scripts/verify_generation_lineage.py`
- **الحجم:** 510 بايت (0.5 KB)
- **الامتداد:** `.py`

```python
# -*- coding: utf-8 -*-
from __future__ import annotations
import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from training.generation_lineage import verify_lineage

ap = argparse.ArgumentParser()
ap.add_argument('--generation', required=True)
args = ap.parse_args()
result = verify_lineage(ROOT / 'models', args.generation)
print(json.dumps(result, ensure_ascii=False, indent=2))
sys.exit(0 if result.get('valid') else 1)
```

---

### `361/588` `backend/scripts/windows_preflight.py`

- **المسار الكامل:** `F:\1f\p\ALI_Studio_Pro_Design4_4.6.0\04_Adaptive_Hybrid\backend/scripts/windows_preflight.py`
- **الحجم:** 951 بايت (0.9 KB)
- **الامتداد:** `.py`

```python
# -*- coding: utf-8 -*-
from __future__ import annotations
import importlib.util
import platform
import sys

REQUIRED = {
    "torch": "torch",
    "numpy": "numpy",
    "psutil": "psutil",
    "safetensors": "safetensors",
    "sentencepiece": "sentencepiece",
    "pytest": "pytest",
    "tkinterdnd2": "tkinterdnd2",
}

missing = [name for name, mod in REQUIRED.items() if importlib.util.find_spec(mod) is None]
print(f"[PREFLIGHT] Python: {platform.python_version()} ({platform.architecture()[0]})")
print(f"[PREFLIGHT] Missing: {', '.join(missing) if missing else 'none'}")
if missing:
    print("[PREFLIGHT] Dependency environment is incomplete.")
    raise SystemExit(2)

try:
    import torch
    print(f"[PREFLIGHT] torch={torch.__version__}")
    print(f"[PREFLIGHT] cuda_available={torch.cuda.is_available()}")
except Exception as exc:
    print(f"[PREFLIGHT] torch import failed: {exc}")
    raise SystemExit(3)

print("[PREFLIGHT] PASS")
```

---

### `362/588` `backend/security/__init__.py`

- **المسار الكامل:** `F:\1f\p\ALI_Studio_Pro_Design4_4.6.0\04_Adaptive_Hybrid\backend/security/__init__.py`
- **الحجم:** 602 بايت (0.6 KB)
- **الامتداد:** `.py`

```python
# -*- coding: utf-8 -*-
"""security/__init__.py — حزمة Security.

- paths: حماية مسارات الملفات (workspace containment).
- commands: فلتر الأوامر الخطيرة.
- permissions: PermissionManager — يربط بين perm_mode والـ tool permission.
"""

from security.paths import safe_project_path
from security.commands import is_command_safe
from security.permissions import (
    PermissionManager, Decision, get_permission_manager,
)

__all__ = [
    "safe_project_path",
    "is_command_safe",
    "PermissionManager", "Decision", "get_permission_manager",
]
```

---

### `363/588` `backend/security/commands.py`

- **المسار الكامل:** `F:\1f\p\ALI_Studio_Pro_Design4_4.6.0\04_Adaptive_Hybrid\backend/security/commands.py`
- **الحجم:** 2446 بايت (2.4 KB)
- **الامتداد:** `.py`

```python
# -*- coding: utf-8 -*-
"""فلتر الأوامر الخطيرة.

القواعد دفاعية وليست sandbox: أي أمر مطلوب للحماية يُرفض بشكل صريح،
مع تغطية أوسع لـ Windows + Unix + سلاسل تشغيل أوامر/سكربتات غير آمنة.
"""

from __future__ import annotations

import re
from typing import List, Tuple


# (regex pattern, reason)
# الترتيب غير مهم — أي تطابق = رفض.
_BLACKLIST: List[Tuple[re.Pattern, str]] = [
    # Unix / Linux destructive operations
    (re.compile(r"\brm\s+-[-a-z]*r[-a-z]*f\s+(?:--\s*)?(?:/|~)(?:\s|$)", re.I),
                                                     "recursive root/home delete"),
    (re.compile(r"\bdd\s+if=.*\s+of=/dev/(?:sd[a-z]+|nvme\d+n\d+|hd[a-z]+)", re.I),
                                                     "dd overwrite disk"),
    (re.compile(r"\b(?:mkfs|fdisk|parted)\b", re.I), "partition tool"),
    (re.compile(r":\(\)\s*\{\s*:\s*\|\s*:\s*&\s*\}\s*;\s*:", re.I),
                                                     "fork bomb"),

    # Windows destructive / persistence operations
    (re.compile(r"\bformat\s+[a-zA-Z]:", re.I), "format drive"),
    (re.compile(r"\b(?:del|erase)\s+/[sq].*[a-zA-Z]:\\", re.I),
                                                     "recursive drive delete"),
    (re.compile(r"\b(?:rd|rmdir)\s+/[sq].*[a-zA-Z]:\\", re.I),
                                                     "recursive directory delete"),
    (re.compile(r"\bdiskpart\b", re.I), "diskpart"),
    (re.compile(r"\bbcdedit\b", re.I), "bcdedit"),
    (re.compile(r"\bregedit\b", re.I), "regedit"),
    (re.compile(r"\breg\s+(?:delete|import)\b", re.I), "reg destructive"),
    (re.compile(r"\bnetsh\s+(?:advfirewall|firewall)\s+delete\b", re.I),
                                                     "netsh delete"),
    (re.compile(r"\bcipher\s+/w\b", re.I), "cipher wipe"),
    (re.compile(r"\b(?:shutdown|logoff)\b", re.I), "session shutdown"),
    (re.compile(r"\bwevtutil\s+cl\b", re.I), "event log clear"),
    (re.compile(r"\bschtasks\s+/delete\b", re.I), "scheduled task delete"),

    # Script / binary execution patterns commonly used to bypass intent boundaries
    (re.compile(r"\bpowershell(?:\.exe)?\b.*(?:-encodedcommand|-enc\b)", re.I),
                                                     "encoded PowerShell"),
    (re.compile(r"\b(?:powershell|pwsh)(?:\.exe)?\b.*\binvoke-expression\b", re.I),
                                                     "PowerShell Invoke-Expression"),
    (re.compile(r"\b(?:powershell|pwsh)(?:\.exe)?\b.*\bstart-process\b", re.I),
                                                     "PowerShell Start-Process"),
    (re.compile(r"\b(?:powershell|pwsh)(?:\.exe)?\b.*\bremove-item\b.*-recurse\b", re.I),
                                                     "PowerShell recursive delete"),
    (re.compile(r"\b(?:mshta|rundll32|regsvr32|wscript|cscript)(?:\.exe)?\b", re.I),
                                                     "script host / binary launcher"),

    # Download-and-execute / pipe-to-shell patterns
    (re.compile(r"\b(?:curl|wget)\b.*\|\s*(?:bash|sh|zsh|fish|pwsh|powershell)\b", re.I),
                                                     "download pipe shell"),
    (re.compile(r"\b(?:iwr|irm|invoke-webrequest|invoke-restmethod)\b.*\|.*\b(?:iex|invoke-expression)\b", re.I),
                                                     "PowerShell download execute"),

    # Explicit shell nesting / command interpreter jumps
    (re.compile(r"\b(?:cmd|command)\.exe\s+/c\s+.*\b(?:powershell|pwsh)\b", re.I),
                                                     "nested PowerShell"),
]

def is_command_safe(cmd: str) -> bool:
    """يرجع True إذا كان الأمر غير مطابق لأي نمط خطير معروف."""
    if not isinstance(cmd, str) or not cmd.strip():
        return False
    normalized = cmd.replace("\u00a0", " ").strip()
    for pat, _reason in _BLACKLIST:
        if pat.search(normalized):
            return False
    return True


__all__ = ["is_command_safe"]
```

---

### `364/588` `backend/security/paths.py`

- **المسار الكامل:** `F:\1f\p\ALI_Studio_Pro_Design4_4.6.0\04_Adaptive_Hybrid\backend/security/paths.py`
- **الحجم:** 3107 بايت (3.0 KB)
- **الامتداد:** `.py`

```python
# -*- coding: utf-8 -*-
"""حماية المسارات — Workspace Containment.

`safe_project_path(project_dir, rel)` يحل المسار النسبي إلى Path مطلق.
يرفع PermissionError إذا:
- rel فارغ أو خارج project_dir (محاولة escape).
- rel يلامس مسارات حساسة معروفة (SystemRoot, ProgramFiles, .ssh, .aws,
  APPDATA, إلخ).

هذه الطبقة هي خط الدفاع الأول قبل أي ملف I/O.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path
from typing import Iterable


# مسارات Windows الحساسة التي لا يُسمح للـ Agent بلمسها مطلقاً.
_WINDOWS_SENSITIVE = (
    r"C:\Windows",
    r"C:\Windows\System32",
    r"C:\Program Files",
    r"C:\Program Files (x86)",
    r"C:\ProgramData",
)

# مكونات أسماء يجب رفضها أينما ظهرت.
_SENSITIVE_NAME_PARTS = (
    ".ssh", ".aws", ".gnupg", "credentials", ".env", "id_rsa",
)

# ملفات حساسة بأسماء محددة (case-insensitive).
_SENSITIVE_FILES = (
    ".env", ".envrc", "credentials", "credentials.json",
    "id_rsa", "id_ed25519",
)


def _is_windows_sensitive(p: Path) -> bool:
    s = str(p).replace("/", "\\")
    for prefix in _WINDOWS_SENSITIVE:
        if s.startswith(prefix):
            return True
    return False


def _has_sensitive_component(p: Path) -> bool:
    parts_lower = {part.lower() for part in p.parts}
    for part in _SENSITIVE_NAME_PARTS:
        if part in parts_lower:
            return True
    name = p.name.lower()
    if name in _SENSITIVE_FILES:
        return True
    return False


def safe_project_path(project_dir: str | os.PathLike,
                      rel: str) -> Path:
    """حلّ rel داخل project_dir.

    - rel=""  → project_dir نفسه.
    - rel="sub/file.py" → project_dir/sub/file.py.
    - محاولات escape (rel يبدأ بـ ../) → PermissionError.
    - لمس path حساس (system/.ssh/.aws/.env) → PermissionError.
    """
    base = Path(project_dir).resolve()
    if not base.exists():
        raise PermissionError("project_dir does not exist: " + str(base))

    if not rel:
        rel = "."

    # حلّ المسار بشكل صريح لرفض escape.
    # نقبل rel المطلق فقط إذا كان داخل base.
    if os.path.isabs(rel):
        candidate = Path(rel).resolve()
    else:
        candidate = (base / rel).resolve()

    # يجب أن يكون داخل base (أو هو نفسه).
    try:
        candidate.relative_to(base)
    except ValueError:
        raise PermissionError(
            f"path escapes workspace: {rel} -> {candidate}"
        )

    # رفض المسارات الحساسة.
    if _is_windows_sensitive(candidate):
        raise PermissionError(
            f"access denied (sensitive windows path): {candidate}"
        )
    if _has_sensitive_component(candidate):
        raise PermissionError(
            f"access denied (sensitive file/path component): {candidate}"
        )

    return candidate


__all__ = ["safe_project_path"]
```

---

### `365/588` `backend/security/permissions.py`

- **المسار الكامل:** `F:\1f\p\ALI_Studio_Pro_Design4_4.6.0\04_Adaptive_Hybrid\backend/security/permissions.py`
- **الحجم:** 5617 بايت (5.5 KB)
- **الامتداد:** `.py`

```python
# -*- coding: utf-8 -*-
"""PermissionManager — Backend الحقيقي للصلاحيات.

القرارات:
- read-only: قراءة فقط. أي شيء >= DEFAULT مرفوض.
- default:   Tool بصلاحية read-only مسموح. >= DEFAULT يحتاج موافقة المستخدم
             (Ask) — الـ UI يحصل على dialog. القرار يُسجَّل في always_allow
             لتفادي تكرار السؤال.
- full-access: كل الأدوات مسموحة تلقائياً.

الـ Manager غير مرتبط بـ UI. الـ UI تستدعي `ask_user(...)` فقط عندما
يكون القرار "ask"، وإذا وافق المستخدم تستدعي `grant(tool_name, session=True)`.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List, Optional


class PermMode(str, Enum):
    READ_ONLY = "read-only"
    DEFAULT = "default"
    FULL_ACCESS = "full-access"


# ترتيب الصلاحيات (أدنى → أعلى).
_PERM_RANK = {
    PermMode.READ_ONLY.value:    0,
    PermMode.DEFAULT.value:      1,
    PermMode.FULL_ACCESS.value:  2,