# ALI AI Project Contract

1. Data is not weights.
2. A checkpoint is not a promoted model.
3. A GGUF file is valid only after conversion and validation.
4. Internet material is knowledge first; it becomes training data only after provenance, cleaning, deduplication and review.
5. Tool execution always passes through PermissionManager and AuditLog.
6. Candidate models pass evaluation before promotion.
7. Recovery uses checkpoints; destructive actions are never the default.
8. Device policy chooses safe defaults; explicit advanced overrides remain possible.
9. Scale profiles describe architecture targets; they do not claim a laptop can train every target.
10. Every training run should record dataset identity, config, code version, metrics and artifact hashes.
11. Every complex request may be represented as KCA state: intent, goal, candidate actions, observation, verification and recovery.
12. The 100-function KCA registry is metadata/capability architecture, not an assertion that every function is an external tool.
13. Structured KCA traces may be trained only from approved/redacted records; private reasoning text is never exported.


11. Autonomous learning consumes only approved, deduplicated high-quality samples and never promotes a candidate without evaluation and regression gates.
12. Failed autonomous training never advances the trained-data cursor; failed runs remain retryable.
