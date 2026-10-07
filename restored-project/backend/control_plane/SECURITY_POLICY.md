# ALI Control Plane Security Policy

## Trust boundaries

1. User/model output is untrusted input.
2. External documents and web results are untrusted content.
3. Tools are capability endpoints and require declared permissions.
4. Filesystem writes are confined to the project workspace.
5. Destructive or externally visible actions require explicit approval.
6. Secrets are not part of model/dataset content and must be redacted from logs.
7. Network egress should be allowlisted when a task requires it.

## Required controls

- path containment and zip-slip protection
- dangerous command screening
- role-based authorization
- tenant-scoped state
- approval gates for high-impact actions
- idempotency for retried operations
- time/tool/task/token budgets
- rate limiting and circuit breaking
- timeouts and cancellation
- pre-change snapshots/checkpoints
- postcondition verification
- artifact hashes and provenance
- regression and quality gates before release

## Self-improvement

Production is never modified solely from an observed failure. The controlled path is:

failure -> root cause -> lesson/candidate -> evaluation -> regression -> approval -> new version
