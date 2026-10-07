# ALI Professional Control Plane Architecture

The control plane is intentionally outside the LLM weights.

USER
 -> Conversation Understanding / V6 Router
 -> Requirements + Task Contract
 -> Memory / Knowledge / Project State
 -> Planner + Dependency Graph
 -> Policy / Permissions / Approval
 -> Tools / Files / Git / Runtime
 -> Verification / Acceptance / Evaluation
 -> Recovery / Checkpoint / Rollback
 -> Delivery
 -> Lineage / Artifacts / Observability / Governance

## Component boundaries

- Model: language, reasoning, coding and tool-intent generation.
- Memory: durable user/project/task facts; validated before reuse.
- Knowledge/RAG: external mutable knowledge with source provenance.
- Planner: decomposes work, resolves dependencies and orders tasks.
- Executor: performs concrete approved operations.
- Verifier: checks actual postconditions, not model claims.
- Recovery: classifies failures, preserves checkpoints and rolls back safe snapshots.
- Evaluation/Release: blocks promotion when quality/regression gates fail.
- Governance/Security: scopes paths, tenants, network, permissions and sensitive data.
- Registries/Lineage: track model, dataset, tool, agent and artifact versions.

## P50 resource policy

CPU-first training; maximum six training threads; two CPU threads reserved; one heavy local training job; AC/power/thermal/RAM admission; Quadro M1000M 2 GB is not a training target; optional GPU inference offload only.

## Completion rule

A plan is not a delivery. Delivery requires applied changes plus machine-checkable verification/acceptance evidence.
