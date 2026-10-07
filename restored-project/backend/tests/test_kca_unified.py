# -*- coding: utf-8 -*-
from __future__ import annotations
from pathlib import Path
import json

from control_plane import KCARequestRouter, RequestEnvelope, summary
from control_plane.kca_registry import FUNCTIONS
from control_plane.state_store import KCAStateStore
from data_engine.kca_dataset import enrich_conversation, build_kca_dataset


def test_kca_registry_has_exactly_100_functions():
    assert len(FUNCTIONS) == 100
    assert summary()["functions"] == 100


def test_kca_router_produces_structured_state():
    state = KCARequestRouter().build_state(RequestEnvelope(raw_text="اقرأ ملف ali_agent.py"))
    assert state.intent == "read_file"
    assert state.confidence > .9
    assert state.task_state["params"]["path"] == "ali_agent.py"
    assert state.selected_action is not None


def test_kca_dataset_enrichment_is_deterministic_and_redacts_secret():
    row = {
        "id": "demo-1",
        "messages": [
            {"role": "user", "content": "أنشئ ملف api_key=sk-abcdefghijklmnopqrstuvwxyz123456"},
            {"role": "assistant", "content": "تم إنشاء الملف بعد التحقق."},
        ],
        "source": "test",
        "quality": .9,
    }
    first = enrich_conversation(row)
    second = enrich_conversation(row)
    assert first["record_hash"] == second["record_hash"]
    assert first["redacted"] is True
    assert "[REDACTED_SECRET]" in first["input"]
    assert first["schema_version"] == "kca-3.0"


def test_kca_dataset_deduplicates(tmp_path: Path):
    src = tmp_path / "chat.jsonl"
    row = {"id": "same", "messages": [{"role": "user", "content": "Hello"}, {"role": "assistant", "content": "Hi"}], "quality": .9}
    src.write_text(json.dumps(row, ensure_ascii=False) + "\n" + json.dumps(row, ensure_ascii=False) + "\n", encoding="utf-8")
    out = tmp_path / "kca.jsonl"
    report = build_kca_dataset([src], out)
    assert report["samples"] == 1
    assert len(out.read_text(encoding="utf-8").splitlines()) == 1


def test_kca_state_store_roundtrip(tmp_path: Path):
    store = KCAStateStore(tmp_path / "kca.sqlite3")
    store.upsert("op-1", "req-1", "completed", {"intent": "question"}, {"status": "completed"})
    rows = store.recent()
    assert rows and rows[0]["operation_id"] == "op-1"
    assert json.loads(rows[0]["state_json"])["intent"] == "question"


def test_invalid_gguf_is_rejected(tmp_path: Path):
    from model.weights_manager import WeightsManager
    p = tmp_path / "broken.gguf"
    p.write_bytes(b"NOTGGUF" + b"\0" * 64)
    wm = WeightsManager(tmp_path)
    info = wm.inspect(p)
    assert info["kind"] == "gguf"
    assert info["compatible"] is False



def test_self_manager_requires_new_approved_samples(tmp_path: Path):
    from autonomy.self_manager import SelfManager
    from memory.conversations import ConversationMemory
    conv = tmp_path / "conversations.sqlite3"
    db = ConversationMemory(conv)
    db.put("سؤال ثابت", "إجابة ثابتة", quality=1.0)
    sm = SelfManager(tmp_path, min_new_samples=2)
    first = sm.status(tmp_path / "missing-harvest.sqlite3", conv)
    assert first["accepted_samples"] == 1
    assert first["ready"] is False
    db.put("سؤال آخر", "إجابة أخرى", quality=1.0)
    second = sm.status(tmp_path / "missing-harvest.sqlite3", conv)
    assert second["accepted_samples"] == 2
    assert second["ready"] is True


def test_self_manager_failure_remains_retryable(tmp_path: Path, monkeypatch):
    from autonomy.self_manager import SelfManager
    from memory.conversations import ConversationMemory
    import training.pipeline as pipeline_module
    conv = tmp_path / "conversations.sqlite3"
    db = ConversationMemory(conv)
    db.put("سؤال 1", "إجابة 1", quality=1.0)
    (tmp_path / "data" / "training" / "bootstrap").mkdir(parents=True)
    (tmp_path / "data" / "training" / "bootstrap" / "chat_validation.jsonl").write_text(
        '{"id":"v","text":"test"}\n', encoding="utf-8"
    )
    class FailingPipeline:
        def __init__(self, *args, **kwargs): pass
        def run(self, *args, **kwargs): raise RuntimeError("intentional test failure")
    monkeypatch.setattr(pipeline_module, "TrainingPipeline", FailingPipeline)
    sm = SelfManager(tmp_path, min_new_samples=1)
    try:
        sm.autonomous_cycle(tmp_path / "missing-harvest.sqlite3", conv, steps=1)
    except RuntimeError:
        pass
    else:
        raise AssertionError("expected autonomous cycle failure")
    state = sm.status(tmp_path / "missing-harvest.sqlite3", conv)
    assert state["last_status"] == "failed"
    assert state["new_samples"] == 1
    assert state["ready"] is True
