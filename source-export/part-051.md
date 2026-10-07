  "manifests/lineage.json": "a9e672a066bbc17223fda16e954bc165b3233cbdbf90a8aeb18e7dadd930cb8c",
  "model/ALI-v4/ali_metadata.json": "098fd4176e1aace95c065b1ab0881ce1b922fd4f5ca3c67570fcf5cfc8a690d2",
  "model/ALI-v4/config.json": "7e47fcdb9da0c7d230e1b0727f7656c584f1da876d2812e00469677d0fa8ffda",
  "model/ALI-v4/manifest.json": "f5b54755025381c127a93eaed71714e5fffb1c92e1b3caf2ba5c0db313ace31b",
  "model/ALI-v4/model.safetensors": "2a19ae517fbc3c171d24dc56f80de161baf403231709944668dce4491a515f82",
  "model/ALI-v4/special_tokens_map.json": "1bd43fafc5dc9b132a08feb83487bb41bf5f53bcf89a15b0aa782d148e78dac2",
  "model/ALI-v4/tokenizer.model": "3d9d560cbcc0a73ce6db8a89a5c290bbe63d7288cacbd6ce5707df4de8e9f776",
  "model/ALI-v4/tokenizer_config.json": "9354c9e340899300c7a6ff94eb0dc271fe37a4d254e00dfd66785d4000873b92"
}
```

---

### `295/588` `backend/releases/ALI-v4-Package/manifests/generation.json`

- **المسار الكامل:** `F:\1f\p\ALI_Studio_Pro_Design4_4.6.0\04_Adaptive_Hybrid\backend/releases/ALI-v4-Package/manifests/generation.json`
- **الحجم:** 855 بايت (0.8 KB)
- **الامتداد:** `.json`

```json
{
  "schema_version": 2,
  "generation": "v4",
  "parent_generation": "v3",
  "ancestors": [
    "v1",
    "v2",
    "v3"
  ],
  "delta_dataset": {
    "path": "models/generations/v4/delta/train.jsonl",
    "sha256": "afe6e3feb0d5e3f6f06c5266873fb65b460226308f0cff9b1eafb991eecf2fd3",
    "samples": 84
  },
  "cumulative_dataset": {
    "path": "models/generations/v4/cumulative/train.jsonl",
    "sha256": "90f96c89541770624c60f416a1ce02f42dc9557c11dd5e06737219f32878cdcd",
    "samples": 1532
  },
  "historical_model_status": "not_reconstructed_from_missing_binary_weights",
  "created_at": 1791296618.2290323,
  "status": "active",
  "artifacts": {
    "merged_hf": "models/active/ALI-v4",
    "checkpoint": "models/active/ALI-v4",
    "adapter": "",
    "gguf_f16": "",
    "gguf_q4_k_m": ""
  },
  "gguf": {
    "status": "pending_converter"
  }
}
```

---

### `296/588` `backend/releases/ALI-v4-Package/manifests/lineage.json`

- **المسار الكامل:** `F:\1f\p\ALI_Studio_Pro_Design4_4.6.0\04_Adaptive_Hybrid\backend/releases/ALI-v4-Package/manifests/lineage.json`
- **الحجم:** 928 بايت (0.9 KB)
- **الامتداد:** `.json`

```json
{
  "schema_version": 2,
  "generation": "v4",
  "parent_generation": "v3",
  "ancestors": [
    "v1",
    "v2",
    "v3"
  ],
  "historical_model_status": "not_reconstructed_from_missing_binary_weights",
  "delta_dataset": {
    "path": "models/generations/v4/delta/train.jsonl",
    "sha256": "afe6e3feb0d5e3f6f06c5266873fb65b460226308f0cff9b1eafb991eecf2fd3",
    "samples": 84
  },
  "cumulative_dataset": {
    "path": "models/generations/v4/cumulative/train.jsonl",
    "sha256": "90f96c89541770624c60f416a1ce02f42dc9557c11dd5e06737219f32878cdcd",
    "samples": 1532
  },
  "parent_model": {
    "generation": "v3",
    "available_in_source_bundle": false
  },
  "final_model": {
    "hf_dir": "models/active/ALI-v4",
    "sha256": "aa12180223a7e1e542b1fd1d7e479f9ac092c0a0678c1f4c227145bd887dd1dc"
  },
  "gguf": {
    "status": "pending_converter",
    "reason": "Windows llama.cpp converter binary not included"
  }
}
```

---

### `297/588` `backend/releases/ALI-v4-Package/model/ALI-v4/ali_metadata.json`

- **المسار الكامل:** `F:\1f\p\ALI_Studio_Pro_Design4_4.6.0\04_Adaptive_Hybrid\backend/releases/ALI-v4-Package/model/ALI-v4/ali_metadata.json`
- **الحجم:** 9088 بايت (8.9 KB)
- **الامتداد:** `.json`

```json
{
  "run_id": "20261006-142710-7225c1",
  "stage": "base",
  "dataset_hash": "90f96c89541770624c60f416a1ce02f42dc9557c11dd5e06737219f32878cdcd",
  "tokenizer_hash": "855ec73474675763ea2f2f3ebf1e3c6b63d99ad25fa205a15d192aa3ae4848de",
  "pipeline_config": {
    "name": "ALI",
    "stage": "base",
    "scale": "micro",
    "train_path": "/mnt/data/ALI_Studio_Pro_Windows_v4.5.8_CUMULATIVE/project/backend/models/generations/v4/cumulative/train.jsonl",
    "validation_path": "/mnt/data/ALI_Studio_Pro_Windows_v4.5.8_CUMULATIVE/project/backend/models/generations/v4/evaluation/diagnostic_validation.jsonl",
    "tokenizer_inputs": null,
    "tokenizer_vocab_size": 2048,
    "base_checkpoint": "",
    "resume_checkpoint": "",
    "max_steps": 60,
    "epochs": 1,
    "max_seq_len": 128,
    "batch_size": 1,
    "grad_accum": 8,
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
  "kca_registry_hash": null,
  "result": {
    "checkpoint": "models/runs/20261006-142710-7225c1/checkpoints/final-000060",
    "global_step": 60,
    "steps": 60,
    "loss": 6.3332366943359375,
    "val_loss": 6.6361991246541345,
    "best_val": 6.6361991246541345,
    "tokens_seen": 37283,
    "tokens_per_sec": 2029.92,
    "history": [
      {
        "step": 41,
        "total_steps": 60,
        "epoch": 1,
        "loss": 6.141725063323975,
        "lr": 0.00013823113564082325,
        "tokens_seen": 25728,
        "tokens_per_sec": 2106.4,
        "samples_seen": 328,
        "total_samples": 1532,
        "elapsed_sec": 12.21,
        "eta_sec": 5.66,
        "rank": 0,
        "world_size": 1
      },
      {
        "step": 42,
        "total_steps": 60,
        "epoch": 1,
        "loss": 6.213365077972412,
        "lr": 0.00012653483024396533,
        "tokens_seen": 26361,
        "tokens_per_sec": 2109.75,
        "samples_seen": 336,
        "total_samples": 1532,
        "elapsed_sec": 12.49,
        "eta_sec": 5.35,
        "rank": 0,
        "world_size": 1
      },
      {
        "step": 43,
        "total_steps": 60,
        "epoch": 1,
        "loss": 5.775788307189941,
        "lr": 0.00011498319542161423,
        "tokens_seen": 26804,
        "tokens_per_sec": 2103.96,
        "samples_seen": 344,
        "total_samples": 1532,
        "elapsed_sec": 12.74,
        "eta_sec": 5.04,
        "rank": 0,
        "world_size": 1
      },
      {
        "step": 44,
        "total_steps": 60,
        "epoch": 1,
        "loss": 6.631865978240967,
        "lr": 0.0001036474508437579,
        "tokens_seen": 27487,
        "tokens_per_sec": 2108.97,
        "samples_seen": 352,
        "total_samples": 1532,
        "elapsed_sec": 13.03,
        "eta_sec": 4.74,
        "rank": 0,
        "world_size": 1
      },
      {
        "step": 45,
        "total_steps": 60,
        "epoch": 1,
        "loss": 6.223092555999756,
        "lr": 9.259748514523653e-05,
        "tokens_seen": 28014,
        "tokens_per_sec": 2108.06,
        "samples_seen": 360,
        "total_samples": 1532,
        "elapsed_sec": 13.29,
        "eta_sec": 4.43,
        "rank": 0,
        "world_size": 1
      },
      {
        "step": 46,
        "total_steps": 60,
        "epoch": 1,
        "loss": 5.998691558837891,
        "lr": 8.190142503906798e-05,
        "tokens_seen": 28645,
        "tokens_per_sec": 2110.31,
        "samples_seen": 368,
        "total_samples": 1532,
        "elapsed_sec": 13.57,
        "eta_sec": 4.13,
        "rank": 0,
        "world_size": 1
      },
      {
        "step": 47,
        "total_steps": 60,
        "epoch": 1,
        "loss": 6.3459272384643555,
        "lr": 7.162521529260767e-05,
        "tokens_seen": 29098,
        "tokens_per_sec": 2105.42,
        "samples_seen": 376,
        "total_samples": 1532,
        "elapsed_sec": 13.82,
        "eta_sec": 3.82,
        "rank": 0,
        "world_size": 1
      },
      {
        "step": 48,
        "total_steps": 60,
        "epoch": 1,
        "loss": 6.283822059631348,
        "lr": 6.183221215612904e-05,
        "tokens_seen": 29785,
        "tokens_per_sec": 2107.4,
        "samples_seen": 384,
        "total_samples": 1532,
        "elapsed_sec": 14.13,
        "eta_sec": 3.53,
        "rank": 0,
        "world_size": 1
      },
      {
        "step": 49,
        "total_steps": 60,
        "epoch": 1,
        "loss": 6.194177627563477,
        "lr": 5.2582792750472464e-05,
        "tokens_seen": 30513,
        "tokens_per_sec": 2112.43,
        "samples_seen": 392,
        "total_samples": 1532,
        "elapsed_sec": 14.44,
        "eta_sec": 3.24,
        "rank": 0,
        "world_size": 1
      },
      {
        "step": 50,
        "total_steps": 60,
        "epoch": 1,
        "loss": 6.3557634353637695,
        "lr": 4.3933982822017876e-05,
        "tokens_seen": 31035,
        "tokens_per_sec": 2111.58,
        "samples_seen": 400,
        "total_samples": 1532,
        "elapsed_sec": 14.7,
        "eta_sec": 2.94,
        "rank": 0,
        "world_size": 1
      },
      {
        "step": 51,
        "total_steps": 60,
        "epoch": 1,
        "loss": 6.226706504821777,
        "lr": 3.593910515999536e-05,
        "tokens_seen": 31570,
        "tokens_per_sec": 2111.7,
        "samples_seen": 408,
        "total_samples": 1532,
        "elapsed_sec": 14.95,
        "eta_sec": 2.64,
        "rank": 0,
        "world_size": 1
      },
      {
        "step": 52,
        "total_steps": 60,
        "epoch": 1,
        "loss": 6.0981268882751465,
        "lr": 2.8647450843757897e-05,
        "tokens_seen": 32322,
        "tokens_per_sec": 2115.79,
        "samples_seen": 416,
        "total_samples": 1532,
        "elapsed_sec": 15.28,
        "eta_sec": 2.35,
        "rank": 0,
        "world_size": 1
      },
      {
        "step": 53,
        "total_steps": 60,
        "epoch": 1,
        "loss": 6.139437198638916,
        "lr": 2.210397534688617e-05,
        "tokens_seen": 32879,
        "tokens_per_sec": 2114.37,
        "samples_seen": 424,
        "total_samples": 1532,
        "elapsed_sec": 15.55,
        "eta_sec": 2.05,
        "rank": 0,
        "world_size": 1
      },
      {
        "step": 54,
        "total_steps": 60,
        "epoch": 1,
        "loss": 6.279908180236816,
        "lr": 1.634902137174483e-05,
        "tokens_seen": 33541,
        "tokens_per_sec": 2116.67,
        "samples_seen": 432,
        "total_samples": 1532,
        "elapsed_sec": 15.85,
        "eta_sec": 1.76,
        "rank": 0,
        "world_size": 1
      },
      {
        "step": 55,
        "total_steps": 60,
        "epoch": 1,
        "loss": 6.39638090133667,
        "lr": 1.1418070123306989e-05,
        "tokens_seen": 34220,
        "tokens_per_sec": 2118.9,
        "samples_seen": 440,
        "total_samples": 1532,
        "elapsed_sec": 16.15,
        "eta_sec": 1.47,
        "rank": 0,
        "world_size": 1
      },
      {
        "step": 56,
        "total_steps": 60,
        "epoch": 1,
        "loss": 6.225327968597412,
        "lr": 7.34152255572697e-06,
        "tokens_seen": 34931,
        "tokens_per_sec": 2120.81,
        "samples_seen": 448,
        "total_samples": 1532,
        "elapsed_sec": 16.47,
        "eta_sec": 1.18,
        "rank": 0,
        "world_size": 1
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
  "parameter_count": 3147456,
  "source": "ALI Studio trained-from-scratch",
  "architecture": "LlamaForCausalLM"
}
```

---

### `298/588` `backend/releases/ALI-v4-Package/model/ALI-v4/config.json`

- **المسار الكامل:** `F:\1f\p\ALI_Studio_Pro_Design4_4.6.0\04_Adaptive_Hybrid\backend/releases/ALI-v4-Package/model/ALI-v4/config.json`
- **الحجم:** 559 بايت (0.5 KB)
- **الامتداد:** `.json`

```json
{
  "vocab_size": 2048,
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

### `299/588` `backend/releases/ALI-v4-Package/model/ALI-v4/manifest.json`

- **المسار الكامل:** `F:\1f\p\ALI_Studio_Pro_Design4_4.6.0\04_Adaptive_Hybrid\backend/releases/ALI-v4-Package/model/ALI-v4/manifest.json`
- **الحجم:** 2733 بايت (2.7 KB)
- **الامتداد:** `.json`

```json
{
  "artifact_id": "ALI:hf:20261006-142710-7225c1",
  "artifact_type": "model",
  "compatibility": {},
  "created_at": 1791296849.646673,
  "evaluation": {},
  "files": [
    {
      "path": "ali_metadata.json",
      "sha256": "098fd4176e1aace95c065b1ab0881ce1b922fd4f5ca3c67570fcf5cfc8a690d2",
      "size": 9088
    },
    {
      "path": "config.json",
      "sha256": "7e47fcdb9da0c7d230e1b0727f7656c584f1da876d2812e00469677d0fa8ffda",
      "size": 559
    },
    {
      "path": "model.safetensors",
      "sha256": "2a19ae517fbc3c171d24dc56f80de161baf403231709944668dce4491a515f82",
      "size": 12594064
    },
    {
      "path": "special_tokens_map.json",
      "sha256": "1bd43fafc5dc9b132a08feb83487bb41bf5f53bcf89a15b0aa782d148e78dac2",
      "size": 202
    },
    {
      "path": "tokenizer.model",
      "sha256": "3d9d560cbcc0a73ce6db8a89a5c290bbe63d7288cacbd6ce5707df4de8e9f776",
      "size": 274994
    },
    {
      "path": "tokenizer_config.json",
      "sha256": "9354c9e340899300c7a6ff94eb0dc271fe37a4d254e00dfd66785d4000873b92",
      "size": 313
    }
  ],
  "lineage": {
    "generation": "v4",
    "parent_generation": "v3",
    "ancestors": [
      "v1",
      "v2",
      "v3"
    ],
    "base_checkpoint": "models/active/ALI-v4",
    "delta_dataset_hash": "afe6e3feb0d5e3f6f06c5266873fb65b460226308f0cff9b1eafb991eecf2fd3",
    "cumulative_dataset_hash": "90f96c89541770624c60f416a1ce02f42dc9557c11dd5e06737219f32878cdcd",
    "cumulative_sample_count": 1532,
    "tokenizer_hash": "855ec73474675763ea2f2f3ebf1e3c6b63d99ad25fa205a15d192aa3ae4848de"
  },
  "metadata": {
    "run_id": "20261006-142710-7225c1",
    "stage": "base",
    "generation": "v4",
    "parent_generation": "v3",
    "release": "ALI-4.6.0-cumulative"
  },
  "name": "ALI",
  "path": "/mnt/data/ALI_Studio_Pro_Windows_v4.5.8_CUMULATIVE/project/models/runs/20261006-142710-7225c1/checkpoints/final-000060/hf",
  "schema_version": 2,
  "sha256": "7dabe9015700a199b883c4d808c2f035b8d158f383de7c144c1eaa6c47eb3195",
  "source": "training-export",
  "training": {
    "amp": true,
    "batch_size": 1,
    "cpu_amp": false,
    "cpu_threads": 0,
    "curriculum": true,
    "dataset_mode": "causal",
    "device": "cpu",
    "distributed_backend": "auto",
    "dtype": "float16",
    "epochs": 1,
    "eval_every": 100,
    "grad_accum": 8,
    "gradient_checkpointing": true,
    "learning_rate": 0.0003,
    "lora_alpha": 16.0,
    "lora_dropout": 0.05,
    "lora_rank": 8,
    "max_grad_norm": 1.0,
    "max_seq_len": 128,
    "max_steps": 60,
    "save_every": 100,
    "seed": 42,
    "train_mode": "full",
    "use_compile": false,
    "warmup_steps": 20,
    "weight_decay": 0.1,
    "world_size": 1
  },
  "version": "v4"
}
```

---

### `300/588` `backend/releases/ALI-v4-Package/model/ALI-v4/special_tokens_map.json`

- **المسار الكامل:** `F:\1f\p\ALI_Studio_Pro_Design4_4.6.0\04_Adaptive_Hybrid\backend/releases/ALI-v4-Package/model/ALI-v4/special_tokens_map.json`
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

### `301/588` `backend/releases/ALI-v4-Package/model/ALI-v4/tokenizer_config.json`

- **المسار الكامل:** `F:\1f\p\ALI_Studio_Pro_Design4_4.6.0\04_Adaptive_Hybrid\backend/releases/ALI-v4-Package/model/ALI-v4/tokenizer_config.json`
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

### `302/588` `backend/releases/ALI-v4-Package/README.md`

- **المسار الكامل:** `F:\1f\p\ALI_Studio_Pro_Design4_4.6.0\04_Adaptive_Hybrid\backend/releases/ALI-v4-Package/README.md`
- **الحجم:** 158 بايت (0.2 KB)
- **الامتداد:** `.md`

```markdown
# ALI v4 Package

Independent ALI generation package.

Generation: v4
Parent: v3
Cumulative samples: 1532

Archived generations are not runtime dependencies.
```

---

### `303/588` `backend/REPAIR-WINDOWS-DEPS.bat`

- **المسار الكامل:** `F:\1f\p\ALI_Studio_Pro_Design4_4.6.0\04_Adaptive_Hybrid\backend/REPAIR-WINDOWS-DEPS.bat`
- **الحجم:** 283 بايت (0.3 KB)
- **الامتداد:** `.bat`

```batch
@echo off
setlocal EnableExtensions
chcp 65001 >nul
cd /d "%~dp0"
echo ============================================================
echo ALI AI - Repair missing Python dependencies
echo ============================================================
call SETUP.bat
exit /b %errorlevel%
```

---

### `304/588` `backend/requirements-core.txt`

- **المسار الكامل:** `F:\1f\p\ALI_Studio_Pro_Design4_4.6.0\04_Adaptive_Hybrid\backend/requirements-core.txt`
- **الحجم:** 188 بايت (0.2 KB)
- **الامتداد:** `.txt`

```text
# ALI AI core — Windows adaptive CPU/GPU
# Keep the core install small and reproducible.
torch==2.14.0
numpy>=2.0,<3
psutil>=7,<8
safetensors>=0.7,<1
sentencepiece>=0.2,<1
pytest>=9,<10
```

---

### `305/588` `backend/requirements-optional-qwen.txt`

- **المسار الكامل:** `F:\1f\p\ALI_Studio_Pro_Design4_4.6.0\04_Adaptive_Hybrid\backend/requirements-optional-qwen.txt`
- **الحجم:** 198 بايت (0.2 KB)
- **الامتداد:** `.txt`

```text
# Optional stronger local base / LoRA training
# The Qwen model card currently requires transformers support for qwen2.
transformers>=4.43.1,<5
peft>=0.12,<2
accelerate>=0.33,<2
safetensors>=0.7,<1
```

---

### `306/588` `backend/requirements-optional.txt`

- **المسار الكامل:** `F:\1f\p\ALI_Studio_Pro_Design4_4.6.0\04_Adaptive_Hybrid\backend/requirements-optional.txt`
- **الحجم:** 184 بايت (0.2 KB)
- **الامتداد:** `.txt`

```text
# Optional document/media ingestion and packaging
PyMuPDF>=1.26
pypdf>=5
python-docx>=1.2
beautifulsoup4>=4.14
lxml>=6
rarfile>=4.2
py7zr>=1
Pillow>=10
pytesseract>=0.3
pyinstaller>=6
```

---

### `307/588` `backend/requirements-windows-legacy-gpu.txt`

- **المسار الكامل:** `F:\1f\p\ALI_Studio_Pro_Design4_4.6.0\04_Adaptive_Hybrid\backend/requirements-windows-legacy-gpu.txt`
- **الحجم:** 262 بايت (0.3 KB)
- **الامتداد:** `.txt`

```text
# NVIDIA Maxwell / legacy CUDA path for ALI Studio Pro on Windows
# PyTorch 2.14.0 is intentionally pinned because later releases may not publish
# prebuilt CUDA wheels supporting Maxwell (sm_50).
--index-url https://download.pytorch.org/whl/cu126
torch==2.14.0
```

---

### `308/588` `backend/requirements-windows.txt`

- **المسار الكامل:** `F:\1f\p\ALI_Studio_Pro_Design4_4.6.0\04_Adaptive_Hybrid\backend/requirements-windows.txt`
- **الحجم:** 158 بايت (0.2 KB)
- **الامتداد:** `.txt`

```text
# ALI Studio Pro 4.5.2 Windows non-PyTorch dependencies
numpy>=2.0,<3
psutil>=7,<8
safetensors>=0.7,<1
sentencepiece>=0.2,<1
pytest>=9,<10
tkinterdnd2==0.6.3
```

---

### `309/588` `backend/requirements.txt`

- **المسار الكامل:** `F:\1f\p\ALI_Studio_Pro_Design4_4.6.0\04_Adaptive_Hybrid\backend/requirements.txt`
- **الحجم:** 171 بايت (0.2 KB)
- **الامتداد:** `.txt`

```text
# Core dependencies used by the ALI AI desktop/training path.
# Optional document/media/packaging dependencies live in requirements-optional.txt.
-r requirements-core.txt
```

---

### `310/588` `backend/research/__init__.py`

- **المسار الكامل:** `F:\1f\p\ALI_Studio_Pro_Design4_4.6.0\04_Adaptive_Hybrid\backend/research/__init__.py`
- **الحجم:** 46 بايت (0.0 KB)
- **الامتداد:** `.py`

```python
from .web import search, fetch_text, research
```

---

### `311/588` `backend/research/downloads.py`

- **المسار الكامل:** `F:\1f\p\ALI_Studio_Pro_Design4_4.6.0\04_Adaptive_Hybrid\backend/research/downloads.py`
- **الحجم:** 1248 بايت (1.2 KB)
- **الامتداد:** `.py`

```python
# -*- coding: utf-8 -*-
"""Safe public download helper. Files are kept in ALI's dedicated downloads directory."""
from __future__ import annotations
from pathlib import Path
from urllib.request import Request, urlopen
import hashlib, json, ssl, time
from research.web import _safe_public_url

def download(url: str, root: str|Path='downloads', max_mb:int=200) -> dict:
    _safe_public_url(url); root=Path(root); root.mkdir(parents=True,exist_ok=True)
    name=Path(url.split('?',1)[0]).name or ('download-'+hashlib.sha256(url.encode()).hexdigest()[:12])
    out=root/name
    req=Request(url,headers={'User-Agent':'ALI-Studio/3.0'})
    h=hashlib.sha256(); total=0
    with urlopen(req,timeout=30,context=ssl.create_default_context()) as r, out.open('wb') as f:
        while True:
            b=r.read(1024*1024)
            if not b: break
            total += len(b)
            if total > max_mb*1024*1024: raise ValueError('download exceeds configured size limit')
            h.update(b); f.write(b)
    meta={'url':url,'path':str(out.resolve()),'sha256':h.hexdigest(),'size':total,'downloaded_at':time.time()}
    out.with_suffix(out.suffix+'.json').write_text(json.dumps(meta,ensure_ascii=False,indent=2),encoding='utf-8')
    return meta
```

---

### `312/588` `backend/research/store.py`

- **المسار الكامل:** `F:\1f\p\ALI_Studio_Pro_Design4_4.6.0\04_Adaptive_Hybrid\backend/research/store.py`
- **الحجم:** 815 بايت (0.8 KB)
- **الامتداد:** `.py`

```python
# -*- coding: utf-8 -*-
from __future__ import annotations
from pathlib import Path
from knowledge.store import KnowledgeStore

def store_documents(store: KnowledgeStore, documents: list[dict], query: str='') -> dict:
    stored=0; skipped=0; rows=[]
    for d in documents or []:
        url=str(d.get('url') or '').strip(); text=str(d.get('text') or '').strip()
        if not text or not url: skipped+=1; continue
        title=str(d.get('title') or url); did=store.add_document(url,title,'web',{'url':url,'query':query,'retrieved_at':__import__('time').time(),'source_type':'web_research','eligible_for_training':False},[text[i:i+1800] for i in range(0,len(text),1800)])
        rows.append({'document_id':did,'url':url,'title':title}); stored+=1
    return {'stored':stored,'skipped':skipped,'documents':rows}
```

---

### `313/588` `backend/research/web.py`

- **المسار الكامل:** `F:\1f\p\ALI_Studio_Pro_Design4_4.6.0\04_Adaptive_Hybrid\backend/research/web.py`
- **الحجم:** 11880 بايت (11.6 KB)
- **الامتداد:** `.py`

```python
# -*- coding: utf-8 -*-
"""Local, source-backed web research for ALI.

The web layer is an internal tool used by the normal chat pipeline. It does not
open a browser window and it never asks a separate UI surface to answer the user.
The result is returned to the same conversation as evidence with source URLs.
"""
from __future__ import annotations

from dataclasses import dataclass, asdict
from html import unescape
from urllib.parse import quote, urlparse, parse_qs, unquote
from urllib.request import Request, urlopen
import ipaddress
import re
import socket
import ssl
from typing import Any


@dataclass
class SearchResult:
    title: str
    url: str
    snippet: str
    source: str
    rank: int = 0

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


UA = "ALI-Studio/4.6 (+local-agent; source-backed-research)"
_EXPLICIT_WEB_RE = re.compile(
    r"(?:ابحث\s+(?:لي\s+)?(?:على|في|عبر)\s*ال(?:إنترنت|انترنت|انترنيت|ويب)|"
    r"ابحث\s+(?:عن|في|عبر)\s+(?:الويب|الإنترنت|انترنت)|"
    r"بحث\s+ويب|web\s+search|search\s+the\s+web|browse\s+the\s+web|"
    r"look\s+it\s+up|online\s+research|internet\s+research)",
    re.I,
)
_CURRENT_RE = re.compile(
    r"(?:اليوم|حالي(?:اً|ا)?|الآن|اخر|آخر|أحدث|حديث(?:ة|ا)?|مؤخر(?:اً|ا)?|حالياً|"
    r"today|now|current|latest|recent|newest|live|this\s+(?:week|month|year)|"
    r"2026|20\d{2})",
    re.I,
)
_WEB_NEGATIVE_RE = re.compile(r"(?:ابحث\s+في\s+(?:الملفات|المشروع|المجلد)|search\s+(?:files|the\s+project))", re.I)


def should_search_web(query: str, *, auto_current: bool = True) -> tuple[bool, str]:
    """Return whether the normal chat pipeline should invoke web research."""
    q = str(query or "").strip()
    if not q or _WEB_NEGATIVE_RE.search(q):
        return False, ""
    if _EXPLICIT_WEB_RE.search(q):
        return True, "explicit_web_request"
    if auto_current and _CURRENT_RE.search(q):
        return True, "freshness_required"
    return False, ""


def clean_query(query: str) -> str:
    q = str(query or "").strip()
    q = _EXPLICIT_WEB_RE.sub(" ", q)
    q = re.sub(r"\s+", " ", q).strip(" .،,؟?\t\n")
    return q or str(query or "").strip()


def _dns_addresses(host: str) -> set[str]:
    out: set[str] = set()
    try:
        for item in socket.getaddrinfo(host, None):
            sockaddr = item[4]
            if sockaddr:
                out.add(str(sockaddr[0]))
    except Exception:
        pass
    return out


def _safe_public_url(url: str) -> None:
    p = urlparse(str(url))
    if p.scheme not in {"http", "https"} or not p.hostname:
        raise ValueError("Only public http(s) URLs are allowed")
    host = p.hostname.lower().rstrip(".")
    if host in {"localhost", "localhost.localdomain"} or host.endswith(".local"):
        raise ValueError("Localhost URL blocked")
    try:
        ip = ipaddress.ip_address(host)
        addresses = {str(ip)}
    except ValueError:
        addresses = _dns_addresses(host)
    for raw in addresses:
        try:
            ip = ipaddress.ip_address(raw)
        except ValueError:
            continue
        if (
            ip.is_private
            or ip.is_loopback
            or ip.is_link_local
            or ip.is_reserved
            or ip.is_multicast
            or ip.is_unspecified
        ):
            raise ValueError("Private/local network URL blocked")


def _fetch(url: str, timeout: int = 15) -> tuple[str, dict[str, str]]:
    _safe_public_url(url)
    req = Request(
        url,
        headers={
            "User-Agent": UA,
            "Accept-Language": "ar,en;q=0.8",
            "Accept": "text/html,application/xhtml+xml,text/plain;q=0.8,*/*;q=0.1",
        },
    )
    ctx = ssl.create_default_context()
    with urlopen(req, timeout=timeout, context=ctx) as response:
        raw = response.read(4_000_000)
        headers = {
            "content_type": str(response.headers.get("Content-Type", "")),
            "charset": str(response.headers.get_content_charset() or "utf-8"),
        }
        return raw.decode(headers["charset"], "replace"), headers


def _strip_html(value: str) -> str:
    text = unescape(re.sub(r"<[^>]+>", " ", str(value or "")))
    text = re.sub(r"\s+", " ", text).strip()