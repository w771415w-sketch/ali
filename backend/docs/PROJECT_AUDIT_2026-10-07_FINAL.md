# ALI Full Project Audit — 2026-10-07

## Scope

This audit covered the current GitHub `main` branch, the 85-part `source-export`, the reproducible restored source tree, the professional control plane, security/runtime layers, training/model lifecycle, Arabic language handling, diagnostics, and CI.

## Source integrity

- `source-export/`: 85 ordered Markdown parts.
- Source manifest states 588 source files.
- `restored-project/MANIFEST.json`: 588 restored source files plus the manifest itself.
- Restoration is reproducible with `scripts/extract_project.py`.
- Restoration CI now removes stale output, validates the exact 588-file count, compiles restored Python, and writes deterministic SHA-256 metadata.
- Historical source is kept under `restored-project/`; modern executable control-plane code remains under `backend/`.

## Implemented professional foundation

### Understanding and conversation
- Requirement extraction and structured task contracts.
- Missing requirement and contradiction detection.
- Arabic normalization and typo correction.
- Selectable Arabic response profiles: MSA, Saudi, Yemeni, Egyptian.
- Conversation correction metadata retained separately from the original user text.
- Tool/context/verification boundaries.
- V5/V6 conversation intelligence retained and covered by CI.

### Agent and project execution
- Dependency-aware planning and task state.
- Project state/events/checkpoints.
- Memory validation/consolidation.
- Local RAG ingestion/retrieval/provenance.
- Knowledge graph.
- Tool registry and permission metadata.
- Workspace containment, patch preconditions, snapshots, restore.
- Command safety and approval gates.
- Acceptance checks and postcondition verification.
- Failure classification and recovery.
- Git checkpoint/rollback.
- Budgets, retry, rate limiting, circuit breaker, idempotency, cancellation and scheduling.
- Project/code/AST intelligence.
- Local JSON gateway.

### Diagnostics
- File type detection.
- Python/JSON syntax validation.
- ZIP/TAR archive inspection.
- Zip Slip / path traversal protection.
- Archive size/file-count/compression-ratio limits.
- Safe extraction only after approval.
- Project-wide syntax and JSON checks.
- Root-cause classification with evidence and suggested next checks.

### Training and model lifecycle
- P50-aware training options.
- Default continued training path: `lora_continue_cpu`.
- Continued SFT CPU path.
- Micro full fine-tune path only for very small models.
- GPU QLoRA disabled on the P50 profile by default.
- Cumulative replay dataset strategy.
- Checkpoint/adapter retention and previous-production retention.
- GGUF is treated as a runtime/export artifact, never as the training source.
- GGUF conversion/quantization is approval-gated and performs format verification.
- Artifact hashes, lineage and provenance.

## P50 policy

The current profile is CPU-first for heavy local training:
- maximum six training threads;
- two CPU threads reserved;
- one heavy local job;
- AC/power/thermal/RAM admission;
- 2 GB Quadro M1000M is not a training target;
- optional GPU inference offload only where policy permits.

## CI evidence

The latest main-branch certification commit is covered by successful:
- ALI Control Plane
- Conversation Intelligence V5
- Conversation Intelligence V6
- Rebuild ALI Source Tree

The Control Plane CI runs on Python 3.11 and 3.12 and includes compile, backend regression tests, control-plane self-test, and deterministic P50 admission.

## Improvements discovered and addressed during the audit

- Fixed source extraction so Markdown wrappers are not written into restored code.
- Preserved backward-compatible security/runtime APIs instead of breaking legacy consumers.
- Hardened read-only permission behavior.
- Hardened command/path safety.
- Fixed CI coverage so restored desktop source changes run through the control-plane gate.
- Corrected stale 682-file restored output to the current 588-file source count.
- Added explicit settings validation instead of trusting user-selected training methods blindly.
- Added controlled self-improvement: candidate -> evaluation -> regression -> approval.
- Added provenance/lineage instead of treating generated artifacts as untraceable.

## Explicit remaining native gates

These are intentionally not marked complete without execution on the physical target:
1. Native Windows desktop run on the ThinkPad P50.
2. Electron/node-pty and full UI-driven tool execution.
3. Real model-weight loading, tokenizer assets and GGUF/llama.cpp inference with the actual model artifact.
4. Real SFT/LoRA training and checkpoint resume on the P50.
5. Full real-project E2E cycle: requirements -> build -> tests -> failure -> repair -> retest -> delivery.
6. Real browser/database/package-manager integrations for supported project types.
7. Actual multimodal runtime paths where optional dependencies are not installed.
8. Production distributed HA/DR, remote worker scaling and multi-tenant infrastructure.

## Important training rule

Do not merge Binary/GGUF files by concatenating them. Continue training from a verified checkpoint/adapter, use cumulative replay when preserving earlier behavior matters, evaluate against regression/golden suites, then export a new GGUF and retain the previous production version until the new one is verified.

## Current status

The repository now has a tested professional control-plane foundation around the model, a reproducible 588-file restored source tree, P50-safe training/conversion settings, Arabic dialect/typo handling, diagnostics and CI gates. Native model/Windows/E2E production work remains an execution gate, not an undocumented assumption.
