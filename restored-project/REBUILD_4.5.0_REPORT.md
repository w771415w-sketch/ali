# ALI Studio Pro 4.5.0 — Professional Rebuild

## What was corrected
- Fixed a frontend syntax error in `desktop/src/App.jsx` (`const result = const result`).
- Fixed streaming chat so it preserves conversation ID and compute mode.
- Added `/api/memory/list` compatibility alias.
- Improved NVIDIA SMI polling with cache and a hard timeout to reduce blocking.
- Added explicit per-process CUDA memory budgeting.
- Added adaptive GGUF offload policy for 2 GB-class GPUs.
- Added target ThinkPad P50 profile and knowledge documents.
- Added 34 curated, non-duplicated project/hardware Q&A training examples.
- Added optional llama.cpp bridge and Qwen model manifest.
- Strengthened Launcher validation for missing Embedded Python.
- Added Electron rebuild step for node-pty native module.
- Added grounded RAG fallback when the tiny bootstrap model emits unusable text.

## Important truth about model quality
The previous report recorded 0/8 model-only answers for the 30 MB bootstrap model. This rebuild does not pretend that LoRA can turn a tiny custom bootstrap into a strong general assistant. The production path therefore separates:
- training base + LoRA/merged HF artifacts
- inference GGUF + llama.cpp

## Hardware fit
The target profile is 32 GB RAM + Quadro M1000M 2 GB. Auto mode uses only free VRAM with headroom and can fall back to CPU.

## Verification done in this environment
- Python source compilation: required before release.
- Backend tests and deterministic import/route tests: run by the build verification script.
- Electron production build, C# publish, node-pty/ConPTY and CUDA on Windows: must be run on the Windows release host; this Linux environment cannot truthfully certify those binaries.
