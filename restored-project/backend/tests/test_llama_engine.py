from pathlib import Path
from inference.llama_engine import LlamaServerEngine


def test_llama_engine_builds_safe_server_contract(monkeypatch, tmp_path):
    exe=tmp_path/"llama-server.exe"; model=tmp_path/"m.gguf"
    exe.write_bytes(b"x"); model.write_bytes(b"GGUF")
    monkeypatch.setattr("inference.llama_engine.detect", lambda **kwargs: type("H", (), {"gpu_mem_free_gb":1.5,"gpu_mem_used_gb":0.5,"vram_gb":2.0,"gpu_available":True,"torch_cuda":False})())
    e=LlamaServerEngine(exe,model,compute_mode="cpu")
    assert e.n_gpu_layers == 0
    assert e.server.port == 48921
