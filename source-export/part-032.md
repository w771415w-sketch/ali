    ]
  },
  "validation": {
    "loss": 3.7926310777664183,
    "perplexity": 44.37299562522513,
    "samples": 10
  },
  "hf": "/mnt/data/ALI_Studio_Pro_v3/ali_work/models/checkpoints/ALI-Conversation-v0.2/final-000350/hf",
  "created_at": 1790895323.3180726
}
```

---

### `117/588` `backend/evaluation/README.md`

- **المسار الكامل:** `F:\1f\p\ALI_Studio_Pro_Design4_4.6.0\04_Adaptive_Hybrid\backend/evaluation/README.md`
- **الحجم:** 225 بايت (0.2 KB)
- **الامتداد:** `.md`

```markdown
# ALI Evaluation

Run the same Arabic/English, project, tool-calling, memory, safety and multimodal benchmarks before and after a candidate training run. Promotion requires regression checks and a recorded metric comparison.
```

---

### `118/588` `backend/evaluation/report.py`

- **المسار الكامل:** `F:\1f\p\ALI_Studio_Pro_Design4_4.6.0\04_Adaptive_Hybrid\backend/evaluation/report.py`
- **الحجم:** 603 بايت (0.6 KB)
- **الامتداد:** `.py`

```python
# -*- coding: utf-8 -*-
from __future__ import annotations
from pathlib import Path
import json,time
def compare(baseline:dict|None,candidate:dict|None)->dict:
    a=baseline or {}; b=candidate or {}; out={"created_at":time.time(),"baseline":a,"candidate":b,"deltas":{}}
    for k in set(a)|set(b):
        if isinstance(a.get(k),(int,float)) and isinstance(b.get(k),(int,float)): out["deltas"][k]=b[k]-a[k]
    return out
def save_report(path,report):
    p=Path(path); p.parent.mkdir(parents=True,exist_ok=True); p.write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8'); return p
```

---

### `119/588` `backend/evaluation/suite.py`

- **المسار الكامل:** `F:\1f\p\ALI_Studio_Pro_Design4_4.6.0\04_Adaptive_Hybrid\backend/evaluation/suite.py`
- **الحجم:** 2319 بايت (2.3 KB)
- **الامتداد:** `.py`

```python
# -*- coding: utf-8 -*-
"""Offline Arabic/English evaluation of a loaded ALI model.

Metrics deliberately stay simple and reproducible: loss/perplexity, response
language coverage, required-keyword coverage, and structured tool-call accuracy.
"""
from __future__ import annotations
from pathlib import Path
import json, math, re
from training.trainer import JsonlTextDataset, JsonlChatDataset, collate
from core.tool_protocol import parse_tool_calls
import torch

def _lang(text): return 'ar' if re.search(r'[\u0600-\u06ff]',text) else 'en'
def evaluate_suite(engine, path:str|Path, max_cases:int=200)->dict:
    rows=[json.loads(x) for x in Path(path).read_text(encoding='utf-8').splitlines() if x.strip()][:max_cases]
    metrics={'cases':len(rows),'arabic':0,'english':0,'language_matches':0,'keyword_hits':0,'tool_cases':0,'tool_hits':0}
    for r in rows:
        q=next((m.get('content','') for m in r.get('messages',[]) if m.get('role')=='user'),'')
        lang=r.get('language') or _lang(q); metrics['arabic' if lang=='ar' else 'english']+=1
        try: answer=engine.complete([m for m in r.get('messages',[]) if m.get('role')=='user'],max_new_tokens=96,temperature=0)
        except Exception: continue
        if _lang(answer)==lang:metrics['language_matches']+=1
        kws=r.get('expected_keywords') or []
        if kws and any(str(k).lower() in answer.lower() for k in kws):metrics['keyword_hits']+=1
        if r.get('category')=='tool-calling':
            metrics['tool_cases']+=1
            calls=parse_tool_calls(answer)
            if calls and calls[0].get('tool'):metrics['tool_hits']+=1
    n=max(1,metrics['cases']); metrics['language_accuracy']=metrics['language_matches']/n; metrics['keyword_coverage']=metrics['keyword_hits']/n; metrics['tool_call_accuracy']=metrics['tool_hits']/max(1,metrics['tool_cases']); return metrics

def evaluate_loss(model,tokenizer,path,device='cpu'):
    ds=JsonlChatDataset(path,tokenizer,model.config.max_position_embeddings); total=0.; n=0; model.to(device).eval()
    with torch.no_grad():
        for i in range(len(ds)):
            b=collate([ds[i]],tokenizer.pad_id); b={k:v.to(device) for k,v in b.items()}; out=model(**b); total+=float(out['loss']); n+=1
    loss=total/max(1,n); return {'loss':loss,'perplexity':math.exp(min(20,loss)),'samples':n}
```

---

### `120/588` `backend/external/Hermes/README.md`

- **المسار الكامل:** `F:\1f\p\ALI_Studio_Pro_Design4_4.6.0\04_Adaptive_Hybrid\backend/external/Hermes/README.md`
- **الحجم:** 171 بايت (0.2 KB)
- **الامتداد:** `.md`

```markdown
# External Hermes mount point

ALI AI does not copy Hermes here. Keep your Hermes installation at `D:\AI ALI\Hermes\`.
This directory is only a documentation placeholder.
```

---

### `121/588` `backend/FINAL_VERIFICATION.json`

- **المسار الكامل:** `F:\1f\p\ALI_Studio_Pro_Design4_4.6.0\04_Adaptive_Hybrid\backend/FINAL_VERIFICATION.json`
- **الحجم:** 737 بايت (0.7 KB)
- **الامتداد:** `.json`

```json
{
  "version": "4.2.0",
  "release": "Professional Assistant P50 · Accumulated Training",
  "source_tests": {
    "gui": "174 passed, 3 skipped",
    "compileall": "PASS",
    "kca_doctor": "100/100 PASS",
    "release_check": "PASS"
  },
  "model_smoke": {
    "status": "PASS",
    "model": "ALI-Bootstrap-v2.5",
    "training": "20-step from-scratch micro bootstrap",
    "note": "Functional startup/inference checkpoint; not production-scale quality."
  },
  "package": {
    "zip_entries": 391,
    "required_payloads_present": true,
    "private_credential_files_excluded": true
  },
  "windows_native_test": "Not executed in this Linux container; the project includes Windows setup/launcher/build scripts for the native test."
}
```

---

### `122/588` `backend/HARVEST-AND-BUILD.bat`

- **المسار الكامل:** `F:\1f\p\ALI_Studio_Pro_Design4_4.6.0\04_Adaptive_Hybrid\backend/HARVEST-AND-BUILD.bat`
- **الحجم:** 434 بايت (0.4 KB)
- **الامتداد:** `.bat`

```batch
@echo off
setlocal
chcp 65001 >nul
cd /d "%~dp0"
if not exist ".venv\Scripts\python.exe" call SETUP.bat
call ".venv\Scripts\activate.bat"
set "DATA_ROOT=%~1"
if "%DATA_ROOT%"=="" (
  echo Enter the folder that contains your books, conversations, documents or datasets.
  set /p "DATA_ROOT=Data folder: "
)
if "%DATA_ROOT%"=="" exit /b 1
python scripts\harvest.py "%DATA_ROOT%" --db artifacts\harvest.sqlite3 --export data\train
pause
```

---

### `123/588` `backend/HERMES_INTEGRATION_STATE.json`

- **المسار الكامل:** `F:\1f\p\ALI_Studio_Pro_Design4_4.6.0\04_Adaptive_Hybrid\backend/HERMES_INTEGRATION_STATE.json`
- **الحجم:** 1001 بايت (1.0 KB)
- **الامتداد:** `.json`

```json
{
  "base_app_version": "2.5.0",
  "integration_revision": "2.6.0",
  "hermes_root": "D:\\AI ALI\\Hermes",
  "files_not_bundled": [
    ".env",
    "auth.json",
    "credentials",
    "private_keys"
  ],
  "model_path": "models/active/ALI-Bootstrap-v2.5",
  "training_policy": {
    "profile": "p50-auto",
    "mode": "from-scratch",
    "train_mode": "full",
    "dataset_mode": "chat",
    "epochs": 1,
    "max_steps": 0,
    "seq_len": 256,
    "batch_size": 1,
    "grad_accum": 16,
    "learning_rate": 0.0003,
    "warmup_steps": 20,
    "save_every": 50,
    "eval_every": 50,
    "gradient_checkpointing": true,
    "amp": false,
    "resume_checkpoints": true,
    "scale": "small",
    "bootstrap_scale": "micro",
    "cpu_threads": 6
  },
  "hardware_profile": {
    "label": "Lenovo ThinkPad P50 (user target)",
    "cpu_threads": 8,
    "physical_cores": 4,
    "ram_gb": 32,
    "gpu_name": "NVIDIA Quadro M1000M",
    "vram_gb": 2,
    "cuda_capability": [
      5,
      0
    ]
  }
}
```

---

### `124/588` `backend/inference/__init__.py`

- **المسار الكامل:** `F:\1f\p\ALI_Studio_Pro_Design4_4.6.0\04_Adaptive_Hybrid\backend/inference/__init__.py`
- **الحجم:** 1 بايت (0.0 KB)
- **الامتداد:** `.py`

```python

```

---

### `125/588` `backend/inference/batch.py`

- **المسار الكامل:** `F:\1f\p\ALI_Studio_Pro_Design4_4.6.0\04_Adaptive_Hybrid\backend/inference/batch.py`
- **الحجم:** 460 بايت (0.4 KB)
- **الامتداد:** `.py`

```python
# -*- coding: utf-8 -*-
"""Bounded batch inference for offline evaluation and data generation."""
from __future__ import annotations
from typing import Iterable

def batch_complete(engine, prompts: Iterable[str], batch_size: int = 1, **kwargs) -> list[str]:
    prompts=list(prompts); out=[]
    for i in range(0,len(prompts),max(1,int(batch_size))):
        for p in prompts[i:i+max(1,int(batch_size))]: out.append(engine.complete(p,**kwargs))
    return out
```

---

### `126/588` `backend/inference/context.py`

- **المسار الكامل:** `F:\1f\p\ALI_Studio_Pro_Design4_4.6.0\04_Adaptive_Hybrid\backend/inference/context.py`
- **الحجم:** 1410 بايت (1.4 KB)
- **الامتداد:** `.py`

```python
# -*- coding: utf-8 -*-
"""Context budgeting for low-memory ALI inference."""
from __future__ import annotations
from dataclasses import dataclass
from typing import Any

@dataclass
class ContextBudget:
    max_tokens: int
    reserved_output_tokens: int
    prompt_tokens: int
    kept_messages: int
    truncated: bool


def fit_messages(messages: list[dict[str, Any]], tokenizer, max_context: int, reserved_output: int = 128) -> tuple[list[dict[str, Any]], ContextBudget]:
    max_context = max(64, int(max_context))
    reserved_output = max(8, min(int(reserved_output), max_context // 2))
    budget = max_context - reserved_output
    kept: list[dict[str, Any]] = []
    total = 0
    truncated = False
    # System stays first; then keep newest turns that fit.
    system = [m for m in messages if m.get("role") == "system"][:1]
    rest = [m for m in messages if m.get("role") != "system"]
    base = system
    if base:
        total = len(tokenizer.encode(base[0].get("content", ""), add_bos=False, add_eos=False))
    for msg in reversed(rest):
        n = len(tokenizer.encode(str(msg.get("content", "")), add_bos=False, add_eos=False)) + 4
        if total + n > budget:
            truncated = True
            break
        kept.append(msg)
        total += n
    kept.reverse()
    final = base + kept
    return final, ContextBudget(max_context, reserved_output, total, len(final), truncated)
```

---

### `127/588` `backend/inference/engine.py`

- **المسار الكامل:** `F:\1f\p\ALI_Studio_Pro_Design4_4.6.0\04_Adaptive_Hybrid\backend/inference/engine.py`
- **الحجم:** 3247 بايت (3.2 KB)
- **الامتداد:** `.py`

```python
# -*- coding: utf-8 -*-
"""Local ALI inference engine — ALI's own trained neural model only."""
from __future__ import annotations
from pathlib import Path
from typing import Iterator
import json, torch
from model.ali_lm import AliConfig, ALIForCausalLM, load_state
from tokenizer.spm import AliTokenizer
from inference.context import fit_messages

class LocalInference:
    def __init__(self, model_dir:str|Path, tokenizer_dir:str|Path|None=None, device:str='cpu'):
        self.model_dir=Path(model_dir); tok_path=Path(tokenizer_dir or model_dir); self.tokenizer=AliTokenizer(tok_path/'tokenizer.model' if tok_path.is_dir() else tok_path); self.device=torch.device(device)
        cfg=json.loads((self.model_dir/'config.json').read_text(encoding='utf-8')); self.model_version=self.model_dir.name; self.model=ALIForCausalLM(AliConfig.from_dict(cfg)); state=self.model_dir/'model.safetensors'
        if not state.exists(): state=self.model_dir/'pytorch_model.bin'
        load_state(self.model,state,self.device)
        self.dtype='float32'
        if self.device.type=='cuda':
            self.model.half(); self.dtype='float16'
        self.model.eval()
    def prompt(self,messages:list[dict],system:str='')->str:
        rows=[]
        if system: rows.append({'role':'system','content':system})
        rows.extend(messages)
        return ''.join(f"<|{m['role']}|>\n{m['content']}<|eot|>\n" for m in rows)+'<|assistant|>\n'
    def stream(self,messages:list[dict],system:str='',max_new_tokens:int=128,temperature:float=.7,top_k:int=40,context_size:int|None=None)->Iterator[str]:
        rows=[]
        if system: rows.append({'role':'system','content':system})
        rows.extend(messages)
        rows,_budget=fit_messages(rows,self.tokenizer,int(context_size or self.model.config.max_position_embeddings),reserved_output=int(max_new_tokens)+8)
        p=self.prompt([m for m in rows if m.get('role')!='system'],system=next((m['content'] for m in rows if m.get('role')=='system'),'')); ids=self.tokenizer.encode(p,add_bos=True,add_eos=False); max_ctx=self.model.config.max_position_embeddings; ids=ids[-max(1,max_ctx-max_new_tokens):]
        inp=torch.tensor([ids],dtype=torch.long,device=self.device); out=[]; last_text=''
        with torch.inference_mode():
            for tok in self.model.generate_stream(inp,max_new_tokens=max_new_tokens,temperature=temperature,top_k=top_k,eos_token_id=self.tokenizer.eos_id,bad_token_ids=[self.tokenizer.sp.unk_id(),self.tokenizer.bos_id,self.tokenizer.pad_id]+[self.tokenizer.special_id(x) for x in ('<|system|>','<|user|>','<|assistant|>','<|eot|>') if self.tokenizer.special_id(x)>=0],stop_token_ids=[self.tokenizer.eos_id,self.tokenizer.special_id('<|eot|>')]):
                out.append(tok)
                piece=self.tokenizer.decode(out)
                delta=piece[len(last_text):] if piece.startswith(last_text) else piece
                if delta:
                    yield delta
                last_text=piece
    def complete(self,prompt,**kwargs)->str:
        rows=prompt if isinstance(prompt,list) else [{'role':'user','content':str(prompt)}]
        return ''.join(self.stream(rows,**kwargs))


# Compatibility alias used by integrations.
InferenceEngine = LocalInference
```

---

### `128/588` `backend/inference/gguf.py`

- **المسار الكامل:** `F:\1f\p\ALI_Studio_Pro_Design4_4.6.0\04_Adaptive_Hybrid\backend/inference/gguf.py`
- **الحجم:** 1838 بايت (1.8 KB)
- **الامتداد:** `.py`

```python
# -*- coding: utf-8 -*-
"""Run ALI's own GGUF locally through an installed llama.cpp binary."""
from __future__ import annotations
from pathlib import Path
import os, subprocess
from typing import Iterator

class GGUFInference:
    def __init__(self, model_path: str | Path, llama_dir: str | Path = "vendor/llama.cpp", n_gpu_layers: int = 0):
        self.model = Path(model_path).resolve()
        self.root = Path(llama_dir).resolve()
        self.n_gpu_layers = max(0, int(n_gpu_layers))
        self.binary = self._find()
        if not self.model.exists():
            raise FileNotFoundError(self.model)
        if not self.binary:
            raise FileNotFoundError("llama-cli executable not found in vendor/llama.cpp")

    def _find(self) -> Path | None:
        names = ["llama-cli.exe", "llama-cli"]
        candidates = []
        for n in names:
            candidates += [self.root / n, self.root / "build" / "bin" / n, self.root / "bin" / n]
        return next((p for p in candidates if p.exists()), None)

    def stream(self, prompt: str, max_new_tokens: int = 256, context: int = 512, temperature: float = 0.7) -> Iterator[str]:
        cmd = [str(self.binary), "-m", str(self.model), "-p", prompt, "-n", str(max_new_tokens), "-c", str(context), "-ngl", str(self.n_gpu_layers), "--no-display-prompt", "--no-show-timings", "-no-cnv"]
        if temperature <= 0:
            cmd += ["--temp", "0"]
        else:
            cmd += ["--temp", str(temperature)]
        env = dict(os.environ)
        p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, encoding="utf-8", errors="replace", cwd=str(self.root), bufsize=1, env=env)
        assert p.stdout is not None
        try:
            for line in p.stdout:
                yield line
        finally:
            p.wait(timeout=5)
```

---

### `129/588` `backend/inference/gguf_runtime.py`

- **المسار الكامل:** `F:\1f\p\ALI_Studio_Pro_Design4_4.6.0\04_Adaptive_Hybrid\backend/inference/gguf_runtime.py`
- **الحجم:** 2043 بايت (2.0 KB)
- **الامتداد:** `.py`

```python
# -*- coding: utf-8 -*-
"""Optional llama-server bridge using only the Python standard library."""
from __future__ import annotations
from pathlib import Path
import json,subprocess,time,urllib.request,urllib.error
class LlamaServer:
    def __init__(self,executable:str|Path,model:str|Path,port:int=8080,context:int=2048): self.executable=Path(executable); self.model=Path(model); self.port=int(port); self.context=int(context); self.proc=None
    @property
    def base_url(self): return f"http://127.0.0.1:{self.port}"
    def start(self):
        if self.proc and self.proc.poll() is None:return
        if not self.executable.exists():raise FileNotFoundError(self.executable)
        if not self.model.exists():raise FileNotFoundError(self.model)
        self.proc=subprocess.Popen([str(self.executable),"-m",str(self.model),"-c",str(self.context),"--host","127.0.0.1","--port",str(self.port)],stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True)
        for _ in range(80):
            try:
                with urllib.request.urlopen(self.base_url+"/health",timeout=1) as r:
                    if r.status<500:return
            except Exception:time.sleep(.25)
        raise RuntimeError("llama-server did not become ready")
    def stop(self):
        if self.proc and self.proc.poll() is None:self.proc.terminate()
        self.proc=None
    def chat(self,messages,max_tokens=256,temperature=.7):
        body=json.dumps({"messages":messages,"max_tokens":int(max_tokens),"temperature":float(temperature)}).encode()
        req=urllib.request.Request(self.base_url+"/v1/chat/completions",data=body,headers={"Content-Type":"application/json"},method="POST")
        try:
            with urllib.request.urlopen(req,timeout=1800) as r:data=json.loads(r.read().decode())
        except urllib.error.HTTPError as e:raise RuntimeError(e.read().decode(errors="replace")[-4000:])
        choices=data.get("choices") or []; text=choices[0].get("message",{}).get("content","") if choices else ""
        return {"text":text,"raw":data}
```

---

### `130/588` `backend/inference/llama_engine.py`

- **المسار الكامل:** `F:\1f\p\ALI_Studio_Pro_Design4_4.6.0\04_Adaptive_Hybrid\backend/inference/llama_engine.py`
- **الحجم:** 3494 بايت (3.4 KB)
- **الامتداد:** `.py`

```python
# -*- coding: utf-8 -*-
"""Local GGUF chat engine backed by llama.cpp's OpenAI-compatible llama-server.

The engine is deliberately optional: when the model/binary are absent the main
ALI runtime can continue with its internal model. GPU offload is adaptive and
falls back to CPU automatically in auto mode if the installed llama.cpp build
cannot use the legacy Maxwell GPU.
"""
from __future__ import annotations
from pathlib import Path
from typing import Iterable, Any

from inference.llama_server import LlamaServer
from runtime.device_policy import gguf_offload_policy
from runtime.hardware import detect


class LlamaServerEngine:
    def __init__(self, executable: str | Path, model: str | Path, *, compute_mode: str = "auto", context: int = 2048, model_version: str = ""):
        self.executable = Path(executable).resolve()
        self.model = Path(model).resolve()
        self.tokenizer = None
        self.model_version = model_version or self.model.stem
        hw = detect(probe_torch=False, force=True)
        policy = gguf_offload_policy(hw, mode=compute_mode, total_layers=24)
        self.device = str(policy.get("device", "cpu"))
        self.n_gpu_layers = int(policy.get("n_gpu_layers", 0))
        self.gpu_memory_fraction = float(policy.get("gpu_memory_fraction", 0.0) or 0.0)
        self.context = int(context)
        self.server = LlamaServer(
            self.executable,
            self.model,
            port=48921,
            n_gpu_layers=self.n_gpu_layers,
            context=self.context,
        )

    def _ensure(self) -> None:
        try:
            self.server.start()
        except Exception:
            # Auto mode must prefer a working CPU inference path over a hard
            # failure if a CUDA/Maxwell binary is present but incompatible.
            if self.device != "cpu":
                self.device = "cpu"
                self.n_gpu_layers = 0
                self.server.stop()
                self.server = LlamaServer(
                    self.executable,
                    self.model,
                    port=48921,
                    n_gpu_layers=0,
                    context=self.context,
                )
                self.server.start()
            else:
                raise

    def complete(self, messages: list[dict[str, Any]], *, system: str = "", max_new_tokens: int = 256, temperature: float = .6) -> str:
        self._ensure()
        final_messages = []
        if system:
            final_messages.append({"role": "system", "content": str(system)})
        final_messages.extend(messages)
        return str((self.server.chat(final_messages, max_tokens=max_new_tokens, temperature=temperature) or {}).get('text',''))

    def stream(self, messages: list[dict[str, Any]], *, system: str = "", max_new_tokens: int = 256, temperature: float = .6) -> Iterable[str]:
        # The local llama-server bridge uses a deterministic non-streaming call
        # for maximum compatibility on older Windows/Maxwell environments. The
        # UI still receives the answer through the normal stream event contract.
        self._ensure()
        final_messages=[]
        if system: final_messages.append({'role':'system','content':str(system)})
        final_messages.extend(messages)
        yield from self.server.stream_chat(final_messages, max_tokens=max_new_tokens, temperature=temperature)

    def close(self) -> None:
        try:
            self.server.stop()
        except Exception:
            pass
```

---

### `131/588` `backend/inference/llama_server.py`

- **المسار الكامل:** `F:\1f\p\ALI_Studio_Pro_Design4_4.6.0\04_Adaptive_Hybrid\backend/inference/llama_server.py`
- **الحجم:** 3944 بايت (3.9 KB)
- **الامتداد:** `.py`

```python
# -*- coding: utf-8 -*-
"""Local llama-server bridge with adaptive GPU offload and streaming-safe calls."""
from __future__ import annotations
from pathlib import Path
import json, subprocess, time, urllib.request, urllib.error, socket, os

class LlamaServer:
    def __init__(self, executable: str|Path, model: str|Path, port: int=0, context: int=2048, n_gpu_layers: int=0):
        self.executable=Path(executable).resolve(); self.model=Path(model).resolve()
        self.port=int(port); self.context=int(context); self.n_gpu_layers=max(0,int(n_gpu_layers)); self.proc=None

    def _pick_port(self):
        if self.port > 0:
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as probe:
                    probe.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                    probe.bind(('127.0.0.1', self.port))
                return self.port
            except OSError:
                pass
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as probe:
            probe.bind(('127.0.0.1', 0))
            return int(probe.getsockname()[1])

    @property
    def base_url(self): return f'http://127.0.0.1:{self.port}'

    def start(self):
        if self.proc and self.proc.poll() is None: return
        if not self.executable.exists(): raise FileNotFoundError(self.executable)
        if not self.model.exists(): raise FileNotFoundError(self.model)
        preferred = self.port
        self.port = self._pick_port()
        cmd=[str(self.executable),'-m',str(self.model),'-c',str(self.context),'--host','127.0.0.1','--port',str(self.port),'-ngl',str(self.n_gpu_layers)]
        env=dict(os.environ)
        self.proc=subprocess.Popen(cmd,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True,errors='replace',env=env)
        for _ in range(120):
            try:
                with urllib.request.urlopen(self.base_url+'/health',timeout=1) as r:
                    if r.status<500: return
            except Exception: time.sleep(.25)
        self.stop(); raise RuntimeError('llama-server did not become ready')

    def stop(self):
        if self.proc and self.proc.poll() is None:
            try: self.proc.terminate(); self.proc.wait(timeout=3)
            except Exception:
                try: self.proc.kill()
                except Exception: pass
        self.proc=None

    def chat(self,messages,max_tokens=256,temperature=.7):
        body=json.dumps({'messages':messages,'max_tokens':int(max_tokens),'temperature':float(temperature),'stream':False}).encode()
        req=urllib.request.Request(self.base_url+'/v1/chat/completions',data=body,headers={'Content-Type':'application/json'},method='POST')
        try:
            with urllib.request.urlopen(req,timeout=1800) as r: data=json.loads(r.read().decode('utf-8','replace'))
        except urllib.error.HTTPError as e: raise RuntimeError(e.read().decode(errors='replace')[-4000:])
        choices=data.get('choices') or []
        text=choices[0].get('message',{}).get('content','') if choices else ''
        return {'text':text,'raw':data}

    def stream_chat(self,messages,max_tokens=256,temperature=.7):
        body=json.dumps({'messages':messages,'max_tokens':int(max_tokens),'temperature':float(temperature),'stream':True}).encode()
        req=urllib.request.Request(self.base_url+'/v1/chat/completions',data=body,headers={'Content-Type':'application/json'},method='POST')
        with urllib.request.urlopen(req,timeout=1800) as r:
            for raw in r:
                line=raw.decode('utf-8','replace').strip()
                if not line.startswith('data:'): continue
                payload=line[5:].strip()
                if payload=='[DONE]': break
                try:
                    data=json.loads(payload); delta=((data.get('choices') or [{}])[0].get('delta') or {}).get('content')
                    if delta: yield delta
                except Exception: continue
```

---

### `132/588` `backend/inference/quantized.py`

- **المسار الكامل:** `F:\1f\p\ALI_Studio_Pro_Design4_4.6.0\04_Adaptive_Hybrid\backend/inference/quantized.py`
- **الحجم:** 2110 بايت (2.1 KB)
- **الامتداد:** `.py`

```python
# -*- coding: utf-8 -*-
"""Real PyTorch CPU quantization helpers for ALI.

Dynamic int8 quantization targets Linear modules and is suitable for CPU inference
on the user's 32GB-RAM machine. GGUF remains the preferred disk/runtime format when
llama.cpp tooling is installed.
"""
from __future__ import annotations
from pathlib import Path
import torch
from torch import nn
from typing import Any

def quantize_cpu_int8(model: nn.Module) -> nn.Module:
    model=model.cpu().eval()
    try:
        return torch.ao.quantization.quantize_dynamic(model,{nn.Linear},dtype=torch.qint8)
    except Exception:
        return model

def save_quantized(model: nn.Module, path: str|Path) -> Path:
    p=Path(path); p.parent.mkdir(parents=True,exist_ok=True)
    # Save the quantized state plus a small descriptor so loading can recreate
    # the same dynamic-quantization wrapper around a fresh ALI architecture.
    torch.save({'format':'torch_dynamic_int8_v1','state_dict':model.state_dict()},p)
    return p

def load_quantized(model: nn.Module, path: str|Path, device: str='cpu')->nn.Module:
    p=Path(path); blob=torch.load(p,map_location=device,weights_only=False)
    if isinstance(blob,dict) and blob.get('format')=='torch_dynamic_int8_v1':
        model=quantize_cpu_int8(model)
        model.load_state_dict(blob['state_dict'],strict=False)
        return model
    if isinstance(blob,dict) and 'state_dict' in blob:
        blob=blob['state_dict']
    model.load_state_dict(blob,strict=False); return model

def inspect_quantized(path: str|Path)->dict[str,Any]:
    p=Path(path); info={'path':str(p),'exists':p.exists(),'size_bytes':p.stat().st_size if p.exists() else 0,'format':'unknown'}
    if not p.exists(): return info
    try:
        blob=torch.load(p,map_location='cpu',weights_only=False)
        info['format']=blob.get('format','torch_state_dict') if isinstance(blob,dict) else 'torch_object'
        info['tensor_count']=len(blob.get('state_dict',{})) if isinstance(blob,dict) and isinstance(blob.get('state_dict'),dict) else None
    except Exception as e: info['error']=str(e)
    return info
```

---

### `133/588` `backend/integration/hermes/__init__.py`

- **المسار الكامل:** `F:\1f\p\ALI_Studio_Pro_Design4_4.6.0\04_Adaptive_Hybrid\backend/integration/hermes/__init__.py`
- **الحجم:** 263 بايت (0.3 KB)
- **الامتداد:** `.py`

```python
"""Hermes external integration for ALI AI. Hermes remains outside the project tree."""
from .config import HermesConfig
from .router import HermesContextRouter
from .adapter import HermesAdapter

__all__ = ["HermesConfig", "HermesContextRouter", "HermesAdapter"]
```

---

### `134/588` `backend/integration/hermes/adapter.py`

- **المسار الكامل:** `F:\1f\p\ALI_Studio_Pro_Design4_4.6.0\04_Adaptive_Hybrid\backend/integration/hermes/adapter.py`
- **الحجم:** 4705 بايت (4.6 KB)
- **الامتداد:** `.py`

```python
from __future__ import annotations
from pathlib import Path
import sqlite3, json, re
from typing import Any
from .config import HermesConfig, load_config
from .security import safe_root, guard_file, READABLE_DB

class HermesAdapter:
    """Safe, read-oriented bridge to an external Hermes installation.

    It never copies Hermes into ALI and it never exposes .env/auth.json contents.
    """
    def __init__(self, config: HermesConfig | None = None):
        self.config = config or load_config()
        self.root = safe_root(self.config.root)

    def status(self) -> dict[str, Any]:
        exists = self.root.exists() and self.root.is_dir()
        return {
            "enabled": self.config.enabled, "root": str(self.root),
            "exists": exists, "mode": "read-only" if self.config.read_only else "write-enabled",
            "database_reads": bool(self.config.allow_database_reads),
            "api": bool(self.config.allow_api), "mcp": bool(self.config.allow_mcp),
        }

    def read_text(self, relative: str) -> str:
        if not self.config.enabled:
            raise RuntimeError("Hermes integration is disabled")
        p = guard_file(self.root, relative)
        if not p.exists():
            raise FileNotFoundError(str(p))
        if p.stat().st_size > self.config.max_file_bytes:
            raise ValueError("Hermes file exceeds configured read limit")
        return p.read_text(encoding="utf-8", errors="replace")[: self.config.max_context_chars]

    def list_memories(self, limit: int = 12) -> list[dict[str, str]]:
        out=[]
        mem = self.root / "memories"
        if not mem.exists(): return out
        for p in sorted(mem.rglob("*.md"))[:max(1,int(limit))]:
            try:
                guard_file(self.root, p)
                out.append({"name": p.name, "path": p.relative_to(self.root).as_posix()})
            except Exception:
                continue
        return out

    def list_skills(self, limit: int = 100) -> list[dict[str, str]]:
        out=[]; skills=self.root/'skills'
        if not skills.exists(): return out
        for p in sorted(skills.rglob('SKILL.md'))[:max(1,int(limit))]:
            try:
                guard_file(self.root,p); out.append({"name":p.parent.name,"path":p.relative_to(self.root).as_posix()})
            except Exception: continue
        return out

    def read_database(self, db_name: str, query: str, params: tuple = (), limit: int = 100) -> list[dict[str, Any]]:
        if not self.config.allow_database_reads:
            raise PermissionError("Hermes database reads are disabled")
        if db_name not in READABLE_DB:
            raise PermissionError("Database is not in Hermes read-only allowlist")
        p=guard_file(self.root, db_name, allow_db=True)
        if not p.exists(): raise FileNotFoundError(str(p))
        if not re.match(r"^\s*(SELECT|PRAGMA)\b", query, re.I):
            raise PermissionError("Hermes database adapter only accepts SELECT/PRAGMA")
        query = query.rstrip(' ;') + f" LIMIT {max(1,min(int(limit),1000))}" if re.match(r"^\s*SELECT\b",query,re.I) and ' limit ' not in query.lower() else query
        uri=f"file:{p.as_posix()}?mode=ro"
        con=sqlite3.connect(uri, uri=True); con.row_factory=sqlite3.Row
        try:
            rows=con.execute(query, params).fetchall()
            return [dict(r) for r in rows]
        finally:
            con.close()

    def context_snapshot(self, query: str = "") -> dict[str, Any]:
        q=query.lower()
        data: dict[str, Any] = {"status": self.status()}
        if not data["status"]["exists"]:
            return data
        wants_memory=any(k in q for k in ["memory","ذاكرة","ذكريات","user.md","soul.md","المعلومات المحفوظة"])
        wants_project=any(k in q for k in ["project","projects","مشروع","مشاريع","kanban","tasks","مهام"])
        if wants_memory:
            for rel,key in [("memories/MEMORY.md","memory"),("memories/USER.md","user_profile"),("SOUL.md","soul")]:
                try: data[key]=self.read_text(rel)
                except Exception as e: data[key+"_error"]=str(e)
            data["memory_index"]=self.list_memories()
        if wants_project and self.config.allow_database_reads:
            for db in ("projects.db","kanban.db"):
                try:
                    tables=self.read_database(db,"SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")
                    data[db]={"tables":tables}
                except Exception as e: data[db]={"error":str(e)}
        if "skill" in q or "مهار" in q or "skills" in q:
            data["skills"]=self.list_skills()
        return data
```

---

### `135/588` `backend/integration/hermes/api.py`

- **المسار الكامل:** `F:\1f\p\ALI_Studio_Pro_Design4_4.6.0\04_Adaptive_Hybrid\backend/integration/hermes/api.py`
- **الحجم:** 902 بايت (0.9 KB)
- **الامتداد:** `.py`

```python
from __future__ import annotations
"""Optional future API bridge. No Hermes endpoint is assumed without explicit configuration."""
from dataclasses import dataclass
import urllib.request, json

@dataclass
class HermesApiBridge:
    base_url: str = ""
    enabled: bool = False

    def health(self):
        if not (self.enabled and self.base_url):
            return {"enabled":False,"status":"not-configured"}
        req=urllib.request.Request(self.base_url.rstrip('/') + "/health", method="GET")
        try:
            with urllib.request.urlopen(req, timeout=3) as r:
                body=r.read().decode('utf-8','replace')[:4000]
            try: return {"enabled":True,"status":"ok","data":json.loads(body)}
            except Exception: return {"enabled":True,"status":"ok","data":body}
        except Exception as e:
            return {"enabled":True,"status":"unavailable","error":str(e)}
```

---

### `136/588` `backend/integration/hermes/config.py`

- **المسار الكامل:** `F:\1f\p\ALI_Studio_Pro_Design4_4.6.0\04_Adaptive_Hybrid\backend/integration/hermes/config.py`
- **الحجم:** 1038 بايت (1.0 KB)
- **الامتداد:** `.py`

```python
from __future__ import annotations
from dataclasses import dataclass, asdict
from pathlib import Path
import json, os

DEFAULT_HERMES_ROOT = Path(r"D:\AI ALI\Hermes")

@dataclass
class HermesConfig:
    enabled: bool = True
    root: str = str(DEFAULT_HERMES_ROOT)
    read_only: bool = True
    max_file_bytes: int = 2_000_000
    max_context_chars: int = 8_000
    allow_database_reads: bool = True
    allow_api: bool = False
    allow_mcp: bool = False

    def to_dict(self):
        return asdict(self)

def load_config(path: str | Path | None = None) -> HermesConfig:
    p = Path(path) if path else Path(__file__).resolve().parents[2] / "config" / "hermes_integration.json"
    data = {}
    try:
        if p.exists():
            data = json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        data = {}
    env_root = os.environ.get("ALI_HERMES_ROOT", "").strip()
    if env_root:
        data["root"] = env_root
    return HermesConfig(**{k:v for k,v in data.items() if k in HermesConfig.__dataclass_fields__})
```

---

### `137/588` `backend/integration/hermes/mcp.py`

- **المسار الكامل:** `F:\1f\p\ALI_Studio_Pro_Design4_4.6.0\04_Adaptive_Hybrid\backend/integration/hermes/mcp.py`
- **الحجم:** 358 بايت (0.3 KB)
- **الامتداد:** `.py`

```python
from __future__ import annotations
"""MCP configuration boundary for a future Hermes MCP endpoint."""
from dataclasses import dataclass

@dataclass
class HermesMcpBridge:
    enabled: bool = False
    endpoint: str = ""

    def status(self):
        return {"enabled":self.enabled,"endpoint":self.endpoint,"configured":bool(self.endpoint) and self.enabled}
```

---

### `138/588` `backend/integration/hermes/README.md`

- **المسار الكامل:** `F:\1f\p\ALI_Studio_Pro_Design4_4.6.0\04_Adaptive_Hybrid\backend/integration/hermes/README.md`
- **الحجم:** 544 بايت (0.5 KB)
- **الامتداد:** `.md`

```markdown
# ALI AI ↔ Hermes external integration

Hermes is **not copied into ALI AI**. The integration treats Hermes as an external installation at:

`D:\AI ALI\Hermes\`

Default access is read-only. ALI may inspect approved Markdown memory, the read-only project/kanban SQLite databases, and skill indexes. `.env`, `auth.json`, credential files and private keys are explicitly blocked.

API and MCP bridges are configuration boundaries only until the actual Hermes protocol endpoint is supplied. No fake endpoint or undocumented protocol is assumed.
```

---

### `139/588` `backend/integration/hermes/reference_inventory.json`

- **المسار الكامل:** `F:\1f\p\ALI_Studio_Pro_Design4_4.6.0\04_Adaptive_Hybrid\backend/integration/hermes/reference_inventory.json`
- **الحجم:** 67 بايت (0.1 KB)
- **الامتداد:** `.json`

```json
{
  "error": "'Rar5FileInfo' object has no attribute 'flag_bits'"
}
```

---

### `140/588` `backend/integration/hermes/router.py`

- **المسار الكامل:** `F:\1f\p\ALI_Studio_Pro_Design4_4.6.0\04_Adaptive_Hybrid\backend/integration/hermes/router.py`
- **الحجم:** 1436 بايت (1.4 KB)
- **الامتداد:** `.py`

```python
from __future__ import annotations
import json
from typing import Any
from .adapter import HermesAdapter
from .config import HermesConfig

class HermesContextRouter:
    """Deterministic routing: Hermes is consulted only when the request is relevant."""
    KEYWORDS = (
        "hermes", "ذاكرة hermes", "ذكريات hermes", "مشاريع hermes", "مهام hermes",
        "بيانات hermes", "skills hermes", "مهارات hermes", "memory.md", "soul.md", "user.md",
        "hermes memory", "hermes project", "hermes skills"
    )
    def __init__(self, config: HermesConfig | None = None):
        self.adapter=HermesAdapter(config)
        self.last={"used":False,"reason":"not-routed","context":{}}
    def route(self, query: str) -> dict[str, Any]:
        text=str(query or "").strip()
        low=text.lower()
        relevant=any(k in low for k in self.KEYWORDS)
        if not relevant:
            self.last={"used":False,"reason":"no-hermes-intent","context":{}}
            return self.last
        ctx=self.adapter.context_snapshot(text)
        compact=json.dumps(ctx,ensure_ascii=False,indent=2)
        self.last={"used":True,"reason":"hermes-intent","context":ctx,"prompt_context":compact[:self.adapter.config.max_context_chars]}
        return self.last
    def status(self):
        s=self.adapter.status(); s["last_used"]=self.last.get("used",False); s["last_reason"]=self.last.get("reason"); return s
```

---

### `141/588` `backend/integration/hermes/security.py`

- **المسار الكامل:** `F:\1f\p\ALI_Studio_Pro_Design4_4.6.0\04_Adaptive_Hybrid\backend/integration/hermes/security.py`
- **الحجم:** 1276 بايت (1.2 KB)
- **الامتداد:** `.py`

```python
from __future__ import annotations
from pathlib import Path

BLOCKED_NAMES = {".env", "auth.json", "credentials.json", "token.json", "secrets.json"}
READABLE_FILES = {"SOUL.md", "MEMORY.md", "USER.md", "config.yaml", "skills/.bundled_manifest"}