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
    from model.registry import ModelRegistry
    from model.manager import ModelManager
    root = tmp_path / 'root'; root.mkdir()
    model_dir = root / 'models' / 'active' / 'ALI-Bootstrap-v2.5'
    model_dir.mkdir(parents=True)
    (model_dir / 'config.json').write_text(json.dumps({"vocab_size": 8}), encoding='utf-8')
    reg = ModelRegistry(root / 'registry.sqlite3')
    stale = str(tmp_path / 'old' / 'installation' / 'backend' / 'models' / 'active' / 'ALI-Bootstrap-v2.5')
    reg.register('ALI','2.5.0-bootstrap-micro', artifact_type='base', status='active', hf_dir=stale, checkpoint=stale)
    mgr = ModelManager(root, reg)
    row = mgr.discover_active()
    assert row and row['hf_dir'] == str(model_dir.resolve())


def test_markdown_conversation_import_parses_explicit_pairs(tmp_path):
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    from training.continuous_learning import ContinuousLearningManager
    from model.registry import ModelRegistry
    md = tmp_path / 'conversation.md'
    md.write_text('## المحادثة 1\n\n**User:** ما هو RAG؟\n\n**Assistant:** هو الاسترجاع المعزز بالتوليد.\n\n---\n\n## المحادثة 2\n\n**User:** كيف يعمل v1؟\n\n**Assistant:** يبدأ من النموذج النشط السابق ويستخدم بيانات جديدة.\n', encoding='utf-8')
    root = tmp_path / 'root'; root.mkdir()
    mgr = ContinuousLearningManager(root, ModelRegistry(root / 'models.sqlite3'))
    result = mgr.import_files([md])[0]
    assert result['status'] == 'validated'
    assert result['sample_count'] == 2


def test_all_existing_samples_are_reported_as_duplicate_not_rag_only(tmp_path):
    import sys, json
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    from training.continuous_learning import ContinuousLearningManager
    from model.registry import ModelRegistry
    root = tmp_path / 'root'; root.mkdir()
    mgr = ContinuousLearningManager(root, ModelRegistry(root / 'models.sqlite3'))
    md = tmp_path / 'conversation.md'
    md.write_text('**User:** سؤال فريد\n\n**Assistant:** جواب فريد.\n', encoding='utf-8')
    first = mgr.import_files([md])[0]
    assert first['status'] == 'validated' and first['sample_count'] == 1
    second = mgr.import_files([md])[0]
    assert second['status'] == 'duplicate'
