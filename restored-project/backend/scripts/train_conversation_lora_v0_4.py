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
