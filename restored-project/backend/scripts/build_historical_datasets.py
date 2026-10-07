# -*- coding: utf-8 -*-
"""Build verified historical/cumulative conversation datasets from project sources.

This script only uses explicit User/Assistant training material already present in the
project source bundle. It never treats arbitrary docs or source code as training data.
"""
from __future__ import annotations
from pathlib import Path
import hashlib, json, re, shutil, sys, time

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from training.continuous_learning import ContinuousLearningManager
from training.generation_lineage import sample_id, merge_jsonl_unique, sha256_file

SOURCES = {
    "v1": [
        ROOT / "training" / "updates" / "v1" / "docs" / "CONVERSATIONS_V1.md",
        ROOT / "training" / "examples" / "ALI_Professional_QA_P50_V1.md",
    ],
    "v2": [
        ROOT / "artifacts" / "continuous_learning" / "validated" / "06ba230d8cf9b575_ALI_Conversation_Training_Core_V2.md",
        ROOT / "artifacts" / "continuous_learning" / "validated" / "094791a57c8c0572_ALI_behavior_training_V2_import_sample.md",
        ROOT / "training" / "examples" / "ALI_Professional_QA_P50_V2.md",
    ],
    "v3": [
        ROOT / "training" / "examples" / "ALI_MASTER_TRAINING_4.5.2.md",
    ],
    "v4": [
        ROOT / "artifacts" / "continuous_learning" / "validated" / "d7b0aaf9a09cff6b_ALI_Behavior_Training_V4_User_Understanding_Import_Ready.md",
        ROOT / "data" / "training" / "testdata" / "ALI_User_Understanding_Bundle_V4.md",
    ],
}

OUT = ROOT / "models" / "generations"


def to_rows(path: Path, manager: ContinuousLearningManager, generation: str):
    samples, _safe, warnings = manager.parse_file(path)
    rows = []
    for pair in samples:
        messages = [{"role": str(m.get("role", "user")), "content": str(m.get("content", "")).strip()} for m in pair]
        if not any(m["role"] == "user" and m["content"] for m in messages):
            continue
        if not any(m["role"] == "assistant" and m["content"] for m in messages):
            continue
        sid = sample_id({"messages": messages})
        rows.append({
            "sample_id": sid,
            "id": sid,
            "messages": messages,
            "provenance": {
                "source_file": str(path.relative_to(ROOT)),
                "historical_generation": generation,
                "parser": "ContinuousLearningManager.parse_file",
                "approved": True,
                "built_at": time.time(),
            },
        })
    return rows, warnings


def write_rows(path: Path, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")


def main():
    manager = ContinuousLearningManager(ROOT)
    reports = {}
    for generation, sources in SOURCES.items():
        gdir = OUT / generation
        (gdir / "delta").mkdir(parents=True, exist_ok=True)
        (gdir / "cumulative").mkdir(parents=True, exist_ok=True)
        all_rows = []
        source_reports = []
        for src in sources:
            if not src.exists():
                source_reports.append({"source": str(src.relative_to(ROOT)), "exists": False, "samples": 0})
                continue
            rows, warnings = to_rows(src, manager, generation)
            all_rows.extend(rows)
            source_reports.append({"source": str(src.relative_to(ROOT)), "exists": True, "samples": len(rows), "warnings": warnings})
        raw = gdir / "delta" / "raw.jsonl"
        write_rows(raw, all_rows)
        delta = gdir / "delta" / "train.jsonl"
        dmeta = merge_jsonl_unique([raw], delta)
        try: raw.unlink()
        except Exception: pass

        parent = "" if generation == "v1" else f"v{int(generation[1:]) - 1}"
        parent_cum = OUT / parent / "cumulative" / "train.jsonl" if parent else None
        cumulative = gdir / "cumulative" / "train.jsonl"
        inputs = [parent_cum, delta] if parent_cum else [delta]
        cmeta = merge_jsonl_unique([p for p in inputs if p and Path(p).exists()], cumulative)
        report = {
            "generation": generation,
            "parent_generation": parent or None,
            "source_reports": source_reports,
            "delta_samples": dmeta["written_rows"],
            "delta_duplicates_removed": dmeta["duplicates_removed"],
            "delta_hash": dmeta["dataset_hash"],
            "cumulative_samples": cmeta["written_rows"],
            "cumulative_duplicates_removed": cmeta["duplicates_removed"],
            "cumulative_hash": cmeta["dataset_hash"],
            "historical_model_weights_available": False,
            "historical_model_lineage_status": "data_reconstructed_only",
            "created_at": time.time(),
        }
        (gdir / "cumulative_report.json").write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
        lineage = {
            "schema_version": 2,
            "generation": generation,
            "parent_generation": parent,
            "ancestors": [f"v{i}" for i in range(1, int(generation[1:]) + 1)],
            "delta_dataset": {"path": str(delta), "sha256": dmeta["dataset_hash"], "samples": dmeta["written_rows"]},
            "cumulative_dataset": {"path": str(cumulative), "sha256": cmeta["dataset_hash"], "samples": cmeta["written_rows"]},
            "historical_model_status": "not_reconstructed_from_missing_binary_weights",
            "created_at": time.time(),
        }
        (gdir / "lineage.json").write_text(json.dumps(lineage, ensure_ascii=False, indent=2), encoding="utf-8")
        (gdir / "generation.json").write_text(json.dumps({**lineage, "status": "dataset-ready"}, ensure_ascii=False, indent=2), encoding="utf-8")
        reports[generation] = report
    print(json.dumps(reports, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    raise SystemExit(main())
