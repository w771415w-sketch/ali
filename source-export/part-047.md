    "todoist",
    "twilio-docs",
    "unreal-engine",
    "vercel",
    "webflow",
    "wolfram",
    "wordpress-com"
  ],
  "note": "Source request listed 65 ready servers but only these names were explicitly provided; remaining slots are intentionally left unassigned.",
  "enabled_by_default": false
}
```

---

### `270/588` `backend/phase2/phase2_roadmap.json`

- **المسار الكامل:** `F:\1f\p\ALI_Studio_Pro_Design4_4.6.0\04_Adaptive_Hybrid\backend/phase2/phase2_roadmap.json`
- **الحجم:** 602 بايت (0.6 KB)
- **الامتداد:** `.json`

```json
{
  "phase": "2-preparation",
  "status": "catalog-ready-not-activated",
  "stages": [
    "provider adapters",
    "search router",
    "MCP gateway",
    "skill marketplace/loader",
    "tool gateway",
    "browser/CDP automation",
    "computer-use with confirmation",
    "cron scheduler",
    "subagent orchestration",
    "messaging connectors",
    "education/skill learning loop",
    "voice IO",
    "multimodal"
  ],
  "safety_defaults": {
    "internet": false,
    "external_connectors": false,
    "computer_control": false,
    "scheduler": false,
    "model_remote_download": false
  }
}
```

---

### `271/588` `backend/phase2/platforms.json`

- **المسار الكامل:** `F:\1f\p\ALI_Studio_Pro_Design4_4.6.0\04_Adaptive_Hybrid\backend/phase2/platforms.json`
- **الحجم:** 220 بايت (0.2 KB)
- **الامتداد:** `.json`

```json
{
  "messaging_platform_slots": 22,
  "defined_names": [],
  "status": "prepared_for_phase_2",
  "enabled_by_default": false,
  "reason": "The request specifies 22 messaging platforms but does not provide their names."
}
```

---

### `272/588` `backend/phase2/providers.json`

- **المسار الكامل:** `F:\1f\p\ALI_Studio_Pro_Design4_4.6.0\04_Adaptive_Hybrid\backend/phase2/providers.json`
- **الحجم:** 446 بايت (0.4 KB)
- **الامتداد:** `.json`

```json
{
  "image_providers": [
    "openai",
    "openai-codex",
    "deepinfra",
    "fal",
    "krea",
    "openrouter",
    "xai"
  ],
  "video_providers": [
    "xai",
    "deepinfra",
    "fal"
  ],
  "search_providers": [
    "brave_free",
    "ddgs",
    "exa",
    "firecrawl",
    "keenable",
    "parallel",
    "searxng",
    "tavily",
    "xai"
  ],
  "policy": "catalog-only; credentials are never bundled",
  "enabled_by_default": false
}
```

---

### `273/588` `backend/phase2/README.md`

- **المسار الكامل:** `F:\1f\p\ALI_Studio_Pro_Design4_4.6.0\04_Adaptive_Hybrid\backend/phase2/README.md`
- **الحجم:** 399 بايت (0.4 KB)
- **الامتداد:** `.md`

```markdown
# ALI AI 2.5 — Phase-2 Integration Catalog

This directory is a preparation contract only. It records providers, search engines, MCP servers, skills, toolsets, messaging-platform slots and future runtime capabilities requested for a later development stage.

All entries are `disabled_by_default`. No credentials are bundled. Names not explicitly supplied by the source request remain unassigned.
```

---

### `274/588` `backend/phase2/skills.json`

- **المسار الكامل:** `F:\1f\p\ALI_Studio_Pro_Design4_4.6.0\04_Adaptive_Hybrid\backend/phase2/skills.json`
- **الحجم:** 1640 بايت (1.6 KB)
- **الامتداد:** `.json`

```json
{
  "requested_total": 58,
  "categories": {
    "apple": [
      "notes",
      "reminders",
      "findmy",
      "imessage"
    ],
    "autonomous-ai-agents": [
      "claude-code",
      "codex",
      "computer-use",
      "ALI-agent",
      "opencode"
    ],
    "creative": [
      "architecture-diagram",
      "ascii-video",
      "baoyu-infographic",
      "claude-design",
      "design-md",
      "humanizer",
      "manim-video",
      "p5js",
      "popular-web-designs",
      "songwriting"
    ],
    "devops": [
      "sdlc-review"
    ],
    "email": [
      "inbox-triage",
      "himalaya"
    ],
    "media": [
      "gif-search",
      "songsee",
      "youtube-content"
    ],
    "note-taking": [
      "obsidian"
    ],
    "productivity": [
      "airtable",
      "box",
      "docx",
      "google-workspace",
      "maps",
      "meeting-action-items",
      "notion",
      "pdf",
      "powerpoint",
      "product-price-monitor",
      "teams-meeting-pipeline",
      "weekly-review",
      "xlsx",
      "document-to-action-items"
    ],
    "research": [
      "arxiv",
      "competitor-news",
      "grounded-citations",
      "llm-wiki"
    ],
    "social-media": [
      "xurl"
    ],
    "software-development": [
      "codebase-inspection",
      "dogfood",
      "github",
      "ALI-skill-authoring",
      "inspecting-dom",
      "node-inspect",
      "python-debugpy",
      "requesting-code-review",
      "simplify-code",
      "spike",
      "systematic-debugging",
      "tdd"
    ],
    "web": [
      "blocked-page-recovery"
    ]
  },
  "listed_total": 58,
  "enabled_by_default": false
}
```

---

### `275/588` `backend/phase2/toolsets.json`

- **المسار الكامل:** `F:\1f\p\ALI_Studio_Pro_Design4_4.6.0\04_Adaptive_Hybrid\backend/phase2/toolsets.json`
- **الحجم:** 896 بايت (0.9 KB)
- **الامتداد:** `.json`

```json
{
  "requested_toolsets": 58,
  "catalog": {
    "web": [
      "web",
      "search",
      "x_search",
      "browser",
      "video_analyze",
      "vision_analyze",
      "homeassistant",
      "feishu_doc",
      "feishu_drive"
    ],
    "files_code": [
      "file",
      "terminal",
      "code_execution",
      "delegate_task"
    ],
    "creative_media": [
      "image_gen",
      "video_gen",
      "tts",
      "creative"
    ],
    "intelligence_control": [
      "skills",
      "todo",
      "memory",
      "session_search",
      "cronjob",
      "clarify"
    ],
    "planned": [
      "voice",
      "subagents",
      "browser_use",
      "computer_use"
    ],
    "enabled_by_default": false
  },
  "note": "The request states 58 toolsets while only the explicitly named toolsets are recorded here; no unnamed capabilities are fabricated.",
  "enabled_by_default": false
}
```

---

### `276/588` `backend/PHASE2_CATALOG.md`

- **المسار الكامل:** `F:\1f\p\ALI_Studio_Pro_Design4_4.6.0\04_Adaptive_Hybrid\backend/PHASE2_CATALOG.md`
- **الحجم:** 1786 بايت (1.7 KB)
- **الامتداد:** `.md`

```markdown
# ALI AI 2.5.0 — Phase-2 Capability Catalog

هذه القائمة محفوظة داخل المشروع كعقدة تحضير للمرحلة التالية فقط. العناصر الخارجية والامتدادات ذات الصلاحيات لا تعمل تلقائيًا في إصدار 2.5.0.

## Image / Video providers

Images: `openai`, `openai-codex`, `deepinfra`, `fal`, `krea`, `openrouter`, `xai`

Video: `xai`, `deepinfra`, `fal`

## Search engines

`brave_free`, `ddgs`, `exa`, `firecrawl`, `keenable`, `parallel`, `searxng`, `tavily`, `xai`

## MCP servers

The project records the 46 server names explicitly supplied in the request. The request states 65 total, so the remaining 19 names are intentionally left unassigned rather than invented.

## Skills

The supplied list is stored exactly by category in `phase2/skills.json` and contains 58 named skills across the requested categories.

## Toolsets

The named toolsets supplied in the request are recorded in `phase2/toolsets.json`. The request states 58 toolsets overall, but only the names provided in the request are recorded.

## Messaging platforms

The request states 22 platforms but does not provide their names. The project keeps 22 reserved slots in `phase2/platforms.json` without inventing connector names.

## Future runtime surfaces

Prepared contracts include: terminal, browser/CDP, computer-use with confirmation gates, cron scheduling, subagents, memory/session search, skills loader, provider router, MCP gateway, multimodal analysis/generation, voice, messaging connectors and an educational/self-improvement loop.

## Security rule

No API keys, OAuth tokens, passwords, private `.env` values, `auth.json`, machine UUIDs or personal connector credentials are included in this project bundle.
```

---

### `277/588` `backend/plugins/example_local/plugin.json`

- **المسار الكامل:** `F:\1f\p\ALI_Studio_Pro_Design4_4.6.0\04_Adaptive_Hybrid\backend/plugins/example_local/plugin.json`
- **الحجم:** 131 بايت (0.1 KB)
- **الامتداد:** `.json`

```json
{"name":"example_local","version":"1.0.0","enabled":false,"entry":"plugin.py","description":"Disabled-by-default plugin example."}
```

---

### `278/588` `backend/plugins/example_local/plugin.py`

- **المسار الكامل:** `F:\1f\p\ALI_Studio_Pro_Design4_4.6.0\04_Adaptive_Hybrid\backend/plugins/example_local/plugin.py`
- **الحجم:** 44 بايت (0.0 KB)
- **الامتداد:** `.py`

```python
def register(registry):
    return registry
```

---

### `279/588` `backend/plugins/loader.py`

- **المسار الكامل:** `F:\1f\p\ALI_Studio_Pro_Design4_4.6.0\04_Adaptive_Hybrid\backend/plugins/loader.py`
- **الحجم:** 595 بايت (0.6 KB)
- **الامتداد:** `.py`

```python
# -*- coding: utf-8 -*-
from __future__ import annotations
from pathlib import Path
import json, importlib.util

def discover(root:str|Path='plugins'):
    root=Path(root); out=[]
    for p in root.glob('*/plugin.json'):
        try:o=json.loads(p.read_text(encoding='utf-8')); o['_path']=str(p.parent); out.append(o)
        except Exception: pass
    return out

def load_python_plugin(path:str|Path):
    p=Path(path); spec=importlib.util.spec_from_file_location('ali_plugin_'+p.stem,p); mod=importlib.util.module_from_spec(spec); assert spec.loader; spec.loader.exec_module(mod); return mod
```

---

### `280/588` `backend/plugins/registry.py`

- **المسار الكامل:** `F:\1f\p\ALI_Studio_Pro_Design4_4.6.0\04_Adaptive_Hybrid\backend/plugins/registry.py`
- **الحجم:** 409 بايت (0.4 KB)
- **الامتداد:** `.py`

```python
# -*- coding: utf-8 -*-
from __future__ import annotations
from pathlib import Path
import json
class PluginRegistry:
    def __init__(self,root):self.root=Path(root)
    def discover(self):
        out=[]
        for p in self.root.glob('*/plugin.json'):
            try:d=json.loads(p.read_text(encoding='utf-8')); d['path']=str(p.parent); out.append(d)
            except Exception:pass
        return out
```

---

### `281/588` `backend/PROJECT_VERSION.json`

- **المسار الكامل:** `F:\1f\p\ALI_Studio_Pro_Design4_4.6.0\04_Adaptive_Hybrid\backend/PROJECT_VERSION.json`
- **الحجم:** 909 بايت (0.9 KB)
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
  "upgraded_from": "4.5.8"
}
```

---

### `282/588` `backend/providers/local_ali.py`

- **المسار الكامل:** `F:\1f\p\ALI_Studio_Pro_Design4_4.6.0\04_Adaptive_Hybrid\backend/providers/local_ali.py`
- **الحجم:** 467 بايت (0.5 KB)
- **الامتداد:** `.py`

```python
# -*- coding: utf-8 -*-
"""First-party provider: ALI's own trained model only."""
from inference.engine import LocalInference
class LocalALIProvider:
    name='local-ali'
    def __init__(self,model_dir,tokenizer_dir=None,device='cpu'):self.engine=LocalInference(model_dir,tokenizer_dir,device)
    def stream(self,messages,**kwargs):return self.engine.stream(messages,**kwargs)
    def complete(self,messages,**kwargs):return self.engine.complete(messages,**kwargs)
```

---

### `283/588` `backend/pytest.ini`

- **المسار الكامل:** `F:\1f\p\ALI_Studio_Pro_Design4_4.6.0\04_Adaptive_Hybrid\backend/pytest.ini`
- **الحجم:** 241 بايت (0.2 KB)
- **الامتداد:** `.ini`

```ini
[pytest]
testpaths = tests
addopts = -ra --ignore=tests/test_tokenizer_v072.py
norecursedirs = .git .venv venv build dist checkpoints weights artifacts runtime/python/Lib runtime/python/Lib/test runtime/python/Lib/tests desktop/node_modules
```

---

### `284/588` `backend/README.md`

- **المسار الكامل:** `F:\1f\p\ALI_Studio_Pro_Design4_4.6.0\04_Adaptive_Hybrid\backend/README.md`
- **الحجم:** 2079 بايت (2.0 KB)
- **الامتداد:** `.md`

```markdown
# ALI AI 2.5.0 — Unified KCA / Local AI Engineering Platform

ALI AI 2.5.0 is the unified release built on the existing ALI AI 2.0 foundations and the AI-KCA 3.0 operational architecture. The desktop UI, runtime, training, tokenizer, memory/RAG, tools and artifact registry remain separate layers so they can evolve without rewriting the application shell.

## What is real

- PyTorch decoder-only language model with from-scratch and continuation training paths.
- Versioned SentencePiece tokenizer lifecycle with corpus hashing and deterministic reuse.
- Full-parameter training, dependency-light LoRA, checkpoints and safe resume.
- Progressive training stages: `base → sft → lora → merged`.
- Evaluation plus candidate/promotion gate; inactive candidates never replace the active model in place.
- Dataset harvesting, normalization, deduplication, provenance and train/validation/test separation.
- Persistent memory and local knowledge/RAG kept separate from learned weights.
- Permissioned tools with audit logging and bounded tool-calling.
- HF export and a real llama.cpp GGUF conversion/validation bridge.
- Professional three-pane desktop UI with local chat, streaming, project explorer, editor, terminal, jobs, models and device monitoring.
- Central weight/artifact import: `models/inbox → inspect → install → verify → registry`.
- Explicit artifact manifests with SHA-256, lineage, training metadata and evaluation metadata.
- CPU-first P50 operation with an explicit CUDA/DDP path for stronger systems.
- Autonomous incremental learning from approved, deduplicated conversations with candidate evaluation and promotion gating.
- Included small bootstrap and P50 datasets so the source bundle can train immediately after dependency installation.

## Important separation: data ≠ weights

A conversation JSONL file is training data. A tokenizer model is a tokenizer artifact. A checkpoint contains tensors. A LoRA adapter is a specialization artifact. A GGUF file is a deployment artifact. The system never treats arbitrary numeric JSON as a model.
```

---

### `285/588` `backend/README_P50.md`

- **المسار الكامل:** `F:\1f\p\ALI_Studio_Pro_Design4_4.6.0\04_Adaptive_Hybrid\backend/README_P50.md`
- **الحجم:** 962 بايت (0.9 KB)
- **الامتداد:** `.md`

```markdown
# ALI AI 2.5 — ThinkPad P50 profile / Professional Assistant

This profile is tuned for the supplied ThinkPad P50 class: 4 physical / 8 logical CPU threads, 32 GB RAM and a 2 GB Quadro M1000M.

## Defaults

- Training: CPU-first
- Torch threads: 6
- Torch inter-op threads: 1
- Batch size: 1
- Gradient accumulation: 16
- Sequence length: 256
- Inference context: 384
- New tokens: 192
- AMP: disabled
- Bootstrap model: `micro`
- Local research model: `small`

## Data

`data/training/device_p50/` is included in this source bundle as a deterministic 600-record subset of the curriculum (480 train / 60 validation / 60 test). The full curriculum dataset is also included for longer training.

## Storage recommendation

Use the NVMe drive for active models, checkpoints and datasets. Use the HDD for archived checkpoints and older datasets. Do not put training checkpoints on the Windows system partition when a fast data partition is available.

## Commands
```

---

### `286/588` `backend/README_WINDOWS.md`

- **المسار الكامل:** `F:\1f\p\ALI_Studio_Pro_Design4_4.6.0\04_Adaptive_Hybrid\backend/README_WINDOWS.md`
- **الحجم:** 2596 بايت (2.5 KB)
- **الامتداد:** `.md`

```markdown
# ALI AI 2.5.0 — Windows Installation and Runtime Guide

## Included in this project

- Professional Tkinter desktop shell matching the supplied light UI reference.
- Three-pane workspace with conversations/projects/files on the left, chat in the center, and developer/telemetry/health surfaces on the right.
- Live Execution Monitor below the developer notebook; it displays active job, phase, detail and progress while work is running.
- Accumulated Markdown Training Center with validation, secret redaction, deduplication, incremental cursor protection, LoRA adapters and threshold-based merge candidates.
- KCA control plane, local memory/RAG layers, dataset and training pipeline, model registry and GGUF validation/conversion bridge.
- Phase-2 catalog only: future image/video providers, search engines, MCP servers, skills, toolsets, browser/CDP, computer-use, cron, subagents and messaging connectors are recorded in `phase2/` and disabled by default.
- A functional micro bootstrap model is included at `models/active/ALI-Bootstrap-v2.5/` for startup and inference smoke tests.

## Windows setup

1. Install 64-bit Python.
2. Extract this project to a normal writable path such as `D:\ALI-AI`.
3. Run `SETUP.bat`.
4. Run `RUN-ALL-TESTS.bat`.
5. Run `START.bat`.

## Optional external runtime

GGUF execution is intentionally separated from the core Python application. When you later install a compatible `llama.cpp` Windows build, place/configure the runtime path through the model/runtime settings and keep GGUF files under `models/gguf/`.

## Model note

The included bootstrap model is a small model trained from scratch for pipeline/startup validation. It is not a large production-quality assistant model. The application can load it immediately, while larger models may be imported into `models/inbox/` and then validated through the model manager.

## Phase-2 policy

`phase2/*.json` contains the exact names supplied for the future integration stage. Unspecified names (for example, the user's 22 messaging platforms) remain empty rather than being invented. No provider credentials, API keys, OAuth tokens or private connector data are bundled.

## Portable EXE

Run `BUILD_EXE.bat` after `SETUP.bat`. It produces `dist\\ALI-AI\\` as an onedir application with the bootstrap model and phase-2 catalogs included.


## Continuous Learning 4.1
Drag training files into the Electron Training Center. Accepted Q/A data is deduplicated, indexed into RAG immediately, trained incrementally from the current Active model, evaluated, and versioned as v1, v2, v3... before promotion.
```

---

### `287/588` `backend/README_WINDOWS_FINAL.md`

- **المسار الكامل:** `F:\1f\p\ALI_Studio_Pro_Design4_4.6.0\04_Adaptive_Hybrid\backend/README_WINDOWS_FINAL.md`
- **الحجم:** 1703 بايت (1.7 KB)
- **الامتداد:** `.md`

```markdown
# ALI AI Windows Deployment — P50 profile + Hermes

## Target
The build is tuned for a Lenovo ThinkPad P50 class workstation: 4 physical CPU cores / 8 logical threads, 32 GB RAM, and a 2 GB Quadro-class legacy GPU. Training defaults are CPU-first to avoid relying on 2 GB VRAM.

## Install
1. Install Python 3.13.x 64-bit.
2. Extract the selected project folder to `D:\ALI-AI`.
3. Run `SETUP.bat`.
4. Run `RUN-ALL-TESTS.bat`.
5. Run `START.bat`.

## Hermes
Keep Hermes separately at `D:\AI ALI\Hermes\`. Do not copy `.env` or `auth.json` into ALI. In the Hermes variants, the adapter reads only approved read-only files and SELECT/PRAGMA database data.

Use `RUN-HERMES-DOCTOR.bat` to inspect the configured external Hermes path. ALI still starts when Hermes is absent.

## Training
Use `Training Files` in the desktop UI and drop `.md` files. The manager validates, normalizes, redacts secrets, deduplicates, creates an incremental dataset, produces LoRA adapters, and waits for the configured merge threshold before creating a candidate merge.

## Included model
`models/active/ALI-Bootstrap-v2.5/` contains a small real bootstrap model for local smoke/inference/training tests. It is intentionally small for this hardware profile; it is not a 3B production model.

## Build EXE
Run `BUILD_EXE.bat` after setup. Python itself, GPU drivers, and platform-specific large wheel caches are not embedded because they are environment-specific.


## Continuous Learning 4.1
Drag training files into the Electron Training Center. Accepted Q/A data is deduplicated, indexed into RAG immediately, trained incrementally from the current Active model, evaluated, and versioned as v1, v2, v3... before promotion.
```

---

### `288/588` `backend/RELEASE_MANIFEST.json`

- **المسار الكامل:** `F:\1f\p\ALI_Studio_Pro_Design4_4.6.0\04_Adaptive_Hybrid\backend/RELEASE_MANIFEST.json`
- **الحجم:** 48625 بايت (47.5 KB)
- **الامتداد:** `.json`

```json
{
  "name": "ALI AI",
  "version": "4.5.2",
  "codename": "Unified-KCA-P50",
  "generated_at": 1791040131.2848713,
  "files": [
    {
      "path": "ALI-AI.bat",
      "size": 25,
      "sha256": "a441f1a29d6e68bc374e7a476f8e0454326017a70b2570f8ea95b0307e368d8f"
    },
    {
      "path": "ALI_AI_2.5_FULL_PROJECT_SOURCE.md",
      "size": 3918232,
      "sha256": "927083d63541e753be54d5206ec2007bc66ce528ea934660b818342c77ffc7a0"
    },
    {
      "path": "BUILD_EXE.bat",
      "size": 1611,
      "sha256": "8abab974cda45a93112fa396c4874c457b07a4cb3eccfbbb05f03027073187fa"
    },
    {
      "path": "CLI/ali.py",
      "size": 681,
      "sha256": "634b610c693e6b1327332f181cb78d8d852b6ad90f3e4fc2cc4e017c6d511a3b"
    },
    {
      "path": "HARVEST-AND-BUILD.bat",
      "size": 434,
      "sha256": "30eb06cd0a5f1747a81f21fc54972e471a71036690e7861ed19532bcf23e2e9f"
    },
    {
      "path": "PHASE2_CATALOG.md",
      "size": 1786,
      "sha256": "5ed1e82eba1f8e6622b6e0ddb66bfd1ec1a2e5e07ff07882d38d5b5a6404a719"
    },
    {
      "path": "PROJECT_VERSION.json",
      "size": 504,
      "sha256": "756feb04301bff2fea8835edba2181138cf4c2698c94149f2a3e702ff66d9c5a"
    },
    {
      "path": "README.md",
      "size": 6183,
      "sha256": "867159f5f9482f93153f88a52326479bee5cc59e274abb389ca86a92f3cc836b"
    },
    {
      "path": "README_P50.md",
      "size": 2967,
      "sha256": "b3872c03955c1c5adf2cfe9bee2efa7af0a72c77c2a96d3e4fa70e9df398fa9d"
    },
    {
      "path": "README_WINDOWS.md",
      "size": 2334,
      "sha256": "0eb2ebecaa16d251cda57f70e6ac263f2d9faa0035b6bb996f97f35442bde569"
    },
    {
      "path": "RELEASE_NOTES.md",
      "size": 2159,
      "sha256": "d5087d70758d4caca0d2458d7fe1842fb807da6edc116cdc01e7a56db122b8ee"
    },
    {
      "path": "RUN-ALL-TESTS.bat",
      "size": 345,
      "sha256": "9c4047c594d2c228947939ccdd860d0e6a0776ffbc01480220ff33a8f1268bd9"
    },
    {
      "path": "RUN-BENCHMARK.bat",
      "size": 179,
      "sha256": "2229b7a0f8ca4ce1e5e9eff2edabe9b37114808d765168d13e9abeba4aaa1455"
    },
    {
      "path": "RUN-DOCTOR.bat",
      "size": 153,
      "sha256": "67eede61bc6b88bd6920cee024e6eb19adf048443b219b117ab97f9b2d87c88a"
    },
    {
      "path": "RUN-KCA-DOCTOR.bat",
      "size": 200,
      "sha256": "64fd0f494a3a8a31530b399722dfa9b3bad278e5a45dd60e951620c3ac638d54"
    },
    {
      "path": "RUN-MODEL-SMOKE.bat",
      "size": 212,
      "sha256": "376402ea101864ff623531bc06ce9f182ec80ce39292c1a9a1d5a75f7ba4eaea"
    },
    {
      "path": "RUN-TESTS.bat",
      "size": 173,
      "sha256": "d668d73eef8ce52eeae490661353939237ead3f34b6ef42296e01b8078329eef"
    },
    {
      "path": "SELF-MANAGER.bat",
      "size": 158,
      "sha256": "3b1d6b1234b2a198b392776157069075d6a75c2bd4c891113b723f69dcdb52a8"
    },
    {
      "path": "SETUP-OPTIONAL.bat",
      "size": 350,
      "sha256": "19dc208e269d2b7943bd35d0c8f58ba509dbec5327e3f804a8251938f407cf84"
    },
    {
      "path": "SETUP.bat",
      "size": 1398,
      "sha256": "937734e778d751c9045e0a7fa32f690485e11330a0bc902634f79f1948d0ef1b"
    },
    {
      "path": "START.bat",
      "size": 282,
      "sha256": "7207361a9240b281c10f2f3484f37d590e18a02e1cdc2606d509b50da18a5670"
    },
    {
      "path": "TRAIN-ALI.bat",
      "size": 339,
      "sha256": "5fa3a2808117f69699c1dfe31de1b43178eeddbbe69de32149f60cbb645375b4"
    },
    {
      "path": "TRAIN-CHAT.bat",
      "size": 350,
      "sha256": "a1b5cdcc20224e0f72b8fd0327bba7e060a25373775bd842ff751f166812d9fa"
    },
    {
      "path": "agent/README.md",
      "size": 85,
      "sha256": "0bd0723421f81530d9c156525046b90d58bcf41223ed86ff3a25d2d584130017"
    },
    {
      "path": "agent/project_orchestrator.py",
      "size": 2423,
      "sha256": "9cd0bfa1130a5788e65af9260807c8180b021774cdcf883d43172e3bcd86724c"
    },
    {
      "path": "agent/recipes/project_change_cycle.md",
      "size": 137,
      "sha256": "6ee9a1d42e55b52e33830b949e8c916d45665e8a5a220835c69e3e43bcfd1d0d"
    },
    {
      "path": "ali_agent.py",
      "size": 2895,
      "sha256": "52940f2a10fbe2e331240b4ce86ced435136051ad223e78539b62e4fa190bbde"
    },
    {
      "path": "ali_agent.py.legacy",
      "size": 151,
      "sha256": "ad08bc5bde88df9d239142dba71665a2323d341353e299ea46af74e03cd19e63"
    },
    {
      "path": "ali_ai.py",
      "size": 78484,
      "sha256": "8af7e6514fdf219d5e085e4c6bb20d7fa7e59da1922f4cc619daa7eb625ba1ca"
    },
    {
      "path": "api/__init__.py",
      "size": 1,
      "sha256": "01ba4719c80b6fe911b091a7c05124b64eeece964e09c058ef8f9805daca546b"
    },
    {
      "path": "api/server.py",
      "size": 2343,
      "sha256": "08b5594eb81d809fb5c07d1385d839b65acc5e304428775fb51eb39d4eaf8429"
    },
    {
      "path": "artifacts/release_check.json",
      "size": 4193,
      "sha256": "61f522576f6ee2ba15e6bb4037a8ca286e0a32367f6b085d3881154fc42dd92d"
    },
    {
      "path": "assistant/__init__.py",
      "size": 83,
      "sha256": "140b4965ee799fe120ee308940df473c27265a8def51b955c10a6834c37a5d34"
    },
    {
      "path": "assistant/context.py",
      "size": 828,
      "sha256": "3ee3027756a05092f61adcb70a8fecc6b67a2f3a1d210755780c6bd5ecf7fd57"
    },
    {
      "path": "assistant/error_learning.py",
      "size": 1052,
      "sha256": "fcc3242911c8152eeb84b298d9fd7c5cb36dbaf2eed74d86e294bf64f441e773"
    },
    {
      "path": "assistant/orchestrator.py",
      "size": 1768,
      "sha256": "320b523e0be29bc846bd96384178f5b8724da9f26c2a4bbeacb2b46558517dff"
    },
    {
      "path": "assistant/verifier.py",
      "size": 679,
      "sha256": "6e1df5c00b5c6e688bc943b3738dfb92496c890e9e78d13c81c3d7dcc56a3bf6"
    },
    {
      "path": "autonomy/__init__.py",
      "size": 1,
      "sha256": "01ba4719c80b6fe911b091a7c05124b64eeece964e09c058ef8f9805daca546b"
    },
    {
      "path": "autonomy/agent_loop.py",
      "size": 2828,
      "sha256": "14a4bf25b906d7c38fa10608b3e68365ef337777dd45d63b4931f148d899c418"
    },
    {
      "path": "autonomy/continuous.py",
      "size": 4098,
      "sha256": "20792e75157bc58f90738e84b5ba26775fb6e4f365eab379d0d1d494f555097f"
    },
    {
      "path": "autonomy/improvement.py",
      "size": 1469,
      "sha256": "a35c6a0c0785e62f7c3d95ca9d32071842ace08ba96d1371b6efe19205e9267c"
    },
    {
      "path": "autonomy/jobs.py",
      "size": 1972,
      "sha256": "312c9fd8adb053ebd299ce17764e57357a7e203179cb76e4169642a32c5e8313"
    },
    {
      "path": "autonomy/policy.py",
      "size": 436,
      "sha256": "c9f801991b04deb7616a062a68eedd7696d24f66fb42429019545bfdbf7a0a15"
    },
    {
      "path": "autonomy/self_manager.py",
      "size": 8917,
      "sha256": "b1437fbefed4e51140a2037254dcd9a9afc84aba67a0cd705b695504ba977c13"
    },
    {
      "path": "config/__init__.py",
      "size": 31,
      "sha256": "a31d7d13682462b600bd4ccb589defe09c6073de4024f2962cdaab0009bd2ec4"
    },
    {
      "path": "config/app_config.py",
      "size": 1648,
      "sha256": "1c8f6f51c3c5d7c836413b7f50179feee8b51295491d6ced20f553a623c16f46"
    },
    {
      "path": "config/default_config.json",
      "size": 1806,
      "sha256": "294f418b019a4f18e3c38ad0ad29ffb5735f477e3c95823d6acc77c3a54e6a0d"
    },
    {
      "path": "config/device_profiles.py",
      "size": 2255,
      "sha256": "16fe0b4a9c61a017c22fd76494bc601b0f408fc9e39d779dc06cb1f84704091d"
    },
    {
      "path": "config/hardware_override.example.json",
      "size": 182,
      "sha256": "3af272ffb30fead7c6562a307eee09e8b4688fa876354405bd64b8f3adb0ceed"
    },
    {
      "path": "config/hardware_profile.json",
      "size": 193,
      "sha256": "afe854d99abb4cb98ac3f86d5beb29a955b4e5ff15ca6d23c3166e396383d3ce"
    },
    {
      "path": "config/i18n.py",
      "size": 3823,
      "sha256": "62681cee5652997af5f3e5314bb108f37574c23608e237740e8e2f158e20b6d7"
    },
    {
      "path": "config/paths.py",
      "size": 3093,
      "sha256": "405710e83d2f12c8b09f4883038bed1d098e4b3def24f1bb93d4ff54c709c46a"
    },
    {
      "path": "control_plane/README.md",
      "size": 770,
      "sha256": "130097bd56a89996925d3f21942a9158b6c0f724e5c76382d25157b301ab57de"
    },
    {
      "path": "control_plane/__init__.py",
      "size": 448,
      "sha256": "aa026cdf3b84d019db91e1cd396a724cea5d1225a77db574b6cc10a5978bbd5a"
    },
    {
      "path": "control_plane/contracts.py",
      "size": 2984,
      "sha256": "8c2441ec3ca7fe45f403986607cfbcbf508d770946600c1162e6e1d16ab1bfa6"
    },
    {
      "path": "control_plane/execution.py",
      "size": 3032,
      "sha256": "c554513cc7aa04294e3944a79c171f43a1fb3d7a2bbb9a58a908362fbcbf484b"
    },
    {
      "path": "control_plane/function_registry.json",
      "size": 31986,
      "sha256": "9ed24e57ea920e5ffa8b0746db0283191d240587d5e77753f1fcf6e8a66a713a"
    },
    {
      "path": "control_plane/kca_registry.py",
      "size": 1027,
      "sha256": "09ab6eddeb5991c591e4bdf5d49a50c214f9930716c25750f09361a44ed9256f"
    },
    {
      "path": "control_plane/router.py",
      "size": 5284,
      "sha256": "25c9f1faec1cd37ddf47aac66c9801840de3c009e73a6469b06244c6c2b24ba4"
    },
    {
      "path": "control_plane/state_store.py",
      "size": 2265,
      "sha256": "0602ffcc4017bdc3f696c911c7bba63d0423f271f9361690c4b96041d996946d"
    },
    {
      "path": "core/__init__.py",
      "size": 738,
      "sha256": "df53f3b0b80164aa4825177f2eef8217eb0e078e75a0a79f4e3a6cb43778bcdd"
    },
    {
      "path": "core/agent.py",
      "size": 14713,
      "sha256": "3680ffd155acf29a69f55cc1402455d22f8170fad721182f9aaeae51a1d37423"
    },
    {
      "path": "core/audit.py",
      "size": 877,
      "sha256": "27a4ccb2aa37c8d13cfebe2a02982ce63b91c55624b5bcd6637736c7123121a0"
    },
    {
      "path": "core/context.py",
      "size": 3022,
      "sha256": "272f920ed5370f01231f8f40f1b5983063a7694f2600f9144c2caf630dcccce4"
    },
    {
      "path": "core/events.py",
      "size": 2688,
      "sha256": "e526deb2450cfd28307f99f4d797f7b945f28f38dbd2424a92be061742d8fad2"
    },
    {
      "path": "core/job_manager.py",
      "size": 3151,
      "sha256": "c2bf43daf20f3006831d85d527fa07b02acbf45fbd176b8dfd6a5e8324181ade"
    },
    {
      "path": "core/logger.py",
      "size": 2253,
      "sha256": "8ec3185ca6d07f551c3905cd967ba222fdd0d02624375e012129c91d0056f74e"
    },
    {
      "path": "core/orchestrator.py",
      "size": 4927,
      "sha256": "4e69ab4cd357d05eae680e65ae8504a96a996852964b00e9930ac42c9afd732c"
    },
    {
      "path": "core/response_guard.py",