# -*- coding: utf-8 -*-
from pathlib import Path
import json, zipfile, os, tempfile, subprocess, sys
import pytest

def test_importer_on_internal_model(tmp_path):
    from model.ali_lm import AliConfig, ALIForCausalLM, save_hf_checkpoint
    from model.importer import inspect_weights, load_into
    from tokenizer.spm import train_sentencepiece, AliTokenizer
    corpus=tmp_path/'c.txt'; corpus.write_text('hello world\nالمساعد يجيب بشكل صحيح\n',encoding='utf-8')
    tokdir=tmp_path/'tok'; train_sentencepiece([str(corpus)],tokdir,vocab_size=512); tok=AliTokenizer(tokdir/'tokenizer.model')
    c=AliConfig(vocab_size=tok.vocab_size,hidden_size=32,intermediate_size=64,num_hidden_layers=1,num_attention_heads=4,num_key_value_heads=4,max_position_embeddings=32)
    m=ALIForCausalLM(c); out=save_hf_checkpoint(m,tokdir,tmp_path/'hf',{'test':True})
    r=inspect_weights(out,c); assert r.compatible; assert r.tensor_count>0
    m2=ALIForCausalLM(c); load_into(m2,out/'model.safetensors');
    for a,b in zip(m.parameters(),m2.parameters()): assert a.shape==b.shape

def test_training_resume(tmp_path):
    from model.ali_lm import AliConfig, ALIForCausalLM
    from tokenizer.spm import train_sentencepiece, AliTokenizer
    from training.trainer import Trainer, TrainConfig
    corpus=tmp_path/'c.txt'; corpus.write_text('a b c d e f g\n' * 30,encoding='utf-8')
    tokdir=tmp_path/'tok'; train_sentencepiece([str(corpus)],tokdir,vocab_size=512); tok=AliTokenizer(tokdir/'tokenizer.model')
    ds=tmp_path/'train.jsonl'; ds.write_text('\n'.join(json.dumps({'text':'<|user|> hello <|assistant|> hi <|eot|>'}) for _ in range(8)),encoding='utf-8')
    c=AliConfig(vocab_size=tok.vocab_size,hidden_size=32,intermediate_size=64,num_hidden_layers=1,num_attention_heads=4,num_key_value_heads=4,max_position_embeddings=32)
    tc=TrainConfig(epochs=1,max_steps=1,save_every=0,eval_every=0,max_seq_len=32,batch_size=1,grad_accum=1,device='cpu',gradient_checkpointing=False)
    t=Trainer(ALIForCausalLM(c),tok,ds,None,tc,tmp_path/'ck'); r=t.train(); assert r['steps']==1
    t2=Trainer(ALIForCausalLM(c),tok,ds,None,tc,tmp_path/'ck2'); t2.resume(r['checkpoint']); assert t2.global_step==1

def test_lora_roundtrip(tmp_path):
    from model.ali_lm import AliConfig, ALIForCausalLM
    from training.lora import apply_lora, save_lora_adapter, merge_lora
    c=AliConfig(vocab_size=64,hidden_size=32,intermediate_size=64,num_hidden_layers=1,num_attention_heads=4,num_key_value_heads=4,max_position_embeddings=32)
    m=ALIForCausalLM(c); names=apply_lora(m,rank=2); assert names
    assert any('lora_A' in n for n,_ in m.named_parameters())
    p=save_lora_adapter(m,tmp_path/'adapter'); assert (p/'adapter_model.safetensors').exists() or (p/'adapter_model.pt').exists()
    assert merge_lora(m)>=1

def test_archive_traversal_block(tmp_path):
    from data_engine.parsers import safe_extract_zip
    z=tmp_path/'bad.zip';
    with zipfile.ZipFile(z,'w') as f: f.writestr('../escape.txt','bad')
    with pytest.raises(ValueError): safe_extract_zip(z,tmp_path/'out')

def test_knowledge_ingest(tmp_path):
    from data_engine.harvester import Harvester
    from training.dataset import build_chat_dataset, build_causal_dataset
    from knowledge.ingest import ingest_harvest
    root=tmp_path/'src'; root.mkdir(); (root/'notes.md').write_text('Python is useful for automation.\nUser: what is python?\nAssistant: a programming language.\n',encoding='utf-8')
    hdb=tmp_path/'h.sqlite'; s=Harvester(hdb).scan(root); assert s['files']>=1
    out=tmp_path/'train'; a=build_chat_dataset(hdb,out); b=build_causal_dataset(hdb,out); assert a['train']>0; assert b['train']>0; assert (out/'chat_train.jsonl').exists(); assert (out/'cpt_train.jsonl').exists()
    k=ingest_harvest(hdb,tmp_path/'k.sqlite'); assert k['chunks']>=1

def test_runtime_no_model(tmp_path):
    from core.runtime import ALIRuntime
    r=ALIRuntime(tmp_path,tmp_path/'x.sqlite',None,False)
    x=r.answer([{'role':'user','content':'hello'}],tmp_path)
    assert x['mode']=='no_model'
