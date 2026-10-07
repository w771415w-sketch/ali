from pathlib import Path

from training.continuous_learning import ContinuousLearningManager


def test_import_ready_markdown_conversation_bundle(tmp_path: Path):
    root = tmp_path / 'ALI'
    root.mkdir()
    f = root / 'ALI_Conversation_Training_V1.md'
    f.write_text(
        '# Bundle\n\n'
        '## المحادثة 001 — agent\n'
        '> النوع: `agent` · المجموعة: `train`\n\n'
        '**User:** كيف أنفذ مشروعاً؟\n\n'
        '**Assistant:** أحول الطلب إلى خطة، أنفذ الأدوات المصرح بها، ثم أتحقق من النتيجة.\n\n'
        '## المحادثة 002 — debugging\n'
        '> النوع: `debugging` · المجموعة: `train`\n\n'
        '**User:** كيف أصلح الخطأ؟\n\n'
        '**Assistant:** أفحص سبب الخطأ، أطبق الإصلاح، ثم أشغل الاختبارات.\n',
        encoding='utf-8',
    )
    m = ContinuousLearningManager(root)
    result = m.import_files([f])[0]
    assert result['ok'] is True
    assert result['status'] == 'validated'
    assert result['sample_count'] == 2
    batch = root / 'artifacts' / 'continuous_learning' / 'batches' / f"{result['batch_id']}.jsonl"
    assert batch.exists()
    assert sum(1 for line in batch.read_text(encoding='utf-8').splitlines() if line.strip()) == 2
