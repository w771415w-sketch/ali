#!/usr/bin/env python
"""Source/release gate for ALI AI 2.5.

The checker is valid for a source-only bundle: large binary checkpoints are optional.
Set ALI_REQUIRE_ARTIFACTS=1 when a deployment package is expected to carry trained artifacts.
"""
from __future__ import annotations

import hashlib
import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def sha_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def main() -> int:
    report = {"ok": True, "checks": []}

    def check(name: str, ok: bool, detail: str = "", *, required: bool = True) -> None:
        entry = {"name": name, "ok": bool(ok), "detail": detail, "required": required}
        if not required and not ok:
            entry["status"] = "skipped"
            entry["ok"] = True
        report["checks"].append(entry)
        if required and not ok:
            report["ok"] = False

    required = [
        "model/ali_lm.py", "training/trainer.py", "training/pipeline.py",
        "tokenizer/manager.py", "model/artifacts.py", "model/weights_manager.py",
        "inference/engine.py", "knowledge/rag.py", "memory/conversations.py",
        "core/runtime.py", "core/tool_protocol.py", "core/session_store.py",
        "ui/theme.py", "ui/widgets.py", "ali_ai.py", "tools/gguf.py", "training/accumulated_updates.py", "ui/activity.py",
    ]
    for rel in required:
        check("file:" + rel, (ROOT / rel).exists())

    try:
        project = json.loads((ROOT / "PROJECT_VERSION.json").read_text(encoding="utf-8"))
        check("project version", project.get("version") == "2.5.0", json.dumps(project, ensure_ascii=False))
        check("previous project", project.get("previous_project") == "ALI Studio Pro 3.0.0")
        check("previous release", project.get("previous_release") == "2.0.0")
    except Exception as exc:
        check("project identity", False, repr(exc))

    # Validate the dataset uniqueness contract without requiring model binaries.
    corpus = ROOT / "data/seed/conversations_curriculum.jsonl"
    if corpus.exists():
        try:
            rows = [json.loads(x) for x in corpus.read_text(encoding="utf-8").splitlines() if x.strip()]
            ids = [r.get("id") for r in rows]
            hashes = [sha_text("\n".join(
                f"{m.get('role','')}:{str(m.get('content','')).strip()}"
                for m in r.get('messages', []) if isinstance(m, dict)
            )) for r in rows]
            check("conversation corpus nonempty", bool(rows), str(len(rows)))
            check("conversation ids unique", len(ids) == len(set(ids)))
            check("conversation content unique", len(hashes) == len(set(hashes)))
        except Exception as exc:
            check("conversation dataset validation", False, repr(exc))
    else:
        check("conversation corpus optional", True, "large training datasets are excluded from the Markdown source bundle", required=False)

    try:
        from runtime.hardware import detect, model_profile, training_profile
        hw = detect(); mp = model_profile(hw); tp = training_profile(hw)
        check("hardware detector", hw.cpu_cores >= 1)
        check("2GB-safe profile", mp["layers"] <= 8 and mp["hidden"] <= 320)
        check("CPU-safe training", tp["batch_size"] == 1)
    except Exception as exc:
        check("hardware detector", False, repr(exc))

    # Large trained artifacts are intentionally optional in a source bundle.
    artifact_paths = {
        "conversation checkpoint": ROOT / "models/checkpoints/ALI-Conversation-v0.4",
        "model registry": ROOT / "artifacts/models.sqlite3",
        "LoRA adapter": ROOT / "models/lora/ALI-Conversation-v0.4-corrected/adapter_model.safetensors",
    }
    require_artifacts = os.environ.get("ALI_REQUIRE_ARTIFACTS") == "1"
    for name, path in artifact_paths.items():
        check(name, path.exists(), str(path), required=require_artifacts)

    out = ROOT / "artifacts/release_check.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if report["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
