# -*- coding: utf-8 -*-
"""Model-size registry and hardware-neutral training estimates."""
from __future__ import annotations
from dataclasses import dataclass, asdict
from typing import Dict, Any

@dataclass(frozen=True)
class ScaleProfile:
    name: str
    hidden_size: int
    intermediate_size: int
    layers: int
    heads: int
    vocab_size: int
    context: int
    target_params: int
    note: str

PROFILES = {
    "micro": ScaleProfile("micro", 192, 768, 4, 6, 4096, 256, 1_000_000, "P50 smoke tests and tokenizer/bootstrap validation"),
    "small": ScaleProfile("small", 256, 1024, 6, 8, 8192, 384, 10_000_000, "P50 local research model"),
    "medium": ScaleProfile("medium", 512, 2048, 12, 8, 16000, 1024, 100_000_000, "strong workstation / server"),
    "large": ScaleProfile("large", 1024, 4096, 24, 16, 32000, 2048, 500_000_000, "multi-GPU target"),
    "xlarge": ScaleProfile("xlarge", 2048, 8192, 32, 32, 64000, 4096, 2_000_000_000, "cluster-scale research target"),
}

def get(name: str) -> ScaleProfile:
    if name not in PROFILES:
        raise KeyError(f"unknown scale profile: {name}")
    return PROFILES[name]

def estimated_param_count(p: ScaleProfile) -> int:
    h, i, l, v = p.hidden_size, p.intermediate_size, p.layers, p.vocab_size
    return int(v*h*2 + l*(4*h*h + 3*h*i + 4*h))

def estimate_memory_gb(params: int, dtype_bytes: float = 4.0, optimizer_multiplier: float = 8.0,
                       gradients: bool = True, activation_factor: float = 1.5) -> float:
    """Conservative planning estimate; not a profiler measurement."""
    base = params * (dtype_bytes + (dtype_bytes if gradients else 0) + optimizer_multiplier) / (1024**3)
    return base * activation_factor

def build_training_plan(name: str, hardware: Any) -> Dict[str, Any]:
    p = get(name)
    params = estimated_param_count(p)
    ram = float(getattr(hardware, "ram_gb", 0) or 0)
    vram = float(getattr(hardware, "vram_gb", 0) or 0)
    cpu_threads = int(getattr(hardware, "cpu_cores", 1) or 1)
    legacy = bool(getattr(hardware, "cuda_capability", None) and tuple(hardware.cuda_capability) < (6, 0))
    fits_ram = estimate_memory_gb(params) <= max(0.5, ram * 0.55)
    fits_vram = estimate_memory_gb(params, dtype_bytes=2.0) <= max(0.5, vram * 0.65) if vram else False
    return {
        "profile": asdict(p),
        "estimated_parameters": params,
        "estimated_training_memory_gb": round(estimate_memory_gb(params), 2),
        "hardware_ram_gb": ram,
        "hardware_vram_gb": vram,
        "fits_2gb_vram": bool(fits_vram and vram <= 2.1),
        "fits_ram_estimate": fits_ram,
        "strategy": "CPU-first" if vram < 3 or legacy else "GPU/CPU adaptive",
        "recommended_cpu_threads": min(6, max(1, cpu_threads - 2)),
        "recommendation": "usable-bootstrap" if fits_ram else "requires-more-memory-or-smaller-profile",
    }
