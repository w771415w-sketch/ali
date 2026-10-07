# -*- coding: utf-8 -*-
from pathlib import Path
import importlib.util
import sys

P = Path(__file__).with_name("v5_router.py")

spec = importlib.util.spec_from_file_location("ali_ci_v5", P)
mod = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = mod
spec.loader.exec_module(mod)


def test_arabic_continuation():
    f = mod.classify("أكمل من حيث توقفنا", previous_intent="project_analysis")
    assert f.intent == "follow_up"
    assert f.continuation
    assert f.mode == "continue"


def test_research_is_freshness_aware():
    f = mod.classify("ابحث عبر الإنترنت عن آخر إصدار")
    assert f.intent == "web_research"
    assert f.freshness_required
    assert f.mode == "research"


def test_high_risk_short_request_needs_guard():
    f = mod.classify("احذف الملف")
    assert f.high_risk
    assert mod.needs_clarification(f)


def test_multistep_is_orchestrated():
    f = mod.classify("حلل المشروع ثم عدل الأخطاء ثم اختبر ثم ارفع النتيجة")
    assert f.intent == "multi_step_task"
    assert f.mode == "orchestrate"


def test_correction_becomes_recovery():
    f = mod.classify("النتيجة غير صحيحة صححها")
    assert f.correction
    assert f.intent == "correction"
    assert f.mode == "recover"


def test_mixed_language():
    f = mod.classify("راجع هذا Python code بالتفصيل")
    assert f.language == "mixed"
    assert f.domain == "software"
    assert f.requested_depth == "detailed"


def test_response_policy_is_user_safe():
    f = mod.classify("قارن بين الخيارين")
    p = mod.build_response_policy(f)
    assert p["avoid_hidden_reasoning"] is True
    assert "deliverable" in p
