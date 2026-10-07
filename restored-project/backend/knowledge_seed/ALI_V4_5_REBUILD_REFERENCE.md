# ALI Studio Pro 4.5.0 Rebuild Reference

The previous report documented a functioning architecture but also listed 10 remaining issues: tiny 30 MB bootstrap model with 0/8 model-only answers, only 1566 new samples, heavy RAG reliance, garbled Arabic generation, unreliable nvidia-smi, unstable Electron backend URL detection, JSONL conversation/messages mismatch, incomplete production dist, Windows/GPU skipped tests, and a missing memory alias endpoint.

## Rebuild goals
1. Make the reported limitations explicit in the UI and Doctor.
2. Keep training Base Model separate from inference GGUF.
3. Make Markdown ingestion tolerant of common exporter wrappers.
4. Preserve chat sessions with explicit create/list/open/rename/delete operations.
5. Make GPU use adaptive and evidence-based for 2 GB VRAM.
6. Fall back to CPU safely in Auto mode on CUDA errors.
7. Never promote an unverified artifact.
8. Provide RAG-grounded fallback text when the tiny bootstrap model emits unusable output.
