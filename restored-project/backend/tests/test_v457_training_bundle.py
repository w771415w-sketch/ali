from __future__ import annotations

from pathlib import Path

from core.runtime import ALIRuntime
from knowledge.store import KnowledgeStore
from training.continuous_learning import ContinuousLearningManager


BUNDLE = """# ALI bundle
## إحصائيات الحزمة
- إجمالي المحادثات: **3**
- Train: **2**
- Validation: **1**
- Test: **0**

## المحادثة 1 — user_understanding
> النوع: `user_understanding` · المجموعة: `train`
**User:** ما هو NLU؟
**Assistant:** NLU هو فهم اللغة الطبيعية واستخراج المعنى والنية من نص المستخدم.

## المحادثة 2 — user_understanding
> النوع: `user_understanding` · المجموعة: `train`
**User:** ما هو RAG؟
**Assistant:** RAG يسترجع معلومات من مصادر خارجية أو محلية ثم يستخدمها لتوليد إجابة grounded.

## المحادثة 3 — user_understanding
> النوع: `user_understanding` · المجموعة: `validation`
**User:** كيف يتعامل AI مع الغموض؟
**Assistant:** يطلب التوضيح عندما لا تكفي الأدلة بدلاً من التخمين.

## المحادثة 4 — user_understanding
> النوع: `user_understanding` · المجموعة: `test`
**User:** ما هو NLU؟
**Assistant:** NLU هو فهم اللغة الطبيعية واستخراج المعنى والنية من نص المستخدم.
"""


def test_v457_bundle_import_deduplicates_and_reports_metadata_mismatch(tmp_path: Path):
    src = tmp_path / "bundle.md"
    src.write_text(BUNDLE, encoding="utf-8")
    manager = ContinuousLearningManager(tmp_path)
    result = manager.import_files([src])[0]
    assert result["ok"] is True
    assert result["status"] == "validated"
    assert result["sample_count"] == 3
    assert "declared_conversation_count_mismatch:3!=4" in result["warnings"]
    assert "duplicate_samples_in_file:1" in result["warnings"]
    assert manager.status()["pending_sources"] == 1

    store = KnowledgeStore(tmp_path / "runtime_knowledge.sqlite3")
    hit = store.training_qa_match("ما هو RAG؟")
    assert hit is not None
    assert hit["score"] == 1.0
    assert "يسترجع معلومات" in hit["answer"]


def test_v457_runtime_answers_imported_questions_before_model(tmp_path: Path):
    src = tmp_path / "bundle.md"
    src.write_text(BUNDLE, encoding="utf-8")
    manager = ContinuousLearningManager(tmp_path)
    manager.import_files([src])
    runtime = ALIRuntime(tmp_path, tmp_path / "runtime.sqlite3", model_engine=None, allow_internet=False)
    result = runtime.answer([{"role": "user", "content": "ما هو NLU؟"}], tmp_path)
    assert result["mode"] == "training_qa"
    assert result["confidence"] == 1.0
    assert "فهم اللغة الطبيعية" in result["text"]

    stream = list(runtime.stream_answer([{"role": "user", "content": "ما هو RAG؟"}], tmp_path))
    assert stream[-1]["type"] == "final"
    assert stream[-1]["mode"] == "training_qa"
    assert "يسترجع معلومات" in stream[-1]["text"]
