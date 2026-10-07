from __future__ import annotations
from pathlib import Path
from training.accumulated_updates import AccumulatedTrainingManager

def test_markdown_validation_and_dedup(tmp_path: Path):
    root=tmp_path/'ALI'
    root.mkdir()
    f=root/'sample.md'
    f.write_text('# Training\n\nUser: كيف تنفذ الاختبار؟\n\nAssistant: سأفحص المتطلبات ثم أشغل الاختبار وأتحقق من النتيجة.\n',encoding='utf-8')
    m=AccumulatedTrainingManager(root)
    first=m.add_files([f])[0]
    assert first['accepted'] is True
    assert m.pending_batch_paths()
    second=m.add_files([f])[0]
    assert second['accepted'] is False
    assert second['reason']=='duplicate_content'
    assert m.mark_sources_as_adapterized(m.pending_batch_paths())==1
    assert not m.pending_batch_paths()
