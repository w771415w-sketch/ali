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
