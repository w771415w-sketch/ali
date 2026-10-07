# ALI AI Windows Deployment — P50 profile + Hermes

## Target
The build is tuned for a Lenovo ThinkPad P50 class workstation: 4 physical CPU cores / 8 logical threads, 32 GB RAM, and a 2 GB Quadro-class legacy GPU. Training defaults are CPU-first to avoid relying on 2 GB VRAM.

## Install
1. Install Python 3.13.x 64-bit.
2. Extract the selected project folder to `D:\ALI-AI`.
3. Run `SETUP.bat`.
4. Run `RUN-ALL-TESTS.bat`.
5. Run `START.bat`.

## Hermes
Keep Hermes separately at `D:\AI ALI\Hermes\`. Do not copy `.env` or `auth.json` into ALI. In the Hermes variants, the adapter reads only approved read-only files and SELECT/PRAGMA database data.

Use `RUN-HERMES-DOCTOR.bat` to inspect the configured external Hermes path. ALI still starts when Hermes is absent.

## Training
Use `Training Files` in the desktop UI and drop `.md` files. The manager validates, normalizes, redacts secrets, deduplicates, creates an incremental dataset, produces LoRA adapters, and waits for the configured merge threshold before creating a candidate merge.

## Included model
`models/active/ALI-Bootstrap-v2.5/` contains a small real bootstrap model for local smoke/inference/training tests. It is intentionally small for this hardware profile; it is not a 3B production model.

## Build EXE
Run `BUILD_EXE.bat` after setup. Python itself, GPU drivers, and platform-specific large wheel caches are not embedded because they are environment-specific.


## Continuous Learning 4.1
Drag training files into the Electron Training Center. Accepted Q/A data is deduplicated, indexed into RAG immediately, trained incrementally from the current Active model, evaluated, and versioned as v1, v2, v3... before promotion.
