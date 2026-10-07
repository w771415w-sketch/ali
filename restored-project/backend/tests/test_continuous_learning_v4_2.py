from pathlib import Path
from tempfile import TemporaryDirectory

from model.registry import ModelRegistry
from training.continuous_learning import ContinuousLearningManager


def test_document_is_rag_only_and_chat_pairs_are_training():
    with TemporaryDirectory() as tmp:
        root = Path(tmp)
        registry = ModelRegistry(root / "models.sqlite3")
        manager = ContinuousLearningManager(root, registry)
        try:
            manual = root / "manual.md"
            manual.write_text("# Manual\nUse the safety checklist before promotion.", encoding="utf-8")
            first = manager.import_files([manual])[0]
            assert first["ok"] is True
            assert first["status"] == "rag_only"
            assert first["routed_to_rag"] is True
            assert manager.pending() == []

            qa = root / "qa.md"
            qa.write_text("User:\nWhat is the policy?\nAssistant:\nRun the checks first.\n", encoding="utf-8")
            second = manager.import_files([qa])[0]
            assert second["ok"] is True
            assert second["status"] == "validated"
            assert second["sample_count"] == 1
            assert len(manager.pending()) == 1
        finally:
            manager.close()
            del manager
            del registry
            # Give Windows a moment to release the SQLite file handles
            import gc; gc.collect()
            import time; time.sleep(0.05)


def test_duplicate_source_is_rejected():
    with TemporaryDirectory() as tmp:
        root = Path(tmp)
        registry = ModelRegistry(root / "models.sqlite3")
        manager = ContinuousLearningManager(root, registry)
        try:
            qa = root / "qa.md"
            qa.write_text("User:\nHi\nAssistant:\nHello\n", encoding="utf-8")
            assert manager.import_files([qa])[0]["status"] == "validated"
            duplicate = manager.import_files([qa])[0]
            assert duplicate["ok"] is False
            assert duplicate["status"] == "duplicate"
        finally:
            manager.close()
            del manager
            del registry
            import gc; gc.collect()
            import time; time.sleep(0.05)
