# ALI AI model storage

- `active/` — only the promoted active HF/checkpoint model.
- `inbox/` — import-only staging area; never trusted automatically.
- `adapters/pending/` — accumulated LoRA updates waiting for merge.
- `adapters/archive/` — merged adapter archives.
- `merged/` — merged candidate outputs before promotion.
- `gguf/` — validated GGUF deployment artifacts.
- `archive/` — older model versions.

Large third-party model weights are not bundled into source distributions. Use the included model acquisition scripts/configuration when a real model is selected.
