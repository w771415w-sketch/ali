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
```

---

### `171/588` `backend/model/model.py`

- **المسار الكامل:** `F:\1f\p\ALI_Studio_Pro_Design4_4.6.0\04_Adaptive_Hybrid\backend/model/model.py`
- **الحجم:** 362 بايت (0.4 KB)
- **الامتداد:** `.py`

```python
# -*- coding: utf-8 -*-
"""Deprecated compatibility module.

The old NumPy TinyTransformer implementation was removed because it did not train
real language-model weights. Use model.ali_lm.ALIForCausalLM instead.
"""
from .ali_lm import AliConfig, ALIForCausalLM
ModelConfig = AliConfig
TinyTransformer = ALIForCausalLM
__all__=['ModelConfig','TinyTransformer']
```

---

### `172/588` `backend/model/registry.py`

- **المسار الكامل:** `F:\1f\p\ALI_Studio_Pro_Design4_4.6.0\04_Adaptive_Hybrid\backend/model/registry.py`
- **الحجم:** 7836 بايت (7.7 KB)
- **الامتداد:** `.py`

```python
# -*- coding: utf-8 -*-
"""Versioned model/artifact registry with immutable lineage metadata."""
from __future__ import annotations

from pathlib import Path
import hashlib
import json
import sqlite3
import time
from typing import Any


class ModelRegistry:
    def __init__(self, db_path: str | Path):
        self.path = Path(db_path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._bootstrap()

    def _connect(self):
        c = sqlite3.connect(self.path, timeout=10)
        c.row_factory = sqlite3.Row
        return c

    def _bootstrap(self):
        c = self._connect()
        c.execute(
            """
            CREATE TABLE IF NOT EXISTS model_versions(
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                version TEXT NOT NULL,
                artifact_type TEXT NOT NULL DEFAULT 'base',
                status TEXT NOT NULL,
                base_version TEXT,
                checkpoint TEXT,
                hf_dir TEXT,
                gguf TEXT,
                adapter TEXT,
                quantized TEXT,
                dataset_hash TEXT,
                tokenizer_hash TEXT,
                artifact_hash TEXT,
                train_config TEXT,
                eval_json TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                parent_generation TEXT NOT NULL DEFAULT '',
                cumulative_dataset_hash TEXT NOT NULL DEFAULT '',
                UNIQUE(name,version)
            )
            """
        )
        cols = {r["name"] for r in c.execute("PRAGMA table_info(model_versions)").fetchall()}
        if "artifact_type" not in cols:
            c.execute("ALTER TABLE model_versions ADD COLUMN artifact_type TEXT NOT NULL DEFAULT 'base'")
        for name, typ in (("adapter", "TEXT"), ("quantized", "TEXT"), ("artifact_hash", "TEXT"), ("parent_generation", "TEXT NOT NULL DEFAULT ''"), ("cumulative_dataset_hash", "TEXT NOT NULL DEFAULT ''")):
            if name not in cols:
                c.execute(f"ALTER TABLE model_versions ADD COLUMN {name} {typ}")
        c.commit()
        c.close()

    def register(self, name: str, version: str, **meta):
        payload = (
            name,
            version,
            str(meta.get("artifact_type", "base")),
            str(meta.get("status", "candidate")),
            str(meta.get("base_version", "")),
            str(meta.get("checkpoint", "")),
            str(meta.get("hf_dir", "")),
            str(meta.get("gguf", "")),
            str(meta.get("adapter", "")),
            str(meta.get("quantized", "")),
            str(meta.get("dataset_hash", "")),
            str(meta.get("tokenizer_hash", "")),
            str(meta.get("artifact_hash", "")),
            json.dumps(meta.get("train_config", {}), ensure_ascii=False),
            json.dumps(meta.get("eval", {}), ensure_ascii=False),
            str(meta.get("parent_generation", "")),
            str(meta.get("cumulative_dataset_hash", "")),
        )
        c = self._connect()
        c.execute(
            """
            INSERT OR REPLACE INTO model_versions(
                name,version,artifact_type,status,base_version,checkpoint,hf_dir,gguf,
                adapter,quantized,dataset_hash,tokenizer_hash,artifact_hash,train_config,eval_json,parent_generation,cumulative_dataset_hash
            ) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
            """,
            payload,
        )
        c.commit()
        c.close()


    def update_artifacts(self, name: str, version: str, **fields) -> None:
        """Attach post-promotion artifacts such as GGUF without changing lifecycle status."""
        allowed = {"checkpoint", "hf_dir", "gguf", "adapter", "quantized", "artifact_hash", "eval_json"}
        updates = {k: v for k, v in fields.items() if k in allowed}
        if not updates:
            return
        parts = []
        values = []
        for k, v in updates.items():
            parts.append(f"{k}=?")
            if k == "eval_json" and not isinstance(v, str):
                v = json.dumps(v, ensure_ascii=False)
            values.append(v)
        values.extend([name, version])
        c = self._connect()
        c.execute(f"UPDATE model_versions SET {', '.join(parts)} WHERE name=? AND version=?", tuple(values))
        c.commit()
        c.close()

    def promote(self, name: str, version: str) -> None:
        c = self._connect()
        row = c.execute(
            "SELECT artifact_type,hf_dir,checkpoint FROM model_versions WHERE name=? AND version=?",
            (name, version),
        ).fetchone()
        if not row:
            c.close()
            raise KeyError(f"model version not found: {name}:{version}")
        if row["artifact_type"] not in {"base", "merged"} or not (row["hf_dir"] or row["checkpoint"]):
            c.close()
            raise ValueError("only base/merged model artifacts with a loadable checkpoint can become active")
        c.execute(
            "UPDATE model_versions SET status='archived' WHERE name=? AND status='active'",
            (name,),
        )
        c.execute(
            "UPDATE model_versions SET status='active' WHERE name=? AND version=?",
            (name, version),
        )
        c.commit()
        c.close()
        try:
            active_dir = self.path.parent / "active"
            active_dir.mkdir(parents=True, exist_ok=True)
            active_row = self.active(name)
            if active_row:
                (active_dir / "current.json").write_text(
                    json.dumps({
                        "model": name,
                        "active_generation": active_row.get("version", ""),
                        "hf_dir": active_row.get("hf_dir", ""),
                        "checkpoint": active_row.get("checkpoint", ""),
                        "gguf": active_row.get("gguf", ""),
                        "updated_at": time.time() if "time" in globals() else 0,
                    }, ensure_ascii=False, indent=2) + "\n",
                    encoding="utf-8",
                )
        except Exception:
            pass

    def active(self, name: str = "ALI") -> dict[str, Any] | None:
        c = self._connect()
        row = c.execute(
            "SELECT * FROM model_versions WHERE name=? AND status='active' ORDER BY id DESC LIMIT 1",
            (name,),
        ).fetchone()
        c.close()
        return dict(row) if row else None

    def list(self, name: str = "ALI") -> list[dict[str, Any]]:
        c = self._connect()
        rows = c.execute(
            "SELECT * FROM model_versions WHERE name=? ORDER BY id DESC",
            (name,),
        ).fetchall()
        c.close()
        return [dict(x) for x in rows]

    def list_loadable(self, name: str = "ALI") -> list[dict[str, Any]]:
        return [
            r for r in self.list(name)
            if r.get("artifact_type") in {"base", "merged"} and (r.get("hf_dir") or r.get("checkpoint"))
        ]

    def find_dataset(self, dataset_hash: str, name: str = "ALI"):
        c = self._connect()
        c.row_factory = sqlite3.Row
        row = c.execute(
            "SELECT * FROM model_versions WHERE name=? AND dataset_hash=? ORDER BY id DESC LIMIT 1",
            (name, dataset_hash),
        ).fetchone()
        c.close()
        return dict(row) if row else None


def file_hash(path: str | Path) -> str:
    p = Path(path)
    h = hashlib.sha256()
    if p.is_file():
        with p.open("rb") as f:
            for b in iter(lambda: f.read(1024 * 1024), b""):
                h.update(b)
        return h.hexdigest()
    for f in sorted(x for x in p.rglob("*") if x.is_file()):
        h.update(str(f.relative_to(p)).encode("utf-8"))
        h.update(file_hash(f).encode("ascii"))
    return h.hexdigest()


__all__ = ["ModelRegistry", "file_hash"]
```

---

### `173/588` `backend/model/weights_manager.py`

- **المسار الكامل:** `F:\1f\p\ALI_Studio_Pro_Design4_4.6.0\04_Adaptive_Hybrid\backend/model/weights_manager.py`
- **الحجم:** 9071 بايت (8.9 KB)
- **الامتداد:** `.py`

```python
# -*- coding: utf-8 -*-
"""Real model/weight lifecycle for ALI AI 2.0.

Users drop checkpoints/adapters/GGUF files into the UI or ``models/inbox``.
ALI validates them, assigns a deterministic destination, writes a manifest and
registers the artifact. It never fabricates weights and never overwrites an
active model in place.
"""
from __future__ import annotations

from pathlib import Path
from typing import Any, Iterable
import json
import shutil
import time
import uuid

from model.artifacts import ArtifactManifest, atomic_json_write, sha256_path
from model.ali_lm import AliConfig
from model.importer import inspect_weights, import_compatible
from model.registry import ModelRegistry


class WeightsManager:
    """Centralized artifact store.

    Layout:
        models/
          inbox/
          quarantine/
          base/<name>/<version>/
          adapters/<name>/<version>/
          merged/<name>/<version>/
          gguf/<name>/<version>/
          tokenizers/<name>/<version>/
    """

    TYPES = ("base", "adapter", "merged", "gguf")

    def __init__(self, root: str | Path, registry: ModelRegistry | None = None):
        self.root = Path(root)
        self.models_root = self.root / "models"
        self.registry = registry or ModelRegistry(self.models_root / "models.sqlite3")
        for rel in ("inbox", "quarantine", "base", "adapters", "merged", "gguf", "tokenizers"):
            (self.models_root / rel).mkdir(parents=True, exist_ok=True)

    # Backward-compatible helpers
    def list_models(self):
        return [x["version"] for x in self.registry.list("ALI")]

    def get_model_info(self, model_name):
        rows = self.registry.list("ALI")
        return next((r for r in rows if r["version"] == model_name), None)

    def inspect(self, source: str | Path, config: AliConfig | None = None) -> dict[str, Any]:
        p = Path(source).resolve()
        if p.is_file() and p.suffix.lower() == ".gguf":
            from tools.gguf import GGUFManager
            validation = GGUFManager().validate(p)
            return {
                "kind": "gguf",
                "path": str(p),
                "compatible": bool(validation.get("valid")),
                "size": p.stat().st_size,
                "validation": validation,
                "sha256": sha256_path(p),
            }
        if self._looks_like_adapter(p):
            return self._inspect_adapter(p)
        report = inspect_weights(p, config)
        data = report.to_dict()
        data["kind"] = "base"
        data["sha256"] = sha256_path(p)
        return data

    def install(
        self,
        source: str | Path,
        *,
        artifact_type: str | None = None,
        name: str = "ALI",
        version: str | None = None,
        config: AliConfig | None = None,
        base_version: str = "",
        dataset_hash: str = "",
        tokenizer_hash: str = "",
        training: dict[str, Any] | None = None,
        evaluation: dict[str, Any] | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        src = Path(source).resolve()
        if not src.exists():
            raise FileNotFoundError(src)

        info = self.inspect(src, config)
        kind = artifact_type or info["kind"]
        if kind not in self.TYPES:
            raise ValueError(f"Unsupported artifact type: {kind}")

        if not info.get("compatible", False):
            raise ValueError("Artifact is not compatible with the active ALI architecture: " +
                             json.dumps(info, ensure_ascii=False)[:6000])

        safe_name = self._safe(name or "ALI")
        ver = version or time.strftime("%Y%m%d-%H%M%S") + "-" + uuid.uuid4().hex[:6]
        destination = self.models_root / {
            "base": "base",
            "adapter": "adapters",
            "merged": "merged",
            "gguf": "gguf",
        }[kind] / safe_name / ver
        destination.parent.mkdir(parents=True, exist_ok=True)

        staging = destination.with_name(destination.name + ".staging")
        if staging.exists():
            shutil.rmtree(staging)
        if src.is_dir():
            shutil.copytree(src, staging)
        else:
            staging.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, staging / src.name)

        manifest = ArtifactManifest(
            artifact_id=f"{safe_name}:{ver}",
            artifact_type=kind,
            name=safe_name,
            version=ver,
            source="user-import",
            lineage={
                "base_version": base_version,
                "dataset_hash": dataset_hash,
                "tokenizer_hash": tokenizer_hash,
            },
            training=training or {},
            evaluation=evaluation or {},
            compatibility={
                "report": info,
            },
            metadata=metadata or {},
        )
        manifest.finalize(staging)
        manifest.write(staging / "manifest.json")

        if destination.exists():
            shutil.rmtree(destination)
        staging.replace(destination)

        manifest.path = str(destination.resolve())
        # The manifest contains its pre-move hash, which is fine for contents;
        # rewrite after the atomic move so path/sha are canonical.
        manifest.finalize(destination)
        manifest.write(destination / "manifest.json")

        reg_name = safe_name if kind in {"base", "merged"} else f"{safe_name}-{kind}"
        reg_meta = {
            "artifact_type": kind,
            "status": "candidate",
            "base_version": base_version,
            "checkpoint": str(destination if kind != "gguf" else ""),
            "hf_dir": str(destination if kind in {"base", "merged"} else ""),
            "gguf": str(destination) if kind == "gguf" else "",
            "adapter": str(destination) if kind == "adapter" else "",
            "dataset_hash": dataset_hash,
            "tokenizer_hash": tokenizer_hash,
            "artifact_hash": manifest.sha256,
            "train_config": training or {},
            "eval": evaluation or {},
        }
        self.registry.register(reg_name, ver, **reg_meta)
        return {
            "installed": True,
            "type": kind,
            "version": ver,
            "path": str(destination),
            "manifest": manifest.to_dict(),
            "registry": reg_meta,
        }

    def verify(self, path: str | Path) -> dict[str, Any]:
        p = Path(path).resolve()
        m = p / "manifest.json"
        if not m.exists():
            return {"valid": False, "reason": "manifest_missing", "path": str(p)}
        return ArtifactManifest.load(m).verify()

    def quarantine(self, source: str | Path, reason: str) -> dict[str, Any]:
        src = Path(source).resolve()
        dest = self.models_root / "quarantine" / f"{src.stem}-{time.strftime('%Y%m%d-%H%M%S')}"
        dest.parent.mkdir(parents=True, exist_ok=True)
        if src.is_dir():
            shutil.copytree(src, dest)
        else:
            shutil.copy2(src, dest)
        atomic_json_write(dest.with_suffix(".reason.json"), {
            "source": str(src), "reason": reason, "sha256": sha256_path(src),
            "created_at": time.time(),
        })
        return {"quarantined": True, "path": str(dest), "reason": reason}

    def scan_inbox(self) -> list[dict[str, Any]]:
        inbox = self.models_root / "inbox"
        rows = []
        for p in sorted(inbox.iterdir()):
            try:
                rows.append(self.inspect(p))
            except Exception as exc:
                rows.append({"path": str(p), "compatible": False, "error": str(exc)})
        return rows

    @staticmethod
    def _safe(value: str) -> str:
        clean = "".join(ch if ch.isalnum() or ch in "._-" else "_" for ch in value.strip())
        return clean or "ALI"

    @staticmethod
    def _looks_like_adapter(path: Path) -> bool:
        if path.is_dir():
            return any((path / n).exists() for n in ("adapter_config.json", "adapter_model.safetensors", "adapter_model.pt"))
        return "adapter" in path.name.lower()

    @staticmethod
    def _inspect_adapter(path: Path) -> dict[str, Any]:
        if path.is_dir():
            cfg = path / "adapter_config.json"
            data = json.loads(cfg.read_text(encoding="utf-8")) if cfg.exists() else {}
            tensors = path / "adapter_model.safetensors"
            if not tensors.exists():
                tensors = path / "adapter_model.pt"
            if not tensors.exists():
                raise FileNotFoundError("adapter_model.safetensors/pt not found")
            return {
                "kind": "adapter",
                "path": str(path),
                "compatible": True,
                "config": data,
                "sha256": sha256_path(path),
                "size": tensors.stat().st_size,
            }
        return {
            "kind": "adapter",
            "path": str(path),
            "compatible": False,
            "error": "A standalone adapter file needs its adapter directory/config.",
        }
```

---

### `174/588` `backend/models/active/ALI-Bootstrap-v2.5/ali_metadata.json`

- **المسار الكامل:** `F:\1f\p\ALI_Studio_Pro_Design4_4.6.0\04_Adaptive_Hybrid\backend/models/active/ALI-Bootstrap-v2.5/ali_metadata.json`
- **الحجم:** 5090 بايت (5.0 KB)
- **الامتداد:** `.json`

```json
{
  "training_result": {
    "checkpoint": "/mnt/data/ALI_AI_2.5_BUILD/models/bootstrap/runs/final-000020",
    "global_step": 20,
    "steps": 20,
    "loss": 6.552404403686523,
    "val_loss": 6.7709697167078655,
    "best_val": 6.7709697167078655,
    "tokens_seen": 31849,
    "tokens_per_sec": 1923.38,
    "history": [
      {
        "step": 1,
        "epoch": 1,
        "loss": 8.209212303161621,
        "lr": 2.9999999999999997e-05,
        "tokens_seen": 1590,
        "tokens_per_sec": 1966.97,
        "rank": 0,
        "world_size": 1
      },
      {
        "step": 2,
        "epoch": 1,
        "loss": 8.106521606445312,
        "lr": 4.4999999999999996e-05,
        "tokens_seen": 3215,
        "tokens_per_sec": 1931.49,
        "rank": 0,
        "world_size": 1
      },
      {
        "step": 3,
        "epoch": 1,
        "loss": 8.086342811584473,
        "lr": 5.9999999999999995e-05,
        "tokens_seen": 4834,
        "tokens_per_sec": 1953.57,
        "rank": 0,
        "world_size": 1
      },
      {
        "step": 4,
        "epoch": 1,
        "loss": 8.063976287841797,
        "lr": 7.5e-05,
        "tokens_seen": 6417,
        "tokens_per_sec": 2015.16,
        "rank": 0,
        "world_size": 1
      },
      {
        "step": 5,
        "epoch": 1,
        "loss": 7.897658824920654,
        "lr": 8.999999999999999e-05,
        "tokens_seen": 7941,
        "tokens_per_sec": 1999.23,
        "rank": 0,
        "world_size": 1
      },
      {
        "step": 6,
        "epoch": 1,
        "loss": 7.952786922454834,
        "lr": 0.00010499999999999999,
        "tokens_seen": 9452,
        "tokens_per_sec": 2046.73,
        "rank": 0,
        "world_size": 1
      },
      {
        "step": 7,
        "epoch": 1,
        "loss": 7.802600383758545,
        "lr": 0.00011999999999999999,
        "tokens_seen": 10960,
        "tokens_per_sec": 2059.69,
        "rank": 0,
        "world_size": 1
      },
      {
        "step": 8,
        "epoch": 1,
        "loss": 7.57593297958374,
        "lr": 0.000135,
        "tokens_seen": 12557,
        "tokens_per_sec": 2020.53,
        "rank": 0,
        "world_size": 1
      },
      {
        "step": 9,
        "epoch": 1,
        "loss": 7.715093612670898,
        "lr": 0.00015,
        "tokens_seen": 14112,
        "tokens_per_sec": 1988.48,
        "rank": 0,
        "world_size": 1
      },
      {
        "step": 10,
        "epoch": 1,
        "loss": 7.807801723480225,
        "lr": 0.000165,
        "tokens_seen": 15771,
        "tokens_per_sec": 2006.42,
        "rank": 0,
        "world_size": 1
      },
      {
        "step": 11,
        "epoch": 1,
        "loss": 7.807729721069336,
        "lr": 0.00017999999999999998,
        "tokens_seen": 17392,
        "tokens_per_sec": 2012.49,
        "rank": 0,
        "world_size": 1
      },
      {
        "step": 12,
        "epoch": 1,
        "loss": 7.7083258628845215,
        "lr": 0.000195,
        "tokens_seen": 19006,
        "tokens_per_sec": 1999.06,
        "rank": 0,
        "world_size": 1
      },
      {
        "step": 13,
        "epoch": 1,
        "loss": 7.548254489898682,
        "lr": 0.00020999999999999998,
        "tokens_seen": 20716,
        "tokens_per_sec": 2028.85,
        "rank": 0,
        "world_size": 1
      },
      {
        "step": 14,
        "epoch": 1,
        "loss": 7.609013080596924,
        "lr": 0.000225,
        "tokens_seen": 22397,
        "tokens_per_sec": 2029.81,
        "rank": 0,
        "world_size": 1
      },
      {
        "step": 15,
        "epoch": 1,
        "loss": 7.591832160949707,
        "lr": 0.00023999999999999998,
        "tokens_seen": 23995,
        "tokens_per_sec": 2017.68,
        "rank": 0,
        "world_size": 1
      },
      {
        "step": 16,
        "epoch": 1,
        "loss": 7.590664863586426,
        "lr": 0.00025499999999999996,
        "tokens_seen": 25539,
        "tokens_per_sec": 1998.47,
        "rank": 0,
        "world_size": 1
      },
      {
        "step": 17,
        "epoch": 1,
        "loss": 7.463057041168213,
        "lr": 0.00027,
        "tokens_seen": 27059,
        "tokens_per_sec": 1988.59,
        "rank": 0,
        "world_size": 1
      },
      {
        "step": 18,
        "epoch": 1,
        "loss": 6.517185211181641,
        "lr": 0.000285,
        "tokens_seen": 28712,
        "tokens_per_sec": 1998.1,
        "rank": 0,
        "world_size": 1
      },
      {
        "step": 19,
        "epoch": 1,
        "loss": 6.463642120361328,
        "lr": 0.0003,
        "tokens_seen": 30310,
        "tokens_per_sec": 2006.14,
        "rank": 0,
        "world_size": 1
      },
      {
        "step": 20,
        "epoch": 1,
        "loss": 6.552404403686523,
        "lr": 0.0003,
        "tokens_seen": 31849,
        "tokens_per_sec": 2006.75,
        "rank": 0,
        "world_size": 1
      }
    ]
  },
  "scale": "micro",
  "train_mode": "full",
  "parameter_count": 3607872,
  "source": "ALI Studio trained-from-scratch",
  "architecture": "LlamaForCausalLM"
}
```

---

### `175/588` `backend/models/active/ALI-Bootstrap-v2.5/config.json`

- **المسار الكامل:** `F:\1f\p\ALI_Studio_Pro_Design4_4.6.0\04_Adaptive_Hybrid\backend/models/active/ALI-Bootstrap-v2.5/config.json`
- **الحجم:** 559 بايت (0.5 KB)
- **الامتداد:** `.json`

```json
{
  "vocab_size": 3247,
  "hidden_size": 192,
  "intermediate_size": 768,
  "num_hidden_layers": 4,
  "num_attention_heads": 6,
  "num_key_value_heads": 6,
  "max_position_embeddings": 128,
  "rms_norm_eps": 1e-06,
  "rope_theta": 10000.0,
  "attention_dropout": 0.0,
  "bos_token_id": 1,
  "eos_token_id": 2,
  "pad_token_id": 3,
  "model_type": "llama",
  "architectures": [
    "LlamaForCausalLM"
  ],
  "hidden_act": "silu",
  "initializer_range": 0.02,
  "use_cache": true,
  "use_sdpa": true,
  "tie_word_embeddings": false,
  "torch_dtype": "float32"
}
```

---

### `176/588` `backend/models/active/ALI-Bootstrap-v2.5/MODEL_CARD.json`

- **المسار الكامل:** `F:\1f\p\ALI_Studio_Pro_Design4_4.6.0\04_Adaptive_Hybrid\backend/models/active/ALI-Bootstrap-v2.5/MODEL_CARD.json`
- **الحجم:** 595 بايت (0.6 KB)
- **الامتداد:** `.json`

```json
{
  "name": "ALI-Bootstrap-v2.5",
  "version": "2.5.0-bootstrap-micro",
  "type": "hf_local",
  "status": "active-bootstrap",
  "training": "from-scratch micro model",
  "steps": 20,
  "purpose": [
    "desktop startup smoke test",
    "local development",
    "training pipeline validation"
  ],
  "quality_note": "This is a functional tiny bootstrap checkpoint, not a production-quality general assistant model.",
  "source_dataset": "data/training/device_p50/chat_train.jsonl",
  "validation_dataset": "data/training/device_p50/chat_validation.jsonl",
  "created_by": "ALI AI build process"
}
```

---

### `177/588` `backend/models/active/ALI-Bootstrap-v2.5/special_tokens_map.json`

- **المسار الكامل:** `F:\1f\p\ALI_Studio_Pro_Design4_4.6.0\04_Adaptive_Hybrid\backend/models/active/ALI-Bootstrap-v2.5/special_tokens_map.json`
- **الحجم:** 202 بايت (0.2 KB)
- **الامتداد:** `.json`

```json
{
  "bos_token": "<s>",
  "eos_token": "</s>",
  "pad_token": "<pad>",
  "unk_token": "<unk>",
  "additional_special_tokens": [
    "<|system|>",
    "<|user|>",
    "<|assistant|>",
    "<|eot|>"
  ]
}
```

---

### `178/588` `backend/models/active/ALI-Bootstrap-v2.5/tokenizer_config.json`

- **المسار الكامل:** `F:\1f\p\ALI_Studio_Pro_Design4_4.6.0\04_Adaptive_Hybrid\backend/models/active/ALI-Bootstrap-v2.5/tokenizer_config.json`
- **الحجم:** 313 بايت (0.3 KB)
- **الامتداد:** `.json`

```json
{
  "model_type": "llama",
  "add_bos_token": true,
  "add_eos_token": false,
  "bos_token": "<s>",
  "eos_token": "</s>",
  "pad_token": "<pad>",
  "unk_token": "<unk>",
  "chat_template": "<s>{% for message in messages %}<|{{ message['role'] }}|>\n{{ message['content'] }}<|eot|>\n{% endfor %}<|assistant|>\n"
}
```

---

### `179/588` `backend/models/active/ALI-v1/ali_metadata.json`

- **المسار الكامل:** `F:\1f\p\ALI_Studio_Pro_Design4_4.6.0\04_Adaptive_Hybrid\backend/models/active/ALI-v1/ali_metadata.json`
- **الحجم:** 6376 بايت (6.2 KB)
- **الامتداد:** `.json`

```json
{
  "run_id": "20261004-224649-233144",
  "stage": "lora",
  "dataset_hash": "406ccb419f45bc20acc61368b41bb3f31451370bcfd8217c2d3d565f114d8a8d",
  "tokenizer_hash": "5e6970f5f6bac2d299df737015ef5006310fe2a153a2d44c6e6f477ed10565e1",
  "pipeline_config": {
    "name": "ALI",
    "stage": "lora",
    "scale": "small",
    "train_path": "models/runs/ALI-v1-20261004-224649-233144/training/train_new.jsonl",
    "validation_path": "models/runs/ALI-v1-20261004-224649-233144/training/stable_validation.jsonl",
    "tokenizer_inputs": null,
    "tokenizer_vocab_size": 4096,
    "base_checkpoint": "models/active/ALI-Bootstrap-v2.5",
    "resume_checkpoint": "",
    "max_steps": 0,
    "epochs": 1,
    "max_seq_len": 256,
    "batch_size": 1,
    "grad_accum": 16,
    "learning_rate": 0.0003,
    "device": "cpu",
    "lora_rank": 8,
    "lora_alpha": 16.0,
    "lora_dropout": 0.05,
    "curriculum": true,
    "distributed_backend": "auto",
    "world_size": 1
  },
  "kca_schema": "3.0",
  "kca_registry_hash": "9ed24e57ea920e5ffa8b0746db0283191d240587d5e77753f1fcf6e8a66a713a",
  "result": {
    "checkpoint": "models/runs/ALI-v1-20261004-224649-233144/checkpoints/final-000013",
    "global_step": 13,
    "steps": 13,
    "loss": 7.509772777557373,
    "val_loss": 6.771079770723978,
    "best_val": 6.771079770723978,
    "tokens_seen": 26624,
    "tokens_per_sec": 1605.26,
    "history": [
      {
        "step": 1,
        "total_steps": 13,
        "epoch": 1,
        "loss": 7.530920028686523,
        "lr": 2.9999999999999997e-05,
        "tokens_seen": 2048,
        "tokens_per_sec": 1581.13,
        "samples_seen": 16,
        "total_samples": 195,
        "elapsed_sec": 1.3,
        "eta_sec": 15.54,
        "rank": 0,
        "world_size": 1
      },
      {
        "step": 2,
        "total_steps": 13,
        "epoch": 1,
        "loss": 7.573794841766357,
        "lr": 4.4999999999999996e-05,
        "tokens_seen": 4096,
        "tokens_per_sec": 1743.49,
        "samples_seen": 32,
        "total_samples": 195,
        "elapsed_sec": 2.35,
        "eta_sec": 12.92,
        "rank": 0,
        "world_size": 1
      },
      {
        "step": 3,
        "total_steps": 13,
        "epoch": 1,
        "loss": 7.536900520324707,
        "lr": 5.9999999999999995e-05,
        "tokens_seen": 6144,
        "tokens_per_sec": 1665.7,
        "samples_seen": 48,
        "total_samples": 195,
        "elapsed_sec": 3.69,
        "eta_sec": 12.3,
        "rank": 0,
        "world_size": 1
      },
      {
        "step": 4,
        "total_steps": 13,
        "epoch": 1,
        "loss": 7.3177103996276855,
        "lr": 7.5e-05,
        "tokens_seen": 8192,
        "tokens_per_sec": 1697.2,
        "samples_seen": 64,
        "total_samples": 195,
        "elapsed_sec": 4.83,
        "eta_sec": 10.86,
        "rank": 0,
        "world_size": 1
      },