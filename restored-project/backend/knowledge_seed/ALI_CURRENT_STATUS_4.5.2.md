# ALI Studio Pro 4.5.2 — Current Authoritative Status

This document overrides historical claims in earlier audit reports when they conflict. It describes the intended and tested state of the 4.5.2 rebuild.

## Target machine
Lenovo ThinkPad P50, Intel i7-6820HQ, 32 GB RAM, NVIDIA Quadro M1000M 2 GB GDDR5 (Maxwell), Windows 11 Pro x64.

## Runtime architecture
C#/.NET 8 launcher → Electron 40.10.2 → React 19 → localhost Python 3.11.9 backend. Terminal uses node-pty/ConPTY on Windows.

## AI architecture
The bootstrap ALI model is retained as a small, trainable diagnostic/base artifact. For stronger local chat, the release provides a setup path for Qwen2.5-0.5B-Instruct Q4_K_M through llama.cpp. RAG and Memory remain separate from learned weights.

## Continuous learning
Dropped Markdown/JSON/JSONL/text/document sources are validated, de-duplicated, indexed into RAG, and eligible chat pairs are used for incremental LoRA training. Each generation is versioned (v1, v2, v3, ...). Candidate models are evaluated before promotion; the previous active generation remains available for rollback.

## GPU/VRAM policy
Auto mode uses a real CUDA kernel self-test plus current free VRAM. A 2 GB GPU is never assumed to be completely free. llama.cpp inference uses adaptive layer offload; training uses conservative batch/sequence/gradient-accumulation settings and falls back to CPU in Auto mode if CUDA or memory allocation is not safe.

## Known environment limitation
The current build container is Linux, so Windows-native Electron production build, .NET publish, ConPTY, and real Maxwell CUDA execution cannot be marked as executed here. Windows scripts are included to perform those final native gates.
