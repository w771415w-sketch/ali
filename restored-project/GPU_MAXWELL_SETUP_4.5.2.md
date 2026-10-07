# ALI Studio Pro 4.5.5 — Quadro M1000M 2GB / GPU Setup

The P50 profile records a Quadro M1000M with 2GB VRAM and compute capability 5.0. ALI never assumes the full 2GB is free.

## Runtime policy
- Auto: probe CUDA with a real kernel and query current free VRAM.
- Inference: use llama.cpp GGUF with adaptive `n_gpu_layers` when enough VRAM is free.
- Training: use CUDA only when the real CUDA self-test succeeds; otherwise use CPU.
- Shared GPU: lower sequence length / increase gradient accumulation / lower offload layers as free VRAM drops.

## Thresholds used by the project
- >= 1.35GB free: full 24-layer Qwen GGUF offload / seq 256 training profile.
- >= 0.95GB free: half-layer GGUF offload / seq 192 profile.
- >= 0.65GB free: low-layer GGUF offload / seq 128 profile.
- < 0.65GB or unknown occupancy: CPU-safe fallback in Auto.

## Windows setup
1. Run `backend\RUN-GPU-DOCTOR.bat`.
2. Run `scripts\SETUP_QWEN_LOCAL.bat` to install Qwen GGUF + llama.cpp locally.
3. Run `scripts\VERIFY_ALL.bat`.
4. Select `Auto (Smart)` in the top bar.

## Important
The repository includes exact download/verification scripts, but this Linux build environment cannot download the 398MB Qwen GGUF or execute Windows CUDA/ConPTY tests. The Windows release host must run the setup scripts and final native verification.
