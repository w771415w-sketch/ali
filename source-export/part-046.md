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

### `247/588` `backend/models/runs/ALI-v1-20261004-224649-233144/checkpoints/final-000013/merged_hf/config.json`

- **المسار الكامل:** `F:\1f\p\ALI_Studio_Pro_Design4_4.6.0\04_Adaptive_Hybrid\backend/models/runs/ALI-v1-20261004-224649-233144/checkpoints/final-000013/merged_hf/config.json`
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

### `248/588` `backend/models/runs/ALI-v1-20261004-224649-233144/checkpoints/final-000013/merged_hf/manifest.json`

- **المسار الكامل:** `F:\1f\p\ALI_Studio_Pro_Design4_4.6.0\04_Adaptive_Hybrid\backend/models/runs/ALI-v1-20261004-224649-233144/checkpoints/final-000013/merged_hf/manifest.json`
- **الحجم:** 2802 بايت (2.7 KB)
- **الامتداد:** `.json`

```json
{
  "artifact_id": "ALI:merged:20261004-224649-233144",
  "artifact_type": "merged",
  "compatibility": {
    "hf_dir": "/mnt/data/ali_v457_postfix2_e2e/backend/models/runs/20261004-224649-233144/checkpoints/final-000013/merged_hf"
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
    "adapter_artifact": "/mnt/data/ali_v457_postfix2_e2e/backend/models/runs/20261004-224649-233144/checkpoints/final-000013/adapter",
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
  "path": "/mnt/data/ali_v457_postfix2_e2e/backend/models/runs/20261004-224649-233144/checkpoints/final-000013/merged_hf",
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

### `249/588` `backend/models/runs/ALI-v1-20261004-224649-233144/checkpoints/final-000013/merged_hf/special_tokens_map.json`

- **المسار الكامل:** `F:\1f\p\ALI_Studio_Pro_Design4_4.6.0\04_Adaptive_Hybrid\backend/models/runs/ALI-v1-20261004-224649-233144/checkpoints/final-000013/merged_hf/special_tokens_map.json`
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

### `250/588` `backend/models/runs/ALI-v1-20261004-224649-233144/checkpoints/final-000013/merged_hf/tokenizer_config.json`

- **المسار الكامل:** `F:\1f\p\ALI_Studio_Pro_Design4_4.6.0\04_Adaptive_Hybrid\backend/models/runs/ALI-v1-20261004-224649-233144/checkpoints/final-000013/merged_hf/tokenizer_config.json`
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

### `251/588` `backend/models/runs/ALI-v1-20261004-224649-233144/checkpoints/final-000013/trainer_state.json`

- **المسار الكامل:** `F:\1f\p\ALI_Studio_Pro_Design4_4.6.0\04_Adaptive_Hybrid\backend/models/runs/ALI-v1-20261004-224649-233144/checkpoints/final-000013/trainer_state.json`
- **الحجم:** 871 بايت (0.9 KB)
- **الامتداد:** `.json`

```json
{
  "global_step": 13,
  "micro_step": 208,
  "best_val": 6.771079770723978,
  "tokens_seen": 26624,
  "samples_seen": 208,
  "config": {
    "epochs": 1,
    "batch_size": 1,
    "grad_accum": 16,
    "learning_rate": 0.0003,
    "weight_decay": 0.1,
    "warmup_steps": 20,
    "max_steps": 0,
    "save_every": 100,
    "eval_every": 100,
    "max_seq_len": 128,
    "seed": 42,
    "device": "cpu",
    "gradient_checkpointing": true,
    "max_grad_norm": 1.0,
    "train_mode": "lora",
    "lora_rank": 8,
    "lora_alpha": 16.0,
    "lora_dropout": 0.05,
    "amp": true,
    "dtype": "float16",
    "cpu_amp": false,
    "cpu_threads": 0,
    "use_compile": false,
    "dataset_mode": "chat",
    "curriculum": true,
    "distributed_backend": "auto",
    "world_size": 1
  },
  "meta": {
    "last_loss": 7.509772777557373,
    "val_loss": 6.771079770723978
  }
}
```

---

### `252/588` `backend/models/runs/ALI-v1-20261004-224649-233144/FINAL_FILE_TRAINING_E2E_RECEIPT_4.5.8.json`

- **المسار الكامل:** `F:\1f\p\ALI_Studio_Pro_Design4_4.6.0\04_Adaptive_Hybrid\backend/models/runs/ALI-v1-20261004-224649-233144/FINAL_FILE_TRAINING_E2E_RECEIPT_4.5.8.json`
- **الحجم:** 4793 بايت (4.7 KB)
- **الامتداد:** `.json`

```json
{
  "release": "4.5.7",
  "fixture": "ALI_User_Understanding_Bundle_V4.md",
  "fixture_sha256": "371d2e0de7e109848ee8246801e4de80e1f339a9d3be9d0f5add36bc241087bb",
  "actual_conversation_headings": 216,
  "unique_samples": 215,
  "duplicate_exact_qa_samples": 1,
  "duplicate_question_groups": 3,
  "unique_questions": 213,
  "postfix_regression": {
    "relative_base_checkpoint_tokenizer_reuse": "fixed_and_passed",
    "tokenizer_long_input": "65 passed in 1.89s"
  },
  "import": {
    "status": "validated",
    "sample_count": 215,
    "routed_to_rag": true,
    "warnings": [
      "declared_conversation_count_mismatch:50!=216",
      "duplicate_samples_in_file:1"
    ]
  },
  "training": {
    "run_id": "continuous-v1-20261004-224649-e71dab",
    "generation": "v1",
    "status": "success",
    "base_version": "2.5.0-bootstrap-micro",
    "device": "cpu",
    "steps": 13,
    "samples_seen": 208,
    "tokens_seen": 26624,
    "last_loss": 7.509772777557373,
    "evaluation": {
      "loss": 6.771079858144124,
      "perplexity": 872.2532954340983,
      "samples": 60
    },
    "new_data_holdout": {
      "loss": 7.454573845863342,
      "perplexity": 1727.7475515931083,
      "samples": 20
    },
    "promoted_active": true,
    "tokenizer_lineage": {
      "reused_base_tokenizer": true,
      "base_tokenizer_sha256": "5c1ca7b2eb4a855452c133adbdc52d15306ee2dcdf2590cdf78102ba1c5a3d4b",
      "merged_tokenizer_sha256": "5c1ca7b2eb4a855452c133adbdc52d15306ee2dcdf2590cdf78102ba1c5a3d4b"
    }
  },
  "quiz": {
    "questions": 216,
    "unique_questions": 213,
    "training_qa_mode": 216,
    "source_answer_match": 216,
    "failures": 0
  },
  "streaming": {
    "mode": "training_qa",
    "exact_answer": true
  },
  "reimport": {
    "status": "duplicate",
    "reason": "duplicate_source"
  },
  "model_manager_reload": {
    "pass": true,
    "version": "v1",
    "engine": "LocalInference"
  },
  "artifacts": {
    "checkpoint_pt": "backend/models/runs/20261004-224649-233144/checkpoints/final-000013",
    "internal_model_safetensors": "backend/models/runs/20261004-224649-233144/checkpoints/final-000013/model.safetensors",
    "adapter_safetensors": "backend/models/runs/20261004-224649-233144/checkpoints/final-000013/adapter/adapter_model.safetensors",
    "merged_model_safetensors": "backend/models/runs/20261004-224649-233144/checkpoints/final-000013/merged_hf/model.safetensors"
  },
  "artifact_hashes": {
    "checkpoint.pt": {
      "size_bytes": 16216409,
      "sha256": "67d6d4297242854e8268b32dd775372eb5c02e70144ee5132b89492fececa5d0"
    },
    "model.safetensors": {
      "size_bytes": 15006408,
      "sha256": "b8ce83adb606742998ad7841ecd5905239b0d52831ce0bc9a4aa998362ae024c"
    },
    "adapter_model.safetensors": {
      "size_bytes": 570696,
      "sha256": "66430925b5f6d6f270a9def44ea52fb90adca14381186dbbb031b5078f4e8938"
    },
    "merged_model.safetensors": {
      "size_bytes": 14435744,
      "sha256": "50b9c5ec66a1cd19035d93f969c412cc7fc87922e03b0a557d5d565ab5123eca"
    },
    "checkpoint_pt": {
      "size_bytes": 16216409,
      "sha256": "67d6d4297242854e8268b32dd775372eb5c02e70144ee5132b89492fececa5d0"
    },
    "internal_model_safetensors": {
      "size_bytes": 15006408,
      "sha256": "b8ce83adb606742998ad7841ecd5905239b0d52831ce0bc9a4aa998362ae024c"
    },
    "adapter_safetensors": {
      "size_bytes": 570696,
      "sha256": "66430925b5f6d6f270a9def44ea52fb90adca14381186dbbb031b5078f4e8938"
    },
    "merged_model_safetensors": {
      "size_bytes": 14435744,
      "sha256": "50b9c5ec66a1cd19035d93f969c412cc7fc87922e03b0a557d5d565ab5123eca"
    }
  },
  "merge_equivalence": {
    "logit_max_diff": 0.016632080078125,
    "logit_mean_diff": 0.0008416299242526293,
    "weight_formula_max_diff": 0.0,
    "weight_disk_max_diff": 0.0,
    "argmax_equal": true,
    "pass": true,
    "logit_note": "Logit difference is due to float32 operation-order associativity; the stored merged Q projection weight exactly equals base + B@A*scale (max diff 0.0), and the serialized merged weight equals the in-memory merged weight (max diff 0.0)."
  },
  "gguf": {
    "status": "pending_converter",
    "reason": "No Windows llama.cpp converter/quantizer is bundled or executable in this Linux container."
  },
  "native_windows": {
    "electron_net_conpty_cuda": "not executed in Linux container"
  },
  "initial_bug_fixed": {
    "description": "Relative base-checkpoint paths were resolved from process CWD during continuation-tokenizer lookup, causing tokenizer retraining and a possible embedding index mismatch. The lookup is now anchored to the pipeline root and covered by regression tests."
  },
  "test_suite": {
    "pytest": "239 passed, 34 skipped, 2 warnings",
    "release_audit": "PASS"
  }
}
```

---

### `253/588` `backend/models/tokenizers/ALI/v4-rebuilt/manifest.json`

- **المسار الكامل:** `F:\1f\p\ALI_Studio_Pro_Design4_4.6.0\04_Adaptive_Hybrid\backend/models/tokenizers/ALI/v4-rebuilt/manifest.json`
- **الحجم:** 1455 بايت (1.4 KB)
- **الامتداد:** `.json`

```json
{
  "artifact_id": "ALI:tokenizer:v4-rebuilt",
  "artifact_type": "tokenizer",
  "compatibility": {
    "vocab_size": 2048
  },
  "created_at": 1791296817.0041904,
  "evaluation": {},
  "files": [
    {
      "path": "special_tokens_map.json",
      "sha256": "1bd43fafc5dc9b132a08feb83487bb41bf5f53bcf89a15b0aa782d148e78dac2",
      "size": 202
    },
    {
      "path": "tokenizer.model",
      "sha256": "b665294a6b18ba47511f0c38d7b0f90fd104ddb5a5c33403e610f1fa09120d52",
      "size": 275000
    },
    {
      "path": "tokenizer.vocab",
      "sha256": "5596ac489deb70f2415368648fd3a08a544107b77e71be8f9b10fe04b0a1310d",
      "size": 34245
    },
    {
      "path": "tokenizer_config.json",
      "sha256": "9354c9e340899300c7a6ff94eb0dc271fe37a4d254e00dfd66785d4000873b92",
      "size": 313
    }
  ],
  "lineage": {
    "corpus_hash": "72c5f8f688598e118d3dcb4f3f0332562f6870f3ca0fd7a0eef3574902c5c8d7",
    "inputs": [
      "/mnt/data/ALI_Studio_Pro_Windows_v4.5.8_CUMULATIVE/project/backend/models/generations/v4/cumulative/train.jsonl"
    ]
  },
  "metadata": {
    "actual_vocab_size": 2048,
    "requested_vocab_size": 2048
  },
  "name": "ALI",
  "path": "/mnt/data/ALI_Studio_Pro_Windows_v4.5.8_CUMULATIVE/project/backend/models/tokenizers/ALI/v4-rebuilt",
  "schema_version": 2,
  "sha256": "eb7294d724db32495c49f564c3e53794eea87b66628c7a8a5bdd15c9f9c61d39",
  "source": "local-training",
  "training": {},
  "version": "v4-rebuilt"
}
```

---

### `254/588` `backend/models/tokenizers/ALI/v4-rebuilt/special_tokens_map.json`

- **المسار الكامل:** `F:\1f\p\ALI_Studio_Pro_Design4_4.6.0\04_Adaptive_Hybrid\backend/models/tokenizers/ALI/v4-rebuilt/special_tokens_map.json`
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

### `255/588` `backend/models/tokenizers/ALI/v4-rebuilt/tokenizer_config.json`

- **المسار الكامل:** `F:\1f\p\ALI_Studio_Pro_Design4_4.6.0\04_Adaptive_Hybrid\backend/models/tokenizers/ALI/v4-rebuilt/tokenizer_config.json`
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

### `256/588` `backend/multimodal/__init__.py`

- **المسار الكامل:** `F:\1f\p\ALI_Studio_Pro_Design4_4.6.0\04_Adaptive_Hybrid\backend/multimodal/__init__.py`
- **الحجم:** 71 بايت (0.1 KB)
- **الامتداد:** `.py`

```python
from .media import load_media
from .model import ALIMultimodalFrontEnd
```

---

### `257/588` `backend/multimodal/dataset.py`

- **المسار الكامل:** `F:\1f\p\ALI_Studio_Pro_Design4_4.6.0\04_Adaptive_Hybrid\backend/multimodal/dataset.py`
- **الحجم:** 370 بايت (0.4 KB)
- **الامتداد:** `.py`

```python
# -*- coding: utf-8 -*-
"""Manifest format for multimodal alignment examples."""
from __future__ import annotations
from pathlib import Path
import json

def write_manifest(rows,out):
    p=Path(out); p.parent.mkdir(parents=True,exist_ok=True)
    with p.open('w',encoding='utf-8') as f:
        for r in rows:f.write(json.dumps(r,ensure_ascii=False)+'\n')
    return p
```

---

### `258/588` `backend/multimodal/inference.py`

- **المسار الكامل:** `F:\1f\p\ALI_Studio_Pro_Design4_4.6.0\04_Adaptive_Hybrid\backend/multimodal/inference.py`
- **الحجم:** 962 بايت (0.9 KB)
- **الامتداد:** `.py`

```python
# -*- coding: utf-8 -*-
from __future__ import annotations
from pathlib import Path
import torch
from multimodal.media import load_media
from multimodal.model import ALIMultimodalFrontEnd

class MultimodalAdapter:
    def __init__(self,weights_dir:str|Path,hidden_size:int=256,device='cpu'):
        self.device=torch.device(device); self.model=ALIMultimodalFrontEnd(hidden_size).to(self.device).eval(); p=Path(weights_dir)
        state=p/'multimodal.safetensors'
        if state.exists():
            from safetensors.torch import load_file; self.model.load_state_dict(load_file(str(state),device='cpu'),strict=False)
        elif (p/'multimodal.pt').exists(): self.model.load_state_dict(torch.load(p/'multimodal.pt',map_location='cpu',weights_only=False),strict=False)
    @torch.no_grad()
    def prefix_from_file(self,path):
        media=load_media(path); return media['kind'],self.model.encode(media['kind'],media['tensor'].unsqueeze(0).to(self.device))
```

---

### `259/588` `backend/multimodal/media.py`

- **المسار الكامل:** `F:\1f\p\ALI_Studio_Pro_Design4_4.6.0\04_Adaptive_Hybrid\backend/multimodal/media.py`
- **الحجم:** 2525 بايت (2.5 KB)
- **الامتداد:** `.py`

```python
# -*- coding: utf-8 -*-
"""Offline media decoding: image, WAV audio and video frames."""
from __future__ import annotations
from pathlib import Path
import math, subprocess, wave
import torch

def _norm_img(t):return t.float()/255.0 if t.max()>1.5 else t.float()
def load_image(path:str|Path,size:int=128)->torch.Tensor:
    from PIL import Image
    img=Image.open(path).convert('RGB').resize((size,size))
    return torch.from_numpy(__import__('numpy').asarray(img)).permute(2,0,1).float()/255.0

def load_wav(path:str|Path,n_mels:int=64,max_seconds:int=20)->torch.Tensor:
    import numpy as np
    with wave.open(str(path),'rb') as wf:
        ch=wf.getnchannels(); sr=wf.getframerate(); frames=min(wf.getnframes(),sr*max_seconds); raw=wf.readframes(frames); width=wf.getsampwidth()
    dtype={1:np.int8,2:np.int16,4:np.int32}.get(width,np.int16); a=np.frombuffer(raw,dtype=dtype).astype(np.float32)
    if ch>1:a=a.reshape(-1,ch).mean(1)
    scale=float(2**(8*width-1)); a=torch.from_numpy(a/scale)
    if a.numel()<512:a=torch.nn.functional.pad(a,(0,512-a.numel()))
    win=400; hop=160; spec=torch.stft(a,n_fft=512,hop_length=hop,win_length=win,return_complex=True).abs(); spec=spec[:n_mels]; return torch.log1p(spec).unsqueeze(0)

def extract_video_frames(path:str|Path,size:int=128,max_frames:int=8)->torch.Tensor:
    """Uses local ffmpeg if available; no network/download occurs."""
    import tempfile, shutil
    if not shutil.which('ffmpeg'): raise FileNotFoundError('ffmpeg is required for video media support')
    with tempfile.TemporaryDirectory(prefix='ali-video-') as td:
        pattern=str(Path(td)/'f-%03d.jpg'); subprocess.run(['ffmpeg','-hide_banner','-loglevel','error','-i',str(path),'-vf',f'fps=1,scale={size}:{size}:force_original_aspect_ratio=decrease','-frames:v',str(max_frames),pattern],check=True,timeout=180)
        from PIL import Image
        frames=[]
        for p in sorted(Path(td).glob('f-*.jpg'))[:max_frames]:frames.append(load_image(p,size))
        if not frames: raise ValueError('no frames decoded from video')
        return torch.stack(frames)

def load_media(path:str|Path,size:int=128):
    p=Path(path); ext=p.suffix.lower()
    if ext in {'.png','.jpg','.jpeg','.webp','.bmp'}: return {'kind':'image','tensor':load_image(p,size)}
    if ext in {'.wav'}: return {'kind':'audio','tensor':load_wav(p)}
    if ext in {'.mp4','.mov','.mkv','.avi','.webm'}: return {'kind':'video','tensor':extract_video_frames(p,size)}
    raise ValueError(f'unsupported media type: {ext}')
```

---

### `260/588` `backend/multimodal/model.py`

- **المسار الكامل:** `F:\1f\p\ALI_Studio_Pro_Design4_4.6.0\04_Adaptive_Hybrid\backend/multimodal/model.py`
- **الحجم:** 2236 بايت (2.2 KB)
- **الامتداد:** `.py`

```python
# -*- coding: utf-8 -*-
"""Small trainable multimodal front-end for ALI.

It learns to map image/audio/video representations into the same hidden space as
ALI token embeddings. The language model can then condition on those prefix states.
"""
from __future__ import annotations
import torch
from torch import nn

class TinyVisionEncoder(nn.Module):
    def __init__(self,out_dim=256):
        super().__init__(); self.net=nn.Sequential(nn.Conv2d(3,32,5,2,2),nn.GELU(),nn.Conv2d(32,64,5,2,2),nn.GELU(),nn.Conv2d(64,128,3,2,1),nn.GELU(),nn.AdaptiveAvgPool2d((1,1))); self.proj=nn.Linear(128,out_dim)
    def forward(self,x):return self.proj(self.net(x).flatten(1))

class TinyAudioEncoder(nn.Module):
    def __init__(self,out_dim=256):
        super().__init__(); self.net=nn.Sequential(nn.Conv2d(1,32,5,2,2),nn.GELU(),nn.Conv2d(32,64,5,2,2),nn.GELU(),nn.Conv2d(64,128,3,2,1),nn.GELU(),nn.AdaptiveAvgPool2d((1,1))); self.proj=nn.Linear(128,out_dim)
    def forward(self,x):
        if x.dim()==3:x=x.unsqueeze(1)
        return self.proj(self.net(x).flatten(1))

class TinyVideoEncoder(nn.Module):
    def __init__(self,out_dim=256):
        super().__init__(); self.vision=TinyVisionEncoder(out_dim)
    def forward(self,x):
        b,t,c,h,w=x.shape; z=self.vision(x.reshape(b*t,c,h,w)).view(b,t,-1); return z.mean(1)

class MediaProjector(nn.Module):
    def __init__(self,media_dim:int,hidden_size:int,prefix_tokens:int=4):
        super().__init__(); self.prefix_tokens=prefix_tokens; self.net=nn.Sequential(nn.Linear(media_dim,hidden_size*2),nn.GELU(),nn.Linear(hidden_size*2,hidden_size*prefix_tokens))
    def forward(self,x):return self.net(x).view(x.size(0),self.prefix_tokens,-1)

class ALIMultimodalFrontEnd(nn.Module):
    def __init__(self,hidden_size:int=256):
        super().__init__(); self.vision=TinyVisionEncoder(hidden_size); self.audio=TinyAudioEncoder(hidden_size); self.video=TinyVideoEncoder(hidden_size); self.projector=MediaProjector(hidden_size,hidden_size)
    def encode(self,kind,tensor):
        if kind=='image': z=self.vision(tensor)
        elif kind=='audio': z=self.audio(tensor)
        elif kind=='video': z=self.video(tensor)
        else: raise ValueError(kind)
        return self.projector(z)
```

---

### `261/588` `backend/multimodal/train.py`

- **المسار الكامل:** `F:\1f\p\ALI_Studio_Pro_Design4_4.6.0\04_Adaptive_Hybrid\backend/multimodal/train.py`
- **الحجم:** 1582 بايت (1.5 KB)
- **الامتداد:** `.py`

```python
# -*- coding: utf-8 -*-
"""Train media-to-ALI projector with paired media tensors and target ALI hidden states."""
from __future__ import annotations
from pathlib import Path
import json, torch
from multimodal.media import load_media
from multimodal.model import ALIMultimodalFrontEnd

def train_pairs(manifest:str|Path,out_dir:str|Path,hidden_size:int=256,steps:int=200,lr:float=2e-4)->dict:
    rows=[json.loads(x) for x in Path(manifest).read_text(encoding='utf-8').splitlines() if x.strip()]
    if not rows: raise ValueError('empty multimodal manifest')
    model=ALIMultimodalFrontEnd(hidden_size).train(); opt=torch.optim.AdamW(model.parameters(),lr=lr); losses=[]
    for step in range(steps):
        row=rows[step%len(rows)]; media=load_media(row['path']); t=media['tensor'];
        if media['kind']=='image': inp=t.unsqueeze(0)
        elif media['kind']=='audio': inp=t.unsqueeze(0)
        else: inp=t.unsqueeze(0)
        z=model.encode(media['kind'],inp)
        target=torch.tensor(row['target_embedding'],dtype=z.dtype).view(1,1,-1).expand(1,z.size(1),-1)
        loss=torch.nn.functional.mse_loss(z,target); opt.zero_grad(); loss.backward(); opt.step(); losses.append(float(loss.item()))
    p=Path(out_dir); p.mkdir(parents=True,exist_ok=True)
    try:
        from safetensors.torch import save_file; save_file({k:v.detach().cpu() for k,v in model.state_dict().items()},str(p/'multimodal.safetensors'))
    except Exception: torch.save(model.state_dict(),p/'multimodal.pt')
    return {'steps':steps,'loss':losses[-1],'initial_loss':losses[0],'weights':str(p)}
```

---

### `262/588` `backend/nix/README.md`

- **المسار الكامل:** `F:\1f\p\ALI_Studio_Pro_Design4_4.6.0\04_Adaptive_Hybrid\backend/nix/README.md`
- **الحجم:** 72 بايت (0.1 KB)
- **الامتداد:** `.md`

```markdown
# Nix
Optional reproducibility metadata. Windows is the primary target.
```

---

### `263/588` `backend/optional-mcps/client.py`

- **المسار الكامل:** `F:\1f\p\ALI_Studio_Pro_Design4_4.6.0\04_Adaptive_Hybrid\backend/optional-mcps/client.py`
- **الحجم:** 2289 بايت (2.2 KB)
- **الامتداد:** `.py`

```python
# -*- coding: utf-8 -*-
"""Minimal optional MCP stdio client.

It implements JSON-RPC initialization, tools/list and tools/call. It is opt-in and never starts
an untrusted server automatically; callers must supply an executable from the local allowlist.
"""
from __future__ import annotations
import json, subprocess, threading
from pathlib import Path

class MCPClient:
    def __init__(self, command:list[str], cwd:str|Path|None=None, timeout:float=20):
        if not command: raise ValueError('command required')
        self.command=[str(x) for x in command]; self.cwd=str(cwd) if cwd else None; self.timeout=timeout; self.p=None; self._id=0
    def start(self):
        if self.p: return
        self.p=subprocess.Popen(self.command,cwd=self.cwd,stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True,encoding='utf-8',bufsize=1,creationflags=getattr(subprocess,'CREATE_NO_WINDOW',0))
        self.request('initialize',{'protocolVersion':'2025-06-18','capabilities':{},'clientInfo':{'name':'ALI Studio','version':'3.0.0'}})
        self.notify('notifications/initialized',{})
    def _write(self,obj):
        assert self.p and self.p.stdin; self.p.stdin.write(json.dumps(obj,ensure_ascii=False)+'\n'); self.p.stdin.flush()
    def notify(self,method,params): self._write({'jsonrpc':'2.0','method':method,'params':params})
    def request(self,method,params):
        self._id+=1; rid=self._id; self._write({'jsonrpc':'2.0','id':rid,'method':method,'params':params})
        assert self.p and self.p.stdout
        while True:
            line=self.p.stdout.readline()
            if not line: raise RuntimeError('MCP server closed stdout')
            try: msg=json.loads(line)
            except Exception: continue
            if msg.get('id')==rid:
                if 'error' in msg: raise RuntimeError(json.dumps(msg['error'],ensure_ascii=False))
                return msg.get('result',{})
    def tools(self): self.start(); return self.request('tools/list',{}).get('tools',[])
    def call(self,name:str,arguments:dict|None=None): self.start(); return self.request('tools/call',{'name':name,'arguments':arguments or {}})
    def close(self):
        if self.p:
            try:self.p.terminate()
            except Exception:pass
            self.p=None
```

---

### `264/588` `backend/optional-mcps/README.md`

- **المسار الكامل:** `F:\1f\p\ALI_Studio_Pro_Design4_4.6.0\04_Adaptive_Hybrid\backend/optional-mcps/README.md`
- **الحجم:** 92 بايت (0.1 KB)
- **الامتداد:** `.md`

```markdown
# Optional MCPs
MCP adapters are opt-in and never contacted without explicit configuration.
```

---

### `265/588` `backend/optional-skills/pdf-research.md`

- **المسار الكامل:** `F:\1f\p\ALI_Studio_Pro_Design4_4.6.0\04_Adaptive_Hybrid\backend/optional-skills/pdf-research.md`
- **الحجم:** 200 بايت (0.2 KB)
- **الامتداد:** `.md`

```markdown
# PDF Research

Extract pages and metadata, preserve page numbers and source paths, then store the document in Knowledge/RAG. Promote information to training only after quality and provenance checks.
```

---

### `266/588` `backend/optional-skills/README.md`

- **المسار الكامل:** `F:\1f\p\ALI_Studio_Pro_Design4_4.6.0\04_Adaptive_Hybrid\backend/optional-skills/README.md`
- **الحجم:** 55 بايت (0.1 KB)
- **الامتداد:** `.md`

```markdown
# Optional skills
Disabled until explicitly activated.
```

---

### `267/588` `backend/optional_mcps/__init__.py`

- **المسار الكامل:** `F:\1f\p\ALI_Studio_Pro_Design4_4.6.0\04_Adaptive_Hybrid\backend/optional_mcps/__init__.py`
- **الحجم:** 53 بايت (0.1 KB)
- **الامتداد:** `.py`

```python
from .client import MCPClient

__all__=["MCPClient"]
```

---

### `268/588` `backend/optional_mcps/client.py`

- **المسار الكامل:** `F:\1f\p\ALI_Studio_Pro_Design4_4.6.0\04_Adaptive_Hybrid\backend/optional_mcps/client.py`
- **الحجم:** 2289 بايت (2.2 KB)
- **الامتداد:** `.py`

```python
# -*- coding: utf-8 -*-
"""Minimal optional MCP stdio client.

It implements JSON-RPC initialization, tools/list and tools/call. It is opt-in and never starts
an untrusted server automatically; callers must supply an executable from the local allowlist.
"""
from __future__ import annotations
import json, subprocess, threading
from pathlib import Path

class MCPClient:
    def __init__(self, command:list[str], cwd:str|Path|None=None, timeout:float=20):
        if not command: raise ValueError('command required')
        self.command=[str(x) for x in command]; self.cwd=str(cwd) if cwd else None; self.timeout=timeout; self.p=None; self._id=0
    def start(self):
        if self.p: return
        self.p=subprocess.Popen(self.command,cwd=self.cwd,stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True,encoding='utf-8',bufsize=1,creationflags=getattr(subprocess,'CREATE_NO_WINDOW',0))
        self.request('initialize',{'protocolVersion':'2025-06-18','capabilities':{},'clientInfo':{'name':'ALI Studio','version':'3.0.0'}})
        self.notify('notifications/initialized',{})
    def _write(self,obj):
        assert self.p and self.p.stdin; self.p.stdin.write(json.dumps(obj,ensure_ascii=False)+'\n'); self.p.stdin.flush()
    def notify(self,method,params): self._write({'jsonrpc':'2.0','method':method,'params':params})
    def request(self,method,params):
        self._id+=1; rid=self._id; self._write({'jsonrpc':'2.0','id':rid,'method':method,'params':params})
        assert self.p and self.p.stdout
        while True:
            line=self.p.stdout.readline()
            if not line: raise RuntimeError('MCP server closed stdout')
            try: msg=json.loads(line)
            except Exception: continue
            if msg.get('id')==rid:
                if 'error' in msg: raise RuntimeError(json.dumps(msg['error'],ensure_ascii=False))
                return msg.get('result',{})
    def tools(self): self.start(); return self.request('tools/list',{}).get('tools',[])
    def call(self,name:str,arguments:dict|None=None): self.start(); return self.request('tools/call',{'name':name,'arguments':arguments or {}})
    def close(self):
        if self.p:
            try:self.p.terminate()
            except Exception:pass
            self.p=None
```

---

### `269/588` `backend/phase2/mcp_servers.json`

- **المسار الكامل:** `F:\1f\p\ALI_Studio_Pro_Design4_4.6.0\04_Adaptive_Hybrid\backend/phase2/mcp_servers.json`
- **الحجم:** 977 بايت (1.0 KB)
- **الامتداد:** `.json`

```json
{
  "requested_count": 65,
  "listed_count": 46,
  "servers": [
    "airtable",
    "algolia",
    "asana",
    "atlassian",
    "attio",
    "aws-knowledge",
    "buildkite",
    "canva",
    "circleci",
    "clickup",
    "cloudflare",
    "comfy-cloud",
    "context7",
    "datadog",
    "deepwiki",
    "dropbox",
    "figma",
    "fireflies",
    "gamma",
    "gitlab",
    "grafana",
    "hugging_face",
    "intercom",
    "klaviyo",
    "linear",
    "microsoft-learn",
    "miro",
    "monday",
    "notion",
    "paypal",
    "plaid",
    "postman",
    "prisma-postgres",
    "railway",
    "semgrep",
    "sentry",
    "strava",
    "stripe",
    "supabase",