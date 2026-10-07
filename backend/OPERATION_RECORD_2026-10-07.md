# ALI Operation Record — 2026-10-07

## Scope reviewed
The complete feature-request document was read through layer 160 and compared with the current repository architecture. The operation focused on turning the most safety- and reliability-critical foundations into executable code for the Lenovo ThinkPad P50 target.

## Backups created before modification
- change-backups/2026-10-07/source-export-part-054-pre-hardware-security.md
- change-backups/2026-10-07/source-export-part-055-pre-hardware-security.md
- change-backups/2026-10-07/source-export-part-062-pre-hardware-security.md
- change-backups/2026-10-07/device_profiles.py.pre-hardware-hardening
- change-backups/2026-10-07/hardware_profile.json.pre-hardware-hardening.redacted
- change-backups/2026-10-07/conversation-intelligence__v6_router.py.pre-p50
- change-backups/2026-10-07/conversation-intelligence__training_record_schema_v6.json.pre-p50
- change-backups/2026-10-07/conversation-intelligence__response_policy_v6.json.pre-p50
- change-backups/2026-10-07/conversation-intelligence__NEXT_OPERATION_QUEUE_V6.1.md.pre-p50

## Implemented executable components
1. Privacy-safe ThinkPad P50 hardware profile.
2. Hardware detection with psutil/nvidia-smi/optional torch probes.
3. P50 CPU-first training policy for 4C/8T, 32 GB RAM and Quadro M1000M 2 GB.
4. Maximum 6 training threads, 2 threads reserved for Windows/UI.
5. Maximum one heavy local training job at a time.
6. AC-power requirement for heavy training.
7. Battery guard at 45% and hard stop at 25% when not on AC.
8. Thermal guard at 80 C and hard stop at 88 C.
9. Minimum free-RAM guard of 4 GB.
10. Workspace containment and sensitive-path blocking.
11. Dangerous command screening.
12. Permission semantics where read-only is a hard ceiling and default mode asks for approval.
13. Explicit Agent state machine with checkpoint history.
14. Postcondition verification primitives.
15. Persistent heavy-job scheduler.
16. Audit redaction for credentials/tokens.
17. Deterministic conversation request framing and state updates.
18. Conversation-to-runtime admission boundary.
19. Dataset split/metadata governance.
20. Deterministic P50 health-check entrypoint.

## Local verification evidence
- Python compileall: PASS.
- P50 regression suite: 7/7 passed.
- Deterministic P50 health check: PASS.
- Expected P50 policy: CPU training, max 6 training threads, one heavy job, AC required, optional GPU offload for inference.

## Device execution policy
The supplied battery reading was 38%. Because the report did not establish AC-plugged state, the runtime deliberately refuses heavy training when running on battery at that state. This is an intentional safety behavior, not a failure.

## Repository boundary
The repository still contains the historical 588-file source publication in source-export/. The connector cannot reconstruct or physically execute the complete Windows/Electron/.NET/node-pty/llama.cpp stack on a non-Windows remote runtime. Therefore no claim is made that all 588 legacy files have passed native end-to-end execution.

## Next operation
- Synchronize remaining executable modules from source-export into a real file tree.
- Wire the new request pipeline/resource policy into the existing desktop application.
- Run Windows-native gates on the actual P50.
- Validate real model loading, GGUF/llama.cpp inference, training resume, tool execution, filesystem operations and rollback.
- Expand project/agent integration for the remaining feature layers.
- Keep Hermes inactive until separately authorized and verified.

## Control-plane integration — 2026-10-07

After the initial P50 work, the requested feature map was converted into an executable control-plane foundation rather than model-only prompt text. Existing files were backed up before modification; new files were added only after local verification.

### Added
- `backend/ali_control_plane.py`: requirements/contract extraction, clarification, planning/DAG, SQLite state, memory, knowledge index/search, secure project execution, snapshots, model routing, multi-agent supervision, and AgentLoop.
- `backend/tests/test_ali_control_plane.py`: regression tests for gaps/conflicts, planning, memory, workspace safety, command blocking, multi-agent, and dry-run flow.
- `backend/main.py`: `--self-test` entrypoint.

### Local evidence
- `python -m compileall`: PASS.
- Backend test suite: **22/22 passed**.
- Control-plane self-test: **checks_passed=true**.
- Deterministic P50 health gate: **admission.allowed=true**, CPU training policy, max 6 CPU threads, one heavy job, AC required.

### Safety/accuracy boundary
The control plane does not treat an unverified action as completed. High-impact file/command paths require approval, workspace escape is rejected, dangerous command patterns are blocked, and model fallback is explicit. The feature specification also requires that self-improvement be gated by testing/evaluation/approval instead of uncontrolled production mutation. fileciteturn358file0L771-L799

### Remaining native gates
The GitHub repository still publishes the historical 588-file source export; the native Windows/Electron/.NET/node-pty/model-binary stack has not been reconstructed and executed end-to-end in this non-Windows connector runtime. The remaining work therefore stays explicitly tracked instead of being marked complete by documentation alone.


## Professional completion pass — 2026-10-07

### Added executable modules
The canonical `backend/control_plane/` package now covers: schemas, requirements, planner, durable state store, memory, local knowledge/RAG, knowledge graph, tools, policy, workspace/project execution, acceptance, recovery/checkpoints, reliability, registry/lineage, provenance, scheduler, RBAC/network/tenant scope, observability, evaluation, release gates, dataset governance, self-improvement, capabilities, code/project intelligence, model runtime/GGUF capability detection, multimodal capability detection, local HTTP gateway, transaction wrapper, and the ProfessionalRuntime facade.

### Operational controls
- High-impact or externally visible actions remain approval-gated.
- Workspace escapes and unsafe command patterns are rejected.
- Stateful tasks use SQLite/WAL plus checkpoints and event logs.
- Retries are bounded with idempotency, budgets, rate limiting and circuit-breaker primitives.
- New model/dataset/tool/agent/artifact versions can be tracked with provenance/lineage and promotion gates.
- Self-improvement is candidate/evaluation/regression/approval based rather than uncontrolled production mutation.

### Verification
- compileall: PASS
- backend tests: **25/25 PASS**
- control-plane self-test: PASS
- canonical main self-test: PASS
- P50 deterministic admission: PASS
- professional health: PASS
- CI workflow added for Python 3.11 and 3.12.

### Native gates deliberately still open
The real physical Windows P50 remains required for Electron/node-pty, native UI integration, real model weights and GGUF/llama.cpp inference, real SFT/LoRA training/resume, full user-project E2E build/test/debug/rollback, multimodal execution, and distributed production HA/DR. These are not marked complete from code/docs alone.


## Final professional foundation pass

The control plane has been expanded beyond the initial P50 spine. The canonical package now includes requirements/contracts, acceptance and planning, durable state/events/failure memory, scoped memory, document ingestion, lexical/hybrid retrieval, knowledge graph, tool registry, safe workspace execution, command policy, Git checkpoints/rollback, recovery, reliability controls, scheduling, model routing/fallback, artifact/provenance/lineage, governance/RBAC/network/tenant scope, observability, categorized evaluation, release gates, dataset quality/leakage controls, controlled self-improvement, project/code intelligence, model/GGUF capability discovery, multimodal capability detection, local JSON gateway, transaction wrapper, and P50-aware training preflight.

Additional operational assets include CI for Python 3.11/3.12, a native Windows P50 validation script, architecture/security/acceptance/feature-matrix documentation, and the canonical control-plane self-test.

Final local evidence: compileall PASS; backend tests 29/29 PASS; control-plane self-test PASS; main.py self-test PASS; deterministic P50 admission PASS; professional health PASS.

Native target gates remain open until physically executed on the ThinkPad P50: Electron/node-pty integration, real model weights and GGUF/llama.cpp inference, real SFT/LoRA training and resume, complete UI-driven project E2E build/test/debug/rollback, actual multimodal execution where dependencies are absent, and distributed production HA/DR.

## Final main certification — 2026-10-07

- Final certified main base commit before snapshot branch: `e83ff7537eddbfde05ef8da8aeb034d448c9cadc`.
- Final certification commit in main: `e83ff7537eddbfde05ef8da8aeb034d448c9cadc` plus the post-certification snapshot branch changes only; application code is identical.
- GitHub Actions final Control Plane: Python 3.11 **33 passed**, Python 3.12 **33 passed**, `checks_passed=true`, P50 deterministic admission PASS.
- GitHub Actions final V5, V6 and Rebuild Source Tree: PASS.
- Final GitHub snapshot artifact: `ALI-main-final-full.zip`, SHA-256 `51ac2151f43de9c21c5c37bddc0dff918eba9743a1eb882e94da510e02f3bbe7`.
- Exact local snapshot verification: **995 files**, **425 Python**, **17 JSONL**, **683 restored-project files**, **85 source-export parts**; `compileall` PASS; `33 passed in 0.76s`.
- Restored source manifest reports **682** materialized files before the repository-level snapshot wrapper file, and the source-export remains 85 ordered parts.
- Final model lifecycle policy: training continues from verified checkpoint/adapter; GGUF remains runtime/export output only; cumulative replay is default; previous model/dataset/checkpoint versions are retained; destructive cleanup occurs only after verification.
- Final language policy: Arabic MSA + Saudi + Yemeni + Egyptian profiles; spelling normalization/correction is separated from response style selection.
- Final diagnostics: safe file inspection, ZIP/TAR path traversal checks, archive size/compression limits, project syntax/JSON checks, and root-cause classification.
- Known non-blocking GitHub Actions warning: hosted Action runtime is reporting Node 20 deprecation for currently used checkout/setup-python action versions; application tests remain green.
- Physical-target gates still require execution on the actual ThinkPad P50 for native Windows desktop/Electron/node-pty, actual model weights/GGUF/llama.cpp inference, real SFT/LoRA resume, full user-project E2E, and multimodal hardware-backed paths.
