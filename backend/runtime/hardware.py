# -*- coding: utf-8 -*-
"""Runtime hardware detection and compatibility profile for ALI."""
from __future__ import annotations
from dataclasses import dataclass,asdict
import json,os,platform,subprocess
from pathlib import Path
try: import psutil
except Exception: psutil=None
ROOT=Path(__file__).resolve().parents[1]; PROFILE_PATH=ROOT/"config"/"hardware_profile.json"
@dataclass
class HardwareInfo:
    os:str=""; python:str=""; cpu_cores:int=0; ram_gb:float=0.0; gpu_available:bool=False; gpu_name:str="CPU"; vram_gb:float=0.0; torch_cuda:bool=False; disk_free_gb:float=0.0; cuda_capability:tuple[int,int]|None=None; physical_cores:int=0; backend_hint:str=""; gpu_mem_used_gb:float=0.0; gpu_mem_free_gb:float=0.0; cuda_self_test:bool=False
    device_name:str="Unknown"; model:str=""; os_name:str=""; cpu_model:str=""; cpu_threads:int=0; ram_available_gb:float=0.0; ram_used_percent:float=0.0; gpu_percent:float=0.0; temperature_c:float=0.0; battery_percent:float=-1.0; battery_minutes:int=-1; power_plugged:bool|None=None
    def __post_init__(self):
        if not self.cpu_threads:self.cpu_threads=self.cpu_cores
        if not self.cpu_cores:self.cpu_cores=self.cpu_threads
        if not self.physical_cores:self.physical_cores=max(1,self.cpu_cores//2 if self.cpu_cores else 1)
        if not self.os_name:self.os_name=self.os or platform.platform()
        if not self.os:self.os=self.os_name
        if not self.python:self.python=platform.python_version()
        if self.gpu_available is False and self.gpu_name not in {"","CPU"}:self.gpu_available=True
        if self.torch_cuda and not self.cuda_self_test:self.cuda_self_test=True
        if self.vram_gb and not self.gpu_mem_free_gb:self.gpu_mem_free_gb=max(0.0,self.vram_gb-self.gpu_mem_used_gb)
    def to_dict(self):return asdict(self)
def _profile():
    try:return json.loads(PROFILE_PATH.read_text(encoding="utf-8"))
    except Exception:return {}
def _nvidia_probe():
    try:
        r=subprocess.run(["nvidia-smi","--query-gpu=name,memory.total,utilization.gpu,memory.used,memory.free","--format=csv,noheader,nounits"],capture_output=True,timeout=2,check=False,creationflags=getattr(subprocess,"CREATE_NO_WINDOW",0))
        if r.returncode!=0:return {}
        p=[x.strip() for x in r.stdout.decode("utf-8","replace").splitlines()[0].split(",")]
        return {"gpu_name":p[0],"vram_gb":round(float(p[1])/1024,2),"gpu_percent":float(p[2]),"gpu_mem_used_gb":round(float(p[3])/1024,2),"gpu_mem_free_gb":round(float(p[4])/1024,2)}
    except Exception:return {}
def detect(probe_torch=False,force=False):
    p=_profile();logical=int(os.cpu_count() or p.get("cpu_threads",1));physical=logical
    if psutil:
        try:physical=int(psutil.cpu_count(logical=False) or logical)
        except Exception:pass
    h=HardwareInfo(os=str(p.get("os_label") or platform.platform()),python=platform.python_version(),cpu_cores=logical,ram_gb=float(p.get("ram_gb",0) or 0),gpu_available=bool(p.get("gpu_name") and p.get("gpu_name")!="CPU"),gpu_name=str(p.get("gpu_name","CPU")),vram_gb=float(p.get("vram_gb",0) or 0),cuda_capability=tuple(p.get("cuda_capability")) if p.get("cuda_capability") else None,physical_cores=physical,device_name=str(p.get("device_name","Unknown")),model=str(p.get("model","")),os_name=str(p.get("os_label") or platform.platform()),cpu_model=str(p.get("cpu_model","")),ram_available_gb=float(p.get("ram_available_gb_observed",0) or 0),temperature_c=float(p.get("cpu_temp_c",p.get("notes",{}).get("cpu_temperature_c",0)) or 0),battery_percent=float(p.get("battery_percent_observed",p.get("battery_percent",-1)) or -1),battery_minutes=int(p.get("battery_minutes_observed",p.get("battery_minutes",-1)) or -1))
    if psutil:
        try:vm=psutil.virtual_memory();h.ram_gb=round(vm.total/2**30,2);h.ram_available_gb=round(vm.available/2**30,2);h.ram_used_percent=float(vm.percent)
        except Exception:pass
        try:h.cpu_percent=float(psutil.cpu_percent(interval=None))
        except Exception:pass
        try:b=psutil.sensors_battery();h.battery_percent=float(b.percent);h.power_plugged=bool(b.power_plugged) if b is not None else None;h.battery_minutes=max(0,int(b.secsleft//60)) if b is not None and b.secsleft not in (psutil.POWER_TIME_UNLIMITED,psutil.POWER_TIME_UNKNOWN) else -1
        except Exception:pass
    g=_nvidia_probe()
    if g:h.gpu_name=g["gpu_name"];h.vram_gb=g["vram_gb"];h.gpu_percent=g["gpu_percent"];h.gpu_mem_used_gb=g["gpu_mem_used_gb"];h.gpu_mem_free_gb=g["gpu_mem_free_gb"];h.gpu_available=True;h.backend_hint="cuda"
    if probe_torch:
        try:
            import torch
            if torch.cuda.is_available():h.torch_cuda=True;h.cuda_self_test=True;h.cuda_capability=tuple(map(int,torch.cuda.get_device_capability(0)));h.gpu_name=torch.cuda.get_device_name(0);h.gpu_available=True;h.vram_gb=round(torch.cuda.get_device_properties(0).total_memory/2**30,2);h.gpu_mem_free_gb=h.vram_gb
        except Exception:pass
    h.__post_init__();return h
def apply_cuda_memory_budget(fraction=0.60):
    try:
        import torch
        if torch.cuda.is_available():torch.cuda.set_per_process_memory_fraction(max(.1,min(float(fraction),.95)));return {"ok":True,"fraction":float(fraction)}
    except Exception as exc:return {"ok":False,"error":str(exc)}
    return {"ok":False,"status":"cuda_unavailable"}
def training_profile(hardware,mode="cpu"):
    from config.device_profiles import recommend_for_hardware
    p=recommend_for_hardware(hardware);t=dict(p["training"]);t.update(device="cpu",cpu_threads=6,amp=False,seq_len=256,context=320)
    m=str(mode or "cpu").lower();free=float(getattr(hardware,"gpu_mem_free_gb",0) or 0);cuda=bool(getattr(hardware,"torch_cuda",False) or getattr(hardware,"cuda_self_test",False) or getattr(hardware,"gpu_available",False))
    if m in {"gpu","cuda"}:
        if not cuda or free<1.0:raise RuntimeError("usable CUDA/VRAM unavailable")
        t.update(device="cuda",seq_len=192,context=256,amp=False)
    elif m=="auto" and cuda and free>=1.0:t.update(device="cuda",seq_len=192,context=256,amp=False)
    return t
def model_profile(hardware):
    from training.scaling import get
    p=get("small");return {"hidden":p.hidden_size,"intermediate":p.intermediate_size,"layers":p.layers,"heads":p.heads,"vocab_size":p.vocab_size,"context":p.context}
