# -*- coding: utf-8 -*-
from __future__ import annotations
import shutil, os

class ResourceManager:
    def __init__(self,hardware): self.hardware=hardware
    def snapshot(self):
        free_disk=shutil.disk_usage(os.getcwd()).free/2**30
        return {"cpu_percent":float(getattr(self.hardware,"cpu_percent",0) or 0),
                "ram_available_gb":round(float(getattr(self.hardware,"ram_available_gb",0) or 0),2),
                "ram_used_percent":float(getattr(self.hardware,"ram_used_percent",0) or 0),
                "gpu_percent":float(getattr(self.hardware,"gpu_percent",0) or 0),
                "temperature_c":float(getattr(self.hardware,"temperature_c",0) or 0),
                "battery_percent":float(getattr(self.hardware,"battery_percent",-1) or -1),
                "power_plugged":getattr(self.hardware,"power_plugged",None),
                "disk_free_gb":round(free_disk,2)}
    def admission(self,policy):
        s=self.snapshot(); reasons=[]
        if not policy.get("training_enabled",True): reasons.append(policy.get("runtime_mode","training disabled"))
        if s["ram_available_gb"] and s["ram_available_gb"]<policy.get("min_free_ram_gb",4.0): reasons.append("low available RAM")
        if s["power_plugged"] is False: reasons.append("AC power required")
        if s["temperature_c"]>=policy.get("thermal_guard_c",80.0): reasons.append("thermal guard")
        return {"allowed":not reasons,"reasons":reasons,"snapshot":s}
