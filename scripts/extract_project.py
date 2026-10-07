from pathlib import Path
import re
import shutil

ROOT=Path(__file__).resolve().parents[1]
SOURCE_DIR=ROOT/'source-export'
OUT_DIR=ROOT/'restored-project'
PARTS=sorted(SOURCE_DIR.glob('part-*.md'))
if not PARTS: raise SystemExit('No source-export parts found.')
text='\n'.join(p.read_text(encoding='utf-8') for p in PARTS)
marker=re.compile(r'^###\s+`(\d+)/(\d+)`\s+`([^\n]+?)`\s*$',re.M)
matches=list(marker.finditer(text))
if not matches: raise SystemExit('No file-content markers found.')
declared_total=int(matches[0].group(2))
if declared_total!=len(matches): raise SystemExit(f'File marker count mismatch: declared {declared_total}, found {len(matches)}.')
if OUT_DIR.exists(): shutil.rmtree(OUT_DIR)
OUT_DIR.mkdir(parents=True,exist_ok=True)
fence_open=re.compile(r'^```[^\n]*\n',re.M)
fence_close=re.compile(r'^```\s*$',re.M)
written=0
for i,m in enumerate(matches):
    rel=Path(m.group(3))
    if rel.is_absolute() or '..' in rel.parts: raise SystemExit(f'Unsafe output path: {rel}')
    end=matches[i+1].start() if i+1<len(matches) else len(text)
    block=text[m.end():end]
    opening=fence_open.search(block)
    if opening:
        closing=fence_close.search(block,opening.end())
        if not closing: raise SystemExit(f'Unclosed code fence for {rel}')
        content=block[opening.end():closing.start()]
    else:
        content=block
        lines=content.splitlines()
        while lines and (not lines[0].strip() or lines[0].lstrip().startswith('- **')): lines.pop(0)
        content='\n'.join(lines)
    dst=OUT_DIR/rel
    dst.parent.mkdir(parents=True,exist_ok=True)
    dst.write_text(content.rstrip('\n')+'\n',encoding='utf-8')
    written+=1
print(f'Restored {written} files into: {OUT_DIR}')