# ALI AI Pro 3.0 Architecture

## Core principle
ALI is trained from scratch. No Ollama, no external base model and no cloud model provider is required for local inference.

## Learning planes
1. **Weights plane**: full training / SFT / LoRA / checkpoints / evaluation / registry.
2. **Knowledge plane**: PDF/MD/DOCX/HTML/archives/web -> chunks -> hybrid retrieval.
3. **Memory plane**: conversations, episodic facts, project memory and provenance.
4. **Agent plane**: inspect -> plan -> snapshot -> apply -> test -> verify -> review.
5. **Extension plane**: skills, plugins, optional MCP and providers.
6. **Media plane**: image/audio/video encoders + trainable projector into ALI hidden space.
7. **Inference plane**: native PyTorch, CPU int8 path, HF export and GGUF bridge.

## Continuous learning identity
Every accepted training sample contributes a deterministic identity. A new candidate can be scheduled only when the accepted dataset identity changes. GGUF exports are keyed by checkpoint identity + dataset identity + quantization mode; repeated identities are skipped.

## Safe self-improvement
The self-manager never edits the program core blindly. Changes follow snapshot/branch, tests and verification. Model promotion is separate from code promotion.

## Hardware target
The default 2GB-VRAM profile uses batch size 1, gradient accumulation, conservative sequence length and CPU fallback. The model size is intentionally small enough for local experimentation; frontier-model equivalence is not assumed.
