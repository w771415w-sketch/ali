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
