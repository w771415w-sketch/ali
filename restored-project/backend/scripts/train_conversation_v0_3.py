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
