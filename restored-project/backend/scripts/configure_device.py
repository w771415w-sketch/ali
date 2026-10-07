# -*- coding: utf-8 -*-
"""Create a local, non-secret hardware override and print the recommended profile."""
from __future__ import annotations
from pathlib import Path
import json
from runtime.hardware import detect, training_profile, model_profile
from runtime.device_policy import choose_policy

ROOT = Path(__file__).resolve().parent.parent
PROFILE = ROOT / 'config' / 'hardware_profile.json'

def main() -> None:
    h = detect()
    if not PROFILE.exists():
        PROFILE.write_text(json.dumps({
            'label': 'Auto-detected device',
            'cpu_threads': h.cpu_cores,
            'physical_cores': h.physical_cores,
            'ram_gb': h.ram_gb,
            'gpu_name': h.gpu_name,
            'vram_gb': h.vram_gb,
            'cuda_capability': list(h.cuda_capability) if h.cuda_capability else None,
        }, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps({'hardware':h.to_dict(),'policy':choose_policy(h),'training':training_profile(h),'model':model_profile(h)},ensure_ascii=False,indent=2))

if __name__ == '__main__': main()
