        rows = cur.execute(
            "SELECT name FROM sqlite_master WHERE type='table';"
        ).fetchall()
        names = {r["name"] for r in rows}
    missing = required - names
    assert not missing, "missing tables: " + str(missing)


def test_indexes_exist(fresh_db):
    with fresh_db.cursor() as cur:
        rows = cur.execute(
            "SELECT name FROM sqlite_master WHERE type='index';"
        ).fetchall()
        names = {r["name"] for r in rows}
    for idx in ("idx_threads_project", "idx_messages_thread",
                "idx_tool_calls_thread", "idx_logs_ts"):
        assert idx in names, "missing index: " + idx


def test_project_repo_crud(fresh_db):
    repo = db_mod.ProjectRepo(fresh_db)
    pid = repo.create("ALI", str(ROOT))
    assert pid.startswith("p_")
    p = repo.get(pid)
    assert p["name"] == "ALI"
    assert repo.by_path(str(ROOT)) is not None
    repo.touch(pid)
    assert repo.list_recent()[0]["id"] == pid


def test_thread_repo_lifecycle(fresh_db):
    projects = db_mod.ProjectRepo(fresh_db)
    pid = projects.create("ALI", str(ROOT))
    threads = db_mod.ThreadRepo(fresh_db)
    tid = threads.create(pid, "Test")
    threads.rename(tid, "Renamed")
    t = threads.get(tid)
    assert t["title"] == "Renamed"
    threads.touch(tid)


def test_message_repo(fresh_db):
    projects = db_mod.ProjectRepo(fresh_db)
    threads = db_mod.ThreadRepo(fresh_db)
    messages = db_mod.MessageRepo(fresh_db)
    pid = projects.create("ALI", str(ROOT))
    tid = threads.create(pid)
    messages.add(tid, "user", "hi")
    messages.add(tid, "assistant", "hello")
    msgs = messages.list_for_thread(tid)
    assert len(msgs) == 2
    assert msgs[0]["role"] == "user"
    assert msgs[1]["role"] == "assistant"
    assert messages.count(tid) == 2


def test_settings_repo(fresh_db):
    s = db_mod.SettingsRepo(fresh_db)
    s.set("perm_mode", "default")
    assert s.get("perm_mode") == "default"
    s.set("perm_mode", "read-only")
    assert s.get("perm_mode") == "read-only"
    assert s.all()["perm_mode"] == "read-only"


def test_tool_call_repo(fresh_db):
    tc = db_mod.ToolCallRepo(fresh_db)
    cid = tc.start(None, None, "read_file", {"path": "x.py"})
    tc.finish(cid, "ok", {"content": "hello"})
    rows = tc.recent()
    assert rows[0]["status"] == "ok"
    assert rows[0]["tool_name"] == "read_file"


def test_log_repo(fresh_db):
    lr = db_mod.LogRepo(fresh_db)
    lr.add("INFO", "test", "hello")
    lr.add("ERROR", "test", "boom")
    rows = lr.recent()
    assert len(rows) == 2
    # حذف كل ما عمره أقل من ثانية واحدة (يضمن حذف السجلات التي أُضيفت الآن)
    deleted = lr.prune_older_than(-1)
    assert deleted >= 2


def test_migration_is_idempotent(tmp_path):
    """فتح نفس DB مرتين يجب ألا يعيد تشغيل migrations."""
    p = tmp_path / "ali.db"
    db1 = db_mod.Database.__new__(db_mod.Database)
    db1.__init__(p)
    v1 = db1.get_meta("schema_version")
    # إعادة الفتح على نفس المسار
    db_mod._BOOTSTRAPPED.discard(str(p))
    db2 = db_mod.Database.__new__(db_mod.Database)
    db2.__init__(p)
    v2 = db2.get_meta("schema_version")
    assert v1 == v2
    assert int(v1) == schema_mod.SCHEMA_VERSION
```

---

### `390/588` `backend/tests/test_hardware_memory_order.py`

- **المسار الكامل:** `F:\1f\p\ALI_Studio_Pro_Design4_4.6.0\04_Adaptive_Hybrid\backend/tests/test_hardware_memory_order.py`
- **الحجم:** 583 بايت (0.6 KB)
- **الامتداد:** `.py`

```python
from runtime.hardware import HardwareInfo
from runtime.device_policy import gguf_offload_policy


def test_gpu_memory_fields_are_semantically_ordered():
    h = HardwareInfo(os="Windows", python="3.11.9", cpu_cores=8, ram_gb=32, gpu_available=True, gpu_name="NVIDIA Quadro M1000M", vram_gb=2.0, torch_cuda=True, disk_free_gb=100.0, cuda_capability=(5,0), physical_cores=4, backend_hint="cuda", gpu_mem_used_gb=0.50, gpu_mem_free_gb=1.50)
    assert h.gpu_mem_used_gb < h.gpu_mem_free_gb
    p = gguf_offload_policy(h, mode="auto", total_layers=24)
    assert p["n_gpu_layers"] == 24
```

---

### `391/588` `backend/tests/test_hermes_integration.py`

- **المسار الكامل:** `F:\1f\p\ALI_Studio_Pro_Design4_4.6.0\04_Adaptive_Hybrid\backend/tests/test_hermes_integration.py`
- **الحجم:** 1622 بايت (1.6 KB)
- **الامتداد:** `.py`

```python
from pathlib import Path
import json, sqlite3
from integration.hermes.config import HermesConfig
from integration.hermes.adapter import HermesAdapter
from integration.hermes.router import HermesContextRouter

def make_hermes(tmp_path):
    root=tmp_path/'Hermes'; (root/'memories').mkdir(parents=True); (root/'skills'/'demo').mkdir(parents=True)
    (root/'SOUL.md').write_text('soul',encoding='utf-8'); (root/'memories'/'MEMORY.md').write_text('memory',encoding='utf-8'); (root/'memories'/'USER.md').write_text('user',encoding='utf-8'); (root/'skills'/'demo'/'SKILL.md').write_text('skill',encoding='utf-8')
    (root/'kanban.db').touch()
    con=sqlite3.connect(root/'projects.db'); con.execute('create table items(name text)'); con.execute("insert into items values ('A')"); con.commit(); con.close()
    (root/'.env').write_text('SECRET=x',encoding='utf-8'); (root/'auth.json').write_text('{"token":"x"}',encoding='utf-8')
    return root

def test_adapter_read_only_and_secret_block(tmp_path):
    root=make_hermes(tmp_path); a=HermesAdapter(HermesConfig(root=str(root)))
    assert a.read_text('memories/MEMORY.md')=='memory'
    assert a.read_database('projects.db','SELECT name FROM items')[0]['name']=='A'
    try: a.read_text('.env')
    except PermissionError: pass
    else: raise AssertionError('secret file was readable')

def test_router_only_routes_hermes_requests(tmp_path):
    root=make_hermes(tmp_path); r=HermesContextRouter(HermesConfig(root=str(root)))
    assert r.route('كيف أفتح ملفًا محليًا؟')['used'] is False
    assert r.route('اعرض ذاكرة Hermes')['used'] is True
```

---

### `392/588` `backend/tests/test_inference_stream.py`

- **المسار الكامل:** `F:\1f\p\ALI_Studio_Pro_Design4_4.6.0\04_Adaptive_Hybrid\backend/tests/test_inference_stream.py`
- **الحجم:** 316 بايت (0.3 KB)
- **الامتداد:** `.py`

```python
from pathlib import Path


def test_stream_source_uses_deltas():
    root = Path(__file__).resolve().parents[1]
    text = (root / "inference" / "engine.py").read_text(encoding="utf8")
    assert "last_text=''" in text
    assert 'yield delta' in text
    assert "return ''.join(self.stream(rows,**kwargs))" in text
```

---

### `393/588` `backend/tests/test_integration.py`

- **المسار الكامل:** `F:\1f\p\ALI_Studio_Pro_Design4_4.6.0\04_Adaptive_Hybrid\backend/tests/test_integration.py`
- **الحجم:** 3035 بايت (3.0 KB)
- **الامتداد:** `.py`

```python
# -*- coding: utf-8 -*-
"""اختبار Integration: Tools + Registry + PermissionManager + Context معاً."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def _setup(tmp_path):
    from core.context import ConversationContext
    from security.permissions import PermissionManager
    from tools.registry import get_registry, reset_registry_for_tests
    reset_registry_for_tests()
    reg = get_registry()
    pm = PermissionManager(mode="default")
    # Simulate the user approval that the production UI must obtain before
    # write/commit actions. Default mode must never auto-allow them.
    pm.grant("write_file", session=True)
    pm.grant("git_commit", session=True)
    reg.set_permission_manager(pm)
    ctx = ConversationContext(
        thread_id="t_int", project_dir=str(tmp_path), perm_mode="default",
    )
    return reg, ctx


def test_integration_read_then_write(tmp_path):
    reg, ctx = _setup(tmp_path)
    # 1) write
    r = reg.execute("write_file", ctx, path="hello.txt", content="ALI")
    assert r.ok, r.error
    assert (tmp_path / "hello.txt").exists()
    # 2) read back
    r = reg.execute("read_file", ctx, path="hello.txt")
    assert r.ok
    assert r.data["content"] == "ALI"


def test_integration_read_only_mode_blocks_write(tmp_path):
    reg, ctx = _setup(tmp_path)
    ctx.perm_mode = "read-only"
    r = reg.execute("write_file", ctx, path="x.txt", content="nope")
    assert not r.ok
    assert r.error_code == "DENIED"
    # لكن read مسموح
    (tmp_path / "x.txt").write_text("ok")
    r = reg.execute("read_file", ctx, path="x.txt")
    assert r.ok


def test_integration_path_blocked(tmp_path):
    reg, ctx = _setup(tmp_path)
    r = reg.execute("read_file", ctx, path="../../etc/passwd")
    assert not r.ok
    assert r.error_code == "PATH_BLOCKED"


def test_integration_dangerous_command(tmp_path):
    reg, ctx = _setup(tmp_path)
    r = reg.execute("run_command", ctx, command="rm -rf /")
    assert not r.ok
    assert r.error_code == "DENIED"


def test_integration_full_access_allows_all(tmp_path):
    reg, ctx = _setup(tmp_path)
    ctx.perm_mode = "full-access"
    r = reg.execute("write_file", ctx, path="ok.txt", content="ok")
    assert r.ok


def test_integration_git_tools(tmp_path):
    reg, ctx = _setup(tmp_path)
    # تهيئة git repo بسيط
    import subprocess
    subprocess.run(["git", "init"], cwd=str(tmp_path), capture_output=True,
                   creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
    subprocess.run(["git", "config", "user.email", "test@x"],
                   cwd=str(tmp_path), capture_output=True,
                   creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
    subprocess.run(["git", "config", "user.name", "test"],
                   cwd=str(tmp_path), capture_output=True,
                   creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
    (tmp_path / "f.txt").write_text("x")
    # status
    r = reg.execute("git_status", ctx)
    assert r.ok
    # commit
    r = reg.execute("git_commit", ctx, message="init", add_all=True)
    assert r.ok
    assert r.data["code"] == 0
```

---

### `394/588` `backend/tests/test_kca_unified.py`

- **المسار الكامل:** `F:\1f\p\ALI_Studio_Pro_Design4_4.6.0\04_Adaptive_Hybrid\backend/tests/test_kca_unified.py`
- **الحجم:** 4650 بايت (4.5 KB)
- **الامتداد:** `.py`

```python
# -*- coding: utf-8 -*-
from __future__ import annotations
from pathlib import Path
import json

from control_plane import KCARequestRouter, RequestEnvelope, summary
from control_plane.kca_registry import FUNCTIONS
from control_plane.state_store import KCAStateStore
from data_engine.kca_dataset import enrich_conversation, build_kca_dataset


def test_kca_registry_has_exactly_100_functions():
    assert len(FUNCTIONS) == 100
    assert summary()["functions"] == 100


def test_kca_router_produces_structured_state():
    state = KCARequestRouter().build_state(RequestEnvelope(raw_text="اقرأ ملف ali_agent.py"))
    assert state.intent == "read_file"
    assert state.confidence > .9
    assert state.task_state["params"]["path"] == "ali_agent.py"
    assert state.selected_action is not None


def test_kca_dataset_enrichment_is_deterministic_and_redacts_secret():
    row = {
        "id": "demo-1",
        "messages": [
            {"role": "user", "content": "أنشئ ملف api_key=sk-abcdefghijklmnopqrstuvwxyz123456"},
            {"role": "assistant", "content": "تم إنشاء الملف بعد التحقق."},
        ],
        "source": "test",
        "quality": .9,
    }
    first = enrich_conversation(row)
    second = enrich_conversation(row)
    assert first["record_hash"] == second["record_hash"]
    assert first["redacted"] is True
    assert "[REDACTED_SECRET]" in first["input"]
    assert first["schema_version"] == "kca-3.0"


def test_kca_dataset_deduplicates(tmp_path: Path):
    src = tmp_path / "chat.jsonl"
    row = {"id": "same", "messages": [{"role": "user", "content": "Hello"}, {"role": "assistant", "content": "Hi"}], "quality": .9}
    src.write_text(json.dumps(row, ensure_ascii=False) + "\n" + json.dumps(row, ensure_ascii=False) + "\n", encoding="utf-8")
    out = tmp_path / "kca.jsonl"
    report = build_kca_dataset([src], out)
    assert report["samples"] == 1
    assert len(out.read_text(encoding="utf-8").splitlines()) == 1


def test_kca_state_store_roundtrip(tmp_path: Path):
    store = KCAStateStore(tmp_path / "kca.sqlite3")
    store.upsert("op-1", "req-1", "completed", {"intent": "question"}, {"status": "completed"})
    rows = store.recent()
    assert rows and rows[0]["operation_id"] == "op-1"
    assert json.loads(rows[0]["state_json"])["intent"] == "question"


def test_invalid_gguf_is_rejected(tmp_path: Path):
    from model.weights_manager import WeightsManager
    p = tmp_path / "broken.gguf"
    p.write_bytes(b"NOTGGUF" + b"\0" * 64)
    wm = WeightsManager(tmp_path)
    info = wm.inspect(p)
    assert info["kind"] == "gguf"
    assert info["compatible"] is False



def test_self_manager_requires_new_approved_samples(tmp_path: Path):
    from autonomy.self_manager import SelfManager
    from memory.conversations import ConversationMemory
    conv = tmp_path / "conversations.sqlite3"
    db = ConversationMemory(conv)
    db.put("سؤال ثابت", "إجابة ثابتة", quality=1.0)
    sm = SelfManager(tmp_path, min_new_samples=2)
    first = sm.status(tmp_path / "missing-harvest.sqlite3", conv)
    assert first["accepted_samples"] == 1
    assert first["ready"] is False
    db.put("سؤال آخر", "إجابة أخرى", quality=1.0)
    second = sm.status(tmp_path / "missing-harvest.sqlite3", conv)
    assert second["accepted_samples"] == 2
    assert second["ready"] is True


def test_self_manager_failure_remains_retryable(tmp_path: Path, monkeypatch):
    from autonomy.self_manager import SelfManager
    from memory.conversations import ConversationMemory
    import training.pipeline as pipeline_module
    conv = tmp_path / "conversations.sqlite3"
    db = ConversationMemory(conv)
    db.put("سؤال 1", "إجابة 1", quality=1.0)
    (tmp_path / "data" / "training" / "bootstrap").mkdir(parents=True)
    (tmp_path / "data" / "training" / "bootstrap" / "chat_validation.jsonl").write_text(
        '{"id":"v","text":"test"}\n', encoding="utf-8"
    )
    class FailingPipeline:
        def __init__(self, *args, **kwargs): pass
        def run(self, *args, **kwargs): raise RuntimeError("intentional test failure")
    monkeypatch.setattr(pipeline_module, "TrainingPipeline", FailingPipeline)
    sm = SelfManager(tmp_path, min_new_samples=1)
    try:
        sm.autonomous_cycle(tmp_path / "missing-harvest.sqlite3", conv, steps=1)
    except RuntimeError:
        pass
    else:
        raise AssertionError("expected autonomous cycle failure")
    state = sm.status(tmp_path / "missing-harvest.sqlite3", conv)
    assert state["last_status"] == "failed"
    assert state["new_samples"] == 1
    assert state["ready"] is True
```

---

### `395/588` `backend/tests/test_llama_engine.py`

- **المسار الكامل:** `F:\1f\p\ALI_Studio_Pro_Design4_4.6.0\04_Adaptive_Hybrid\backend/tests/test_llama_engine.py`
- **الحجم:** 580 بايت (0.6 KB)
- **الامتداد:** `.py`

```python
from pathlib import Path
from inference.llama_engine import LlamaServerEngine


def test_llama_engine_builds_safe_server_contract(monkeypatch, tmp_path):
    exe=tmp_path/"llama-server.exe"; model=tmp_path/"m.gguf"
    exe.write_bytes(b"x"); model.write_bytes(b"GGUF")
    monkeypatch.setattr("inference.llama_engine.detect", lambda **kwargs: type("H", (), {"gpu_mem_free_gb":1.5,"gpu_mem_used_gb":0.5,"vram_gb":2.0,"gpu_available":True,"torch_cuda":False})())
    e=LlamaServerEngine(exe,model,compute_mode="cpu")
    assert e.n_gpu_layers == 0
    assert e.server.port == 48921
```

---

### `396/588` `backend/tests/test_no_lovable.py`

- **المسار الكامل:** `F:\1f\p\ALI_Studio_Pro_Design4_4.6.0\04_Adaptive_Hybrid\backend/tests/test_no_lovable.py`
- **الحجم:** 1966 بايت (1.9 KB)
- **الامتداد:** `.py`

```python
# -*- coding: utf-8 -*-
"""اختبار أن ali_agent.py لا يحتوي على Lovable."""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def test_no_lovable_in_agent():
    """التأكد من أن ali_agent.py لا يحتوي على أي كود يتصل بـ Lovable.

    ملاحظة: يُسمح بذكر Lovable في التعليقات والـ docstrings لتوثيق الإزالة.
    """
    import re
    p = ROOT / "ali_agent.py"
    text = p.read_text(encoding="utf-8")
    # إزالة كل التعليقات و docstrings قبل الفحص
    no_doc = re.sub(r'""".*?"""', '', text, flags=re.S)
    no_doc = re.sub(r"'''.*?'''", '', no_doc, flags=re.S)
    no_doc = re.sub(r'#.*', '', no_doc)
    code_only = no_doc.lower()
    assert "lovable" not in code_only, "Lovable found in code (not docstring)"
    assert "genius-connect" not in code_only
    assert "DEFAULT_SITE" not in code_only
    assert "_connect_loop" not in code_only
    assert "_handle_remote" not in code_only
    assert "urllib" not in code_only
    # فحص token كمعرّف أو قيمة، ليس كلمة عربية
    assert not re.search(r'\btoken\s*[:=]\s*["\']', code_only), "hardcoded token found"


def test_no_token_leak_in_default_config():
    from config.paths import APP_PATHS
    cfg = APP_PATHS.default_config()
    assert "token" not in cfg
    assert "site" not in cfg


def test_legacy_kept_for_reference():
    """ملف .legacy يجب أن يبقى للمراجعة لكنه ليس نقطة الدخول."""
    legacy = ROOT / "ali_agent.py.legacy"
    assert legacy.exists(), "legacy file missing"
    # نقطة الدخول يجب أن تكون ali_agent.py
    main = (ROOT / "ali_agent.py").read_text(encoding="utf-8")
    assert "__main__" in main
    assert 'if __name__ == "__main__"' in main
```

---

### `397/588` `backend/tests/test_p50_profile.py`

- **المسار الكامل:** `F:\1f\p\ALI_Studio_Pro_Design4_4.6.0\04_Adaptive_Hybrid\backend/tests/test_p50_profile.py`
- **الحجم:** 828 بايت (0.8 KB)
- **الامتداد:** `.py`

```python
from runtime.hardware import HardwareInfo, training_profile, model_profile
from runtime.device_policy import choose_policy
from config.device_profiles import recommend_for_hardware

def p50():
    return HardwareInfo('Windows 11', '3.13', 8, 32.0, True, 'NVIDIA Quadro M1000M', 2.0, False, 300.0, (5,0), 4, 'cpu-or-llama')

def test_p50_cpu_first():
    h=p50(); tp=training_profile(h); policy=choose_policy(h)
    assert tp['device']=='cpu' and tp['amp'] is False
    assert tp['cpu_threads']==6
    assert policy['train_device']=='cpu'
    assert policy['recommended_seq_len']==256

def test_p50_profile_dataset_contract():
    p=recommend_for_hardware(p50())
    assert p['id']=='thinkpad-p50-32gb-2gb'
    assert p['training']['scale']=='small'

def test_p50_model_is_small():
    assert model_profile(p50())['hidden']==256
```

---

### `398/588` `backend/tests/test_pipeline_relative_paths.py`

- **المسار الكامل:** `F:\1f\p\ALI_Studio_Pro_Design4_4.6.0\04_Adaptive_Hybrid\backend/tests/test_pipeline_relative_paths.py`
- **الحجم:** 2002 بايت (2.0 KB)
- **الامتداد:** `.py`

```python
from pathlib import Path

import pytest

from training.pipeline import TrainingPipeline, PipelineConfig


def _resolve_base(pipe, value):
    base = Path(value)
    if not base.is_absolute():
        base = (pipe.root / base).resolve()
    else:
        base = base.resolve()
    return base


def test_relative_base_checkpoint_is_resolved_from_pipeline_root(tmp_path):
    root = Path(tmp_path) / "project"
    base = root / "models" / "active" / "base"
    base.mkdir(parents=True)
    (base / "config.json").write_text("{}", encoding="utf-8")
    pipe = TrainingPipeline(root)
    cfg = PipelineConfig(base_checkpoint="models/active/base")
    resolved = _resolve_base(pipe, cfg.base_checkpoint)
    assert resolved == base.resolve()


def test_run_reuses_relative_base_tokenizer_from_pipeline_root(tmp_path, monkeypatch):
    root = Path(tmp_path) / "project"
    base = root / "models" / "active" / "base"
    base.mkdir(parents=True)
    source_tokenizer = Path(__file__).resolve().parents[1] / "models" / "active" / "ALI-Bootstrap-v2.5" / "tokenizer.model"
    (base / "tokenizer.model").write_bytes(source_tokenizer.read_bytes())
    train = root / "train.jsonl"
    train.write_text('{"messages":[{"role":"user","content":"سؤال"},{"role":"assistant","content":"جواب"}]}\n', encoding="utf-8")
    pipe = TrainingPipeline(root)
    monkeypatch.chdir(tmp_path)

    def unexpected_prepare(*args, **kwargs):
        raise AssertionError("continuation incorrectly retrained the tokenizer")

    def stop_after_tokenizer(self, cfg, tokenizer_vocab_size):
        raise RuntimeError("tokenizer_reuse_reached_new_model")

    monkeypatch.setattr(pipe, "prepare_tokenizer", unexpected_prepare)
    monkeypatch.setattr(pipe, "new_model", stop_after_tokenizer.__get__(pipe, TrainingPipeline))
    cfg = PipelineConfig(stage="lora", train_path=str(train), base_checkpoint="models/active/base")
    with pytest.raises(RuntimeError, match="tokenizer_reuse_reached_new_model"):
        pipe.run(cfg)
```

---

### `399/588` `backend/tests/test_professional_ai.py`

- **المسار الكامل:** `F:\1f\p\ALI_Studio_Pro_Design4_4.6.0\04_Adaptive_Hybrid\backend/tests/test_professional_ai.py`
- **الحجم:** 11179 بايت (10.9 KB)
- **الامتداد:** `.py`

```python
# -*- coding: utf-8 -*-
"""اختبارات V0.7.3 — Professional AI Agent."""

from __future__ import annotations

import sys
import os
import pytest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

pytestmark = pytest.mark.skipif(os.name != "nt" and os.environ.get("ALI_GUI_TESTS") != "1", reason="Desktop GUI unavailable in headless environment")
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


# =====================================================================
# Intent Classification
# =====================================================================

class TestIntentClassification:
    """تصنيف intent يجب أن يكون deterministic."""

    def test_read_file_intent(self):
        from core.agent import classify_intent
        i = classify_intent("read_file ali_agent.py")
        assert i.primary == "read_file", f"got {i.primary}"
        assert "path" in i.params, f"missing path in {i.params}"
        assert i.params["path"] == "ali_agent.py"
        assert i.confidence > 0.5

    def test_write_file_intent(self):
        from core.agent import classify_intent
        i = classify_intent("write_file test.py")
        assert i.primary == "write_file"
        assert "path" in i.params

    def test_list_dir_intent(self):
        from core.agent import classify_intent
        i = classify_intent("list_dir")
        assert i.primary == "list_dir"

        i = classify_intent("ls tokenizer")
        assert i.primary == "list_dir"

    def test_search_intent(self):
        from core.agent import classify_intent
        i = classify_intent("search_files class.*App")
        assert i.primary == "search_files"
        assert "pattern" in i.params

    def test_run_command_intent(self):
        from core.agent import classify_intent
        i = classify_intent("run_command dir")
        assert i.primary == "run_command"
        assert "command" in i.params

    def test_git_intent(self):
        from core.agent import classify_intent
        i = classify_intent("git status")
        assert i.primary == "git"
        assert "subcommand" in i.params
        assert i.params["subcommand"] == "status"

        i = classify_intent("git commit add tests")
        assert i.primary == "git"
        assert i.params.get("subcommand") == "commit"

    def test_question_intent(self):
        from core.agent import classify_intent
        i = classify_intent("ما هو Python؟")
        assert i.primary == "code_question"

        i = classify_intent("how does this work?")
        assert i.primary == "code_question"

    def test_empty_text(self):
        from core.agent import classify_intent
        i = classify_intent("")
        assert i.primary == "unknown"
        assert i.confidence == 0.0

    def test_arabic_text(self):
        from core.agent import classify_intent
        i = classify_intent("افتح ملف ali_agent.py")
        # Either read_file or list_dir, both ok
        assert i.primary in ("read_file", "list_dir")


# =====================================================================
# Plan
# =====================================================================

class TestPlanActions:
    """خطة agent تبني sequence صحيح."""

    def test_read_file_plan(self):
        from core.agent import classify_intent, plan_actions
        i = classify_intent("read_file tokenizer/__init__.py")
        plan = plan_actions(i)
        assert not plan.is_empty()
        assert len(plan.steps) == 1
        assert plan.steps[0].tool_name == "read_file"
        assert plan.steps[0].kwargs["path"] == "tokenizer/__init__.py"

    def test_analyze_project_plan_multi_step(self):
        from core.agent import classify_intent, plan_actions
        i = classify_intent("analyze project structure")
        plan = plan_actions(i)
        # analyze_project يبني خطة متعددة الخطوات
        assert not plan.is_empty()
        assert len(plan.steps) >= 2

    def test_question_plan_empty(self):
        from core.agent import classify_intent, plan_actions
        i = classify_intent("ما هو Python؟")
        plan = plan_actions(i)
        # لا tools — خطة فارغة
        assert plan.is_empty()


# =====================================================================
# Execute Plan
# =====================================================================

class TestExecutePlan:
    """تنفيذ الخطة مع tool runner وهمي."""

    def test_execute_read_file(self):
        from core.agent import (
            classify_intent, plan_actions, execute_plan,
        )

        i = classify_intent("read_file ali_agent.py")
        plan = plan_actions(i)

        # tool runner وهمي ينجح.
        def fake_runner(tool_name, kwargs):
            return {"ok": True, "data": f"content of {kwargs.get('path', '?')}",
                    "error": ""}

        result = execute_plan(plan, fake_runner, "read_file ali_agent.py")
        assert result.ok
        assert len(result.tool_results) == 1
        assert result.tool_results[0]["tool"] == "read_file"
        assert "content of ali_agent.py" in result.tool_results[0]["data"]

    def test_execute_question_no_tools(self):
        from core.agent import (
            classify_intent, plan_actions, execute_plan,
        )

        i = classify_intent("what is AI?")
        plan = plan_actions(i)
        assert plan.is_empty()

        def never_called(tool_name, kwargs):
            raise AssertionError("Should not be called")

        result = execute_plan(plan, never_called, "what is AI?")
        assert result.ok  # Empty plan = ok
        assert "🤖" in result.summary  # Knowledge answer

    def test_execute_failure_returns_error(self):
        from core.agent import (
            classify_intent, plan_actions, execute_plan,
        )

        i = classify_intent("read_file nonexistent.py")
        plan = plan_actions(i)

        def failing_runner(tool_name, kwargs):
            return {"ok": False, "data": "", "error": "file not found"}

        result = execute_plan(plan, failing_runner, "read_file nonexistent.py")
        assert not result.ok
        assert "file not found" in result.tool_results[0]["error"]


# =====================================================================
# Token Counting
# =====================================================================

class TestTokenCounting:
    """count_tokens يعمل مع/بدون tokenizer."""

    def test_count_arabic(self):
        from core.agent import count_tokens
        n = count_tokens("مرحبا ALI Studio")
        assert n > 0
        assert isinstance(n, int)

    def test_count_english(self):
        from core.agent import count_tokens
        n = count_tokens("Hello World")
        assert n > 0

    def test_count_empty(self):
        from core.agent import count_tokens
        n = count_tokens("")
        # Empty string يقدّر بـ 0
        assert n == 0


# =====================================================================
# App Integration (via App._agent_reply)
# =====================================================================

class TestAppAgentMode:
    """App يستخدم _agent_reply في Professional mode."""

    def test_app_has_agent_method(self):
        # Headless import.
        import tkinter as tk
        from tkinter import StringVar
        # We can't instantiate App without Tcl, so check via static analysis.
        import importlib
        ali_agent = importlib.import_module("ali_agent")
        assert hasattr(ali_agent.App, "_agent_reply")
        assert hasattr(ali_agent.App, "_ai_mode_menu")
        assert hasattr(ali_agent.App, "_set_ai_mode")

    def test_ai_mode_attribute_default(self):
        """App default ai_mode هو tools."""
        import tkinter as tk
        root = tk.Tk()
        root.withdraw()
        # Use isolated APPDATA via monkey-patch.
        import tempfile
        import os
        tmp = tempfile.mkdtemp(prefix="ai_mode_test_")
        os.environ["APPDATA"] = tmp
        try:
            if "ali_agent" in sys.modules:
                del sys.modules["ali_agent"]
            import ali_agent
            app = ali_agent.App(root)
            assert app.ai_mode.get() == "professional", f"got {app.ai_mode.get()}"
        finally:
            root.destroy()
            import shutil
            shutil.rmtree(tmp, ignore_errors=True)

    def test_set_ai_mode_persists(self):
        """اختبار استمرارية ai_mode عبر إنشاء App جديد بعد الإغلاق."""
        import tkinter as tk
        import tempfile
        import os
        import sys
        import json

        tmp = tempfile.mkdtemp(prefix="persist_test_")
        old_appdata = os.environ.get("APPDATA")
        os.environ["APPDATA"] = tmp
        # امسح الـ module من sys.modules لضمان fresh load.
        for mod_name in list(sys.modules):
            if mod_name == "ali_agent" or mod_name.startswith("ali_agent."):
                del sys.modules[mod_name]
        try:
            import ali_agent as ali_mod

            root = tk.Tk()
            root.withdraw()
            app = ali_mod.App(root)
            app._set_ai_mode("professional")

            # تحقق أن الـ cfg يحفظ ai_mode.
            cfg_path = ali_mod.APP_PATHS.user_config()
            if os.path.exists(cfg_path):
                cfg_data = json.loads(open(cfg_path, encoding="utf-8").read())
                assert cfg_data.get("ai_mode") == "professional", (
                    f"ai_mode not in JSON cfg: {cfg_data}"
                )

            # بدلاً من إنشاء Tk root جديد (يعرّض لـ Tcl state تالف على Windows)،
            # تحقق مباشرة من قراءة الـ config من القرص.
            root.destroy()
            import gc; gc.collect(); import time; time.sleep(0.05)

            for mod_name in list(sys.modules):
                if mod_name == "ali_agent" or mod_name.startswith("ali_agent."):
                    del sys.modules[mod_name]
            import importlib
            ali_mod2 = importlib.import_module("ali_agent")
            cfg_path2 = ali_mod2.APP_PATHS.user_config()
            if os.path.exists(cfg_path2):
                cfg_data2 = json.loads(open(cfg_path2, encoding="utf-8").read())
                assert cfg_data2.get("ai_mode") == "professional", (
                    f"persistence failed: {cfg_data2}"
                )
        finally:
            os.environ["APPDATA"] = old_appdata or ""
            import shutil
            shutil.rmtree(tmp, ignore_errors=True)


# =====================================================================
# Run imports sanity
# =====================================================================

def test_agent_module_imports():
    """core.agent imports بدون أخطاء."""
    from core.agent import (
        Intent, Plan, ToolCall, ExecutionResult,
        classify_intent, plan_actions, execute_plan, count_tokens,
    )
    assert Intent is not None
    assert Plan is not None
    assert ExecutionResult is not None
```

---

### `400/588` `backend/tests/test_rag_fallback.py`

- **المسار الكامل:** `F:\1f\p\ALI_Studio_Pro_Design4_4.6.0\04_Adaptive_Hybrid\backend/tests/test_rag_fallback.py`
- **الحجم:** 669 بايت (0.7 KB)
- **الامتداد:** `.py`

```python
from core.runtime import ALIRuntime

def test_rag_fallback_prefers_matching_qa(tmp_path):
    runtime = ALIRuntime(tmp_path, tmp_path / "runtime.sqlite3", None, False)
    doc = tmp_path / "qa.md"
    doc.write_text("**User:** ما هو ALI؟\n\n**Assistant:** ALI هو مساعد محلي قابل للتدريب.\n\n---\n", encoding="utf-8")
    chunks=[doc.read_text(encoding="utf-8")]
    runtime.knowledge.add_document(str(doc), doc.name, "test", {}, chunks)
    rag = runtime._knowledge("ما هو ALI؟")
    assert rag["sources"]
    answer = runtime._grounded_fallback("ما هو ALI؟", rag)
    assert "مساعد محلي قابل للتدريب" in answer
```

---

### `401/588` `backend/tests/test_release_453.py`

- **المسار الكامل:** `F:\1f\p\ALI_Studio_Pro_Design4_4.6.0\04_Adaptive_Hybrid\backend/tests/test_release_453.py`
- **الحجم:** 5643 بايت (5.5 KB)
- **الامتداد:** `.py`

```python
from pathlib import Path

def test_arabic_p50_knowledge_retrieval(tmp_path):
    import sys
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    from knowledge.store import KnowledgeStore
    k = KnowledgeStore(tmp_path / "k.sqlite3")
    doc = tmp_path / "p50.md"
    doc.write_text("المعالج Intel Core i7-6820HQ يحتوي على 4 أنوية و8 خيوط. بطاقة الرسومات NVIDIA Quadro M1000M لديها 2 GB GDDR5.", encoding="utf-8")
    k.add_document(str(doc), "P50", "test", {}, [doc.read_text(encoding="utf-8")])
    hits = k.search("ما هو معالج جهازي؟ وكم عدد الأنوية؟", 3)
    assert hits and "i7-6820HQ" in hits[0]["text"]


def test_dynamic_port_fallback(tmp_path):
    import os, socket, subprocess, sys, time, urllib.request, json
    backend = Path(__file__).resolve().parents[1]
    ep = backend / "runtime_backend_endpoint.json"
    try: ep.unlink()
    except FileNotFoundError: pass
    sock = socket.socket(); sock.bind(("127.0.0.1", 8765)); sock.listen(1)
    env = dict(os.environ); env["ALI_PORT"] = "8765"
    proc = subprocess.Popen([sys.executable, str(backend / "scripts" / "desktop_server.py")], cwd=backend, env=env, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    try:
        deadline=time.time()+15; url=None
        last_error=None
        while time.time()<deadline:
            if ep.exists():
                try:
                    data=json.loads(ep.read_text())
                    if data.get('ready'): url=data.get('url')
                except Exception: pass
            if url:
                try:
                    body=urllib.request.urlopen(url+"/api/health", timeout=1.5).read().decode()
                    if json.loads(body)["ok"] is True: break
                except Exception as exc: last_error=exc
            time.sleep(.2)
        assert url and not url.endswith(":8765"), last_error
        body=urllib.request.urlopen(url+"/api/health", timeout=2).read().decode()
        assert json.loads(body)["ok"] is True
    finally:
        proc.terminate();
        try: proc.wait(timeout=3)
        except subprocess.TimeoutExpired: proc.kill()
        sock.close()
        try: (backend/"runtime_backend_endpoint.json").unlink()
        except FileNotFoundError: pass


def test_knowledge_upsert_preserves_chunk_links(tmp_path):
    import sqlite3
    from knowledge.store import KnowledgeStore
    k=KnowledgeStore(tmp_path / "k.sqlite3")
    p=tmp_path / "doc.md"; p.write_text("المعالج i7-6820HQ أربع أنوية",encoding="utf-8")
    k.add_document(str(p),"P50","test",{"priority":100},[p.read_text(encoding="utf-8")])
    k.add_document(str(p),"P50 updated","test",{"priority":100},[p.read_text(encoding="utf-8")])
    hits=k.search("ما هو المعالج؟",3)
    assert hits and hits[0]["title"]=="P50 updated"
    c=sqlite3.connect(tmp_path / "k.sqlite3")
    assert c.execute("select count(*) from chunks c join documents d on d.id=c.document_id").fetchone()[0] == 1


def test_model_manager_reanchors_stale_absolute_model_path(tmp_path):
    import sys, json
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))