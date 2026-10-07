# -*- coding: utf-8 -*-
"""ALI runtime entrypoint: hardware health plus canonical control-plane self-test."""
from __future__ import annotations
import argparse, json
from runtime.hardware import HardwareInfo, detect
from runtime.device_policy import choose_policy
from runtime.resources import ResourceManager

def target_p50():
    return HardwareInfo(
        device_name="Lenovo ThinkPad P50", model="20EQS2L900",
        cpu_model="Intel Core i7-6820HQ", cpu_threads=8, physical_cores=4,
        ram_gb=32, ram_available_gb=21.32, gpu_name="NVIDIA Quadro M1000M",
        vram_gb=2, cpu_percent=0, temperature_c=41.05,
        battery_percent=80, power_plugged=True,
    )

def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--target-p50", action="store_true")
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--professional-health", action="store_true")
    args = ap.parse_args(argv)

    if args.self_test:
        from control_plane.self_test import run
        result = run()
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0 if result.get("checks_passed") else 3

    if args.professional_health:
        from control_plane.runtime_facade import ProfessionalRuntime
        rt = ProfessionalRuntime("runtime-state")
        try:
            print(json.dumps(rt.health(), ensure_ascii=False, indent=2))
        finally:
            rt.close()
        return 0

    h = target_p50() if args.target_p50 else detect()
    policy = choose_policy(h)
    admission = ResourceManager(h).admission(policy)
    print(json.dumps({"hardware": h.to_dict(), "policy": policy, "admission": admission},
                     ensure_ascii=False, indent=2))
    return 0 if admission["allowed"] else 2

if __name__ == "__main__":
    raise SystemExit(main())
