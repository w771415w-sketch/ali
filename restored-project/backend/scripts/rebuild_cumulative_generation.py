# -*- coding: utf-8 -*-
from __future__ import annotations
import argparse
import json
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from training.generation_lineage import build_cumulative_dataset

ap = argparse.ArgumentParser()
ap.add_argument('--generation', required=True)
ap.add_argument('--delta', default='')
ap.add_argument('--output', default='')
ap.add_argument('--parent', default='')
ap.add_argument('--dry-run', action='store_true')
args = ap.parse_args()
models_root = ROOT / 'models'
out = Path(args.output) if args.output else models_root / 'generations' / args.generation / 'cumulative' / 'train.jsonl'
if args.dry_run:
    print(json.dumps({'ok': True, 'dry_run': True, 'generation': args.generation, 'output': str(out)}, ensure_ascii=False, indent=2))
    raise SystemExit(0)
result = build_cumulative_dataset(models_root, args.generation, args.delta or None, out, parent_generation=args.parent or None)
print(json.dumps(result, ensure_ascii=False, indent=2))
