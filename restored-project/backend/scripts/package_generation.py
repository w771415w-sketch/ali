# -*- coding: utf-8 -*-
"""Build a portable, self-contained ALI generation release package."""
from __future__ import annotations
import argparse
import json
import shutil
import time
from pathlib import Path
import sys
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from model.registry import file_hash
from training.generation_lineage import generation_manifest_path, verify_lineage

def resolve_path(value):
    if not value:
        return None
    p = Path(str(value))
    return p if p.is_absolute() else ROOT / p

def copy_path(src: Path, dst: Path):
    if src.is_dir():
        shutil.copytree(src, dst)
    else:
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('--generation', required=True)
    ap.add_argument('--output', default='')
    args = ap.parse_args()
    generation = str(args.generation)
    check = verify_lineage(ROOT / 'models', generation)
    if not check.get('valid'):
        print(json.dumps(check, ensure_ascii=False, indent=2))
        return 2
    manifest_path = generation_manifest_path(ROOT / 'models', generation)
    data = json.loads(manifest_path.read_text(encoding='utf-8'))
    out = Path(args.output) if args.output else ROOT / 'releases' / f'ALI-{generation}-Package'
    if not out.is_absolute():
        out = ROOT / out
    if out.exists():
        shutil.rmtree(out)
    for directory in ('model', 'manifests', 'datasets', 'evaluation'):
        (out / directory).mkdir(parents=True, exist_ok=True)
    artifacts = data.get('artifacts') or {}
    copied = []
    for key in ('gguf_q4_k_m', 'gguf_f16', 'merged_hf'):
        src = resolve_path(artifacts.get(key))
        if src and src.exists():
            dest = out / 'model' / src.name
            copy_path(src, dest)
            copied.append({'kind': key, 'source': str(src), 'destination': str(dest.relative_to(out))})
            if key == 'gguf_q4_k_m':
                break
    for source, target in (
        (manifest_path, out / 'manifests' / 'generation.json'),
        (manifest_path.parent / 'lineage.json', out / 'manifests' / 'lineage.json'),
        (manifest_path.parent / 'cumulative_report.json', out / 'datasets' / 'cumulative_report.json'),
    ):
        if source.exists():
            shutil.copy2(source, target)
    for key, target in (('cumulative_dataset', 'cumulative_train.jsonl'), ('delta_dataset', 'delta_train.jsonl')):
        value = data.get(key) or {}
        value = value.get('path') if isinstance(value, dict) else value
        src = resolve_path(value)
        if src and src.exists():
            shutil.copy2(src, out / 'datasets' / target)
    eval_dir = manifest_path.parent / 'evaluation'
    if eval_dir.exists():
        for src in eval_dir.glob('*.jsonl'):
            shutil.copy2(src, out / 'evaluation' / src.name)
    checksums = {}
    for file in sorted(out.rglob('*')):
        if file.is_file():
            checksums[str(file.relative_to(out)).replace('\\', '/')] = file_hash(file)
    (out / 'manifests' / 'checksums.json').write_text(json.dumps(checksums, ensure_ascii=False, indent=2, sort_keys=True) + '\n', encoding='utf-8')
    parent = data.get('parent_generation', '')
    samples = (data.get('cumulative_dataset') or {}).get('samples', 0)
    (out / 'README.md').write_text(
        '# ALI {} Package\n\nIndependent ALI generation package.\n\nGeneration: {}\nParent: {}\nCumulative samples: {}\n\nArchived generations are not runtime dependencies.\n'.format(generation, generation, parent, samples),
        encoding='utf-8',
    )
    print(json.dumps({'ok': True, 'generation': generation, 'output': str(out), 'files': len(checksums), 'copied': copied, 'created_at': time.time()}, ensure_ascii=False, indent=2))
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
