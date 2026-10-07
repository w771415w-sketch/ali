# ALI Studio Pro 4.1.0 — Upgrade & Verification Report

## Implemented

1. Electron/React Training Center now has a real drag-and-drop training area.
2. Electron preload resolves local file paths securely for dropped files.
3. Python API endpoints were added for training ingest, status, start and cancel.
4. Accepted training files are normalized and common secret patterns are redacted.
5. Cross-file sample hashes prevent the same training example from being learned twice.
6. Valid sources are indexed into local RAG immediately, so the information is available without waiting for a weight update.
7. Only new validated training samples are used by each incremental cycle.
8. Each cycle creates a generation alias: v1, v2, v3, ...
9. Every generation records base version, dataset hash, training artifact, adapter and evaluation metadata.
10. A candidate is promoted only when the stable validation gate passes; otherwise the previous Active model remains active.
11. Failed jobs keep their source status as `validated` so the batch remains retryable.
12. The UI shows live phase, progress, pending source count and generation history.
13. Training starts automatically after a valid import when the `تدريب تلقائي` switch is enabled (default ON).

## Data routing

- Explicit Q/A or chat datasets → RAG + incremental training.
- Plain reference documents without explicit User/Assistant pairs → RAG only.
- User/session facts → should remain in Memory rather than being baked into weights.

## Verification

- Python compilation: PASS.
- Backend test suite: 148 passed, 34 skipped, 2 warnings.
- Electron main/preload CommonJS syntax: PASS.
- Native Windows Electron packaging and C# publish: not executable in the current Linux verification environment; these are release-gated in the Windows build scripts.

## Release path

Use `scripts/BUILD_DESKTOP.bat` then `scripts/BUILD_PORTABLE.bat` on Windows with Node.js 22, .NET 8 SDK, and the embedded Python 3.11.9 runtime populated at `runtime\python\python.exe`.


## End-to-end training verification

A real PyTorch/LoRA cycle was executed against the bundled bootstrap model in a temporary verification workspace: `v1` trained and promoted, followed by a second independent batch that trained from `v1` and promoted as `v2`. Both generations preserved lineage and reported `pending_converter` for GGUF only because the verification environment does not contain a `vendor/llama.cpp` converter.
