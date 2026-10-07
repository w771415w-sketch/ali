# ALI AI 2.5.0 — Unified KCA / P50

This release turns the existing 1.1.0 foundations into one coherent control plane for local AI development.

## Major changes

- Reworked the desktop UI into a professional dark three-pane command center with local chat, persistent sessions, streaming, project explorer, editor, terminal, jobs, models and hardware state.
- Added a versioned tokenizer lifecycle with corpus hashing and deterministic reuse.
- Added one progressive `TrainingPipeline` for base training, conversation SFT and LoRA continuation without creating a separate training application.
- LoRA now produces both a portable adapter artifact and a merged HF model candidate for the existing runtime.
- Added immutable artifact manifests with SHA-256 hashes, lineage, training/evaluation metadata and atomic installation.
- Added safe weight import into dedicated `models/base`, `models/adapters`, `models/merged` and `models/gguf` locations.
- Added CLI parity for training and weight management.
- Unified structured tool-call parsing and bounded agent-loop execution.
- Kept CPU-first P50 policy while exposing an explicit CUDA/DDP control path for stronger systems.
- Fixed project/version inconsistencies and the missing `ali_agent.py.legacy` compatibility artifact.
- Added real autonomous incremental self-learning with dataset identity tracking, SFT/LoRA candidate training, regression checks and promotion gating.
- Added bootstrap and P50 training datasets to make the source bundle runnable without relying on missing external seed files.
- Continuation SFT/LoRA now reuses the base tokenizer artifact to prevent vocabulary/embedding mismatches.

## Verification

The source bundle was extracted and syntax-checked before packaging. The regression suite was rerun after the 2.0 changes; see the generated verification report in the final MD bundle.

## Self-learning verification

A real one-step autonomous cycle was executed during release verification. It produced a LoRA/merged candidate, ran the complete regression suite, and kept the candidate inactive because the measured validation improvement did not meet the promotion threshold.
