# -*- coding: utf-8 -*-
"""Runtime hardware detection with safe P50 fallback values."""
from __future__ import annotations
from dataclasses import dataclass, asdict
import json, os, platform, subprocess
from pathlib import Path
try: import psutil
except Exception: psutil=None
ROOT=Path(__file__).resolve().parents[1]; PROFILE_PATH=ROOT/"config"/"hardware_profile.json"

@dataclass
class HardwareInfo:
    device_name:str="Unknown"; model:str=""; os_name:str=""; cpu_model:str=""; cpu_threads:int=1; physical_cores:int=1
    ram_gb:float=0.0; ram_available_gb:float=0.0; ram_used_percent:float=0.0
    gpu_name:str="CPU"; vram_gb:float=0.0; gpu_percent:float=0.0; cuda_capability:tuple[int,int]|None=None
    cpu_percent:float=0.0; temperature_c:float=0.0; battery_percent:float=-1.0; battery_minutes:int=-1; power_plugged:bool|None=None
    def to_dict(self): return asdict(self)

def _profile():
    try: return json.loads(PROFILE_PATH.read_text(encoding="utf-8"))
    except Exception: return {}

def _nvidia_probe():
    try:
        r=subprocess.run(["nvidia-smi","--query-gpu=name,memory.total,utilization.gpu","--format=csv,noheader,nounits"],
                         capture_output=True,timeout=2,check=False,creationflags=getattr(subprocess,"CREATE_NO_WINDOW",0))
        if r.returncode!=0: return {}
        p=[x.strip() for x in r.stdout.decode("utf-8","replace").splitlines()[0].split(",")]
        return {"gpu_name":p[0],"vram_gb":round(float(p[1])/1024,2),"gpu_percent":float(p[2])}
    except Exception: return {}

def detect(probe_torch=False):
    p=_profile(); logical=int(os.cpu_count() or p.get("cpu_threads",1)); physical=logical
    if psutil:
        try: physical=int(psutil.cpu_count(logical=False) or logical)
        except Exception: pass
    h=HardwareInfo(device_name=str(p.get("device_name","Unknown")),model=str(p.get("model","")),
      os_name=str(p.get("os_label") or platform.platform()),cpu_model=str(p.get("cpu_model","")),
      cpu_threads=logical,physical_cores=physical,ram_gb=float(p.get("ram_gb",0) or 0),
      ram_available_gb=float(p.get("ram_available_gb_observed",0) or 0),
      gpu_name=str(p.get("gpu_name","CPU")),vram_gb=float(p.get("vram_gb",0) or 0),
      temperature_c=float(p.get("notes",{}).get("cpu_temperature_c",p.get("cpu_temp_c",0)) or 0),
      battery_percent=float(p.get("battery_percent_observed",p.get("battery_percent",-1)) or -1),
      battery_minutes=int(p.get("battery_minutes_observed",p.get("battery_minutes",-1)) or -1))
    if psutil:
        try:
            vm=psutil.virtual_memory(); h.ram_gb=round(vm.total/2**30,2); h.ram_available_gb=round(vm.available/2**30,2); h.ram_used_percent=float(vm.percent)
        except Exception: pass
        try: h.cpu_percent=float(psutil.cpu_percent(interval=None))
        except Exception: pass
        try:
            b=psutil.sensors_battery()
            if b is not None:
                h.battery_percent=float(b.percent); h.power_plugged=bool(b.power_plugged)
                if b.secsleft not in (psutil.POWER_TIME_UNLIMITED,psutil.POWER_TIME_UNKNOWN): h.battery_minutes=max(0,int(b.secsleft//60))
        except Exception: pass
    g=_nvidia_probe()
    if g: h.gpu_name=g["gpu_name"]; h.vram_gb=g["vram_gb"]; h.gpu_percent=g["gpu_percent"]
    if probe_torch:
        try:
            import torch
            if torch.cuda.is_available():
                h.cuda_capability=tuple(map(int,torch.cuda.get_device_capability(0))); h.gpu_name=torch.cuda.get_device_name(0)
                h.vram_gb=round(torch.cuda.get_device_properties(0).total_memory/2**30,2)
        except Exception: pass
    return h

def training_profile(hardware):
    from config.device_profiles import recommend_for_hardware
    return recommend_for_hardware(hardware)["training"].copy()

def model_profile(hardware):
    from config.device_profiles import recommend_for_hardware
    return recommend_for_hardware(hardware)["runtime"].copy()
