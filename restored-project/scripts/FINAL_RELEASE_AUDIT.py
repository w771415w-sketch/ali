from __future__ import annotations
import json, re, subprocess, sys, ast
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
errors=[]; checks=[]
def ok(label): checks.append(label)
# required structure
required=['backend','backend/training','desktop','launcher','runtime','scripts','PROJECT_MANIFEST.json','README.md']
for p in required:
    if not (ROOT/p).exists(): errors.append(f'missing:{p}')
    else: ok(f'present:{p}')
# python compile
cp=subprocess.run([sys.executable,'-m','compileall','-q',str(ROOT/'backend')],capture_output=True,text=True)
if cp.returncode: errors.append('python_compile')
else: ok('python_compile')
# parse all json
for p in ROOT.rglob('*.json'):
    if any(x in p.parts for x in ['node_modules','.venv']): continue
    try: json.loads(p.read_text(encoding='utf-8'))
    except Exception as e: errors.append(f'invalid_json:{p}:{e}')
if not any(x.startswith('invalid_json:') for x in errors): ok('json_validation')
# node source syntax where node exists
node=__import__('shutil').which('node')
if node:
    for rel in ['desktop/electron/main.cjs','desktop/electron/preload.cjs','desktop/src/api.js']:
        r=subprocess.run([node,'--check',str(ROOT/rel)],capture_output=True,text=True)
        if r.returncode: errors.append(f'node_syntax:{rel}')
    ok('node_syntax')
# version coherence
pkg=json.loads((ROOT/'desktop/package.json').read_text(encoding='utf-8'))
server=(ROOT/'backend/scripts/desktop_server.py').read_text(encoding='utf-8')
manifest=json.loads((ROOT/'PROJECT_MANIFEST.json').read_text(encoding='utf-8'))
if pkg.get('version')!='4.5.8' or 'VERSION = "4.5.8"' not in server or manifest.get('version')!='4.5.8': errors.append('version_mismatch')
else: ok('version_coherence')
# UI invariants
app=(ROOT/'desktop/src/App.jsx').read_text(encoding='utf-8')
for needle in ['محادثة جديدة','المحادثات السابقة','onDrop','api.trainingIngest','api.trainingStart']:
    if needle not in app: errors.append(f'ui_missing:{needle}')
ok('ui_training_chat_invariants')
# model bridge invariants
ll=(ROOT/'backend/inference/llama_server.py').read_text(encoding='utf-8')
if '-ngl' not in ll or 'stream_chat' not in ll: errors.append('llama_bridge_incomplete')
else: ok('llama_bridge')
# deterministic QA import smoke
sys.path.insert(0,str(ROOT/'backend'))
from core.deterministic_qa import DeterministicQA
from knowledge.store import KnowledgeStore
qa=DeterministicQA(ROOT/'backend')
for q in ['ما اسمك؟','كم VRAM لدي؟','ما هو معالج جهازي؟','كيف يعمل التدريب التراكمي؟']:
    if not qa.match(q): errors.append(f'qa_no_match:{q}')
ok('deterministic_qa')
# Training-QA retrieval contract (small in-memory DB smoke)
import tempfile
with tempfile.TemporaryDirectory() as _td:
    _store=KnowledgeStore(Path(_td)/'knowledge.sqlite3')
    _store.add_document('training.md','training.md','training-source',{'priority':180},['**User:** ما هو RAG؟\n**Assistant:** RAG هو استرجاع معزز بالتوليد.'],chunk_metadata=[{'training_question':'ما هو RAG؟','training_answer':'RAG هو استرجاع معزز بالتوليد.','training_sample_id':'smoke'}])
    if not _store.training_qa_match('ما هو RAG؟'): errors.append('training_qa_route')
    else: ok('training_qa_route')
fixture=ROOT/'backend/data/training/testdata/ALI_User_Understanding_Bundle_V4.md'
if fixture.is_file() and fixture.stat().st_size>0: ok('user_training_fixture')
else: errors.append('user_training_fixture_missing')
active_v1=ROOT/'backend/models/active/ALI-v1'
for rel in ['model.safetensors','tokenizer.model','config.json','MODEL_CARD.json']:
    if not (active_v1/rel).is_file(): errors.append(f'active_v1_missing:{rel}')
else:
    ok('bundled_active_trained_model')
knowledge_db=ROOT/'backend/runtime_knowledge.sqlite3'
if knowledge_db.is_file() and knowledge_db.stat().st_size>0: ok('bundled_runtime_knowledge')
else: errors.append('bundled_runtime_knowledge_missing')
print('FINAL_RELEASE_AUDIT 4.5.8')
for c in checks: print('[OK]',c)
if errors:
    print('ERRORS')
    for e in errors: print('[FAIL]',e)
    raise SystemExit(1)
print('[PASS] audit complete')
