        },
        {
          "elapsed_sec": 16.74,
          "epoch": 1,
          "eta_sec": 0.88,
          "loss": 6.091390132904053,
          "lr": 4.144511940348516e-06,
          "rank": 0,
          "samples_seen": 456,
          "step": 57,
          "tokens_per_sec": 2119.17,
          "tokens_seen": 35485,
          "total_samples": 1532,
          "total_steps": 60,
          "world_size": 1
        },
        {
          "elapsed_sec": 17.01,
          "epoch": 1,
          "eta_sec": 0.59,
          "loss": 6.475715160369873,
          "lr": 1.8467489107293509e-06,
          "rank": 0,
          "samples_seen": 464,
          "step": 58,
          "tokens_per_sec": 2115.82,
          "tokens_seen": 35996,
          "total_samples": 1532,
          "total_steps": 60,
          "world_size": 1
        },
        {
          "elapsed_sec": 17.29,
          "epoch": 1,
          "eta_sec": 0.29,
          "loss": 6.202650547027588,
          "lr": 4.623999400308054e-07,
          "rank": 0,
          "samples_seen": 472,
          "step": 59,
          "tokens_per_sec": 2115.96,
          "tokens_seen": 36590,
          "total_samples": 1532,
          "total_steps": 60,
          "world_size": 1
        },
        {
          "elapsed_sec": 17.6,
          "epoch": 1,
          "eta_sec": 0.0,
          "loss": 6.3332366943359375,
          "lr": 0.0,
          "rank": 0,
          "samples_seen": 480,
          "step": 60,
          "tokens_per_sec": 2118.82,
          "tokens_seen": 37283,
          "total_samples": 1532,
          "total_steps": 60,
          "world_size": 1
        }
      ],
      "loss": 6.3332366943359375,
      "steps": 60,
      "tokens_per_sec": 2029.92,
      "tokens_seen": 37283,
      "val_loss": 6.6361991246541345
    },
    "stage": "base"
  },
  "name": "ALI",
  "path": "/mnt/data/ALI_Studio_Pro_Windows_v4.5.8_CUMULATIVE/project/models/runs/20261006-142710-7225c1/checkpoints/final-000060",
  "schema_version": 2,
  "sha256": "09721a367d386418bf8908cf0df346936d53bc453f7c4c8e6ff8f8f300fb7fa9",
  "source": "training-pipeline",
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

### `518/588` `models/runs/20261006-142710-7225c1/checkpoints/final-000060/trainer_state.json`

- **المسار الكامل:** `F:\1f\p\ALI_Studio_Pro_Design4_4.6.0\04_Adaptive_Hybrid\models/runs/20261006-142710-7225c1/checkpoints/final-000060/trainer_state.json`
- **الحجم:** 876 بايت (0.9 KB)
- **الامتداد:** `.json`

```json
{
  "global_step": 60,
  "micro_step": 480,
  "best_val": 6.6361991246541345,
  "tokens_seen": 37283,
  "samples_seen": 480,
  "config": {
    "epochs": 1,
    "batch_size": 1,
    "grad_accum": 8,
    "learning_rate": 0.0003,
    "weight_decay": 0.1,
    "warmup_steps": 20,
    "max_steps": 60,
    "save_every": 100,
    "eval_every": 100,
    "max_seq_len": 128,
    "seed": 42,
    "device": "cpu",
    "gradient_checkpointing": true,
    "max_grad_norm": 1.0,
    "train_mode": "full",
    "lora_rank": 8,
    "lora_alpha": 16.0,
    "lora_dropout": 0.05,
    "amp": true,
    "dtype": "float16",
    "cpu_amp": false,
    "cpu_threads": 0,
    "use_compile": false,
    "dataset_mode": "causal",
    "curriculum": true,
    "distributed_backend": "auto",
    "world_size": 1
  },
  "meta": {
    "last_loss": 6.3332366943359375,
    "val_loss": 6.6361991246541345
  }
}
```

---

### `519/588` `models/runs/20261006-142710-7225c1/latest_event.json`

- **المسار الكامل:** `F:\1f\p\ALI_Studio_Pro_Design4_4.6.0\04_Adaptive_Hybrid\models/runs/20261006-142710-7225c1/latest_event.json`
- **الحجم:** 370 بايت (0.4 KB)
- **الامتداد:** `.json`

```json
{
  "run_id": "20261006-142710-7225c1",
  "stage": "complete",
  "status": "success",
  "checkpoint": "models/runs/20261006-142710-7225c1/checkpoints/final-000060",
  "hf_dir": "models/runs/20261006-142710-7225c1/checkpoints/final-000060/hf",
  "adapter": "",
  "evaluation": {
    "loss": 6.969683837890625,
    "perplexity": 1063.8863368118753,
    "samples": 60
  }
}
```

---

### `520/588` `models/tokenizers/ALI/20261006-142710/manifest.json`

- **المسار الكامل:** `F:\1f\p\ALI_Studio_Pro_Design4_4.6.0\04_Adaptive_Hybrid\models/tokenizers/ALI/20261006-142710/manifest.json`
- **الحجم:** 1461 بايت (1.4 KB)
- **الامتداد:** `.json`

```json
{
  "artifact_id": "ALI:tokenizer:20261006-142710",
  "artifact_type": "tokenizer",
  "compatibility": {
    "vocab_size": 2048
  },
  "created_at": 1791296830.577539,
  "evaluation": {},
  "files": [
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
  "path": "/mnt/data/ALI_Studio_Pro_Windows_v4.5.8_CUMULATIVE/project/models/tokenizers/ALI/20261006-142710",
  "schema_version": 2,
  "sha256": "855ec73474675763ea2f2f3ebf1e3c6b63d99ad25fa205a15d192aa3ae4848de",
  "source": "local-training",
  "training": {},
  "version": "20261006-142710"
}
```

---

### `521/588` `models/tokenizers/ALI/20261006-142710/special_tokens_map.json`

- **المسار الكامل:** `F:\1f\p\ALI_Studio_Pro_Design4_4.6.0\04_Adaptive_Hybrid\models/tokenizers/ALI/20261006-142710/special_tokens_map.json`
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

### `522/588` `models/tokenizers/ALI/20261006-142710/tokenizer_config.json`

- **المسار الكامل:** `F:\1f\p\ALI_Studio_Pro_Design4_4.6.0\04_Adaptive_Hybrid\models/tokenizers/ALI/20261006-142710/tokenizer_config.json`
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

### `523/588` `package.json`

- **المسار الكامل:** `F:\1f\p\ALI_Studio_Pro_Design4_4.6.0\04_Adaptive_Hybrid\package.json`
- **الحجم:** 552 بايت (0.5 KB)
- **الامتداد:** `.json`

```json
{
  "name": "ali-studio-pro",
  "version": "4.5.8",
  "description": "نسخة سطح مكتب احترافية من ALI مبنية على فصل واضح بين الـLauncher والواجهة ومحرك الذكاء الاصطناعي.",
  "main": "index.js",
  "scripts": {
    "verify": "python scripts/FINAL_RELEASE_AUDIT.py",
    "test": "python -m pytest -q backend",
    "build:desktop": "cmd /c scripts\\BUILD_DESKTOP.bat",
    "build:portable": "cmd /c scripts\\BUILD_PORTABLE.bat"
  },
  "keywords": [],
  "author": "",
  "license": "ISC"
}
```

---

### `524/588` `PROJECT_MANIFEST.json`

- **المسار الكامل:** `F:\1f\p\ALI_Studio_Pro_Design4_4.6.0\04_Adaptive_Hybrid\PROJECT_MANIFEST.json`
- **الحجم:** 3284 بايت (3.2 KB)
- **الامتداد:** `.json`

```json
{
  "name": "ALI Studio Pro",
  "version": "4.5.8",
  "ui_reference": "supplied ALI Studio screenshot",
  "launcher": {
    "language": "C#",
    "framework": ".NET 8"
  },
  "desktop": {
    "electron": "40.10.2",
    "react": "19",
    "node": "22",
    "styling": [
      "Tailwind CSS",
      "PostCSS"
    ],
    "terminal": [
      "xterm.js",
      "node-pty",
      "ConPTY"
    ]
  },
  "backend": {
    "language": "Python 3.11.9",
    "source": "ALI AI 2.6 Hermes Replacement"
  },
  "release_assets": [
    "Build-time Electron node_modules",
    "Build-time Embedded Python 3.11.9",
    "Build-time Windows Python wheelhouse"
  ],
  "included_model": "ALI-v1 (bundled trained merged HF) with ALI-Bootstrap-v2.5 fallback",
  "release": "Professional Final · Bundled trained weights · Grounded local QA · adaptive GPU · continuous learning",
  "architecture": [
    "C# .NET 8 Launcher",
    "Electron 40.10.2",
    "React 19",
    "Python 3.11.9",
    "node-pty/ConPTY"
  ],
  "continuous_learning": {
    "generation_format": "vN",
    "auto_train_after_valid_import": true,
    "accepted_training_formats": [
      ".csv",
      ".json",
      ".jsonl",
      ".markdown",
      ".md",
      ".txt"
    ],
    "immediate_rag_index": true,
    "new_samples_only": true,
    "cross_file_dedup": true,
    "promotion_required": true,
    "rollback_preserved": true,
    "markdown_conversation_bundle": "supported"
  },
  "verification": {
    "python_compile": "PASS",
    "pytest": "239 passed, 34 skipped, 2 warnings in Linux validation",
    "desktop_source": "PASS",
    "native_windows_build": "REQUIRES_WINDOWS_HOST",
    "clean_release_registry": "bootstrap active only",
    "bundled_qwen_gguf": "NOT_BUNDLED_IN_THIS_LINUX_VALIDATION_ENV",
    "bundled_windows_runtime": "NOT_BUNDLED_IN_THIS_LINUX_VALIDATION_ENV",
    "node_syntax": "PASS",
    "arabic_rag_e2e": "PASS",
    "dynamic_port": "PASS",
    "training_progress_e2e": "PASS (isolated run reached step 25/31; full evaluation requires longer isolated run)",
    "gpu_training": "REQUIRES_WINDOWS_CUDA_SELF_TEST"
  },
  "training_update": "v1 bundled and verified end-to-end",
  "training_examples": 215,
  "trained_artifacts": [
    "backend/models/active/ALI-v1",
    "backend/models/runs/ALI-v1-20261004-224649-233144/checkpoints/final-000013"
  ],
  "target": "Windows x64",
  "training": "continuous versioned LoRA",
  "recommended_model": "Qwen2.5-0.5B-Instruct-Q4_K_M.gguf (398 MB; optional Windows download)",
  "runtime_seed_knowledge": [
    "knowledge_seed/ALI_CORE_QA_AR.md",
    "knowledge_seed/ALI_CURRENT_STATUS_4.5.2.md",
    "knowledge_seed/ALI_V4_4_COMPLETE_REPORT.md",
    "knowledge_seed/THINKPAD_P50_ARABIC_REFERENCE.md",
    "knowledge_seed/THINKPAD_P50_COMPLETE_USER_PROFILE.md"
  ],
  "e2e_training_fixture": "backend/data/training/testdata/ALI_User_Understanding_Bundle_V4.md",
  "e2e_training_fixture_samples": 215,
  "e2e_quiz_questions": 216,
  "e2e_quiz_exact_source_answer_match": "216/216",
  "native_windows_build": "REQUIRES_WINDOWS_HOST",
  "bundled_runtime_knowledge": "backend/runtime_knowledge.sqlite3",
  "bundled_training_data": "backend/models/runs/ALI-v1-20261004-224649-233144/training",
  "bundled_qwen_gguf": "NOT_BUNDLED_NO_NETWORK_AVAILABLE_DURING_BUILD"
}
```

---

### `525/588` `PROJECT_VERSION.json`

- **المسار الكامل:** `F:\1f\p\ALI_Studio_Pro_Design4_4.6.0\04_Adaptive_Hybrid\PROJECT_VERSION.json`
- **الحجم:** 1137 بايت (1.1 KB)
- **الامتداد:** `.json`

```json
{
  "name": "ALI AI",
  "version": "4.6.0",
  "codename": "Cumulative Generation · Web-Grounded Chat · Error Learning · P50 Professional",
  "previous_project": "2.5.0",
  "release_date": "2026-10-06",
  "principles": [
    "local-first",
    "real-training",
    "versioned-artifacts",
    "verifiable-lineage",
    "safe-tools",
    "scalable-architecture",
    "professional-ui",
    "bidi-ui",
    "assistant-orchestration",
    "verified-completion",
    "adaptive-workload",
    "grounded-answering",
    "cumulative-generations",
    "web-grounded-chat",
    "error-correction-learning",
    "portable-release",
    "runtime-independence"
  ],
  "training_mode": "cumulative_generation_lora",
  "base_version": "2.5.0",
  "training_update": "cumulative_v1",
  "target": "Windows x64",
  "hardware_profile": "config/hardware_profile.json",
  "previous_release": "2.0.0",
  "upgraded_from": "4.5.8",
  "ui_design": "design4",
  "ui_title": "التصميم الرابع — Adaptive Hybrid",
  "ui_description": "واجهة زجاجية طبقية حديثة تجمع المحادثة وسياق النظام والأدوات."
}
```

---

### `526/588` `pytest.ini`

- **المسار الكامل:** `F:\1f\p\ALI_Studio_Pro_Design4_4.6.0\04_Adaptive_Hybrid\pytest.ini`
- **الحجم:** 163 بايت (0.2 KB)
- **الامتداد:** `.ini`

```ini
[pytest]
testpaths = backend/tests
norecursedirs = runtime/python/Lib runtime/python/Lib/test runtime/python/Lib/tests desktop/node_modules .venv __pycache__ .git
```

---

### `527/588` `README.md`

- **المسار الكامل:** `F:\1f\p\ALI_Studio_Pro_Design4_4.6.0\04_Adaptive_Hybrid\README.md`
- **الحجم:** 2977 بايت (2.9 KB)
- **الامتداد:** `.md`

```markdown
# ALI Studio Pro 4.5.8 — Full Bundled Final

هذا الإصدار يجمع المصدر الكامل للمشروع مع إصلاحات التشغيل السابقة، النموذج المدرّب `ALI-v1`، الـcheckpoint، الـLoRA adapter، الأوزان المدمجة، بيانات التدريب، وقاعدة المعرفة المحلية المجهزة مسبقاً.

## البنية
- Launcher: C# / .NET 8
- Desktop: Electron 40.10.2 + React 19 + xterm.js + node-pty/ConPTY
- Backend: Python 3.11.9 target
- Local AI: ALI custom Llama-compatible model + RAG + Memory + Tools + continuous LoRA learning
- Hardware policy: adaptive CPU/GPU with safe fallback for 2GB-class legacy Maxwell GPUs

## النموذج المضمّن
- Active: `backend/models/active/ALI-v1`
- Fallback: `backend/models/active/ALI-Bootstrap-v2.5`
- Full training run: `backend/models/runs/ALI-v1-20261004-224649-233144/checkpoints/final-000013`
- Includes checkpoint, internal weights, adapter, merged HF weights, tokenizer, manifests and training JSONL.

## بيانات التدريب المضمّنة
`backend/data/training/testdata/ALI_User_Understanding_Bundle_V4.md` is the exact uploaded fixture. The parser found 216 conversation sections and 215 unique Q/A samples after exact deduplication. The bundled local knowledge DB contains 215 training-QA chunks, so the application can answer the fixture questions immediately on a clean start.

## التحقق المنفّذ
- Python compile: PASS
- Full backend tests: **242 passed, 34 skipped, 2 warnings**
- Final release audit: PASS
- Clean-start backend API health: PASS
- Active `ALI-v1` model reload: PASS
- All 216 fixture questions through `/api/chat`: **216/216** in `training_qa` mode
- Source-answer match: **216/216**
- Checkpoint load: PASS
- Active merged weights match bundled merged weights: PASS

## لماذا توجد SKIP؟
الاختبارات الـ34 المتجاوزة مرتبطة ببيئة GUI/Windows native غير المتوفرة في Linux build container. لم يتم الادعاء بتشغيل Electron production، C#/.NET publish، node-pty/ConPTY، embedded Windows CPython، CUDA kernel، أو llama.cpp Windows binaries هنا.

## التشغيل على Windows
1. شغّل `scripts\SETUP_WINDOWS_COMPLETE.bat` على جهاز Windows x64.
2. شغّل `scripts\FINAL_WINDOWS_RELEASE_GATE.ps1` للتحقق من runtime وElectron و.NET وGPU وnode-pty.
3. شغّل `scripts\VERIFY_ALL.bat`.
4. شغّل build/portable launcher من `desktop\release\` أو الناتج من `scripts\BUILD_PORTABLE.bat`.

للاستخدام دون إنترنت، يمكن إبقاء `allow_internet=false`. تنزيل Qwen GGUF وllama.cpp اختياري ويُنفّذ بواسطة سكربتات `scripts\DOWNLOAD_*`.

راجع `FINAL_RELEASE_REPORT_4.5.8.md` و`BUNDLED_TRAINED_MODEL_MANIFEST_4.5.8.json` و`FINAL_FILE_TRAINING_E2E_RECEIPT_4.5.8.json` للتفاصيل والأثر التدريبي.
```

---

### `528/588` `README_4.4.0.md`

- **المسار الكامل:** `F:\1f\p\ALI_Studio_Pro_Design4_4.6.0\04_Adaptive_Hybrid\README_4.4.0.md`
- **الحجم:** 1585 بايت (1.5 KB)
- **الامتداد:** `.md`

```markdown
# ALI Studio Pro 4.5.0 — Complete Professional Desktop

## Architecture
C#/.NET 8 Portable Launcher → Electron 40.10.2/Chromium → React 19 → Electron IPC → Python Runtime → ALI Agent/Model/RAG/Memory/Tools/Training.

## Training
Drop Markdown or supported documents into the cumulative learning center. The importer validates, normalizes, removes secrets, hashes for deduplication, indexes knowledge into RAG, extracts conversation samples, and creates an incremental dataset. Training runs from the current active model and produces v1/v2/v3... candidates. Evaluation and regression run before promotion.

## Chat sessions
Use **محادثة جديدة** to create an independent saved session. Use **المحادثات السابقة** to open, rename, or delete saved sessions. Streaming and non-streaming responses stay in the same session.

## Adaptive GPU
Select Auto/CPU/GPU from the top bar. Auto runs a CUDA availability check plus a real kernel self-test and uses free VRAM to choose a workload. On a 2 GB legacy GPU, the workload reduces sequence length as free VRAM falls and falls back to CPU if safe headroom is unavailable. Forced GPU reports a clear diagnostic instead of silently switching to CPU.

## Windows setup
For the requested Python 3.11 line, `backend/SETUP.bat` creates the development environment. Legacy NVIDIA hardware is routed to `requirements-windows-legacy-gpu.txt`. The final Portable build still requires a Windows machine with .NET 8, Node.js 22, native node-pty tooling, Embedded Python 3.11.9 and the required model/runtime binaries.
```

---

### `529/588` `README_TRAINING_V1.md`

- **المسار الكامل:** `F:\1f\p\ALI_Studio_Pro_Design4_4.6.0\04_Adaptive_Hybrid\README_TRAINING_V1.md`
- **الحجم:** 345 بايت (0.3 KB)
- **الامتداد:** `.md`

```markdown
# ALI Studio Pro 4.3.0 — V1 Weight Update

هذه النسخة تحتوي على تحديث أوزان فعلي v1 تم تدريبه فوق `ALI-Bootstrap-v2.5` باستخدام LoRA، مع نسختي Adapter وMerged HF.

الملف `INSTALL_TRAINING_UPDATE_V1.bat` يسجل v1 كـCandidate. لا يقوم بالترقية تلقائياً.
```

---

### `530/588` `REBUILD_4.5.0_REPORT.md`

- **المسار الكامل:** `F:\1f\p\ALI_Studio_Pro_Design4_4.6.0\04_Adaptive_Hybrid\REBUILD_4.5.0_REPORT.md`
- **الحجم:** 1725 بايت (1.7 KB)
- **الامتداد:** `.md`

```markdown
# ALI Studio Pro 4.5.0 — Professional Rebuild

## What was corrected
- Fixed a frontend syntax error in `desktop/src/App.jsx` (`const result = const result`).
- Fixed streaming chat so it preserves conversation ID and compute mode.
- Added `/api/memory/list` compatibility alias.
- Improved NVIDIA SMI polling with cache and a hard timeout to reduce blocking.
- Added explicit per-process CUDA memory budgeting.
- Added adaptive GGUF offload policy for 2 GB-class GPUs.
- Added target ThinkPad P50 profile and knowledge documents.
- Added 34 curated, non-duplicated project/hardware Q&A training examples.
- Added optional llama.cpp bridge and Qwen model manifest.
- Strengthened Launcher validation for missing Embedded Python.
- Added Electron rebuild step for node-pty native module.
- Added grounded RAG fallback when the tiny bootstrap model emits unusable text.

## Important truth about model quality
The previous report recorded 0/8 model-only answers for the 30 MB bootstrap model. This rebuild does not pretend that LoRA can turn a tiny custom bootstrap into a strong general assistant. The production path therefore separates:
- training base + LoRA/merged HF artifacts
- inference GGUF + llama.cpp

## Hardware fit
The target profile is 32 GB RAM + Quadro M1000M 2 GB. Auto mode uses only free VRAM with headroom and can fall back to CPU.

## Verification done in this environment
- Python source compilation: required before release.
- Backend tests and deterministic import/route tests: run by the build verification script.
- Electron production build, C# publish, node-pty/ConPTY and CUDA on Windows: must be run on the Windows release host; this Linux environment cannot truthfully certify those binaries.
```

---

### `531/588` `REBUILD_FINAL_CHECKLIST_4.5.2.md`

- **المسار الكامل:** `F:\1f\p\ALI_Studio_Pro_Design4_4.6.0\04_Adaptive_Hybrid\REBUILD_FINAL_CHECKLIST_4.5.2.md`
- **الحجم:** 1919 بايت (1.9 KB)
- **الامتداد:** `.md`

```markdown
# ALI Studio Pro 4.5.3 — Final Rebuild Checklist

## Imported reference facts
- Previous audit: `backend/knowledge_seed/ALI_V4_4_COMPLETE_REPORT.md`
- P50 full profile: `backend/knowledge_seed/THINKPAD_P50_COMPLETE_USER_PROFILE.md`
- P50 engineering profile: `backend/knowledge_seed/THINKPAD_P50_USER_PROFILE.md`

## Functional fixes included
- continuous training base/validation paths are resolved relative to the backend root;
- active-generation ledger archives the previous generation when a new one is promoted;
- GPU VRAM used/free ordering is correct;
- unknown GPU memory occupancy is never treated as 100% free;
- `/api/memory/list` remains an alias;
- Electron starts the backend automatically and discovers the packaged runtime;
- training import accepts Markdown + JSON/JSONL + text/document formats;
- new chat / history / rename / delete are wired to persistent sessions;
- training progress reports real steps, elapsed time and ETA;
- grounded fallback prefers a matching RAG Q&A answer instead of the first chunk;
- Qwen GGUF + llama.cpp are first-class optional local inference assets;
- setup scripts provide online and offline preparation paths.

## Acceptance gates
1. Python compileall.
2. Full pytest suite.
3. Import the P50 QA pack and assert sample count.
4. Real v1 training in an isolated workspace.
5. Real v2 training from v1 in an isolated workspace.
6. Registry promotion and rollback semantics.
7. API E2E for health/status/hardware/models/memory/conversations/training/chat/search.
8. Electron main/preload/api syntax checks.
9. Windows native: Electron build, .NET publish, node-pty/ConPTY, embedded Python, CUDA self-test.
10. Final ZIP integrity.

## Release honesty
This environment is Linux. Windows-native gates 8-9 cannot be truthfully marked PASS here. The package therefore contains scripts to execute those gates on the target Windows machine instead of inventing results.
```

---

### `532/588` `RELEASE_MANIFEST_4.1.0.json`

- **المسار الكامل:** `F:\1f\p\ALI_Studio_Pro_Design4_4.6.0\04_Adaptive_Hybrid\RELEASE_MANIFEST_4.1.0.json`
- **الحجم:** 726 بايت (0.7 KB)
- **الامتداد:** `.json`

```json
{
  "name": "ALI Studio Pro Windows",
  "version": "4.2.0",
  "created_for": "Continuous Learning v1→vN",
  "file_count": 394,
  "files_sha256": "2592ba7494c75dd054aa8f33698da91f0d4d1ca04bdd7bbfac844d2378296df5",
  "verification": {
    "pytest": "148 passed, 34 skipped, 2 warnings",
    "python_compile": "216 files / 0 failures",
    "electron_syntax": "PASS",
    "e2e": "v1 then v2 promoted successfully in temporary workspace",
    "windows_native_package": "not executed in Linux"
  },
  "notable": {
    "automatic_training_after_drop": true,
    "immediate_rag_index": true,
    "cross_file_sample_dedup": true,
    "human_versions": "v1,v2,...",
    "promotion_gate": true,
    "rollback_via_registry": true
  }
}
```

---

### `533/588` `RELEASE_MANIFEST_4.2.0.json`

- **المسار الكامل:** `F:\1f\p\ALI_Studio_Pro_Design4_4.6.0\04_Adaptive_Hybrid\RELEASE_MANIFEST_4.2.0.json`
- **الحجم:** 16133 بايت (15.8 KB)
- **الامتداد:** `.json`

```json
{
  "name": "ALI Studio Pro",
  "version": "4.2.0",
  "platform": "Windows x64",
  "desktop": {
    "electron": "40.10.2",
    "node": "22.x",
    "react": "19.x",
    "terminal": "node-pty/ConPTY"
  },
  "backend": {
    "python": "3.11.9 target embedded runtime",
    "continuous_learning": true
  },
  "files": 398,
  "source_verification": {
    "python_tests": "150 passed, 34 skipped, 2 warnings",
    "json": "pass",
    "electron_cjs": "pass",
    "desktop_source_scan": "pass"
  },
  "windows_release_gates": [
    "npm install + npm run dist on Windows",
    "dotnet publish launcher on Windows",
    "populate runtime/python with Python 3.11.9",
    "populate Windows wheelhouse/dependencies",
    "bundle llama.cpp converter/quantizer if GGUF export is required"
  ],
  "not_claimed_as_executed": [
    "native Windows Electron production build",
    "native .NET publish",
    "fully bundled offline Python runtime and wheels"
  ],
  "release_files": [
    "DESIGN_REFERENCE.md",
    "VERIFICATION_REPORT_4.2.0.md",
    "UPGRADE_REPORT_4.2.0.md",
    "TRAINING_DATA_FORMAT.md",
    "FINAL_BUILD_GUIDE_4.2.0.md",
    "PROJECT_MANIFEST.json",
    "RELEASE_NOTES_4.2.0.md",
    "README.md",
    "UI_CONTROL_MATRIX_4.2.0.md",
    "RELEASE_MANIFEST_4.1.0.json",
    "VERIFICATION_REPORT.json",
    "VERIFICATION_REPORT.md",
    "RELEASE_NOTES.md",
    "CONTINUOUS_LEARNING.md",
    "UPGRADE_REPORT_4.1.0.md",
    "launcher/ALI.Portable.Launcher.csproj",
    "launcher/README.md",
    "launcher/Program.cs",
    "desktop/index.html",
    "desktop/README.md",
    "desktop/postcss.config.cjs",
    "desktop/tailwind.config.cjs",
    "desktop/package.json",
    "desktop/vite.config.js",
    "backend/SELF-MANAGER.bat",
    "backend/RELEASE_MANIFEST.json",
    "backend/ALI-AI.bat",
    "backend/TRAIN-CHAT.bat",
    "backend/HERMES_INTEGRATION_STATE.json",
    "backend/PROJECT_VERSION.json",
    "backend/runtime_knowledge.sqlite3",
    "backend/RUN-BENCHMARK.bat",
    "backend/requirements.txt",
    "backend/REPAIR-WINDOWS-DEPS.bat",
    "backend/CONTINUOUS_LEARNING_README.md",
    "backend/runtime_kca.sqlite3",
    "backend/SETUP-HERMES.bat",
    "backend/RUN-ALL-TESTS.bat",
    "backend/RUN-DOCTOR.bat",
    "backend/WINDOWS_DEPENDENCY_FIX.json",
    "backend/README_P50.md",
    "backend/RUN-MODEL-SMOKE.bat",
    "backend/requirements-windows.txt",
    "backend/runtime_kca.sqlite3-wal",
    "backend/START.bat",
    "backend/README.md",
    "backend/ali_agent.py",
    "backend/RUN-TESTS.bat",
    "backend/README_WINDOWS.md",
    "backend/START-OFFLINE.bat",
    "backend/SETUP-OFFLINE.bat",
    "backend/ali_ai.py",
    "backend/PHASE2_CATALOG.md",
    "backend/ALI_AI_2.5_FULL_PROJECT_SOURCE.md",
    "backend/TRAIN-ALI.bat",
    "backend/requirements-core.txt",
    "backend/RUN-KCA-DOCTOR.bat",
    "backend/runtime_conversations.sqlite3",
    "backend/ALI_AI_2.6_FULL_PROJECT_SOURCE.md",
    "backend/BUILD_EXE.bat",
    "backend/RUN-HERMES-DOCTOR.bat",
    "backend/README_WINDOWS_FINAL.md",
    "backend/SETUP-OPTIONAL.bat",
    "backend/HARVEST-AND-BUILD.bat",
    "backend/ali_agent.py.legacy",
    "backend/RELEASE_NOTES.md",
    "backend/FINAL_VERIFICATION.json",
    "backend/runtime_memory.sqlite3",
    "backend/.env.example",
    "backend/requirements-optional.txt",
    "backend/SETUP.bat",
    "backend/runtime_kca.sqlite3-shm",
    "backend/runtime_audit.sqlite3",
    "backend/pytest.ini",
    "runtime/README.md",
    "scripts/BUILD_DESKTOP.bat",
    "scripts/BUILD_PORTABLE.bat",
    "scripts/VERIFY_ALL.bat",
    "scripts/VERIFY_DESKTOP_SOURCE.py",
    "scripts/START_DEV.bat",
    "backend/multimodal/train.py",
    "backend/multimodal/model.py",
    "backend/multimodal/__init__.py",
    "backend/multimodal/media.py",
    "backend/multimodal/dataset.py",
    "backend/multimodal/inference.py",
    "backend/web-ui-tui/README.md",
    "backend/memory/manager.py",
    "backend/memory/__init__.py",
    "backend/memory/conversations.py",
    "backend/tools/project.py",
    "backend/tools/base.py",
    "backend/tools/registry.py",
    "backend/tools/terminal_stream.py",
    "backend/tools/__init__.py",
    "backend/tools/gguf.py",
    "backend/tools/terminal.py",
    "backend/tools/filesystem.py",
    "backend/tools/web.py",
    "backend/tools/git.py",
    "backend/ui/widgets.py",
    "backend/ui/rtl.py",
    "backend/ui/ali_professional_shell.py",
    "backend/ui/theme.py",
    "backend/ui/__init__.py",
    "backend/ui/preview.py",
    "backend/ui/activity.py",
    "backend/libraries/README.md",
    "backend/data_engine/parsers.py",
    "backend/data_engine/kca_dataset.py",
    "backend/data_engine/dataset_builder.py",
    "backend/data_engine/review.py",
    "backend/data_engine/dedup.py",
    "backend/data_engine/__init__.py",
    "backend/data_engine/ocr.py",
    "backend/data_engine/harvester.py",
    "backend/data_engine/normalization.py",
    "backend/data_engine/ledger.py",
    "backend/config/device_profiles.py",
    "backend/config/paths.py",
    "backend/config/app_config.py",
    "backend/config/__init__.py",
    "backend/config/hardware_profile.json",
    "backend/config/hardware_override.example.json",
    "backend/config/hermes_integration.json",
    "backend/config/i18n.py",
    "backend/config/default_config.json",
    "backend/plugins/registry.py",
    "backend/plugins/loader.py",
    "backend/docs/V0.7.2_FINAL_GATE.md",
    "backend/docs/ARCHITECTURE_2.1.md",
    "backend/docs/V0.7.2_REPORT.md",
    "backend/docs/DEVELOPMENT.md",
    "backend/docs/WINDOWS_DEPENDENCIES.md",
    "backend/docs/ROADMAP.md",
    "backend/docs/HERMES_INTEGRATION.md",
    "backend/docs/AI_KCA_MASTER.md",
    "backend/docs/UI_2.0.md",
    "backend/docs/V0.7.3_REPORT.md",
    "backend/docs/WINDOWS_P50_PROFILE.md",
    "backend/docs/UI_2.4.md",
    "backend/docs/README.md",
    "backend/docs/HARDWARE_P50.md",
    "backend/docs/TOKENIZER.md",
    "backend/docs/VERIFICATION_2.0.md",
    "backend/docs/V0.5_REPORT.md",
    "backend/docs/OPERATIONS_2.0.md",
    "backend/docs/ARCHITECTURE.md",
    "backend/docs/ARCHITECTURE_V3.0.md",
    "backend/docs/ALI_AI_2.5_FULL_PROJECT_SOURCE.md",
    "backend/docs/ARCHITECTURE_2.0.md",
    "backend/docs/VERIFICATION_2.1.md",
    "backend/docs/V0.7.2_FINAL_EVIDENCE.md",
    "backend/docs/REFERENCES.md",
    "backend/docs/PROJECT_AUDIT.md",
    "backend/docs/RELEASE_NOTES.md",
    "backend/docs/V0.7_REPORT.md",
    "backend/docs/KNOWLEDGE.md",
    "backend/docs/WEIGHTS_LIFECYCLE_2.0.md",
    "backend/docs/V0.6_REPORT.md",
    "backend/docs/PROJECT_CONTRACT.md",
    "backend/api/__init__.py",
    "backend/api/server.py",
    "backend/optional-mcps/client.py",
    "backend/optional-mcps/README.md",
    "backend/vendor/README.md",
    "backend/skills/registry.py",
    "backend/skills/loader.py",
    "backend/skills/project-builder.md",
    "backend/skills/README.md",
    "backend/control_plane/contracts.py",
    "backend/control_plane/execution.py",
    "backend/control_plane/function_registry.json",
    "backend/control_plane/__init__.py",
    "backend/control_plane/README.md",
    "backend/control_plane/state_store.py",
    "backend/control_plane/kca_registry.py",
    "backend/control_plane/router.py",
    "backend/agent/project_orchestrator.py",
    "backend/agent/README.md",
    "backend/evaluation/suite.py",
    "backend/evaluation/report.py",
    "backend/evaluation/README.md",
    "backend/core/runtime.py",
    "backend/core/workflow.py",
    "backend/core/orchestrator.py",
    "backend/core/response_guard.py",
    "backend/core/job_manager.py",
    "backend/core/events.py",
    "backend/core/__init__.py",
    "backend/core/audit.py",
    "backend/core/logger.py",
    "backend/core/tool_protocol.py",
    "backend/core/session_store.py",
    "backend/core/agent.py",
    "backend/core/context.py",
    "backend/CLI/ali.py",
    "backend/artifacts/accumulated_training.sqlite3",
    "backend/artifacts/models.sqlite3",
    "backend/artifacts/ali.sqlite3",
    "backend/artifacts/release_check.json",
    "backend/nix/README.md",
    "backend/models/README.md",
    "backend/models/models.sqlite3",
    "backend/providers/local_ali.py",
    "backend/knowledge/rag.py",
    "backend/knowledge/__init__.py",
    "backend/knowledge/ingest.py",
    "backend/knowledge/embeddings.py",
    "backend/knowledge/store.py",
    "backend/research/__init__.py",
    "backend/research/store.py",
    "backend/research/downloads.py",
    "backend/research/web.py",
    "backend/autonomy/policy.py",
    "backend/autonomy/__init__.py",
    "backend/autonomy/improvement.py",
    "backend/autonomy/continuous.py",
    "backend/autonomy/jobs.py",
    "backend/autonomy/agent_loop.py",
    "backend/autonomy/self_manager.py",
    "backend/security/paths.py",
    "backend/security/commands.py",
    "backend/security/__init__.py",
    "backend/security/permissions.py",
    "backend/optional_mcps/client.py",
    "backend/optional_mcps/__init__.py",
    "backend/model/manager.py",
    "backend/model/weights_manager.py",
    "backend/model/artifacts.py",
    "backend/model/importer.py",
    "backend/model/model.py",
    "backend/model/ali_lm.py",
    "backend/model/registry.py",
    "backend/model/__init__.py",
    "backend/assistant/orchestrator.py",
    "backend/assistant/__init__.py",
    "backend/assistant/verifier.py",
    "backend/assistant/error_learning.py",
    "backend/assistant/context.py",
    "backend/web/policy.py",
    "backend/web/README.md",
    "backend/tokenizer/manager.py",
    "backend/tokenizer/serialization.py",
    "backend/tokenizer/tokenizer.py",
    "backend/tokenizer/spm.py",
    "backend/tokenizer/__init__.py",
    "backend/tokenizer/vocabulary.py",
    "backend/tokenizer/config.py",
    "backend/tokenizer/train_tokenizer.py",
    "backend/tokenizer/trainer.py",
    "backend/runtime/paths.py",
    "backend/runtime/__init__.py",
    "backend/runtime/hardware.py",
    "backend/runtime/resources.py",
    "backend/runtime/doctor.py",
    "backend/runtime/device_policy.py",
    "backend/training/evaluator.py",
    "backend/training/curriculum.py",
    "backend/training/manifest.py",
    "backend/training/scaling.py",