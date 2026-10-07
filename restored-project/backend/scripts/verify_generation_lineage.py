# -*- coding: utf-8 -*-
from __future__ import annotations
import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from training.generation_lineage import verify_lineage

ap = argparse.ArgumentParser()
ap.add_argument('--generation', required=True)
args = ap.parse_args()
result = verify_lineage(ROOT / 'models', args.generation)
print(json.dumps(result, ensure_ascii=False, indent=2))
sys.exit(0 if result.get('valid') else 1)
