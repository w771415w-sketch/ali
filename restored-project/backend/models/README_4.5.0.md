# ALI local model strategy 4.5.0

The bundled bootstrap model is a tiny custom model used to test the training/promotion pipeline; the project report measured 0/8 model-only answers on that model. For real general chat on a 2 GB Quadro M1000M, the recommended practical upgrade is a small instruct GGUF plus llama.cpp.

Recommended starting point: Qwen2.5-0.5B-Instruct in Q4_K_M (~491 MB in the official GGUF repository). A 1.5B Q4_K_M is possible but leaves substantially less VRAM headroom.

The project keeps Training Base Model and Chat GGUF as separate artifacts: this prevents an inference-only GGUF from being accidentally used as a LoRA training base.
