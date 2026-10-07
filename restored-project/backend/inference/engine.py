# -*- coding: utf-8 -*-
"""Local ALI inference engine — ALI's own trained neural model only."""
from __future__ import annotations
from pathlib import Path
from typing import Iterator
import json, torch
from model.ali_lm import AliConfig, ALIForCausalLM, load_state
from tokenizer.spm import AliTokenizer
from inference.context import fit_messages

class LocalInference:
    def __init__(self, model_dir:str|Path, tokenizer_dir:str|Path|None=None, device:str='cpu'):
        self.model_dir=Path(model_dir); tok_path=Path(tokenizer_dir or model_dir); self.tokenizer=AliTokenizer(tok_path/'tokenizer.model' if tok_path.is_dir() else tok_path); self.device=torch.device(device)
        cfg=json.loads((self.model_dir/'config.json').read_text(encoding='utf-8')); self.model_version=self.model_dir.name; self.model=ALIForCausalLM(AliConfig.from_dict(cfg)); state=self.model_dir/'model.safetensors'
        if not state.exists(): state=self.model_dir/'pytorch_model.bin'
        load_state(self.model,state,self.device)
        self.dtype='float32'
        if self.device.type=='cuda':
            self.model.half(); self.dtype='float16'
        self.model.eval()
    def prompt(self,messages:list[dict],system:str='')->str:
        rows=[]
        if system: rows.append({'role':'system','content':system})
        rows.extend(messages)
        return ''.join(f"<|{m['role']}|>\n{m['content']}<|eot|>\n" for m in rows)+'<|assistant|>\n'
    def stream(self,messages:list[dict],system:str='',max_new_tokens:int=128,temperature:float=.7,top_k:int=40,context_size:int|None=None)->Iterator[str]:
        rows=[]
        if system: rows.append({'role':'system','content':system})
        rows.extend(messages)
        rows,_budget=fit_messages(rows,self.tokenizer,int(context_size or self.model.config.max_position_embeddings),reserved_output=int(max_new_tokens)+8)
        p=self.prompt([m for m in rows if m.get('role')!='system'],system=next((m['content'] for m in rows if m.get('role')=='system'),'')); ids=self.tokenizer.encode(p,add_bos=True,add_eos=False); max_ctx=self.model.config.max_position_embeddings; ids=ids[-max(1,max_ctx-max_new_tokens):]
        inp=torch.tensor([ids],dtype=torch.long,device=self.device); out=[]; last_text=''
        with torch.inference_mode():
            for tok in self.model.generate_stream(inp,max_new_tokens=max_new_tokens,temperature=temperature,top_k=top_k,eos_token_id=self.tokenizer.eos_id,bad_token_ids=[self.tokenizer.sp.unk_id(),self.tokenizer.bos_id,self.tokenizer.pad_id]+[self.tokenizer.special_id(x) for x in ('<|system|>','<|user|>','<|assistant|>','<|eot|>') if self.tokenizer.special_id(x)>=0],stop_token_ids=[self.tokenizer.eos_id,self.tokenizer.special_id('<|eot|>')]):
                out.append(tok)
                piece=self.tokenizer.decode(out)
                delta=piece[len(last_text):] if piece.startswith(last_text) else piece
                if delta:
                    yield delta
                last_text=piece
    def complete(self,prompt,**kwargs)->str:
        rows=prompt if isinstance(prompt,list) else [{'role':'user','content':str(prompt)}]
        return ''.join(self.stream(rows,**kwargs))


# Compatibility alias used by integrations.
InferenceEngine = LocalInference
