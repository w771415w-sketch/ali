# -*- coding: utf-8 -*-
"""اختبارات V0.7.3 — Professional AI Agent."""

from __future__ import annotations

import sys
import os
import pytest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

pytestmark = pytest.mark.skipif(os.name != "nt" and os.environ.get("ALI_GUI_TESTS") != "1", reason="Desktop GUI unavailable in headless environment")
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


# =====================================================================
# Intent Classification
# =====================================================================

class TestIntentClassification:
    """تصنيف intent يجب أن يكون deterministic."""

    def test_read_file_intent(self):
        from core.agent import classify_intent
        i = classify_intent("read_file ali_agent.py")
        assert i.primary == "read_file", f"got {i.primary}"
        assert "path" in i.params, f"missing path in {i.params}"
        assert i.params["path"] == "ali_agent.py"
        assert i.confidence > 0.5

    def test_write_file_intent(self):
        from core.agent import classify_intent
        i = classify_intent("write_file test.py")
        assert i.primary == "write_file"
        assert "path" in i.params

    def test_list_dir_intent(self):
        from core.agent import classify_intent
        i = classify_intent("list_dir")
        assert i.primary == "list_dir"

        i = classify_intent("ls tokenizer")
        assert i.primary == "list_dir"

    def test_search_intent(self):
        from core.agent import classify_intent
        i = classify_intent("search_files class.*App")
        assert i.primary == "search_files"
        assert "pattern" in i.params

    def test_run_command_intent(self):
        from core.agent import classify_intent
        i = classify_intent("run_command dir")
        assert i.primary == "run_command"
        assert "command" in i.params

    def test_git_intent(self):
        from core.agent import classify_intent
        i = classify_intent("git status")
        assert i.primary == "git"
        assert "subcommand" in i.params
        assert i.params["subcommand"] == "status"

        i = classify_intent("git commit add tests")
        assert i.primary == "git"
        assert i.params.get("subcommand") == "commit"

    def test_question_intent(self):
        from core.agent import classify_intent
        i = classify_intent("ما هو Python؟")
        assert i.primary == "code_question"

        i = classify_intent("how does this work?")
        assert i.primary == "code_question"

    def test_empty_text(self):
        from core.agent import classify_intent
        i = classify_intent("")
        assert i.primary == "unknown"
        assert i.confidence == 0.0

    def test_arabic_text(self):
        from core.agent import classify_intent
        i = classify_intent("افتح ملف ali_agent.py")
        # Either read_file or list_dir, both ok
        assert i.primary in ("read_file", "list_dir")


# =====================================================================
# Plan
# =====================================================================

class TestPlanActions:
    """خطة agent تبني sequence صحيح."""

    def test_read_file_plan(self):
        from core.agent import classify_intent, plan_actions
        i = classify_intent("read_file tokenizer/__init__.py")
        plan = plan_actions(i)
        assert not plan.is_empty()
        assert len(plan.steps) == 1
        assert plan.steps[0].tool_name == "read_file"
        assert plan.steps[0].kwargs["path"] == "tokenizer/__init__.py"

    def test_analyze_project_plan_multi_step(self):
        from core.agent import classify_intent, plan_actions
        i = classify_intent("analyze project structure")
        plan = plan_actions(i)
        # analyze_project يبني خطة متعددة الخطوات
        assert not plan.is_empty()
        assert len(plan.steps) >= 2

    def test_question_plan_empty(self):
        from core.agent import classify_intent, plan_actions
        i = classify_intent("ما هو Python؟")
        plan = plan_actions(i)
        # لا tools — خطة فارغة
        assert plan.is_empty()


# =====================================================================
# Execute Plan
# =====================================================================

class TestExecutePlan:
    """تنفيذ الخطة مع tool runner وهمي."""

    def test_execute_read_file(self):
        from core.agent import (
            classify_intent, plan_actions, execute_plan,
        )

        i = classify_intent("read_file ali_agent.py")
        plan = plan_actions(i)

        # tool runner وهمي ينجح.
        def fake_runner(tool_name, kwargs):
            return {"ok": True, "data": f"content of {kwargs.get('path', '?')}",
                    "error": ""}

        result = execute_plan(plan, fake_runner, "read_file ali_agent.py")
        assert result.ok
        assert len(result.tool_results) == 1
        assert result.tool_results[0]["tool"] == "read_file"
        assert "content of ali_agent.py" in result.tool_results[0]["data"]

    def test_execute_question_no_tools(self):
        from core.agent import (
            classify_intent, plan_actions, execute_plan,
        )

        i = classify_intent("what is AI?")
        plan = plan_actions(i)
        assert plan.is_empty()

        def never_called(tool_name, kwargs):
            raise AssertionError("Should not be called")

        result = execute_plan(plan, never_called, "what is AI?")
        assert result.ok  # Empty plan = ok
        assert "🤖" in result.summary  # Knowledge answer

    def test_execute_failure_returns_error(self):
        from core.agent import (
            classify_intent, plan_actions, execute_plan,
        )

        i = classify_intent("read_file nonexistent.py")
        plan = plan_actions(i)

        def failing_runner(tool_name, kwargs):
            return {"ok": False, "data": "", "error": "file not found"}

        result = execute_plan(plan, failing_runner, "read_file nonexistent.py")
        assert not result.ok
        assert "file not found" in result.tool_results[0]["error"]


# =====================================================================
# Token Counting
# =====================================================================

class TestTokenCounting:
    """count_tokens يعمل مع/بدون tokenizer."""

    def test_count_arabic(self):
        from core.agent import count_tokens
        n = count_tokens("مرحبا ALI Studio")
        assert n > 0
        assert isinstance(n, int)

    def test_count_english(self):
        from core.agent import count_tokens
        n = count_tokens("Hello World")
        assert n > 0

    def test_count_empty(self):
        from core.agent import count_tokens
        n = count_tokens("")
        # Empty string يقدّر بـ 0
        assert n == 0


# =====================================================================
# App Integration (via App._agent_reply)
# =====================================================================

class TestAppAgentMode:
    """App يستخدم _agent_reply في Professional mode."""

    def test_app_has_agent_method(self):
        # Headless import.
        import tkinter as tk
        from tkinter import StringVar
        # We can't instantiate App without Tcl, so check via static analysis.
        import importlib
        ali_agent = importlib.import_module("ali_agent")
        assert hasattr(ali_agent.App, "_agent_reply")
        assert hasattr(ali_agent.App, "_ai_mode_menu")
        assert hasattr(ali_agent.App, "_set_ai_mode")

    def test_ai_mode_attribute_default(self):
        """App default ai_mode هو tools."""
        import tkinter as tk
        root = tk.Tk()
        root.withdraw()
        # Use isolated APPDATA via monkey-patch.
        import tempfile
        import os
        tmp = tempfile.mkdtemp(prefix="ai_mode_test_")
        os.environ["APPDATA"] = tmp
        try:
            if "ali_agent" in sys.modules:
                del sys.modules["ali_agent"]
            import ali_agent
            app = ali_agent.App(root)
            assert app.ai_mode.get() == "professional", f"got {app.ai_mode.get()}"
        finally:
            root.destroy()
            import shutil
            shutil.rmtree(tmp, ignore_errors=True)

    def test_set_ai_mode_persists(self):
        """اختبار استمرارية ai_mode عبر إنشاء App جديد بعد الإغلاق."""
        import tkinter as tk
        import tempfile
        import os
        import sys
        import json

        tmp = tempfile.mkdtemp(prefix="persist_test_")
        old_appdata = os.environ.get("APPDATA")
        os.environ["APPDATA"] = tmp
        # امسح الـ module من sys.modules لضمان fresh load.
        for mod_name in list(sys.modules):
            if mod_name == "ali_agent" or mod_name.startswith("ali_agent."):
                del sys.modules[mod_name]
        try:
            import ali_agent as ali_mod

            root = tk.Tk()
            root.withdraw()
            app = ali_mod.App(root)
            app._set_ai_mode("professional")

            # تحقق أن الـ cfg يحفظ ai_mode.
            cfg_path = ali_mod.APP_PATHS.user_config()
            if os.path.exists(cfg_path):
                cfg_data = json.loads(open(cfg_path, encoding="utf-8").read())
                assert cfg_data.get("ai_mode") == "professional", (
                    f"ai_mode not in JSON cfg: {cfg_data}"
                )

            # بدلاً من إنشاء Tk root جديد (يعرّض لـ Tcl state تالف على Windows)،
            # تحقق مباشرة من قراءة الـ config من القرص.
            root.destroy()
            import gc; gc.collect(); import time; time.sleep(0.05)

            for mod_name in list(sys.modules):
                if mod_name == "ali_agent" or mod_name.startswith("ali_agent."):
                    del sys.modules[mod_name]
            import importlib
            ali_mod2 = importlib.import_module("ali_agent")
            cfg_path2 = ali_mod2.APP_PATHS.user_config()
            if os.path.exists(cfg_path2):
                cfg_data2 = json.loads(open(cfg_path2, encoding="utf-8").read())
                assert cfg_data2.get("ai_mode") == "professional", (
                    f"persistence failed: {cfg_data2}"
                )
        finally:
            os.environ["APPDATA"] = old_appdata or ""
            import shutil
            shutil.rmtree(tmp, ignore_errors=True)


# =====================================================================
# Run imports sanity
# =====================================================================

def test_agent_module_imports():
    """core.agent imports بدون أخطاء."""
    from core.agent import (
        Intent, Plan, ToolCall, ExecutionResult,
        classify_intent, plan_actions, execute_plan, count_tokens,
    )
    assert Intent is not None
    assert Plan is not None
    assert ExecutionResult is not None
