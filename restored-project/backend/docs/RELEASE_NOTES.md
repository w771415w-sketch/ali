# ALI AI 2.1.0 — Unified KCA / P50

## 2.1.0 changes

- Integrated the uploaded AI-KCA 3.0 operational architecture as a real control-plane layer.
- Added a source-derived 100-function registry with stable IDs and contracts.
- Added typed request/state/plan/trace contracts and deterministic routing.
- Added SQLite KCA operation/state persistence.
- Added KCA-enriched conversation dataset generation with deduplication, provenance and secret redaction.
- Made model/training services lazy in the desktop UI.
- Added cached/lazy hardware probing and explicit P50 CPU-first policy.
- Hardened GGUF artifact inspection so arbitrary `.gguf` files are not accepted as valid.
- Preserved progressive `base → sft → lora → merged` lifecycle and candidate/promotion gates from 2.0.

## Verification target

The project is designed so source compilation, unit/regression tests, KCA registry checks and artifact validation are run before release claims.
