# -*- coding: utf-8 -*-
"""Run ALI's own GGUF locally through an installed llama.cpp binary."""
from __future__ import annotations
from pathlib import Path
import os, subprocess
from typing import Iterator

class GGUFInference:
    def __init__(self, model_path: str | Path, llama_dir: str | Path = "vendor/llama.cpp", n_gpu_layers: int = 0):
        self.model = Path(model_path).resolve()
        self.root = Path(llama_dir).resolve()
        self.n_gpu_layers = max(0, int(n_gpu_layers))
        self.binary = self._find()
        if not self.model.exists():
            raise FileNotFoundError(self.model)
        if not self.binary:
            raise FileNotFoundError("llama-cli executable not found in vendor/llama.cpp")

    def _find(self) -> Path | None:
        names = ["llama-cli.exe", "llama-cli"]
        candidates = []
        for n in names:
            candidates += [self.root / n, self.root / "build" / "bin" / n, self.root / "bin" / n]
        return next((p for p in candidates if p.exists()), None)

    def stream(self, prompt: str, max_new_tokens: int = 256, context: int = 512, temperature: float = 0.7) -> Iterator[str]:
        cmd = [str(self.binary), "-m", str(self.model), "-p", prompt, "-n", str(max_new_tokens), "-c", str(context), "-ngl", str(self.n_gpu_layers), "--no-display-prompt", "--no-show-timings", "-no-cnv"]
        if temperature <= 0:
            cmd += ["--temp", "0"]
        else:
            cmd += ["--temp", str(temperature)]
        env = dict(os.environ)
        p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, encoding="utf-8", errors="replace", cwd=str(self.root), bufsize=1, env=env)
        assert p.stdout is not None
        try:
            for line in p.stdout:
                yield line
        finally:
            p.wait(timeout=5)
