#!/usr/bin/env python
from __future__ import annotations
from pathlib import Path
import json,sys,time
ROOT=Path(__file__).resolve().parents[1]; sys.path.insert(0,str(ROOT))
def main():
 import torch
 from model.ali_lm import AliConfig,ALIForCausalLM,save_hf_checkpoint
 from tokenizer.spm import AliTokenizer
 from training.trainer import Trainer,TrainConfig
 from training.evaluator import evaluate_model
 tokdir=ROOT/'models/base/ALI-Conversation-v0.1/tokenizer'; tok=AliTokenizer(tokdir/'tokenizer.model')
 resume=ROOT/'models/checkpoints/ALI-Conversation-v0.2/step-000300'; blob=torch.load(resume/'checkpoint.pt',map_location='cpu',weights_only=False); model=ALIForCausalLM(AliConfig.from_dict(blob['config']));
 tc=TrainConfig(epochs=20,batch_size=1,grad_accum=2,learning_rate=3e-4,warmup_steps=20,max_steps=350,save_every=25,eval_every=25,max_seq_len=192,device='cpu',gradient_checkpointing=True,dataset_mode='chat',curriculum=True,cpu_threads=2)
 tr=Trainer(model,tok,ROOT/'data/training/bootstrap/chat_train.jsonl',ROOT/'data/training/bootstrap/chat_validation.jsonl',tc,ROOT/'models/checkpoints/ALI-Conversation-v0.2')
 tr.resume(resume); res=tr.train(lambda e:print(json.dumps(e,ensure_ascii=False),flush=True))
 final=Path(res['checkpoint']); hf=final/'hf'; save_hf_checkpoint(model,tokdir,hf,{'training_result':res,'specialization':'conversation-quality-v0.2'})
 ev=evaluate_model(model,tok,ROOT/'data/training/bootstrap/chat_validation.jsonl','cpu'); report={'training':res,'validation':ev,'hf':str(hf),'created_at':time.time()}; (ROOT/'evaluation/artifacts').mkdir(parents=True,exist_ok=True); (ROOT/'evaluation/artifacts/conversation_v0.2.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8'); print(json.dumps(report,ensure_ascii=False,indent=2))
if __name__=='__main__':main()
