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
