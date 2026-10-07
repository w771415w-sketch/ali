from pathlib import Path
import ast, json, re, sys
ROOT=Path(__file__).resolve().parents[1]
errors=[]
# Python compile
for p in (ROOT/'backend').rglob('*.py'):
    try: ast.parse(p.read_text(encoding='utf-8'))
    except Exception as e: errors.append(f'PY {p}: {e}')
# app invariants
app=(ROOT/'desktop'/'src'/'App.jsx').read_text(encoding='utf-8')
checks=[
 ('duplicate_const','const result = const result' not in app),
 ('new_chat','createConversation' in app),
 ('history','conversations' in app),
 ('training_drop','onDrop' in app),
 ('compute_mode','computeMode' in app),
]
for n,ok in checks:
    if not ok: errors.append(n)
# JSON
for p in [ROOT/'desktop/package.json',ROOT/'backend/config/hardware_profile.json',ROOT/'backend/models/model_manifest.json']:
    try: json.loads(p.read_text(encoding='utf-8'))
    except Exception as e: errors.append(f'JSON {p}: {e}')
# report source requirements
req=(ROOT/'backend/requirements-windows-legacy-gpu.txt').read_text(encoding='utf-8')
if 'torch==2.14.0' not in req: errors.append('legacy GPU requirements missing torch 2.14')
print(f'ALI 4.5 static checks: {"PASS" if not errors else "FAIL"}')
for e in errors: print(' -',e)
sys.exit(0 if not errors else 1)
