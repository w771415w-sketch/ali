# -*- coding: utf-8 -*-
from __future__ import annotations
import argparse
import json
import time
from pathlib import Path
import sys
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from training.generation_lineage import build_ancestors

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('--dry-run', action='store_true')
    args = ap.parse_args()
    root = ROOT / 'models'
    changes = []
    generations = root / 'generations'
    files = sorted(generations.glob('v*/generation.json')) if generations.exists() else []
    for path in files:
        try:
            data = json.loads(path.read_text(encoding='utf-8'))
        except Exception:
            continue
        generation = str(data.get('generation') or path.parent.name)
        before = json.dumps(data, ensure_ascii=False, sort_keys=True)
        data['schema_version'] = max(2, int(data.get('schema_version') or 0))
        parent = str(data.get('parent_generation') or data.get('base_version') or '')
        data['parent_generation'] = parent
        data['ancestors'] = build_ancestors(root, generation)
        if data.get('base_version') and 'historical_base_version' not in data:
            data['historical_base_version'] = data.get('base_version')
        after = json.dumps(data, ensure_ascii=False, sort_keys=True)
        if before != after:
            changes.append({'generation': generation, 'path': str(path), 'parent': parent, 'ancestors': data['ancestors']})
            if not args.dry_run:
                path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({'ok': True, 'dry_run': args.dry_run, 'changes': changes, 'completed_at': time.time()}, ensure_ascii=False, indent=2))
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
