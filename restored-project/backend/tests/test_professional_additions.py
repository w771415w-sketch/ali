from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).parents[1]))
from control_plane.document_ingestion import DocumentIngestor
from control_plane.knowledge import KnowledgeBase
from control_plane.retrieval import HybridRetriever
from control_plane.model_runtime import ModelRuntime
from control_plane.multimodal import MultimodalCapabilities
from control_plane.code_intelligence import CodeIntelligence

def test_document_ingestion_and_retrieval(tmp_path):
    kb=KnowledgeBase(tmp_path/"kb")
    p=tmp_path/"notes.txt";p.write_text("Inventory sales and purchases must stay consistent.",encoding="utf-8")
    r=DocumentIngestor(kb).ingest(p)
    assert r["chunks_added"]==1
    hit=HybridRetriever(kb).search("inventory sales")
    assert hit["results"] and hit["mode"]=="lexical"

def test_runtime_capabilities_are_explicit(tmp_path):
    gg=ModelRuntime().inspect_gguf(tmp_path/"missing.gguf")
    assert gg["ok"] is False and gg["status"]=="not_found"
    caps=MultimodalCapabilities().inspect()
    assert isinstance(caps,dict) and "PIL" in caps

def test_project_search(tmp_path):
    (tmp_path/"a.py").write_text("def hello():\n    return 1\n",encoding="utf-8")
    (tmp_path/"b.txt").write_text("hello world",encoding="utf-8")
    assert "a.py" in CodeIntelligence().search(tmp_path,"hello")


def test_training_bridge(tmp_path):
    from control_plane.training_bridge import TrainingBridge
    bridge=TrainingBridge(tmp_path/"jobs.json")
    plan=bridge.plan({"ram_gb":32,"vram_gb":2,"cpu_threads":8},"micro",5)
    assert plan["ok"] and plan["plan"]["training"]["scale"]=="micro"
    job=bridge.create_job("demo")
    assert job["status"] in {"running","queued"}
