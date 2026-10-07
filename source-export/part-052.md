    return text


def _search_duckduckgo(query: str, limit: int) -> list[SearchResult]:
    html, _ = _fetch("https://html.duckduckgo.com/html/?q=" + quote(query), timeout=15)
    blocks = re.findall(
        r'<div[^>]+class="result"[^>]*>(.*?)</div>\s*</div>',
        html,
        flags=re.S | re.I,
    )
    if not blocks:
        blocks = re.findall(r'<a[^>]+class="result__a"[^>]*>.*?</a>', html, flags=re.S | re.I)
    out: list[SearchResult] = []
    seen: set[str] = set()
    for block in blocks:
        m = re.search(r'<a[^>]+class="result__a"[^>]+href="([^"]+)"[^>]*>(.*?)</a>', block, re.S | re.I)
        if not m:
            m = re.search(r'<a[^>]+href="([^"]+)"[^>]+class="result__a"[^>]*>(.*?)</a>', block, re.S | re.I)
        if not m:
            continue
        url = unescape(m.group(1))
        try:
            params = parse_qs(urlparse(url).query)
            url = unquote(params.get("uddg", [url])[0])
        except Exception:
            pass
        if not url.startswith(("http://", "https://")) or url in seen:
            continue
        title = _strip_html(m.group(2))
        sm = re.search(r'class="result__snippet"[^>]*>(.*?)</(?:a|span|div)>', block, re.S | re.I)
        snippet = _strip_html(sm.group(1)) if sm else ""
        seen.add(url)
        out.append(SearchResult(title or url, url, snippet, "duckduckgo", len(out) + 1))
        if len(out) >= limit:
            break
    return out


def _search_bing(query: str, limit: int) -> list[SearchResult]:
    html, _ = _fetch("https://www.bing.com/search?q=" + quote(query), timeout=15)
    out: list[SearchResult] = []
    for block in re.findall(r'<li[^>]+class="b_algo"[^>]*>(.*?)</li>', html, re.S | re.I):
        m = re.search(r'<h2[^>]*>\s*<a[^>]+href="([^"]+)"[^>]*>(.*?)</a>', block, re.S | re.I)
        if not m:
            continue
        url = unescape(m.group(1))
        if not url.startswith(("http://", "https://")):
            continue
        title = _strip_html(m.group(2))
        sm = re.search(r'<p[^>]*>(.*?)</p>', block, re.S | re.I)
        snippet = _strip_html(sm.group(1)) if sm else ""
        out.append(SearchResult(title or url, url, snippet, "bing", len(out) + 1))
        if len(out) >= limit:
            break
    return out


def search(query: str, limit: int = 8) -> list[SearchResult]:
    q = clean_query(query)
    if not q:
        return []
    limit = max(1, min(int(limit or 8), 10))
    errors: list[str] = []
    try:
        results = _search_duckduckgo(q, limit)
        if results:
            return results
    except Exception as exc:
        errors.append(f"duckduckgo: {exc}")
    try:
        results = _search_bing(q, limit)
        if results:
            return results
    except Exception as exc:
        errors.append(f"bing: {exc}")
    return [SearchResult("تعذر البحث عبر الإنترنت", "", " | ".join(errors) or "لا توجد نتائج", "search")]


def _extract_title(html: str, fallback: str) -> str:
    m = re.search(r"<title[^>]*>(.*?)</title>", html, re.S | re.I)
    return _strip_html(m.group(1)) if m else fallback


def _html_to_text(html: str) -> str:
    try:
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(html, "html.parser")
        for tag in soup(["script", "style", "noscript", "svg", "canvas", "template"]):
            tag.decompose()
        text = soup.get_text("\n")
    except Exception:
        text = re.sub(r"<script.*?</script>|<style.*?</style>|<noscript.*?</noscript>", "", html, flags=re.S | re.I)
        text = re.sub(r"<[^>]+>", " ", text)
    text = unescape(text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    text = re.sub(r"[ \t]+", " ", text)
    return text.strip()


def fetch_text(url: str, timeout: int = 20) -> dict[str, Any]:
    html, headers = _fetch(url, timeout)
    content_type = headers.get("content_type", "").lower()
    if content_type and not any(x in content_type for x in ("text/html", "application/xhtml+xml", "text/plain")):
        return {"url": url, "title": url, "text": "", "error": f"unsupported_content_type:{content_type}"}
    return {
        "url": url,
        "title": _extract_title(html, url),
        "text": _html_to_text(html)[:1_000_000],
    }


def research(query: str, limit: int = 5) -> dict[str, Any]:
    q = clean_query(query)
    results = search(q, limit)
    documents: list[dict[str, Any]] = []
    for result in results:
        if not result.url.startswith(("http://", "https://")):
            continue
        try:
            doc = fetch_text(result.url)
            if result.snippet and not doc.get("text"):
                doc["text"] = result.snippet
            doc["snippet"] = result.snippet
            doc["rank"] = result.rank
            doc["source"] = result.source
            documents.append(doc)
        except Exception as exc:
            documents.append({
                "url": result.url,
                "title": result.title,
                "text": result.snippet,
                "snippet": result.snippet,
                "rank": result.rank,
                "source": result.source,
                "error": str(exc),
            })
    return {
        "query": q,
        "results": [r.to_dict() for r in results],
        "documents": documents,
        "result_count": len(results),
        "fetched_count": sum(1 for d in documents if d.get("text")),
    }


def evidence_text(web: dict[str, Any], *, max_chars: int = 3000, max_sources: int = 3) -> str:
    """Compact evidence for a small local context window."""
    blocks: list[str] = []
    used = 0
    for i, doc in enumerate((web or {}).get("documents", [])[:max_sources], 1):
        text = re.sub(r"\s+", " ", str(doc.get("text") or doc.get("snippet") or "").strip())
        if not text:
            continue
        take = min(len(text), 700, max(0, max_chars - used))
        if take <= 0:
            break
        title = str(doc.get("title") or doc.get("url") or f"Web {i}")
        blocks.append(f"[W{i}] {title}\n{text[:take]}\nURL: {doc.get('url','')}")
        used += take
    return "\n\n".join(blocks)


def source_footer(web: dict[str, Any], *, language: str = "ar", max_sources: int = 5) -> str:
    docs = [d for d in (web or {}).get("documents", []) if d.get("url")][:max_sources]
    if not docs:
        return ""
    heading = "المصادر" if language.lower().startswith("ar") else "Sources"
    lines = [f"\n\n{heading}:"]
    for i, d in enumerate(docs, 1):
        title = str(d.get("title") or d.get("url") or "Source").strip()
        url = str(d.get("url") or "").strip()
        lines.append(f"[{i}] {title} — {url}")
    return "\n".join(lines)


def web_fallback(web: dict[str, Any], *, language: str = "ar") -> str:
    docs = [d for d in (web or {}).get("documents", []) if d.get("text")]
    if not docs:
        return "تعذر الحصول على مصادر من الإنترنت في الوقت الحالي." if language.lower().startswith("ar") else "No usable web sources were retrieved."
    intro = "اعتمدتُ على نتائج الإنترنت التالية، وهذه خلاصة أولية لما وجدته:" if language.lower().startswith("ar") else "I found the following web evidence; here is a concise extract:"
    parts = [intro]
    for i, d in enumerate(docs[:3], 1):
        text = re.sub(r"\s+", " ", str(d.get("text") or "").strip())
        if text:
            parts.append(f"\n[{i}] {d.get('title') or d.get('url')}\n{text[:650]}")
    return "\n".join(parts)
```

---

### `314/588` `backend/RUN-ALL-TESTS.bat`

- **المسار الكامل:** `F:\1f\p\ALI_Studio_Pro_Design4_4.6.0\04_Adaptive_Hybrid\backend/RUN-ALL-TESTS.bat`
- **الحجم:** 345 بايت (0.3 KB)
- **الامتداد:** `.bat`

```batch
@echo off
setlocal
chcp 65001 >nul
cd /d "%~dp0"
if not exist ".venv\Scripts\activate.bat" call SETUP.bat
if errorlevel 1 exit /b 1
call ".venv\Scripts\activate.bat"
python -m pytest tests -q --disable-warnings
if errorlevel 1 (
  echo.
  echo [ERROR] Test suite contains failures.
  pause & exit /b 1
)
echo.
echo [OK] Test suite passed.
pause
```

---

### `315/588` `backend/RUN-BENCHMARK.bat`

- **المسار الكامل:** `F:\1f\p\ALI_Studio_Pro_Design4_4.6.0\04_Adaptive_Hybrid\backend/RUN-BENCHMARK.bat`
- **الحجم:** 179 بايت (0.2 KB)
- **الامتداد:** `.bat`

```batch
@echo off
setlocal
chcp 65001 >nul
cd /d "%~dp0"
if not exist ".venv\Scripts\python.exe" call SETUP.bat
call ".venv\Scripts\activate.bat"
python scripts\benchmark_device.py
pause
```

---

### `316/588` `backend/RUN-DOCTOR.bat`

- **المسار الكامل:** `F:\1f\p\ALI_Studio_Pro_Design4_4.6.0\04_Adaptive_Hybrid\backend/RUN-DOCTOR.bat`
- **الحجم:** 257 بايت (0.3 KB)
- **الامتداد:** `.bat`

```batch
@echo off
setlocal
chcp 65001 >nul
cd /d "%~dp0"
if not exist ".venv\Scripts\python.exe" call SETUP.bat
if errorlevel 1 exit /b 1
call ".venv\Scripts\activate.bat"
python scripts\windows_preflight.py
if errorlevel 1 exit /b 1
python scripts\doctor.py
pause
```

---

### `317/588` `backend/RUN-GPU-DOCTOR.bat`

- **المسار الكامل:** `F:\1f\p\ALI_Studio_Pro_Design4_4.6.0\04_Adaptive_Hybrid\backend/RUN-GPU-DOCTOR.bat`
- **الحجم:** 948 بايت (0.9 KB)
- **الامتداد:** `.bat`

```batch
@echo off
setlocal EnableExtensions
chcp 65001 >nul
cd /d "%~dp0"
if exist ".venv\Scripts\python.exe" (
  set "PY=.venv\Scripts\python.exe"
) else if exist "..\runtime\python\python.exe" (
  set "PY=..\runtime\python\python.exe"
) else (
  set "PY=py -3.11"
)
echo ================================================
echo ALI Studio Pro 4.5.2 - GPU Doctor
echo ================================================
%PY% -c "from runtime.hardware import detect,training_profile; import json; h=detect(force=True, probe_torch=True); print(json.dumps(h.to_dict(),ensure_ascii=False,indent=2)); print(json.dumps(training_profile(h),ensure_ascii=False,indent=2))"
if errorlevel 1 (
  echo [ERROR] GPU Doctor could not start the Python runtime.
  exit /b 1
)
echo.
echo Auto mode will use the GPU only after a real CUDA self-test and enough free VRAM.
echo On a 2GB Maxwell card the policy preserves headroom for Windows and other GPU processes.
pause
exit /b 0
```

---

### `318/588` `backend/RUN-HERMES-DOCTOR.bat`

- **المسار الكامل:** `F:\1f\p\ALI_Studio_Pro_Design4_4.6.0\04_Adaptive_Hybrid\backend/RUN-HERMES-DOCTOR.bat`
- **الحجم:** 176 بايت (0.2 KB)
- **الامتداد:** `.bat`

```batch
@echo off
setlocal
chcp 65001 >nul
cd /d "%~dp0"
if not exist ".venv\Scripts\python.exe" call SETUP.bat
call ".venv\Scripts\activate.bat"
python scripts\hermes_doctor.py
pause
```

---

### `319/588` `backend/RUN-KCA-DOCTOR.bat`

- **المسار الكامل:** `F:\1f\p\ALI_Studio_Pro_Design4_4.6.0\04_Adaptive_Hybrid\backend/RUN-KCA-DOCTOR.bat`
- **الحجم:** 200 بايت (0.2 KB)
- **الامتداد:** `.bat`

```batch
@echo off
setlocal
chcp 65001 >nul
cd /d "%~dp0"
if not exist ".venv\Scripts\python.exe" call SETUP.bat
if errorlevel 1 exit /b 1
call ".venv\Scripts\activate.bat"
python scripts\kca_doctor.py
pause

```

---

### `320/588` `backend/RUN-MODEL-SMOKE.bat`

- **المسار الكامل:** `F:\1f\p\ALI_Studio_Pro_Design4_4.6.0\04_Adaptive_Hybrid\backend/RUN-MODEL-SMOKE.bat`
- **الحجم:** 272 بايت (0.3 KB)
- **الامتداد:** `.bat`

```batch
@echo off
setlocal
chcp 65001 >nul
cd /d "%~dp0"
if not exist ".venv\Scripts\python.exe" call SETUP.bat
if errorlevel 1 exit /b 1
call ".venv\Scripts\activate.bat"
python scripts\windows_preflight.py
if errorlevel 1 exit /b 1
python scripts\bootstrap_model_check.py
pause
```

---

### `321/588` `backend/RUN-TESTS.bat`

- **المسار الكامل:** `F:\1f\p\ALI_Studio_Pro_Design4_4.6.0\04_Adaptive_Hybrid\backend/RUN-TESTS.bat`
- **الحجم:** 173 بايت (0.2 KB)
- **الامتداد:** `.bat`

```batch
@echo off
setlocal
cd /d "%~dp0"
if not exist ".venv\Scripts\python.exe" call SETUP.bat
call ".venv\Scripts\activate.bat"
python -m pytest tests -q --disable-warnings
pause
```

---

### `322/588` `backend/scripts/benchmark_device.py`

- **المسار الكامل:** `F:\1f\p\ALI_Studio_Pro_Design4_4.6.0\04_Adaptive_Hybrid\backend/scripts/benchmark_device.py`
- **الحجم:** 931 بايت (0.9 KB)
- **الامتداد:** `.py`

```python
# -*- coding: utf-8 -*-
"""Small deterministic ALI device benchmark. No model training/downloads."""
from __future__ import annotations
import json, time, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT))
from runtime.hardware import detect, training_profile, model_profile

def main():
    import torch
    h=detect(); tp=training_profile(h)
    torch.set_num_threads(int(tp.get('cpu_threads', max(1,h.cpu_cores-2))))
    x=torch.randn(256,256); y=torch.randn(256,256)
    for _ in range(3): _=x@y
    t=time.perf_counter();
    for _ in range(20): _=x@y
    elapsed=time.perf_counter()-t
    print(json.dumps({'hardware':h.to_dict(),'training_profile':tp,'model_profile':model_profile(h),'matmul_256x256_20_iters_sec':round(elapsed,4),'notes':['Micro benchmark only; not a language-model throughput measurement.']},ensure_ascii=False,indent=2))
if __name__=='__main__': main()
```

---

### `323/588` `backend/scripts/bootstrap_conversation.py`

- **المسار الكامل:** `F:\1f\p\ALI_Studio_Pro_Design4_4.6.0\04_Adaptive_Hybrid\backend/scripts/bootstrap_conversation.py`
- **الحجم:** 5736 بايت (5.6 KB)
- **الامتداد:** `.py`

```python
#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Create and verify a first real ALI conversation model + conversation LoRA adapter.

This is a compact end-to-end smoke training run for the user's 32GB RAM / 2GB VRAM
class machine. It does not use a pretrained model or Ollama.
"""
from __future__ import annotations
import json,sys,time,hashlib,shutil
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]; sys.path.insert(0,str(ROOT))

def fmt(messages):
    return ''.join(f"<|{m['role']}|>\n{m.get('content','')}\n<|eot|>\n" for m in messages if m.get('content') is not None)

def build_source(seed,train,val,test):
    rows=[json.loads(x) for x in seed.read_text(encoding='utf-8').splitlines() if x.strip()]
    uniq={}
    for r in rows:
        txt=fmt(r.get('messages',[])); h=hashlib.sha256(txt.encode('utf-8')).hexdigest()
        if txt.strip() and h not in uniq:uniq[h]={'id':h,'text':txt,'messages':r.get('messages',[])}
    ordered=[uniq[k] for k in sorted(uniq)]
    n=len(ordered); ntr=max(1,int(n*.8)); nv=max(1,int(n*.1)) if n>=3 else max(0,n-ntr)
    parts={'train':ordered[:ntr],'validation':ordered[ntr:ntr+nv],'test':ordered[ntr+nv:]}
    for path,items in [(train,parts['train']),(val,parts['validation']),(test,parts['test'])]:
        path.parent.mkdir(parents=True,exist_ok=True); path.write_text(''.join(json.dumps(x,ensure_ascii=False)+'\n' for x in items),encoding='utf-8')
    corpus=train.parent/'tokenizer_corpus.txt'; corpus.write_text('\n\n'.join(x['text'] for x in ordered),encoding='utf-8')
    return {'total':n,'train':len(parts['train']),'validation':len(parts['validation']),'test':len(parts['test']),'corpus':str(corpus)}

def main():
    import torch
    from runtime.hardware import detect
    from tokenizer.spm import train_sentencepiece,AliTokenizer
    from model.ali_lm import AliConfig,ALIForCausalLM,save_hf_checkpoint
    from training.trainer import Trainer,TrainConfig
    from training.conversation import save_conversation_adapter
    from training.evaluator import evaluate_model
    from model.registry import ModelRegistry,file_hash
    h=detect(); print('[hardware]',h.to_dict())
    seed=ROOT/'data/seed/conversations.jsonl'; out=ROOT/'data/training/bootstrap'
    paths={k:out/f'chat_{k}.jsonl' for k in ('train','validation','test')}; split=build_source(seed,*paths.values()); print('[dataset]',split)
    tokdir=ROOT/'models/base/ALI-Conversation-v0.1/tokenizer'; tokfile=tokdir/'tokenizer.model'
    if tokfile.exists(): shutil.rmtree(tokdir.parent,ignore_errors=True)
    train_sentencepiece([split['corpus']],tokdir,vocab_size=512)
    tok=AliTokenizer(tokfile)
    cfg=AliConfig(vocab_size=tok.vocab_size,hidden_size=128,intermediate_size=512,num_hidden_layers=2,num_attention_heads=4,num_key_value_heads=4,max_position_embeddings=256,use_sdpa=True)
    base_dir=ROOT/'models/base/ALI-Conversation-v0.1'; ckpt_root=ROOT/'models/checkpoints/ALI-Conversation-v0.1'
    model=ALIForCausalLM(cfg)
    tc=TrainConfig(epochs=3,batch_size=1,grad_accum=2,learning_rate=4e-4,warmup_steps=5,max_steps=80,save_every=40,eval_every=20,max_seq_len=192,device='cpu',gradient_checkpointing=True,amp=False,cpu_amp=False,dataset_mode='chat',curriculum=True,cpu_threads=max(1,(h.cpu_cores or 2)-1))
    tr=Trainer(model,tok,paths['train'],paths['validation'],tc,ckpt_root)
    res=tr.train(lambda e: print(json.dumps(e,ensure_ascii=False),flush=True))
    final=Path(res['checkpoint']); hf=final/'hf'; save_hf_checkpoint(model,tokdir,hf,{'training_result':res,'specialization':'conversation-base'})
    merged_dir=ROOT/'models/merged/ALI-Conversation-v0.1'; shutil.rmtree(merged_dir,ignore_errors=True); save_hf_checkpoint(model,tokdir,merged_dir,{'training_result':res,'specialization':'conversation-base-merged'})
    # Real conversation LoRA adapter on top of the trained base.
    blob=torch.load(final/'checkpoint.pt',map_location='cpu',weights_only=False); base=ALIForCausalLM(AliConfig.from_dict(blob['config'])); base.load_state_dict(blob['model'])
    ltc=TrainConfig(epochs=2,batch_size=1,grad_accum=2,learning_rate=8e-4,warmup_steps=3,max_steps=30,save_every=15,eval_every=15,max_seq_len=192,device='cpu',gradient_checkpointing=True,amp=False,dataset_mode='chat',train_mode='lora',lora_rank=4,lora_alpha=8,curriculum=True)
    ltr=Trainer(base,tok,paths['train'],paths['validation'],ltc,ROOT/'models/checkpoints/ALI-Conversation-LoRA-v0.1'); lres=ltr.train(lambda e: None)
    adapter=Path(lres['checkpoint'])/'adapter'; adapter_out=ROOT/'models/lora/ALI-Conversation-v0.1'; shutil.rmtree(adapter_out,ignore_errors=True); shutil.copytree(adapter,adapter_out)
    eval_res=evaluate_model(model,tok,paths['validation'],'cpu')
    test_res=evaluate_model(model,tok,paths['test'],'cpu') if paths['test'].exists() and paths['test'].read_text(encoding='utf-8').strip() else {}
    registry=ModelRegistry(ROOT/'artifacts/models.sqlite3'); ver='v'+time.strftime('%Y%m%d-%H%M%S'); ds_hash=file_hash(paths['train']); registry.register('ALI',ver,status='candidate',checkpoint=str(final),hf_dir=str(hf),adapter=str(adapter_out),dataset_hash=ds_hash,tokenizer_hash=file_hash(tokdir),train_config=tc.to_dict(),eval={'validation':eval_res,'test':test_res,'loss':res.get('val_loss')})
    result={'base_training':res,'lora_training':lres,'validation':eval_res,'test':test_res,'hf':str(hf),'merged':str(merged_dir),'adapter':str(adapter_out),'registry_version':ver}
    (ROOT/'evaluation/artifacts').mkdir(parents=True,exist_ok=True)
    (ROOT/'evaluation/artifacts/bootstrap_report.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps(result,ensure_ascii=False,indent=2)); return 0
if __name__=='__main__':raise SystemExit(main())
```

---

### `324/588` `backend/scripts/bootstrap_conversation_memory.py`

- **المسار الكامل:** `F:\1f\p\ALI_Studio_Pro_Design4_4.6.0\04_Adaptive_Hybrid\backend/scripts/bootstrap_conversation_memory.py`
- **الحجم:** 1339 بايت (1.3 KB)
- **الامتداد:** `.py`

```python
#!/usr/bin/env python
"""Seed local conversation memory from reviewed seed conversations.
This does not alter model weights; it provides immediate, provenance-aware recall.
"""
from __future__ import annotations
from pathlib import Path
import json, sys
ROOT=Path(__file__).resolve().parents[1]; sys.path.insert(0,str(ROOT))
from memory.conversations import ConversationMemory

def main():
    db=ConversationMemory(ROOT/'runtime_conversations.sqlite3')
    src=ROOT/'data/seed/conversations_curriculum.jsonl' if (ROOT/'data/seed/conversations_curriculum.jsonl').exists() else ROOT/'data/seed/conversations.jsonl'; n=0
    with src.open(encoding='utf-8') as f:
        for line in f:
            try:o=json.loads(line); msgs=o.get('messages',[])
            except Exception: continue
            user=next((m.get('content','') for m in msgs if m.get('role')=='user'),'')
            assistant=next((m.get('content','') for m in msgs if m.get('role')=='assistant'),'')
            if user and assistant:
                meta=o.get('metadata') or {}; db.put(user,assistant,source=meta.get('source','reviewed-seed'),model_version=meta.get('version','curriculum-seed'),quality=1.0); n+=1
    print(json.dumps({'stored_or_updated':n,'db':str(ROOT/'runtime_conversations.sqlite3')},ensure_ascii=False,indent=2))
if __name__=='__main__': main()
```

---

### `325/588` `backend/scripts/bootstrap_model_check.py`

- **المسار الكامل:** `F:\1f\p\ALI_Studio_Pro_Design4_4.6.0\04_Adaptive_Hybrid\backend/scripts/bootstrap_model_check.py`
- **الحجم:** 1249 بايت (1.2 KB)
- **الامتداد:** `.py`

```python
# -*- coding: utf-8 -*-
"""Verify that the included ALI bootstrap model is present and loadable."""
from __future__ import annotations
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from model.registry import ModelRegistry
from model.manager import ModelManager


def main() -> int:
    registry = ModelRegistry(ROOT / "models" / "models.sqlite3")
    row = registry.active("ALI")
    if not row:
        print("ERROR: no active ALI model is registered")
        return 1
    manager = ModelManager(ROOT, registry)
    discovered = manager.discover_active("ALI")
    if not discovered:
        print("ERROR: registered active model is not loadable")
        return 1
    engine, _ = manager.load(discovered)
    sample = engine.complete("Hello ALI", max_new_tokens=8, temperature=0.0, context_size=128)
    print("[OK] Active model:", discovered.get("version"))
    print("[OK] HF model:", discovered.get("hf_dir"))
    print("[OK] Inference smoke completed; generated characters:", len(sample))
    print("NOTE: the bundled bootstrap model is a functional micro checkpoint, not a production-scale assistant.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
```

---

### `326/588` `backend/scripts/build_conversation_curriculum.py`

- **المسار الكامل:** `F:\1f\p\ALI_Studio_Pro_Design4_4.6.0\04_Adaptive_Hybrid\backend/scripts/build_conversation_curriculum.py`
- **الحجم:** 21410 بايت (20.9 KB)
- **الامتداد:** `.py`

```python
#!/usr/bin/env python
from __future__ import annotations
from pathlib import Path
import json, hashlib, random, sys
ROOT=Path(__file__).resolve().parents[1]; sys.path.insert(0,str(ROOT))

TOPICS_EXTENDED=[
('training_success','كيف تقيس نجاح تدريب ALI؟','قارن validation loss والمقاييس الثابتة مع baseline، ثم نفّذ اختبارات regression قبل ترقية النموذج.'),
('continuous_learning','كيف يضيف ALI محادثة جديدة إلى التعلم المستمر؟','يسجل المحادثة بعد التنظيف والـdedup، يستخدمها فورًا عبر الذاكرة، ثم يضيفها إلى Dataset incremental مرة واحدة قبل دورة تدريب وتقييم جديدة.'),
('response_quality','كيف يمنع ALI عرض إجابة مولدة غير موثوقة؟','يمرر الناتج عبر اختبارات جودة اللغة والتكرار والبنية، وإذا فشل يستخدم معرفة موثوقة أو ذاكرة مناسبة بدل تقديم النص المنهار كحقيقة.'),
]
TOPICS=[
('project_inspect','حلل لي مشروعًا قبل التعديل.','ابدأ بجرد الملفات ونقطة الدخول والاعتماديات ومسار التشغيل والاختبارات، ثم سجّل المخاطر قبل اقتراح أي تعديل.'),
('safe_change','كيف تعدل مشروعًا دون كسره؟','اقرأ السياق أولًا، خذ snapshot، ضع خطة صغيرة، طبّقها، شغّل الاختبارات المركزة ثم اختبارات regression وتحقق من الناتج.'),
('test_failure','ماذا تفعل إذا فشل اختبار بعد تعديل؟','حدد أول فشل قابل للتفسير، تتبع السبب الجذري، أصلحه، أعد الاختبار المركز ثم المجموعة الكاملة قبل اعتبار التعديل ناجحًا.'),
('rollback','متى تستخدم rollback؟','استخدم rollback عندما يفشل التحقق أو يظهر regression أو فساد غير مقصود، مع إبقاء النسخة السابقة المعتمدة دون تغيير.'),
('new_project','كيف تنشئ مشروعًا جديدًا؟','حدد المتطلبات، اختر بنية بسيطة، أنشئ الملفات الأساسية والاختبارات، شغّل المشروع ثم وثّق طريقة التشغيل.'),
('python','كيف تحسن برنامج Python؟','قس الأداء والاختبارات أولًا، أصلح أكبر عنق زجاجة مؤكد، حافظ على واجهات المشروع، ثم أعد الاختبارات قبل الانتقال.'),
('sqlite','كيف تتعامل مع SQLite في مشروع محلي؟','استخدم migrations بسيطة، معاملات واضحة، فهارس مناسبة، ونسخة احتياطية قبل تغييرات المخطط المهمة.'),
('git','كيف تستخدم Git أثناء تطوير المشروع؟','افحص status وdiff، اجعل التغييرات صغيرة وقابلة للمراجعة، ثم اختبر قبل commit واضح يصف التغيير الحقيقي.'),
('rag','ما الفرق بين RAG والتدريب؟','RAG يضيف المعرفة وقت الاستدعاء من مصادر قابلة للتحديث، بينما التدريب يغيّر الأوزان ويحتاج Dataset وتقييمًا وإصدارًا جديدًا.'),
('web_research','كيف تحفظ معلومة من الإنترنت؟','احفظ الرابط والعنوان وتاريخ الالتقاط والنص أو المقتطف، افحص المصدر، ثم خزّنها في Knowledge Base قبل التفكير في التدريب.'),
('memory','كيف تتعلم ALI من محادثة جديدة؟','يحفظ الزوج بعد التنظيف وتسجيل المصدر ويستطيع استرجاعه فورًا، ثم يدخل Dataset جديدًا فقط إذا كان عالي الجودة وغير مكرر.'),
('dedup','كيف تمنع تكرار التدريب؟','احسب hash ثابتًا للعينات وDataset الكامل، وسجل آخر هوية تم تدريبها، وأنشئ Candidate فقط عند وجود هويات جديدة.'),
('checkpoint','ماذا يحتوي checkpoint حقيقي؟','يحفظ الأوزان وحالة optimizer وscheduler وRNG وإعدادات التدريب والعدادات والمقاييس اللازمة للاستئناف.'),
('resume','كيف يستأنف ALI التدريب؟','يحمل آخر checkpoint موثوق، يستعيد النموذج والoptimizer وscheduler وRNG ثم يكمل من الخطوة المسجلة بدل البدء من الصفر.'),
('gguf','ما هو GGUF في ALI؟','هو snapshot للاستدلال من أوزان ALI المصدّرة، وليس قاعدة بيانات لإضافة معلومات جديدة مباشرة إلى الملف نفسه.'),
('quant','كيف تضغط النموذج؟','بعد تقييم checkpoint صدّر نسخة استدلال مناسبة ثم طبّق quantization مدعومة مثل Q4 أو Q5 أو Q8 عند توفر الأداة، واحتفظ بالأصل.'),
('cpu','كيف تسرع التدريب على CPU؟','استخدم عدد خيوط مناسب، SDPA، batch صغير مع gradient accumulation، sequence قصيرة، checkpointing وتجنب تحميل بيانات مكرر.'),
('2gb','كيف تضبط ALI لجهاز 2GB VRAM؟','اجعل batch=1، استخدم gradient accumulation وcheckpointing وسياقًا متحفظًا، واسمح بالتحول إلى CPU إذا لم تكفِ VRAM.'),
('ram','كيف تستفيد من 32GB RAM؟','استخدم RAM للتخزين المؤقت، فهرسة المعرفة، DataLoader بسيط وoffload محسوب، مع حد أعلى يمنع امتلاء الذاكرة.'),
('multimodal','كيف يتعامل ALI مع الصور والصوت والفيديو؟','يستخرج تمثيلًا عصبيًا محليًا للوسيط ثم يمرره عبر projector إلى مساحة ALI، مع حفظ المصدر وعدم خلط ملفات الوسائط عشوائيًا مع نص التدريب.'),
('pdf','كيف يتعلم من PDF؟','استخرج النص والصفحات والجداول عند الإمكان، احتفظ برقم الصفحة والمصدر، ثم افصل المعرفة القابلة للبحث عن أمثلة التدريب.'),
('archive','كيف تتعامل مع ZIP أو أرشيف؟','تحقق من المسار ونوع الملف والحجم، فكّه داخل مجلد downloads/extracted آمن، ثم افحص المحتويات recursively.'),
('security','ما أهم قواعد أمان الوكيل؟','قيّد المسارات والأوامر، استخدم allowlist، اطلب تأكيدًا للعمليات الحساسة، وسجّل audit trail ولا تسرب الأسرار.'),
('tool','متى يستخدم ALI الأدوات؟','يستخدم الأداة عندما يحتاج دليلًا أو فعلًا خارج النموذج، وينتظر نتيجة حقيقية ثم يبني الإجابة منها.'),
('tool_call','كيف يتعلم tool calling؟','تدرّب المحادثات على مخططات الأدوات وأمثلة اختيار الأداة والوسائط، ثم قيّم صحة JSON والتنفيذ قبل الترقية.'),
('agent','كيف يعمل وكيل المشروع؟','يفحص ثم يخطط ثم يأخذ snapshot ثم يطبق ثم يختبر ثم يتحقق ثم يراجع قبل إغلاق المهمة.'),
('skills','ما فائدة skills؟','هي وصفات قابلة للتحميل تحدد طريقة حل نوع من المهام وأدواتها وشروط النجاح، وتبقى منفصلة عن النواة.'),
('plugins','كيف تعمل plugins؟','تُسجّل كإضافات اختيارية بصلاحيات واضحة ومخطط إدخال وإخراج، ولا تعمل تلقائيًا دون تفعيلها.'),
('mcp','كيف تستخدم MCP؟','يُشغّل خادم MCP اختياريًا عبر قناة محلية مضبوطة، وتُكتشف الأدوات منه ثم تمر كل عملية عبر صلاحيات ALI.'),
('offline','هل يعمل ALI بدون إنترنت؟','نعم في مسار المعرفة المحلية والتدريب والاستدلال، أما البحث الشبكي فيبقى طبقة اختيارية لا يعتمد عليها التشغيل الأساسي.'),
('uncertainty','ماذا تفعل عندما لا تعرف الإجابة؟','لا تخمّن كحقيقة؛ اذكر حدود الأدلة واستعمل Knowledge أو البحث أو اطلب معلومة إضافية عندما تكون ضرورية.'),
('conversation','كيف يجب أن يرد ALI على المستخدم؟','يحافظ على لغة المستخدم، يجيب مباشرة، يوضح الخطوات عند الحاجة، ويذكر عدم اليقين والمصادر عندما تكون مهمة.'),
('dataset','كيف تبني Dataset للمحادثات؟','نظف الرسائل، حافظ على ترتيب الأدوار، احذف الأسرار والتكرار، افصل train/validation/test ثم افحص الجودة قبل التدريب.'),
('curriculum','ما فائدة Curriculum Learning؟','يجعل التدريب يمر من أمثلة أسهل إلى أمثلة أصعب وفق درجة محددة بدل خلط كل الصعوبات من البداية.'),
('evaluation','كيف تعرف أن النموذج تحسن؟','قارن baseline وcandidate على validation وbenchmarks واختبارات regression ولا تعتمد على training loss وحده.'),
('arabic','كيف تقيم العربية؟','استخدم أسئلة عربية متنوعة، قياس تطابق اللغة، فهم التعليمات، استرجاع المعرفة، وجودة الأجوبة وعدم اختلاق الأدلة.'),
('english','كيف تقيم الإنجليزية؟','استخدم أسئلة متنوعة في التعليمات والبرمجة والاستدعاء والحوارات وراجع الدقة والوضوح والثبات عبر benchmark ثابت.'),
('new_info','ماذا يحدث عند إدخال معلومات جديدة؟','تُنقّى وتُفهرس وتُسجل بهوية مصدر، ثم تستخدم فورًا في RAG، ولا تدخل الأوزان إلا عبر دورة Dataset وتدريب وتقييم جديدة.'),
('no_dup_gguf','كيف تمنع GGUF المكرر؟','اربط GGUF بهوية checkpoint وDataset وquantization، ولا تصدر ملفًا جديدًا إذا كانت الهوية مطابقة لإصدار موجود.'),
('download','أين تحفظ الملفات التي ينزلها ALI؟','ضعها في downloads مع metadata المصدر والوقت وhash، وافحصها قبل فكها أو إدخالها في المعرفة.'),
('libraries','كيف تدير المكتبات؟','افصل المكتبات المحلية عن المشروع، سجل الإصدار والمصدر، واستخدم بيئة افتراضية حتى لا تلوث النظام.'),
('preview','متى تستخدم Preview Pane؟','عند الحاجة لمعاينة HTML أو صورة أو ملف إخراج للمشروع بعد التعديل، مع إبقاء المعاينة منفصلة عن صلاحيات التنفيذ.'),
('web_ui','كيف تبني Web UI محليًا؟','استخدم API محليًا على localhost وواجهة ثابتة، واجعل الواجهة تتصل بالمحرك المحلي بدل إرسال البيانات خارجيًا.'),
('tui','ما فائدة TUI؟','توفر تحكمًا سريعًا من الطرفية في الأنظمة التي لا تحتاج واجهة رسومية كاملة، مع عرض الحالة والسجل والتدريب.'),
('logs','ما الذي يجب تسجيله؟','سجل الوقت والمهمة والأداة والنتيجة والمدة وحالة الموارد والمصدر مع منع كتابة الأسرار أو الرموز السرية إلى السجل.'),
('errors','كيف يتعامل النظام مع خطأ داخلي؟','احتفظ بالنسخة السابقة، سجل traceback محليًا، اعرض رسالة مفهومة، ثم أعد المحاولة فقط إذا كانت السياسة تسمح بذلك.'),
('self_dev','كيف يطور ALI نفسه؟','لا يعدل النواة عشوائيًا؛ يقترح تغييرًا، ينشئ branch أو snapshot، يشغّل الاختبارات، ثم يقبل النسخة فقط إذا اجتازت بوابة التحقق.'),
('project_graph','كيف يفهم علاقات المشروع؟','يبني فهرسًا للملفات والرموز والاختبارات والمداخل والاعتماديات ثم يستخدم هذه العلاقات عند التخطيط للتغيير.'),
('code_search','كيف يجد الملف المرتبط بمشكلة؟','يستخدم فهرس أسماء الملفات ونصوصها والرموز ثم يقرأ السياق المحيط قبل اختيار موضع التعديل.'),
('performance','كيف تقيس سرعة ALI؟','سجل tokens/sec وزمن الاستجابة واستخدام CPU/RAM/VRAM وحجم السياق ومعدل الأخطاء لكل إصدار.'),
]

TOPICS = TOPICS + TOPICS_EXTENDED

TEMPLATES_AR=[
    'كيف يتم تنفيذ {}؟', 'اشرح لي طريقة {}.', 'أريد من ALI أن ينفذ {}؛ كيف يفعل ذلك؟',
    'ما الخطوات العملية لتنفيذ {}؟', 'كيف أتعامل مع مشكلة مرتبطة بـ{}؟', 'متى يكون مناسبًا تنفيذ عملية {}؟',
    'ما الذي يجب فحصه قبل تنفيذ {}؟', 'كيف يتحقق ALI من نجاح عملية {}؟', 'ماذا يفعل ALI أثناء عملية {}؟', 'كيف يمكن تحسين عملية {}؟'
]
TEMPLATES_EN=[
    'What is the correct way to {}?', 'Explain how to {}.', 'I want ALI to {}; how should it do that?',
    'What are the practical steps to {}?', 'How should I handle a case where I need to {}?', 'When is it appropriate to {}?',
    'What should be checked before I {}?', 'How does ALI verify successful execution of {}?', 'What should ALI do if it needs to {}?', 'How can the approach to {} be improved?'
]
AR_ACTIONS={
'project_inspect':'تحليل المشروع قبل التعديل','safe_change':'تعديل المشروع دون كسره','test_failure':'التعامل مع فشل اختبار بعد تعديل','rollback':'استخدام rollback عند الحاجة','new_project':'إنشاء مشروع جديد','python':'تحسين برنامج Python','sqlite':'التعامل مع SQLite في مشروع محلي','git':'استخدام Git أثناء تطوير المشروع','rag':'فهم الفرق بين RAG والتدريب','web_research':'حفظ معلومة من الإنترنت','memory':'تعلم ALI من محادثة جديدة','dedup':'منع تكرار بيانات التدريب','checkpoint':'فهم ما يحتويه checkpoint الحقيقي','resume':'استئناف تدريب ALI','gguf':'استخدام GGUF في ALI','quant':'ضغط النموذج بالـquantization','cpu':'تسريع التدريب على CPU','2gb':'ضبط ALI لجهاز بذاكرة VRAM قدرها 2GB','ram':'الاستفادة من 32GB RAM','multimodal':'تعامل ALI مع الصور والصوت والفيديو','pdf':'تعلم ALI من ملف PDF','archive':'التعامل مع ملفات ZIP والأرشيفات','security':'تأمين الوكيل وأدواته','tool':'تحديد متى يستخدم ALI الأدوات','tool_call':'تعلم ALI لاستدعاء الأدوات','agent':'تشغيل دورة عمل وكيل المشروع','skills':'استخدام skills','plugins':'استخدام plugins','mcp':'استخدام MCP','offline':'تشغيل ALI دون إنترنت','uncertainty':'التعامل مع الأسئلة التي لا يعرفها','conversation':'الرد على المستخدم بطريقة صحيحة','dataset':'بناء Dataset للمحادثات','curriculum':'استخدام Curriculum Learning','evaluation':'قياس تحسن النموذج','arabic':'تقييم جودة العربية','english':'تقييم جودة الإنجليزية','new_info':'إضافة معلومات جديدة','no_dup_gguf':'منع تكرار ملفات GGUF','download':'حفظ الملفات التي ينزلها ALI','libraries':'إدارة المكتبات المحلية','preview':'استخدام Preview Pane','web_ui':'بناء Web UI محلي','tui':'استخدام TUI','logs':'تسجيل العمليات والسجلات بشكل آمن','errors':'التعامل مع خطأ داخلي','self_dev':'تطوير ALI لنفسه بشكل آمن','project_graph':'فهم علاقات المشروع','code_search':'العثور على الملف المرتبط بمشكلة','performance':'قياس سرعة وأداء ALI','training_success':'قياس نجاح تدريب ALI','continuous_learning':'إضافة محادثة جديدة إلى التعلم المستمر','response_quality':'منع عرض إجابة مولدة غير موثوقة'
}

def build():
    out=[]; seen=set()
    for key, ar_answer, en_answer in TOPICS:
        # derive a compact infinitive/phrase from the topic's first clause for prompts
        ar_action=AR_ACTIONS[key]
        en_action={
            'project_inspect':'inspect a project before changing it','safe_change':'modify a project without breaking it','test_failure':'a test fails after a change',
            'rollback':'use rollback','new_project':'create a new project','python':'improve a Python program','sqlite':'handle SQLite in a local project','git':'use Git while developing',
            'rag':'understand RAG versus training','web_research':'store information from the internet','memory':'teach ALI from a new conversation','dedup':'prevent duplicate training',
            'checkpoint':'understand a real checkpoint','resume':'resume ALI training','gguf':'use GGUF in ALI','quant':'quantize the model','cpu':'speed up training on CPU',
            '2gb':'configure ALI for a 2GB VRAM machine','ram':'use 32GB of RAM effectively','multimodal':'handle images, audio and video','pdf':'learn from a PDF','archive':'process ZIP or archive files',
            'security':'secure the agent','tool':'decide when ALI should use tools','tool_call':'learn tool calling','agent':'run the project agent workflow','skills':'use skills','plugins':'use plugins',
            'mcp':'use MCP','offline':'run ALI without internet','uncertainty':'handle unknown questions','conversation':'respond to the user','dataset':'build a conversation dataset','curriculum':'use curriculum learning',
            'evaluation':'measure whether the model improved','arabic':'evaluate Arabic','english':'evaluate English','new_info':'add new information','no_dup_gguf':'prevent duplicate GGUF exports',
            'download':'store downloaded files','libraries':'manage local libraries','preview':'use the preview pane','web_ui':'build a local Web UI','tui':'use the TUI','logs':'log the right information',
            'errors':'handle an internal error','self_dev':'let ALI improve itself safely','project_graph':'understand project relationships','code_search':'find the file related to a problem',
            'performance':'measure ALI performance','training_success':'measure ALI training success','continuous_learning':'add a new conversation to continuous learning','response_quality':'prevent an unreliable generated answer from being shown'
        }[key]
        for i in range(10):
            ar=TEMPLATES_AR[i].format(ar_action)
            en= TEMPLATES_EN[i].format(en_action)
            for lang,prompt,ans in [('ar',ar,ar_answer),('en',en,en_answer)]:
                pair=(prompt,ans)
                h=hashlib.sha256((prompt+'\n'+ans).encode()).hexdigest()
                if h in seen: continue
                seen.add(h)
                out.append({'id':h,'messages':[{'role':'system','content':'You are ALI. Answer in the user language and do not invent evidence.'},{'role':'user','content':prompt},{'role':'assistant','content':ans}], 'metadata':{'topic':key,'language':lang,'source':'curated-curriculum'}})
    random.Random(42).shuffle(out)
    path=ROOT/'data/seed/conversations_curriculum.jsonl'; path.parent.mkdir(parents=True,exist_ok=True)
    with path.open('w',encoding='utf-8') as f:
        for r in out:f.write(json.dumps(r,ensure_ascii=False)+'\n')
    # split
    split=ROOT/'data/training/curriculum'; split.mkdir(parents=True,exist_ok=True)
    n=len(out); a=int(n*.8); b=int(n*.9)
    parts={'chat_train':out[:a],'chat_validation':out[a:b],'chat_test':out[b:]}
    for name,rows in parts.items():
        with (split/(name+'.jsonl')).open('w',encoding='utf-8') as f:
            for r in rows:f.write(json.dumps({'id':r['id'],'messages':r['messages'],'text':''.join(f"<|{m['role']}|>\n{m['content']}\n<|eot|>\n" for m in r['messages'])},ensure_ascii=False)+'\n')
    print(json.dumps({'total':n,'train':a,'validation':b-a,'test':n-b,'path':str(path)},ensure_ascii=False,indent=2))
if __name__=='__main__':build()
```

---

### `327/588` `backend/scripts/build_historical_datasets.py`

- **المسار الكامل:** `F:\1f\p\ALI_Studio_Pro_Design4_4.6.0\04_Adaptive_Hybrid\backend/scripts/build_historical_datasets.py`
- **الحجم:** 5939 بايت (5.8 KB)
- **الامتداد:** `.py`

```python
# -*- coding: utf-8 -*-
"""Build verified historical/cumulative conversation datasets from project sources.

This script only uses explicit User/Assistant training material already present in the
project source bundle. It never treats arbitrary docs or source code as training data.
"""
from __future__ import annotations
from pathlib import Path
import hashlib, json, re, shutil, sys, time

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from training.continuous_learning import ContinuousLearningManager
from training.generation_lineage import sample_id, merge_jsonl_unique, sha256_file

SOURCES = {
    "v1": [
        ROOT / "training" / "updates" / "v1" / "docs" / "CONVERSATIONS_V1.md",
        ROOT / "training" / "examples" / "ALI_Professional_QA_P50_V1.md",
    ],
    "v2": [
        ROOT / "artifacts" / "continuous_learning" / "validated" / "06ba230d8cf9b575_ALI_Conversation_Training_Core_V2.md",
        ROOT / "artifacts" / "continuous_learning" / "validated" / "094791a57c8c0572_ALI_behavior_training_V2_import_sample.md",
        ROOT / "training" / "examples" / "ALI_Professional_QA_P50_V2.md",
    ],
    "v3": [
        ROOT / "training" / "examples" / "ALI_MASTER_TRAINING_4.5.2.md",
    ],
    "v4": [
        ROOT / "artifacts" / "continuous_learning" / "validated" / "d7b0aaf9a09cff6b_ALI_Behavior_Training_V4_User_Understanding_Import_Ready.md",
        ROOT / "data" / "training" / "testdata" / "ALI_User_Understanding_Bundle_V4.md",
    ],
}

OUT = ROOT / "models" / "generations"


def to_rows(path: Path, manager: ContinuousLearningManager, generation: str):
    samples, _safe, warnings = manager.parse_file(path)
    rows = []
    for pair in samples:
        messages = [{"role": str(m.get("role", "user")), "content": str(m.get("content", "")).strip()} for m in pair]
        if not any(m["role"] == "user" and m["content"] for m in messages):
            continue
        if not any(m["role"] == "assistant" and m["content"] for m in messages):
            continue
        sid = sample_id({"messages": messages})
        rows.append({
            "sample_id": sid,
            "id": sid,
            "messages": messages,
            "provenance": {
                "source_file": str(path.relative_to(ROOT)),
                "historical_generation": generation,
                "parser": "ContinuousLearningManager.parse_file",
                "approved": True,
                "built_at": time.time(),
            },
        })
    return rows, warnings


def write_rows(path: Path, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")


def main():
    manager = ContinuousLearningManager(ROOT)
    reports = {}
    for generation, sources in SOURCES.items():
        gdir = OUT / generation
        (gdir / "delta").mkdir(parents=True, exist_ok=True)
        (gdir / "cumulative").mkdir(parents=True, exist_ok=True)
        all_rows = []
        source_reports = []
        for src in sources:
            if not src.exists():
                source_reports.append({"source": str(src.relative_to(ROOT)), "exists": False, "samples": 0})
                continue
            rows, warnings = to_rows(src, manager, generation)
            all_rows.extend(rows)
            source_reports.append({"source": str(src.relative_to(ROOT)), "exists": True, "samples": len(rows), "warnings": warnings})
        raw = gdir / "delta" / "raw.jsonl"
        write_rows(raw, all_rows)
        delta = gdir / "delta" / "train.jsonl"
        dmeta = merge_jsonl_unique([raw], delta)
        try: raw.unlink()
        except Exception: pass

        parent = "" if generation == "v1" else f"v{int(generation[1:]) - 1}"
        parent_cum = OUT / parent / "cumulative" / "train.jsonl" if parent else None
        cumulative = gdir / "cumulative" / "train.jsonl"
        inputs = [parent_cum, delta] if parent_cum else [delta]
        cmeta = merge_jsonl_unique([p for p in inputs if p and Path(p).exists()], cumulative)
        report = {
            "generation": generation,
            "parent_generation": parent or None,
            "source_reports": source_reports,
            "delta_samples": dmeta["written_rows"],
            "delta_duplicates_removed": dmeta["duplicates_removed"],
            "delta_hash": dmeta["dataset_hash"],
            "cumulative_samples": cmeta["written_rows"],
            "cumulative_duplicates_removed": cmeta["duplicates_removed"],
            "cumulative_hash": cmeta["dataset_hash"],
            "historical_model_weights_available": False,
            "historical_model_lineage_status": "data_reconstructed_only",
            "created_at": time.time(),
        }
        (gdir / "cumulative_report.json").write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
        lineage = {
            "schema_version": 2,
            "generation": generation,
            "parent_generation": parent,
            "ancestors": [f"v{i}" for i in range(1, int(generation[1:]) + 1)],
            "delta_dataset": {"path": str(delta), "sha256": dmeta["dataset_hash"], "samples": dmeta["written_rows"]},
            "cumulative_dataset": {"path": str(cumulative), "sha256": cmeta["dataset_hash"], "samples": cmeta["written_rows"]},
            "historical_model_status": "not_reconstructed_from_missing_binary_weights",
            "created_at": time.time(),
        }
        (gdir / "lineage.json").write_text(json.dumps(lineage, ensure_ascii=False, indent=2), encoding="utf-8")
        (gdir / "generation.json").write_text(json.dumps({**lineage, "status": "dataset-ready"}, ensure_ascii=False, indent=2), encoding="utf-8")
        reports[generation] = report
    print(json.dumps(reports, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    raise SystemExit(main())
```

---

### `328/588` `backend/scripts/build_kca_dataset.py`

- **المسار الكامل:** `F:\1f\p\ALI_Studio_Pro_Design4_4.6.0\04_Adaptive_Hybrid\backend/scripts/build_kca_dataset.py`
- **الحجم:** 725 بايت (0.7 KB)
- **الامتداد:** `.py`

```python
#!/usr/bin/env python
from __future__ import annotations
import argparse
from pathlib import Path
import sys
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from data_engine.kca_dataset import build_kca_dataset

def main(argv=None) -> int:
    p = argparse.ArgumentParser(description="Build enriched ALI KCA training dataset")
    p.add_argument("inputs", nargs="+", help="conversation JSONL files")
    p.add_argument("--output", default="data/training/kca_train.jsonl")
    p.add_argument("--min-quality", type=float, default=.6)
    a = p.parse_args(argv)
    print(build_kca_dataset(a.inputs, ROOT / a.output, a.min_quality))
    return 0
if __name__ == "__main__":
    raise SystemExit(main())

```

---

### `329/588` `backend/scripts/build_release_manifest.py`

- **المسار الكامل:** `F:\1f\p\ALI_Studio_Pro_Design4_4.6.0\04_Adaptive_Hybrid\backend/scripts/build_release_manifest.py`
- **الحجم:** 1193 بايت (1.2 KB)
- **الامتداد:** `.py`

```python
# -*- coding: utf-8 -*-
from __future__ import annotations
from pathlib import Path
import hashlib,json,time
ROOT=Path(__file__).resolve().parent.parent
SKIP={'.git','.pytest_cache','__pycache__','.venv','checkpoints','weights'}
TEXT_EXT={'.py','.pyw','.bat','.cmd','.ps1','.json','.jsonl','.md','.txt','.toml','.ini','.cfg','.yaml','.yml','.html','.css','.js','.legacy'}
def sha(p):
    h=hashlib.sha256()
    with p.open('rb') as f:
        for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
    return h.hexdigest()
rows=[]
for p in sorted(ROOT.rglob('*')):
    if not p.is_file() or any(x in SKIP for x in p.parts):continue
    if p.name.endswith('.pyc') or p.suffix.lower() not in TEXT_EXT:continue
    if p.name == 'RELEASE_MANIFEST.json':continue
    rows.append({'path':str(p.relative_to(ROOT)).replace('\\','/'),'size':p.stat().st_size,'sha256':sha(p)})
out={'name':'ALI AI','version':'2.5.0','codename':'Unified-KCA-P50','generated_at':time.time(),'files':rows}
(ROOT/'RELEASE_MANIFEST.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'files':len(rows),'manifest':str(ROOT/'RELEASE_MANIFEST.json')},ensure_ascii=False,indent=2))
```

---

### `330/588` `backend/scripts/configure_device.py`

- **المسار الكامل:** `F:\1f\p\ALI_Studio_Pro_Design4_4.6.0\04_Adaptive_Hybrid\backend/scripts/configure_device.py`
- **الحجم:** 1080 بايت (1.1 KB)
- **الامتداد:** `.py`

```python
# -*- coding: utf-8 -*-
"""Create a local, non-secret hardware override and print the recommended profile."""
from __future__ import annotations
from pathlib import Path
import json
from runtime.hardware import detect, training_profile, model_profile
from runtime.device_policy import choose_policy

ROOT = Path(__file__).resolve().parent.parent
PROFILE = ROOT / 'config' / 'hardware_profile.json'

def main() -> None:
    h = detect()
    if not PROFILE.exists():
        PROFILE.write_text(json.dumps({
            'label': 'Auto-detected device',
            'cpu_threads': h.cpu_cores,
            'physical_cores': h.physical_cores,
            'ram_gb': h.ram_gb,
            'gpu_name': h.gpu_name,
            'vram_gb': h.vram_gb,
            'cuda_capability': list(h.cuda_capability) if h.cuda_capability else None,
        }, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps({'hardware':h.to_dict(),'policy':choose_policy(h),'training':training_profile(h),'model':model_profile(h)},ensure_ascii=False,indent=2))

if __name__ == '__main__': main()
```

---

### `331/588` `backend/scripts/continuous_update.py`

- **المسار الكامل:** `F:\1f\p\ALI_Studio_Pro_Design4_4.6.0\04_Adaptive_Hybrid\backend/scripts/continuous_update.py`
- **الحجم:** 2531 بايت (2.5 KB)
- **الامتداد:** `.py`

```python
#!/usr/bin/env python
"""Prepare a duplicate-safe incremental dataset from harvested data + new conversations."""
from __future__ import annotations
from pathlib import Path
import argparse,json,sys,time
ROOT=Path(__file__).resolve().parents[1]; sys.path.insert(0,str(ROOT))

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--db',default='artifacts/harvest.sqlite3'); ap.add_argument('--conversation-db',default='runtime_conversations.sqlite3'); ap.add_argument('--min-new',type=int,default=24); args=ap.parse_args()
    from autonomy.continuous import ContinuousLearning
    from data_engine.dataset_builder import export_incremental,export_conversation_incremental
    cl=ContinuousLearning(ROOT,args.min_new); plan=cl.plan(ROOT/args.db,ROOT/args.conversation_db)
    print(json.dumps(plan,ensure_ascii=False,indent=2))
    if not plan['train_needed']: return 0
    st=cl._read(); after_id=int(st.get('last_trained_sample_id',0)); after_ts=float(st.get('conversation_trained_at',0.0))
    parts=[]
    a=ROOT/'data/training/incremental/harvest.jsonl'; b=ROOT/'data/training/incremental/conversations.jsonl'
    if Path(args.db).exists(): parts.append(export_incremental(ROOT/args.db,a,after_id))
    if Path(args.conversation_db).exists(): parts.append(export_conversation_incremental(ROOT/args.conversation_db,b,after_ts,min_quality=.6))
    # Merge by stable sample hash so the same conversation cannot be trained twice.
    merged=ROOT/'data/training/incremental/current.jsonl'; merged.parent.mkdir(parents=True,exist_ok=True); seen=set(); written=0
    with merged.open('w',encoding='utf-8') as out:
        for part in parts:
            p=Path(part['output'])
            if not p.exists(): continue
            for line in p.read_text(encoding='utf-8').splitlines():
                if not line.strip(): continue
                obj=json.loads(line); h=str(obj.get('id',''))
                if not h or h in seen: continue
                seen.add(h); out.write(json.dumps(obj,ensure_ascii=False)+'\n'); written+=1
    manifest={'plan':plan,'parts':parts,'incremental':{'samples':written,'output':str(merged),'ids':sorted(seen)},'resume_checkpoint':st.get('last_checkpoint',''),'operator_action':'train-candidate'}
    out=ROOT/'artifacts/continuous_plan.json'; out.parent.mkdir(parents=True,exist_ok=True); out.write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8'); print(json.dumps(manifest,ensure_ascii=False,indent=2)); return 0
if __name__=='__main__': raise SystemExit(main())
```

---

### `332/588` `backend/scripts/convert_gguf.py`

- **المسار الكامل:** `F:\1f\p\ALI_Studio_Pro_Design4_4.6.0\04_Adaptive_Hybrid\backend/scripts/convert_gguf.py`
- **الحجم:** 825 بايت (0.8 KB)
- **الامتداد:** `.py`

```python
# -*- coding: utf-8 -*-
from pathlib import Path
import argparse,sys,json
ROOT=Path(__file__).resolve().parent.parent; sys.path.insert(0,str(ROOT))
from tools.gguf import GGUFManager
ap=argparse.ArgumentParser(); ap.add_argument('hf_dir'); ap.add_argument('outfile'); ap.add_argument('--llama-dir',default='vendor/llama.cpp'); ap.add_argument('--outtype',default='f16'); ap.add_argument('--quantize',default=''); ap.add_argument('--quantized-out',default='')
args=ap.parse_args(); m=GGUFManager(args.llama_dir); r=m.convert(args.hf_dir,args.outfile,args.outtype); print(json.dumps(r,ensure_ascii=False,indent=2));
if args.quantize: print(json.dumps(m.quantize(args.outfile,args.quantized_out or str(Path(args.outfile).with_name(Path(args.outfile).stem+'-'+args.quantize+'.gguf')),args.quantize),ensure_ascii=False,indent=2))
```

---

### `333/588` `backend/scripts/desktop_server.py`

- **المسار الكامل:** `F:\1f\p\ALI_Studio_Pro_Design4_4.6.0\04_Adaptive_Hybrid\backend/scripts/desktop_server.py`
- **الحجم:** 34141 بايت (33.3 KB)