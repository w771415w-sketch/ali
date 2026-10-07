# -*- coding: utf-8 -*-
"""ALI model lifecycle: discover, load, validate and activate model versions."""
from __future__ import annotations
from pathlib import Path
import json
from typing import Any

from model.registry import ModelRegistry
from model.ali_lm import AliConfig
from inference.engine import LocalInference
from runtime.device_policy import choose_policy
from runtime.hardware import detect, apply_cuda_memory_budget

class ModelManager:
    def __init__(self, root: str | Path, registry: ModelRegistry):
        self.root=Path(root); self.registry=registry; self.engine=None; self.current=None

    def _resolve_artifact_path(self, value: str | Path | None) -> Path | None:
        """Resolve portable/legacy absolute model paths against the current install root."""
        if not value:
            return None
        raw = Path(str(value))
        candidates = []
        if raw.is_absolute():
            candidates.append(raw)
            # Release databases from older copies may retain an absolute path from a
            # previous extraction directory. Re-anchor the path below this project
            # when the tail matches a known model layout. Handle both native separators
            # and Windows-style backslashes even when a release is inspected on Linux.
            parts = list(raw.parts)
            normalized_parts = [x for x in str(value).replace('\\', '/').split('/') if x]
            marker_i = None
            for marker in ('models', 'active', 'inbox', 'merged', 'runs'):
                if marker in parts:
                    marker_i = parts.index(marker); break
                if marker in normalized_parts:
                    marker_i = normalized_parts.index(marker); break
            if marker_i is not None:
                tail = parts[marker_i:] if marker in parts else normalized_parts[marker_i:]
                candidates.append(self.root / Path(*tail))
            candidates.append(self.root / raw.name)
        else:
            # A Windows path can be serialized into a registry and later parsed by a
            # non-Windows maintenance tool as a relative string containing backslashes.
            normalized_parts = [x for x in str(value).replace('\\', '/').split('/') if x]
            marker_i = None
            for marker in ('models', 'active', 'inbox', 'merged', 'runs'):
                if marker in normalized_parts:
                    marker_i = normalized_parts.index(marker); break
            if marker_i is not None:
                candidates.append(self.root / Path(*normalized_parts[marker_i:]))
            candidates.append(self.root / raw)
            candidates.append(self.root / 'models' / raw)
        for c in candidates:
            try:
                if c.exists():
                    return c.resolve()
            except Exception:
                continue
        return None

    def discover_active(self, name='ALI'):
        row=self.registry.active(name)
        if row:
            hf = self._resolve_artifact_path(row.get('hf_dir') or row.get('checkpoint'))
            if hf and hf.exists():
                row = dict(row); row['hf_dir'] = str(hf); row['checkpoint'] = row.get('checkpoint') or str(hf); return row
        return None

    def discover_development(self, name='ALI'):
        """Return the newest valid candidate for local preview, never marking it active."""
        rows=self.registry.list(name)
        for row in rows:
            if row.get('status') != 'candidate':
                continue
            hf = self._resolve_artifact_path(row.get('hf_dir') or row.get('checkpoint'))
            if hf and hf.exists():
                row = dict(row); row['hf_dir'] = str(hf); row['checkpoint'] = row.get('checkpoint') or str(hf); return row
        return None

    def load(self, row: dict | None=None, name='ALI', compute_mode: str = 'auto'):
        row=row or self.discover_active(name)
        if not row: raise FileNotFoundError('No active ALI model version with an HF checkpoint')
        hf=self._resolve_artifact_path(row.get('hf_dir') or row.get('checkpoint'))
        if not hf: raise FileNotFoundError(f"Model artifact not found in current installation: {row.get('hf_dir') or row.get('checkpoint')}")
        cfg_path = hf/'config.json'
        if not cfg_path.is_file(): raise FileNotFoundError(f'Model config missing: {cfg_path}')
        cfg=json.loads(cfg_path.read_text(encoding='utf-8'))
        policy=choose_policy(detect(force=True), mode=compute_mode)
        device=str(policy.get('train_device','cpu'))
        if device == 'cuda':
            apply_cuda_memory_budget(float(policy.get('gpu_memory_fraction', 0.60) or 0.60))
        try:
            self.engine=LocalInference(hf,hf,device=device)
        except RuntimeError:
            if device == 'cuda' and str(compute_mode).lower() == 'auto':
                try:
                    import torch; torch.cuda.empty_cache()
                except Exception: pass
                self.engine=LocalInference(hf,hf,device='cpu')
                device='cpu'
            else:
                raise
        self.current=row
        return self.engine, row

    def load_path(self, hf_dir: str | Path, device: str | None=None, compute_mode: str = 'auto'):
        p=self._resolve_artifact_path(hf_dir)
        if p is None: raise FileNotFoundError(f'Model artifact not found: {hf_dir}')
        if device is None:
            policy=choose_policy(detect(force=True), mode=compute_mode); device=str(policy.get('train_device','cpu'))
        self.engine=LocalInference(p,p,device=device); self.current={'hf_dir':str(p),'status':'loaded'}; return self.engine

def _cuda_ok():
    try:
        import torch
        return bool(torch.cuda.is_available())
    except Exception: return False
