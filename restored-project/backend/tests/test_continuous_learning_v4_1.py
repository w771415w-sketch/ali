from pathlib import Path

from training.continuous_learning import ContinuousLearningManager
from model.registry import ModelRegistry


def make_root(tmp_path: Path):
    (tmp_path / 'models').mkdir(parents=True)
    (tmp_path / 'data' / 'training' / 'device_p50').mkdir(parents=True)
    val = tmp_path / 'data' / 'training' / 'device_p50' / 'chat_validation.jsonl'
    val.write_text('{"messages":[{"role":"user","content":"x"},{"role":"assistant","content":"y"}]}\n', encoding='utf-8')
    reg = ModelRegistry(tmp_path / 'models' / 'models.sqlite3')
    reg.register('ALI', 'bootstrap', artifact_type='base', status='active', hf_dir=str(tmp_path / 'base'), checkpoint=str(tmp_path / 'base'))
    return tmp_path, reg


def test_import_markdown_qna_and_cross_file_dedup(tmp_path: Path):
    root, reg = make_root(tmp_path)
    manager = ContinuousLearningManager(root, reg)
    first = root / 'one.md'
    first.write_text('User:\nما هو ALI؟\n\nAssistant:\nALI مساعد محلي.\n', encoding='utf-8')
    second = root / 'two.md'
    second.write_text('# نسخة ثانية\n\nUser:\nما هو ALI؟\n\nAssistant:\nALI مساعد محلي.\n', encoding='utf-8')
    a = manager.import_files([first])
    b = manager.import_files([second])
    assert a[0]['status'] == 'validated'
    assert a[0]['sample_count'] == 1
    assert b[0]['status'] == 'duplicate'
    assert 'all_samples_already_imported' in (b[0]['warnings'] or [])
    assert len(manager.pending()) == 1


def test_plain_markdown_is_rag_only(tmp_path: Path):
    root, reg = make_root(tmp_path)
    manager = ContinuousLearningManager(root, reg)
    doc = root / 'manual.md'
    doc.write_text('# ALI Manual\n\nهذا مستند معرفة وليس محادثة تدريبية صريحة.\n', encoding='utf-8')
    result = manager.import_files([doc])[0]
    assert result['ok'] is True
    assert result['status'] == 'rag_only'
    assert result['routed_to_rag'] is True
    assert not manager.pending()


def test_generation_counter_ignores_runtime_versions(tmp_path: Path):
    root, reg = make_root(tmp_path)
    reg.register('ALI', 'v3', artifact_type='merged', status='candidate', hf_dir=str(root / 'candidate'))
    manager = ContinuousLearningManager(root, reg)
    assert manager._next_generation() == 'v4'
