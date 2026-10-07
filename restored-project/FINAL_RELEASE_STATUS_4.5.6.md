# ALI Studio Pro 4.5.6 — Final Release Status

## What this release fixes
- Grounded local Q&A router answers high-confidence local/project questions before the tiny bootstrap model.
- Full P50 user hardware profile is bundled into local knowledge.
- llama.cpp bridge now passes `-ngl` and returns the actual completion text instead of the raw response object.
- llama-server uses a free localhost port instead of a fixed port to prevent collisions.
- Chat streaming supports true delta parsing when llama-server is available.
- Version metadata is coherent at 4.5.6.
- Existing continuous-learning pipeline, RAG, Memory, session history and training progress remain intact.

## Target hardware policy
Lenovo ThinkPad P50, i7-6820HQ, 32 GB RAM, Quadro M1000M 2 GB GDDR5.

Auto mode never assumes all 2 GB are free. CUDA training is attempted only after a real self-test; otherwise CPU is used. GGUF inference uses adaptive layer offload when a compatible llama.cpp CUDA build is installed.

## Local QA strategy
The small bootstrap model is retained as a trainable/diagnostic model. For project facts and curated operational questions, ALI first uses deterministic local Q&A and RAG. This gives reliable answers without pretending the 30 MB bootstrap model is a strong general-purpose model.

## Training lifecycle
`Import → Validate → Dedup → RAG → Dataset → LoRA → Evaluate → Candidate → Promote → Runtime Reload → vN+1`

## Verification in this environment
- Python compile: PASS
- pytest: 167 passed, 34 skipped, 2 warnings
- Release audit: PASS
- Arabic P50 RAG/Q&A smoke: PASS

## Windows-only release gates
The following must be run on the target Windows machine:
- Embedded Python 3.11.9 preparation
- Node/npm installation and `npm install`
- Vite/Electron production build
- native `node-pty` rebuild / ConPTY
- C#/.NET 8 publish
- real NVIDIA CUDA kernel test on Quadro M1000M
- compatible llama.cpp Windows CUDA binary

The package contains scripts for these gates and does not claim they were executed on Linux.
