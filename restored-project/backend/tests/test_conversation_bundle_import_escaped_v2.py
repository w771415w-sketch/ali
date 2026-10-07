from pathlib import Path
from training.continuous_learning import ContinuousLearningManager

def test_escaped_bold_conversation_bundle_imports_all_samples(tmp_path: Path):
    root = tmp_path / "escaped_bold_120.md"
    sections=[]
    for i in range(120):
        bs = chr(92)
        sections.append(f"**## المحادثة {i+1} — agent**\n\n> النوع: `agent` · المجموعة: `train`\n\n**{bs}*{bs}*User:{bs}*{bs}*** سؤال اختبار {i+1}؟\n\n**{bs}*{bs}*Assistant:{bs}*{bs}*** إجابة اختبار {i+1}.\n")
    root.write_text("\n---\n".join(sections), encoding="utf-8")
    m = ContinuousLearningManager(tmp_path / "ALI")
    result = m.import_files([root])[0]
    assert result["ok"] is True
    assert result["status"] == "validated"
    assert result["sample_count"] == 120
    assert result["routed_to_rag"] is True
