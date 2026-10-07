from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
SOURCE_DIR = ROOT / 'source-export'
OUT_DIR = ROOT / 'restored-project'

PARTS = sorted(SOURCE_DIR.glob('part-*.md'))
if not PARTS:
    raise SystemExit('No source-export parts found.')

text = '\n'.join(p.read_text(encoding='utf-8') for p in PARTS)
marker = re.compile(r'^###\\s+`(\\d+)/(\\d+)`\\s+`([^\\n]+?)`\\s*$', re.M)
matches = list(marker.finditer(text))
if not matches:
    raise SystemExit('No file-content markers found.')

declared_total = int(matches[0].group(2))
if declared_total != len(matches):
    raise SystemExit(f'File marker count mismatch: declared {declared_total}, found {len(matches)}.')

OUT_DIR.mkdir(parents=True, exist_ok=True)
written = 0
for i, m in enumerate(matches):
    rel = Path(m.group(3))
    if rel.is_absolute() or '..' in rel.parts:
        raise SystemExit(f'Unsafe output path: {rel}')
    end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
    content = text[m.end():end]
    content = re.sub(r'^\\s*---\\s*\\n', '', content, count=1)
    content = content.rstrip('\\n') + '\\n'
    dst = OUT_DIR / rel
    dst.parent.mkdir(parents=True, exist_ok=True)
    dst.write_text(content, encoding='utf-8', newline='')
    written += 1

print(f'Restored {written} files into: {OUT_DIR}')