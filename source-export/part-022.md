            raise
```

---

### `33/588` `backend/BUILD_EXE.bat`

- **المسار الكامل:** `F:\1f\p\ALI_Studio_Pro_Design4_4.6.0\04_Adaptive_Hybrid\backend/BUILD_EXE.bat`
- **الحجم:** 1611 بايت (1.6 KB)
- **الامتداد:** `.bat`

```batch
@echo off
setlocal
chcp 65001 >nul
cd /d "%~dp0"
if not exist ".venv\Scripts\python.exe" (call SETUP.bat)
if errorlevel 1 exit /b 1
call ".venv\Scripts\activate.bat"
python -c "import PyInstaller, tkinterdnd2" >nul 2>nul
if errorlevel 1 (
  echo [INFO] Installing PyInstaller + TkDnD...
  python -m pip install "pyinstaller>=6" "tkinterdnd2==0.6.3" --prefer-binary
  if errorlevel 1 goto fail
)
if exist build rmdir /s /q build
if exist dist\ALI-AI rmdir /s /q dist\ALI-AI
python -m PyInstaller --noconfirm --clean --windowed --name ALI-AI --onedir ^
  --collect-all tkinterdnd2 ^
  --add-data "control_plane\function_registry.json;control_plane" ^
  --add-data "config\default_config.json;config" ^
  --add-data "models\active\ALI-Bootstrap-v2.5;models\active\ALI-Bootstrap-v2.5" ^
  --add-data "phase2;phase2" ^
  ali_ai.py
if errorlevel 1 goto fail
if exist config xcopy /E /I /Y /Q config dist\ALI-AI\config >nul
if exist control_plane xcopy /E /I /Y /Q control_plane dist\ALI-AI\control_plane >nul
if exist data xcopy /E /I /Y /Q data dist\ALI-AI\data >nul
if exist models xcopy /E /I /Y /Q models dist\ALI-AI\models >nul
if exist phase2 xcopy /E /I /Y /Q phase2 dist\ALI-AI\phase2 >nul
if exist README_WINDOWS.md copy /Y README_WINDOWS.md dist\ALI-AI\README_WINDOWS.md >nul
echo @echo off>dist\ALI-AI\START-ALI-AI.bat
echo cd /d "%%~dp0">>dist\ALI-AI\START-ALI-AI.bat
echo start "ALI AI" "ALI-AI.exe">>dist\ALI-AI\START-ALI-AI.bat
echo.
echo [OK] Portable app created at dist\ALI-AI\
echo Run dist\ALI-AI\ALI-AI.exe or START-ALI-AI.bat
pause
exit /b 0
:fail
echo [ERROR] EXE build failed.
pause
exit /b 1
```

---

### `34/588` `backend/CLI/ali.py`

- **المسار الكامل:** `F:\1f\p\ALI_Studio_Pro_Design4_4.6.0\04_Adaptive_Hybrid\backend/CLI/ali.py`
- **الحجم:** 681 بايت (0.7 KB)
- **الامتداد:** `.py`

```python
#!/usr/bin/env python
from __future__ import annotations
import argparse,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]; sys.path.insert(0,str(ROOT))
def main(argv=None):
 p=argparse.ArgumentParser(prog='ali'); sub=p.add_subparsers(dest='cmd',required=True)
 sub.add_parser('doctor'); h=sub.add_parser('harvest'); h.add_argument('path')
 a=p.parse_args(argv)
 if a.cmd=='doctor':
  from runtime.hardware import detect; print(detect().__dict__)
  return 0
 if a.cmd=='harvest':
  from data_engine.harvester import Harvester; print(Harvester(ROOT/'artifacts/harvest.sqlite3').scan(a.path)); return 0
 return 0
if __name__=='__main__': raise SystemExit(main())
```

---

### `35/588` `backend/config/__init__.py`

- **المسار الكامل:** `F:\1f\p\ALI_Studio_Pro_Design4_4.6.0\04_Adaptive_Hybrid\backend/config/__init__.py`
- **الحجم:** 31 بايت (0.0 KB)
- **الامتداد:** `.py`

```python
# ALI AI configuration package
```

---

### `36/588` `backend/config/app_config.py`

- **المسار الكامل:** `F:\1f\p\ALI_Studio_Pro_Design4_4.6.0\04_Adaptive_Hybrid\backend/config/app_config.py`
- **الحجم:** 1648 بايت (1.6 KB)
- **الامتداد:** `.py`

```python
# -*- coding: utf-8 -*-
"""ALI AI 2.5 — single source of truth for identity, UI palette and user-facing modes."""
from __future__ import annotations

APP = "ALI AI"
VERSION = "4.4.0"
CODENAME = "Professional Assistant · P50"
LEGACY_APP = "ALI Studio"

# Visual baseline derived from the supplied ali_agent_ui.py reference.
# Do not silently replace these with a dark theme in the production build.
PALETTE = {
    "BG": "#ffffff",
    "RAIL": "#f4f4f6",
    "RAIL_HOVER": "#e9e9ed",
    "LINE": "#e3e3e8",
    "INK": "#1a1a1f",
    "MUTED": "#8a8a94",
    "SOFT": "#f7f7f9",
    "PANEL": "#ffffff",
    "PANEL_2": "#f7f7f9",
    "ACCENT": "#1a1a1f",
    "BLUE": "#3b6ef5",
    "GREEN": "#1a7f45",
    "RED": "#c0392b",
    "AMBER": "#9a6700",
    "EDITOR": "#fbfbfc",
    "WHITE": "#ffffff",
}

PERM_MODES = [
    ("read-only", "Read only", "قراءة فقط"),
    ("default", "Ask before sensitive actions", "يسأل قبل التعديل والأوامر الحساسة"),
    ("full-access", "Full access", "تنفيذ مباشر للأدوات المسموح بها"),
]

AI_MODES = ["auto", "professional", "agent", "chat", "tools", "research"]
MODELS = ["Auto", "ALI-local", "ALI-candidate", "ALI-GGUF"]
EFFORTS = ["AUTO", "LOW", "MEDIUM", "HIGH", "ULTRA"]

SENSITIVE = {
    "write_file": "تعديل / إنشاء ملف",
    "run_command": "تشغيل أمر على الجهاز",
    "git_commit": "إنشاء commit",
    "delete": "حذف عنصر",
    "install": "تثبيت مكوّن",
}

__all__ = [
    "APP", "VERSION", "CODENAME", "LEGACY_APP", "PALETTE", "PERM_MODES",
    "AI_MODES", "MODELS", "EFFORTS", "SENSITIVE",
]
```

---

### `37/588` `backend/config/default_config.json`

- **المسار الكامل:** `F:\1f\p\ALI_Studio_Pro_Design4_4.6.0\04_Adaptive_Hybrid\backend/config/default_config.json`
- **الحجم:** 1852 بايت (1.8 KB)
- **الامتداد:** `.json`

```json
{
  "app": {
    "name": "ALI AI",
    "version": "4.5.2"
  },
  "device": {
    "policy": "auto-safe",
    "prefer_cpu_for_training_on_legacy_gpu": false,
    "max_cpu_threads": 6,
    "ram_reserve_gb": 5.0,
    "vram_reserve_gb": 0.45,
    "profile": "p50-auto",
    "cpu_threads": 6,
    "interop_threads": 1,
    "pause_below_available_ram_gb": 3.0,
    "pause_below_battery_percent": 15
  },
  "agent": {
    "mode": "professional",
    "max_steps": 12,
    "verify_after_tool": true,
    "auto_repair": true,
    "allow_internet": true,
    "kca_control_plane": true,
    "auto_learning": true,
    "auto_learning_min_new_samples": 32,
    "auto_learning_scale": "micro",
    "auto_learning_steps": 1
  },
  "security": {
    "permission_mode": "default"
  },
  "training": {
    "profile": "p50-auto",
    "mode": "continuous_lora",
    "train_mode": "lora",
    "dataset_mode": "chat",
    "epochs": 1,
    "max_steps": 0,
    "seq_len": 256,
    "batch_size": 1,
    "grad_accum": 16,
    "learning_rate": 0.0003,
    "warmup_steps": 20,
    "save_every": 50,
    "eval_every": 50,
    "gradient_checkpointing": true,
    "amp": false,
    "resume_checkpoints": true,
    "scale": "small",
    "bootstrap_scale": "micro",
    "cpu_threads": 6,
    "lora_rank": 16,
    "lora_alpha": 32
  },
  "paths": {
    "workspace": "",
    "last_dir": ""
  },
  "runtime": {
    "backend": "auto",
    "context": 384,
    "max_new_tokens": 192,
    "temperature": 0.65
  },
  "online": {
    "enabled": true,
    "ingest_to_weights": false
  },
  "scaling": {
    "distributed": false,
    "world_size": 1,
    "remote_training": false
  },
  "kca": {
    "master_version": "3.0",
    "function_registry": "control_plane/function_registry.json",
    "record_structured_state": true,
    "require_verification_for_tools": true
  },
  "version": "4.5.2"
}
```

---

### `38/588` `backend/config/desktop_settings.json`

- **المسار الكامل:** `F:\1f\p\ALI_Studio_Pro_Design4_4.6.0\04_Adaptive_Hybrid\backend/config/desktop_settings.json`
- **الحجم:** 29 بايت (0.0 KB)
- **الامتداد:** `.json`

```json
{
  "allow_internet": true
}
```

---

### `39/588` `backend/config/device_profiles.py`

- **المسار الكامل:** `F:\1f\p\ALI_Studio_Pro_Design4_4.6.0\04_Adaptive_Hybrid\backend/config/device_profiles.py`
- **الحجم:** 2255 بايت (2.2 KB)
- **الامتداد:** `.py`

```python
# -*- coding: utf-8 -*-
"""Concrete, reproducible device profiles for ALI AI deployments.

The ThinkPad P50 profile is deliberately conservative: the Quadro M1000M has
only 2 GB VRAM, so local training stays CPU-first while inference may use
optional GGUF/llama.cpp offload. Profiles are copied deeply before adaptation
so nested configuration cannot leak mutations between callers.
"""
from __future__ import annotations

from copy import deepcopy
from typing import Any, Dict

P50_PROFILE: Dict[str, Any] = {
    "id": "thinkpad-p50-32gb-2gb",
    "label": "Lenovo ThinkPad P50 / 32 GB / Quadro M1000M 2 GB",
    "cpu": {
        "threads": 8,
        "physical_cores": 4,
        "recommended_torch_threads": 6,
        "interop_threads": 1,
        "leave_free_threads": 2,
    },
    "ram_gb": 32,
    "gpu": {
        "name": "NVIDIA Quadro M1000M",
        "vram_gb": 2,
        "cuda_capability": [5, 0],
        "training": "disabled-by-default",
        "inference": "optional-offload",
    },
    "training": {
        "device": "cpu",
        "scale": "small",
        "bootstrap_scale": "micro",
        "batch_size": 1,
        "grad_accum": 16,
        "seq_len": 256,
        "context": 320,
        "max_new_tokens": 160,
        "amp": False,
        "gradient_checkpointing": True,
        "weight_decay": 0.05,
        "learning_rate": 0.0003,
        "warmup_steps": 20,
        "save_every": 50,
        "eval_every": 50,
        "max_steps_bootstrap": 50,
        "max_concurrent_jobs": 1,
        "require_ac_power": True,
        "min_available_ram_gb": 4.0,
        "max_cpu_threads": 6,
    },
    "runtime": {
        "recommended_context": 320,
        "max_context": 384,
        "recommended_max_new_tokens": 160,
        "max_new_tokens": 192,
        "temperature_default": 0.65,
        "max_concurrent_inference": 1,
        "min_available_ram_gb": 3.0,
    },
    "power": {
        "battery_guard_percent": 45,
        "battery_hard_stop_percent": 25,
        "thermal_guard_c": 80.0,
        "thermal_hard_stop_c": 88.0,
        "prefer_ac_for_training": True,
    },
    "storage": {
        "fast_root": "D:/ALI-AI",
        "archive_root": "F:/ALI-AI-Archive",
        "avoid_system_drive_for_checkpoints": True,
    },
    "rules": [
        "CPU-first training is the default for this 2 GB legacy GPU class.",
        "Use at most 6 logical CPU threads for training so Windows/UI retain headroom.",
        "Run one heavy local training job at a time.",
        "Use micro scale for smoke tests; use small scale only for real local runs.",
        "Prefer GGUF/llama.cpp for production inference when a compatible GGUF exists.",
        "Pause or refuse heavy training when battery, thermal, or free-RAM guards are violated.",
    ],
}


def _adaptive_training(base: Dict[str, Any], ram_gb: float) -> Dict[str, Any]:
    training = deepcopy(base["training"])
    if ram_gb < 16:
        training.update(scale="micro", seq_len=192, context=256, grad_accum=8)
    elif ram_gb < 24:
        training.update(scale="micro", seq_len=224, context=288, grad_accum=12)
    elif ram_gb < 32:
        training.update(scale="small", seq_len=256, context=320, grad_accum=16)
    return training


def recommend_for_hardware(hardware: Any) -> Dict[str, Any]:
    ram = float(getattr(hardware, "ram_gb", 0) or 0)
    vram = float(getattr(hardware, "vram_gb", 0) or 0)
    threads = int(getattr(hardware, "cpu_cores", 0) or 0)
    gpu_name = str(getattr(hardware, "gpu_name", "") or "").lower()

    profile = deepcopy(P50_PROFILE)
    p50_match = ram >= 24 and threads >= 6 and vram < 3 and (
        "m1000m" in gpu_name or "quadro" in gpu_name or not gpu_name
    )
    if p50_match:
        profile["detected_match"] = True
        return profile

    profile["id"] = "adaptive"
    profile["label"] = (
        f"Adaptive profile · {ram:.1f} GB RAM · "
        f"{vram:.1f} GB VRAM · {threads} logical threads"
    )
    profile["detected_match"] = False
    profile["training"] = _adaptive_training(profile, ram)
    if ram < 16:
        profile["runtime"].update(recommended_context=256, max_context=320,
                                  recommended_max_new_tokens=128, max_new_tokens=160)
    elif ram < 24:
        profile["runtime"].update(recommended_context=288, max_context=352,
                                  recommended_max_new_tokens=144, max_new_tokens=176)
    return profile

```

---

### `40/588` `backend/config/hardware_override.example.json`

- **المسار الكامل:** `F:\1f\p\ALI_Studio_Pro_Design4_4.6.0\04_Adaptive_Hybrid\backend/config/hardware_override.example.json`
- **الحجم:** 182 بايت (0.2 KB)
- **الامتداد:** `.json`

```json
{
  "label": "ThinkPad P50",
  "cpu": "Intel Core i7-6820HQ",
  "cpu_threads": 8,
  "ram_gb": 32,
  "gpu": "NVIDIA Quadro M1000M",
  "vram_gb": 2,
  "policy": "cpu-first-training"
}
```

---

### `41/588` `backend/config/hardware_profile.json`

- **المسار الكامل:** `F:\1f\p\ALI_Studio_Pro_Design4_4.6.0\04_Adaptive_Hybrid\backend/config/hardware_profile.json`
- **الحجم:** 2719 بايت (2.7 KB)
- **الامتداد:** `.json`

```json
{
  "profile_name": "ALI ThinkPad P50 target profile",
  "source": "user-provided hardware report",
  "enabled": true,
  "privacy": "Personal/device unique identifiers intentionally excluded from the canonical project profile.",
  "device_name": "Lenovo ThinkPad P50",
  "model": "20EQS2L900",
  "os_label": "Windows 11 Pro 10.0.26200 (64-bit)",
  "language": "ar-SA",
  "cpu_model": "Intel Core i7-6820HQ",
  "cpu_threads": 8,
  "physical_cores": 4,
  "cpu_temp_c": 41.05,
  "ram_gb": 32,
  "ram_available_gb_observed": 21.32,
  "ram_type": "DDR4",
  "ram_speed_mhz": 2133,
  "gpu_name": "NVIDIA Quadro M1000M",
  "gpu_driver": "31.0.15.3818",
  "vram_gb": 2,
  "vram_type": "GDDR5",
  "cuda_capability": [
    5,
    0
  ],
  "battery_percent": 38,
  "battery_minutes": 42,
  "screen": "1920x1080 @ 60Hz IPS FlexView",
  "wifi": "Intel Dual Band Wireless-AC 8260",
  "network_speed_mbps": 72.2,
  "storage": {
    "ssd_model": "WDC PC SN720 SDAPNTW-512G-1006",
    "ssd_capacity_gb": 512,
    "ssd_bus": "NVMe",
    "ssd_partition_style": "GPT",
    "ssd_health": "Healthy",
    "hdd_model": "WDC WD20SPZX-22UA7T0",
    "hdd_capacity_gb": 2000,
    "hdd_bus": "SATA 5400 RPM",
    "hdd_partition_style": "MBR",
    "hdd_health": "Healthy"
  },
  "connectivity": {
    "ethernet": "Intel I219-LM Gigabit LAN",
    "bluetooth": "Bluetooth Device (PAN)"
  },
  "notes": {
    "cpu_temperature_source": "User-provided ACPI reading",
    "ssd_tbw": "Requires smartctl or CrystalDiskInfo for exact SMART/TBW data",
    "cuda_cores": "Not used as a training decision variable; hardware-reported VRAM and runtime CUDA probing are preferred",
    "intel_vram_type": "Not treated as authoritative",
    "battery_cells": "Requires Lenovo Vantage for exact cell count"
  }
}
```

---

### `42/588` `backend/config/hermes_integration.json`

- **المسار الكامل:** `F:\1f\p\ALI_Studio_Pro_Design4_4.6.0\04_Adaptive_Hybrid\backend/config/hermes_integration.json`
- **الحجم:** 212 بايت (0.2 KB)
- **الامتداد:** `.json`

```json
{
  "enabled": true,
  "root": "D:\\\\AI ALI\\\\Hermes",
  "read_only": true,
  "max_file_bytes": 2000000,
  "max_context_chars": 8000,
  "allow_database_reads": true,
  "allow_api": false,
  "allow_mcp": false
}
```

---

### `43/588` `backend/config/i18n.py`

- **المسار الكامل:** `F:\1f\p\ALI_Studio_Pro_Design4_4.6.0\04_Adaptive_Hybrid\backend/config/i18n.py`
- **الحجم:** 3823 بايت (3.7 KB)
- **الامتداد:** `.py`

```python
# -*- coding: utf-8 -*-
"""Small deterministic bilingual UI dictionary. Runtime content remains model-generated."""
from __future__ import annotations

TEXT = {
    "ar": {
        "app_subtitle": "المساعد الذكي المحلي الاحترافي", "professional": "الوضع الاحترافي", "auto": "تلقائي (ذكي)",
        "connected": "متصل", "offline": "محلي · دون اتصال أولاً", "auto_learn": "التعلم الذاتي",
        "new_chat": "محادثة جديدة", "conversations": "المحادثات", "projects": "المشاريع", "files": "الملفات",
        "memory": "الذاكرة", "tools": "الأدوات", "web": "البحث والويب", "models": "النماذج", "datasets": "البيانات والتدريب",
        "settings": "الإعدادات", "overview": "نظرة عامة", "editor": "المحرر", "terminal": "الطرفية", "jobs": "المهام",
        "health": "الصحة", "sources": "المصادر", "context": "السياق", "send": "إرسال", "stop": "إيقاف", "ready": "جاهز",
        "open_project": "فتح مشروع", "doctor": "فحص النظام", "train": "تدريب", "self_learn": "تعلم ذاتي", "refresh": "تحديث",
        "analyze": "تحليل المشروع", "check_device": "فحص الجهاز", "inspect_model": "فحص النموذج", "train_tokenizer": "تدريب Tokenizer",
        "import_weights": "استيراد الأوزان", "write_here": "اكتب سؤالك هنا...", "copy": "نسخ", "system_health": "حالة النظام",
        "battery": "البطارية", "activity": "النشاط الحالي", "current_context": "السياق الحالي", "model": "النموذج",
        "cpu": "المعالج", "gpu": "GPU", "ram": "الذاكرة", "temp": "الحرارة", "disk": "التخزين",
        "language": "اللغة", "arabic": "العربية", "english": "English", "training_files": "ملفات التدريب",
    },
    "en": {
        "app_subtitle": "Professional Local AI Assistant", "professional": "Professional Mode", "auto": "Auto (Smart)",
        "connected": "Connected", "offline": "Local · Offline-first", "auto_learn": "Self Learning",
        "new_chat": "New conversation", "conversations": "Conversations", "projects": "Projects", "files": "Files",
        "memory": "Memory", "tools": "Tools", "web": "Web Research", "models": "Models", "datasets": "Data & Training",
        "settings": "Settings", "overview": "Overview", "editor": "Editor", "terminal": "Terminal", "jobs": "Jobs",
        "health": "Health", "sources": "Sources", "context": "Context", "send": "Send", "stop": "Stop", "ready": "Ready",
        "open_project": "Open Project", "doctor": "System Check", "train": "Train", "self_learn": "Self Learn", "refresh": "Refresh",
        "analyze": "Analyze project", "check_device": "Check device", "inspect_model": "Inspect model", "train_tokenizer": "Train tokenizer",
        "import_weights": "Import weights", "write_here": "Write your question here...", "copy": "Copy", "system_health": "System health",
        "battery": "Battery", "activity": "Current activity", "current_context": "Current context", "model": "Model",
        "cpu": "CPU", "gpu": "GPU", "ram": "RAM", "temp": "Temperature", "disk": "Storage",
        "language": "Language", "arabic": "العربية", "english": "English", "training_files": "Training files",
    },
}

def normalize_language(value: str | None) -> str:
    return "ar" if str(value or "").lower().split("-")[0] == "ar" else "en"

def tr(key: str, language: str = "ar") -> str:
    lang=normalize_language(language)
    return TEXT.get(lang, TEXT["ar"]).get(key, key)

def is_rtl(language: str) -> bool:
    return normalize_language(language) == "ar"
```

---

### `44/588` `backend/config/paths.py`

- **المسار الكامل:** `F:\1f\p\ALI_Studio_Pro_Design4_4.6.0\04_Adaptive_Hybrid\backend/config/paths.py`
- **الحجم:** 3214 بايت (3.1 KB)
- **الامتداد:** `.py`

```python
# -*- coding: utf-8 -*-
"""طبقة المسارات المركزية. أي مسار يجب أن يمر من هنا."""

from __future__ import annotations

import os
import sys
from pathlib import Path


def _project_root() -> Path:
    """Project data root for source runs and frozen Windows builds."""
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent
    return Path(__file__).resolve().parent.parent


def _user_data_dir() -> Path:
    """Return persistent data path; portable mode keeps all app data inside the project."""
    if os.environ.get("ALI_PORTABLE_MODE", "0") == "1":
        root = _project_root()
        p = root / "runtime" / "user_data"
    else:
        base = os.environ.get("APPDATA") or str(Path.home())
        p = Path(base) / "ALI-AI"
    p.mkdir(parents=True, exist_ok=True)
    return p


class AppPaths:
    """نقطة مركزية لكل مسارات ALI AI."""

    def __init__(self):
        self._root = _project_root()
        self._user = _user_data_dir()

    # -------- project root
    def project_root(self) -> Path:
        return self._root

    # -------- user appdata
    def user_data_dir(self) -> Path:
        return self._user

    def user_config(self) -> Path:
        return self._user / "config.json"

    def user_threads(self) -> Path:
        return self._user / "threads.json"

    def user_logs_dir(self) -> Path:
        p = self._user / "logs"
        p.mkdir(parents=True, exist_ok=True)
        return p

    # -------- local under project root
    def local_config(self) -> Path:
        return self._root / "config" / "default_config.json"

    def local_config_candidates(self) -> list:
        """مرشحات للـ config عند الإقلاع: الجذر أولاً ثم project root."""
        return [
            self._root / "config" / "config.json",
            self._root / "config.json",
        ]

    def checkpoints_dir(self) -> Path:
        p = self._root / "checkpoints"
        p.mkdir(parents=True, exist_ok=True)
        return p

    def weights_dir(self) -> Path:
        p = self._root / "weights"
        p.mkdir(parents=True, exist_ok=True)
        return p

    def data_dir(self) -> Path:
        p = self._root / "data"
        return p

    def tests_dir(self) -> Path:
        return self._root / "tests"

    def models_dir(self) -> Path:
        p = self._root / "models"
        p.mkdir(parents=True, exist_ok=True)
        return p

    def model_inbox_dir(self) -> Path:
        p = self.models_dir() / "inbox"
        p.mkdir(parents=True, exist_ok=True)
        return p

    def model_archive_dir(self) -> Path:
        p = self.models_dir() / "archive"
        p.mkdir(parents=True, exist_ok=True)
        return p

    # -------- default config (no secrets, no Lovable)
    def default_config(self) -> dict:
        return {
            "name": "Windows PC",
            "model": "ALI-local",
            "app": "ALI AI",
            "version": "4.5.2",
            "ai_mode": "professional",
            "perm_mode": "default",
            "last_dir": str(self._root),
            "threads": {},
            "always_allow": [],
        }


APP_PATHS = AppPaths()
```

---

### `45/588` `backend/CONTINUOUS_LEARNING_README.md`

- **المسار الكامل:** `F:\1f\p\ALI_Studio_Pro_Design4_4.6.0\04_Adaptive_Hybrid\backend/CONTINUOUS_LEARNING_README.md`
- **الحجم:** 666 بايت (0.7 KB)
- **الامتداد:** `.md`

```markdown
# Continuous Learning Manager

`training/continuous_learning.py` is the Windows desktop training control layer.

It intentionally does not run training inside React. The Electron UI calls the local Python API, which queues a background training job. The real PyTorch/LoRA work remains in `training/pipeline.py` and `training/trainer.py`.

Generation aliases are stored in the normal `ModelRegistry` as `v1`, `v2`, ... and are promoted only after validation. The existing timestamped pipeline artifacts are kept underneath each generation for reproducibility.

The desktop UI starts the next cycle automatically by default after at least one new source is validated.
```

---

### `46/588` `backend/control_plane/__init__.py`

- **المسار الكامل:** `F:\1f\p\ALI_Studio_Pro_Design4_4.6.0\04_Adaptive_Hybrid\backend/control_plane/__init__.py`
- **الحجم:** 448 بايت (0.4 KB)
- **الامتداد:** `.py`

```python
# -*- coding: utf-8 -*-
from control_plane.contracts import RequestEnvelope, TaskState, PlanStep, ExecutionTrace
from control_plane.router import KCARequestRouter
from control_plane.execution import KCAExecutionEngine
from control_plane.kca_registry import FUNCTIONS, BY_NAME, summary

__all__ = [
    "RequestEnvelope", "TaskState", "PlanStep", "ExecutionTrace",
    "KCARequestRouter", "KCAExecutionEngine", "FUNCTIONS", "BY_NAME", "summary",
]

```

---

### `47/588` `backend/control_plane/contracts.py`

- **المسار الكامل:** `F:\1f\p\ALI_Studio_Pro_Design4_4.6.0\04_Adaptive_Hybrid\backend/control_plane/contracts.py`
- **الحجم:** 2984 بايت (2.9 KB)
- **الامتداد:** `.py`

```python
# -*- coding: utf-8 -*-
"""Stable typed contracts for the ALI KCA control plane."""
from __future__ import annotations
from dataclasses import dataclass, field, asdict
from typing import Any
import time
import uuid


def _id(prefix: str) -> str:
    return f"{prefix}-{uuid.uuid4().hex[:12]}"


@dataclass
class RequestEnvelope:
    raw_text: str
    project_dir: str = ""
    session_id: str = ""
    language: str = "auto"
    channel: str = "desktop"
    request_id: str = field(default_factory=lambda: _id("req"))
    created_at: float = field(default_factory=time.time)
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class TaskState:
    request_id: str
    intent: str = "unknown"
    confidence: float = 0.0
    goal: str = ""
    constraints: list[str] = field(default_factory=list)
    entities: list[dict[str, Any]] = field(default_factory=list)
    implicit_intent: str | None = None
    knowledge_state: dict[str, Any] = field(default_factory=dict)
    task_state: dict[str, Any] = field(default_factory=dict)
    candidate_actions: list[dict[str, Any]] = field(default_factory=list)
    selected_action: dict[str, Any] | None = None
    tool_state: dict[str, Any] = field(default_factory=dict)
    observation: dict[str, Any] | None = None
    error_state: dict[str, Any] | None = None
    correction: dict[str, Any] | None = None
    verification: dict[str, Any] | None = None
    final_output: Any = None
    uncertainty: dict[str, Any] | None = None
    provenance: list[dict[str, Any]] = field(default_factory=list)
    updated_at: float = field(default_factory=time.time)

    def touch(self) -> None:
        self.updated_at = time.time()

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class PlanStep:
    step_id: str
    title: str
    action: str
    tool_name: str | None = None
    kwargs: dict[str, Any] = field(default_factory=dict)
    requires_confirmation: bool = False
    verify: bool = True
    status: str = "pending"
    result: Any = None

    @classmethod
    def make(cls, title: str, action: str, **kwargs: Any) -> "PlanStep":
        return cls(step_id=_id("step"), title=title, action=action, **kwargs)


@dataclass
class ExecutionTrace:
    operation_id: str = field(default_factory=lambda: _id("op"))
    tool_call_id: str | None = None
    observation_id: str | None = None
    state_transition_id: str | None = None
    started_at: float = field(default_factory=time.time)
    finished_at: float | None = None
    events: list[dict[str, Any]] = field(default_factory=list)
    status: str = "created"

    def add(self, event: str, **data: Any) -> None:
        self.events.append({"event": event, "ts": time.time(), **data})

    def finish(self, status: str) -> None:
        self.status = status
        self.finished_at = time.time()

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

```

---

### `48/588` `backend/control_plane/execution.py`

- **المسار الكامل:** `F:\1f\p\ALI_Studio_Pro_Design4_4.6.0\04_Adaptive_Hybrid\backend/control_plane/execution.py`
- **الحجم:** 3032 بايت (3.0 KB)
- **الامتداد:** `.py`

```python
# -*- coding: utf-8 -*-
"""Observation, verification and bounded recovery for KCA plans."""
from __future__ import annotations
from typing import Any, Callable
import hashlib
import json

from control_plane.contracts import ExecutionTrace, PlanStep, TaskState


class KCAExecutionEngine:
    def __init__(self, tool_runner: Callable[[str, dict[str, Any]], dict[str, Any]]):
        self.tool_runner = tool_runner

    def execute(self, state: TaskState, steps: list[PlanStep]) -> dict[str, Any]:
        trace = ExecutionTrace()
        results: list[dict[str, Any]] = []
        trace.add("request_state", state=state.to_dict())
        for step in steps:
            step.status = "running"
            trace.add("step_started", step_id=step.step_id, action=step.action)
            if step.requires_confirmation:
                step.status = "blocked_confirmation"
                result = {"ok": False, "needs_confirmation": True, "action": step.action}
                results.append(result)
                trace.add("confirmation_required", step_id=step.step_id)
                break
            if not step.tool_name:
                step.status = "completed"
                continue
            result = self.tool_runner(step.tool_name, step.kwargs)
            step.result = result
            ok = bool(result.get("ok") or result.get("success"))
            step.status = "completed" if ok else "failed"
            results.append({"step_id": step.step_id, "tool": step.tool_name, "result": result})
            trace.add("observation", step_id=step.step_id, tool=step.tool_name, result=result)
            if not ok:
                state.error_state = {"step_id": step.step_id, "tool": step.tool_name, "result": result}
                trace.add("failure", **state.error_state)
                break
            if step.verify:
                verification = self.verify_result(step.tool_name, result)
                state.verification = verification
                trace.add("verification", verification=verification)
                if not verification["ok"]:
                    state.error_state = {"type": "verification_failed", "verification": verification}
                    break
        state.observation = {"results": results}
        state.touch()
        trace.finish("completed" if not state.error_state else "failed")
        return {"ok": trace.status == "completed", "results": results, "state": state.to_dict(), "trace": trace.to_dict()}

    @staticmethod
    def verify_result(tool_name: str, result: dict[str, Any]) -> dict[str, Any]:
        ok = bool(result.get("ok") or result.get("success"))
        payload = result.get("data")
        digest = hashlib.sha256(json.dumps(payload, ensure_ascii=False, sort_keys=True, default=str).encode("utf-8")).hexdigest() if payload is not None else ""
        return {"ok": ok, "tool": tool_name, "result_digest": digest, "reason": "tool reported success" if ok else str(result.get("error") or "unknown failure")}


__all__ = ["KCAExecutionEngine"]

```

---

### `49/588` `backend/control_plane/function_registry.json`

- **المسار الكامل:** `F:\1f\p\ALI_Studio_Pro_Design4_4.6.0\04_Adaptive_Hybrid\backend/control_plane/function_registry.json`
- **الحجم:** 31986 بايت (31.2 KB)
- **الامتداد:** `.json`

```json
{
  "version": "3.0",
  "functions": [
    {
      "id": "F-001",
      "name": "REQUEST_INGEST",
      "domain": "فهم المهمة",
      "purpose": "استقبال طلب المستخدم وتحديد الهدف، القيود، المخرج المتوقع، والسياق المتاح.",
      "input_contract": "نص الطلب + السياق",
      "output_contract": "مهمة داخلية موحدة"
    },
    {
      "id": "F-002",
      "name": "CONTEXT_ASSEMBLER",
      "domain": "فهم السياق",
      "purpose": "تجميع الرسائل والملفات والنتائج السابقة ذات الصلة قبل اتخاذ الإجراء.",
      "input_contract": "جلسة + مراجع",
      "output_contract": "حزمة سياق"
    },
    {
      "id": "F-003",
      "name": "TASK_ROUTER",
      "domain": "توجيه المهمة",
      "purpose": "اختيار مسار المعالجة العام المناسب للمهمة.",
      "input_contract": "مهمة مطبّعة",
      "output_contract": "Workflow ID"
    },
    {
      "id": "F-004",
      "name": "CAPABILITY_ROUTER",
      "domain": "توجيه القدرة",
      "purpose": "اختيار القدرات اللازمة من Capability Registry.",
      "input_contract": "هدف + سياق",
      "output_contract": "Capability set"
    },
    {
      "id": "F-005",
      "name": "TOOL_ROUTER",
      "domain": "توجيه الأدوات",
      "purpose": "اختيار الأداة المناسبة بدل تنفيذ كل شيء داخل النموذج.",
      "input_contract": "مهمة + قيود",
      "output_contract": "Tool plan"
    },
    {
      "id": "F-006",
      "name": "SOURCE_ROUTER",
      "domain": "توجيه المصادر",
      "purpose": "اختيار المصدر الأنسب: ملف، ويب، ذاكرة، أداة، أو معرفة داخلية.",
      "input_contract": "سؤال + freshness",
      "output_contract": "Source plan"
    },
    {
      "id": "F-007",
      "name": "RISK_GATE",
      "domain": "بوابة المخاطر",
      "purpose": "تحديد ما إذا كانت المهمة تحتاج قيودًا أو تحققًا إضافيًا قبل التنفيذ.",
      "input_contract": "Task + risk signals",
      "output_contract": "Risk level + controls"
    },
    {
      "id": "F-008",
      "name": "PLAN_BUILDER",
      "domain": "التخطيط",
      "purpose": "بناء خطوات قابلة للتنفيذ مع اعتماديات ونقاط تحقق.",
      "input_contract": "Goal + constraints",
      "output_contract": "Plan graph"
    },
    {
      "id": "F-009",
      "name": "EXECUTION_ENGINE",
      "domain": "التنفيذ",
      "purpose": "تنفيذ الخطوات وفق الخطة وتسجيل النتائج.",
      "input_contract": "Plan",
      "output_contract": "Execution trace"
    },
    {
      "id": "F-010",
      "name": "OBSERVATION_ENGINE",
      "domain": "مراقبة النتائج",
      "purpose": "قراءة نتيجة كل خطوة وعدم افتراض نجاحها من مجرد استدعائها.",
      "input_contract": "Tool result",
      "output_contract": "Observation"
    },
    {
      "id": "F-011",
      "name": "VERIFICATION_ENGINE",
      "domain": "التحقق",
      "purpose": "فحص النتيجة مقابل الهدف، الأدلة، القيود، والبنية المطلوبة.",
      "input_contract": "Output + criteria",
      "output_contract": "Verification report"
    },
    {
      "id": "F-012",
      "name": "REPAIR_ENGINE",
      "domain": "إصلاح المسار",
      "purpose": "تصحيح الفشل وإعادة التخطيط عند الحاجة.",
      "input_contract": "Failure + state",
      "output_contract": "Repaired plan"
    },
    {
      "id": "F-013",
      "name": "OUTPUT_ROUTER",
      "domain": "توجيه المخرج",
      "purpose": "اختيار شكل الرد أو الملف أو العنصر التفاعلي المناسب.",
      "input_contract": "Result + requested format",
      "output_contract": "Output contract"
    },
    {
      "id": "F-014",
      "name": "CITATION_MANAGER",
      "domain": "إدارة الإسناد",
      "purpose": "ربط الادعاءات بالمراجع المناسبة عند استخدام مصادر خارجية أو ملفات.",
      "input_contract": "Claims + sources",
      "output_contract": "Citation map"
    },
    {
      "id": "F-015",
      "name": "PROGRESS_REPORTER",