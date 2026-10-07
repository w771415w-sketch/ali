from __future__ import annotations
from runtime.hardware import detect
from runtime.device_policy import choose_policy
from runtime.resources import ResourceManager
class HardwareBridge:
    def snapshot(self):
        h=detect(); p=choose_policy(h); a=ResourceManager(h).admission(p); return {"hardware":h.to_dict(),"policy":p,"admission":a}
