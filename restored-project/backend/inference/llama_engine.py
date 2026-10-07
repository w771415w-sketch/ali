# -*- coding: utf-8 -*-
"""Local GGUF chat engine backed by llama.cpp's OpenAI-compatible llama-server.

The engine is deliberately optional: when the model/binary are absent the main
ALI runtime can continue with its internal model. GPU offload is adaptive and
falls back to CPU automatically in auto mode if the installed llama.cpp build
cannot use the legacy Maxwell GPU.
"""
from __future__ import annotations
from pathlib import Path
from typing import Iterable, Any

from inference.llama_server import LlamaServer
from runtime.device_policy import gguf_offload_policy
from runtime.hardware import detect


class LlamaServerEngine:
    def __init__(self, executable: str | Path, model: str | Path, *, compute_mode: str = "auto", context: int = 2048, model_version: str = ""):
        self.executable = Path(executable).resolve()
        self.model = Path(model).resolve()
        self.tokenizer = None
        self.model_version = model_version or self.model.stem
        hw = detect(probe_torch=False, force=True)
        policy = gguf_offload_policy(hw, mode=compute_mode, total_layers=24)
        self.device = str(policy.get("device", "cpu"))
        self.n_gpu_layers = int(policy.get("n_gpu_layers", 0))
        self.gpu_memory_fraction = float(policy.get("gpu_memory_fraction", 0.0) or 0.0)
        self.context = int(context)
        self.server = LlamaServer(
            self.executable,
            self.model,
            port=48921,
            n_gpu_layers=self.n_gpu_layers,
            context=self.context,
        )

    def _ensure(self) -> None:
        try:
            self.server.start()
        except Exception:
            # Auto mode must prefer a working CPU inference path over a hard
            # failure if a CUDA/Maxwell binary is present but incompatible.
            if self.device != "cpu":
                self.device = "cpu"
                self.n_gpu_layers = 0
                self.server.stop()
                self.server = LlamaServer(
                    self.executable,
                    self.model,
                    port=48921,
                    n_gpu_layers=0,
                    context=self.context,
                )
                self.server.start()
            else:
                raise

    def complete(self, messages: list[dict[str, Any]], *, system: str = "", max_new_tokens: int = 256, temperature: float = .6) -> str:
        self._ensure()
        final_messages = []
        if system:
            final_messages.append({"role": "system", "content": str(system)})
        final_messages.extend(messages)
        return str((self.server.chat(final_messages, max_tokens=max_new_tokens, temperature=temperature) or {}).get('text',''))

    def stream(self, messages: list[dict[str, Any]], *, system: str = "", max_new_tokens: int = 256, temperature: float = .6) -> Iterable[str]:
        # The local llama-server bridge uses a deterministic non-streaming call
        # for maximum compatibility on older Windows/Maxwell environments. The
        # UI still receives the answer through the normal stream event contract.
        self._ensure()
        final_messages=[]
        if system: final_messages.append({'role':'system','content':str(system)})
        final_messages.extend(messages)
        yield from self.server.stream_chat(final_messages, max_tokens=max_new_tokens, temperature=temperature)

    def close(self) -> None:
        try:
            self.server.stop()
        except Exception:
            pass
