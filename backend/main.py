# -*- coding: utf-8 -*-
from __future__ import annotations
import json
from runtime.hardware import detect
from runtime.device_policy import choose_policy
from runtime.resources import ResourceManager
def main():
 h=detect(); p=choose_policy(h); a=ResourceManager(h).admission(p); print(json.dumps({"hardware":h.to_dict(),"policy":p,"admission":a},ensure_ascii=False,indent=2)); return 0 if a["allowed"] else 2
if __name__=="__main__": raise SystemExit(main())
