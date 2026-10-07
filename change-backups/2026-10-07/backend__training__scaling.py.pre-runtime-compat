# -*- coding: utf-8 -*-
from __future__ import annotations
from copy import deepcopy
PROFILES={"micro":{"seq_len":192,"batch_size":1,"grad_accum":8},"small":{"seq_len":256,"batch_size":1,"grad_accum":16}}
def build_training_plan(hardware,requested_scale="small",steps=0):
    from config.device_profiles import recommend_for_hardware
    profile=deepcopy(recommend_for_hardware(hardware)); t=profile["training"]
    scale=requested_scale if requested_scale in PROFILES else t["scale"]; t.update(PROFILES[scale]); t["scale"]=scale; t["requested_steps"]=int(steps or 0)
    return {"profile_id":profile["id"],"hardware":profile["label"],"training":t}
