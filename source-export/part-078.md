- **الحجم:** 1317 بايت (1.3 KB)
- **الامتداد:** `.md`

```markdown
# ALI Studio Pro 4.5.5 — Quadro M1000M 2GB / GPU Setup

The P50 profile records a Quadro M1000M with 2GB VRAM and compute capability 5.0. ALI never assumes the full 2GB is free.

## Runtime policy
- Auto: probe CUDA with a real kernel and query current free VRAM.
- Inference: use llama.cpp GGUF with adaptive `n_gpu_layers` when enough VRAM is free.
- Training: use CUDA only when the real CUDA self-test succeeds; otherwise use CPU.
- Shared GPU: lower sequence length / increase gradient accumulation / lower offload layers as free VRAM drops.

## Thresholds used by the project
- >= 1.35GB free: full 24-layer Qwen GGUF offload / seq 256 training profile.
- >= 0.95GB free: half-layer GGUF offload / seq 192 profile.
- >= 0.65GB free: low-layer GGUF offload / seq 128 profile.
- < 0.65GB or unknown occupancy: CPU-safe fallback in Auto.

## Windows setup
1. Run `backend\RUN-GPU-DOCTOR.bat`.
2. Run `scripts\SETUP_QWEN_LOCAL.bat` to install Qwen GGUF + llama.cpp locally.
3. Run `scripts\VERIFY_ALL.bat`.
4. Select `Auto (Smart)` in the top bar.

## Important
The repository includes exact download/verification scripts, but this Linux build environment cannot download the 398MB Qwen GGUF or execute Windows CUDA/ConPTY tests. The Windows release host must run the setup scripts and final native verification.
```

---

### `508/588` `GPU_MAXWELL_SETUP_4.5.6.md`

- **المسار الكامل:** `F:\1f\p\ALI_Studio_Pro_Design4_4.6.0\04_Adaptive_Hybrid\GPU_MAXWELL_SETUP_4.5.6.md`
- **الحجم:** 1317 بايت (1.3 KB)
- **الامتداد:** `.md`

```markdown
# ALI Studio Pro 4.5.6 — Quadro M1000M 2GB / GPU Setup

The P50 profile records a Quadro M1000M with 2GB VRAM and compute capability 5.0. ALI never assumes the full 2GB is free.

## Runtime policy
- Auto: probe CUDA with a real kernel and query current free VRAM.
- Inference: use llama.cpp GGUF with adaptive `n_gpu_layers` when enough VRAM is free.
- Training: use CUDA only when the real CUDA self-test succeeds; otherwise use CPU.
- Shared GPU: lower sequence length / increase gradient accumulation / lower offload layers as free VRAM drops.

## Thresholds used by the project
- >= 1.35GB free: full 24-layer Qwen GGUF offload / seq 256 training profile.
- >= 0.95GB free: half-layer GGUF offload / seq 192 profile.
- >= 0.65GB free: low-layer GGUF offload / seq 128 profile.
- < 0.65GB or unknown occupancy: CPU-safe fallback in Auto.

## Windows setup
1. Run `backend\RUN-GPU-DOCTOR.bat`.
2. Run `scripts\SETUP_QWEN_LOCAL.bat` to install Qwen GGUF + llama.cpp locally.
3. Run `scripts\VERIFY_ALL.bat`.
4. Select `Auto (Smart)` in the top bar.

## Important
The repository includes exact download/verification scripts, but this Linux build environment cannot download the 398MB Qwen GGUF or execute Windows CUDA/ConPTY tests. The Windows release host must run the setup scripts and final native verification.
```

---

### `509/588` `GPU_MAXWELL_SETUP_4.5.7.md`

- **المسار الكامل:** `F:\1f\p\ALI_Studio_Pro_Design4_4.6.0\04_Adaptive_Hybrid\GPU_MAXWELL_SETUP_4.5.7.md`
- **الحجم:** 1317 بايت (1.3 KB)
- **الامتداد:** `.md`

```markdown
# ALI Studio Pro 4.5.7 — Quadro M1000M 2GB / GPU Setup

The P50 profile records a Quadro M1000M with 2GB VRAM and compute capability 5.0. ALI never assumes the full 2GB is free.

## Runtime policy
- Auto: probe CUDA with a real kernel and query current free VRAM.
- Inference: use llama.cpp GGUF with adaptive `n_gpu_layers` when enough VRAM is free.
- Training: use CUDA only when the real CUDA self-test succeeds; otherwise use CPU.
- Shared GPU: lower sequence length / increase gradient accumulation / lower offload layers as free VRAM drops.

## Thresholds used by the project
- >= 1.35GB free: full 24-layer Qwen GGUF offload / seq 256 training profile.
- >= 0.95GB free: half-layer GGUF offload / seq 192 profile.
- >= 0.65GB free: low-layer GGUF offload / seq 128 profile.
- < 0.65GB or unknown occupancy: CPU-safe fallback in Auto.

## Windows setup
1. Run `backend\RUN-GPU-DOCTOR.bat`.
2. Run `scripts\SETUP_QWEN_LOCAL.bat` to install Qwen GGUF + llama.cpp locally.
3. Run `scripts\VERIFY_ALL.bat`.
4. Select `Auto (Smart)` in the top bar.

## Important
The repository includes exact download/verification scripts, but this Linux build environment cannot download the 398MB Qwen GGUF or execute Windows CUDA/ConPTY tests. The Windows release host must run the setup scripts and final native verification.
```

---

### `510/588` `INSTALL_TRAINING_UPDATE_V1.bat`

- **المسار الكامل:** `F:\1f\p\ALI_Studio_Pro_Design4_4.6.0\04_Adaptive_Hybrid\INSTALL_TRAINING_UPDATE_V1.bat`
- **الحجم:** 503 بايت (0.5 KB)
- **الامتداد:** `.bat`

```batch
@echo off
setlocal
cd /d "%~dp0"
set "PY=%~dp0runtime\python\python.exe"
if not exist "%PY%" set "PY=py -3.11"
if not exist "%~dp0backend\models\models.sqlite3" (
  echo [ERROR] ALI backend was not found.
  exit /b 1
)
echo [ALI] Installing Training Update v1 as Candidate...
%PY% "%~dp0backend\training\updates\v1\install_update_v1.py" "%~dp0"
if errorlevel 1 (
  echo [ERROR] Update installation failed.
  exit /b 1
)
echo [OK] v1 is installed as a Candidate. It was not promoted automatically.
pause
```

---

### `511/588` `launcher/README.md`

- **المسار الكامل:** `F:\1f\p\ALI_Studio_Pro_Design4_4.6.0\04_Adaptive_Hybrid\launcher/README.md`
- **الحجم:** 230 بايت (0.2 KB)
- **الامتداد:** `.md`

```markdown
# ALI Portable Launcher 4.2.0

The launcher is intentionally small and independent from the AI engine. It verifies the portable layout, records a local launcher log, and starts the packaged Electron application.

Expected layout:
```

---

### `512/588` `models/runs/20261006-142710-7225c1/checkpoints/final-000060/hf/ali_metadata.json`

- **المسار الكامل:** `F:\1f\p\ALI_Studio_Pro_Design4_4.6.0\04_Adaptive_Hybrid\models/runs/20261006-142710-7225c1/checkpoints/final-000060/hf/ali_metadata.json`
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

### `513/588` `models/runs/20261006-142710-7225c1/checkpoints/final-000060/hf/config.json`

- **المسار الكامل:** `F:\1f\p\ALI_Studio_Pro_Design4_4.6.0\04_Adaptive_Hybrid\models/runs/20261006-142710-7225c1/checkpoints/final-000060/hf/config.json`
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

### `514/588` `models/runs/20261006-142710-7225c1/checkpoints/final-000060/hf/manifest.json`

- **المسار الكامل:** `F:\1f\p\ALI_Studio_Pro_Design4_4.6.0\04_Adaptive_Hybrid\models/runs/20261006-142710-7225c1/checkpoints/final-000060/hf/manifest.json`
- **الحجم:** 2401 بايت (2.3 KB)
- **الامتداد:** `.json`

```json
{
  "artifact_id": "ALI:hf:20261006-142710-7225c1",
  "artifact_type": "base",
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
    "base_checkpoint": "",
    "dataset_hash": "90f96c89541770624c60f416a1ce02f42dc9557c11dd5e06737219f32878cdcd",
    "stage": "base",
    "tokenizer_hash": "855ec73474675763ea2f2f3ebf1e3c6b63d99ad25fa205a15d192aa3ae4848de"
  },
  "metadata": {
    "run_id": "20261006-142710-7225c1",
    "stage": "base"
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
  "version": "20261006-142710-7225c1"
}
```

---

### `515/588` `models/runs/20261006-142710-7225c1/checkpoints/final-000060/hf/special_tokens_map.json`

- **المسار الكامل:** `F:\1f\p\ALI_Studio_Pro_Design4_4.6.0\04_Adaptive_Hybrid\models/runs/20261006-142710-7225c1/checkpoints/final-000060/hf/special_tokens_map.json`
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

### `516/588` `models/runs/20261006-142710-7225c1/checkpoints/final-000060/hf/tokenizer_config.json`

- **المسار الكامل:** `F:\1f\p\ALI_Studio_Pro_Design4_4.6.0\04_Adaptive_Hybrid\models/runs/20261006-142710-7225c1/checkpoints/final-000060/hf/tokenizer_config.json`
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

### `517/588` `models/runs/20261006-142710-7225c1/checkpoints/final-000060/manifest.json`

- **المسار الكامل:** `F:\1f\p\ALI_Studio_Pro_Design4_4.6.0\04_Adaptive_Hybrid\models/runs/20261006-142710-7225c1/checkpoints/final-000060/manifest.json`
- **الحجم:** 11626 بايت (11.4 KB)
- **الامتداد:** `.json`

```json
{
  "artifact_id": "ALI:candidate:20261006-142710-7225c1",
  "artifact_type": "base",
  "compatibility": {
    "adapter_dir": "",
    "hf_dir": "models/runs/20261006-142710-7225c1/checkpoints/final-000060/hf",
    "merged_hf_dir": ""
  },
  "created_at": 1791296850.4251153,
  "evaluation": {
    "loss": 6.969683837890625,
    "perplexity": 1063.8863368118753,
    "samples": 60
  },
  "files": [
    {
      "path": "checkpoint.pt",
      "sha256": "e8611c51521616fdb04f435b3ff6679f222fcdc5896f7806add3e3cef629a30a",
      "size": 37833646
    },
    {
      "path": "hf/ali_metadata.json",
      "sha256": "098fd4176e1aace95c065b1ab0881ce1b922fd4f5ca3c67570fcf5cfc8a690d2",
      "size": 9088
    },
    {
      "path": "hf/config.json",
      "sha256": "7e47fcdb9da0c7d230e1b0727f7656c584f1da876d2812e00469677d0fa8ffda",
      "size": 559
    },
    {
      "path": "hf/model.safetensors",
      "sha256": "2a19ae517fbc3c171d24dc56f80de161baf403231709944668dce4491a515f82",
      "size": 12594064
    },
    {
      "path": "hf/special_tokens_map.json",
      "sha256": "1bd43fafc5dc9b132a08feb83487bb41bf5f53bcf89a15b0aa782d148e78dac2",
      "size": 202
    },
    {
      "path": "hf/tokenizer.model",
      "sha256": "3d9d560cbcc0a73ce6db8a89a5c290bbe63d7288cacbd6ce5707df4de8e9f776",
      "size": 274994
    },
    {
      "path": "hf/tokenizer_config.json",
      "sha256": "9354c9e340899300c7a6ff94eb0dc271fe37a4d254e00dfd66785d4000873b92",
      "size": 313
    },
    {
      "path": "model.safetensors",
      "sha256": "3e73251d9cf4f4ddb7cabebaf8021405ee320a90be1d174c00f16c88446dbc4c",
      "size": 12593808
    },
    {
      "path": "trainer_state.json",
      "sha256": "0e085f6074d074bb63f671769be3f6a511782a8217f803ae09058785f3274464",
      "size": 876
    }
  ],
  "lineage": {
    "base_checkpoint": "",
    "dataset_hash": "90f96c89541770624c60f416a1ce02f42dc9557c11dd5e06737219f32878cdcd",
    "resume_checkpoint": "",
    "scale": "micro",
    "stage": "base",
    "tokenizer_hash": "855ec73474675763ea2f2f3ebf1e3c6b63d99ad25fa205a15d192aa3ae4848de"
  },
  "metadata": {
    "result": {
      "best_val": 6.6361991246541345,
      "checkpoint": "models/runs/20261006-142710-7225c1/checkpoints/final-000060",
      "global_step": 60,
      "history": [
        {
          "elapsed_sec": 12.21,
          "epoch": 1,
          "eta_sec": 5.66,
          "loss": 6.141725063323975,
          "lr": 0.00013823113564082325,
          "rank": 0,
          "samples_seen": 328,
          "step": 41,
          "tokens_per_sec": 2106.4,
          "tokens_seen": 25728,
          "total_samples": 1532,
          "total_steps": 60,
          "world_size": 1
        },
        {
          "elapsed_sec": 12.49,
          "epoch": 1,
          "eta_sec": 5.35,
          "loss": 6.213365077972412,
          "lr": 0.00012653483024396533,
          "rank": 0,
          "samples_seen": 336,
          "step": 42,
          "tokens_per_sec": 2109.75,
          "tokens_seen": 26361,
          "total_samples": 1532,
          "total_steps": 60,
          "world_size": 1
        },
        {
          "elapsed_sec": 12.74,
          "epoch": 1,
          "eta_sec": 5.04,
          "loss": 5.775788307189941,
          "lr": 0.00011498319542161423,
          "rank": 0,
          "samples_seen": 344,
          "step": 43,
          "tokens_per_sec": 2103.96,
          "tokens_seen": 26804,
          "total_samples": 1532,
          "total_steps": 60,
          "world_size": 1
        },
        {
          "elapsed_sec": 13.03,
          "epoch": 1,
          "eta_sec": 4.74,
          "loss": 6.631865978240967,
          "lr": 0.0001036474508437579,
          "rank": 0,
          "samples_seen": 352,
          "step": 44,
          "tokens_per_sec": 2108.97,
          "tokens_seen": 27487,
          "total_samples": 1532,
          "total_steps": 60,
          "world_size": 1
        },
        {
          "elapsed_sec": 13.29,
          "epoch": 1,
          "eta_sec": 4.43,
          "loss": 6.223092555999756,
          "lr": 9.259748514523653e-05,
          "rank": 0,
          "samples_seen": 360,
          "step": 45,
          "tokens_per_sec": 2108.06,
          "tokens_seen": 28014,
          "total_samples": 1532,
          "total_steps": 60,
          "world_size": 1
        },
        {
          "elapsed_sec": 13.57,
          "epoch": 1,
          "eta_sec": 4.13,
          "loss": 5.998691558837891,
          "lr": 8.190142503906798e-05,
          "rank": 0,
          "samples_seen": 368,
          "step": 46,
          "tokens_per_sec": 2110.31,
          "tokens_seen": 28645,
          "total_samples": 1532,
          "total_steps": 60,
          "world_size": 1
        },
        {
          "elapsed_sec": 13.82,
          "epoch": 1,
          "eta_sec": 3.82,
          "loss": 6.3459272384643555,
          "lr": 7.162521529260767e-05,
          "rank": 0,
          "samples_seen": 376,
          "step": 47,
          "tokens_per_sec": 2105.42,
          "tokens_seen": 29098,
          "total_samples": 1532,
          "total_steps": 60,
          "world_size": 1
        },
        {
          "elapsed_sec": 14.13,
          "epoch": 1,
          "eta_sec": 3.53,
          "loss": 6.283822059631348,
          "lr": 6.183221215612904e-05,
          "rank": 0,
          "samples_seen": 384,
          "step": 48,
          "tokens_per_sec": 2107.4,
          "tokens_seen": 29785,
          "total_samples": 1532,
          "total_steps": 60,
          "world_size": 1
        },
        {
          "elapsed_sec": 14.44,
          "epoch": 1,
          "eta_sec": 3.24,
          "loss": 6.194177627563477,
          "lr": 5.2582792750472464e-05,
          "rank": 0,
          "samples_seen": 392,
          "step": 49,
          "tokens_per_sec": 2112.43,
          "tokens_seen": 30513,
          "total_samples": 1532,
          "total_steps": 60,
          "world_size": 1
        },
        {
          "elapsed_sec": 14.7,
          "epoch": 1,
          "eta_sec": 2.94,
          "loss": 6.3557634353637695,
          "lr": 4.3933982822017876e-05,
          "rank": 0,
          "samples_seen": 400,
          "step": 50,
          "tokens_per_sec": 2111.58,
          "tokens_seen": 31035,
          "total_samples": 1532,
          "total_steps": 60,
          "world_size": 1
        },
        {
          "elapsed_sec": 14.95,
          "epoch": 1,
          "eta_sec": 2.64,
          "loss": 6.226706504821777,
          "lr": 3.593910515999536e-05,
          "rank": 0,
          "samples_seen": 408,
          "step": 51,
          "tokens_per_sec": 2111.7,
          "tokens_seen": 31570,
          "total_samples": 1532,
          "total_steps": 60,
          "world_size": 1
        },
        {
          "elapsed_sec": 15.28,
          "epoch": 1,
          "eta_sec": 2.35,
          "loss": 6.0981268882751465,
          "lr": 2.8647450843757897e-05,
          "rank": 0,
          "samples_seen": 416,
          "step": 52,
          "tokens_per_sec": 2115.79,
          "tokens_seen": 32322,
          "total_samples": 1532,
          "total_steps": 60,
          "world_size": 1
        },
        {
          "elapsed_sec": 15.55,
          "epoch": 1,
          "eta_sec": 2.05,
          "loss": 6.139437198638916,
          "lr": 2.210397534688617e-05,
          "rank": 0,
          "samples_seen": 424,
          "step": 53,
          "tokens_per_sec": 2114.37,
          "tokens_seen": 32879,
          "total_samples": 1532,
          "total_steps": 60,
          "world_size": 1
        },
        {
          "elapsed_sec": 15.85,
          "epoch": 1,
          "eta_sec": 1.76,
          "loss": 6.279908180236816,
          "lr": 1.634902137174483e-05,
          "rank": 0,
          "samples_seen": 432,
          "step": 54,
          "tokens_per_sec": 2116.67,
          "tokens_seen": 33541,
          "total_samples": 1532,
          "total_steps": 60,
          "world_size": 1
        },
        {
          "elapsed_sec": 16.15,
          "epoch": 1,
          "eta_sec": 1.47,
          "loss": 6.39638090133667,
          "lr": 1.1418070123306989e-05,
          "rank": 0,
          "samples_seen": 440,
          "step": 55,
          "tokens_per_sec": 2118.9,
          "tokens_seen": 34220,
          "total_samples": 1532,
          "total_steps": 60,
          "world_size": 1
        },
        {
          "elapsed_sec": 16.47,
          "epoch": 1,
          "eta_sec": 1.18,
          "loss": 6.225327968597412,
          "lr": 7.34152255572697e-06,
          "rank": 0,
          "samples_seen": 448,
          "step": 56,
          "tokens_per_sec": 2120.81,
          "tokens_seen": 34931,
          "total_samples": 1532,
          "total_steps": 60,
          "world_size": 1