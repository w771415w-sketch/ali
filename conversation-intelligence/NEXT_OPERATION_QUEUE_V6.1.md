# NEXT OPERATION QUEUE — V6.1 / Professional Runtime

## Completed in the current foundation pass
- P50 hardware-aware runtime policy and deterministic health gate.
- Verified control-plane architecture around the model.
- Requirements/contract/acceptance/clarification/conflict management.
- Project/task DAG, state persistence, checkpoints, recovery and rollback path.
- Memory, knowledge/RAG, document ingestion and provenance.
- Tool registry, security/permissions, safe workspace execution, Git controls.
- Reliability: budgets, retries, rate limits, circuit breaker, idempotency and cancellation.
- Model routing/fallback, artifact/lineage, observability/evaluation/release gates.
- Dataset validation/deduplication/split/leakage checks and controlled self-improvement.
- Project/code intelligence, multimodal capability detection, local gateway.
- P50-aware training preflight and persistent training job management.
- CI and Windows/P50 validation tooling.
- Local verification: 29/29 tests pass, compileall pass, control-plane self-test pass, P50 deterministic gate pass.

## Next native integration gates
1. Synchronize remaining historical source-export files into a real native Windows file tree where the source format permits.
2. Wire the professional control plane into the actual Desktop/Electron/Python request path.
3. Execute the native Windows/P50 gate and capture hardware telemetry.
4. Validate real model loading/inference, GGUF/llama.cpp runtime and model registry promotion.
5. Validate real SFT/LoRA training, checkpointing and resume under the P50 policy.
6. Validate real filesystem/Git project workflows end-to-end.
7. Build Golden/Regression/Arabic/Tool/Agent/Safety/Real-World long-horizon acceptance suites.
8. Add optional document/vision/speech dependencies only where the P50 resource budget supports them.
9. Keep Hermes inactive until separately authorized and natively verified.

The queue does not mark a feature complete from documentation alone.