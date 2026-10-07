# ALI AI 2.5.0 — Unified KCA / Local AI Engineering Platform

ALI AI 2.5.0 is the unified release built on the existing ALI AI 2.0 foundations and the AI-KCA 3.0 operational architecture. The desktop UI, runtime, training, tokenizer, memory/RAG, tools and artifact registry remain separate layers so they can evolve without rewriting the application shell.

## What is real

- PyTorch decoder-only language model with from-scratch and continuation training paths.
- Versioned SentencePiece tokenizer lifecycle with corpus hashing and deterministic reuse.
- Full-parameter training, dependency-light LoRA, checkpoints and safe resume.
- Progressive training stages: `base → sft → lora → merged`.
- Evaluation plus candidate/promotion gate; inactive candidates never replace the active model in place.
- Dataset harvesting, normalization, deduplication, provenance and train/validation/test separation.
- Persistent memory and local knowledge/RAG kept separate from learned weights.
- Permissioned tools with audit logging and bounded tool-calling.
- HF export and a real llama.cpp GGUF conversion/validation bridge.
- Professional three-pane desktop UI with local chat, streaming, project explorer, editor, terminal, jobs, models and device monitoring.
- Central weight/artifact import: `models/inbox → inspect → install → verify → registry`.
- Explicit artifact manifests with SHA-256, lineage, training metadata and evaluation metadata.
- CPU-first P50 operation with an explicit CUDA/DDP path for stronger systems.
- Autonomous incremental learning from approved, deduplicated conversations with candidate evaluation and promotion gating.
- Included small bootstrap and P50 datasets so the source bundle can train immediately after dependency installation.

## Important separation: data ≠ weights

A conversation JSONL file is training data. A tokenizer model is a tokenizer artifact. A checkpoint contains tensors. A LoRA adapter is a specialization artifact. A GGUF file is a deployment artifact. The system never treats arbitrary numeric JSON as a model.
