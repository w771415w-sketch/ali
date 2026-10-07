# -*- coding: utf-8 -*-
from v6_router import frame, update_state


def test_continue_binds_to_state():
    f = frame("كمل من حيث توقفنا", {"active_goal":"project_build"})
    assert f.continuation is True
    s = update_state({"active_goal":"project_build","stage":"execute"}, f)
    assert s["active_goal"] == "project_build"


def test_risky_action_requests_confirmation():
    f = frame("احذف الملفات القديمة وارفع الإصدار")
    assert f.risk_level == "external_side_effect"
    assert f.confirmation_required is True


def test_correction_is_recovery():
    f = frame("هذا خطأ، صحح النتيجة")
    assert f.correction is True
    s = update_state({"active_goal":"debugging","stage":"execute"}, f)
    assert s["stage"] == "recover"


def test_research_requires_evidence():
    f = frame("ابحث عن آخر إصدار واذكر المصادر")
    assert f.freshness_required is True
    assert f.evidence_required is True
    assert "web" in f.required_tools


def test_mixed_language_and_format():
    f = frame("اشرح RAG بالعربي وأخرج النتيجة بصيغة JSON")
    assert f.language == "mixed"
    assert f.output_format == "json"


if __name__ == "__main__":
    tests=[
        test_continue_binds_to_state,
        test_risky_action_requests_confirmation,
        test_correction_is_recovery,
        test_research_requires_evidence,
        test_mixed_language_and_format,
    ]
    for t in tests: t()
    print("V6 router tests passed")

def test_high_risk_database_confirmation():
    f = frame("احذف قاعدة البيانات بالكامل")
    assert f.confirmation_required is True
    assert f.risk_level in {"high","external_side_effect"}


def test_multi_intent_and_final_verification_signals():
    f = frame("عدّل المشروع ثم اختبره ثم تحقق من النتيجة")
    assert f.multi_intent is True
    assert f.required_tools


def test_context_reference_needs_state():
    f = frame("عدّل هذا المشروع السابق")
    assert f.references
    assert f.ambiguity_level in {"high","dangerous","none","medium"}
