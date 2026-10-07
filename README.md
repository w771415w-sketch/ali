# ALI Studio Pro — Design4

Current project source export: ALI Studio Pro Design4 4.6.0.

## Repository layout
- source-export/part-001.md … source-export/part-085.md: ordered slices of the full source export.
- SOURCE_MANIFEST.json: source metadata and part ordering.
- scripts/reassemble_source.py: local reassembly helper.
- scripts/extract_project.py: restores the 588-file text source tree locally.

Hermes integration is intentionally inactive in this release.

## Conversation Intelligence V6.1
The repository retains the V6/V6.1 conversation layer with structured dialogue state, intent taxonomy, deterministic scenario generation, Arabic/noisy/mixed-language handling, memory boundaries, tool planning and measurable verification.

## Professional Control Plane
The executable control plane now surrounds the model with:
requirements/contracts -> memory/RAG -> project state -> dependency-aware planning -> policy/approval -> tools/files/Git -> verification/evaluation -> recovery/checkpoints -> delivery -> lineage/observability/governance.

The package at backend/control_plane includes requirements extraction, acceptance criteria, durable SQLite state, memory validation/consolidation, document ingestion, lexical/hybrid retrieval with provenance, knowledge graph, tools, workspace-safe execution, command safety, Git checkpoints/rollback, recovery, reliability controls, scheduling, model routing/fallback, artifact/lineage tracking, governance/RBAC/network policy, project/code intelligence, dataset controls, controlled self-improvement, model/GGUF capability discovery, multimodal capability detection, local loopback gateway, training preflight, CI and native P50 validation tooling.

## Validation
Local reconstructed working tree:
- compileall: PASS
- backend tests: 29/29 PASS
- control-plane self-test: PASS
- main.py --self-test: PASS
- main.py --target-p50: PASS
- main.py --professional-health: PASS

Useful commands:
- PYTHONPATH=backend python backend/main.py --self-test
- PYTHONPATH=backend python backend/main.py --target-p50
- PYTHONPATH=backend python backend/main.py --professional-health

## Hardware policy
The Lenovo ThinkPad P50 profile remains CPU-first for heavy training: maximum six training threads, one heavy local job, AC/power/thermal/RAM admission, no GPU training target for the 2 GB Quadro, and optional GPU inference offload.

## Native completion boundary
The repository does not claim that the historical 588-file text export has become a fully native Windows production application merely from these additions. Real Electron/node-pty, real model weights and GGUF/llama.cpp inference, real SFT/LoRA checkpoint resume, complete UI-driven project build/test/debug/rollback, multimodal execution and distributed production HA/DR remain gates until exercised in the real target environment.
