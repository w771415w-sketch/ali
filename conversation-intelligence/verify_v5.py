# -*- coding: utf-8 -*-
"""Zero-dependency smoke verification for Conversation Intelligence V5."""
from pathlib import Path
import importlib.util

HERE = Path(__file__).resolve().parent
source = HERE / "v5_router.py"
spec = importlib.util.spec_from_file_location("ali_ci_v5", source)
mod = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(mod)

cases = [
    ("أكمل من حيث توقفنا", "follow_up"),
    ("ابحث عبر الإنترنت عن آخر إصدار", "web_research"),
    ("النتيجة غير صحيحة صححها", "correction"),
    ("حلل المشروع ثم عدل الأخطاء ثم اختبر ثم ارفع", "multi_step_task"),
]

for text, expected in cases:
    frame = mod.classify(text, previous_intent="project_analysis")
    assert frame.intent == expected, (text, frame.to_dict())

danger = mod.classify("احذف الملف")
assert danger.high_risk
assert mod.needs_clarification(danger)

mixed = mod.classify("راجع هذا Python code بالتفصيل")
assert mixed.language == "mixed"
assert mixed.domain == "software"
assert mixed.requested_depth == "detailed"

policy = mod.build_response_policy(mixed)
assert policy["avoid_hidden_reasoning"] is True

print("Conversation Intelligence V5 verification: PASS")
