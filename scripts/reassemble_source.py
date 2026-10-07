from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
parts=sorted((ROOT/'source-export').glob('part-*.md'))
out=ROOT/'ALI_Studio_Pro_Design4_4.6.0_FULL_SOURCE.md'
with out.open('w',encoding='utf-8',newline='') as dst:
    for p in parts:
        dst.write(p.read_text(encoding='utf-8'))
print(out)
