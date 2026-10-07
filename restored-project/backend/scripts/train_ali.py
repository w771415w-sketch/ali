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
