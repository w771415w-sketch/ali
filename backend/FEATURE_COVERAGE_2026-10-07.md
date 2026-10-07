# Feature Coverage — 2026-10-07 Professional Pass

The requested architecture is retained as the target: the model supplies language/reasoning capabilities, while the control plane owns state, memory, RAG, tools, planning, execution, verification, recovery, governance and release control.

## Executable foundation now present

- Conversation understanding/state framing
- Multi-step request pipeline
- Task/requirement contract and acceptance criteria
- Missing-requirement and contradiction detection
- Dependency-aware planning/DAG
- Persistent project state/events/failures in SQLite/WAL
- Scoped memory with relevance/currentness/trust validation
- Document ingestion for common text/code/data formats plus optional PDF/DOCX/XLSX/PPTX parsers
- Local knowledge ingestion/chunking/provenance
- Lexical retrieval and optional hybrid embedding retrieval
- Knowledge graph entities/relations/observations/conflict handling
- Versioned tools, permissions, risk/timeout metadata and result envelopes
- Workspace containment, file preconditions, patch/delete, snapshots and zip-slip-safe restore
- Command safety and explicit approval
- Git status/diff/checkpoint/rollback
- Failure classification, failure memory and checkpoints
- Budgets, retries, rate limiting, circuit breakers, idempotency and cancellation
- Priority scheduling
- Model routing/fallback abstraction and GGUF/runtime discovery
- Artifact hashing, provenance and lineage
- Dataset validation, quality filtering, deduplication, split and leakage detection
- Evaluation categories including golden/regression/adversarial/coding/Arabic/long-context/tool/agent/safety/real-world
- Quality/release gates and controlled self-improvement
- RBAC, tenant scoping, network allowlist and sensitive-data governance
- Observability metrics/events
- Repository/AST/project intelligence
- Multimodal capability detection
- Local JSON gateway
- P50-aware training preflight and persistent job management
- CI workflow and Windows/P50 validation script

## Verification evidence

Local reconstructed tree: **29/29 backend tests passed**, compileall passed, control-plane self-test passed, canonical main self-test passed, deterministic P50 admission passed, professional health passed.

## Explicit pending native gates

- Native Windows end-to-end run on the physical ThinkPad P50
- Electron/node-pty desktop integration
- Actual model weights, GGUF/llama.cpp loading and inference
- Real SFT/LoRA training and checkpoint resume
- Complete UI-driven filesystem/Git workflows
- Full end-to-end real project build/test/debug/repair/retest/rollback
- Actual vision/speech/OCR/document runtime paths where optional dependencies are unavailable
- Production gateway/worker/object/vector serving and distributed HA/DR

No pending feature is marked complete from documentation alone.
