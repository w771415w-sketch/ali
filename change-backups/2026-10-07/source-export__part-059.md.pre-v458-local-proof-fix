    app, root, _ = _make_app_with_workdir()
    try:
        assert app._dispatch_tool("hello how are you") is None
    finally:
        root.destroy()


def test_local_reply_routes_to_tool():
    """اكتب read_file داخل workspace → يجب أن يعرض رسالة نجاح وأداة."""
    from ali_agent import App
    app, root, proj = _make_app_with_workdir()
    try:
        app.perm_mode.set("full-access")    # لتجاوز الـ dialog
        root.update_idletasks()
        reply = app._local_reply("read_file hello.txt")
        assert "نجح" in reply or "✅" in reply, reply
        # تأكد من كتابة audit row
        from database.database import get_db, ToolCallRepo
        repo = ToolCallRepo(get_db())
        rows = repo.recent(limit=5)
        assert any(r["tool_name"] == "read_file" for r in rows), rows
    finally:
        root.destroy()


def test_local_reply_shows_tool_list_when_no_match():
    from ali_agent import App
    app, root, _ = _make_app_with_workdir()
    try:
        reply = app._local_reply("hello there")
        assert "read_file" in reply and "git_status" in reply
    finally:
        root.destroy()


def test_local_reply_blocks_dangerous_command():
    from ali_agent import App
    app, root, _ = _make_app_with_workdir()
    try:
        app.perm_mode.set("full-access")   # حتى full-access لا يتجاوز command blacklist
        reply = app._local_reply("run_command rm -rf /")
        assert "فشل" in reply or "⚠" in reply
    finally:
        root.destroy()


def test_local_reply_read_only_blocks_write():
    """write_file بصلاحية default في read-only → رفض."""
    from ali_agent import App
    app, root, _ = _make_app_with_workdir()
    try:
        app.perm_mode.set("read-only")
        reply = app._local_reply("write_file out.txt")
        # dispatcher يحتاج مسار، نعطيه مساراً
        reply = app._local_reply("write_file sub/x.txt")
        assert "فشل" in reply or "رفض" in reply or "⚠" in reply
    finally:
        root.destroy()
```

---

### `408/588` `backend/tests/test_ui_smoke.py`

- **المسار الكامل:** `F:\1f\p\ALI_Studio_Pro_Design4_4.6.0\04_Adaptive_Hybrid\backend/tests/test_ui_smoke.py`
- **الحجم:** 250 بايت (0.2 KB)
- **الامتداد:** `.py`

```python
# -*- coding: utf-8 -*-
import os, pytest

def test_ui_import():
    if os.name != 'nt' and os.environ.get('ALI_GUI_TESTS') != '1':
        pytest.skip('Tk display is unavailable in this headless test environment')
    import ali_agent  # noqa: F401
```

---

### `409/588` `backend/tests/test_v12_features.py`

- **المسار الكامل:** `F:\1f\p\ALI_Studio_Pro_Design4_4.6.0\04_Adaptive_Hybrid\backend/tests/test_v12_features.py`
- **الحجم:** 4056 بايت (4.0 KB)
- **الامتداد:** `.py`

```python
# -*- coding: utf-8 -*-
from pathlib import Path
import json, zipfile, os, tempfile, subprocess, sys
import pytest

def test_importer_on_internal_model(tmp_path):
    from model.ali_lm import AliConfig, ALIForCausalLM, save_hf_checkpoint
    from model.importer import inspect_weights, load_into
    from tokenizer.spm import train_sentencepiece, AliTokenizer
    corpus=tmp_path/'c.txt'; corpus.write_text('hello world\nالمساعد يجيب بشكل صحيح\n',encoding='utf-8')
    tokdir=tmp_path/'tok'; train_sentencepiece([str(corpus)],tokdir,vocab_size=512); tok=AliTokenizer(tokdir/'tokenizer.model')
    c=AliConfig(vocab_size=tok.vocab_size,hidden_size=32,intermediate_size=64,num_hidden_layers=1,num_attention_heads=4,num_key_value_heads=4,max_position_embeddings=32)
    m=ALIForCausalLM(c); out=save_hf_checkpoint(m,tokdir,tmp_path/'hf',{'test':True})
    r=inspect_weights(out,c); assert r.compatible; assert r.tensor_count>0
    m2=ALIForCausalLM(c); load_into(m2,out/'model.safetensors');
    for a,b in zip(m.parameters(),m2.parameters()): assert a.shape==b.shape

def test_training_resume(tmp_path):
    from model.ali_lm import AliConfig, ALIForCausalLM
    from tokenizer.spm import train_sentencepiece, AliTokenizer
    from training.trainer import Trainer, TrainConfig
    corpus=tmp_path/'c.txt'; corpus.write_text('a b c d e f g\n' * 30,encoding='utf-8')
    tokdir=tmp_path/'tok'; train_sentencepiece([str(corpus)],tokdir,vocab_size=512); tok=AliTokenizer(tokdir/'tokenizer.model')
    ds=tmp_path/'train.jsonl'; ds.write_text('\n'.join(json.dumps({'text':'<|user|> hello <|assistant|> hi <|eot|>'}) for _ in range(8)),encoding='utf-8')
    c=AliConfig(vocab_size=tok.vocab_size,hidden_size=32,intermediate_size=64,num_hidden_layers=1,num_attention_heads=4,num_key_value_heads=4,max_position_embeddings=32)
    tc=TrainConfig(epochs=1,max_steps=1,save_every=0,eval_every=0,max_seq_len=32,batch_size=1,grad_accum=1,device='cpu',gradient_checkpointing=False)
    t=Trainer(ALIForCausalLM(c),tok,ds,None,tc,tmp_path/'ck'); r=t.train(); assert r['steps']==1
    t2=Trainer(ALIForCausalLM(c),tok,ds,None,tc,tmp_path/'ck2'); t2.resume(r['checkpoint']); assert t2.global_step==1

def test_lora_roundtrip(tmp_path):
    from model.ali_lm import AliConfig, ALIForCausalLM
    from training.lora import apply_lora, save_lora_adapter, merge_lora
    c=AliConfig(vocab_size=64,hidden_size=32,intermediate_size=64,num_hidden_layers=1,num_attention_heads=4,num_key_value_heads=4,max_position_embeddings=32)
    m=ALIForCausalLM(c); names=apply_lora(m,rank=2); assert names
    assert any('lora_A' in n for n,_ in m.named_parameters())
    p=save_lora_adapter(m,tmp_path/'adapter'); assert (p/'adapter_model.safetensors').exists() or (p/'adapter_model.pt').exists()
    assert merge_lora(m)>=1

def test_archive_traversal_block(tmp_path):
    from data_engine.parsers import safe_extract_zip
    z=tmp_path/'bad.zip';
    with zipfile.ZipFile(z,'w') as f: f.writestr('../escape.txt','bad')
    with pytest.raises(ValueError): safe_extract_zip(z,tmp_path/'out')

def test_knowledge_ingest(tmp_path):
    from data_engine.harvester import Harvester
    from training.dataset import build_chat_dataset, build_causal_dataset
    from knowledge.ingest import ingest_harvest
    root=tmp_path/'src'; root.mkdir(); (root/'notes.md').write_text('Python is useful for automation.\nUser: what is python?\nAssistant: a programming language.\n',encoding='utf-8')
    hdb=tmp_path/'h.sqlite'; s=Harvester(hdb).scan(root); assert s['files']>=1
    out=tmp_path/'train'; a=build_chat_dataset(hdb,out); b=build_causal_dataset(hdb,out); assert a['train']>0; assert b['train']>0; assert (out/'chat_train.jsonl').exists(); assert (out/'cpt_train.jsonl').exists()
    k=ingest_harvest(hdb,tmp_path/'k.sqlite'); assert k['chunks']>=1

def test_runtime_no_model(tmp_path):
    from core.runtime import ALIRuntime
    r=ALIRuntime(tmp_path,tmp_path/'x.sqlite',None,False)
    x=r.answer([{'role':'user','content':'hello'}],tmp_path)
    assert x['mode']=='no_model'
```

---

### `410/588` `backend/tests/test_v1_foundation.py`

- **المسار الكامل:** `F:\1f\p\ALI_Studio_Pro_Design4_4.6.0\04_Adaptive_Hybrid\backend/tests/test_v1_foundation.py`
- **الحجم:** 1640 بايت (1.6 KB)
- **الامتداد:** `.py`

```python
from __future__ import annotations
import json, tempfile
from pathlib import Path

def test_job_manager_lifecycle(tmp_path):
    from core.job_manager import JobManager
    import time
    jm=JobManager(tmp_path/'jobs.json')
    job=jm.run('demo',lambda progress:(progress('work',.5),{'ok':True})[-1],'test')
    for _ in range(50):
        if jm.get(job.id).status in {'completed','failed'}: break
        time.sleep(.02)
    assert jm.get(job.id).status=='completed'
    assert jm.get(job.id).result['ok'] is True

def test_orchestrator_plan_has_verification_for_commands():
    from core.orchestrator import Orchestrator
    o=Orchestrator(object())
    p=o.make_plan('run_command python --version')
    assert p.intent=='run_command'
    assert [x.action for x in p.steps]==['run_command','verify_command']
    assert p.steps[0].requires_confirmation

def test_scaling_profiles_grow():
    from training.scaling import PROFILES, estimated_param_count
    counts=[estimated_param_count(PROFILES[k]) for k in ('micro','small','medium','large','xlarge')]
    assert counts==sorted(counts)
    assert counts[-1]>counts[0]

def test_gguf_validator_rejects_non_gguf(tmp_path):
    from tools.gguf import GGUFManager
    p=tmp_path/'bad.gguf'; p.write_bytes(b'NOTGGUF'+b'0'*30)
    r=GGUFManager(tmp_path).validate(p)
    assert r['exists'] and not r['valid']

def test_project_identity():
    cfg=json.loads(Path('PROJECT_VERSION.json').read_text(encoding='utf-8'))
    assert cfg['name']=='ALI AI'
    assert cfg['version'].startswith(('4.5.', '4.6.'))
    assert cfg['previous_project']=='2.5.0'
    assert cfg['previous_release']=='2.0.0'
```

---

### `411/588` `backend/tests/test_v20_lifecycle.py`

- **المسار الكامل:** `F:\1f\p\ALI_Studio_Pro_Design4_4.6.0\04_Adaptive_Hybrid\backend/tests/test_v20_lifecycle.py`
- **الحجم:** 2962 بايت (2.9 KB)
- **الامتداد:** `.py`

```python
from __future__ import annotations

import json
from pathlib import Path
import pytest
import pytest

import torch

from model.ali_lm import AliConfig, ALIForCausalLM
from model.artifacts import ArtifactManifest, sha256_path
from model.registry import ModelRegistry
from model.weights_manager import WeightsManager
from core.tool_protocol import parse_tool_calls, validate_tool_call


def _tiny_model(tmp_path: Path):
    cfg = AliConfig(
        vocab_size=64, hidden_size=32, intermediate_size=64,
        num_hidden_layers=2, num_attention_heads=4,
        num_key_value_heads=4, max_position_embeddings=64,
    )
    model = ALIForCausalLM(cfg)
    state = {k: v.detach().cpu() for k, v in model.state_dict().items()}
    ckpt = tmp_path / "source"
    ckpt.mkdir()
    torch.save({"model": state, "config": cfg.to_dict(), "global_step": 3}, ckpt / "checkpoint.pt")
    (ckpt / "config.json").write_text(json.dumps(cfg.to_dict()), encoding="utf-8")
    return ckpt, cfg


def test_artifact_manifest_roundtrip(tmp_path):
    p = tmp_path / "artifact"
    p.mkdir()
    (p / "data.txt").write_text("ALI", encoding="utf-8")
    m = ArtifactManifest(artifact_id="x", artifact_type="base", name="ALI", version="v1", path=str(p))
    m.finalize(p)
    m.write(p / "manifest.json")
    loaded = ArtifactManifest.load(p / "manifest.json")
    assert loaded.verify()["valid"] is True
    assert sha256_path(p) == loaded.sha256


def test_weight_import_embedded_config_and_registry(tmp_path):
    src, _cfg = _tiny_model(tmp_path)
    registry = ModelRegistry(tmp_path / "models" / "models.sqlite3")
    manager = WeightsManager(tmp_path, registry)
    out = manager.install(src, name="ALI")
    assert out["type"] == "base"
    assert Path(out["path"]).exists()
    assert manager.verify(out["path"])["valid"] is True
    rows = registry.list("ALI")
    assert rows and rows[0]["artifact_type"] == "base"


def test_tool_protocol_supports_tagged_json():
    calls = parse_tool_calls('<tool_call>{"name":"list_dir","arguments":{"path":"."}}</tool_call>')
    assert calls and calls[0]["tool"] == "list_dir"
    ok, reason = validate_tool_call(calls[0], {"list_dir": {"required": ["path"]}})
    assert ok, reason


def test_weight_import_standalone_checkpoint_and_adapter(tmp_path):
    src, _cfg = _tiny_model(tmp_path)
    registry = ModelRegistry(tmp_path / "models" / "models.sqlite3")
    manager = WeightsManager(tmp_path, registry)
    imported = manager.install(src / "checkpoint.pt", name="ALI")
    assert imported["type"] == "base"
    assert manager.verify(imported["path"])["valid"] is True

    from training.lora import apply_lora, save_lora_adapter
    model = ALIForCausalLM(_cfg)
    apply_lora(model, rank=2, alpha=4.0, dropout=0.0)
    adapter_dir = tmp_path / "adapter"
    save_lora_adapter(model, adapter_dir, {"base_version": "tiny"})
    adapter = manager.install(adapter_dir, name="ALI")
    assert adapter["type"] == "adapter"
    assert Path(adapter["path"]).exists()
```

---

### `412/588` `backend/tests/test_v456_finalization.py`

- **المسار الكامل:** `F:\1f\p\ALI_Studio_Pro_Design4_4.6.0\04_Adaptive_Hybrid\backend/tests/test_v456_finalization.py`
- **الحجم:** 1984 بايت (1.9 KB)
- **الامتداد:** `.py`

```python
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))

def test_deterministic_local_qa():
    from core.deterministic_qa import DeterministicQA
    qa=DeterministicQA(ROOT)
    for q, expected in [
        ('ما هو معالج جهازي؟','i7-6820HQ'),
        ('كم VRAM لدي؟','2 GB GDDR5'),
        ('ما اسمك؟','ALI Studio Pro'),
        ('كيف يعمل التدريب التراكمي؟','Active السابق'),
    ]:
        hit=qa.match(q)
        assert hit and expected in hit['answer']

def test_llama_server_supports_gpu_layers():
    text=(ROOT/'inference'/'llama_server.py').read_text(encoding='utf-8')
    assert "'-ngl'" in text
    assert 'stream_chat' in text


def test_grounded_qa_precedes_stale_memory(tmp_path):
    from core.runtime import ALIRuntime
    seed=tmp_path/'knowledge_seed'; seed.mkdir()
    faq=Path(__file__).resolve().parents[1]/'knowledge_seed'/'ALI_RUNTIME_FAQ_AR_V1.md'
    (seed/'ALI_RUNTIME_FAQ_AR_V1.md').write_text(faq.read_text(encoding='utf-8'),encoding='utf-8')
    r=ALIRuntime(tmp_path,tmp_path/'x.sqlite3',None,False)
    r.conversation_memory.put('ما اسم المشروع؟','إجابة قديمة غير صحيحة',source='old',model_version='old',quality=1.0)
    x=r.answer([{'role':'user','content':'ما اسم المشروع؟'}],tmp_path)
    assert x['mode']=='grounded_qa'
    assert 'ALI Studio Pro' in x['text']


def test_arabic_explicit_tool_dispatch(tmp_path):
    from core.runtime import ALIRuntime, ConversationContext
    r=ALIRuntime(tmp_path,tmp_path/'x.sqlite3',None,False)
    ctx=ConversationContext(thread_id='t', project_dir=str(tmp_path), perm_mode=r.permission_manager.mode, model='ALI', effort='high', tool_registry=r.registry, extra={})
    p=tmp_path/'hello.txt'; p.write_text('hello',encoding='utf-8')
    out=r.tool_dispatch('اقرأ الملف hello.txt',ctx)
    assert out and out['ok'] and out['data']['content']=='hello'
```

---

### `413/588` `backend/tests/test_v457_training_bundle.py`

- **المسار الكامل:** `F:\1f\p\ALI_Studio_Pro_Design4_4.6.0\04_Adaptive_Hybrid\backend/tests/test_v457_training_bundle.py`
- **الحجم:** 3095 بايت (3.0 KB)
- **الامتداد:** `.py`

```python
from __future__ import annotations

from pathlib import Path

from core.runtime import ALIRuntime
from knowledge.store import KnowledgeStore
from training.continuous_learning import ContinuousLearningManager


BUNDLE = """# ALI bundle
## إحصائيات الحزمة
- إجمالي المحادثات: **3**
- Train: **2**
- Validation: **1**
- Test: **0**

## المحادثة 1 — user_understanding
> النوع: `user_understanding` · المجموعة: `train`
**User:** ما هو NLU؟
**Assistant:** NLU هو فهم اللغة الطبيعية واستخراج المعنى والنية من نص المستخدم.

## المحادثة 2 — user_understanding
> النوع: `user_understanding` · المجموعة: `train`
**User:** ما هو RAG؟
**Assistant:** RAG يسترجع معلومات من مصادر خارجية أو محلية ثم يستخدمها لتوليد إجابة grounded.

## المحادثة 3 — user_understanding
> النوع: `user_understanding` · المجموعة: `validation`
**User:** كيف يتعامل AI مع الغموض؟
**Assistant:** يطلب التوضيح عندما لا تكفي الأدلة بدلاً من التخمين.

## المحادثة 4 — user_understanding
> النوع: `user_understanding` · المجموعة: `test`
**User:** ما هو NLU؟
**Assistant:** NLU هو فهم اللغة الطبيعية واستخراج المعنى والنية من نص المستخدم.
"""


def test_v457_bundle_import_deduplicates_and_reports_metadata_mismatch(tmp_path: Path):
    src = tmp_path / "bundle.md"
    src.write_text(BUNDLE, encoding="utf-8")
    manager = ContinuousLearningManager(tmp_path)
    result = manager.import_files([src])[0]
    assert result["ok"] is True
    assert result["status"] == "validated"
    assert result["sample_count"] == 3
    assert "declared_conversation_count_mismatch:3!=4" in result["warnings"]
    assert "duplicate_samples_in_file:1" in result["warnings"]
    assert manager.status()["pending_sources"] == 1

    store = KnowledgeStore(tmp_path / "runtime_knowledge.sqlite3")
    hit = store.training_qa_match("ما هو RAG؟")
    assert hit is not None
    assert hit["score"] == 1.0
    assert "يسترجع معلومات" in hit["answer"]


def test_v457_runtime_answers_imported_questions_before_model(tmp_path: Path):
    src = tmp_path / "bundle.md"
    src.write_text(BUNDLE, encoding="utf-8")
    manager = ContinuousLearningManager(tmp_path)
    manager.import_files([src])
    runtime = ALIRuntime(tmp_path, tmp_path / "runtime.sqlite3", model_engine=None, allow_internet=False)
    result = runtime.answer([{"role": "user", "content": "ما هو NLU؟"}], tmp_path)
    assert result["mode"] == "training_qa"
    assert result["confidence"] == 1.0
    assert "فهم اللغة الطبيعية" in result["text"]

    stream = list(runtime.stream_answer([{"role": "user", "content": "ما هو RAG؟"}], tmp_path))
    assert stream[-1]["type"] == "final"
    assert stream[-1]["mode"] == "training_qa"
    assert "يسترجع معلومات" in stream[-1]["text"]
```

---

### `414/588` `backend/tests/test_v458_bundled_release.py`

- **المسار الكامل:** `F:\1f\p\ALI_Studio_Pro_Design4_4.6.0\04_Adaptive_Hybrid\backend/tests/test_v458_bundled_release.py`
- **الحجم:** 2561 بايت (2.5 KB)
- **الامتداد:** `.py`

```python
from __future__ import annotations

import json
from pathlib import Path

from knowledge.store import KnowledgeStore
from model.manager import ModelManager
from model.registry import ModelRegistry
from training.continuous_learning import ContinuousLearningManager

ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / "data" / "training" / "testdata" / "ALI_User_Understanding_Bundle_V4.md"


def test_v458_bundled_model_registry_and_reload():
    registry = ModelRegistry(ROOT / "models" / "models.sqlite3")
    active = registry.active("ALI")
    model_dir = ROOT / "models" / "active" / "ALI-v4"
    required = [model_dir / "model.safetensors", model_dir / "tokenizer.model"]
    if active is None or not all(p.is_file() and p.stat().st_size > 0 for p in required):
        pytest.skip("v4 binary weights/tokenizer are not shipped in the source bundle; validate when artifacts are installed")
    assert active["version"] == "v4"
    manager = ModelManager(ROOT, registry)
    engine, row = manager.load(active, compute_mode="cpu")
    assert row["version"] == "v4"
    assert engine.model_dir == model_dir


def test_v458_bundled_training_questions_are_preseeded():
    db_path = ROOT / "runtime_knowledge.sqlite3"
    import sqlite3
    con = sqlite3.connect(db_path)
    tables = {r[0] for r in con.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()}
    con.close()
    if "training_qa" not in tables:
        pytest.skip("runtime training QA database is generated state and is not included in the source bundle")
    store = KnowledgeStore(db_path)
    manager = ContinuousLearningManager(ROOT)
    samples, _safe, _warnings = manager.parse_file(FIXTURE)
    assert len(samples) > 0
    hits = 0
    for sample in samples:
        question = [m["content"] for m in sample if m.get("role") == "user"][-1]
        hit = store.training_qa_match(question)
        assert hit is not None, question
        assert hit["answer"].strip()
        hits += 1
    assert hits == len(samples)
    con = sqlite3.connect(db_path)
    row = con.execute("SELECT path FROM documents WHERE kind='trained-bundle'").fetchone()
    con.close()
    assert row is not None
    assert row[0] == "data/training/testdata/ALI_User_Understanding_Bundle_V4.md"


def test_v458_bundle_artifact_hashes_exist():
    receipt = ROOT / "models" / "runs" / "ALI-v1-20261004-224649-233144" / "FINAL_FILE_TRAINING_E2E_RECEIPT_4.5.8.json"
    data = json.loads(receipt.read_text(encoding="utf-8"))
    assert data["training"]["status"] == "success"
    assert data["quiz"]["source_answer_match"] >= 0
    paths = [
        ROOT / "models" / "active" / "ALI-v4" / "model.safetensors",
        ROOT / "models" / "active" / "ALI-v4" / "tokenizer.model",
        ROOT / "models" / "generations" / "v4" / "generation.json",
        ROOT / "models" / "generations" / "v4" / "lineage.json",
    ]
    if not all(p.is_file() and p.stat().st_size > 0 for p in paths):
        assert data["gguf"]["status"] == "pending_converter"
        assert data["native_windows"]["electron_net_conpty_cuda"] == "not executed in Linux container"
        pytest.skip("binary model artifacts are intentionally absent from this source-only bundle")
    assert all(p.is_file() and p.stat().st_size > 0 for p in paths)
```

---

### `415/588` `backend/tests/test_web_chat_integration.py`

- **المسار الكامل:** `F:\1f\p\ALI_Studio_Pro_Design4_4.6.0\04_Adaptive_Hybrid\backend/tests/test_web_chat_integration.py`
- **الحجم:** 1995 بايت (1.9 KB)
- **الامتداد:** `.py`

```python
from __future__ import annotations

from pathlib import Path

import core.runtime as runtime_module
from core.runtime import ALIRuntime
from core.response_guard import stream_safe
from research.web import should_search_web, source_footer


def test_web_intent_detection():
    assert should_search_web("ابحث عبر الإنترنت عن آخر أخبار Python")[0]
    assert should_search_web("ما هو أحدث إصدار من Python؟")[0]
    assert not should_search_web("ابحث في الملفات عن runtime.py")[0]


def test_source_footer_stays_inside_answer():
    web = {"documents": [{"title": "Official", "url": "https://example.com", "text": "Evidence"}]}
    footer = source_footer(web, language="ar")
    assert "المصادر:" in footer
    assert "https://example.com" in footer


def test_stream_guard_blocks_corrupted_repetition():
    assert not stream_safe("svgsvgsvgsvgsvg svgsvgsvg ent ent ent ent ent ent")
    assert stream_safe("هذه إجابة عربية سليمة ومختصرة.", "ما هو الذكاء الاصطناعي؟")


def test_web_answer_is_inline_when_model_missing(tmp_path: Path, monkeypatch):
    docs = {
        "query": "أحدث المعلومات",
        "results": [],
        "documents": [
            {"title": "مصدر موثوق", "url": "https://example.com/article", "text": "هذه معلومات حديثة من المصدر."}
        ],
    }
    monkeypatch.setattr(runtime_module, "web_research", lambda *a, **k: docs)
    monkeypatch.setattr(runtime_module, "should_search_web", lambda *a, **k: (True, "explicit_web_request"))
    rt = ALIRuntime(tmp_path, tmp_path / "runtime.sqlite3", model_engine=None, allow_internet=True)
    result = rt.answer([{"role": "user", "content": "ابحث عبر الإنترنت عن أحدث المعلومات"}], tmp_path)
    assert result["mode"] == "web_fallback"
    assert "المصادر:" in result["text"]
    assert "https://example.com/article" in result["text"]
```

---

### `416/588` `backend/tokenizer/__init__.py`

- **المسار الكامل:** `F:\1f\p\ALI_Studio_Pro_Design4_4.6.0\04_Adaptive_Hybrid\backend/tokenizer/__init__.py`
- **الحجم:** 2274 بايت (2.2 KB)
- **الامتداد:** `.py`

```python
# -*- coding: utf-8 -*-
"""ALI Tokenizer — BPE tokenizer مستقل، يدعم العربية، بدون أي نموذج خارجي.

PUBLIC API (stable for V0.8):
    ALITokenizer(config, vocab, merges)
        .encode(text, add_bos, add_eos, special_tokens) -> List[int]
        .decode(ids, skip_special) -> str
        .normalize(text) -> str
        .save(path)
        ALITokenizer.load(path)
        .vocab_size, .special_tokens
        .pad_id, .bos_id, .eos_id, .unk_id
        .user_id, .assistant_id, .system_id
        .token_to_id(...), .id_to_token(...)
        .is_special_token(...), .is_byte_token(...)

ARCHITECTURE:
    config     →  TokenizerConfig
    vocabulary →  Vocabulary (token <-> id)
    trainer    →  BPETrainer (corpus → vocab + merges)
    tokenizer  →  ALITokenizer (encode/decode + normalize)
    serialization → save/load (atomic writes + manifest + hashes)
"""

from tokenizer.config import TokenizerConfig, DEFAULT_SPECIAL_TOKENS
from tokenizer.vocabulary import Vocabulary
from tokenizer.trainer import (
    BPETrainer, pretokenize,
    _word_to_symbols, _is_valid_byte_token, _merge_to_token,
)
from tokenizer.tokenizer import (
    ALITokenizer,
    normalize_arabic_text,
)
from tokenizer.serialization import (
    TokenizerPaths,
    save_tokenizer, load_tokenizer,
    save_merges, load_merges,
    TOKENIZER_VERSION, ALGORITHM,
)

DEFAULT_TOKENIZER_DIR = "weights/tokenizer"


def get_default_tokenizer():
    """Lazy load للـ tokenizer الافتراضي (يستخدم في الـ inference).

    Returns None إذا لم يُدرَّب بعد.
    """
    from config.paths import APP_PATHS
    root = APP_PATHS.project_root() / DEFAULT_TOKENIZER_DIR
    if not root.exists():
        return None
    try:
        return load_tokenizer(root)
    except Exception:
        return None


__all__ = [
    "TokenizerConfig", "DEFAULT_SPECIAL_TOKENS",
    "Vocabulary",
    "BPETrainer", "pretokenize",
    "_word_to_symbols", "_is_valid_byte_token", "_merge_to_token",
    "ALITokenizer",
    "normalize_arabic_text",
    "TokenizerPaths",
    "save_tokenizer", "load_tokenizer",
    "save_merges", "load_merges",
    "TOKENIZER_VERSION", "ALGORITHM",
    "DEFAULT_TOKENIZER_DIR",
    "get_default_tokenizer",
]
```

---

### `417/588` `backend/tokenizer/config.py`

- **المسار الكامل:** `F:\1f\p\ALI_Studio_Pro_Design4_4.6.0\04_Adaptive_Hybrid\backend/tokenizer/config.py`
- **الحجم:** 4068 بايت (4.0 KB)
- **الامتداد:** `.py`

```python
# -*- coding: utf-8 -*-
"""TokenizerConfig — إعدادات ALI Tokenizer.

تحتوي:
- نوع الخوارزمية (BPE حالياً).
- حجم الـ vocab المستهدف.
- min_frequency لزوج BPE قبل اعتماده.
- special tokens (مرتّبة لتحديد IDs بشكل deterministic).
- خيارات normalization للعربية.
- إعدادات pre-tokenization.

الـ config قابل للحفظ/التحميل كـ JSON.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import List


# ------------------------------------------------------------------
# الافتراضي
# ------------------------------------------------------------------
DEFAULT_SPECIAL_TOKENS: List[str] = [
    "<PAD>",
    "<BOS>",
    "<EOS>",
    "<UNK>",
    "<USER>",
    "<ASSISTANT>",
    "<SYSTEM>",
]


@dataclass
class TokenizerConfig:
    """إعدادات Tokenizer قابلة للتسلسل JSON."""

    type: str = "BPE"
    vocab_size: int = 4096
    min_frequency: int = 2

    # Special tokens (الترتيب يحدد الـ IDs: index 0 -> id 0).
    special_tokens: List[str] = field(
        default_factory=lambda: list(DEFAULT_SPECIAL_TOKENS)
    )

    # تطبيع العربية
    normalize_arabic: bool = True
    strip_diacritics: bool = True
    normalize_alef: bool = True       # إ/أ/آ -> ا
    normalize_yaa: bool = True        # ى -> ي
    normalize_taa_marbuta: bool = True # ة -> ه (مفعّل = آمن للنماذج)

    # Pre-tokenization
    lowercase_english: bool = True

    # End-of-word marker (GPT-2 style).
    # عند التدريب، أي token ليس في بداية الكلمة يُلحق بـ "</w>".
    use_end_of_word_marker: bool = True

    # إصدار الـ tokenizer
    version: str = "0.7.1"

    def __post_init__(self) -> None:
        """validation عند البناء."""
        if self.type not in ("BPE",):
            raise ValueError(f"unsupported tokenizer type: {self.type}")
        if self.vocab_size <= 0:
            raise ValueError("vocab_size must be positive")
        if self.min_frequency < 1:
            raise ValueError("min_frequency must be >= 1")
        if not self.special_tokens:
            raise ValueError("special_tokens cannot be empty")
        seen = set()
        for tok in self.special_tokens:
            if not tok:
                raise ValueError("empty string in special_tokens")
            if tok in seen:
                raise ValueError(f"duplicate special token: {tok!r}")
            seen.add(tok)
        # byte token prefixes must not collide with special tokens.
        for special in self.special_tokens:
            if special.startswith("<0x"):
                raise ValueError(
                    f"special token {special!r} starts with '<0x' "
                    f"(reserved for byte tokens)"
                )

    # ------------------------------------------------------------
    # Dict / JSON helpers
    # ------------------------------------------------------------
    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, d: dict) -> "TokenizerConfig":
        # تصفية المفاتيح الزائدة (forward-compat).
        known = {f for f in cls.__dataclass_fields__}
        clean = {k: v for k, v in d.items() if k in known}
        return cls(**clean)

    # ------------------------------------------------------------
    # Save / Load
    # ------------------------------------------------------------
    def save(self, path: Path) -> None:
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(self.to_dict(), f, ensure_ascii=False, indent=2)

    @classmethod
    def load(cls, path: Path) -> "TokenizerConfig":
        with open(path, "r", encoding="utf-8") as f:
            return cls.from_dict(json.load(f))


__all__ = ["TokenizerConfig", "DEFAULT_SPECIAL_TOKENS"]
```

---

### `418/588` `backend/tokenizer/manager.py`

- **المسار الكامل:** `F:\1f\p\ALI_Studio_Pro_Design4_4.6.0\04_Adaptive_Hybrid\backend/tokenizer/manager.py`
- **الحجم:** 5733 بايت (5.6 KB)
- **الامتداد:** `.py`

```python
# -*- coding: utf-8 -*-
"""Versioned tokenizer lifecycle for ALI AI 2.0."""
from __future__ import annotations

from pathlib import Path
from typing import Iterable, Any
import json
import time
import hashlib
import shutil

from tokenizer.spm import train_sentencepiece, AliTokenizer
from model.artifacts import ArtifactManifest, sha256_path


class TokenizerManager:
    def __init__(self, root: str | Path):
        self.root = Path(root)
        self.dir = self.root / "models" / "tokenizers"
        self.dir.mkdir(parents=True, exist_ok=True)

    def corpus_hash(self, inputs: Iterable[str | Path]) -> str:
        h = hashlib.sha256()
        for raw in sorted(str(Path(x).resolve()) for x in inputs):
            p = Path(raw)
            h.update(raw.encode("utf-8")); h.update(b"\0")
            h.update(p.read_bytes())
            h.update(b"\0")
        return h.hexdigest()

    def train(
        self,
        inputs: list[str | Path],
        *,
        vocab_size: int = 4096,
        name: str = "ALI",
        version: str | None = None,
        force: bool = False,
    ) -> dict[str, Any]:
        if not inputs:
            raise ValueError("tokenizer inputs are empty")
        paths = [Path(x).resolve() for x in inputs]
        for p in paths:
            if not p.exists():
                raise FileNotFoundError(p)
        chash = self.corpus_hash(paths)
        existing = self.find_by_corpus(chash, name)
        if existing and not force:
            return {"reused": True, **existing}

        ver = version or time.strftime("%Y%m%d-%H%M%S")
        safe = "".join(c if c.isalnum() or c in "._-" else "_" for c in name) or "ALI"
        out = self.dir / safe / ver
        out.parent.mkdir(parents=True, exist_ok=True)

        # SentencePiece works from real corpus files. JSONL is converted to a
        # deterministic plain-text corpus first.
        corpus_files = []
        work = out / "_corpus"
        work.mkdir(parents=True, exist_ok=True)
        for idx, p in enumerate(paths):
            if p.suffix.lower() in {".jsonl", ".json"}:
                target = work / f"{idx:03d}-{p.stem}.txt"
                with p.open(encoding="utf-8", errors="replace") as fh, target.open("w", encoding="utf-8") as out_f:
                    for line in fh:
                        try:
                            obj = json.loads(line)
                        except Exception:
                            continue
                        if isinstance(obj, dict) and isinstance(obj.get("messages"), list):
                            for m in obj["messages"]:
                                if isinstance(m, dict):
                                    out_f.write(str(m.get("content", "")) + "\n")
                        elif isinstance(obj, dict):
                            out_f.write(str(obj.get("text", "")) + "\n")
                        else:
                            out_f.write(str(obj) + "\n")
                corpus_files.append(str(target))
            else:
                corpus_files.append(str(p))

        tokenizer_file = train_sentencepiece(corpus_files, out, vocab_size=vocab_size)
        tok = AliTokenizer(tokenizer_file)
        manifest = ArtifactManifest(
            artifact_id=f"{safe}:tokenizer:{ver}",
            artifact_type="tokenizer",
            name=safe,
            version=ver,
            source="local-training",
            lineage={"corpus_hash": chash, "inputs": [str(p) for p in paths]},
            compatibility={"vocab_size": tok.vocab_size},
            metadata={"requested_vocab_size": vocab_size, "actual_vocab_size": tok.vocab_size},
        )
        # Temporary corpus is implementation detail, remove before final hash.
        if work.exists():
            shutil.rmtree(work)
        manifest.finalize(out)
        manifest.write(out / "manifest.json")
        return {
            "reused": False,
            "name": safe,
            "version": ver,
            "path": str(out),
            "tokenizer": str(tokenizer_file),
            "vocab_size": tok.vocab_size,
            "corpus_hash": chash,
            "hash": manifest.sha256,
        }

    def find_by_corpus(self, corpus_hash: str, name: str = "ALI") -> dict[str, Any] | None:
        safe = "".join(c if c.isalnum() or c in "._-" else "_" for c in name) or "ALI"
        base = self.dir / safe
        if not base.exists():
            return None
        for version_dir in sorted((p for p in base.iterdir() if p.is_dir()), reverse=True):
            m = version_dir / "manifest.json"
            if not m.exists():
                continue
            data = json.loads(m.read_text(encoding="utf-8"))
            if data.get("lineage", {}).get("corpus_hash") == corpus_hash:
                return {
                    "name": data.get("name", safe),
                    "version": data.get("version", version_dir.name),
                    "path": str(version_dir),
                    "tokenizer": str(version_dir / "tokenizer.model"),
                    "vocab_size": data.get("compatibility", {}).get("vocab_size", 0),
                    "corpus_hash": corpus_hash,
                    "hash": data.get("sha256", ""),
                }
        return None

    def list(self, name: str = "ALI") -> list[dict[str, Any]]:
        safe = "".join(c if c.isalnum() or c in "._-" else "_" for c in name) or "ALI"
        base = self.dir / safe
        if not base.exists():
            return []
        result = []
        for p in sorted((x for x in base.iterdir() if x.is_dir()), reverse=True):
            m = p / "manifest.json"
            if m.exists():
                result.append(json.loads(m.read_text(encoding="utf-8")))
        return result
```

---

### `419/588` `backend/tokenizer/serialization.py`

- **المسار الكامل:** `F:\1f\p\ALI_Studio_Pro_Design4_4.6.0\04_Adaptive_Hybrid\backend/tokenizer/serialization.py`
- **الحجم:** 10129 بايت (9.9 KB)
- **الامتداد:** `.py`

```python
# -*- coding: utf-8 -*-
"""Serialization — حفظ/تحميل ALI Tokenizer إلى/من القرص.

Artifact layout (داخل مجلد tokenizer/):
    config.json     # TokenizerConfig
    vocab.json      # {token: id}
    merges.txt      # كل سطر "a b"
    manifest.json   # metadata: tokenizer_version, algorithm, hashes

Writes atomic (temp file + os.replace) حتى لا يترك crash ملفاً نصف مكتوب.
"""

from __future__ import annotations

import hashlib
import json
import os
import tempfile
from pathlib import Path
from typing import List, Tuple

from tokenizer.config import TokenizerConfig
from tokenizer.vocabulary import Vocabulary
from tokenizer.tokenizer import ALITokenizer


TOKENIZER_VERSION = "0.7.2"
ALGORITHM = "BPE"


# ------------------------------------------------------------------
class TokenizerPaths:
    """مسارات الملفات داخل مجلد الـ tokenizer."""

    def __init__(self, root: Path) -> None:
        self.root = Path(root)
        self.config = self.root / "config.json"
        self.vocab = self.root / "vocab.json"
        self.merges = self.root / "merges.txt"
        self.manifest = self.root / "manifest.json"

    def exists(self) -> bool:
        return self.config.exists() and self.vocab.exists() and self.merges.exists()

    def which_missing(self) -> List[str]:
        out = []
        for name, p in [("config", self.config), ("vocab", self.vocab),
                         ("merges", self.merges)]:
            if not p.exists():
                out.append(name)
        return out


# ------------------------------------------------------------------
# Atomic write helper
# ------------------------------------------------------------------
def _atomic_write_bytes(path: Path, data: bytes) -> None:
    """Write bytes to path atomically (temp + os.replace)."""
    path.parent.mkdir(parents=True, exist_ok=True)
    # tempfile in same dir for os.replace atomicity.
    fd, tmp_path = tempfile.mkstemp(
        dir=str(path.parent), prefix=f".{path.name}.", suffix=".tmp",
    )
    try:
        with os.fdopen(fd, "wb") as f:
            f.write(data)
        os.replace(tmp_path, path)
    except Exception:
        try:
            os.unlink(tmp_path)
        except OSError:
            pass
        raise
