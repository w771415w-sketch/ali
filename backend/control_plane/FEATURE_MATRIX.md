# ALI Professional Control Plane — Feature Matrix

| Area | Capability | Module |
|---|---|---|
| Understanding | requirements, ambiguity, conflicts | requirements.py |
| Contracts | requirements, assumptions, acceptance | schemas.py, requirements.py |
| Planning | priorities, dependency DAG, layers | planner.py |
| State | project state, events, failures | store.py |
| Memory | scoped validation/consolidation | memory.py |
| RAG | ingestion, chunks, lexical retrieval, citations | knowledge.py |
| Knowledge graph | entities, relations, observations, conflicts | knowledge_graph.py |
| Tools | registry, versions, permissions, risk, timeout | tools.py |
| Project execution | writes, patches, delete, snapshots | project_io.py, project_agent.py |
| Safety | command policy, approval, containment | policy.py, backend/security/* |
| Recovery | classification, failure memory, checkpoints | recovery.py |
| Reliability | budgets, retries, rate, circuit breaker, idempotency, cancellation | reliability.py |
| Scheduling | priority queue, bounded workers | scheduler.py |
| Model layer | routing/fallback | model_router.py |
| Artifacts | hashing/registry/lineage/provenance | artifacts.py, lineage.py, provenance.py |
| Governance | sensitive data, retention, RBAC, tenant, network | governance.py, security_ext.py |
| Observability | metrics/events | observability.py |
| Evaluation | golden/regression/adversarial/coding/Arabic/long-context/tool/agent/safety/real-world | evaluation.py |
| Release | quality gates, canary, promotion, rollback | release.py |
| Learning | validation, dedupe, split, leakage/quality | dataset.py |
| Self improvement | candidate -> evaluate -> regression -> approval | self_improvement.py |
| Environment | OS/tool/capability discovery | capabilities.py |

Completion requires an executable artifact plus a passing postcondition. Native Windows desktop/model/multimodal/production infrastructure remain explicit integration gates.