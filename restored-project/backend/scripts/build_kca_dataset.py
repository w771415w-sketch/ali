#!/usr/bin/env python
from __future__ import annotations
import argparse
from pathlib import Path
import sys
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from data_engine.kca_dataset import build_kca_dataset

def main(argv=None) -> int:
    p = argparse.ArgumentParser(description="Build enriched ALI KCA training dataset")
    p.add_argument("inputs", nargs="+", help="conversation JSONL files")
    p.add_argument("--output", default="data/training/kca_train.jsonl")
    p.add_argument("--min-quality", type=float, default=.6)
    a = p.parse_args(argv)
    print(build_kca_dataset(a.inputs, ROOT / a.output, a.min_quality))
    return 0
if __name__ == "__main__":
    raise SystemExit(main())
