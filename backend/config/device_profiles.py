# -*- coding: utf-8 -*-
"""Hardware-aware ALI profiles for the ThinkPad P50 and adaptive hosts."""
from __future__ import annotations
from copy import deepcopy
from typing import Any

P50_PROFILE = {
    "id": "thinkpad-p50-32gb-2gb",
    "label": "Lenovo ThinkPad P50 / 32 GB / Quadro M1000M 2 GB",
    "cpu": {"threads": 8, "physical_cores": 4, "leave_free_threads": 2, "max_training_threads": 6,
            "torch_threads": 6, "torch_interop_threads": 1},
    "gpu": {"name": "NVIDIA Quadro M1000M", "vram_gb": 2, "cuda_capability": [5, 0],
            "training": "cpu-first", "inference": "optional-offload"},
    "training": {"device": "cpu", "scale": "small", "bootstrap_scale": "micro",
                 "batch_size": 1, "grad_accum": 16, "seq_len": 256, "context": 320,
                 "max_new_tokens": 160, "amp": False, "gradient_checkpointing": True,
                 "learning_rate": 3e-4, "weight_decay": 0.05, "warmup_steps": 20,
                 "save_every": 50, "eval_every": 50, "max_steps_bootstrap": 50,
                 "max_concurrent_jobs": 1, "require_ac_power": True,
                 "min_available_ram_gb": 4.0, "max_cpu_threads": 6},
    "runtime": {"recommended_context": 320, "max_context": 384,
                "recommended_max_new_tokens": 160, "max_new_tokens": 192,
                "temperature": 0.65, "max_concurrent_inference": 1},
    "power": {"battery_guard_percent": 45, "battery_hard_stop_percent": 25,
              "thermal_guard_c": 80.0, "thermal_hard_stop_c": 88.0},
    "storage": {"fast_root": "D:/ALI-AI", "archive_root": "F:/ALI-AI-Archive",
                "avoid_system_drive_for_checkpoints": True},
}

def recommend_for_hardware(hardware: Any) -> dict:
    ram=float(getattr(hardware,"ram_gb",0) or 0)
    vram=float(getattr(hardware,"vram_gb",0) or 0)
    threads=int(getattr(hardware,"cpu_threads",getattr(hardware,"cpu_cores",0)) or 0)
    gpu=str(getattr(hardware,"gpu_name","") or "").lower()
    p50=ram>=24 and threads>=6 and vram<3 and ("quadro" in gpu or "m1000m" in gpu or not gpu)
    out=deepcopy(P50_PROFILE)
    if p50: out["detected_match"]=True; return out
    out["id"]="adaptive"; out["label"]=f"Adaptive / {ram:.1f} GB RAM / {vram:.1f} GB VRAM / {threads} threads"; out["detected_match"]=False
    if ram<16: out["training"].update(scale="micro",seq_len=192,context=256,grad_accum=8)
    elif ram<24: out["training"].update(scale="micro",seq_len=224,context=288,grad_accum=12)
    return out
