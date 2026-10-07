# ALI Studio Pro 4.5.2 — Release Notes

## Rebuild focus
- Corrected continuous-learning checkpoint path resolution.
- Corrected GPU used/free VRAM bookkeeping and safe unknown-occupancy fallback.
- Added current P50 knowledge profile and authoritative current-status document.
- Added a 791-sample master conversation training pack assembled from prior packs plus new curated cases with duplicate removal.
- Improved grounded answer fallback to extract a matching Assistant answer from RAG Q&A blocks.
- Added robust new-chat/history refresh.
- Fixed malformed GPU Doctor batch script.
- Added Windows complete setup, embedded Python preparation, and offline wheelhouse preparation scripts.
- Added Qwen2.5-0.5B-Instruct Q4_K_M + llama.cpp download/verification path.
- Updated project version/tests to 4.5.2.

## Quality gates
Python tests and source-level checks run in Linux; Windows-native release gates remain explicitly deferred to the Windows target host.
