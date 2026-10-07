# ALI Studio Pro 4.5.3 — Final Rebuild Checklist

## Imported reference facts
- Previous audit: `backend/knowledge_seed/ALI_V4_4_COMPLETE_REPORT.md`
- P50 full profile: `backend/knowledge_seed/THINKPAD_P50_COMPLETE_USER_PROFILE.md`
- P50 engineering profile: `backend/knowledge_seed/THINKPAD_P50_USER_PROFILE.md`

## Functional fixes included
- continuous training base/validation paths are resolved relative to the backend root;
- active-generation ledger archives the previous generation when a new one is promoted;
- GPU VRAM used/free ordering is correct;
- unknown GPU memory occupancy is never treated as 100% free;
- `/api/memory/list` remains an alias;
- Electron starts the backend automatically and discovers the packaged runtime;
- training import accepts Markdown + JSON/JSONL + text/document formats;
- new chat / history / rename / delete are wired to persistent sessions;
- training progress reports real steps, elapsed time and ETA;
- grounded fallback prefers a matching RAG Q&A answer instead of the first chunk;
- Qwen GGUF + llama.cpp are first-class optional local inference assets;
- setup scripts provide online and offline preparation paths.

## Acceptance gates
1. Python compileall.
2. Full pytest suite.
3. Import the P50 QA pack and assert sample count.
4. Real v1 training in an isolated workspace.
5. Real v2 training from v1 in an isolated workspace.
6. Registry promotion and rollback semantics.
7. API E2E for health/status/hardware/models/memory/conversations/training/chat/search.
8. Electron main/preload/api syntax checks.
9. Windows native: Electron build, .NET publish, node-pty/ConPTY, embedded Python, CUDA self-test.
10. Final ZIP integrity.

## Release honesty
This environment is Linux. Windows-native gates 8-9 cannot be truthfully marked PASS here. The package therefore contains scripts to execute those gates on the target Windows machine instead of inventing results.
