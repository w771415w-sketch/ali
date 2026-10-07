from pathlib import Path
import json,sys,zipfile
sys.path.insert(0,str(Path(__file__).parents[1]))
from config.language_settings import LanguageSettingsManager
from conversation_intelligence.language_adapter import ArabicLanguageAdapter
from diagnostics.engine import DiagnosticsEngine
from diagnostics.root_cause import classify_error,next_checks
from model import GGUFConverter
from training.lifecycle import TrainingLifecycle,TrainingLifecycleError
from training.controller import TrainingController
from training.continual_dataset import ContinualDataset
from control_plane.runtime_facade import ProfessionalRuntime
def test_language_profiles_and_correction(tmp_path):
    base=Path(__file__).parents[1];c=tmp_path/"language_profiles.json";c.write_text((base/"config/language_profiles.json").read_text(encoding="utf-8"),encoding="utf-8");s=tmp_path/"settings.json";s.write_text("{}",encoding="utf-8")
    m=LanguageSettingsManager(c,s);assert m.validate("ar-YE")["label_ar"]=="العربية اليمنية";assert m.save("ar-EG")["profile"]["id"]=="ar-EG"
    r=ArabicLanguageAdapter(c,"ar-SA").adapt("للبرانامج ابغى يكون سريع");assert "للبرنامج" in r["normalized"] and r["response_profile"]=="ar-SA"
def test_archive_diagnostics(tmp_path):
    z=tmp_path/"x.zip"
    with zipfile.ZipFile(z,"w") as f:f.writestr("a.py","print(1)\n");f.writestr("../evil.txt","bad")
    r=DiagnosticsEngine().inspect_archive(z);assert not r["safe"] and any(x.get("kind")=="zip_slip" for x in r["errors"] if isinstance(x,dict))
def test_training_source_rejects_gguf(tmp_path):
    t=TrainingLifecycle(tmp_path);g=tmp_path/"model.gguf";g.write_bytes(b"GGUF")
    try:t.verify_training_source(g);assert False
    except TrainingLifecycleError:pass
def test_converter_dry_run(): assert "converter_script" in GGUFConverter("/missing/llama.cpp").discover()
def test_training_controller_options(tmp_path):
    h={"ram_gb":32,"vram_gb":2,"cpu_threads":8,"cuda_capability":(5,0)};tc=TrainingController(tmp_path,Path(__file__).parents[1]/"config");o=tc.options(h)
    assert any(x["id"]=="lora_continue_cpu" and x["available"] for x in o["training_methods"]);assert any(x["id"]=="q4_k_m" and x["recommended"] for x in o["conversion_profiles"]);assert not any(x["id"]=="qlora_gpu" and x["available"] for x in o["training_methods"])
def test_root_cause():r=classify_error("ModuleNotFoundError: No module named 'torch'");assert r["kind"]=="missing_dependency" and next_checks(r["kind"])
def test_runtime_settings_and_language(tmp_path):
    rt=ProfessionalRuntime(tmp_path);s=rt.settings_snapshot();assert s["language_profile"]=="ar-SA";assert any(x["id"]=="lora_cpu" for x in s["training_methods"]);assert rt.adapt_language("أشتي برنامج مخزن")["detected"]["profile"] in {"ar-YE","ar-SA","ar-MSA"};rt.close()
def test_continual_dataset_replay(tmp_path):
    old=tmp_path/"old.jsonl";new=tmp_path/"new.jsonl";old.write_text(json.dumps({"messages":[{"role":"user","content":"old"},{"role":"assistant","content":"a"}]})+"\n");new.write_text(json.dumps({"messages":[{"role":"user","content":"new"},{"role":"assistant","content":"b"}]})+"\n")
    r=ContinualDataset(tmp_path/"out").merge(old,new,"v2");assert r["records"]==2 and r["replay_records"]==1
def test_gguf_magic(tmp_path):
    p=tmp_path/"m.gguf";p.write_bytes(b"GGUF"+b"\0"*10);assert GGUFConverter.verify_gguf(p)["ok"]
