      },
      {
        "step": 57,
        "total_steps": 60,
        "epoch": 1,
        "loss": 6.091390132904053,
        "lr": 4.144511940348516e-06,
        "tokens_seen": 35485,
        "tokens_per_sec": 2119.17,
        "samples_seen": 456,
        "total_samples": 1532,
        "elapsed_sec": 16.74,
        "eta_sec": 0.88,
        "rank": 0,
        "world_size": 1
      },
      {
        "step": 58,
        "total_steps": 60,
        "epoch": 1,
        "loss": 6.475715160369873,
        "lr": 1.8467489107293509e-06,
        "tokens_seen": 35996,
        "tokens_per_sec": 2115.82,
        "samples_seen": 464,
        "total_samples": 1532,
        "elapsed_sec": 17.01,
        "eta_sec": 0.59,
        "rank": 0,
        "world_size": 1
      },
      {
        "step": 59,
        "total_steps": 60,
        "epoch": 1,
        "loss": 6.202650547027588,
        "lr": 4.623999400308054e-07,
        "tokens_seen": 36590,
        "tokens_per_sec": 2115.96,
        "samples_seen": 472,
        "total_samples": 1532,
        "elapsed_sec": 17.29,
        "eta_sec": 0.29,
        "rank": 0,
        "world_size": 1
      },
      {
        "step": 60,
        "total_steps": 60,
        "epoch": 1,
        "loss": 6.3332366943359375,
        "lr": 0.0,
        "tokens_seen": 37283,
        "tokens_per_sec": 2118.82,
        "samples_seen": 480,
        "total_samples": 1532,
        "elapsed_sec": 17.6,
        "eta_sec": 0.0,
        "rank": 0,
        "world_size": 1
      }
    ]
  },
  "evaluation": {
    "loss": 6.969683837890625,
    "perplexity": 1063.8863368118753,
    "samples": 60
  },
  "checkpoint": "models/runs/20261006-142710-7225c1/checkpoints/final-000060",
  "run_hf_dir": "models/runs/20261006-142710-7225c1/checkpoints/final-000060/hf",
  "merged_hf": "backend/models/generations/v4/artifacts/merged_hf",
  "merged_hf_hash": "aa12180223a7e1e542b1fd1d7e479f9ac092c0a0678c1f4c227145bd887dd1dc",
  "gguf": {
    "status": "pending_converter",
    "reason": "llama.cpp Windows converter binary is not included in the source bundle"
  }
}
```

---

### `233/588` `backend/models/gguf/README.md`

- **المسار الكامل:** `F:\1f\p\ALI_Studio_Pro_Design4_4.6.0\04_Adaptive_Hybrid\backend/models/gguf/README.md`
- **الحجم:** 95 بايت (0.1 KB)
- **الامتداد:** `.md`

```markdown
# Validated GGUF deployment artifacts. Configure `ALI_LLAMA_SERVER_EXE` for llama.cpp runtime.
```

---

### `234/588` `backend/models/inbox/ALI-v1/ali_metadata.json`

- **المسار الكامل:** `F:\1f\p\ALI_Studio_Pro_Design4_4.6.0\04_Adaptive_Hybrid\backend/models/inbox/ALI-v1/ali_metadata.json`
- **الحجم:** 309 بايت (0.3 KB)
- **الامتداد:** `.json`

```json
{
  "version": "v1",
  "base_version": "2.5.0-bootstrap-micro",
  "dataset_hash": "9c5d81476f79db6cf6200969c11ef514c6b7c95f4935bb9fee91c34c19e88d3d",
  "steps": 200,
  "merged_lora_layers": 28,
  "parameter_count": 3607872,
  "source": "ALI Studio trained-from-scratch",
  "architecture": "LlamaForCausalLM"
}
```

---

### `235/588` `backend/models/inbox/ALI-v1/config.json`

- **المسار الكامل:** `F:\1f\p\ALI_Studio_Pro_Design4_4.6.0\04_Adaptive_Hybrid\backend/models/inbox/ALI-v1/config.json`
- **الحجم:** 559 بايت (0.5 KB)
- **الامتداد:** `.json`

```json
{
  "vocab_size": 3247,
  "hidden_size": 192,
  "intermediate_size": 768,
  "num_hidden_layers": 4,
  "num_attention_heads": 6,
  "num_key_value_heads": 6,
  "max_position_embeddings": 128,
  "rms_norm_eps": 1e-06,
  "rope_theta": 10000.0,
  "attention_dropout": 0.0,
  "bos_token_id": 1,
  "eos_token_id": 2,
  "pad_token_id": 3,
  "model_type": "llama",
  "architectures": [
    "LlamaForCausalLM"
  ],
  "hidden_act": "silu",
  "initializer_range": 0.02,
  "use_cache": true,
  "use_sdpa": true,
  "tie_word_embeddings": false,
  "torch_dtype": "float32"
}
```

---

### `236/588` `backend/models/inbox/ALI-v1/special_tokens_map.json`

- **المسار الكامل:** `F:\1f\p\ALI_Studio_Pro_Design4_4.6.0\04_Adaptive_Hybrid\backend/models/inbox/ALI-v1/special_tokens_map.json`
- **الحجم:** 202 بايت (0.2 KB)
- **الامتداد:** `.json`

```json
{
  "bos_token": "<s>",
  "eos_token": "</s>",
  "pad_token": "<pad>",
  "unk_token": "<unk>",
  "additional_special_tokens": [
    "<|system|>",
    "<|user|>",
    "<|assistant|>",
    "<|eot|>"
  ]
}
```

---

### `237/588` `backend/models/inbox/ALI-v1/tokenizer_config.json`

- **المسار الكامل:** `F:\1f\p\ALI_Studio_Pro_Design4_4.6.0\04_Adaptive_Hybrid\backend/models/inbox/ALI-v1/tokenizer_config.json`
- **الحجم:** 313 بايت (0.3 KB)
- **الامتداد:** `.json`

```json
{
  "model_type": "llama",
  "add_bos_token": true,
  "add_eos_token": false,
  "bos_token": "<s>",
  "eos_token": "</s>",
  "pad_token": "<pad>",
  "unk_token": "<unk>",
  "chat_template": "<s>{% for message in messages %}<|{{ message['role'] }}|>\n{{ message['content'] }}<|eot|>\n{% endfor %}<|assistant|>\n"
}
```

---

### `238/588` `backend/models/inbox/README.md`

- **المسار الكامل:** `F:\1f\p\ALI_Studio_Pro_Design4_4.6.0\04_Adaptive_Hybrid\backend/models/inbox/README.md`
- **الحجم:** 62 بايت (0.1 KB)
- **الامتداد:** `.md`

```markdown
# Put a real HF/GGUF model here for compatibility inspection.
```

---

### `239/588` `backend/models/model_manifest.json`

- **المسار الكامل:** `F:\1f\p\ALI_Studio_Pro_Design4_4.6.0\04_Adaptive_Hybrid\backend/models/model_manifest.json`
- **الحجم:** 815 بايت (0.8 KB)
- **الامتداد:** `.json`

```json
{
  "recommended": {
    "name": "Qwen2.5-0.5B-Instruct",
    "gguf_quant": "Q4_K_M",
    "size_mb": 398,
    "sha256": "750f8f144f0504208add7897f01c7d2350a7363d8855eab59e137a1041e90394",
    "layers": 24,
    "params_b": 0.49,
    "min_free_vram_gb": 0.65,
    "source": "https://huggingface.co/second-state/Qwen2.5-0.5B-Instruct-GGUF"
  },
  "training_base": "models/active/ALI-Bootstrap-v2.5",
  "chat_backend": "llama.cpp local OpenAI-compatible server",
  "notes": [
    "Q4_K_M is the recommended balanced quantization in the referenced GGUF repository.",
    "The internal bootstrap model remains a training/diagnostic model and is not treated as a production-quality chat model.",
    "On a 2GB Maxwell GPU, offload is adaptive and may fall back to CPU if the legacy CUDA build cannot launch safely."
  ]
}
```

---

### `240/588` `backend/models/README.md`

- **المسار الكامل:** `F:\1f\p\ALI_Studio_Pro_Design4_4.6.0\04_Adaptive_Hybrid\backend/models/README.md`
- **الحجم:** 590 بايت (0.6 KB)
- **الامتداد:** `.md`

```markdown
# ALI AI model storage

- `active/` — only the promoted active HF/checkpoint model.
- `inbox/` — import-only staging area; never trusted automatically.
- `adapters/pending/` — accumulated LoRA updates waiting for merge.
- `adapters/archive/` — merged adapter archives.
- `merged/` — merged candidate outputs before promotion.
- `gguf/` — validated GGUF deployment artifacts.
- `archive/` — older model versions.

Large third-party model weights are not bundled into source distributions. Use the included model acquisition scripts/configuration when a real model is selected.
```

---

### `241/588` `backend/models/README_4.5.0.md`

- **المسار الكامل:** `F:\1f\p\ALI_Studio_Pro_Design4_4.6.0\04_Adaptive_Hybrid\backend/models/README_4.5.0.md`
- **الحجم:** 661 بايت (0.6 KB)
- **الامتداد:** `.md`

```markdown
# ALI local model strategy 4.5.0

The bundled bootstrap model is a tiny custom model used to test the training/promotion pipeline; the project report measured 0/8 model-only answers on that model. For real general chat on a 2 GB Quadro M1000M, the recommended practical upgrade is a small instruct GGUF plus llama.cpp.

Recommended starting point: Qwen2.5-0.5B-Instruct in Q4_K_M (~491 MB in the official GGUF repository). A 1.5B Q4_K_M is possible but leaves substantially less VRAM headroom.

The project keeps Training Base Model and Chat GGUF as separate artifacts: this prevents an inference-only GGUF from being accidentally used as a LoRA training base.
```

---

### `242/588` `backend/models/runs/ALI-v1-20261004-224649-233144/BUNDLED_MODEL_README.md`

- **المسار الكامل:** `F:\1f\p\ALI_Studio_Pro_Design4_4.6.0\04_Adaptive_Hybrid\backend/models/runs/ALI-v1-20261004-224649-233144/BUNDLED_MODEL_README.md`
- **الحجم:** 454 بايت (0.4 KB)
- **الامتداد:** `.md`

```markdown
# ALI-v1 bundled trained model

ناتج التدريب الفعلي لملف ALI User Understanding V4. يحتوي الإصدار على checkpoint وLoRA adapter وinternal model وmerged HF weights وبيانات التدريب والـvalidation وسجل التحقق.

- 216 sections parsed
- 215 unique Q/A samples after exact deduplication
- LoRA training: 13 steps
- merged weight verification: max diff 0.0
- quiz: 216/216 source-answer matches
```

---

### `243/588` `backend/models/runs/ALI-v1-20261004-224649-233144/checkpoints/final-000013/adapter/adapter_config.json`

- **المسار الكامل:** `F:\1f\p\ALI_Studio_Pro_Design4_4.6.0\04_Adaptive_Hybrid\backend/models/runs/ALI-v1-20261004-224649-233144/checkpoints/final-000013/adapter/adapter_config.json`
- **الحجم:** 6436 بايت (6.3 KB)
- **الامتداد:** `.json`

```json
{
  "run_id": "20261004-224649-233144",
  "stage": "lora",
  "dataset_hash": "406ccb419f45bc20acc61368b41bb3f31451370bcfd8217c2d3d565f114d8a8d",
  "tokenizer_hash": "5e6970f5f6bac2d299df737015ef5006310fe2a153a2d44c6e6f477ed10565e1",
  "pipeline_config": {
    "name": "ALI",
    "stage": "lora",
    "scale": "small",
    "train_path": "/mnt/data/ali_v457_postfix2_e2e/backend/artifacts/continuous_learning/runs/continuous-v1-20261004-224649-e71dab/train_new.jsonl",
    "validation_path": "/mnt/data/ali_v457_postfix2_e2e/backend/artifacts/continuous_learning/runs/continuous-v1-20261004-224649-e71dab/stable_validation.jsonl",
    "tokenizer_inputs": null,
    "tokenizer_vocab_size": 4096,
    "base_checkpoint": "models/active/ALI-Bootstrap-v2.5",
    "resume_checkpoint": "",
    "max_steps": 0,
    "epochs": 1,
    "max_seq_len": 256,
    "batch_size": 1,
    "grad_accum": 16,
    "learning_rate": 0.0003,
    "device": "cpu",
    "lora_rank": 8,
    "lora_alpha": 16.0,
    "lora_dropout": 0.05,
    "curriculum": true,
    "distributed_backend": "auto",
    "world_size": 1
  },
  "kca_schema": "3.0",
  "kca_registry_hash": "9ed24e57ea920e5ffa8b0746db0283191d240587d5e77753f1fcf6e8a66a713a",
  "result": {
    "checkpoint": "/mnt/data/ali_v457_postfix2_e2e/backend/models/runs/20261004-224649-233144/checkpoints/final-000013",
    "global_step": 13,
    "steps": 13,
    "loss": 7.509772777557373,
    "val_loss": 6.771079770723978,
    "best_val": 6.771079770723978,
    "tokens_seen": 26624,
    "tokens_per_sec": 1605.26,
    "history": [
      {
        "step": 1,
        "total_steps": 13,
        "epoch": 1,
        "loss": 7.530920028686523,
        "lr": 2.9999999999999997e-05,
        "tokens_seen": 2048,
        "tokens_per_sec": 1581.13,
        "samples_seen": 16,
        "total_samples": 195,
        "elapsed_sec": 1.3,
        "eta_sec": 15.54,
        "rank": 0,
        "world_size": 1
      },
      {
        "step": 2,
        "total_steps": 13,
        "epoch": 1,
        "loss": 7.573794841766357,
        "lr": 4.4999999999999996e-05,
        "tokens_seen": 4096,
        "tokens_per_sec": 1743.49,
        "samples_seen": 32,
        "total_samples": 195,
        "elapsed_sec": 2.35,
        "eta_sec": 12.92,
        "rank": 0,
        "world_size": 1
      },
      {
        "step": 3,
        "total_steps": 13,
        "epoch": 1,
        "loss": 7.536900520324707,
        "lr": 5.9999999999999995e-05,
        "tokens_seen": 6144,
        "tokens_per_sec": 1665.7,
        "samples_seen": 48,
        "total_samples": 195,
        "elapsed_sec": 3.69,
        "eta_sec": 12.3,
        "rank": 0,
        "world_size": 1
      },
      {
        "step": 4,
        "total_steps": 13,
        "epoch": 1,
        "loss": 7.3177103996276855,
        "lr": 7.5e-05,
        "tokens_seen": 8192,
        "tokens_per_sec": 1697.2,
        "samples_seen": 64,
        "total_samples": 195,
        "elapsed_sec": 4.83,
        "eta_sec": 10.86,
        "rank": 0,
        "world_size": 1
      },
      {
        "step": 5,
        "total_steps": 13,
        "epoch": 1,
        "loss": 7.579038143157959,
        "lr": 8.999999999999999e-05,
        "tokens_seen": 10240,
        "tokens_per_sec": 1696.8,
        "samples_seen": 80,
        "total_samples": 195,
        "elapsed_sec": 6.03,
        "eta_sec": 9.66,
        "rank": 0,
        "world_size": 1
      },
      {
        "step": 6,
        "total_steps": 13,
        "epoch": 1,
        "loss": 7.777761459350586,
        "lr": 0.00010499999999999999,
        "tokens_seen": 12288,
        "tokens_per_sec": 1705.4,
        "samples_seen": 96,
        "total_samples": 195,
        "elapsed_sec": 7.21,
        "eta_sec": 8.41,
        "rank": 0,
        "world_size": 1
      },
      {
        "step": 7,
        "total_steps": 13,
        "epoch": 1,
        "loss": 7.553614616394043,
        "lr": 0.00011999999999999999,
        "tokens_seen": 14336,
        "tokens_per_sec": 1700.86,
        "samples_seen": 112,
        "total_samples": 195,
        "elapsed_sec": 8.43,
        "eta_sec": 7.22,
        "rank": 0,
        "world_size": 1
      },
      {
        "step": 8,
        "total_steps": 13,
        "epoch": 1,
        "loss": 7.676057815551758,
        "lr": 0.000135,
        "tokens_seen": 16384,
        "tokens_per_sec": 1703.83,
        "samples_seen": 128,
        "total_samples": 195,
        "elapsed_sec": 9.62,
        "eta_sec": 6.01,
        "rank": 0,
        "world_size": 1
      },
      {
        "step": 9,
        "total_steps": 13,
        "epoch": 1,
        "loss": 7.377039909362793,
        "lr": 0.00015,
        "tokens_seen": 18432,
        "tokens_per_sec": 1711.45,
        "samples_seen": 144,
        "total_samples": 195,
        "elapsed_sec": 10.77,
        "eta_sec": 4.79,
        "rank": 0,
        "world_size": 1
      },
      {
        "step": 10,
        "total_steps": 13,
        "epoch": 1,
        "loss": 7.299834728240967,
        "lr": 0.000165,
        "tokens_seen": 20480,
        "tokens_per_sec": 1698.96,
        "samples_seen": 160,
        "total_samples": 195,
        "elapsed_sec": 12.05,
        "eta_sec": 3.62,
        "rank": 0,
        "world_size": 1
      },
      {
        "step": 11,
        "total_steps": 13,
        "epoch": 1,
        "loss": 7.562159061431885,
        "lr": 0.00017999999999999998,
        "tokens_seen": 22528,
        "tokens_per_sec": 1704.55,
        "samples_seen": 176,
        "total_samples": 195,
        "elapsed_sec": 13.22,
        "eta_sec": 2.4,
        "rank": 0,
        "world_size": 1
      },
      {
        "step": 12,
        "total_steps": 13,
        "epoch": 1,
        "loss": 7.417482852935791,
        "lr": 0.000195,
        "tokens_seen": 24576,
        "tokens_per_sec": 1692.23,
        "samples_seen": 192,
        "total_samples": 195,
        "elapsed_sec": 14.52,
        "eta_sec": 1.21,
        "rank": 0,
        "world_size": 1
      },
      {
        "step": 13,
        "total_steps": 13,
        "epoch": 2,
        "loss": 7.509772777557373,
        "lr": 0.00020999999999999998,
        "tokens_seen": 26624,
        "tokens_per_sec": 1699.75,
        "samples_seen": 208,
        "total_samples": 195,
        "elapsed_sec": 15.66,
        "eta_sec": 0.0,
        "rank": 0,
        "world_size": 1
      }
    ]
  },
  "rank": 8,
  "alpha": 16.0,
  "dropout": 0.05
}
```

---

### `244/588` `backend/models/runs/ALI-v1-20261004-224649-233144/checkpoints/final-000013/adapter_config.json`

- **المسار الكامل:** `F:\1f\p\ALI_Studio_Pro_Design4_4.6.0\04_Adaptive_Hybrid\backend/models/runs/ALI-v1-20261004-224649-233144/checkpoints/final-000013/adapter_config.json`
- **الحجم:** 6436 بايت (6.3 KB)
- **الامتداد:** `.json`

```json
{
  "run_id": "20261004-224649-233144",
  "stage": "lora",
  "dataset_hash": "406ccb419f45bc20acc61368b41bb3f31451370bcfd8217c2d3d565f114d8a8d",
  "tokenizer_hash": "5e6970f5f6bac2d299df737015ef5006310fe2a153a2d44c6e6f477ed10565e1",
  "pipeline_config": {
    "name": "ALI",
    "stage": "lora",
    "scale": "small",
    "train_path": "/mnt/data/ali_v457_postfix2_e2e/backend/artifacts/continuous_learning/runs/continuous-v1-20261004-224649-e71dab/train_new.jsonl",
    "validation_path": "/mnt/data/ali_v457_postfix2_e2e/backend/artifacts/continuous_learning/runs/continuous-v1-20261004-224649-e71dab/stable_validation.jsonl",
    "tokenizer_inputs": null,
    "tokenizer_vocab_size": 4096,
    "base_checkpoint": "models/active/ALI-Bootstrap-v2.5",
    "resume_checkpoint": "",
    "max_steps": 0,
    "epochs": 1,
    "max_seq_len": 256,
    "batch_size": 1,
    "grad_accum": 16,
    "learning_rate": 0.0003,
    "device": "cpu",
    "lora_rank": 8,
    "lora_alpha": 16.0,
    "lora_dropout": 0.05,
    "curriculum": true,
    "distributed_backend": "auto",
    "world_size": 1
  },
  "kca_schema": "3.0",
  "kca_registry_hash": "9ed24e57ea920e5ffa8b0746db0283191d240587d5e77753f1fcf6e8a66a713a",
  "result": {
    "checkpoint": "/mnt/data/ali_v457_postfix2_e2e/backend/models/runs/20261004-224649-233144/checkpoints/final-000013",
    "global_step": 13,
    "steps": 13,
    "loss": 7.509772777557373,
    "val_loss": 6.771079770723978,
    "best_val": 6.771079770723978,
    "tokens_seen": 26624,
    "tokens_per_sec": 1605.26,
    "history": [
      {
        "step": 1,
        "total_steps": 13,
        "epoch": 1,
        "loss": 7.530920028686523,
        "lr": 2.9999999999999997e-05,
        "tokens_seen": 2048,
        "tokens_per_sec": 1581.13,
        "samples_seen": 16,
        "total_samples": 195,
        "elapsed_sec": 1.3,
        "eta_sec": 15.54,
        "rank": 0,
        "world_size": 1
      },
      {
        "step": 2,
        "total_steps": 13,
        "epoch": 1,
        "loss": 7.573794841766357,
        "lr": 4.4999999999999996e-05,
        "tokens_seen": 4096,
        "tokens_per_sec": 1743.49,
        "samples_seen": 32,
        "total_samples": 195,
        "elapsed_sec": 2.35,
        "eta_sec": 12.92,
        "rank": 0,
        "world_size": 1
      },
      {
        "step": 3,
        "total_steps": 13,
        "epoch": 1,
        "loss": 7.536900520324707,
        "lr": 5.9999999999999995e-05,
        "tokens_seen": 6144,
        "tokens_per_sec": 1665.7,
        "samples_seen": 48,
        "total_samples": 195,
        "elapsed_sec": 3.69,
        "eta_sec": 12.3,
        "rank": 0,
        "world_size": 1
      },
      {
        "step": 4,
        "total_steps": 13,
        "epoch": 1,
        "loss": 7.3177103996276855,
        "lr": 7.5e-05,
        "tokens_seen": 8192,
        "tokens_per_sec": 1697.2,
        "samples_seen": 64,
        "total_samples": 195,
        "elapsed_sec": 4.83,
        "eta_sec": 10.86,
        "rank": 0,
        "world_size": 1
      },
      {
        "step": 5,
        "total_steps": 13,
        "epoch": 1,
        "loss": 7.579038143157959,
        "lr": 8.999999999999999e-05,
        "tokens_seen": 10240,
        "tokens_per_sec": 1696.8,
        "samples_seen": 80,
        "total_samples": 195,
        "elapsed_sec": 6.03,
        "eta_sec": 9.66,
        "rank": 0,
        "world_size": 1
      },
      {
        "step": 6,
        "total_steps": 13,
        "epoch": 1,
        "loss": 7.777761459350586,
        "lr": 0.00010499999999999999,
        "tokens_seen": 12288,
        "tokens_per_sec": 1705.4,
        "samples_seen": 96,
        "total_samples": 195,
        "elapsed_sec": 7.21,
        "eta_sec": 8.41,
        "rank": 0,
        "world_size": 1
      },
      {
        "step": 7,
        "total_steps": 13,
        "epoch": 1,
        "loss": 7.553614616394043,
        "lr": 0.00011999999999999999,
        "tokens_seen": 14336,
        "tokens_per_sec": 1700.86,
        "samples_seen": 112,
        "total_samples": 195,
        "elapsed_sec": 8.43,
        "eta_sec": 7.22,
        "rank": 0,
        "world_size": 1
      },
      {
        "step": 8,
        "total_steps": 13,
        "epoch": 1,
        "loss": 7.676057815551758,
        "lr": 0.000135,
        "tokens_seen": 16384,
        "tokens_per_sec": 1703.83,
        "samples_seen": 128,
        "total_samples": 195,
        "elapsed_sec": 9.62,
        "eta_sec": 6.01,
        "rank": 0,
        "world_size": 1
      },
      {
        "step": 9,
        "total_steps": 13,
        "epoch": 1,
        "loss": 7.377039909362793,
        "lr": 0.00015,
        "tokens_seen": 18432,
        "tokens_per_sec": 1711.45,
        "samples_seen": 144,
        "total_samples": 195,
        "elapsed_sec": 10.77,
        "eta_sec": 4.79,
        "rank": 0,
        "world_size": 1
      },
      {
        "step": 10,
        "total_steps": 13,
        "epoch": 1,
        "loss": 7.299834728240967,
        "lr": 0.000165,
        "tokens_seen": 20480,
        "tokens_per_sec": 1698.96,
        "samples_seen": 160,
        "total_samples": 195,
        "elapsed_sec": 12.05,
        "eta_sec": 3.62,
        "rank": 0,
        "world_size": 1
      },
      {
        "step": 11,
        "total_steps": 13,
        "epoch": 1,
        "loss": 7.562159061431885,
        "lr": 0.00017999999999999998,
        "tokens_seen": 22528,
        "tokens_per_sec": 1704.55,
        "samples_seen": 176,
        "total_samples": 195,
        "elapsed_sec": 13.22,
        "eta_sec": 2.4,
        "rank": 0,
        "world_size": 1
      },
      {
        "step": 12,
        "total_steps": 13,
        "epoch": 1,
        "loss": 7.417482852935791,
        "lr": 0.000195,
        "tokens_seen": 24576,
        "tokens_per_sec": 1692.23,
        "samples_seen": 192,
        "total_samples": 195,
        "elapsed_sec": 14.52,
        "eta_sec": 1.21,
        "rank": 0,
        "world_size": 1
      },
      {
        "step": 13,
        "total_steps": 13,
        "epoch": 2,
        "loss": 7.509772777557373,
        "lr": 0.00020999999999999998,
        "tokens_seen": 26624,
        "tokens_per_sec": 1699.75,
        "samples_seen": 208,
        "total_samples": 195,
        "elapsed_sec": 15.66,
        "eta_sec": 0.0,
        "rank": 0,
        "world_size": 1
      }
    ]
  },
  "rank": 8,
  "alpha": 16.0,
  "dropout": 0.05
}
```

---

### `245/588` `backend/models/runs/ALI-v1-20261004-224649-233144/checkpoints/final-000013/generation.json`

- **المسار الكامل:** `F:\1f\p\ALI_Studio_Pro_Design4_4.6.0\04_Adaptive_Hybrid\backend/models/runs/ALI-v1-20261004-224649-233144/checkpoints/final-000013/generation.json`
- **الحجم:** 1197 بايت (1.2 KB)
- **الامتداد:** `.json`

```json
{
  "generation": "v1",
  "base_version": "2.5.0-bootstrap-micro",
  "run_id": "continuous-v1-20261004-224649-e71dab",
  "train_path": "/mnt/data/ali_v457_postfix2_e2e/backend/artifacts/continuous_learning/runs/continuous-v1-20261004-224649-e71dab/train_new.jsonl",
  "validation_path": "/mnt/data/ali_v457_postfix2_e2e/backend/artifacts/continuous_learning/runs/continuous-v1-20261004-224649-e71dab/stable_validation.jsonl",
  "hf_dir": "/mnt/data/ali_v457_postfix2_e2e/backend/models/runs/20261004-224649-233144/checkpoints/final-000013/merged_hf",
  "adapter": "/mnt/data/ali_v457_postfix2_e2e/backend/models/runs/20261004-224649-233144/checkpoints/final-000013/adapter",
  "evaluation": {
    "loss": 6.771079858144124,
    "perplexity": 872.2532954340983,
    "samples": 60,
    "new_data_holdout": {
      "loss": 7.454573845863342,
      "perplexity": 1727.7475515931083,
      "samples": 20
    }
  },
  "gate": {
    "promote": true,
    "reason": "first learned generation with valid evaluation"
  },
  "gguf": {
    "status": "pending_converter",
    "llama_dir": "/mnt/data/ali_v457_postfix2_e2e/backend/vendor/llama.cpp"
  },
  "status": "active",
  "created_at": 1791154027.9529731
}
```

---

### `246/588` `backend/models/runs/ALI-v1-20261004-224649-233144/checkpoints/final-000013/merged_hf/ali_metadata.json`

- **المسار الكامل:** `F:\1f\p\ALI_Studio_Pro_Design4_4.6.0\04_Adaptive_Hybrid\backend/models/runs/ALI-v1-20261004-224649-233144/checkpoints/final-000013/merged_hf/ali_metadata.json`
- **الحجم:** 6530 بايت (6.4 KB)
- **الامتداد:** `.json`

```json
{
  "run_id": "20261004-224649-233144",
  "stage": "lora",
  "dataset_hash": "406ccb419f45bc20acc61368b41bb3f31451370bcfd8217c2d3d565f114d8a8d",
  "tokenizer_hash": "5e6970f5f6bac2d299df737015ef5006310fe2a153a2d44c6e6f477ed10565e1",
  "pipeline_config": {
    "name": "ALI",
    "stage": "lora",
    "scale": "small",
    "train_path": "/mnt/data/ali_v457_postfix2_e2e/backend/artifacts/continuous_learning/runs/continuous-v1-20261004-224649-e71dab/train_new.jsonl",
    "validation_path": "/mnt/data/ali_v457_postfix2_e2e/backend/artifacts/continuous_learning/runs/continuous-v1-20261004-224649-e71dab/stable_validation.jsonl",
    "tokenizer_inputs": null,
    "tokenizer_vocab_size": 4096,
    "base_checkpoint": "models/active/ALI-Bootstrap-v2.5",
    "resume_checkpoint": "",
    "max_steps": 0,
    "epochs": 1,
    "max_seq_len": 256,
    "batch_size": 1,
    "grad_accum": 16,
    "learning_rate": 0.0003,
    "device": "cpu",
    "lora_rank": 8,
    "lora_alpha": 16.0,
    "lora_dropout": 0.05,
    "curriculum": true,
    "distributed_backend": "auto",
    "world_size": 1
  },
  "kca_schema": "3.0",
  "kca_registry_hash": "9ed24e57ea920e5ffa8b0746db0283191d240587d5e77753f1fcf6e8a66a713a",
  "result": {
    "checkpoint": "/mnt/data/ali_v457_postfix2_e2e/backend/models/runs/20261004-224649-233144/checkpoints/final-000013",
    "global_step": 13,
    "steps": 13,
    "loss": 7.509772777557373,
    "val_loss": 6.771079770723978,
    "best_val": 6.771079770723978,
    "tokens_seen": 26624,
    "tokens_per_sec": 1605.26,
    "history": [
      {
        "step": 1,
        "total_steps": 13,
        "epoch": 1,
        "loss": 7.530920028686523,
        "lr": 2.9999999999999997e-05,
        "tokens_seen": 2048,
        "tokens_per_sec": 1581.13,
        "samples_seen": 16,
        "total_samples": 195,
        "elapsed_sec": 1.3,
        "eta_sec": 15.54,
        "rank": 0,
        "world_size": 1
      },
      {
        "step": 2,
        "total_steps": 13,
        "epoch": 1,
        "loss": 7.573794841766357,
        "lr": 4.4999999999999996e-05,
        "tokens_seen": 4096,
        "tokens_per_sec": 1743.49,
        "samples_seen": 32,
        "total_samples": 195,
        "elapsed_sec": 2.35,
        "eta_sec": 12.92,
        "rank": 0,
        "world_size": 1
      },
      {
        "step": 3,
        "total_steps": 13,
        "epoch": 1,
        "loss": 7.536900520324707,
        "lr": 5.9999999999999995e-05,
        "tokens_seen": 6144,
        "tokens_per_sec": 1665.7,
        "samples_seen": 48,
        "total_samples": 195,
        "elapsed_sec": 3.69,
        "eta_sec": 12.3,
        "rank": 0,
        "world_size": 1
      },
      {
        "step": 4,
        "total_steps": 13,
        "epoch": 1,
        "loss": 7.3177103996276855,
        "lr": 7.5e-05,
        "tokens_seen": 8192,
        "tokens_per_sec": 1697.2,
        "samples_seen": 64,
        "total_samples": 195,
        "elapsed_sec": 4.83,
        "eta_sec": 10.86,
        "rank": 0,
        "world_size": 1
      },
      {
        "step": 5,
        "total_steps": 13,
        "epoch": 1,
        "loss": 7.579038143157959,
        "lr": 8.999999999999999e-05,
        "tokens_seen": 10240,
        "tokens_per_sec": 1696.8,
        "samples_seen": 80,
        "total_samples": 195,
        "elapsed_sec": 6.03,
        "eta_sec": 9.66,
        "rank": 0,
        "world_size": 1
      },
      {
        "step": 6,
        "total_steps": 13,
        "epoch": 1,
        "loss": 7.777761459350586,
        "lr": 0.00010499999999999999,
        "tokens_seen": 12288,
        "tokens_per_sec": 1705.4,
        "samples_seen": 96,
        "total_samples": 195,
        "elapsed_sec": 7.21,
        "eta_sec": 8.41,
        "rank": 0,
        "world_size": 1
      },
      {
        "step": 7,
        "total_steps": 13,
        "epoch": 1,
        "loss": 7.553614616394043,
        "lr": 0.00011999999999999999,
        "tokens_seen": 14336,
        "tokens_per_sec": 1700.86,
        "samples_seen": 112,
        "total_samples": 195,
        "elapsed_sec": 8.43,
        "eta_sec": 7.22,
        "rank": 0,
        "world_size": 1
      },
      {
        "step": 8,
        "total_steps": 13,
        "epoch": 1,
        "loss": 7.676057815551758,