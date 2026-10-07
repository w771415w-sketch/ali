# -*- coding: utf-8 -*-
from __future__ import annotations
from dataclasses import dataclass,asdict
from copy import deepcopy
@dataclass(frozen=True)
class ScaleProfile:
    name:str; hidden_size:int; intermediate_size:int; layers:int; heads:int; vocab_size:int; context:int; target_params:int; note:str
PROFILES={"micro":ScaleProfile("micro",192,768,4,6,4096,256,1_000_000,"P50 smoke/bootstrap"),"small":ScaleProfile("small",256,1024,6,8,8192,384,10_000_000,"P50 local research"),"medium":ScaleProfile("medium",512,2048,12,8,16000,1024,100_000_000,"strong workstation/server"),"large":ScaleProfile("large",1024,4096,24,16,32000,2048,500_000_000,"multi-GPU"),"xlarge":ScaleProfile("xlarge",2048,8192,32,32,64000,4096,2_000_000_000,"cluster-scale")}
def get(name):
    if name not in PROFILES:raise KeyError(f"unknown scale profile: {name}")
    return PROFILES[name]
def estimated_param_count(p):
    h,i,l,v=p.hidden_size,p.intermediate_size,p.layers,p.vocab_size;return int(v*h*2+l*(4*h*h+3*h*i+4*h))
def estimate_memory_gb(params,dtype_bytes=4.0,optimizer_multiplier=8.0,gradients=True,activation_factor=1.5):
    base=params*(dtype_bytes+(dtype_bytes if gradients else 0)+optimizer_multiplier)/(1024**3);return base*activation_factor
def build_training_plan(*args,**kwargs):
    if args and isinstance(args[0],str):
        name=args[0];hardware=args[1] if len(args)>1 else kwargs.get("hardware");p=get(name);params=estimated_param_count(p);ram=float(getattr(hardware,"ram_gb",0) or 0);vram=float(getattr(hardware,"vram_gb",0) or 0);threads=int(getattr(hardware,"cpu_cores",getattr(hardware,"cpu_threads",1)) or 1);cap=getattr(hardware,"cuda_capability",None);legacy=bool(cap and tuple(cap)<(6,0));mem=estimate_memory_gb(params);fits_ram=mem<=max(.5,ram*.55);fits_vram=estimate_memory_gb(params,2.0)<=max(.5,vram*.65) if vram else False
        return {"profile":asdict(p),"estimated_parameters":params,"estimated_training_memory_gb":round(mem,2),"hardware_ram_gb":ram,"hardware_vram_gb":vram,"fits_2gb_vram":bool(fits_vram and vram<=2.1),"fits_ram_estimate":fits_ram,"strategy":"CPU-first" if vram<3 or legacy else "GPU/CPU adaptive","recommended_cpu_threads":min(6,max(1,threads-2)),"recommendation":"usable-bootstrap" if fits_ram else "requires-more-memory-or-smaller-profile"}
    hardware=args[0] if args else kwargs.get("hardware");requested_scale=kwargs.get("requested_scale",args[1] if len(args)>1 else "small");steps=kwargs.get("steps",0)
    from config.device_profiles import recommend_for_hardware
    profile=deepcopy(recommend_for_hardware(hardware));t=profile["training"];scale=requested_scale if requested_scale in {"micro","small"} else t["scale"];base=PROFILES[scale];t.update({"scale":scale,"seq_len":base.context if scale=="micro" else 256,"batch_size":1,"grad_accum":8 if scale=="micro" else 16,"requested_steps":int(steps or 0)});return {"profile_id":profile["id"],"hardware":profile["label"],"training":t}
