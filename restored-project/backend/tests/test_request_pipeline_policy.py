from types import SimpleNamespace
from core.request_pipeline import RequestPipeline

def test_execution_is_independent_from_training_admission():
    h=SimpleNamespace(ram_gb=32,ram_available_gb=10,cpu_threads=8,vram_gb=2,cuda_capability=(5,0),battery_percent=20,power_plugged=False,temperature_c=45)
    out=RequestPipeline(h).prepare("عدل المشروع ثم اختبره")
    assert out["runtime_policy"]["training_enabled"] is False
    assert out["execution_allowed"] is True

def test_arabic_project_terms_route_to_project():
    h=SimpleNamespace(ram_gb=32,ram_available_gb=10,cpu_threads=8,vram_gb=2,cuda_capability=(5,0),battery_percent=80,power_plugged=True,temperature_c=45)
    out=RequestPipeline(h).prepare("عدّل المشروع ثم اختبره")
    assert "project" in out["request"]["required_tools"]
