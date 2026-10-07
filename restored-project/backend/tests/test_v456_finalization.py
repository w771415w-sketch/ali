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
