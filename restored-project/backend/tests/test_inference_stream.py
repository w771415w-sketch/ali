from pathlib import Path


def test_stream_source_uses_deltas():
    root = Path(__file__).resolve().parents[1]
    text = (root / "inference" / "engine.py").read_text(encoding="utf8")
    assert "last_text=''" in text
    assert 'yield delta' in text
    assert "return ''.join(self.stream(rows,**kwargs))" in text
