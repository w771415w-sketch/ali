# ALI Professional Control Plane — Feature Matrix

| Area | Capability | Module |
|---|---|---|
| Understanding | requirements, ambiguity, conflicts | requirements.py |
| Contracts | requirements, assumptions, acceptance | schemas.py, requirements.py |
| Planning | priorities, dependency DAG, layers | planner.py |
| State | project state, events, failures | store.py |
| Memory | scoped validation/consolidation | memory.py |
| RAG | ingestion, chunking, lexical/hybrid retrieval, citations | knowledge.py, retrieval.py |
| Documents | TXT/MD/code/JSON/CSV/XML/HTML + optional PDF/DOCX/XLSX/PPTX | document_ingestion.py |
| Knowledge graph | entities, relations, observations, temporal/source fields | knowledge_graph.py |
| Tools | registry, versions, permissions, risk, timeouts | tools.py |
| Project intelligence | repository inventory, Python AST symbols/imports, manifests/tests | code_intelligence.py, project_intelligence.py |
| Execution | safe writes, patches, delete, snapshots | project_io.py, project_agent.py |
| Verification | file/hash/text/JSON postconditions | verification_ext.py, acceptance.py |
| Command safety | approval, containment, hardened screening | policy.py, backend/security/* |
| Recovery | failure classes, failure memory, checkpoints | recovery.py |
| Reliability | budgets, retry, rate limit, circuit breaker, idempotency, cancellation | reliability.py |
| Scheduling | priority queue, bounded workers | scheduler.py |
| Model layer | routing/fallback | model_router.py |
| Model runtime | GGUF/llama executable discovery | model_runtime.py |
| Multimodal | vision/OCR/docs/speech capability detection | multimodal.py |
| Training | hardware-aware preflight and persistent jobs | training_bridge.py, backend/training/* |
| Artifacts | hashing, registry, lineage | artifacts.py, lineage.py |
| Provenance | origin, transformations, sources, license | provenance.py |
| Governance | sensitive data, retention | governance.py |
| Security | RBAC, tenant scope, network allowlist | security_ext.py |
| Observability | counters, measurements, events | observability.py |
| Evaluation | golden/regression/adversarial/coding/Arabic/long-context/tool/agent/safety/real-world | evaluation.py |
| Release | quality gates, canary, promotion, rollback | release.py |
| Learning | JSONL validation, quality filtering, dedup, split, leakage checks | dataset.py |
| Self-improvement | candidate -> evaluation -> regression -> approval | self_improvement.py |
| Gateway | localhost JSON health/prepare/execute surface | gateway.py |
| Transactions | prepare/commit/rollback wrapper | transaction.py |
| Capabilities | runtime/environment discovery | capabilities.py |

## P50 policy

CPU-first training, max six training threads, one heavy local job, AC/power/thermal/RAM admission, no GPU training on the 2 GB Quadro, optional GPU inference offload.

## Completion rule

A generated plan is not a successful project delivery. Delivery requires applied changes and passing verification/acceptance evidence. Native Windows desktop, real model/GGUF/llama.cpp, real SFT/LoRA resume, real multimodal execution and distributed production remain gates until exercised on target.
