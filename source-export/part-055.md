}


@dataclass
class Decision:
    allowed: bool
    reason: str = ""
    needs_ask: bool = False       # True = الواجهة يجب أن تسأل المستخدم

    @staticmethod
    def allow(reason: str = "") -> "Decision":
        return Decision(allowed=True, reason=reason, needs_ask=False)

    @staticmethod
    def deny(reason: str) -> "Decision":
        return Decision(allowed=False, reason=reason, needs_ask=False)

    @staticmethod
    def ask(reason: str) -> "Decision":
        return Decision(allowed=False, reason=reason, needs_ask=True)


class PermissionManager:
    """Backend للصلاحيات — يفحص كل طلب tool.

    الاستخدام:
        pm = PermissionManager(mode="default")
        decision = pm.check(tool_name="write_file", permission=DEFAULT, ...)
        if decision.needs_ask:
            ... dialog ...
            if user_says_yes:
                pm.grant("write_file", session=True)
                # ثم استدعِ check مرة أخرى أو سمّ بالتنفيذ مباشرة.
    """

    def __init__(self, mode: str = "default",
                 always_allow: Optional[List[str]] = None) -> None:
        self.set_mode(mode)
        self._always_allow: set = set(always_allow or [])

    # ------------------------------------------------------------ config
    def set_mode(self, mode: str) -> None:
        if mode not in _PERM_RANK:
            raise ValueError("invalid mode: " + mode)
        self.mode = mode

    def grant(self, tool_name: str, session: bool = True) -> None:
        """إضافة أداة إلى الاستثناءات الحالية.

        لا تلغي هذه القائمة وضع read-only؛ الانتقال إلى read-only يجب أن
        يبقى حاجزاً نهائياً حتى لو مُنحت الأداة سابقاً.
        """
        self._always_allow.add(tool_name)

    def revoke(self, tool_name: str) -> None:
        self._always_allow.discard(tool_name)

    def always_allow_snapshot(self) -> List[str]:
        return sorted(self._always_allow)

    # ------------------------------------------------------------ core
    def check(self, *, tool_name: str, permission: Any,
              ctx: Any = None, kwargs: Optional[Dict[str, Any]] = None,
              user: Any = None) -> Decision:
        """يرجع القرار النهائي لطلب تشغيل الأداة."""
        effective_mode = self.mode
        if ctx is not None and getattr(ctx, "perm_mode", None):
            effective_mode = ctx.perm_mode

        if effective_mode not in _PERM_RANK:
            return Decision.deny(f"invalid permission mode: {effective_mode}")

        permission_value = (
            permission.value if hasattr(permission, "value") else str(permission)
        )
        if permission_value not in _PERM_RANK:
            return Decision.deny(
                f"invalid tool permission: {permission_value}"
            )

        tool_rank = _PERM_RANK[permission_value]
        user_rank = _PERM_RANK[effective_mode]

        # read-only is an absolute boundary and cannot be bypassed by grants.
        if effective_mode == PermMode.READ_ONLY.value and tool_rank > user_rank:
            return Decision.deny(
                f"read-only mode forbids '{tool_name}' "
                f"(requires '{permission_value}')"
            )

        # Explicitly granted tools are allowed only after the hard boundary above.
        if tool_name in self._always_allow:
            return Decision.allow("always_allow")

        if effective_mode == PermMode.FULL_ACCESS.value:
            return Decision.allow("full-access")

        if permission_value == PermMode.READ_ONLY.value:
            return Decision.allow("mode permits")

        # In default mode, DEFAULT and FULL_ACCESS actions require an explicit
        # user approval unless that tool was granted for the session.
        return Decision.ask(
            f"tool '{tool_name}' requires '{permission_value}' "
            f"and current mode is '{effective_mode}'"
        )

# Singleton helper (اختياري — يمكن إنشاء instance محلي أيضاً).
_PM_SINGLETON: Optional[PermissionManager] = None


def get_permission_manager(mode: str = "default") -> PermissionManager:
    global _PM_SINGLETON
    if _PM_SINGLETON is None:
        _PM_SINGLETON = PermissionManager(mode=mode)
    return _PM_SINGLETON


def reset_permission_manager_for_tests() -> None:
    global _PM_SINGLETON
    _PM_SINGLETON = None


__all__ = [
    "PermMode", "Decision", "PermissionManager",
    "get_permission_manager", "reset_permission_manager_for_tests",
]
```

---

### `366/588` `backend/SELF-MANAGER.bat`

- **المسار الكامل:** `F:\1f\p\ALI_Studio_Pro_Design4_4.6.0\04_Adaptive_Hybrid\backend/SELF-MANAGER.bat`
- **الحجم:** 158 بايت (0.2 KB)
- **الامتداد:** `.bat`

```batch
@echo off
setlocal
chcp 65001 >nul
cd /d "%~dp0"
if exist ".venv\Scripts\activate.bat" call ".venv\Scripts\activate.bat"
python scripts\self_manager.py
pause
```

---

### `367/588` `backend/SETUP-HERMES.bat`

- **المسار الكامل:** `F:\1f\p\ALI_Studio_Pro_Design4_4.6.0\04_Adaptive_Hybrid\backend/SETUP-HERMES.bat`
- **الحجم:** 305 بايت (0.3 KB)
- **الامتداد:** `.bat`

```batch
@echo off
setlocal
chcp 65001 >nul
cd /d "%~dp0"
if not exist ".venv\Scripts\python.exe" call SETUP.bat
call ".venv\Scripts\activate.bat"
python scripts\hermes_doctor.py
if errorlevel 2 (
  echo.
  echo Hermes is not available at D:\AI ALI\Hermes\ yet.
  echo ALI AI remains usable independently.
)
pause
```

---

### `368/588` `backend/SETUP-OFFLINE.bat`

- **المسار الكامل:** `F:\1f\p\ALI_Studio_Pro_Design4_4.6.0\04_Adaptive_Hybrid\backend/SETUP-OFFLINE.bat`
- **الحجم:** 107 بايت (0.1 KB)
- **الامتداد:** `.bat`

```batch
@echo off
setlocal EnableExtensions
cd /d "%~dp0"
cd /d "%~dp0..\..\.."
call Install\SETUP-ALL-OFFLINE.bat
```

---

### `369/588` `backend/SETUP-OPTIONAL.bat`

- **المسار الكامل:** `F:\1f\p\ALI_Studio_Pro_Design4_4.6.0\04_Adaptive_Hybrid\backend/SETUP-OPTIONAL.bat`
- **الحجم:** 350 بايت (0.3 KB)
- **الامتداد:** `.bat`

```batch
@echo off
setlocal
chcp 65001 >nul
cd /d "%~dp0"
if not exist ".venv\Scripts\python.exe" call SETUP.bat
call ".venv\Scripts\activate.bat"
python -m pip install -r requirements-optional.txt
if errorlevel 1 goto fail
echo [OK] Optional ALI AI packages installed.
pause
exit /b 0
:fail
echo [ERROR] Optional package installation failed.
pause
exit /b 1
```

---

### `370/588` `backend/SETUP.bat`

- **المسار الكامل:** `F:\1f\p\ALI_Studio_Pro_Design4_4.6.0\04_Adaptive_Hybrid\backend/SETUP.bat`
- **الحجم:** 2481 بايت (2.4 KB)
- **الامتداد:** `.bat`

```batch
\
@echo off
setlocal EnableExtensions
chcp 65001 >nul
cd /d "%~dp0"
title ALI AI - Windows Setup / Repair
where py >nul 2>nul
if errorlevel 1 (
  echo [ERROR] Python Launcher (py) was not found.
  echo Install Python 3.11.x 64-bit or use the bundled embedded runtime on a production build.
  pause
  exit /b 1
)
if not exist ".venv\Scripts\python.exe" (
  echo [SETUP] Creating Python 3.11 virtual environment...
  py -3.11 -m venv .venv
  if errorlevel 1 goto fail
)
call ".venv\Scripts\activate.bat"
if errorlevel 1 goto fail
python -m pip install --upgrade pip
if errorlevel 1 goto fail

echo [SETUP] Installing safe CPU baseline dependencies...
python -m pip install --disable-pip-version-check --prefer-binary "numpy>=2.0,<3" "psutil>=7,<8" "safetensors>=0.7,<1" "sentencepiece>=0.2,<1" "pytest>=9,<10"
if errorlevel 1 goto fail

echo [SETUP] Probing NVIDIA GPU...
where nvidia-smi >nul 2>nul
if not errorlevel 1 (
  nvidia-smi --query-gpu=name,memory.total,driver_version --format=csv,noheader > "%TEMP%\ali_gpu.txt" 2>nul
  findstr /i "M1000M Maxwell Quadro" "%TEMP%\ali_gpu.txt" >nul 2>nul
  if not errorlevel 1 (
    echo [SETUP] Legacy NVIDIA GPU detected. Trying PyTorch CUDA wheel...
    python -m pip install --disable-pip-version-check --prefer-binary -r requirements-windows-legacy-gpu.txt
    if errorlevel 1 (
      echo [WARN] CUDA wheel could not be installed. Falling back to CPU torch so the app remains usable.
      python -m pip install --disable-pip-version-check --prefer-binary "torch==2.14.0" --index-url https://download.pytorch.org/whl/cpu
      if errorlevel 1 goto fail
    )
    goto deps
  )
)
echo [SETUP] Installing PyTorch CPU fallback...
python -m pip install --disable-pip-version-check --prefer-binary "torch==2.14.0" --index-url https://download.pytorch.org/whl/cpu
if errorlevel 1 goto fail
:deps
python -m pip install --disable-pip-version-check --prefer-binary -r requirements-windows.txt
if errorlevel 1 goto fail
python scripts\windows_preflight.py
if errorlevel 1 goto fail
python scripts\configure_device.py
if errorlevel 1 goto fail
python scripts\doctor.py
if errorlevel 1 goto fail
python scripts\kca_doctor.py
if errorlevel 1 goto fail
python scripts\release_check.py
if errorlevel 1 goto fail
python -m pip check
if errorlevel 1 goto fail
echo.
echo [OK] ALI AI Windows environment is ready.
echo Run START.bat to launch.
exit /b 0
:fail
echo.
echo [ERROR] Setup/repair failed. The application was not launched.
pause
exit /b 1
```

---

### `371/588` `backend/skills/loader.py`

- **المسار الكامل:** `F:\1f\p\ALI_Studio_Pro_Design4_4.6.0\04_Adaptive_Hybrid\backend/skills/loader.py`
- **الحجم:** 626 بايت (0.6 KB)
- **الامتداد:** `.py`

```python
# -*- coding: utf-8 -*-
from __future__ import annotations
from pathlib import Path
import json,re

def discover(root:str|Path='skills'):
    root=Path(root); out=[]
    for p in sorted(list(root.rglob('*.md'))+list(root.rglob('skill.json'))):
        if p.name=='skill.json':
            try:o=json.loads(p.read_text(encoding='utf-8')); o['_path']=str(p); out.append(o)
            except Exception: pass
        else:
            text=p.read_text(encoding='utf-8',errors='ignore'); m=re.search(r'^#\s+(.+)$',text,re.M); out.append({'name':m.group(1).strip() if m else p.stem,'path':str(p),'type':'markdown'})
    return out
```

---

### `372/588` `backend/skills/project-builder.md`

- **المسار الكامل:** `F:\1f\p\ALI_Studio_Pro_Design4_4.6.0\04_Adaptive_Hybrid\backend/skills/project-builder.md`
- **الحجم:** 213 بايت (0.2 KB)
- **الامتداد:** `.md`

```markdown
# Project Builder
Inspect entry points → understand dependencies/tests → plan → snapshot → apply smallest patch → focused test → regression test → verify expected outputs → review diff → report.
```

---

### `373/588` `backend/skills/README.md`

- **المسار الكامل:** `F:\1f\p\ALI_Studio_Pro_Design4_4.6.0\04_Adaptive_Hybrid\backend/skills/README.md`
- **الحجم:** 98 بايت (0.1 KB)
- **الامتداد:** `.md`

```markdown
# Skills
Declarative workflows, not arbitrary execution. Tool execution remains permission-gated.
```

---

### `374/588` `backend/skills/registry.py`

- **المسار الكامل:** `F:\1f\p\ALI_Studio_Pro_Design4_4.6.0\04_Adaptive_Hybrid\backend/skills/registry.py`
- **الحجم:** 854 بايت (0.8 KB)
- **الامتداد:** `.py`

```python
# -*- coding: utf-8 -*-
"""Declarative local skill registry. Skills are capability instructions, not arbitrary executables."""
from __future__ import annotations
from pathlib import Path
import json
class SkillRegistry:
    def __init__(self,root):self.root=Path(root)
    def discover(self):
        rows=[]
        for p in list(self.root.glob('*/skill.json'))+list(self.root.glob('*/SKILL.md'))+list(self.root.glob('**/skill.json')):
            try:
                if p.suffix=='.json': rows.append(json.loads(p.read_text(encoding='utf-8')))
                else: rows.append({'name':p.parent.name,'path':str(p),'type':'instruction'})
            except Exception:pass
        uniq={r.get('name',r.get('path')):r for r in rows}; return list(uniq.values())
    def get(self,name):return next((x for x in self.discover() if x.get('name')==name),None)
```

---

### `375/588` `backend/START-OFFLINE.bat`

- **المسار الكامل:** `F:\1f\p\ALI_Studio_Pro_Design4_4.6.0\04_Adaptive_Hybrid\backend/START-OFFLINE.bat`
- **الحجم:** 449 بايت (0.4 KB)
- **الامتداد:** `.bat`

```batch
@echo off
setlocal EnableExtensions
cd /d "%~dp0"
if not exist ".venv\Scripts\python.exe" (
  echo [START] Offline venv is missing. Run Install\SETUP-ALL-OFFLINE.bat first.
  pause
  exit /b 1
)
.venv\Scripts\python.exe scripts\windows_preflight.py >nul 2>&1 || (
  echo [ERROR] Offline dependencies are incomplete.
  echo Run Install\SETUP-ALL-OFFLINE.bat after populating Offline_Packages.
  pause
  exit /b 1
)
.venv\Scripts\python.exe ali_ai.py
```

---

### `376/588` `backend/START.bat`

- **المسار الكامل:** `F:\1f\p\ALI_Studio_Pro_Design4_4.6.0\04_Adaptive_Hybrid\backend/START.bat`
- **الحجم:** 969 بايت (0.9 KB)
- **الامتداد:** `.bat`

```batch
@echo off
setlocal EnableExtensions
chcp 65001 >nul
cd /d "%~dp0"
title ALI AI

if not exist ".venv\Scripts\python.exe" (
  echo [START] Virtual environment not found. Running SETUP...
  call SETUP.bat
  if errorlevel 1 exit /b 1
)

call ".venv\Scripts\activate.bat"
if errorlevel 1 exit /b 1

python scripts\windows_preflight.py >nul 2>&1
if errorlevel 1 (
  echo.
  echo [START] Python environment is incomplete. Running SETUP / REPAIR...
  call SETUP.bat
  if errorlevel 1 exit /b 1
  call ".venv\Scripts\activate.bat"
  python scripts\windows_preflight.py >nul 2>&1
  if errorlevel 1 (
    echo.
    echo [ERROR] PyTorch or another required dependency is still missing.
    echo ALI AI was NOT launched to prevent another traceback.
    pause
    exit /b 1
  )
)

echo [START] Environment OK. Launching ALI AI...
python ali_ai.py
if errorlevel 1 (
  echo.
  echo [ERROR] ALI AI exited with an error.
  echo Run RUN-DOCTOR.bat for diagnostics.
  pause
  exit /b 1
)
```

---

### `377/588` `backend/tests/__init__.py`

- **المسار الكامل:** `F:\1f\p\ALI_Studio_Pro_Design4_4.6.0\04_Adaptive_Hybrid\backend/tests/__init__.py`
- **الحجم:** 75 بايت (0.1 KB)
- **الامتداد:** `.py`

```python
# -*- coding: utf-8 -*-
"""حزمة الاختبارات."""

__all__ = []
```

---

### `378/588` `backend/tests/conftest.py`

- **المسار الكامل:** `F:\1f\p\ALI_Studio_Pro_Design4_4.6.0\04_Adaptive_Hybrid\backend/tests/conftest.py`
- **الحجم:** 1223 بايت (1.2 KB)
- **الامتداد:** `.py`

```python
# -*- coding: utf-8 -*-
"""Pytest bootstrap + deterministic headless UI handling."""
import os, sys
# Force TCL/TK to use the bundled runtime tcl before any tkinter import.
_THIS = os.path.dirname(os.path.abspath(__file__))
_RUNTIME_PY = os.path.normpath(os.path.join(_THIS, "..", "..", "runtime", "python"))
os.environ.setdefault("TCL_LIBRARY", os.path.join(_RUNTIME_PY, "tcl", "tcl8.6"))
os.environ.setdefault("TK_LIBRARY", os.path.join(_RUNTIME_PY, "tcl", "tk8.6"))
os.environ.setdefault("TCLLIBPATH", os.path.join(_RUNTIME_PY, "tcl"))

from pathlib import Path
import pytest
ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path: sys.path.insert(0,str(ROOT))


def pytest_collection_modifyitems(config, items):
    # The build environment used for CI/unit verification has no X/Windows desktop.
    # Real UI tests remain enabled on a machine with a display (Windows desktop).
    if os.name != 'nt' and os.environ.get('ALI_GUI_TESTS') != '1':
        mark=pytest.mark.skip(reason='Desktop GUI display unavailable in headless environment')
        for item in items:
            if item.fspath.basename in {'test_professional_ai.py','test_ui_integration.py'}:
                item.add_marker(mark)
```

---

### `379/588` `backend/tests/test_accumulated_training.py`

- **المسار الكامل:** `F:\1f\p\ALI_Studio_Pro_Design4_4.6.0\04_Adaptive_Hybrid\backend/tests/test_accumulated_training.py`
- **الحجم:** 820 بايت (0.8 KB)
- **الامتداد:** `.py`

```python
from __future__ import annotations
from pathlib import Path
from training.accumulated_updates import AccumulatedTrainingManager

def test_markdown_validation_and_dedup(tmp_path: Path):
    root=tmp_path/'ALI'
    root.mkdir()
    f=root/'sample.md'
    f.write_text('# Training\n\nUser: كيف تنفذ الاختبار؟\n\nAssistant: سأفحص المتطلبات ثم أشغل الاختبار وأتحقق من النتيجة.\n',encoding='utf-8')
    m=AccumulatedTrainingManager(root)
    first=m.add_files([f])[0]
    assert first['accepted'] is True
    assert m.pending_batch_paths()
    second=m.add_files([f])[0]
    assert second['accepted'] is False
    assert second['reason']=='duplicate_content'
    assert m.mark_sources_as_adapterized(m.pending_batch_paths())==1
    assert not m.pending_batch_paths()
```

---

### `380/588` `backend/tests/test_adaptive_gpu_policy.py`

- **المسار الكامل:** `F:\1f\p\ALI_Studio_Pro_Design4_4.6.0\04_Adaptive_Hybrid\backend/tests/test_adaptive_gpu_policy.py`
- **الحجم:** 717 بايت (0.7 KB)
- **الامتداد:** `.py`

```python
from runtime.hardware import HardwareInfo, training_profile

def hw(free, cuda=True):
    return HardwareInfo('Windows', '3.11', 8, 32, True, 'NVIDIA Quadro M1000M', 2.0, cuda, 20, (5,0), 4, 'cuda' if cuda else 'cpu', gpu_mem_used_gb=2.0-free, gpu_mem_free_gb=free, cuda_self_test=cuda)

def test_auto_uses_gpu_when_free_vram_is_sufficient():
    p=training_profile(hw(1.20), 'auto')
    assert p['device']=='cuda' and p['seq_len']==192

def test_auto_falls_back_to_cpu_when_vram_is_low():
    p=training_profile(hw(0.40), 'auto')
    assert p['device']=='cpu'

def test_forced_gpu_rejects_unusable_cuda():
    import pytest
    with pytest.raises(RuntimeError):
        training_profile(hw(0.40, cuda=False), 'gpu')
```

---

### `381/588` `backend/tests/test_config.py`

- **المسار الكامل:** `F:\1f\p\ALI_Studio_Pro_Design4_4.6.0\04_Adaptive_Hybrid\backend/tests/test_config.py`
- **الحجم:** 1815 بايت (1.8 KB)
- **الامتداد:** `.py`

```python
# -*- coding: utf-8 -*-
"""اختبار طبقة config: paths + app_config."""

from __future__ import annotations

import json
import os
import sys
import tempfile
from pathlib import Path

# ضمان أن جذر المشروع على sys.path
ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def test_paths_basic():
    from config.paths import APP_PATHS
    assert APP_PATHS.project_root().exists()
    assert APP_PATHS.user_data_dir().exists()
    assert APP_PATHS.user_logs_dir().exists()


def test_default_config_no_secrets():
    """الإعدادات الافتراضية يجب ألا تحتوي على Lovable أو tokens."""
    from config.paths import APP_PATHS
    cfg = APP_PATHS.default_config()
    assert "site" not in cfg
    assert "token" not in cfg
    assert cfg["model"] in ("ALI-local", "ALI-local (V0.1)")
    assert cfg["perm_mode"] in ("read-only", "default", "full-access")


def test_app_config_constants():
    from config import app_config
    assert app_config.APP == "ALI AI"
    assert app_config.VERSION == "4.4.0"
    assert len(app_config.PERM_MODES) == 3
    assert len(app_config.MODELS) >= 1
    # يجب ألا يكون أي نموذج جاهز مدمج في القائمة
    for m in app_config.MODELS:
        assert "gpt" not in m.lower()
        assert "claude" not in m.lower()
        assert "llama" not in m.lower()
        assert "mistral" not in m.lower()
        assert "qwen" not in m.lower()


def test_no_lovable_anywhere():
    """اختبار الحماية: لا Lovable ولا tokens في app_config."""
    from config import app_config
    text = open(app_config.__file__, encoding="utf-8").read()
    assert "lovable" not in text.lower()
    assert "genius-connect" not in text.lower()
```

---

### `382/588` `backend/tests/test_continuous_learning_markdown.py`

- **المسار الكامل:** `F:\1f\p\ALI_Studio_Pro_Design4_4.6.0\04_Adaptive_Hybrid\backend/tests/test_continuous_learning_markdown.py`
- **الحجم:** 1350 بايت (1.3 KB)
- **الامتداد:** `.py`

```python
from pathlib import Path

from training.continuous_learning import ContinuousLearningManager


def test_import_ready_markdown_conversation_bundle(tmp_path: Path):
    root = tmp_path / 'ALI'
    root.mkdir()
    f = root / 'ALI_Conversation_Training_V1.md'
    f.write_text(
        '# Bundle\n\n'
        '## المحادثة 001 — agent\n'
        '> النوع: `agent` · المجموعة: `train`\n\n'
        '**User:** كيف أنفذ مشروعاً؟\n\n'
        '**Assistant:** أحول الطلب إلى خطة، أنفذ الأدوات المصرح بها، ثم أتحقق من النتيجة.\n\n'
        '## المحادثة 002 — debugging\n'
        '> النوع: `debugging` · المجموعة: `train`\n\n'
        '**User:** كيف أصلح الخطأ؟\n\n'
        '**Assistant:** أفحص سبب الخطأ، أطبق الإصلاح، ثم أشغل الاختبارات.\n',
        encoding='utf-8',
    )
    m = ContinuousLearningManager(root)
    result = m.import_files([f])[0]
    assert result['ok'] is True
    assert result['status'] == 'validated'
    assert result['sample_count'] == 2
    batch = root / 'artifacts' / 'continuous_learning' / 'batches' / f"{result['batch_id']}.jsonl"
    assert batch.exists()
    assert sum(1 for line in batch.read_text(encoding='utf-8').splitlines() if line.strip()) == 2
```

---

### `383/588` `backend/tests/test_continuous_learning_v4_1.py`

- **المسار الكامل:** `F:\1f\p\ALI_Studio_Pro_Design4_4.6.0\04_Adaptive_Hybrid\backend/tests/test_continuous_learning_v4_1.py`
- **الحجم:** 2290 بايت (2.2 KB)
- **الامتداد:** `.py`

```python
from pathlib import Path

from training.continuous_learning import ContinuousLearningManager
from model.registry import ModelRegistry


def make_root(tmp_path: Path):
    (tmp_path / 'models').mkdir(parents=True)
    (tmp_path / 'data' / 'training' / 'device_p50').mkdir(parents=True)
    val = tmp_path / 'data' / 'training' / 'device_p50' / 'chat_validation.jsonl'
    val.write_text('{"messages":[{"role":"user","content":"x"},{"role":"assistant","content":"y"}]}\n', encoding='utf-8')
    reg = ModelRegistry(tmp_path / 'models' / 'models.sqlite3')
    reg.register('ALI', 'bootstrap', artifact_type='base', status='active', hf_dir=str(tmp_path / 'base'), checkpoint=str(tmp_path / 'base'))
    return tmp_path, reg


def test_import_markdown_qna_and_cross_file_dedup(tmp_path: Path):
    root, reg = make_root(tmp_path)
    manager = ContinuousLearningManager(root, reg)
    first = root / 'one.md'
    first.write_text('User:\nما هو ALI؟\n\nAssistant:\nALI مساعد محلي.\n', encoding='utf-8')
    second = root / 'two.md'
    second.write_text('# نسخة ثانية\n\nUser:\nما هو ALI؟\n\nAssistant:\nALI مساعد محلي.\n', encoding='utf-8')
    a = manager.import_files([first])
    b = manager.import_files([second])
    assert a[0]['status'] == 'validated'
    assert a[0]['sample_count'] == 1
    assert b[0]['status'] == 'duplicate'
    assert 'all_samples_already_imported' in (b[0]['warnings'] or [])
    assert len(manager.pending()) == 1


def test_plain_markdown_is_rag_only(tmp_path: Path):
    root, reg = make_root(tmp_path)
    manager = ContinuousLearningManager(root, reg)
    doc = root / 'manual.md'
    doc.write_text('# ALI Manual\n\nهذا مستند معرفة وليس محادثة تدريبية صريحة.\n', encoding='utf-8')
    result = manager.import_files([doc])[0]
    assert result['ok'] is True
    assert result['status'] == 'rag_only'
    assert result['routed_to_rag'] is True
    assert not manager.pending()


def test_generation_counter_ignores_runtime_versions(tmp_path: Path):
    root, reg = make_root(tmp_path)
    reg.register('ALI', 'v3', artifact_type='merged', status='candidate', hf_dir=str(root / 'candidate'))
    manager = ContinuousLearningManager(root, reg)
    assert manager._next_generation() == 'v4'
```

---

### `384/588` `backend/tests/test_continuous_learning_v4_2.py`

- **المسار الكامل:** `F:\1f\p\ALI_Studio_Pro_Design4_4.6.0\04_Adaptive_Hybrid\backend/tests/test_continuous_learning_v4_2.py`
- **الحجم:** 2178 بايت (2.1 KB)
- **الامتداد:** `.py`

```python
from pathlib import Path
from tempfile import TemporaryDirectory

from model.registry import ModelRegistry
from training.continuous_learning import ContinuousLearningManager


def test_document_is_rag_only_and_chat_pairs_are_training():
    with TemporaryDirectory() as tmp:
        root = Path(tmp)
        registry = ModelRegistry(root / "models.sqlite3")
        manager = ContinuousLearningManager(root, registry)
        try:
            manual = root / "manual.md"
            manual.write_text("# Manual\nUse the safety checklist before promotion.", encoding="utf-8")
            first = manager.import_files([manual])[0]
            assert first["ok"] is True
            assert first["status"] == "rag_only"
            assert first["routed_to_rag"] is True
            assert manager.pending() == []

            qa = root / "qa.md"
            qa.write_text("User:\nWhat is the policy?\nAssistant:\nRun the checks first.\n", encoding="utf-8")
            second = manager.import_files([qa])[0]
            assert second["ok"] is True
            assert second["status"] == "validated"
            assert second["sample_count"] == 1
            assert len(manager.pending()) == 1
        finally:
            manager.close()
            del manager
            del registry
            # Give Windows a moment to release the SQLite file handles
            import gc; gc.collect()
            import time; time.sleep(0.05)


def test_duplicate_source_is_rejected():
    with TemporaryDirectory() as tmp:
        root = Path(tmp)
        registry = ModelRegistry(root / "models.sqlite3")
        manager = ContinuousLearningManager(root, registry)
        try:
            qa = root / "qa.md"
            qa.write_text("User:\nHi\nAssistant:\nHello\n", encoding="utf-8")
            assert manager.import_files([qa])[0]["status"] == "validated"
            duplicate = manager.import_files([qa])[0]
            assert duplicate["ok"] is False
            assert duplicate["status"] == "duplicate"
        finally:
            manager.close()
            del manager
            del registry
            import gc; gc.collect()
            import time; time.sleep(0.05)
```

---

### `385/588` `backend/tests/test_conversation_bundle_import.py`

- **المسار الكامل:** `F:\1f\p\ALI_Studio_Pro_Design4_4.6.0\04_Adaptive_Hybrid\backend/tests/test_conversation_bundle_import.py`
- **الحجم:** 876 بايت (0.9 KB)
- **الامتداد:** `.py`

```python
from pathlib import Path

from training.continuous_learning import ContinuousLearningManager


def test_bundled_v1_conversation_markdown_imports_504_samples(tmp_path: Path):
    project_root = Path(__file__).resolve().parents[2]
    source = project_root / "ALI_Conversation_Training_V1.md"
    assert source.is_file()
    runtime_root = tmp_path / "runtime"
    manager = ContinuousLearningManager(runtime_root)
    result = manager.import_files([source])[0]
    assert result["ok"] is True
    assert result["status"] == "validated"
    assert result["sample_count"] == 504
    assert result["routed_to_rag"] is True
    batch = runtime_root / "artifacts" / "continuous_learning" / "batches" / f"{result['batch_id']}.jsonl"
    assert batch.is_file()
    lines = [line for line in batch.read_text(encoding="utf-8").splitlines() if line.strip()]
    assert len(lines) == 504
```

---

### `386/588` `backend/tests/test_conversation_bundle_import_escaped_v2.py`

- **المسار الكامل:** `F:\1f\p\ALI_Studio_Pro_Design4_4.6.0\04_Adaptive_Hybrid\backend/tests/test_conversation_bundle_import_escaped_v2.py`
- **الحجم:** 848 بايت (0.8 KB)
- **الامتداد:** `.py`

```python
from pathlib import Path
from training.continuous_learning import ContinuousLearningManager

def test_escaped_bold_conversation_bundle_imports_all_samples(tmp_path: Path):
    root = tmp_path / "escaped_bold_120.md"
    sections=[]
    for i in range(120):
        bs = chr(92)
        sections.append(f"**## المحادثة {i+1} — agent**\n\n> النوع: `agent` · المجموعة: `train`\n\n**{bs}*{bs}*User:{bs}*{bs}*** سؤال اختبار {i+1}؟\n\n**{bs}*{bs}*Assistant:{bs}*{bs}*** إجابة اختبار {i+1}.\n")
    root.write_text("\n---\n".join(sections), encoding="utf-8")
    m = ContinuousLearningManager(tmp_path / "ALI")
    result = m.import_files([root])[0]
    assert result["ok"] is True
    assert result["status"] == "validated"
    assert result["sample_count"] == 120
    assert result["routed_to_rag"] is True
```

---

### `387/588` `backend/tests/test_conversation_sessions.py`

- **المسار الكامل:** `F:\1f\p\ALI_Studio_Pro_Design4_4.6.0\04_Adaptive_Hybrid\backend/tests/test_conversation_sessions.py`
- **الحجم:** 619 بايت (0.6 KB)
- **الامتداد:** `.py`

```python
from memory.sessions import ConversationSessionStore

def test_conversation_sessions_roundtrip(tmp_path):
    s=ConversationSessionStore(tmp_path/'sessions.sqlite3')
    row=s.create('محادثة جديدة','v1')
    sid=row['id']
    s.append(sid,'user','مرحبا','v1')
    s.append(sid,'assistant','أهلاً بك','v1')
    got=s.get(sid)
    assert got['title'].startswith('مرحبا')
    assert [m['role'] for m in got['messages']] == ['user','assistant']
    s.rename(sid,'مشروعي')
    assert s.get(sid)['title'].startswith('مشروعي')
    assert s.delete(sid) is True
    assert s.list() == []
```

---

### `388/588` `backend/tests/test_core.py`

- **المسار الكامل:** `F:\1f\p\ALI_Studio_Pro_Design4_4.6.0\04_Adaptive_Hybrid\backend/tests/test_core.py`
- **الحجم:** 2044 بايت (2.0 KB)
- **الامتداد:** `.py`

```python
# -*- coding: utf-8 -*-
"""اختبارات V0.3 — core/events + core/context."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def test_event_publish_calls_subscribers():
    from core.events import EventBus, Event
    bus = EventBus()
    seen = []
    bus.subscribe("test.evt", lambda e: seen.append(e.data))
    bus.publish(Event("test.evt", {"x": 1}))
    bus.publish(Event("test.evt", {"x": 2}))
    assert len(seen) == 2
    assert seen[0]["x"] == 1
    assert seen[1]["x"] == 2


def test_event_unsubscribe():
    from core.events import EventBus, Event
    bus = EventBus()
    h = lambda e: None
    bus.subscribe("t", h)
    bus.unsubscribe("t", h)
    bus.publish(Event("t", {}))   # لا exception


def test_event_handler_error_does_not_break_others():
    from core.events import EventBus, Event
    bus = EventBus()
    results = []
    bus.subscribe("t", lambda e: (_ for _ in ()).throw(RuntimeError("boom")))
    bus.subscribe("t", lambda e: results.append("ok"))
    bus.publish(Event("t", {}))
    assert results == ["ok"]


def test_context_add_messages():
    from core.context import ConversationContext
    ctx = ConversationContext(thread_id="t1", project_dir=".")
    ctx.add_user("hi")
    ctx.add_assistant("hello")
    assert len(ctx.messages) == 2
    assert ctx.last_user() == "hi"


def test_context_to_dict():
    from core.context import ConversationContext
    ctx = ConversationContext(
        thread_id="t2", project_dir="/tmp",
        perm_mode="default", model="ALI-local",
    )
    ctx.add_user("q")
    d = ctx.to_dict()
    assert d["thread_id"] == "t2"
    assert d["perm_mode"] == "default"
    assert len(d["messages"]) == 1


def test_events_constants_present():
    from core.events import Events
    assert Events.USER_MESSAGE == "message.user"
    assert Events.TOOL_START == "tool.start"
    assert Events.PERMISSION_REQUEST == "permission.request"
```

---

### `389/588` `backend/tests/test_database.py`

- **المسار الكامل:** `F:\1f\p\ALI_Studio_Pro_Design4_4.6.0\04_Adaptive_Hybrid\backend/tests/test_database.py`
- **الحجم:** 4293 بايت (4.2 KB)
- **الامتداد:** `.py`

```python
# -*- coding: utf-8 -*-
"""اختبار V0.2 Database: migrations + repos."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import pytest

import database.database as db_mod
import database.schema as schema_mod


@pytest.fixture
def fresh_db(tmp_path):
    """يوفّر instance معزولة من Database لكل اختبار."""
    p = tmp_path / "ali.db"
    db = db_mod.Database.__new__(db_mod.Database)
    db.__init__(p)
    yield db


def test_bootstrap_creates_schema(fresh_db):
    h = fresh_db.healthcheck()
    assert h["schema_version"] == schema_mod.SCHEMA_VERSION
    assert h["journal_mode"].lower() == "wal"
    assert h["foreign_keys"] is True


def test_required_tables_exist(fresh_db):
    required = {
        "meta", "projects", "threads", "messages",
        "settings", "logs", "tool_calls", "sessions",
    }
    with fresh_db.cursor() as cur: