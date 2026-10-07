# ALI AI 2.0 — Roadmap

## Delivered in the 2.1 control plane
- Professional three-pane desktop UI with local chat and streaming
- Persistent SQLite conversation sessions
- Central artifact lifecycle: inbox → inspect → install → verify → registry
- Versioned TokenizerManager with corpus hashing and reuse
- Progressive base → SFT → LoRA training pipeline
- LoRA adapter + merged-model export path
- Evaluation and promotion gate integration
- Explicit lineage and SHA-256 manifests
- Resume-safe checkpoints and CUDA DDP entry path
- CLI parity for training and artifact management
- P50-safe CPU-first defaults
- Autonomous incremental self-learning with candidate evaluation/promotion gate
- Bootstrap + P50 datasets included in the source bundle

## Next engineering stages
- stronger intent classifier and learned tool selection
- richer tool-call planning/replanning with structured traces
- benchmark suites by Arabic/English domain and task family
- multi-node job launcher and cluster artifact synchronization
- longer-context training experiments
- multimodal document/image/audio datasets
- online research → source review → training-candidate scheduler

The desktop product contract remains stable while these capabilities are added underneath it.
