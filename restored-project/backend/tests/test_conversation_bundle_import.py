from pathlib import Path

from training.continuous_learning import ContinuousLearningManager


def test_bundled_v1_conversation_markdown_imports_504_samples(tmp_path: Path):
    project_root = Path(__file__).resolve().parents[2]
    source = project_root / "ALI_Conversation_Training_V1.md"
    assert source.is_file()
    runtime_root = tmp_path / "runtime"
    manager = ContinuousLearningManager(runtime_root)
    result = manager.import_files([source])[0]
    assert result["ok"] is True
    assert result["status"] == "validated"
    assert result["sample_count"] == 504
    assert result["routed_to_rag"] is True
    batch = runtime_root / "artifacts" / "continuous_learning" / "batches" / f"{result['batch_id']}.jsonl"
    assert batch.is_file()
    lines = [line for line in batch.read_text(encoding="utf-8").splitlines() if line.strip()]
    assert len(lines) == 504
