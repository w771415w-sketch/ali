# -*- coding: utf-8 -*-
"""Concrete, reproducible device profiles for ALI AI deployments.

The ThinkPad P50 profile is deliberately conservative: the Quadro M1000M has
only 2 GB VRAM, so local training stays CPU-first while inference may use
optional GGUF/llama.cpp offload. Profiles are copied deeply before adaptation
so nested configuration cannot leak mutations between callers.
"""
from __future__ import annotations

from copy import deepcopy
from typing import Any, Dict

P50_PROFILE: Dict[str, Any] = {
    "id": "thinkpad-p50-32gb-2gb",
    "label": "Lenovo ThinkPad P50 / 32 GB / Quadro M1000M 2 GB",
    "cpu": {
        "threads": 8,
        "physical_cores": 4,
        "recommended_torch_threads": 6,
        "interop_threads": 1,
        "leave_free_threads": 2,
    },
    "ram_gb": 32,
    "gpu": {
        "name": "NVIDIA Quadro M1000M",
        "vram_gb": 2,
        "cuda_capability": [5, 0],
        "training": "disabled-by-default",
        "inference": "optional-offload",
    },
    "training": {
        "device": "cpu",
        "scale": "small",
        "bootstrap_scale": "micro",
        "batch_size": 1,
        "grad_accum": 16,
        "seq_len": 256,
        "context": 320,
        "max_new_tokens": 160,
        "amp": False,
        "gradient_checkpointing": True,
        "weight_decay": 0.05,
        "learning_rate": 0.0003,
        "warmup_steps": 20,
        "save_every": 50,
        "eval_every": 50,
        "max_steps_bootstrap": 50,
        "max_concurrent_jobs": 1,
        "require_ac_power": True,
        "min_available_ram_gb": 4.0,
        "max_cpu_threads": 6,
    },
    "runtime": {
        "recommended_context": 320,
        "max_context": 384,
        "recommended_max_new_tokens": 160,
        "max_new_tokens": 192,
        "temperature_default": 0.65,
        "max_concurrent_inference": 1,
        "min_available_ram_gb": 3.0,
    },
    "power": {
        "battery_guard_percent": 45,
        "battery_hard_stop_percent": 25,
        "thermal_guard_c": 80.0,
        "thermal_hard_stop_c": 88.0,
        "prefer_ac_for_training": True,
    },
    "storage": {
        "fast_root": "D:/ALI-AI",
        "archive_root": "F:/ALI-AI-Archive",
        "avoid_system_drive_for_checkpoints": True,
    },
    "rules": [
        "CPU-first training is the default for this 2 GB legacy GPU class.",
        "Use at most 6 logical CPU threads for training so Windows/UI retain headroom.",
        "Run one heavy local training job at a time.",
        "Use micro scale for smoke tests; use small scale only for real local runs.",
        "Prefer GGUF/llama.cpp for production inference when a compatible GGUF exists.",
        "Pause or refuse heavy training when battery, thermal, or free-RAM guards are violated.",
    ],
}


def _adaptive_training(base: Dict[str, Any], ram_gb: float) -> Dict[str, Any]:
    training = deepcopy(base["training"])
    if ram_gb < 16:
        training.update(scale="micro", seq_len=192, context=256, grad_accum=8)
    elif ram_gb < 24:
        training.update(scale="micro", seq_len=224, context=288, grad_accum=12)
    elif ram_gb < 32:
        training.update(scale="small", seq_len=256, context=320, grad_accum=16)
    return training


def recommend_for_hardware(hardware: Any) -> Dict[str, Any]:
    ram = float(getattr(hardware, "ram_gb", 0) or 0)
    vram = float(getattr(hardware, "vram_gb", 0) or 0)
    threads = int(getattr(hardware, "cpu_cores", 0) or 0)
    gpu_name = str(getattr(hardware, "gpu_name", "") or "").lower()

    profile = deepcopy(P50_PROFILE)
    p50_match = ram >= 24 and threads >= 6 and vram < 3 and (
        "m1000m" in gpu_name or "quadro" in gpu_name or not gpu_name
    )
    if p50_match:
        profile["detected_match"] = True
        return profile

    profile["id"] = "adaptive"
    profile["label"] = (
        f"Adaptive profile · {ram:.1f} GB RAM · "
        f"{vram:.1f} GB VRAM · {threads} logical threads"
    )
    profile["detected_match"] = False
    profile["training"] = _adaptive_training(profile, ram)
    if ram < 16:
        profile["runtime"].update(recommended_context=256, max_context=320,
                                  recommended_max_new_tokens=128, max_new_tokens=160)
    elif ram < 24:
        profile["runtime"].update(recommended_context=288, max_context=352,
                                  recommended_max_new_tokens=144, max_new_tokens=176)
    return profile
