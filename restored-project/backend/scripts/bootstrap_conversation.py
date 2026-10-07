#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Create and verify a first real ALI conversation model + conversation LoRA adapter.

This is a compact end-to-end smoke training run for the user's 32GB RAM / 2GB VRAM
class machine. It does not use a pretrained model or Ollama.
"""
from __future__ import annotations
import json,sys,time,hashlib,shutil
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]; sys.path.insert(0,str(ROOT))

def fmt(messages):
    return ''.join(f"<|{m['role']}|>\n{m.get('content','')}\n<|eot|>\n" for m in messages if m.get('content') is not None)

def build_source(seed,train,val,test):
    rows=[json.loads(x) for x in seed.read_text(encoding='utf-8').splitlines() if x.strip()]
    uniq={}
    for r in rows:
        txt=fmt(r.get('messages',[])); h=hashlib.sha256(txt.encode('utf-8')).hexdigest()
        if txt.strip() and h not in uniq:uniq[h]={'id':h,'text':txt,'messages':r.get('messages',[])}
    ordered=[uniq[k] for k in sorted(uniq)]
    n=len(ordered); ntr=max(1,int(n*.8)); nv=max(1,int(n*.1)) if n>=3 else max(0,n-ntr)
    parts={'train':ordered[:ntr],'validation':ordered[ntr:ntr+nv],'test':ordered[ntr+nv:]}
    for path,items in [(train,parts['train']),(val,parts['validation']),(test,parts['test'])]:
        path.parent.mkdir(parents=True,exist_ok=True); path.write_text(''.join(json.dumps(x,ensure_ascii=False)+'\n' for x in items),encoding='utf-8')
    corpus=train.parent/'tokenizer_corpus.txt'; corpus.write_text('\n\n'.join(x['text'] for x in ordered),encoding='utf-8')
    return {'total':n,'train':len(parts['train']),'validation':len(parts['validation']),'test':len(parts['test']),'corpus':str(corpus)}

def main():
    import torch
    from runtime.hardware import detect
    from tokenizer.spm import train_sentencepiece,AliTokenizer
    from model.ali_lm import AliConfig,ALIForCausalLM,save_hf_checkpoint
    from training.trainer import Trainer,TrainConfig
    from training.conversation import save_conversation_adapter
    from training.evaluator import evaluate_model
    from model.registry import ModelRegistry,file_hash
    h=detect(); print('[hardware]',h.to_dict())
    seed=ROOT/'data/seed/conversations.jsonl'; out=ROOT/'data/training/bootstrap'
    paths={k:out/f'chat_{k}.jsonl' for k in ('train','validation','test')}; split=build_source(seed,*paths.values()); print('[dataset]',split)
    tokdir=ROOT/'models/base/ALI-Conversation-v0.1/tokenizer'; tokfile=tokdir/'tokenizer.model'
    if tokfile.exists(): shutil.rmtree(tokdir.parent,ignore_errors=True)
    train_sentencepiece([split['corpus']],tokdir,vocab_size=512)
    tok=AliTokenizer(tokfile)
    cfg=AliConfig(vocab_size=tok.vocab_size,hidden_size=128,intermediate_size=512,num_hidden_layers=2,num_attention_heads=4,num_key_value_heads=4,max_position_embeddings=256,use_sdpa=True)
    base_dir=ROOT/'models/base/ALI-Conversation-v0.1'; ckpt_root=ROOT/'models/checkpoints/ALI-Conversation-v0.1'
    model=ALIForCausalLM(cfg)
    tc=TrainConfig(epochs=3,batch_size=1,grad_accum=2,learning_rate=4e-4,warmup_steps=5,max_steps=80,save_every=40,eval_every=20,max_seq_len=192,device='cpu',gradient_checkpointing=True,amp=False,cpu_amp=False,dataset_mode='chat',curriculum=True,cpu_threads=max(1,(h.cpu_cores or 2)-1))
    tr=Trainer(model,tok,paths['train'],paths['validation'],tc,ckpt_root)
    res=tr.train(lambda e: print(json.dumps(e,ensure_ascii=False),flush=True))
    final=Path(res['checkpoint']); hf=final/'hf'; save_hf_checkpoint(model,tokdir,hf,{'training_result':res,'specialization':'conversation-base'})
    merged_dir=ROOT/'models/merged/ALI-Conversation-v0.1'; shutil.rmtree(merged_dir,ignore_errors=True); save_hf_checkpoint(model,tokdir,merged_dir,{'training_result':res,'specialization':'conversation-base-merged'})
    # Real conversation LoRA adapter on top of the trained base.
    blob=torch.load(final/'checkpoint.pt',map_location='cpu',weights_only=False); base=ALIForCausalLM(AliConfig.from_dict(blob['config'])); base.load_state_dict(blob['model'])
    ltc=TrainConfig(epochs=2,batch_size=1,grad_accum=2,learning_rate=8e-4,warmup_steps=3,max_steps=30,save_every=15,eval_every=15,max_seq_len=192,device='cpu',gradient_checkpointing=True,amp=False,dataset_mode='chat',train_mode='lora',lora_rank=4,lora_alpha=8,curriculum=True)
    ltr=Trainer(base,tok,paths['train'],paths['validation'],ltc,ROOT/'models/checkpoints/ALI-Conversation-LoRA-v0.1'); lres=ltr.train(lambda e: None)
    adapter=Path(lres['checkpoint'])/'adapter'; adapter_out=ROOT/'models/lora/ALI-Conversation-v0.1'; shutil.rmtree(adapter_out,ignore_errors=True); shutil.copytree(adapter,adapter_out)
    eval_res=evaluate_model(model,tok,paths['validation'],'cpu')
    test_res=evaluate_model(model,tok,paths['test'],'cpu') if paths['test'].exists() and paths['test'].read_text(encoding='utf-8').strip() else {}
    registry=ModelRegistry(ROOT/'artifacts/models.sqlite3'); ver='v'+time.strftime('%Y%m%d-%H%M%S'); ds_hash=file_hash(paths['train']); registry.register('ALI',ver,status='candidate',checkpoint=str(final),hf_dir=str(hf),adapter=str(adapter_out),dataset_hash=ds_hash,tokenizer_hash=file_hash(tokdir),train_config=tc.to_dict(),eval={'validation':eval_res,'test':test_res,'loss':res.get('val_loss')})
    result={'base_training':res,'lora_training':lres,'validation':eval_res,'test':test_res,'hf':str(hf),'merged':str(merged_dir),'adapter':str(adapter_out),'registry_version':ver}
    (ROOT/'evaluation/artifacts').mkdir(parents=True,exist_ok=True)
    (ROOT/'evaluation/artifacts/bootstrap_report.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps(result,ensure_ascii=False,indent=2)); return 0
if __name__=='__main__':raise SystemExit(main())
