# -*- coding: utf-8 -*-
"""اختبار أن ali_agent.py لا يحتوي على Lovable."""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def test_no_lovable_in_agent():
    """التأكد من أن ali_agent.py لا يحتوي على أي كود يتصل بـ Lovable.

    ملاحظة: يُسمح بذكر Lovable في التعليقات والـ docstrings لتوثيق الإزالة.
    """
    import re
    p = ROOT / "ali_agent.py"
    text = p.read_text(encoding="utf-8")
    # إزالة كل التعليقات و docstrings قبل الفحص
    no_doc = re.sub(r'""".*?"""', '', text, flags=re.S)
    no_doc = re.sub(r"'''.*?'''", '', no_doc, flags=re.S)
    no_doc = re.sub(r'#.*', '', no_doc)
    code_only = no_doc.lower()
    assert "lovable" not in code_only, "Lovable found in code (not docstring)"
    assert "genius-connect" not in code_only
    assert "DEFAULT_SITE" not in code_only
    assert "_connect_loop" not in code_only
    assert "_handle_remote" not in code_only
    assert "urllib" not in code_only
    # فحص token كمعرّف أو قيمة، ليس كلمة عربية
    assert not re.search(r'\btoken\s*[:=]\s*["\']', code_only), "hardcoded token found"


def test_no_token_leak_in_default_config():
    from config.paths import APP_PATHS
    cfg = APP_PATHS.default_config()
    assert "token" not in cfg
    assert "site" not in cfg


def test_legacy_kept_for_reference():
    """ملف .legacy يجب أن يبقى للمراجعة لكنه ليس نقطة الدخول."""
    legacy = ROOT / "ali_agent.py.legacy"
    assert legacy.exists(), "legacy file missing"
    # نقطة الدخول يجب أن تكون ali_agent.py
    main = (ROOT / "ali_agent.py").read_text(encoding="utf-8")
    assert "__main__" in main
    assert 'if __name__ == "__main__"' in main
