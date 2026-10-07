# ALI Acceptance Matrix

| Gate | Evidence required | Current status |
|---|---|---|
| Requirements | structured contract + missing/conflict detection | executable/local pass |
| Planning | dependency graph + cycle detection | executable/local pass |
| State | persisted SQLite project state/events | executable/local pass |
| Memory | scoped validation/retrieval | executable/local pass |
| Knowledge | ingestion/chunking/retrieval/provenance | executable/local pass |\n| Project intelligence | repository/AST/manifests/tests analysis | executable/local pass |\n| Document ingestion | common text formats plus optional office/PDF parsers | executable/local pass |
| Tools | registry/version/permission/result envelope | executable/local pass |
| Safe execution | workspace + approval + command policy | executable/local pass |
| Recovery | failure classification + checkpoints + rollback path | executable/local pass |
| Reliability | budget/retry/rate/circuit/idempotency/cancel | executable/local pass |
| Model routing | route/fallback abstraction | executable/local pass |
| Multi-agent | roles/handoff/loop control | executable/local pass |
| Evaluation | categorized executable cases | executable/local pass |
| Release | quality gate + approval + rollback | executable/local pass |
| Learning | dataset validation/dedup/split/leakage | executable/local pass |
| Governance | redaction/retention/RBAC/network/tenant | executable/local pass |
| Observability | metrics/events | executable/local pass |\n| Model runtime | GGUF runtime discovery | executable/local pass |\n| Multimodal capability | dependency/capability detection | executable/local pass |\n| Local gateway | health/prepare/execute JSON surface | executable/local pass |
| Native Windows | actual target P50 run | pending on physical P50 |
| Electron/node-pty | real desktop integration | pending |
| Real model/GGUF | real model weights/inference | pending |
| Real SFT/LoRA | real training + resume | pending |
| Full E2E project delivery | real user project built/tested/fixed/retested | pending |
| Multimodal | audio/vision/doc pipeline | pending |
| Production infrastructure | gateway/worker/queue/HA/DR | pending |

Pending rows are deliberately not marked complete from documentation alone.


## Final audit marker — 2026-10-07

The repository cleanup removed generated Python bytecode and added persistent ignore rules. This marker intentionally triggers the Control Plane CI on the current `main` tree after cleanup.


## Final verified state — 2026-10-07

The latest main tree is generated from the source export without Python bytecode. The final local verification recorded 31/31 modern backend tests and 8/8 targeted historical integration tests passed, with four explicit artifact-related skips. GitHub CI passed Control Plane, Conversation Intelligence V5, Conversation Intelligence V6, and source restoration on the preceding source commit; this commit exists to re-run those gates against the final main tree.
