from __future__ import annotations

import json
from pathlib import Path
import pytest
import pytest

import torch

from model.ali_lm import AliConfig, ALIForCausalLM
from model.artifacts import ArtifactManifest, sha256_path
from model.registry import ModelRegistry
from model.weights_manager import WeightsManager
from core.tool_protocol import parse_tool_calls, validate_tool_call


def _tiny_model(tmp_path: Path):
    cfg = AliConfig(
        vocab_size=64, hidden_size=32, intermediate_size=64,
        num_hidden_layers=2, num_attention_heads=4,
        num_key_value_heads=4, max_position_embeddings=64,
    )
    model = ALIForCausalLM(cfg)
    state = {k: v.detach().cpu() for k, v in model.state_dict().items()}
    ckpt = tmp_path / "source"
    ckpt.mkdir()
    torch.save({"model": state, "config": cfg.to_dict(), "global_step": 3}, ckpt / "checkpoint.pt")
    (ckpt / "config.json").write_text(json.dumps(cfg.to_dict()), encoding="utf-8")
    return ckpt, cfg


def test_artifact_manifest_roundtrip(tmp_path):
    p = tmp_path / "artifact"
    p.mkdir()
    (p / "data.txt").write_text("ALI", encoding="utf-8")
    m = ArtifactManifest(artifact_id="x", artifact_type="base", name="ALI", version="v1", path=str(p))
    m.finalize(p)
    m.write(p / "manifest.json")
    loaded = ArtifactManifest.load(p / "manifest.json")
    assert loaded.verify()["valid"] is True
    assert sha256_path(p) == loaded.sha256


def test_weight_import_embedded_config_and_registry(tmp_path):
    src, _cfg = _tiny_model(tmp_path)
    registry = ModelRegistry(tmp_path / "models" / "models.sqlite3")
    manager = WeightsManager(tmp_path, registry)
    out = manager.install(src, name="ALI")
    assert out["type"] == "base"
    assert Path(out["path"]).exists()
    assert manager.verify(out["path"])["valid"] is True
    rows = registry.list("ALI")
    assert rows and rows[0]["artifact_type"] == "base"


def test_tool_protocol_supports_tagged_json():
    calls = parse_tool_calls('<tool_call>{"name":"list_dir","arguments":{"path":"."}}</tool_call>')
    assert calls and calls[0]["tool"] == "list_dir"
    ok, reason = validate_tool_call(calls[0], {"list_dir": {"required": ["path"]}})
    assert ok, reason


def test_weight_import_standalone_checkpoint_and_adapter(tmp_path):
    src, _cfg = _tiny_model(tmp_path)
    registry = ModelRegistry(tmp_path / "models" / "models.sqlite3")
    manager = WeightsManager(tmp_path, registry)
    imported = manager.install(src / "checkpoint.pt", name="ALI")
    assert imported["type"] == "base"
    assert manager.verify(imported["path"])["valid"] is True

    from training.lora import apply_lora, save_lora_adapter
    model = ALIForCausalLM(_cfg)
    apply_lora(model, rank=2, alpha=4.0, dropout=0.0)
    adapter_dir = tmp_path / "adapter"
    save_lora_adapter(model, adapter_dir, {"base_version": "tiny"})
    adapter = manager.install(adapter_dir, name="ALI")
    assert adapter["type"] == "adapter"
    assert Path(adapter["path"]).exists()
