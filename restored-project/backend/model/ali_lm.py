# -*- coding: utf-8 -*-
"""ALI neural language model: a small Llama-compatible decoder trained from scratch.

The architecture intentionally mirrors the tensor naming/layout used by Llama-family
models so a trained ALI checkpoint can be exported to a HuggingFace-style folder and
converted with llama.cpp's official HF->GGUF converter. No base model is downloaded or
required: weights are initialized randomly and learned only from ALI's datasets.
"""
from __future__ import annotations
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Optional, Dict, Any, Iterator, Tuple
import json, math
import torch
from torch import nn
import torch.nn.functional as F

@dataclass
class AliConfig:
    vocab_size:int=4096
    hidden_size:int=256
    intermediate_size:int=1024
    num_hidden_layers:int=6
    num_attention_heads:int=8
    num_key_value_heads:int=8
    max_position_embeddings:int=512
    rms_norm_eps:float=1e-6
    rope_theta:float=10000.0
    attention_dropout:float=0.0
    bos_token_id:int=1
    eos_token_id:int=2
    pad_token_id:int=3
    model_type:str='llama'
    architectures:Tuple[str,...]=('LlamaForCausalLM',)
    hidden_act:str='silu'
    initializer_range:float=0.02
    use_cache:bool=True
    use_sdpa:bool=True
    tie_word_embeddings:bool=False
    torch_dtype:str='float32'
    def to_dict(self)->Dict[str,Any]:
        d=asdict(self); d['architectures']=list(self.architectures); return d
    @classmethod
    def from_dict(cls,d:Dict[str,Any]):
        d=dict(d); d['architectures']=tuple(d.get('architectures',('LlamaForCausalLM',))); return cls(**{k:v for k,v in d.items() if k in cls.__dataclass_fields__})
    @classmethod
    def auto_2gb(cls):
        return cls(vocab_size=4096,hidden_size=256,intermediate_size=1024,num_hidden_layers=6,num_attention_heads=8,num_key_value_heads=8,max_position_embeddings=512)

class RMSNorm(nn.Module):
    def __init__(self,dim,eps=1e-6): super().__init__(); self.weight=nn.Parameter(torch.ones(dim)); self.eps=eps
    def forward(self,x): return x*torch.rsqrt(x.pow(2).mean(-1,keepdim=True)+self.eps)*self.weight

def _rotate_half(x):
    half=x.size(-1)//2
    x1=x[...,:half]; x2=x[...,half:]
    return torch.cat((-x2,x1),dim=-1)

def _rope(x, cos, sin): return x*cos + _rotate_half(x)*sin

class RotaryEmbedding(nn.Module):
    def __init__(self,head_dim,max_pos,theta):
        super().__init__(); inv_freq=1.0/(theta**(torch.arange(0,head_dim,2).float()/head_dim)); self.register_buffer('inv_freq',inv_freq,persistent=False); self.max_pos=max_pos; self.cache={}
    def forward(self,seq_len:int,device,dtype):
        key=(seq_len,device.type,str(device),str(dtype))
        if key in self.cache: return self.cache[key]
        t=torch.arange(seq_len,device=device,dtype=self.inv_freq.dtype); freqs=torch.einsum('i,j->ij',t,self.inv_freq); emb=torch.cat((freqs,freqs),dim=-1); cos=emb.cos()[None,None,:,:].to(dtype); sin=emb.sin()[None,None,:,:].to(dtype); self.cache[key]=(cos,sin); return cos,sin

class ALIAttention(nn.Module):
    def __init__(self,c:AliConfig):
        super().__init__(); self.num_heads=c.num_attention_heads; self.num_kv_heads=c.num_key_value_heads; self.head_dim=c.hidden_size//c.num_attention_heads; self.scale=self.head_dim**-0.5
        self.q_proj=nn.Linear(c.hidden_size,c.hidden_size,bias=False); self.k_proj=nn.Linear(c.hidden_size,c.num_key_value_heads*self.head_dim,bias=False); self.v_proj=nn.Linear(c.hidden_size,c.num_key_value_heads*self.head_dim,bias=False); self.o_proj=nn.Linear(c.hidden_size,c.hidden_size,bias=False); self.rotary=RotaryEmbedding(self.head_dim,c.max_position_embeddings,c.rope_theta)
    def forward(self,x,attention_mask=None,past_key_value=None,use_cache=False, use_sdpa=True):
        b,t,_=x.shape; q=self.q_proj(x).view(b,t,self.num_heads,self.head_dim).transpose(1,2); k=self.k_proj(x).view(b,t,self.num_kv_heads,self.head_dim).transpose(1,2); v=self.v_proj(x).view(b,t,self.num_kv_heads,self.head_dim).transpose(1,2)
        past_len=0
        if past_key_value is not None: past_len=past_key_value[0].size(2)
        cos,sin=self.rotary(past_len+t,x.device,x.dtype); q=_rope(q,cos[:,:,past_len:past_len+t],sin[:,:,past_len:past_len+t]); k=_rope(k,cos[:,:,past_len:past_len+t],sin[:,:,past_len:past_len+t])
        if past_key_value is not None: k=torch.cat([past_key_value[0],k],2); v=torch.cat([past_key_value[1],v],2)
        if self.num_kv_heads != self.num_heads:
            rep=self.num_heads//self.num_kv_heads; k=k.repeat_interleave(rep,dim=1); v=v.repeat_interleave(rep,dim=1)
        kv_len=k.size(-2)
        if use_sdpa and past_key_value is None:
            if attention_mask is not None and attention_mask.dim()==2:
                am=(~attention_mask.bool()).to(dtype=q.dtype)*-1e4
                am=am[:,None,None,:].expand(b,1,t,kv_len)
                # causal diagonal is handled independently; padding is additive.
                base=torch.zeros((t,kv_len),device=x.device,dtype=q.dtype)
                causal=torch.triu(torch.full_like(base,float('-inf')),diagonal=1)
                attn_mask=causal[None,None,:,:]+am
                out=F.scaled_dot_product_attention(q,k,v,attn_mask=attn_mask,dropout_p=0.0)
            else:
                out=F.scaled_dot_product_attention(q,k,v,is_causal=True,dropout_p=0.0)
        else:
            scores=torch.matmul(q,k.transpose(-2,-1))*self.scale
            if attention_mask is None:
                allowed = torch.arange(kv_len,device=x.device)[None,:] <= (past_len + torch.arange(t,device=x.device))[:,None]
                scores=scores.masked_fill(~allowed[None,None,:,:],float('-inf'))
            else:
                scores=scores+attention_mask
            out=torch.softmax(scores.float(),-1).to(q.dtype)@v
        out=out.transpose(1,2).contiguous().view(b,t,-1); return self.o_proj(out),(k,v) if use_cache else None

class ALIMLP(nn.Module):
    def __init__(self,c):
        super().__init__(); self.gate_proj=nn.Linear(c.hidden_size,c.intermediate_size,bias=False); self.up_proj=nn.Linear(c.hidden_size,c.intermediate_size,bias=False); self.down_proj=nn.Linear(c.intermediate_size,c.hidden_size,bias=False)
    def forward(self,x): return self.down_proj(F.silu(self.gate_proj(x))*self.up_proj(x))

class ALILayer(nn.Module):
    def __init__(self,c):
        super().__init__(); self.input_layernorm=RMSNorm(c.hidden_size,c.rms_norm_eps); self.self_attn=ALIAttention(c); self.post_attention_layernorm=RMSNorm(c.hidden_size,c.rms_norm_eps); self.mlp=ALIMLP(c)
    def forward(self,x,attention_mask=None,past_key_value=None,use_cache=False,use_sdpa=True):
        h=x
        attn_out,kv=self.self_attn(self.input_layernorm(h),attention_mask=attention_mask,past_key_value=past_key_value,use_cache=use_cache,use_sdpa=use_sdpa)
        h=h+attn_out
        h=h+self.mlp(self.post_attention_layernorm(h))
        return h,kv

class ALIForCausalLM(nn.Module):
    def __init__(self,c:AliConfig):
        super().__init__(); self.config=c; self.embed_tokens=nn.Embedding(c.vocab_size,c.hidden_size,padding_idx=c.pad_token_id); self.layers=nn.ModuleList([ALILayer(c) for _ in range(c.num_hidden_layers)]); self.norm=RMSNorm(c.hidden_size,c.rms_norm_eps); self.lm_head=nn.Linear(c.hidden_size,c.vocab_size,bias=False); self.gradient_checkpointing=False
        self.apply(self._init_weights)
    def _init_weights(self,m):
        if isinstance(m,nn.Linear): nn.init.normal_(m.weight,0.0,0.02)
        elif isinstance(m,nn.Embedding): nn.init.normal_(m.weight,0.0,0.02)
        elif isinstance(m,RMSNorm): nn.init.ones_(m.weight)
    def forward(self,input_ids=None,labels=None,past_key_values=None,use_cache=False,attention_mask=None,inputs_embeds=None):
        h=self.embed_tokens(input_ids) if inputs_embeds is None else inputs_embeds; new=[]
        for i,layer in enumerate(self.layers):
            past=past_key_values[i] if past_key_values else None
            if self.training and self.gradient_checkpointing and past is None and not use_cache:
                from torch.utils.checkpoint import checkpoint
                h=checkpoint(lambda inp: layer(inp,attention_mask=attention_mask,use_cache=False,use_sdpa=self.config.use_sdpa)[0], h, use_reentrant=False)
                kv=None
            else:
                h,kv=layer(h,attention_mask=attention_mask,past_key_value=past,use_cache=use_cache,use_sdpa=self.config.use_sdpa)
            new.append(kv)
        logits=self.lm_head(self.norm(h))
        loss=None
        if labels is not None:
            shift_logits=logits[...,:-1,:].contiguous(); shift_labels=labels[...,1:].contiguous(); loss=F.cross_entropy(shift_logits.view(-1,shift_logits.size(-1)),shift_labels.view(-1),ignore_index=-100)
        return {'loss':loss,'logits':logits,'past_key_values':tuple(new) if use_cache else None}
    @torch.no_grad()
    def generate_stream(self,input_ids=None,max_new_tokens=128,temperature=0.7,top_k=40,eos_token_id:Optional[int]=2,inputs_embeds=None,bad_token_ids=None,stop_token_ids=None)->Iterator[int]:
        self.eval(); bad=set(int(x) for x in (bad_token_ids or [])); stops=set(int(x) for x in (stop_token_ids or []));
        if eos_token_id is not None: stops.add(int(eos_token_id))
        def pick(logits):
            logits=logits.clone()
            for bid in bad:
                if 0 <= bid < logits.size(-1): logits[...,bid]=float('-inf')
            if temperature<=0:
                return int(torch.argmax(logits,-1).item())
            l=logits/temperature
            if top_k and top_k < l.size(-1):
                val,idx=torch.topk(l,top_k,dim=-1); probs=torch.softmax(val,-1); choice=torch.multinomial(probs,1); return int(idx.gather(-1,choice).item())
            return int(torch.multinomial(torch.softmax(l,-1),1).item())
        if inputs_embeds is not None:
            out=self(inputs_embeds=inputs_embeds,use_cache=True); cache=out['past_key_values']; logits=out['logits'][:,-1,:]
            for _ in range(max_new_tokens):
                next_id=pick(logits)
                if next_id in stops: break
                yield next_id
                inp=torch.tensor([[next_id]],device=inputs_embeds.device,dtype=torch.long); out=self(inp,use_cache=True,past_key_values=cache); cache=out['past_key_values']; logits=out['logits'][:,-1,:]
            return
        out=self(input_ids,use_cache=True); cache=out['past_key_values']; logits=out['logits'][:,-1,:]
        for _ in range(max_new_tokens):
            next_id=pick(logits)
            if next_id in stops: break
            yield next_id
            inp=torch.tensor([[next_id]],device=input_ids.device,dtype=input_ids.dtype); out=self(inp,use_cache=True,past_key_values=cache); cache=out['past_key_values']; logits=out['logits'][:,-1,:]

def save_hf_checkpoint(model:ALIForCausalLM, tokenizer_dir:str|Path, out_dir:str|Path, metadata:Optional[Dict[str,Any]]=None)->Path:
    out=Path(out_dir); out.mkdir(parents=True,exist_ok=True)
    (out/'config.json').write_text(json.dumps(model.config.to_dict(),ensure_ascii=False,indent=2),encoding='utf-8')
    # Export with HuggingFace/Llama-compatible `model.` prefix. Internal ALI checkpoints remain unprefixed.
    state={('model.'+k if not k.startswith('lm_head.') else k):v.detach().cpu().contiguous() for k,v in model.state_dict().items()}
    try:
        from safetensors.torch import save_file
        save_file(state,str(out/'model.safetensors'),metadata={'format':'pt','source':'ALI Studio trained-from-scratch','architecture':'LlamaForCausalLM'})
    except Exception:
        torch.save(state,out/'pytorch_model.bin')
    tok=Path(tokenizer_dir)
    for name in ('tokenizer.model','tokenizer.json','tokenizer_config.json','special_tokens_map.json'):
        src=tok/name
        if src.exists(): (out/name).write_bytes(src.read_bytes())
    meta=dict(metadata or {}); meta.setdefault('parameter_count',sum(v.numel() for v in model.parameters())); meta.setdefault('source','ALI Studio trained-from-scratch'); meta.setdefault('architecture','LlamaForCausalLM')
    (out/'ali_metadata.json').write_text(json.dumps(meta,ensure_ascii=False,indent=2),encoding='utf-8')
    return out

def load_state(model:ALIForCausalLM,path:str|Path,device='cpu')->None:
    p=Path(path)
    if p.suffix=='.safetensors':
        from safetensors.torch import load_file; sd=load_file(str(p),device=str(device))
    else: sd=torch.load(p,map_location=device,weights_only=True)
    if any(k.startswith('model.') for k in sd):
        sd={k[6:] if k.startswith('model.') else k:v for k,v in sd.items()}
    missing,unexpected=model.load_state_dict(sd,strict=False)
    if missing: raise ValueError(f'Missing model tensors: {missing[:8]}')
