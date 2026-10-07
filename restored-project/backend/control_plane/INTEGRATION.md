# Control Plane Integration

The control plane composes:

- requirements + task contract + acceptance criteria
- project/task DAG with priorities, dependencies, checkpoints and resume records
- SQLite durable state/events/failures/decisions/artifacts
- scoped memory with relevance/currentness/trust validation
- local knowledge ingestion/chunking/retrieval/provenance
- tool registry with versions, permissions, risk and timeout metadata
- workspace-safe file operations, preconditions, diff and snapshots
- command safety and approval boundary
- Git status/diff/checkpoint/rollback
- failure classification and recovery/checkpoints
- model routing/fallback and environment capability inspection
- multi-agent role registry and supervised handoffs
- dataset validation/deduplication/splitting/leakage checks
- artifact hashes, provenance and lineage
- metrics/events, evaluation categories, quality/release gates
- budgets, rate limits, circuit breakers, retry, idempotency and cancellation
- RBAC, tenant scoping, network allowlist and sensitive-data governance

The model remains a replaceable intelligence component rather than the source of truth for execution state.