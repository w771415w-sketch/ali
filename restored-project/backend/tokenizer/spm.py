# -*- coding: utf-8 -*-
"""SentencePiece tokenizer trained locally for ALI's decoder model."""
from __future__ import annotations
from pathlib import Path
import json, os, re

SPECIAL = ['<pad>','<s>','</s>','<|system|>','<|user|>','<|assistant|>','<|eot|>']

class AliTokenizer:
    def __init__(self, model_path:str|Path):
        import sentencepiece as spm
        self.model_path=Path(model_path); self.sp=spm.SentencePieceProcessor(model_file=str(self.model_path))
    @property
    def vocab_size(self): return int(self.sp.get_piece_size())
    @property
    def bos_id(self): return int(self.sp.bos_id())
    @property
    def eos_id(self): return int(self.sp.eos_id())
    @property
    def pad_id(self): return int(self.sp.pad_id())
    def special_id(self,piece:str)->int:return int(self.sp.piece_to_id(piece))
    def encode(self,text:str,add_bos=True,add_eos=True):
        ids=self.sp.encode(text,out_type=int); return ([self.bos_id] if add_bos else [])+ids+([self.eos_id] if add_eos else [])
    def decode(self,ids): return self.sp.decode(list(map(int,ids)))

def train_sentencepiece(input_files:list[str]|str, output_dir:str|Path, vocab_size:int=4096, character_coverage:float=0.9995)->Path:
    import sentencepiece as spm
    out=Path(output_dir); out.mkdir(parents=True,exist_ok=True); prefix=out/'tokenizer'; files=','.join(input_files) if isinstance(input_files,list) else str(input_files); vocab_size=max(512,int(vocab_size))
    spm.SentencePieceTrainer.Train(input=files,model_prefix=str(prefix),vocab_size=vocab_size,model_type='unigram',character_coverage=character_coverage,bos_id=1,eos_id=2,unk_id=0,pad_id=3, user_defined_symbols='<|system|>,<|user|>,<|assistant|>,<|eot|>',normalization_rule_name='nmt_nfkc',remove_extra_whitespaces=False,byte_fallback=True,hard_vocab_limit=False)
    (out/'tokenizer_config.json').write_text(json.dumps({'model_type':'llama','add_bos_token':True,'add_eos_token':False,'bos_token':'<s>','eos_token':'</s>','pad_token':'<pad>','unk_token':'<unk>','chat_template':"<s>{% for message in messages %}<|{{ message['role'] }}|>\n{{ message['content'] }}<|eot|>\n{% endfor %}<|assistant|>\n"} ,ensure_ascii=False,indent=2),encoding='utf-8')
    (out/'special_tokens_map.json').write_text(json.dumps({'bos_token':'<s>','eos_token':'</s>','pad_token':'<pad>','unk_token':'<unk>','additional_special_tokens':['<|system|>','<|user|>','<|assistant|>','<|eot|>']},ensure_ascii=False,indent=2),encoding='utf-8')
    return out/'tokenizer.model'
