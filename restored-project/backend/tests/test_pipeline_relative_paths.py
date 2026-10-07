from pathlib import Path

import pytest

from training.pipeline import TrainingPipeline, PipelineConfig


def _resolve_base(pipe, value):
    base = Path(value)
    if not base.is_absolute():
        base = (pipe.root / base).resolve()
    else:
        base = base.resolve()
    return base


def test_relative_base_checkpoint_is_resolved_from_pipeline_root(tmp_path):
    root = Path(tmp_path) / "project"
    base = root / "models" / "active" / "base"
    base.mkdir(parents=True)
    (base / "config.json").write_text("{}", encoding="utf-8")
    pipe = TrainingPipeline(root)
    cfg = PipelineConfig(base_checkpoint="models/active/base")
    resolved = _resolve_base(pipe, cfg.base_checkpoint)
    assert resolved == base.resolve()


def test_run_reuses_relative_base_tokenizer_from_pipeline_root(tmp_path, monkeypatch):
    root = Path(tmp_path) / "project"
    base = root / "models" / "active" / "base"
    base.mkdir(parents=True)
    source_tokenizer = Path(__file__).resolve().parents[1] / "models" / "active" / "ALI-Bootstrap-v2.5" / "tokenizer.model"
    (base / "tokenizer.model").write_bytes(source_tokenizer.read_bytes())
    train = root / "train.jsonl"
    train.write_text('{"messages":[{"role":"user","content":"سؤال"},{"role":"assistant","content":"جواب"}]}\n', encoding="utf-8")
    pipe = TrainingPipeline(root)
    monkeypatch.chdir(tmp_path)

    def unexpected_prepare(*args, **kwargs):
        raise AssertionError("continuation incorrectly retrained the tokenizer")

    def stop_after_tokenizer(self, cfg, tokenizer_vocab_size):
        raise RuntimeError("tokenizer_reuse_reached_new_model")

    monkeypatch.setattr(pipe, "prepare_tokenizer", unexpected_prepare)
    monkeypatch.setattr(pipe, "new_model", stop_after_tokenizer.__get__(pipe, TrainingPipeline))
    cfg = PipelineConfig(stage="lora", train_path=str(train), base_checkpoint="models/active/base")
    with pytest.raises(RuntimeError, match="tokenizer_reuse_reached_new_model"):
        pipe.run(cfg)
