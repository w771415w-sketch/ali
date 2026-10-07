# -*- coding: utf-8 -*-
"""Dynamic power/thermal/memory policy for local execution."""
from __future__ import annotations
def choose_policy(hardware, mode="auto"):
    ram=float(getattr(hardware,"ram_gb",0) or 0); free=float(getattr(hardware,"ram_available_gb",0) or 0); threads=int(getattr(hardware,"cpu_threads",getattr(hardware,"cpu_cores",1)) or 1)
    battery=float(getattr(hardware,"battery_percent",-1) or -1); plugged=getattr(hardware,"power_plugged",None); temp=float(getattr(hardware,"temperature_c",0) or 0); vram=float(getattr(hardware,"vram_gb",0) or 0)
    max_threads=max(1,min(6,threads-2)) if threads>2 else 1
    p={"profile":"thinkpad-p50" if ram>=24 and vram<3 else "adaptive","training_device":"cpu","training_enabled":True,"training_requires_ac_power":True,"max_cpu_threads":max_threads,"torch_threads":max_threads,"torch_interop_threads":1,"recommended_context":320 if ram>=24 else 288 if ram>=16 else 256,"max_context":384 if ram>=24 else 352 if ram>=16 else 320,"recommended_max_new_tokens":160 if ram>=24 else 144 if ram>=16 else 128,"max_new_tokens":192 if ram>=24 else 176 if ram>=16 else 160,"max_concurrent_jobs":1,"max_concurrent_inference":1,"gpu_training":False,"gpu_inference":"optional-offload" if vram>=2 else "disabled","min_free_ram_gb":4.0,"train_device":"cpu","gpu_memory_fraction":0.60,"recommended_seq_len":256 if ram>=24 else 224 if ram>=16 else 192,"power_state":"unknown" if plugged is None else "ac" if plugged else "battery","runtime_mode":"normal"}
    if temp>=88:p.update(training_enabled=False,runtime_mode="thermal-hard-stop")
    elif temp>=80:p.update(training_enabled=False,runtime_mode="thermal-guard")
    elif free and free<4:p.update(training_enabled=False,runtime_mode="memory-guard")
    elif battery>=0 and battery<=25 and plugged is not True:p.update(training_enabled=False,runtime_mode="battery-hard-stop")
    elif plugged is False:p.update(training_enabled=False,runtime_mode="battery-no-training")
    elif battery>=0 and battery<45 and plugged is not True:p.update(runtime_mode="battery-saver",max_context=256,max_new_tokens=128)
    return p
def training_allowed(hardware):return bool(choose_policy(hardware)["training_enabled"])
def gguf_offload_policy(hardware,mode="auto",total_layers=0):
    mode=str(mode or "auto").lower();vram=float(getattr(hardware,"vram_gb",0) or 0);cap=getattr(hardware,"cuda_capability",None);cuda_cap=tuple(cap) if cap else (0,0)
    if mode=="cpu":return {"device":"cpu","n_gpu_layers":0,"gpu_memory_fraction":0.0,"reason":"cpu_forced"}
    if mode in {"gpu","cuda"} or (mode=="auto" and vram>=2):return {"device":"cuda","n_gpu_layers":int(total_layers or 0),"gpu_memory_fraction":0.60,"cuda_capability":cuda_cap,"reason":"optional_offload"}
    return {"device":"cpu","n_gpu_layers":0,"gpu_memory_fraction":0.0,"reason":"no_gpu"}
