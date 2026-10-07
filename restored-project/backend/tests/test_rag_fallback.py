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
