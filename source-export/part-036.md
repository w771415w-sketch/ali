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
  "merged_lora_layers": 28,
  "parameter_count": 3607872,
  "source": "ALI Studio trained-from-scratch",
  "architecture": "LlamaForCausalLM"
}
```

---

### `180/588` `backend/models/active/ALI-v1/config.json`

- **المسار الكامل:** `F:\1f\p\ALI_Studio_Pro_Design4_4.6.0\04_Adaptive_Hybrid\backend/models/active/ALI-v1/config.json`
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

### `181/588` `backend/models/active/ALI-v1/manifest.json`

- **المسار الكامل:** `F:\1f\p\ALI_Studio_Pro_Design4_4.6.0\04_Adaptive_Hybrid\backend/models/active/ALI-v1/manifest.json`
- **الحجم:** 2591 بايت (2.5 KB)
- **الامتداد:** `.json`

```json
{
  "artifact_id": "ALI:merged:20261004-224649-233144",
  "artifact_type": "merged",
  "compatibility": {
    "hf_dir": "models/active/ALI-v1"
  },
  "created_at": 1791154027.609106,
  "evaluation": {
    "loss": 6.771079858144124,
    "perplexity": 872.2532954340983,
    "samples": 60
  },
  "files": [
    {
      "path": "ali_metadata.json",
      "sha256": "c453af4d30522caf926e6c426e3fed5e112ac6719f529014f43cb9007443889d",
      "size": 6530
    },
    {
      "path": "config.json",
      "sha256": "e6e75d9063f2a29514729487b62acba158a2fa80c46c92180b5762b8518df302",
      "size": 559
    },
    {
      "path": "model.safetensors",
      "sha256": "50b9c5ec66a1cd19035d93f969c412cc7fc87922e03b0a557d5d565ab5123eca",
      "size": 14435744
    },
    {
      "path": "special_tokens_map.json",
      "sha256": "1bd43fafc5dc9b132a08feb83487bb41bf5f53bcf89a15b0aa782d148e78dac2",
      "size": 202
    },
    {
      "path": "tokenizer.model",
      "sha256": "5c1ca7b2eb4a855452c133adbdc52d15306ee2dcdf2590cdf78102ba1c5a3d4b",
      "size": 284865
    },
    {
      "path": "tokenizer_config.json",
      "sha256": "9354c9e340899300c7a6ff94eb0dc271fe37a4d254e00dfd66785d4000873b92",
      "size": 313
    }
  ],
  "lineage": {
    "adapter_artifact": "models/runs/ALI-v1-20261004-224649-233144/checkpoints/final-000013/adapter",
    "base_checkpoint": "models/active/ALI-Bootstrap-v2.5",
    "dataset_hash": "406ccb419f45bc20acc61368b41bb3f31451370bcfd8217c2d3d565f114d8a8d",
    "resume_checkpoint": "",
    "scale": "small",
    "stage": "lora",
    "tokenizer_hash": "5e6970f5f6bac2d299df737015ef5006310fe2a153a2d44c6e6f477ed10565e1"
  },
  "metadata": {
    "merged_lora_layers": true
  },
  "name": "ALI",
  "path": "models/active/ALI-v1",
  "schema_version": 2,
  "sha256": "4456b789068250d49c2ca55eb13b2763b97d957f63733323b74cf78b30283a7c",
  "source": "lora-merge",
  "training": {
    "amp": true,
    "batch_size": 1,
    "cpu_amp": false,
    "cpu_threads": 0,
    "curriculum": true,
    "dataset_mode": "chat",
    "device": "cpu",
    "distributed_backend": "auto",
    "dtype": "float16",
    "epochs": 1,
    "eval_every": 100,
    "grad_accum": 16,
    "gradient_checkpointing": true,
    "learning_rate": 0.0003,
    "lora_alpha": 16.0,
    "lora_dropout": 0.05,
    "lora_rank": 8,
    "max_grad_norm": 1.0,
    "max_seq_len": 128,
    "max_steps": 0,
    "save_every": 100,
    "seed": 42,
    "train_mode": "lora",
    "use_compile": false,
    "warmup_steps": 20,
    "weight_decay": 0.1,
    "world_size": 1
  },
  "version": "20261004-224649-233144-merged"
}
```

---

### `182/588` `backend/models/active/ALI-v1/MODEL_CARD.json`

- **المسار الكامل:** `F:\1f\p\ALI_Studio_Pro_Design4_4.6.0\04_Adaptive_Hybrid\backend/models/active/ALI-v1/MODEL_CARD.json`
- **الحجم:** 1361 بايت (1.3 KB)
- **الامتداد:** `.json`

```json
{
  "name": "ALI-v1",
  "artifact_type": "merged",
  "status": "active",
  "base_version": "2.5.0-bootstrap-micro",
  "run_id": "20261004-224649-233144",
  "source_fixture": "backend/data/training/testdata/ALI_User_Understanding_Bundle_V4.md",
  "unique_samples": 215,
  "quiz_questions": 216,
  "quiz_exact_source_answer_match": "216/216",
  "training": {
    "amp": true,
    "batch_size": 1,
    "cpu_amp": false,
    "cpu_threads": 0,
    "curriculum": true,
    "dataset_mode": "chat",
    "device": "cpu",
    "distributed_backend": "auto",
    "dtype": "float16",
    "epochs": 1,
    "eval_every": 100,
    "grad_accum": 16,
    "gradient_checkpointing": true,
    "learning_rate": 0.0003,
    "lora_alpha": 16.0,
    "lora_dropout": 0.05,
    "lora_rank": 8,
    "max_grad_norm": 1.0,
    "max_seq_len": 128,
    "max_steps": 0,
    "save_every": 100,
    "seed": 42,
    "train_mode": "lora",
    "use_compile": false,
    "warmup_steps": 20,
    "weight_decay": 0.1,
    "world_size": 1
  },
  "evaluation": {
    "loss": 6.771079858144124,
    "perplexity": 872.2532954340983,
    "samples": 60
  },
  "merged_lora_layers": true,
  "tokenizer_sha256": "5e6970f5f6bac2d299df737015ef5006310fe2a153a2d44c6e6f477ed10565e1",
  "dataset_hash": "406ccb419f45bc20acc61368b41bb3f31451370bcfd8217c2d3d565f114d8a8d",
  "fallback_model": "ALI-Bootstrap-v2.5"
}
```

---

### `183/588` `backend/models/active/ALI-v1/special_tokens_map.json`

- **المسار الكامل:** `F:\1f\p\ALI_Studio_Pro_Design4_4.6.0\04_Adaptive_Hybrid\backend/models/active/ALI-v1/special_tokens_map.json`
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

### `184/588` `backend/models/active/ALI-v1/tokenizer_config.json`

- **المسار الكامل:** `F:\1f\p\ALI_Studio_Pro_Design4_4.6.0\04_Adaptive_Hybrid\backend/models/active/ALI-v1/tokenizer_config.json`
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

### `185/588` `backend/models/active/ALI-v4/ali_metadata.json`

- **المسار الكامل:** `F:\1f\p\ALI_Studio_Pro_Design4_4.6.0\04_Adaptive_Hybrid\backend/models/active/ALI-v4/ali_metadata.json`
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

### `186/588` `backend/models/active/ALI-v4/config.json`

- **المسار الكامل:** `F:\1f\p\ALI_Studio_Pro_Design4_4.6.0\04_Adaptive_Hybrid\backend/models/active/ALI-v4/config.json`
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

### `187/588` `backend/models/active/ALI-v4/manifest.json`

- **المسار الكامل:** `F:\1f\p\ALI_Studio_Pro_Design4_4.6.0\04_Adaptive_Hybrid\backend/models/active/ALI-v4/manifest.json`
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

### `188/588` `backend/models/active/ALI-v4/special_tokens_map.json`

- **المسار الكامل:** `F:\1f\p\ALI_Studio_Pro_Design4_4.6.0\04_Adaptive_Hybrid\backend/models/active/ALI-v4/special_tokens_map.json`
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

### `189/588` `backend/models/active/ALI-v4/tokenizer_config.json`

- **المسار الكامل:** `F:\1f\p\ALI_Studio_Pro_Design4_4.6.0\04_Adaptive_Hybrid\backend/models/active/ALI-v4/tokenizer_config.json`
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

### `190/588` `backend/models/active/current.json`

- **المسار الكامل:** `F:\1f\p\ALI_Studio_Pro_Design4_4.6.0\04_Adaptive_Hybrid\backend/models/active/current.json`
- **الحجم:** 176 بايت (0.2 KB)
- **الامتداد:** `.json`

```json
{
  "model": "ALI",
  "active_generation": "v4",
  "hf_dir": "models/active/ALI-v4",
  "checkpoint": "models/active/ALI-v4",
  "gguf": "",
  "updated_at": 1791299824.4500115
}
```

---

### `191/588` `backend/models/active/README.md`

- **المسار الكامل:** `F:\1f\p\ALI_Studio_Pro_Design4_4.6.0\04_Adaptive_Hybrid\backend/models/active/README.md`
- **الحجم:** 495 بايت (0.5 KB)
- **الامتداد:** `.md`

```markdown
# Active Models

`ALI-Bootstrap-v2.5/` is the included functional micro checkpoint used for desktop startup, local inference smoke tests and validating the training/registry lifecycle.

It was trained from scratch for a small CPU bootstrap run. It is deliberately labeled as a development bootstrap, not as a production-scale general assistant.

Larger HF/Safetensors or validated GGUF models can be imported through `models/inbox/` and the model manager without changing the application shell.
```

---

### `192/588` `backend/models/adapters/pending/ALI-v1/adapter_config.json`

- **المسار الكامل:** `F:\1f\p\ALI_Studio_Pro_Design4_4.6.0\04_Adaptive_Hybrid\backend/models/adapters/pending/ALI-v1/adapter_config.json`
- **الحجم:** 202 بايت (0.2 KB)
- **الامتداد:** `.json`

```json
{
  "version": "v1",
  "base_version": "2.5.0-bootstrap-micro",
  "rank": 16,
  "alpha": 32.0,
  "learning_rate": 0.0005,
  "max_steps": 200,
  "max_seq_len": 96,
  "dataset": "ALI_training_update_v1"
}
```

---

### `193/588` `backend/models/archive/v1/ARCHIVE_README.md`

- **المسار الكامل:** `F:\1f\p\ALI_Studio_Pro_Design4_4.6.0\04_Adaptive_Hybrid\backend/models/archive/v1/ARCHIVE_README.md`
- **الحجم:** 210 بايت (0.2 KB)
- **الامتداد:** `.md`

```markdown
# ALI v1 archive
