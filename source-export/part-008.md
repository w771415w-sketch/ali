
**User:** كيف منع التغيير الذاتي غير الآمن؟

**Assistant:** التطوير الذاتي يجب أن يمر عبر snapshot وpatch وchecks وtests وverification ثم قبول أو rollback، وليس تعديلاً بلا حدود.

---

## المحادثة 479 — Terminal
> النوع: `terminal` · المجموعة: `test` · ID: `2be01dfc735a87756cab135ae568b6a6e8c14f9440dadfa610c13f720c551dde`

**User:** أريد أن أعرف أفضل طريقة لـTerminal داخل الواجهة. داخل المشروع

**Assistant:** أتحقق من الأمر والصلاحيات، أشغله، أسجل exit code والمخرجات، ثم أقرر الخطوة التالية بناءً على النتيجة الفعلية.

---

## المحادثة 480 — التدريب
> النوع: `training` · المجموعة: `test` · ID: `6ae200cb17bf7823c078b348352555adfefc51b4d53a4fea40312921670cf116`

**User:** اجعل ALI يستطيع تدريب سلوك الإجابة. مع اختبار كامل

**Assistant:** أفحص البيانات وأنظفها وأزيل التكرار والأسرار، ثم أبني أمثلة User/Assistant واضحة وأدرب LoRA فوق الإصدار النشط وأقيّم المرشح.

---

## المحادثة 481 — تعلم تراكمي
> النوع: `continuous` · المجموعة: `test` · ID: `3cc962ae2a1073f25a201092d6eb2723cbfbb783ab4c000c369e5c5c1aded248`

**User:** كيف أضيف قدرة منع إعادة تدريب البيانات إلى ALI؟ من خلال واجهة ALI

**Assistant:** تُبنى النسخة الجديدة فوق Active، وتستخدم البيانات الجديدة فقط. بعد التدريب تُجرى Evaluation وRegression ثم Promotion أو Rollback.

---

## المحادثة 482 — الذاكرة
> النوع: `memory` · المجموعة: `test` · ID: `80e40430a09fa50fe731ba14ebc08674848c0d7a44bca171ca1a7164f100f499`

**User:** كيف أنفذ التعلم من المحادثات السابقة بشكل احترافي؟ مع حفظ rollback

**Assistant:** هذه معلومة مناسبة لـMemory بنوع واضح، لأن ذلك يسمح بتحديثها أو حذفها دون إعادة تدريب النموذج.

---

## المحادثة 483 — العتاد
> النوع: `hardware` · المجموعة: `test` · ID: `cde101fdd68a69821b0957ec44c582568326fdcb6f0942ee742c524345e9e4d4`

**User:** قم بـتدريب على CPU. دون كسر الوظائف الحالية

**Assistant:** أختار إعداداً محافظاً يناسب الذاكرة والـCPU، مثل batch صغير وgradient accumulation وsequence length محدود، ثم أرفع الحمل تدريجياً.

---

## المحادثة 484 — تعلم تراكمي
> النوع: `continuous` · المجموعة: `test` · ID: `7109b4036f3dc6c3bd2f0d4e62f462d03bf01abb7eb84af4edc7ddbf113acc19`

**User:** أريد أن أعرف أفضل طريقة لـمنع إعادة تدريب البيانات. داخل المشروع

**Assistant:** تُبنى النسخة الجديدة فوق Active، وتستخدم البيانات الجديدة فقط. بعد التدريب تُجرى Evaluation وRegression ثم Promotion أو Rollback.

---

## المحادثة 485 — العتاد
> النوع: `hardware` · المجموعة: `test` · ID: `ca5a7202f9c68c434cd98f802e22b4a36a8190cf0be02d38643b17e98b69b8aa`

**User:** كيف تدريب على CPU؟

**Assistant:** أختار إعداداً محافظاً يناسب الذاكرة والـCPU، مثل batch صغير وgradient accumulation وsequence length محدود، ثم أرفع الحمل تدريجياً.

---

## المحادثة 486 — تتبع المصدر
> النوع: `provenance` · المجموعة: `test` · ID: `7a0100c6bae041be07773fba47b8c935536c4b960f4b143cc89037117b06a384`

**User:** How do I return sources for answers with verification?

**Assistant:** When RAG is used, I return the relevant source files and retrieval metadata when the interface supports it

---

## المحادثة 487 — جودة البيانات
> النوع: `data_quality` · المجموعة: `test` · ID: `f803fd4a3eef866d001535cab1058c33119beb87dd10b091c1d2bda87d67efc4`

**User:** كيف فصل train/validation/test؟

**Assistant:** أتحقق من البنية والمحتوى، أزيل التكرار والأمثلة التالفة والأسرار، وأبقي train وvalidation وtest منفصلة.

---

## المحادثة 488 — إدارة النماذج
> النوع: `models` · المجموعة: `test` · ID: `fe52db0ed360f8691f178679b7be6ae90d258a062443c72b384aabd39b3b31eb`

**User:** أريد تنفيذ Rollback داخل المشروع. على Windows

**Assistant:** أستخدم Model Registry لتحديد Active. المرشح يبقى غير نشط حتى يجتاز التقييم، مع الاحتفاظ بالنسخة السابقة للرجوع.

---

## المحادثة 489 — تصحيح الأخطاء
> النوع: `debugging` · المجموعة: `test` · ID: `be3c7472891449e02a8bb6ef478f4170a33239bc53819854bb7703d03a8c6972`

**User:** أريد تنفيذ إصلاح خطأ في المشروع داخل المشروع. على Windows

**Assistant:** أبدأ من الخطأ الفعلي والسياق، أحدد السبب الأقرب، أطبق أصغر إصلاح آمن، ثم أعيد الاختبار وأفحص الانحدار.

---

## المحادثة 490 — تصحيح الأخطاء
> النوع: `debugging` · المجموعة: `test` · ID: `83ef62f9eb5a762077542cc9af40b7265f52e4abd701bed75dac24254b5b36c1`

**User:** كيف إصلاح فشل build؟

**Assistant:** أبدأ من الخطأ الفعلي والسياق، أحدد السبب الأقرب، أطبق أصغر إصلاح آمن، ثم أعيد الاختبار وأفحص الانحدار.

---

## المحادثة 491 — RAG والمعرفة
> النوع: `rag` · المجموعة: `test` · ID: `26cf890cc195d8108b3a3ab8f662fc4e126c98951d51403678184ddbeea921fe`

**User:** كيف أضيف قدرة إضافة وثيقة إلى المعرفة إلى ALI؟ من خلال واجهة ALI

**Assistant:** هذه حالة مناسبة لـRAG: أدخل المصدر في Knowledge Store ثم أسترجع المقاطع ذات الصلة وقت الإجابة دون تعديل الأوزان.

---

## المحادثة 492 — التحقق والاختبارات
> النوع: `verification` · المجموعة: `test` · ID: `067f41e02d65bff90022743b02803c263242e97e1ee315b75566681a52d9205f`

**User:** كيف أضيف قدرة التحقق بعد تعديل إلى ALI؟ من خلال واجهة ALI

**Assistant:** أشغّل الفحص أو الاختبار المرتبط ثم اختبارات الانحدار وأتحقق من exit code والسجل قبل تقرير النتيجة.

---

## المحادثة 493 — Git
> النوع: `git` · المجموعة: `test` · ID: `7a3c87f01048e01b13459d61c5daa143a5eafe4192ab12e81a13f441708a1205`

**User:** أريد أن أعرف أفضل طريقة لـإنشاء commit آمن. داخل المشروع

**Assistant:** أراجع status وdiff أولاً، ثم أشغّل الاختبارات، وبعد نجاحها فقط أنفذ عملية Git المطلوبة.

---

## المحادثة 494 — التحسين الذاتي
> النوع: `self_improvement` · المجموعة: `test` · ID: `cce36ea2547f5921beda06174ce7a13b0f0784598b011b05171b507dfd51245a`

**User:** How do I improve itself safely?

**Assistant:** I can create a snapshot, apply a bounded patch, run checks and tests, and keep or roll back the change based on evidence

---

## المحادثة 495 — الصلاحيات والأمن
> النوع: `security` · المجموعة: `test` · ID: `03211aa8e26c85b8f412c791f52d2c2e3966d974c7b85c713202ad1e4a1d68c0`

**User:** أريد تنفيذ الصلاحيات داخل المشروع. على Windows

**Assistant:** أطبق فحص الصلاحيات وتنقية الأسرار والتدقيق، ولا أسمح للنموذج بتجاوز الحدود أو رفع امتيازاته تلقائياً.

---

## المحادثة 496 — الأمان التشغيلي
> النوع: `safety` · المجموعة: `test` · ID: `b4d3ca72837d153aecb949bc9574a8ffc6291f4cfe78d2c8639245ca119a37dc`

**User:** اجعل ALI يستطيع عدم اختلاق النتائج. مع اختبار كامل

**Assistant:** لا أدّعي نتيجة غير متحققة. عند غياب الدليل أقول إن الحالة غير متحققة وأوضح ما يلزم فحصه قبل الاعتماد.

---

## المحادثة 497 — RAG والمعرفة
> النوع: `rag` · المجموعة: `test` · ID: `1d86adfa613b083bb3025ca898ef57bc46fea827cd8040b1a9ef0f547a549ae9`

**User:** اجعل ALI يستطيع معلومة متغيرة باستمرار. مع اختبار كامل

**Assistant:** هذه حالة مناسبة لـRAG: أدخل المصدر في Knowledge Store ثم أسترجع المقاطع ذات الصلة وقت الإجابة دون تعديل الأوزان.

---

## المحادثة 498 — التحقق والاختبارات
> النوع: `verification` · المجموعة: `test` · ID: `9f260457ba91311e4f1183c1a585a800abce09e0aa1522f7551ec3d571c7e62e`

**User:** قم بـالتحقق بعد تعديل. دون كسر الوظائف الحالية

**Assistant:** أشغّل الفحص أو الاختبار المرتبط ثم اختبارات الانحدار وأتحقق من exit code والسجل قبل تقرير النتيجة.

---

## المحادثة 499 — التخطيط
> النوع: `planning` · المجموعة: `test` · ID: `2a2b4bc12bd0ebd988e4241cdcb53c0cf71164e7dbd185fea78483ce6153cfce`

**User:** قم بـإدارة مهمة طويلة. دون كسر الوظائف الحالية

**Assistant:** أقسم المهمة إلى مراحل واضحة: فحص، تخطيط، تنفيذ، اختبار، تحقق، ثم تسليم. كل مرحلة تعتمد على نتيجة المرحلة السابقة.

---

## المحادثة 500 — إدارة النماذج
> النوع: `models` · المجموعة: `test` · ID: `f1bc088b69f022bde83f94ff1818ccca8d05696b30ddeeba352466b17caeea78`

**User:** كيف اختيار نموذج نشط؟

**Assistant:** أستخدم Model Registry لتحديد Active. المرشح يبقى غير نشط حتى يجتاز التقييم، مع الاحتفاظ بالنسخة السابقة للرجوع.

---

## المحادثة 501 — معمارية النظام
> النوع: `architecture` · المجموعة: `test` · ID: `6981793f87ebc0538326dcbf071fffec544aea0fcc9fab6104154a7d38d4ee3a`

**User:** ما الخطوات العملية لـفصل الطبقات؟ بطريقة آمنة

**Assistant:** أفصل الواجهة عن الذكاء: React/Electron للواجهة، C# للـLauncher، وPython للـAgent والـAI، مع IPC واضح وآمن.

---

## المحادثة 502 — إدارة وتنفيذ المشاريع
> النوع: `project` · المجموعة: `test` · ID: `6b54be062df594b0859b5a1d3fad7067b80477c60e27b3960d18ea20c7caac69`

**User:** أريد تنفيذ بناء مشروع من فكرة داخل المشروع. على Windows

**Assistant:** أحوّل المطلوب إلى مواصفات قصيرة، أحدد الملفات، أنفذها تدريجياً، ثم أختبر التشغيل قبل اعتبارها جاهزة.

---

## المحادثة 503 — تتبع المصدر
> النوع: `provenance` · المجموعة: `test` · ID: `02bf99bdd4199dac96a9cb94501cc4d0e6ebcdb6bdaadfc6843f2e504cf08848`

**User:** قم بـمصدر الإجابة. دون كسر الوظائف الحالية

**Assistant:** عند استخدام RAG أرفق المصدر ودرجة الصلة. أما المعرفة المضمّنة داخل الأوزان فلا يمكن نسبها لمصدر محدد تلقائياً.

---

## المحادثة 504 — Terminal
> النوع: `terminal` · المجموعة: `test` · ID: `5085867a55f6813576635d996a36592054377a094b4e561c167b629363515bf7`

**User:** How do I run a terminal command safely?

**Assistant:** I check permission, execute the command, capture exit code and output, and use the verified result in the next step

---
```

---

### `3/588` `backend/agent/project_orchestrator.py`

- **المسار الكامل:** `F:\1f\p\ALI_Studio_Pro_Design4_4.6.0\04_Adaptive_Hybrid\backend/agent/project_orchestrator.py`
- **الحجم:** 2423 بايت (2.4 KB)
- **الامتداد:** `.py`

```python
# -*- coding: utf-8 -*-
"""Evidence-driven project agent helpers: inspect, snapshot, test and verify."""
from __future__ import annotations
from pathlib import Path
import hashlib, json, subprocess, time
from typing import Any
from core.workflow import ChangeWorkflow,Phase
SKIP={'.git','.venv','__pycache__','node_modules','dist','build'}
class ProjectOrchestrator:
    def __init__(self,root:str|Path):self.root=Path(root).resolve()
    def inventory(self,max_files:int=4000)->dict[str,Any]:
        rows=[]
        for p in self.root.rglob('*'):
            if p.is_file() and not any(x in p.parts for x in SKIP):
                try: rows.append({'path':str(p.relative_to(self.root)),'size':p.stat().st_size})
                except OSError: continue
                if len(rows)>=max_files: break
        return {'root':str(self.root),'files':rows,'count':len(rows)}
    def fingerprint(self)->str:
        h=hashlib.sha256()
        for row in sorted(self.inventory()['files'],key=lambda x:x['path']):
            h.update(row['path'].encode()); h.update(str(row['size']).encode()); p=self.root/row['path']
            try: h.update(hashlib.sha256(p.read_bytes()).digest() if row['size']<=2_000_000 else str(p.stat().st_mtime_ns).encode())
            except OSError: pass
        return h.hexdigest()
    def snapshot(self,dst:str|Path)->Path:
        dst=Path(dst); dst.mkdir(parents=True,exist_ok=True)
        (dst/'manifest.json').write_text(json.dumps({'fingerprint':self.fingerprint(),'created_at':time.time()},indent=2),encoding='utf-8'); return dst
    def run_tests(self,timeout:int=900)->dict[str,Any]:
        try:p=subprocess.run(['python','-m','pytest','tests','-q'],cwd=self.root,capture_output=True,text=True,timeout=timeout)
        except Exception as e:return {'passed':False,'returncode':-1,'stdout':'','stderr':str(e)}
        return {'passed':p.returncode==0,'returncode':p.returncode,'stdout':p.stdout[-10000:],'stderr':p.stderr[-10000:]}
    def verify_paths(self,expected:list[str])->dict[str,Any]:
        missing=[x for x in expected if not (self.root/x).exists()]; return {'verified':not missing,'missing':missing}
    def workflow(self,task:str,approved:bool=False)->dict[str,Any]:
        wf=ChangeWorkflow(task); wf.transition(Phase.PLAN,notes='plan created'); wf.transition(Phase.SNAPSHOT,notes='fingerprint='+self.fingerprint()); wf.state.approved=approved; return wf.state.to_dict()
```

---

### `4/588` `backend/agent/README.md`

- **المسار الكامل:** `F:\1f\p\ALI_Studio_Pro_Design4_4.6.0\04_Adaptive_Hybrid\backend/agent/README.md`
- **الحجم:** 85 بايت (0.1 KB)
- **الامتداد:** `.md`

```markdown
# Agent
Planner, project orchestrator, recipes, checkpoints and isolated workspaces.
```

---

### `5/588` `backend/agent/recipes/project_change_cycle.md`

- **المسار الكامل:** `F:\1f\p\ALI_Studio_Pro_Design4_4.6.0\04_Adaptive_Hybrid\backend/agent/recipes/project_change_cycle.md`
- **الحجم:** 137 بايت (0.1 KB)
- **الامتداد:** `.md`

```markdown
# Project Change Cycle
Inspect, plan, snapshot, modify, test, verify, review, complete. Never treat exit code alone as proof of success.
```

---

### `6/588` `backend/ALI-AI.bat`

- **المسار الكامل:** `F:\1f\p\ALI_Studio_Pro_Design4_4.6.0\04_Adaptive_Hybrid\backend/ALI-AI.bat`
- **الحجم:** 25 بايت (0.0 KB)
- **الامتداد:** `.bat`

```batch
@echo off
call START.bat
```

---

### `7/588` `backend/ali_agent.py`

- **المسار الكامل:** `F:\1f\p\ALI_Studio_Pro_Design4_4.6.0\04_Adaptive_Hybrid\backend/ali_agent.py`
- **الحجم:** 2895 بايت (2.8 KB)
- **الامتداد:** `.py`

```python
# -*- coding: utf-8 -*-
"""Compatibility entry point for older ALI Agent integrations/tests.

The canonical desktop application lives in ``ali_ai.py``. This adapter preserves
small legacy helper methods while delegating real work to the new runtime.
"""
from ali_ai import App as _App, main, load_cfg, save_cfg, ROOT, DB, C
from config.paths import APP_PATHS
import tkinter as tk

class App(_App):
    def __init__(self, root):
        super().__init__(root)
        self.perm_mode = tk.StringVar(value=self.runtime.permission_manager.mode)
        self.perm_mode.trace_add('write', self._sync_perm_mode)

    def _sync_perm_mode(self, *_):
        mode=self.perm_mode.get()
        if mode:
            self.runtime.permission_manager.set_mode(mode)
            self.cfg['perm_mode']=mode
            save_cfg(self.cfg)

    def _dispatch_tool(self, text):
        t=text.strip(); low=t.lower()
        if low.startswith(('read_file ','read ')):
            return ('read_file', {'path': t.split(None,1)[1]}, None)
        if low in ('list_dir','ls') or low.startswith(('list_dir ','ls ')):
            return ('list_dir', {'path': t.split(None,1)[1] if len(t.split(None,1))>1 else ''}, None)
        if low.startswith(('search_files ','search ')):
            return ('search_files', {'pattern': t.split(None,1)[1]}, None)
        if low.startswith(('write_file ','write ')):
            return ('write_file', {'path': t.split(None,1)[1]}, None)
        if low.startswith(('run_command ','run ')):
            return ('run_command', {'command': t.split(None,1)[1]}, None)
        if low.startswith('git status'):
            return ('git_status', {}, None)
        if low.startswith('git diff'):
            return ('git_diff', {}, None)
        return None

    def _local_reply(self, text):
        d=self._dispatch_tool(text)
        if d:
            name,kwargs,_=d
            ctx=self._compat_context()
            result=self.runtime._tool(name,ctx,**kwargs)
            if result.get('ok'):
                try:
                    from database.database import get_db, ToolCallRepo
                    repo=ToolCallRepo(get_db()); call_id=repo.start(None,None,name,kwargs); repo.finish(call_id,'completed',result.get('data'))
                except Exception:
                    pass
                return f"✅ نجح تنفيذ {name}\n{result.get('data','')}"
            return f"⚠ فشل تنفيذ {name}: {result.get('error','unknown error')}"
        names=', '.join(sorted(self.runtime.registry.all()))
        return names

    def _compat_context(self):
        from core.context import ConversationContext
        return ConversationContext('compat',self.project_dir,self.runtime.permission_manager.mode,'ALI','high',tool_registry=self.runtime.registry)

__all__=["App","main","load_cfg","save_cfg","ROOT","DB","C","APP_PATHS"]

if __name__ == "__main__":
    main()
```

---

### `8/588` `backend/ali_ai.py`

- **المسار الكامل:** `F:\1f\p\ALI_Studio_Pro_Design4_4.6.0\04_Adaptive_Hybrid\backend/ali_ai.py`
- **الحجم:** 88020 بايت (86.0 KB)
- **الامتداد:** `.py`

```python
# -*- coding: utf-8 -*-
"""ALI AI 2.5 — Professional Assistant / P50 local command center.

The desktop app is the control plane. It does not contain training logic itself:
UI -> jobs -> pipeline/runtime -> artifacts -> registry.

Primary UX:
- three-pane workspace (projects/conversations | local chat | inspector/editor/tools)
- persistent conversations in SQLite
- local streaming inference
- bounded tool calling with confirmation
- dataset/knowledge pipeline
- real tokenizer/base/SFT/LoRA training jobs
- immutable weight import + registry + promotion
- GGUF conversion/validation bridge
"""
from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import threading
import time
from pathlib import Path
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, simpledialog

from config.app_config import APP, VERSION, PALETTE, AI_MODES, PERM_MODES, MODELS, EFFORTS
from config.i18n import tr, normalize_language, is_rtl
from ui.rtl import configure_root, start_side, end_side, anchor_start
from config.paths import APP_PATHS
from core.context import ConversationContext
from core.runtime import ALIRuntime
from core.orchestrator import Orchestrator
from core.job_manager import JobManager
from core.session_store import SessionStore
from runtime.hardware import detect, training_profile, model_profile
from runtime.device_policy import choose_policy
from config.device_profiles import recommend_for_hardware
from runtime.resources import ResourceManager
from model.registry import ModelRegistry
from training.scaling import PROFILES, build_training_plan
from ui.theme import configure as configure_theme
from ui.widgets import ChatView, LineNumberedEditor
from control_plane import KCARequestRouter, RequestEnvelope, summary as kca_summary
from training.accumulated_updates import AccumulatedTrainingManager
from assistant.error_learning import ErrorLearningStore
from core.response_guard import sanitize_output, stream_safe
from ui.activity import ActivityCenter
from integration.hermes import HermesContextRouter

ROOT = APP_PATHS.project_root()
DB = ROOT / "artifacts" / "ali.sqlite3"
C = PALETTE


def load_cfg() -> dict:
    default = {
        "name": "Windows PC",
        "language": "ar",
        "ai_mode": "professional",
        "last_dir": str(ROOT),
        "allow_internet": True,
        "auto_improve": True,
        "perm_mode": "default",
        "model": "ALI",
        "runtime": {"context": 384, "max_new_tokens": 384, "temperature": .65},
        "ui": {"right_tab": 0},
    }
    try:
        p = APP_PATHS.user_config()
        if p.exists():
            data = json.loads(p.read_text(encoding="utf-8"))
            for key, value in default.items():
                if key not in data:
                    data[key] = value
            return data
    except Exception:
        pass
    return default


def save_cfg(cfg: dict) -> None:
    p = APP_PATHS.user_config()
    p.parent.mkdir(parents=True, exist_ok=True)
    tmp = p.with_suffix(".tmp")
    tmp.write_text(json.dumps(cfg, ensure_ascii=False, indent=2), encoding="utf-8")
    os.replace(tmp, p)


class App:
    """Professional desktop UI, kept backward compatible with older tests."""

    def __init__(self, root: tk.Tk):
        self.root = root
        self.cfg = load_cfg()
        self.language = normalize_language(self.cfg.get("language", "ar"))
        self.rtl = is_rtl(self.language)
        self.busy = False
        self.cancel_requested = False
        self.history: list[dict] = []
        self.current_thread = ""
        self.streaming_bubble = None
        self.last_assistant_bubble = None
        self.project_dir = os.path.abspath(self.cfg.get("last_dir") or ROOT)

        self.hardware = detect()
        self.policy = choose_policy(self.hardware)
        self.train_profile = training_profile(self.hardware)
        self.model_profile = model_profile(self.hardware)
        self.device_profile = recommend_for_hardware(self.hardware)
        self.resources = ResourceManager(self.hardware)

        self.registry = ModelRegistry(ROOT / "models" / "models.sqlite3")
        # Heavy model/training services are lazy-loaded so the desktop shell stays responsive.
        self.model_manager = None
        self.weights = None
        self.pipeline = None
        self.kca_router = KCARequestRouter()
        self.kca = kca_summary()
        self.self_manager = __import__("autonomy.self_manager", fromlist=["SelfManager"]).SelfManager(
            ROOT, max(8, int(self.hardware.ram_gb or 8))
        )
        self.runtime = ALIRuntime(
            ROOT,
            DB,
            None,
            bool(self.cfg.get("allow_internet", False)),
        )
        self.runtime.permission_manager.set_mode(self.cfg.get("perm_mode", "default"))
        self.orchestrator = Orchestrator(self.runtime)
        self.jobs = JobManager(ROOT / "runtime" / "jobs.json")
        self.accumulated_training = AccumulatedTrainingManager(ROOT, merge_threshold=4)
        self.error_learning = ErrorLearningStore(ROOT / "runtime_error_learning.sqlite3", ROOT)
        self.hermes_router = HermesContextRouter()
        self._hermes_prompt_context = ""
        self.sessions = SessionStore(DB)
        self.project_id = self.sessions.ensure_project(self.project_dir, Path(self.project_dir).name)
        self.thread_repo = self.sessions.threads
        self.message_repo = self.sessions.messages

        runtime_cfg = self.cfg.get("runtime", {})
        self.temp_var = tk.DoubleVar(value=float(runtime_cfg.get("temperature", .65)))
        self.ctx_var = tk.IntVar(value=int(runtime_cfg.get("context", self.policy["recommended_context"])))
        self.out_var = tk.IntVar(value=int(runtime_cfg.get("max_new_tokens", self.train_profile["max_new_tokens"])))
        self.ai_mode = tk.StringVar(value=self.cfg.get("ai_mode", "professional"))
        self.perm_mode = tk.StringVar(value=self.cfg.get("perm_mode", "default"))

        root.title(f"{APP} {VERSION} — Command Center")
        root.geometry("1600x960")
        root.minsize(1240, 760)
        root.configure(bg=C["BG"])
        configure_root(root, self.language)
        root.protocol("WM_DELETE_WINDOW", self._on_close)

        configure_theme(root)
        self._build()
        self._new_thread(silent=True)
        self._refresh_all()
        root.after(2500, self._refresh_hardware_loop)
        root.after(1800, self._refresh_jobs_loop)
        root.after(5000, self._auto_improvement_tick)

    # ---------- shell ----------
    def _build(self):
        self._build_header()
        self.body = ttk.Panedwindow(self.root, orient="horizontal")
        self.body.pack(fill="both", expand=True, padx=8, pady=8)

        self.left = ttk.Frame(self.body, style="Panel.TFrame", width=290)
        self.center = ttk.Frame(self.body)
        self.right = ttk.Frame(self.body, style="Panel.TFrame", width=390)
        self._set_pane_order()

        self._build_left()
        self._build_center()
        self._build_right()
        self._build_status()

        self.root.bind("<Control-n>", lambda _e: self._new_thread())
        self.root.bind("<Control-Return>", lambda _e: self.send())
        self.root.bind("<Control-Shift-P>", lambda _e: self.settings_dialog())
        self.root.bind("<F5>", lambda _e: self._refresh_all())

    def _set_pane_order(self):
        # The visual shell is mirrored as a unit: Arabic RTL places navigation on the right; English LTR on the left.
        try:
            existing = tuple(self.body.panes())
            for pane in existing:
                self.body.forget(pane)
            ordered = ((self.right, 2), (self.center, 4), (self.left, 1)) if self.rtl else ((self.left, 1), (self.center, 4), (self.right, 2))
            for pane, weight in ordered:
                self.body.add(pane, weight=weight)
        except Exception:
            # Keep the shell usable on Tk/ttk builds with different pane APIs.
            try:
                self.body.add(self.left, weight=1)
                self.body.add(self.center, weight=4)
                self.body.add(self.right, weight=2)
            except Exception:
                pass

    def set_language(self, language: str):
        """Persist language and rebuild the shell so every pane mirrors direction consistently."""
        new_lang = normalize_language(language)
        if new_lang == self.language:
            return
        active_thread = self.current_thread
        self.language = new_lang
        self.rtl = is_rtl(new_lang)
        self.cfg["language"] = new_lang
        save_cfg(self.cfg)
        configure_root(self.root, new_lang)
        for child in list(self.root.winfo_children()):
            try: child.destroy()
            except Exception: pass
        self._build()
        self.current_thread = active_thread
        self._load_thread_by_id(active_thread)
        self._refresh_all()

    def toggle_language(self):
        self.set_language("en" if self.language == "ar" else "ar")

    def _load_thread_by_id(self, thread_id: str):
        if not thread_id or not getattr(self, "thread_list", None):
            return
        if not self.thread_ids or thread_id not in self.thread_ids:
            return
        idx = self.thread_ids.index(thread_id)
        self.thread_list.selection_clear(0, "end")
        self.thread_list.selection_set(idx)
        self._thread_selected()

    def _build_header(self):
        c = C; root = self.root; side0 = start_side(root); side1 = end_side(root)
        h = tk.Frame(root, bg=c["BG"], height=72, highlightbackground=c["LINE"], highlightthickness=1)
        h.pack(fill="x"); h.pack_propagate(False)
        brand = tk.Frame(h, bg=c["BG"]); brand.pack(side=side0, padx=16)
        tk.Label(brand, text="◈", bg=c["BG"], fg=c["BLUE"], font=("Segoe UI Semibold", 21)).pack(side=side0, padx=(0,7))
        brand_text = tk.Frame(brand, bg=c["BG"]); brand_text.pack(side=side0)
        tk.Label(brand_text, text="ALI AI", bg=c["BG"], fg=c["INK"], font=("Segoe UI Semibold", 15)).pack(anchor=anchor_start(root))
        tk.Label(brand_text, text=tr("app_subtitle", self.language), bg=c["BG"], fg=c["MUTED"], font=("Segoe UI", 8)).pack(anchor=anchor_start(root))
        self.model_lbl = tk.Label(h, text=tr("model", self.language)+" · loading", bg=c["SOFT"], fg=c["BLUE"], padx=9, pady=5, font=("Segoe UI Semibold", 8)); self.model_lbl.pack(side=side0, padx=8)
        self.workspace_lbl = tk.Label(h, text=Path(self.project_dir).name, bg=c["BG"], fg=c["MUTED"], font=("Segoe UI", 9)); self.workspace_lbl.pack(side=side0, padx=4)
        self.device_lbl = tk.Label(h, text="", bg=c["BG"], fg=c["MUTED"], font=("Segoe UI", 8)); self.device_lbl.pack(side=side0, padx=10)
        self.kca_lbl = tk.Label(h, text=f"KCA · {self.kca.get('functions', 0)}", bg=c["SOFT"], fg=c["BLUE"], font=("Segoe UI Semibold", 8), padx=8, pady=4); self.kca_lbl.pack(side=side0, padx=3)
        self.local_lbl = tk.Label(h, text=tr("offline", self.language), bg=c["SOFT"], fg=c["GREEN"], font=("Segoe UI Semibold", 8), padx=8, pady=4); self.local_lbl.pack(side=side0, padx=3)
        self.auto_lbl = tk.Label(h, text=tr("auto_learn", self.language)+" · ON", bg=c["SOFT"], fg=c["GREEN"], font=("Segoe UI Semibold", 8), padx=8, pady=4); self.auto_lbl.pack(side=side0, padx=3)
        self.hermes_lbl = tk.Label(h, text="HERMES · EXTERNAL", bg=c["SOFT"], fg=c["BLUE"], font=("Segoe UI Semibold", 8), padx=8, pady=4); self.hermes_lbl.pack(side=side0, padx=3)
        self._button(h, "AR / EN" if self.language == "ar" else "EN / AR", self.toggle_language, side=side1)
        self._button(h, tr("open_project", self.language), self._choose_dir, side=side1)
        self._button(h, tr("doctor", self.language), self.doctor_dialog, side=side1)
        self._button(h, tr("models", self.language), self.models_dialog, side=side1)
        self._button(h, "التعلّم من الأخطاء", self.learning_center_dialog, side=side1)
        self._button(h, tr("train", self.language), self.train_dialog, side=side1, accent=True)

    def _build_left(self):
        c=C; root=self.root; side0=start_side(root); anchor=anchor_start(root)
        # Navigation rail visually follows the supplied reference while reusing the existing business callbacks.
        nav=tk.Frame(self.left,bg=c["RAIL"],highlightbackground=c["LINE"],highlightthickness=1); nav.pack(fill="x",padx=0,pady=0)
        brand=tk.Frame(nav,bg=c["RAIL"]); brand.pack(fill="x",padx=12,pady=(10,6))
        tk.Label(brand,text="◈",bg=c["RAIL"],fg=c["BLUE"],font=("Segoe UI Semibold",18)).pack(side=side0,padx=(0,7))
        tk.Label(brand,text="ALI AI",bg=c["RAIL"],fg=c["INK"],font=("Segoe UI Semibold",12)).pack(side=side0)
        nav_items=(("◌",tr("new_chat",self.language),self._new_thread),("▦",tr("projects",self.language),self._choose_dir),("□",tr("files",self.language),self.knowledge_dialog),("◎",tr("memory",self.language),self.memory_dialog),("⚒",tr("tools",self.language),self.settings_dialog),("⌕",tr("web",self.language),self.settings_dialog),("◈",tr("models",self.language),self.models_dialog),("◫",tr("datasets",self.language),self.knowledge_dialog),("◉",tr("jobs",self.language),lambda:self.nb.select(self.jobs_tab)),("⚙",tr("settings",self.language),self.settings_dialog))
        for icon,label,cmd in nav_items:
            row=tk.Frame(nav,bg=c["RAIL"]); row.pack(fill="x",padx=6,pady=1)
            b=tk.Label(row,text=f"{icon}  {label}",bg=c["RAIL"],fg=c["INK"],font=("Segoe UI",9),cursor="hand2",padx=9,pady=6,anchor=anchor); b.pack(fill="x")
            b.bind("<Button-1>",lambda _e,fn=cmd:fn()); b.bind("<Enter>",lambda _e,w=b:w.configure(bg=c["RAIL_HOVER"])); b.bind("<Leave>",lambda _e,w=b:w.configure(bg=c["RAIL"]))
        conv=tk.Frame(self.left,bg=c["BG"]); conv.pack(fill="x")
        tk.Label(conv,text=tr("conversations",self.language).upper(),bg=c["BG"],fg=c["MUTED"],font=("Segoe UI Semibold",8)).pack(anchor=anchor,padx=14,pady=(10,6))
        top=tk.Frame(conv,bg=c["BG"]); top.pack(fill="x",padx=10)
        self._button(top,"+ "+tr("new_chat",self.language),self._new_thread,side=side0,accent=True); self._button(top,tr("refresh",self.language),self._refresh_threads,side=side0)
        self.thread_list=tk.Listbox(conv,bg=c["SOFT"],fg=c["INK"],selectbackground="#eaf0ff",selectforeground=c["INK"],relief="flat",bd=0,activestyle="none",height=7,font=("Segoe UI",9))
        self.thread_list.pack(fill="x",padx=10,pady=(4,8)); self.thread_list.bind("<<ListboxSelect>>",self._thread_selected); self.thread_ids=[]
        tk.Label(conv,text=tr("projects",self.language).upper(),bg=c["BG"],fg=c["MUTED"],font=("Segoe UI Semibold",8)).pack(anchor=anchor,padx=14,pady=(2,6))
        self.tree=ttk.Treeview(conv,show="tree",height=8); self.tree.pack(fill="x",padx=10); self.tree.bind("<Double-1>",self.open_selected_file)
        self.left_actions=tk.Frame(conv,bg=c["BG"]); self.left_actions.pack(fill="x",padx=9,pady=8)
        for label,command in ((tr("datasets",self.language),self.knowledge_dialog),(tr("training_files",self.language),self.accumulated_training_dialog),(tr("files",self.language),self.knowledge_dialog),(tr("memory",self.language),self.memory_dialog),("التعلّم من الأخطاء",self.learning_center_dialog),("KCA",self.settings_dialog),(tr("self_learn",self.language),self.self_learn_now)):
            self._button(self.left_actions,label,command,side=side0)

    def _build_center(self):
        c=C; root=self.root; side0=start_side(root); side1=end_side(root); anchor=anchor_start(root)
        top=tk.Frame(self.center,bg=c["BG"],height=54); top.pack(fill="x"); top.pack_propagate(False)
        self.title_lbl=tk.Label(top,text=tr("new_chat",self.language),bg=c["BG"],fg=c["INK"],font=("Segoe UI Semibold",12)); self.title_lbl.pack(side=side0,padx=14,pady=14)
        self.intent_lbl=tk.Label(top,text=tr("ready",self.language),bg=c["BG"],fg=c["MUTED"],font=("Segoe UI",8)); self.intent_lbl.pack(side=side0,padx=12)
        self.chat=ChatView(self.center); self.chat.pack(fill="both",expand=True,padx=8)
        composer=tk.Frame(self.center,bg=c["BG"],highlightbackground=c["LINE"],highlightthickness=1); composer.pack(fill="x",padx=8,pady=8)
        chips=tk.Frame(composer,bg=c["BG"]); chips.pack(fill="x",padx=8,pady=(7,3))
        for label,prompt in ((tr("analyze",self.language),"حلل المشروع وحدد أهم المشاكل وخطة الإصلاح."),(tr("inspect_model",self.language),"افحص النموذج والأوزان الحالية ومسار التحميل."),(tr("train_tokenizer",self.language),"تحقق من بيانات التدريب ثم أنشئ tokenizer version جديدة."),(tr("train",self.language),"شغّل تدريب ALI مع checkpointing وevaluation."),(tr("import_weights",self.language),"افحص الأوزان الموجودة وأخبرني أين يجب تثبيتها."),(tr("check_device",self.language),"افحص الجهاز وحدد إعداد التدريب الآمن.")):
            self._button(chips,label,lambda x=prompt:self._insert_prompt(x),side=side0)
        self.entry=tk.Text(composer,height=4,wrap="word",bg=c["EDITOR"],fg=c["INK"],insertbackground=c["INK"],selectbackground="#eaf0ff",relief="flat",bd=0,font=("Segoe UI",10),padx=12,pady=10); self.entry.tag_configure("__ali_direction",justify="right" if self.rtl else "left"); self.entry.pack(fill="x",padx=8,pady=5); self.entry.bind("<KeyRelease>",lambda _e:self.entry.tag_add("__ali_direction","1.0","end"),add="+"); self.entry.bind("<Return>",self._on_return)
        controls=tk.Frame(composer,bg=c["BG"]); controls.pack(fill="x",padx=8,pady=(0,7))
        tk.Label(controls,text=tr("professional",self.language),bg=c["BG"],fg=c["MUTED"]).pack(side=side0)
        ttk.Combobox(controls,textvariable=self.ai_mode,values=AI_MODES,state="readonly",width=12).pack(side=side0,padx=(4,10))
        tk.Label(controls,text="Temp",bg=c["BG"],fg=c["MUTED"]).pack(side=side0)
        tk.Scale(controls,from_=0,to=1,resolution=.05,orient="horizontal",variable=self.temp_var,length=90,bg=c["BG"],fg=c["MUTED"],highlightthickness=0,troughcolor=c["LINE"],bd=0).pack(side=side0)
        tk.Label(controls,text="Ctx",bg=c["BG"],fg=c["MUTED"]).pack(side=side0,padx=(8,2)); tk.Entry(controls,width=7,textvariable=self.ctx_var,bg=c["SOFT"],fg=c["INK"],insertbackground=c["INK"],relief="flat",justify="right" if self.rtl else "left").pack(side=side0)
        tk.Label(controls,text="Out",bg=c["BG"],fg=c["MUTED"]).pack(side=side0,padx=(8,2)); tk.Entry(controls,width=7,textvariable=self.out_var,bg=c["SOFT"],fg=c["INK"],insertbackground=c["INK"],relief="flat",justify="right" if self.rtl else "left").pack(side=side0)
        self.stop_btn=self._button(controls,tr("stop",self.language),self.stop_generation,side=side1); self.stop_btn.configure(state="disabled")
        self.send_btn=self._button(controls,tr("send",self.language)+"  ↵",self.send,side=side1,accent=True)

    def _build_right(self):
        # Right rail is intentionally stacked: developer surfaces at the top, live execution in the middle,
        # and the system-health/telemetry list at the bottom as requested.
        self.right_stack=tk.PanedWindow(self.right,orient="vertical",sashwidth=5,bd=0,bg=C["LINE"],relief="flat")
        self.right_stack.pack(fill="both",expand=True,padx=4,pady=4)
        self.dev_frame=tk.Frame(self.right_stack,bg=C["BG"])
        self.activity_frame=tk.Frame(self.right_stack,bg=C["BG"],height=250)
        self.health_footer=tk.Frame(self.right_stack,bg=C["SOFT"],height=235)
        try:
            self.right_stack.add(self.dev_frame,stretch="always",minsize=180)
            self.right_stack.add(self.activity_frame,stretch="always",minsize=190)
            self.right_stack.add(self.health_footer,stretch="never",minsize=190)
        except Exception:
            self.right_stack.add(self.dev_frame); self.right_stack.add(self.activity_frame); self.right_stack.add(self.health_footer)
        self.nb=ttk.Notebook(self.dev_frame); self.nb.pack(fill="both",expand=True,padx=2,pady=2)
        self.overview_tab=ttk.Frame(self.nb,style="Panel.TFrame"); self.editor_tab=ttk.Frame(self.nb,style="Panel.TFrame"); self.term_tab=ttk.Frame(self.nb,style="Panel.TFrame"); self.jobs_tab=ttk.Frame(self.nb,style="Panel.TFrame"); self.model_tab=ttk.Frame(self.nb,style="Panel.TFrame")
        for tab,key in ((self.overview_tab,"overview"),(self.editor_tab,"editor"),(self.term_tab,"terminal"),(self.jobs_tab,"jobs"),(self.model_tab,"models")): self.nb.add(tab,text=tr(key,self.language))
        self._build_overview(); self._build_editor(); self._build_terminal(); self._build_jobs(); self._build_model_panel()
        self.activity=ActivityCenter(self.activity_frame,self.rtl)
        self._build_health_footer()

    def _build_overview(self):
        wrap=tk.Frame(self.overview_tab,bg=C["BG"]); wrap.pack(fill="both",expand=True,padx=8,pady=8)
        head=tk.Frame(wrap,bg=C["BG"]); head.pack(fill="x",pady=(0,7))
        tk.Label(head,text=tr("system_health",self.language),bg=C["BG"],fg=C["INK"],font=("Segoe UI Semibold",12)).pack(side=start_side(self.root))
        tk.Label(head,text="● "+tr("connected",self.language),bg=C["SOFT"],fg=C["GREEN"],font=("Segoe UI Semibold",8),padx=8,pady=4).pack(side=end_side(self.root))
        metrics=tk.Frame(wrap,bg=C["BG"]); metrics.pack(fill="x",pady=(0,7))
        self._health_metric(metrics,"CPU","cpu_metric"); self._health_metric(metrics,"GPU","gpu_metric"); self._health_metric(metrics,"RAM","ram_metric"); self._health_metric(metrics,"TEMP","temp_metric")
        self._card(wrap,"ACTIVE MODEL","model_card"); self._card(wrap,"WORKFLOW","workflow_card"); self._card(wrap,"MEMORY / RAG","memory_card"); self._card(wrap,"DEVICE","device_card"); self._card(wrap,"KCA CONTROL PLANE","kca_card")
        self.kca_card.configure(text="KCA functions: "+str(self.kca.get("functions",0)))

    def _health_metric(self,parent,label,attr):
        card=tk.Frame(parent,bg=C["WHITE"],highlightbackground=C["LINE"],highlightthickness=1); card.pack(side=start_side(self.root),fill="x",expand=True,padx=2)
        tk.Label(card,text=label,bg=C["WHITE"],fg=C["MUTED"],font=("Segoe UI Semibold",7)).pack(anchor=anchor_start(self.root),padx=8,pady=(6,1))
        value=tk.Label(card,text="—",bg=C["WHITE"],fg=C["INK"],font=("Segoe UI Semibold",10)); value.pack(anchor=anchor_start(self.root),padx=8,pady=(0,6)); setattr(self,attr,value)

    def _card(self, parent, title, attr):
        shell = tk.Frame(parent, bg=C["PANEL_2"], highlightbackground=C["LINE"], highlightthickness=1)
        shell.pack(fill="x", pady=5)
        tk.Label(
            shell, text=title, bg=C["PANEL_2"], fg=C["MUTED"],
            font=("Segoe UI Semibold", 8)
        ).pack(anchor="w", padx=10, pady=(8, 2))
        value = tk.Label(
            shell, text="loading…", bg=C["PANEL_2"], fg=C["INK"],
            justify="left", anchor="w", wraplength=330,
            font=("Consolas", 8),
        )
        value.pack(fill="x", padx=10, pady=(1, 9))
        setattr(self, attr, value)

    def _build_editor(self):
        self.editor = LineNumberedEditor(self.editor_tab)
        self.editor.pack(fill="both", expand=True, padx=6, pady=6)
        self.editor_path: Path | None = None

        bar = tk.Frame(self.editor_tab, bg=C["PANEL"])
        bar.pack(fill="x")
        self._button(bar, "Save", self.save_editor, side="left", accent=True)
        self._button(bar, "Revert", self.revert_editor, side="left")
        self._button(bar, "Open", self._choose_editor_file, side="left")
        self._button(bar, "Run tests", self.run_tests, side="left")

    def _build_terminal(self):
        self.term = tk.Text(
            self.term_tab, bg=C["EDITOR"], fg=C["INK"],
            insertbackground=C["INK"], font=("Consolas", 9),
            relief="flat", bd=0,
        )
        self.term.pack(fill="both", expand=True, padx=6, pady=6)

        row = tk.Frame(self.term_tab, bg=C["PANEL"])
        row.pack(fill="x")
        self.term_entry = tk.Entry(
            row, bg=C["PANEL_2"], fg=C["INK"], insertbackground=C["INK"], relief="flat"
        )
        self.term_entry.pack(side="left", fill="x", expand=True, padx=6, pady=6)
        self.term_entry.bind("<Return>", lambda _e: self.run_terminal())
        self._button(row, "Run", self.run_terminal, side="right", accent=True)

    def _build_jobs(self):
        self.jobs_list = tk.Listbox(
            self.jobs_tab, bg=C["EDITOR"], fg=C["INK"],
            selectbackground=C["LINE"], relief="flat", bd=0,
            font=("Consolas", 8),
        )
        self.jobs_list.pack(fill="both", expand=True, padx=6, pady=6)

    def _build_model_panel(self):
        self.model_list = tk.Listbox(
            self.model_tab, bg=C["EDITOR"], fg=C["INK"],
            selectbackground=C["LINE"], relief="flat", bd=0,
            font=("Consolas", 8),
        )
        self.model_list.pack(fill="both", expand=True, padx=6, pady=6)

        bar = tk.Frame(self.model_tab, bg=C["PANEL"])
        bar.pack(fill="x", padx=6, pady=6)
        self._button(bar, "Import file", self.import_weights, side="left", accent=True)
        self._button(bar, "Import folder", self.import_weights_folder, side="left")
        self._button(bar, "Verify", self.verify_selected_model, side="left")
        self._button(bar, "Promote", self.promote_selected_model, side="left")
        self._button(bar, "GGUF", self.export_gguf, side="left")
        self._button(bar, "Refresh", self._refresh_models, side="right")

    def _build_health_footer(self):
        side0=start_side(self.root); anchor=anchor_start(self.root)
        head=tk.Frame(self.health_footer,bg=C["SOFT"]); head.pack(fill="x",padx=8,pady=(7,4))
        tk.Label(head,text=tr("system_health",self.language),bg=C["SOFT"],fg=C["INK"],font=("Segoe UI Semibold",10)).pack(side=side0)
        self.health_state=tk.Label(head,text="● "+tr("connected",self.language),bg=C["SOFT"],fg=C["GREEN"],font=("Segoe UI Semibold",8)); self.health_state.pack(side=end_side(self.root))
        grid=tk.Frame(self.health_footer,bg=C["SOFT"]); grid.pack(fill="x",padx=8,pady=2)
        self.rh_cpu=self._health_tile(grid,"CPU"); self.rh_gpu=self._health_tile(grid,"GPU"); self.rh_ram=self._health_tile(grid,"RAM"); self.rh_temp=self._health_tile(grid,"TEMP")
        cards=tk.Frame(self.health_footer,bg=C["SOFT"]); cards.pack(fill="x",padx=8,pady=4)
        self.rh_model=self._health_line(cards,"MODEL"); self.rh_task=self._health_line(cards,"TASK"); self.rh_context=self._health_line(cards,"CONTEXT")
        self.rh_hermes=self._health_line(cards,"HERMES")
    def _health_tile(self,parent,label):
        f=tk.Frame(parent,bg=C["WHITE"],highlightbackground=C["LINE"],highlightthickness=1); f.pack(side="left",fill="x",expand=True,padx=2)
        tk.Label(f,text=label,bg=C["WHITE"],fg=C["MUTED"],font=("Segoe UI Semibold",7)).pack(anchor="w",padx=6,pady=(3,0)); v=tk.Label(f,text="—",bg=C["WHITE"],fg=C["INK"],font=("Segoe UI Semibold",9)); v.pack(anchor="w",padx=6,pady=(0,4)); return v
    def _health_line(self,parent,label):
        f=tk.Frame(parent,bg=C["WHITE"],highlightbackground=C["LINE"],highlightthickness=1); f.pack(fill="x",pady=2)
        tk.Label(f,text=label,bg=C["WHITE"],fg=C["MUTED"],font=("Segoe UI Semibold",7)).pack(side=start_side(self.root),padx=6,pady=3); v=tk.Label(f,text="—",bg=C["WHITE"],fg=C["INK"],font=("Consolas",7),anchor=anchor_start(self.root),justify="left"); v.pack(side=end_side(self.root),fill="x",expand=True,padx=6,pady=3); return v

    def _build_status(self):
        s=tk.Frame(self.root,bg=C["BG"],height=28,highlightbackground=C["LINE"],highlightthickness=1); s.pack(fill="x"); s.pack_propagate(False)
        side0=start_side(self.root); side1=end_side(self.root)
        self.status=tk.Label(s,text=tr("ready",self.language),bg=C["BG"],fg=C["MUTED"],font=("Segoe UI",8)); self.status.pack(side=side0,padx=10)
        self.perm_lbl=tk.Label(s,text="Permission: "+self.runtime.permission_manager.mode,bg=C["BG"],fg=C["AMBER"],font=("Segoe UI",8)); self.perm_lbl.pack(side=side1,padx=10)

    def _button(self, parent, text, command, *, side=None, accent=False):
        b=tk.Button(parent,text=text,command=command,bg=C["BLUE"] if accent else C["SOFT"],fg=C["WHITE"] if accent else C["INK"],activebackground="#eaf0ff",activeforeground=C["INK"],relief="flat",bd=0,cursor="hand2",font=("Segoe UI Semibold",8),padx=10,pady=6)
        b.pack(side=side or start_side(self.root),padx=3,pady=3)
        return b

    def _ensure_model_services(self):
        """Load heavy model/artifact services only when they are actually needed."""
        if self.model_manager is None or self.weights is None or self.pipeline is None:
            from model.manager import ModelManager
            from model.weights_manager import WeightsManager
            from training.pipeline import TrainingPipeline
            self.model_manager = ModelManager(ROOT, self.registry)
            self.weights = WeightsManager(ROOT, self.registry)
            self.pipeline = TrainingPipeline(ROOT, self.hardware)
        return self.model_manager, self.weights, self.pipeline

    def _ensure_active_model_loaded(self):
        manager, _weights, _pipeline = self._ensure_model_services()
        active = self.registry.active("ALI")
        if not active:
            return False
        current = getattr(manager, "current", None) or {}
        if current.get("version") == active.get("version") and self.runtime.model_engine is not None:
            return True
        try:
            engine, _ = manager.load(active)
            self.runtime.model_engine = engine
            self.model_lbl.configure(text=f"MODEL · {active['version']}")
            return True
        except Exception as exc:
            self.runtime.model_engine = None
            self._append_system(f"Model load unavailable: {exc}", meta="model-error")
            return False

    # ---------- autonomous learning ----------
    def _self_learning_running(self) -> bool:
        return any(
            j.get("kind") == "self-learning" and j.get("status") in {"queued", "running"}
            for j in self.jobs.snapshot()
        )

    def self_learn_now(self):
        if self._self_learning_running():
            self.status.configure(text="Self-learning job is already running")
            return
        db=ROOT / "artifacts" / "harvest.sqlite3"
        conv_db=ROOT / "runtime_conversations.sqlite3"
        steps=int(self.cfg.get("training",{}).get("auto_learning_steps", 1))
        scale=str(self.cfg.get("training",{}).get("auto_learning_scale", "micro"))
        device=str(self.train_profile.get("device", "cpu"))
        def work(progress):
            result=self.self_manager.autonomous_cycle(
                db, conv_db,
                scale=scale, steps=max(1,steps), device=device,
                progress=progress,
            )
            self.root.after(0, self._load_active)
            self.root.after(0, self._refresh_models)
            return result
        self.jobs.run("ALI Auto Self-Learning", work, "self-learning")
        self.status.configure(text="Self-learning cycle queued")
        self.auto_lbl.configure(text="AUTO LEARN · RUNNING")

    def _auto_improvement_tick(self):
        try:
            enabled=bool(self.cfg.get("auto_improve", self.cfg.get("agent",{}).get("auto_learning", True)))
            db=ROOT / "artifacts" / "harvest.sqlite3"
            conv_db=ROOT / "runtime_conversations.sqlite3"
            st=self.self_manager.status(db,conv_db)
            if not enabled:
                self.auto_lbl.configure(text="AUTO LEARN · OFF", fg=C["MUTED"])
            elif self._self_learning_running():
                self.auto_lbl.configure(text=f"AUTO LEARN · {st.get('new_samples',0)} NEW", fg=C["AMBER"])
            elif st.get("ready"):
                self.auto_lbl.configure(text=f"AUTO LEARN · STARTING ({st['new_samples']})", fg=C["GREEN"])
                self.self_learn_now()
            else:
                self.auto_lbl.configure(text=f"AUTO LEARN · {st.get('new_samples',0)}/{self.self_manager.min_new_samples}", fg=C["GREEN"])
        except Exception as exc:
            try:
                self.auto_lbl.configure(text="AUTO LEARN · ERROR", fg=C["RED"])
                self.status.configure(text=f"Auto-learning check failed: {exc}")
            except Exception:
                pass
        finally:
            try:self.root.after(60000, self._auto_improvement_tick)
            except Exception:pass

    # ---------- refresh ----------
    def _refresh_all(self):
        self.populate_tree()
        self._refresh_threads()
        self._refresh_models()
        self._refresh_status()
        self._load_active()

    def _refresh_status(self):
        snap = self.resources.snapshot()
        self.status.configure(
            text=f"CPU {snap.get('cpu_percent', '?')}%  ·  "
                 f"RAM free {snap.get('ram_available_gb', '?')} GB  ·  "
                 f"Disk {snap.get('disk_free_gb', '?')} GB"
        )
        self.perm_lbl.configure(
            text="Permission: " + self.runtime.permission_manager.mode
        )

    def _refresh_hardware_loop(self):
        try:
            self.hardware = detect(probe_torch=False)
            self.policy = choose_policy(self.hardware)
            self.train_profile = training_profile(self.hardware)
            self.device_profile = recommend_for_hardware(self.hardware)
            badge = "P50 SAFE" if self.device_profile.get("id", "").startswith("thinkpad-p50") else "ADAPTIVE"
            self.device_lbl.configure(text=f"{badge} · {self.hardware.cpu_cores}T · {self.hardware.ram_gb:.1f} GB")
            if hasattr(self, "cpu_metric"):
                self.cpu_metric.configure(text=f"{getattr(self.hardware,'cpu_percent',0) or 0:.0f}%")
                self.gpu_metric.configure(text=f"{getattr(self.hardware,'gpu_percent',0) or 0:.0f}%")
                self.ram_metric.configure(text=f"{getattr(self.hardware,'ram_used_percent',0) or 0:.0f}%")
                self.temp_metric.configure(text=f"{getattr(self.hardware,'temperature_c',0) or 0:.1f}°C")
            if hasattr(self, "rh_cpu"):
                self.rh_cpu.configure(text=f"{getattr(self.hardware,'cpu_percent',0) or 0:.0f}%")
                self.rh_gpu.configure(text=f"{getattr(self.hardware,'gpu_percent',0) or 0:.0f}%")
                self.rh_ram.configure(text=f"{getattr(self.hardware,'ram_used_percent',0) or 0:.0f}%")
                self.rh_temp.configure(text=f"{getattr(self.hardware,'temperature_c',0) or 0:.1f}°C")
            self.device_card.configure(
                text=json.dumps(
                    {"hardware": self.hardware.to_dict(), "policy": self.policy},
                    ensure_ascii=False, indent=2,
                )
            )
            self._refresh_status()
        finally:
            self.root.after(4000, self._refresh_hardware_loop)

    def _refresh_jobs_loop(self):
        try:
            self.jobs_list.delete(0, "end")
            for job in self.jobs.snapshot()[-50:]:
                self.jobs_list.insert(
                    "end",
                    f"{job['status']:<11} {job['progress'] * 100:5.1f}%  "
                    f"{job['name']} [{job['id'][:8]}]",
                )
            jobs=self.jobs.snapshot()
            self.workflow_card.configure(text="\n".join(f"{j['status']}: {j['name']}" for j in jobs[-8:]) or "No background jobs.")
            if hasattr(self, "activity"):
                running=next((j for j in reversed(jobs) if j.get('status') in {'queued','running'}), None)
                chosen=running or (jobs[-1] if jobs else None)
                if chosen: self.activity.update_job(chosen); self.rh_task.configure(text=f"{chosen.get('name','')} · {chosen.get('progress',0)*100:.0f}%")
                else: self.rh_task.configure(text="Ready")
                self.rh_model.configure(text=self.model_lbl.cget('text'))
                try:
                    hs=self.hermes_router.status(); self.rh_hermes.configure(text=("connected · RO" if hs.get("exists") else "external · not found")[:42])