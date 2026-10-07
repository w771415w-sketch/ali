from __future__ import annotations

from pathlib import Path

import core.runtime as runtime_module
from core.runtime import ALIRuntime
from core.response_guard import stream_safe
from research.web import should_search_web, source_footer


def test_web_intent_detection():
    assert should_search_web("ابحث عبر الإنترنت عن آخر أخبار Python")[0]
    assert should_search_web("ما هو أحدث إصدار من Python؟")[0]
    assert not should_search_web("ابحث في الملفات عن runtime.py")[0]


def test_source_footer_stays_inside_answer():
    web = {"documents": [{"title": "Official", "url": "https://example.com", "text": "Evidence"}]}
    footer = source_footer(web, language="ar")
    assert "المصادر:" in footer
    assert "https://example.com" in footer


def test_stream_guard_blocks_corrupted_repetition():
    assert not stream_safe("svgsvgsvgsvgsvg svgsvgsvg ent ent ent ent ent ent")
    assert stream_safe("هذه إجابة عربية سليمة ومختصرة.", "ما هو الذكاء الاصطناعي؟")


def test_web_answer_is_inline_when_model_missing(tmp_path: Path, monkeypatch):
    docs = {
        "query": "أحدث المعلومات",
        "results": [],
        "documents": [
            {"title": "مصدر موثوق", "url": "https://example.com/article", "text": "هذه معلومات حديثة من المصدر."}
        ],
    }
    monkeypatch.setattr(runtime_module, "web_research", lambda *a, **k: docs)
    monkeypatch.setattr(runtime_module, "should_search_web", lambda *a, **k: (True, "explicit_web_request"))
    rt = ALIRuntime(tmp_path, tmp_path / "runtime.sqlite3", model_engine=None, allow_internet=True)
    result = rt.answer([{"role": "user", "content": "ابحث عبر الإنترنت عن أحدث المعلومات"}], tmp_path)
    assert result["mode"] == "web_fallback"
    assert "المصادر:" in result["text"]
    assert "https://example.com/article" in result["text"]
