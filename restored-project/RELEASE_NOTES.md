# ALI Studio Pro 4.1.0

## Continuous Learning Upgrade

- Drag/drop training area in Electron/React.
- Local file path resolution through Electron preload.
- Markdown/TXT/JSON/JSONL/CSV chat-pair parsing.
- Cross-file sample de-duplication using stable sample hashes.
- Accepted training files are indexed into the local RAG store immediately.
- New data only is used by each training cycle.
- Every successful cycle receives a human-readable generation: `v1`, `v2`, `v3`, ...
- New models stay Candidate until validation/regression gates pass.
- The previous Active model is kept by the registry for rollback.
- Failed runs leave the source cursor in `validated`, so they can be retried.
- The Electron status panel exposes live generation/progress/state.

## Important

A plain document without explicit User/Assistant examples is never converted into a fake supervised training sample. It is stored in local RAG and the UI reports `rag_only`.

Actual PyTorch/LoRA training still requires the packaged Python runtime and training dependencies on Windows.
