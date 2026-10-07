# ALI AI 2.5.0 — Windows Installation and Runtime Guide

## Included in this project

- Professional Tkinter desktop shell matching the supplied light UI reference.
- Three-pane workspace with conversations/projects/files on the left, chat in the center, and developer/telemetry/health surfaces on the right.
- Live Execution Monitor below the developer notebook; it displays active job, phase, detail and progress while work is running.
- Accumulated Markdown Training Center with validation, secret redaction, deduplication, incremental cursor protection, LoRA adapters and threshold-based merge candidates.
- KCA control plane, local memory/RAG layers, dataset and training pipeline, model registry and GGUF validation/conversion bridge.
- Phase-2 catalog only: future image/video providers, search engines, MCP servers, skills, toolsets, browser/CDP, computer-use, cron, subagents and messaging connectors are recorded in `phase2/` and disabled by default.
- A functional micro bootstrap model is included at `models/active/ALI-Bootstrap-v2.5/` for startup and inference smoke tests.

## Windows setup

1. Install 64-bit Python.
2. Extract this project to a normal writable path such as `D:\ALI-AI`.
3. Run `SETUP.bat`.
4. Run `RUN-ALL-TESTS.bat`.
5. Run `START.bat`.

## Optional external runtime

GGUF execution is intentionally separated from the core Python application. When you later install a compatible `llama.cpp` Windows build, place/configure the runtime path through the model/runtime settings and keep GGUF files under `models/gguf/`.

## Model note

The included bootstrap model is a small model trained from scratch for pipeline/startup validation. It is not a large production-quality assistant model. The application can load it immediately, while larger models may be imported into `models/inbox/` and then validated through the model manager.

## Phase-2 policy

`phase2/*.json` contains the exact names supplied for the future integration stage. Unspecified names (for example, the user's 22 messaging platforms) remain empty rather than being invented. No provider credentials, API keys, OAuth tokens or private connector data are bundled.

## Portable EXE

Run `BUILD_EXE.bat` after `SETUP.bat`. It produces `dist\\ALI-AI\\` as an onedir application with the bootstrap model and phase-2 catalogs included.


## Continuous Learning 4.1
Drag training files into the Electron Training Center. Accepted Q/A data is deduplicated, indexed into RAG immediately, trained incrementally from the current Active model, evaluated, and versioned as v1, v2, v3... before promotion.
