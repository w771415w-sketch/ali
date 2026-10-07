# ALI Studio Pro 4.4.0

## Major repairs
- Robust Markdown conversation import, including bold/escaped headings and role markers.
- Persistent chat sessions with new conversation, history, rename, delete and clear support.
- Session-safe streaming/fallback chat persistence.
- Adaptive compute policy with Auto/CPU/GPU modes based on CUDA self-test and free VRAM.
- Telemetry exposes GPU utilization, used/free VRAM, step/sample counters, ETA, tokens/sec, loss and LR.
- Auto mode falls back safely when CUDA or free VRAM is insufficient; forced GPU mode reports a clear error instead of silently using CPU.
- Unreviewed model answers are no longer inserted into high-quality learned conversation memory automatically.

## Verification
- Escaped Markdown training bundle: 120/120 samples parsed.
- Session persistence round-trip: PASS.
- Adaptive GPU policy tests: PASS.
- Full Python test suite and Electron static checks are run in the release verification step.

## Windows GPU
The Windows setup detects legacy NVIDIA hardware and installs the dedicated legacy CUDA requirement file; Auto runtime selection still performs a real CUDA kernel self-test before selecting GPU.
