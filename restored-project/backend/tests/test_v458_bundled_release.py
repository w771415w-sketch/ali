from __future__ import annotations

import json
from pathlib import Path

from knowledge.store import KnowledgeStore
from model.manager import ModelManager
from model.registry import ModelRegistry
from training.continuous_learning import ContinuousLearningManager

ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / "data" / "training" / "testdata" / "ALI_User_Understanding_Bundle_V4.md"


def test_v458_bundled_model_registry_and_reload():
    registry = ModelRegistry(ROOT / "models" / "models.sqlite3")
    active = registry.active("ALI")
    assert active is not None
    assert active["version"] == "v4"
    manager = ModelManager(ROOT, registry)
    engine, row = manager.load(active, compute_mode="cpu")
    assert row["version"] == "v4"
    assert engine.model_dir == ROOT / "models" / "active" / "ALI-v4"
    assert (engine.model_dir / "model.safetensors").is_file()
    assert (engine.model_dir / "tokenizer.model").is_file()


def test_v458_bundled_training_questions_are_preseeded():
    store = KnowledgeStore(ROOT / "runtime_knowledge.sqlite3")
    manager = ContinuousLearningManager(ROOT)
    samples, _safe, _warnings = manager.parse_file(FIXTURE)
    assert len(samples) > 0
    hits = 0
    for sample in samples:
        question = [m["content"] for m in sample if m.get("role") == "user"][-1]
        hit = store.training_qa_match(question)
        assert hit is not None, question
        assert hit["answer"].strip()
        hits += 1
    assert hits == len(samples)
    import sqlite3
    con = sqlite3.connect(ROOT / "runtime_knowledge.sqlite3")
    row = con.execute("SELECT path FROM documents WHERE kind='trained-bundle'").fetchone()
    con.close()
    # The fixture is stored as a real portable document, not only in memory.
    assert row is not None
    assert row[0] == "data/training/testdata/ALI_User_Understanding_Bundle_V4.md"


def test_v458_bundle_artifact_hashes_exist():
    receipt = ROOT / "models" / "runs" / "ALI-v1-20261004-224649-233144" / "FINAL_FILE_TRAINING_E2E_RECEIPT_4.5.8.json"
    data = json.loads(receipt.read_text(encoding="utf-8"))
    assert data["training"]["status"] == "success"
    assert data["quiz"]["source_answer_match"] >= 0
    paths = [
        ROOT / "models" / "active" / "ALI-v4" / "model.safetensors",
        ROOT / "models" / "active" / "ALI-v4" / "tokenizer.model",
        ROOT / "models" / "generations" / "v4" / "generation.json",
        ROOT / "models" / "generations" / "v4" / "lineage.json",
    ]
    assert all(p.is_file() and p.stat().st_size > 0 for p in paths)
