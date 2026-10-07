- Current frequency in report: 1.51 GHz
- Socket: U3E1
- Addressing: 64-bit / 64-bit
- Processor ID: BFEBFBFF000506E3
- VT-x: enabled
- L1: 128 KB/core
- L2: 1 MB
- L3: 8 MB
- Reported CPU temperature: 41.05 C
- Raw temperature: 3142 (Kelvin x10) -> 314.2 K -> 41.05 C

## RAM
- 32 GB DDR4 (16+16)
- Available in report: 21.32 GB
- 2 modules, BANK 0 and BANK 2
- SK Hynix HMA82GS6AFR8N-UH
- 2133 MHz / PC4-17000
- 64-bit each; dual-channel total 128-bit
- SODIMM Form Factor 12
- Serials: 91BE090E, 91BE0910

## Storage
- Primary SSD: WDC PC SN720 SDAPNTW-512G-1006, 512 GB NVMe, GPT, reported Healthy
- SSD partitions: C: 152 GB, D: 322 GB
- SSD serial: E823_8FA6_BF53_0001_001B_448B_4601_9BE3
- Secondary HDD: WDC WD20SPZX-22UA7T0, 2 TB SATA 5400 RPM, MBR, reported Healthy
- HDD partitions: F: 1.67 TB, G: 194 GB
- HDD serial: WD-WX62E3049YU1

## GPU
- NVIDIA Quadro M1000M, Maxwell GM107, PCI VEN_10DE & DEV_13B1
- VRAM: 2 GB GDDR5
- Driver: 31.0.15.3818 (2 Jan 2024)
- Intel HD Graphics 530 integrated, PCI VEN_8086 & DEV_191B
- iGPU shared memory reported: 1 GB
- iGPU driver: 30.0.100.9865 (20 Aug 2021)
- Display: 1920x1080 @ 60 Hz, 32-bit

## Display / I/O / Network
- IPS FlexView, Lenovo LEN40BA
- Realtek High Definition Audio
- Enhanced 101/102-key Arabic 0401 keyboard
- Synaptics Pointing Device, TrackPoint + Touchpad
- Wi-Fi: Intel Dual Band Wireless-AC 8260; measured 72.2 Mbps, maximum reported 867 Mbps (802.11ac)
- Ethernet: Intel I219-LM Gigabit LAN
- Bluetooth Device (PAN)
- Wi-Fi MAC: 34:F3:9A:52:12:CD
- LAN MAC: C8:5B:76:BC:60:4A

## Battery
- Lenovo 00NY493, reported 90 Wh original
- Reported state: OK
- Charge in report: 38%
- Remaining: about 42 minutes

## Values that require dedicated tools
- Intel iGPU VRAM type: not precisely readable from WMI alone
- SSD TBW / SMART wear: needs smartctl or CrystalDiskInfo
- Exact CUDA core count: architecture knowledge can suggest a value but WMI alone is insufficient
- Exact battery cell count: needs Lenovo Vantage or equivalent vendor tooling
```

---

### `158/588` `backend/knowledge_seed/THINKPAD_P50_USER_PROFILE.md`

- **المسار الكامل:** `F:\1f\p\ALI_Studio_Pro_Design4_4.6.0\04_Adaptive_Hybrid\backend/knowledge_seed/THINKPAD_P50_USER_PROFILE.md`
- **الحجم:** 1032 بايت (1.0 KB)
- **الامتداد:** `.md`

```markdown
# ALI Target Hardware Profile

## Lenovo ThinkPad P50
- Model: 20EQS2L900
- OS: Windows 11 Pro 10.0.26200 x64
- CPU: Intel Core i7-6820HQ, 4C/8T, 2.70 GHz
- RAM: 32 GB DDR4 2133 MHz
- GPU: NVIDIA Quadro M1000M, 2 GB GDDR5, Maxwell GM107, compute capability 5.0 reported for policy purposes
- iGPU: Intel HD Graphics 530
- Display: 1920x1080, 60 Hz, IPS FlexView
- SSD: WDC SN720 512 GB NVMe
- HDD: WDC WD20SPZX 2 TB SATA 5400 RPM
- Wi-Fi: Intel Dual Band Wireless-AC 8260
- CPU temperature reading from the report: 41.05 C
- Battery: 38%, approximately 42 minutes at the time of measurement

## Engineering policy
Use conservative GPU memory budgets. Prefer small quantized models for inference. Never assume all 2 GB VRAM is free. Probe CUDA with a real kernel self-test before GPU training. Fall back to CPU in Auto mode if CUDA initialization or memory allocation fails.

## Known measurement limits
Some values in the report (SSD TBW, Intel VRAM type, exact battery cell count) require dedicated tools and must not be invented.
```

---

### `159/588` `backend/libraries/README.md`

- **المسار الكامل:** `F:\1f\p\ALI_Studio_Pro_Design4_4.6.0\04_Adaptive_Hybrid\backend/libraries/README.md`
- **الحجم:** 120 بايت (0.1 KB)
- **الامتداد:** `.md`

```markdown
# Libraries
Optional third-party dependencies or vendored helper libraries. Runtime does not silently install packages.
```

---

### `160/588` `backend/locales/ar.json`

- **المسار الكامل:** `F:\1f\p\ALI_Studio_Pro_Design4_4.6.0\04_Adaptive_Hybrid\backend/locales/ar.json`
- **الحجم:** 158 بايت (0.2 KB)
- **الامتداد:** `.json`

```json
{"name":"العربية","send":"إرسال","preview":"المعاينة","training":"التدريب","models":"النماذج","knowledge":"المعرفة"}
```

---

### `161/588` `backend/locales/en.json`

- **المسار الكامل:** `F:\1f\p\ALI_Studio_Pro_Design4_4.6.0\04_Adaptive_Hybrid\backend/locales/en.json`
- **الحجم:** 117 بايت (0.1 KB)
- **الامتداد:** `.json`

```json
{"name":"English","send":"Send","preview":"Preview","training":"Training","models":"Models","knowledge":"Knowledge"}
```

---

### `162/588` `backend/memory/__init__.py`

- **المسار الكامل:** `F:\1f\p\ALI_Studio_Pro_Design4_4.6.0\04_Adaptive_Hybrid\backend/memory/__init__.py`
- **الحجم:** 1 بايت (0.0 KB)
- **الامتداد:** `.py`

```python

```

---

### `163/588` `backend/memory/conversations.py`

- **المسار الكامل:** `F:\1f\p\ALI_Studio_Pro_Design4_4.6.0\04_Adaptive_Hybrid\backend/memory/conversations.py`
- **الحجم:** 5186 بايت (5.1 KB)
- **الامتداد:** `.py`

```python
# -*- coding: utf-8 -*-
"""Persistent conversation-learning memory with deterministic identity and fuzzy lookup.

This is deliberately separate from model weights: new conversations are remembered immediately,
while retraining is scheduled only when the deduplicated training ledger says it is needed.
"""
from __future__ import annotations
from pathlib import Path
import re, sqlite3, time, hashlib
from difflib import SequenceMatcher
from typing import Any

_ROLE_RE = re.compile(r"\s+", re.UNICODE)

def normalize_query(text: str) -> str:
    text = str(text or "").strip().lower()
    text = text.replace("\u0640", "")
    text = _ROLE_RE.sub(" ", text)
    return text

def identity(user: str, assistant: str) -> str:
    raw = normalize_query(user) + "\n" + str(assistant or "").strip()
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()

class ConversationMemory:
    def __init__(self, path: str | Path):
        self.path = Path(path); self.path.parent.mkdir(parents=True, exist_ok=True)
        c = sqlite3.connect(self.path)
        c.execute("""CREATE TABLE IF NOT EXISTS conversations(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_text TEXT NOT NULL,
            assistant_text TEXT NOT NULL,
            user_norm TEXT NOT NULL,
            pair_hash TEXT UNIQUE NOT NULL,
            source TEXT NOT NULL,
            model_version TEXT,
            quality REAL DEFAULT 0.5,
            created_at REAL NOT NULL,
            updated_at REAL NOT NULL
        )""")
        c.execute("CREATE INDEX IF NOT EXISTS idx_conv_norm ON conversations(user_norm)")
        c.execute("CREATE INDEX IF NOT EXISTS idx_conv_quality ON conversations(quality)")
        c.commit(); c.close()

    def put(self, user_text: str, assistant_text: str, source: str = "chat", model_version: str = "", quality: float = .5) -> dict[str, Any]:
        user_text, assistant_text = str(user_text).strip(), str(assistant_text).strip()
        if not user_text or not assistant_text:
            return {"stored": False, "reason": "empty"}
        h = identity(user_text, assistant_text); now = time.time()
        c = sqlite3.connect(self.path)
        c.execute("""INSERT INTO conversations(user_text,assistant_text,user_norm,pair_hash,source,model_version,quality,created_at,updated_at)
                     VALUES(?,?,?,?,?,?,?,?,?) ON CONFLICT(pair_hash) DO UPDATE SET updated_at=excluded.updated_at""",
                  (user_text, assistant_text, normalize_query(user_text), h, source, model_version, max(0,min(1,float(quality))), now, now))
        c.commit(); c.close()
        return {"stored": True, "hash": h}

    def _rows(self, limit: int = 2000):
        c = sqlite3.connect(self.path); c.row_factory = sqlite3.Row
        rows = c.execute("SELECT * FROM conversations ORDER BY quality DESC, updated_at DESC LIMIT ?", (limit,)).fetchall(); c.close()
        return [dict(r) for r in rows]

    def search(self, query: str, limit: int = 5, min_score: float = 0.0, min_quality: float = .6) -> list[dict[str, Any]]:
        q = normalize_query(query)
        if not q: return []
        q_words = set(q.split())
        out = []
        for r in self._rows():
            if float(r.get('quality',0.0)) < float(min_quality):
                continue
            cand = r["user_norm"]
            if cand == q:
                score = 1.0
            else:
                seq = SequenceMatcher(None, q, cand).ratio()
                cw = set(cand.split())
                overlap = len(q_words & cw) / max(1, len(q_words | cw))
                score = .70 * seq + .30 * overlap
            if score >= min_score:
                out.append((score, r))
        out.sort(key=lambda x: (x[0], x[1]["quality"]), reverse=True)
        for score, r in out[:limit]: r["score"] = round(float(score), 4)
        return [r for _, r in out[:limit]]

    def exact(self, query: str) -> dict[str, Any] | None:
        hits = self.search(query, 1, .999999, .6)
        return hits[0] if hits else None


    def feedback(self, user_text: str, assistant_text: str, accepted: bool, source: str = "user-feedback") -> dict[str, Any]:
        """Record explicit human feedback without allowing rejected replies into training search."""
        q=.95 if accepted else .1
        return self.put(user_text,assistant_text,source=source,model_version="human-reviewed",quality=q)

    def export_training(self, out: str | Path, min_quality: float = .6) -> dict[str, Any]:
        out = Path(out); out.parent.mkdir(parents=True, exist_ok=True)
        rows = [r for r in self._rows(100000) if float(r["quality"]) >= min_quality]
        written = 0
        with out.open("w", encoding="utf-8") as f:
            for r in rows:
                obj = {"id": r["pair_hash"], "messages": [
                    {"role": "user", "content": r["user_text"]},
                    {"role": "assistant", "content": r["assistant_text"]}
                ], "source": r["source"], "model_version": r["model_version"], "quality": r["quality"]}
                f.write(__import__("json").dumps(obj, ensure_ascii=False) + "\n"); written += 1
        return {"output": str(out), "samples": written}
```

---

### `164/588` `backend/memory/manager.py`

- **المسار الكامل:** `F:\1f\p\ALI_Studio_Pro_Design4_4.6.0\04_Adaptive_Hybrid\backend/memory/manager.py`
- **الحجم:** 2270 بايت (2.2 KB)
- **الامتداد:** `.py`

```python
# -*- coding: utf-8 -*-
"""Typed persistent memory with provenance."""
from __future__ import annotations
from pathlib import Path
import json, sqlite3
from typing import List, Dict, Any, Optional
from data_engine.normalization import normalized_hash

class MemoryManager:
    TYPES={'short_term','long_term','episodic','semantic','project','user'}
    def __init__(self, db_path: str|Path):
        self.path=Path(db_path); self.path.parent.mkdir(parents=True,exist_ok=True)
        c=sqlite3.connect(self.path); c.execute('''CREATE TABLE IF NOT EXISTS memories(id INTEGER PRIMARY KEY, type TEXT, key TEXT, content TEXT, source TEXT, confidence REAL DEFAULT 1.0, hash TEXT UNIQUE, created_at TEXT DEFAULT CURRENT_TIMESTAMP, updated_at TEXT DEFAULT CURRENT_TIMESTAMP)'''); c.execute('CREATE INDEX IF NOT EXISTS idx_memory_type ON memories(type)'); c.close()
    def put(self, type_:str, key:str, content:str, source:str='user', confidence:float=1.0)->int:
        if type_ not in self.TYPES: raise ValueError('invalid memory type')
        h=normalized_hash(f'{type_}\n{key}\n{content}')
        c=sqlite3.connect(self.path); c.execute('INSERT OR REPLACE INTO memories(type,key,content,source,confidence,hash,updated_at) VALUES(?,?,?,?,?,?,CURRENT_TIMESTAMP)',(type_,key,content,source,max(0,min(1,confidence)),h)); c.commit(); mid=c.execute('SELECT id FROM memories WHERE hash=?',(h,)).fetchone()[0]; c.close(); return mid
    def search(self, query:str, limit:int=10, type_:Optional[str]=None)->List[Dict[str,Any]]:
        c=sqlite3.connect(self.path); c.row_factory=sqlite3.Row
        args=[]; sql='SELECT * FROM memories';
        if type_: sql+=' WHERE type=?'; args.append(type_)
        sql+=' ORDER BY updated_at DESC LIMIT 500'
        rows=c.execute(sql,args).fetchall(); c.close(); q=query.lower(); scored=[]
        for r in rows:
            hay=(r['key']+' '+r['content']).lower(); score=sum(1 for word in q.split() if word in hay)/(len(q.split()) or 1); scored.append((score,r))
        scored.sort(key=lambda x:x[0],reverse=True); return [dict(r) for s,r in scored[:limit] if s>0 or not q]
    def delete(self, memory_id:int)->None:
        c=sqlite3.connect(self.path); c.execute('DELETE FROM memories WHERE id=?',(memory_id,)); c.commit(); c.close()
```

---

### `165/588` `backend/memory/sessions.py`

- **المسار الكامل:** `F:\1f\p\ALI_Studio_Pro_Design4_4.6.0\04_Adaptive_Hybrid\backend/memory/sessions.py`
- **الحجم:** 5705 بايت (5.6 KB)
- **الامتداد:** `.py`

```python
# -*- coding: utf-8 -*-
"""Persistent chat sessions: new conversations, history, rename and delete."""
from __future__ import annotations
from pathlib import Path
from typing import Any
import sqlite3, time, uuid, re


def _title(text: str) -> str:
    s = re.sub(r"\s+", " ", str(text or "").strip())
    return s[:54] + ("…" if len(s) > 54 else "") or "محادثة جديدة"


class ConversationSessionStore:
    def __init__(self, path: str | Path):
        self.path = Path(path); self.path.parent.mkdir(parents=True, exist_ok=True)
        with self._connect() as c:
            c.executescript("""
            CREATE TABLE IF NOT EXISTS sessions(
              id TEXT PRIMARY KEY,
              title TEXT NOT NULL,
              created_at REAL NOT NULL,
              updated_at REAL NOT NULL,
              model_version TEXT DEFAULT '',
              archived INTEGER NOT NULL DEFAULT 0
            );
            CREATE TABLE IF NOT EXISTS session_messages(
              id INTEGER PRIMARY KEY AUTOINCREMENT,
              session_id TEXT NOT NULL,
              seq INTEGER NOT NULL,
              role TEXT NOT NULL,
              content TEXT NOT NULL,
              created_at REAL NOT NULL,
              model_version TEXT DEFAULT '',
              meta_json TEXT DEFAULT '{}',
              UNIQUE(session_id, seq)
            );
            CREATE INDEX IF NOT EXISTS idx_session_updated ON sessions(updated_at DESC);
            CREATE INDEX IF NOT EXISTS idx_session_messages ON session_messages(session_id, seq);
            """)
            try:
                c.execute("ALTER TABLE session_messages ADD COLUMN meta_json TEXT DEFAULT '{}'")
            except sqlite3.OperationalError:
                pass


    def _connect(self):
        c = sqlite3.connect(self.path, timeout=30)
        c.row_factory = sqlite3.Row
        return c

    def create(self, title: str = "محادثة جديدة", model_version: str = "") -> dict[str, Any]:
        sid = f"chat-{uuid.uuid4().hex}"
        now = time.time()
        with self._connect() as c:
            c.execute("INSERT INTO sessions(id,title,created_at,updated_at,model_version) VALUES(?,?,?,?,?)", (sid, _title(title), now, now, model_version))
        return self.get(sid)

    def list(self, limit: int = 100) -> list[dict[str, Any]]:
        with self._connect() as c:
            rows = c.execute("SELECT * FROM sessions WHERE archived=0 ORDER BY updated_at DESC LIMIT ?", (max(1, min(500, int(limit))),)).fetchall()
        return [dict(r) for r in rows]

    def get(self, session_id: str) -> dict[str, Any] | None:
        with self._connect() as c:
            s = c.execute("SELECT * FROM sessions WHERE id=?", (str(session_id),)).fetchone()
            if not s: return None
            msgs = c.execute("SELECT id,session_id,seq,role,content,created_at,model_version,meta_json FROM session_messages WHERE session_id=? ORDER BY seq", (str(session_id),)).fetchall()
        out = dict(s); out['messages'] = [dict(m) for m in msgs]; return out

    def append(self, session_id: str, role: str, content: str, model_version: str = "", meta: dict[str, Any] | None = None) -> dict[str, Any]:
        sid = str(session_id); role = str(role).strip().lower(); content = str(content or '').strip()
        if role not in {'system','user','assistant','tool'}: raise ValueError('invalid role')
        if not content: raise ValueError('content is empty')
        now = time.time()
        with self._connect() as c:
            if not c.execute("SELECT 1 FROM sessions WHERE id=?", (sid,)).fetchone(): raise KeyError('conversation not found')
            seq = int(c.execute("SELECT COALESCE(MAX(seq),0)+1 FROM session_messages WHERE session_id=?", (sid,)).fetchone()[0])
            meta_json = __import__('json').dumps(meta or {}, ensure_ascii=False, sort_keys=True)
            c.execute("INSERT INTO session_messages(session_id,seq,role,content,created_at,model_version,meta_json) VALUES(?,?,?,?,?,?,?)", (sid,seq,role,content,now,model_version,meta_json))
            if role == 'user':
                existing = c.execute("SELECT title FROM sessions WHERE id=?", (sid,)).fetchone()
                title = _title(content) if existing and str(existing['title']) == 'محادثة جديدة' else None
                if title:
                    c.execute("UPDATE sessions SET title=?,updated_at=?,model_version=COALESCE(NULLIF(?,''),model_version) WHERE id=?", (title,now,model_version,sid))
                else:
                    c.execute("UPDATE sessions SET updated_at=?,model_version=COALESCE(NULLIF(?,''),model_version) WHERE id=?", (now,model_version,sid))
            else:
                c.execute("UPDATE sessions SET updated_at=?,model_version=COALESCE(NULLIF(?,''),model_version) WHERE id=?", (now,model_version,sid))
        return {'ok': True, 'session_id': sid, 'seq': seq}

    def rename(self, session_id: str, title: str) -> dict[str, Any] | None:
        with self._connect() as c:
            c.execute("UPDATE sessions SET title=?,updated_at=? WHERE id=?", (_title(title), time.time(), str(session_id)))
        return self.get(session_id)

    def delete(self, session_id: str) -> bool:
        with self._connect() as c:
            cur = c.execute("UPDATE sessions SET archived=1,updated_at=? WHERE id=?", (time.time(), str(session_id)))
            return cur.rowcount > 0

    def clear(self, session_id: str) -> None:
        with self._connect() as c:
            c.execute("DELETE FROM session_messages WHERE session_id=?", (str(session_id),))
            c.execute("UPDATE sessions SET title='محادثة جديدة',updated_at=? WHERE id=?", (time.time(), str(session_id)))
```

---

### `166/588` `backend/model/__init__.py`

- **المسار الكامل:** `F:\1f\p\ALI_Studio_Pro_Design4_4.6.0\04_Adaptive_Hybrid\backend/model/__init__.py`
- **الحجم:** 595 بايت (0.6 KB)
- **الامتداد:** `.py`

```python
# -*- coding: utf-8 -*-
"""ALI neural model package.

Heavy lifecycle modules are imported lazily to avoid package-level circular imports.
"""
from .ali_lm import AliConfig, ALIForCausalLM
from .importer import WeightReport, inspect_weights, import_compatible, load_into
from .registry import ModelRegistry
__all__=['AliConfig','ALIForCausalLM','WeightReport','inspect_weights','import_compatible','load_into','ModelRegistry','ModelManager']
def __getattr__(name):
    if name=='ModelManager':
        from .manager import ModelManager
        return ModelManager
    raise AttributeError(name)
```

---

### `167/588` `backend/model/ali_lm.py`

- **المسار الكامل:** `F:\1f\p\ALI_Studio_Pro_Design4_4.6.0\04_Adaptive_Hybrid\backend/model/ali_lm.py`
- **الحجم:** 12702 بايت (12.4 KB)
- **الامتداد:** `.py`

```python
# -*- coding: utf-8 -*-
"""ALI neural language model: a small Llama-compatible decoder trained from scratch.

The architecture intentionally mirrors the tensor naming/layout used by Llama-family
models so a trained ALI checkpoint can be exported to a HuggingFace-style folder and
converted with llama.cpp's official HF->GGUF converter. No base model is downloaded or
required: weights are initialized randomly and learned only from ALI's datasets.
"""
from __future__ import annotations
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Optional, Dict, Any, Iterator, Tuple
import json, math
import torch
from torch import nn
import torch.nn.functional as F

@dataclass
class AliConfig:
    vocab_size:int=4096
    hidden_size:int=256
    intermediate_size:int=1024
    num_hidden_layers:int=6
    num_attention_heads:int=8
    num_key_value_heads:int=8
    max_position_embeddings:int=512
    rms_norm_eps:float=1e-6
    rope_theta:float=10000.0
    attention_dropout:float=0.0
    bos_token_id:int=1
    eos_token_id:int=2
    pad_token_id:int=3
    model_type:str='llama'
    architectures:Tuple[str,...]=('LlamaForCausalLM',)
    hidden_act:str='silu'
    initializer_range:float=0.02
    use_cache:bool=True
    use_sdpa:bool=True
    tie_word_embeddings:bool=False
    torch_dtype:str='float32'
    def to_dict(self)->Dict[str,Any]:
        d=asdict(self); d['architectures']=list(self.architectures); return d
    @classmethod
    def from_dict(cls,d:Dict[str,Any]):
        d=dict(d); d['architectures']=tuple(d.get('architectures',('LlamaForCausalLM',))); return cls(**{k:v for k,v in d.items() if k in cls.__dataclass_fields__})
    @classmethod
    def auto_2gb(cls):
        return cls(vocab_size=4096,hidden_size=256,intermediate_size=1024,num_hidden_layers=6,num_attention_heads=8,num_key_value_heads=8,max_position_embeddings=512)

class RMSNorm(nn.Module):
    def __init__(self,dim,eps=1e-6): super().__init__(); self.weight=nn.Parameter(torch.ones(dim)); self.eps=eps
    def forward(self,x): return x*torch.rsqrt(x.pow(2).mean(-1,keepdim=True)+self.eps)*self.weight

def _rotate_half(x):
    half=x.size(-1)//2
    x1=x[...,:half]; x2=x[...,half:]
    return torch.cat((-x2,x1),dim=-1)

def _rope(x, cos, sin): return x*cos + _rotate_half(x)*sin

class RotaryEmbedding(nn.Module):
    def __init__(self,head_dim,max_pos,theta):
        super().__init__(); inv_freq=1.0/(theta**(torch.arange(0,head_dim,2).float()/head_dim)); self.register_buffer('inv_freq',inv_freq,persistent=False); self.max_pos=max_pos; self.cache={}
    def forward(self,seq_len:int,device,dtype):
        key=(seq_len,device.type,str(device),str(dtype))
        if key in self.cache: return self.cache[key]
        t=torch.arange(seq_len,device=device,dtype=self.inv_freq.dtype); freqs=torch.einsum('i,j->ij',t,self.inv_freq); emb=torch.cat((freqs,freqs),dim=-1); cos=emb.cos()[None,None,:,:].to(dtype); sin=emb.sin()[None,None,:,:].to(dtype); self.cache[key]=(cos,sin); return cos,sin

class ALIAttention(nn.Module):
    def __init__(self,c:AliConfig):
        super().__init__(); self.num_heads=c.num_attention_heads; self.num_kv_heads=c.num_key_value_heads; self.head_dim=c.hidden_size//c.num_attention_heads; self.scale=self.head_dim**-0.5
        self.q_proj=nn.Linear(c.hidden_size,c.hidden_size,bias=False); self.k_proj=nn.Linear(c.hidden_size,c.num_key_value_heads*self.head_dim,bias=False); self.v_proj=nn.Linear(c.hidden_size,c.num_key_value_heads*self.head_dim,bias=False); self.o_proj=nn.Linear(c.hidden_size,c.hidden_size,bias=False); self.rotary=RotaryEmbedding(self.head_dim,c.max_position_embeddings,c.rope_theta)
    def forward(self,x,attention_mask=None,past_key_value=None,use_cache=False, use_sdpa=True):
        b,t,_=x.shape; q=self.q_proj(x).view(b,t,self.num_heads,self.head_dim).transpose(1,2); k=self.k_proj(x).view(b,t,self.num_kv_heads,self.head_dim).transpose(1,2); v=self.v_proj(x).view(b,t,self.num_kv_heads,self.head_dim).transpose(1,2)
        past_len=0
        if past_key_value is not None: past_len=past_key_value[0].size(2)
        cos,sin=self.rotary(past_len+t,x.device,x.dtype); q=_rope(q,cos[:,:,past_len:past_len+t],sin[:,:,past_len:past_len+t]); k=_rope(k,cos[:,:,past_len:past_len+t],sin[:,:,past_len:past_len+t])
        if past_key_value is not None: k=torch.cat([past_key_value[0],k],2); v=torch.cat([past_key_value[1],v],2)
        if self.num_kv_heads != self.num_heads:
            rep=self.num_heads//self.num_kv_heads; k=k.repeat_interleave(rep,dim=1); v=v.repeat_interleave(rep,dim=1)
        kv_len=k.size(-2)
        if use_sdpa and past_key_value is None:
            if attention_mask is not None and attention_mask.dim()==2:
                am=(~attention_mask.bool()).to(dtype=q.dtype)*-1e4
                am=am[:,None,None,:].expand(b,1,t,kv_len)
                # causal diagonal is handled independently; padding is additive.
                base=torch.zeros((t,kv_len),device=x.device,dtype=q.dtype)
                causal=torch.triu(torch.full_like(base,float('-inf')),diagonal=1)
                attn_mask=causal[None,None,:,:]+am
                out=F.scaled_dot_product_attention(q,k,v,attn_mask=attn_mask,dropout_p=0.0)
            else:
                out=F.scaled_dot_product_attention(q,k,v,is_causal=True,dropout_p=0.0)
        else:
            scores=torch.matmul(q,k.transpose(-2,-1))*self.scale
            if attention_mask is None:
                allowed = torch.arange(kv_len,device=x.device)[None,:] <= (past_len + torch.arange(t,device=x.device))[:,None]
                scores=scores.masked_fill(~allowed[None,None,:,:],float('-inf'))
            else:
                scores=scores+attention_mask
            out=torch.softmax(scores.float(),-1).to(q.dtype)@v
        out=out.transpose(1,2).contiguous().view(b,t,-1); return self.o_proj(out),(k,v) if use_cache else None

class ALIMLP(nn.Module):
    def __init__(self,c):
        super().__init__(); self.gate_proj=nn.Linear(c.hidden_size,c.intermediate_size,bias=False); self.up_proj=nn.Linear(c.hidden_size,c.intermediate_size,bias=False); self.down_proj=nn.Linear(c.intermediate_size,c.hidden_size,bias=False)
    def forward(self,x): return self.down_proj(F.silu(self.gate_proj(x))*self.up_proj(x))

class ALILayer(nn.Module):
    def __init__(self,c):
        super().__init__(); self.input_layernorm=RMSNorm(c.hidden_size,c.rms_norm_eps); self.self_attn=ALIAttention(c); self.post_attention_layernorm=RMSNorm(c.hidden_size,c.rms_norm_eps); self.mlp=ALIMLP(c)
    def forward(self,x,attention_mask=None,past_key_value=None,use_cache=False,use_sdpa=True):
        h=x
        attn_out,kv=self.self_attn(self.input_layernorm(h),attention_mask=attention_mask,past_key_value=past_key_value,use_cache=use_cache,use_sdpa=use_sdpa)
        h=h+attn_out
        h=h+self.mlp(self.post_attention_layernorm(h))
        return h,kv

class ALIForCausalLM(nn.Module):
    def __init__(self,c:AliConfig):
        super().__init__(); self.config=c; self.embed_tokens=nn.Embedding(c.vocab_size,c.hidden_size,padding_idx=c.pad_token_id); self.layers=nn.ModuleList([ALILayer(c) for _ in range(c.num_hidden_layers)]); self.norm=RMSNorm(c.hidden_size,c.rms_norm_eps); self.lm_head=nn.Linear(c.hidden_size,c.vocab_size,bias=False); self.gradient_checkpointing=False
        self.apply(self._init_weights)
    def _init_weights(self,m):
        if isinstance(m,nn.Linear): nn.init.normal_(m.weight,0.0,0.02)
        elif isinstance(m,nn.Embedding): nn.init.normal_(m.weight,0.0,0.02)
        elif isinstance(m,RMSNorm): nn.init.ones_(m.weight)
    def forward(self,input_ids=None,labels=None,past_key_values=None,use_cache=False,attention_mask=None,inputs_embeds=None):
        h=self.embed_tokens(input_ids) if inputs_embeds is None else inputs_embeds; new=[]
        for i,layer in enumerate(self.layers):
            past=past_key_values[i] if past_key_values else None
            if self.training and self.gradient_checkpointing and past is None and not use_cache:
                from torch.utils.checkpoint import checkpoint
                h=checkpoint(lambda inp: layer(inp,attention_mask=attention_mask,use_cache=False,use_sdpa=self.config.use_sdpa)[0], h, use_reentrant=False)
                kv=None
            else:
                h,kv=layer(h,attention_mask=attention_mask,past_key_value=past,use_cache=use_cache,use_sdpa=self.config.use_sdpa)
            new.append(kv)
        logits=self.lm_head(self.norm(h))
        loss=None
        if labels is not None:
            shift_logits=logits[...,:-1,:].contiguous(); shift_labels=labels[...,1:].contiguous(); loss=F.cross_entropy(shift_logits.view(-1,shift_logits.size(-1)),shift_labels.view(-1),ignore_index=-100)
        return {'loss':loss,'logits':logits,'past_key_values':tuple(new) if use_cache else None}
    @torch.no_grad()
    def generate_stream(self,input_ids=None,max_new_tokens=128,temperature=0.7,top_k=40,eos_token_id:Optional[int]=2,inputs_embeds=None,bad_token_ids=None,stop_token_ids=None)->Iterator[int]:
        self.eval(); bad=set(int(x) for x in (bad_token_ids or [])); stops=set(int(x) for x in (stop_token_ids or []));
        if eos_token_id is not None: stops.add(int(eos_token_id))
        def pick(logits):
            logits=logits.clone()
            for bid in bad:
                if 0 <= bid < logits.size(-1): logits[...,bid]=float('-inf')
            if temperature<=0:
                return int(torch.argmax(logits,-1).item())
            l=logits/temperature
            if top_k and top_k < l.size(-1):
                val,idx=torch.topk(l,top_k,dim=-1); probs=torch.softmax(val,-1); choice=torch.multinomial(probs,1); return int(idx.gather(-1,choice).item())
            return int(torch.multinomial(torch.softmax(l,-1),1).item())
        if inputs_embeds is not None:
            out=self(inputs_embeds=inputs_embeds,use_cache=True); cache=out['past_key_values']; logits=out['logits'][:,-1,:]
            for _ in range(max_new_tokens):
                next_id=pick(logits)
                if next_id in stops: break
                yield next_id
                inp=torch.tensor([[next_id]],device=inputs_embeds.device,dtype=torch.long); out=self(inp,use_cache=True,past_key_values=cache); cache=out['past_key_values']; logits=out['logits'][:,-1,:]
            return
        out=self(input_ids,use_cache=True); cache=out['past_key_values']; logits=out['logits'][:,-1,:]
        for _ in range(max_new_tokens):
            next_id=pick(logits)
            if next_id in stops: break
            yield next_id
            inp=torch.tensor([[next_id]],device=input_ids.device,dtype=input_ids.dtype); out=self(inp,use_cache=True,past_key_values=cache); cache=out['past_key_values']; logits=out['logits'][:,-1,:]

def save_hf_checkpoint(model:ALIForCausalLM, tokenizer_dir:str|Path, out_dir:str|Path, metadata:Optional[Dict[str,Any]]=None)->Path:
    out=Path(out_dir); out.mkdir(parents=True,exist_ok=True)
    (out/'config.json').write_text(json.dumps(model.config.to_dict(),ensure_ascii=False,indent=2),encoding='utf-8')
    # Export with HuggingFace/Llama-compatible `model.` prefix. Internal ALI checkpoints remain unprefixed.
    state={('model.'+k if not k.startswith('lm_head.') else k):v.detach().cpu().contiguous() for k,v in model.state_dict().items()}
    try:
        from safetensors.torch import save_file
        save_file(state,str(out/'model.safetensors'),metadata={'format':'pt','source':'ALI Studio trained-from-scratch','architecture':'LlamaForCausalLM'})
    except Exception:
        torch.save(state,out/'pytorch_model.bin')
    tok=Path(tokenizer_dir)
    for name in ('tokenizer.model','tokenizer.json','tokenizer_config.json','special_tokens_map.json'):
        src=tok/name
        if src.exists(): (out/name).write_bytes(src.read_bytes())
    meta=dict(metadata or {}); meta.setdefault('parameter_count',sum(v.numel() for v in model.parameters())); meta.setdefault('source','ALI Studio trained-from-scratch'); meta.setdefault('architecture','LlamaForCausalLM')
    (out/'ali_metadata.json').write_text(json.dumps(meta,ensure_ascii=False,indent=2),encoding='utf-8')
    return out

def load_state(model:ALIForCausalLM,path:str|Path,device='cpu')->None:
    p=Path(path)
    if p.suffix=='.safetensors':
        from safetensors.torch import load_file; sd=load_file(str(p),device=str(device))
    else: sd=torch.load(p,map_location=device,weights_only=True)
    if any(k.startswith('model.') for k in sd):
        sd={k[6:] if k.startswith('model.') else k:v for k,v in sd.items()}
    missing,unexpected=model.load_state_dict(sd,strict=False)
    if missing: raise ValueError(f'Missing model tensors: {missing[:8]}')
```

---

### `168/588` `backend/model/artifacts.py`

- **المسار الكامل:** `F:\1f\p\ALI_Studio_Pro_Design4_4.6.0\04_Adaptive_Hybrid\backend/model/artifacts.py`
- **الحجم:** 4361 بايت (4.3 KB)
- **الامتداد:** `.py`

```python
# -*- coding: utf-8 -*-
"""Immutable artifact manifests and deterministic hashing for ALI AI 2.0.

The artifact layer is deliberately independent from model inference/training.
Every installed weight, adapter, tokenizer or GGUF file receives a manifest
containing hashes, lineage and provenance so a later machine can reproduce the
same promotion decision without rewriting the control plane.
"""
from __future__ import annotations

from dataclasses import dataclass, asdict, field
from pathlib import Path
from typing import Any, Iterable
import hashlib
import json
import os
import tempfile
import time


CHUNK = 1024 * 1024


def sha256_file(path: str | Path) -> str:
    p = Path(path)
    h = hashlib.sha256()
    with p.open("rb") as fh:
        while True:
            data = fh.read(CHUNK)
            if not data:
                break
            h.update(data)
    return h.hexdigest()


def sha256_path(path: str | Path) -> str:
    """Stable hash for a file or directory, including relative filenames."""
    p = Path(path).resolve()
    if p.is_file():
        return sha256_file(p)

    h = hashlib.sha256()
    for child in sorted(x for x in p.rglob("*") if x.is_file() and x.name != "manifest.json"):
        rel = child.relative_to(p).as_posix()
        h.update(rel.encode("utf-8"))
        h.update(b"\0")
        h.update(sha256_file(child).encode("ascii"))
        h.update(b"\0")
    return h.hexdigest()


def collect_files(root: str | Path) -> list[dict[str, Any]]:
    p = Path(root).resolve()
    files = [p] if p.is_file() else sorted(x for x in p.rglob("*") if x.is_file() and x.name != "manifest.json")
    result = []
    for child in files:
        rel = child.name if p.is_file() else child.relative_to(p).as_posix()
        result.append({
            "path": rel,
            "size": child.stat().st_size,
            "sha256": sha256_file(child),
        })
    return result


def atomic_json_write(path: str | Path, payload: Any) -> Path:
    """Write metadata atomically so a crash cannot leave a half manifest."""
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp_name = tempfile.mkstemp(prefix=target.name + ".", dir=str(target.parent))
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as fh:
            json.dump(payload, fh, ensure_ascii=False, indent=2, sort_keys=True)
            fh.write("\n")
            fh.flush()
            os.fsync(fh.fileno())
        os.replace(tmp_name, target)
    finally:
        try:
            os.unlink(tmp_name)
        except FileNotFoundError:
            pass
    return target


@dataclass
class ArtifactManifest:
    schema_version: int = 2
    artifact_id: str = ""
    artifact_type: str = ""  # base | adapter | merged | tokenizer | gguf | checkpoint
    name: str = ""
    version: str = ""
    created_at: float = field(default_factory=time.time)
    source: str = "local"
    path: str = ""
    sha256: str = ""
    files: list[dict[str, Any]] = field(default_factory=list)
    lineage: dict[str, Any] = field(default_factory=dict)
    training: dict[str, Any] = field(default_factory=dict)
    evaluation: dict[str, Any] = field(default_factory=dict)
    compatibility: dict[str, Any] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    def finalize(self, path: str | Path) -> "ArtifactManifest":
        p = Path(path).resolve()
        self.path = str(p)
        self.sha256 = sha256_path(p)
        self.files = collect_files(p)
        return self

    def write(self, path: str | Path | None = None) -> Path:
        target = Path(path) if path else Path(self.path) / "manifest.json"
        return atomic_json_write(target, self.to_dict())

    @classmethod
    def load(cls, path: str | Path) -> "ArtifactManifest":
        data = json.loads(Path(path).read_text(encoding="utf-8"))
        return cls(**data)

    def verify(self) -> dict[str, Any]:
        p = Path(self.path)
        if not p.exists():
            return {"valid": False, "reason": "artifact_missing", "path": str(p)}
        actual = sha256_path(p)
        return {
            "valid": actual == self.sha256,
            "expected": self.sha256,
            "actual": actual,
            "path": str(p),
        }
```

---

### `169/588` `backend/model/importer.py`

- **المسار الكامل:** `F:\1f\p\ALI_Studio_Pro_Design4_4.6.0\04_Adaptive_Hybrid\backend/model/importer.py`
- **الحجم:** 5706 بايت (5.6 KB)
- **الامتداد:** `.py`

```python
# -*- coding: utf-8 -*-
"""Inspect/import real ALI-compatible weight files.

This module deliberately refuses to pretend that an arbitrary checkpoint is an ALI
model. It validates tensor names/shapes before accepting a state dict. Compatible
state dicts can then be loaded into ALIForCausalLM and registered with provenance.
"""
from __future__ import annotations

from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Any, Dict, Mapping
import hashlib
import json
import shutil
import torch

from model.ali_lm import AliConfig, ALIForCausalLM, load_state

@dataclass
class WeightReport:
    path: str
    kind: str
    compatible: bool
    tensor_count: int = 0
    total_parameters: int = 0
    missing: list[str] | None = None
    unexpected: list[str] | None = None
    shape_mismatch: list[str] | None = None
    metadata: Dict[str, Any] | None = None
    error: str = ""

    def to_dict(self):
        return asdict(self)

def _load_state_dict(path: Path) -> tuple[Mapping[str, torch.Tensor], Dict[str, Any]]:
    if path.is_dir():
        for name in ("checkpoint.pt", "model.safetensors", "pytorch_model.bin"):
            candidate = path / name
            if candidate.exists():
                return _load_state_dict(candidate)
        raise FileNotFoundError(f"No supported checkpoint file in {path}")
    if path.suffix.lower() == ".safetensors":
        from safetensors.torch import load_file
        return load_file(str(path), device="cpu"), {}
    blob = torch.load(path, map_location="cpu", weights_only=False)
    if isinstance(blob, Mapping) and "model" in blob and isinstance(blob["model"], Mapping):
        return blob["model"], {k: blob.get(k) for k in ("global_step", "best_val", "train_config", "config")}
    if isinstance(blob, Mapping):
        return blob, {}
    raise ValueError("Unsupported checkpoint payload; expected a state dict")

def inspect_weights(path: str | Path, config: AliConfig | None = None) -> WeightReport:
    p = Path(path).resolve()
    kind = p.suffix.lower().lstrip(".") if p.is_file() else "checkpoint_dir"
    try:
        sd, meta = _load_state_dict(p)
        if config is not None:
            cfg = config
        else:
            embedded_cfg = meta.get("config") if isinstance(meta, dict) else None
            cfg = AliConfig.from_dict(embedded_cfg) if isinstance(embedded_cfg, dict) else AliConfig()
            cfg_file = (p / "config.json") if p.is_dir() else (p.parent / "config.json")
            if cfg_file.exists():
                try:
                    cfg = AliConfig.from_dict(json.loads(cfg_file.read_text(encoding="utf-8")))
                except Exception:
                    pass
        expected = ALIForCausalLM(cfg).state_dict()
        # Support HF-exported state dicts with model.* prefix.
        normalized: dict[str, torch.Tensor] = {}
        for k, v in sd.items():
            nk = k[6:] if k.startswith("model.") else k
            normalized[nk] = v
        missing = [k for k in expected if k not in normalized]
        unexpected = [k for k in normalized if k not in expected]
        shape_mismatch = [f"{k}: {tuple(normalized[k].shape)} != {tuple(expected[k].shape)}"
                          for k in expected if k in normalized and tuple(normalized[k].shape) != tuple(expected[k].shape)]
        total = sum(int(v.numel()) for v in normalized.values() if torch.is_tensor(v))
        compatible = not missing and not shape_mismatch
        return WeightReport(str(p), kind, compatible, len(normalized), total, missing[:40], unexpected[:40], shape_mismatch[:40], meta)
    except Exception as e:
        return WeightReport(str(p), kind, False, error=str(e))

def sha256(path: str | Path) -> str:
    p = Path(path)
    h = hashlib.sha256()
    if p.is_file():
        with p.open("rb") as f:
            for chunk in iter(lambda: f.read(1024 * 1024), b""):
                h.update(chunk)
    else:
        for f in sorted(x for x in p.rglob("*") if x.is_file()):
            h.update(str(f.relative_to(p)).encode("utf-8"))
            with f.open("rb") as fh:
                for chunk in iter(lambda: fh.read(1024 * 1024), b""):
                    h.update(chunk)
    return h.hexdigest()

def import_compatible(path: str | Path, destination: str | Path, config: AliConfig | None = None) -> Dict[str, Any]:
    """Copy a validated ALI checkpoint into the model registry area."""
    report = inspect_weights(path, config)
    if not report.compatible:
        raise ValueError("Weights are not compatible with the active ALI architecture: " + json.dumps(report.to_dict(), ensure_ascii=False))
    src = Path(path).resolve()
    dst = Path(destination).resolve()
    if src.is_dir():
        if dst.exists(): shutil.rmtree(dst)
        shutil.copytree(src, dst)
    else:
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)
    return {"report": report.to_dict(), "destination": str(dst), "sha256": sha256(src)}

def load_into(model: ALIForCausalLM, path: str | Path, device: str = "cpu") -> WeightReport:
    report = inspect_weights(path, model.config)
    if not report.compatible:
        raise ValueError("Incompatible weights")
    file_path = Path(path)
    if file_path.is_dir():
        for name in ("model.safetensors", "checkpoint.pt", "pytorch_model.bin"):
            if (file_path / name).exists():
                file_path = file_path / name
                break
    if file_path.name == "checkpoint.pt":
        blob = torch.load(file_path, map_location=device, weights_only=False)
        model.load_state_dict(blob["model"], strict=True)
    else:
        load_state(model, file_path, device)
    return report
```

---

### `170/588` `backend/model/manager.py`

- **المسار الكامل:** `F:\1f\p\ALI_Studio_Pro_Design4_4.6.0\04_Adaptive_Hybrid\backend/model/manager.py`
- **الحجم:** 5791 بايت (5.7 KB)
- **الامتداد:** `.py`

```python
# -*- coding: utf-8 -*-
"""ALI model lifecycle: discover, load, validate and activate model versions."""
from __future__ import annotations
from pathlib import Path
import json
from typing import Any

from model.registry import ModelRegistry
from model.ali_lm import AliConfig
from inference.engine import LocalInference
from runtime.device_policy import choose_policy
from runtime.hardware import detect, apply_cuda_memory_budget

class ModelManager:
    def __init__(self, root: str | Path, registry: ModelRegistry):
        self.root=Path(root); self.registry=registry; self.engine=None; self.current=None

    def _resolve_artifact_path(self, value: str | Path | None) -> Path | None:
        """Resolve portable/legacy absolute model paths against the current install root."""
        if not value:
            return None
        raw = Path(str(value))
        candidates = []
        if raw.is_absolute():
            candidates.append(raw)
            # Release databases from older copies may retain an absolute path from a
            # previous extraction directory. Re-anchor the path below this project
            # when the tail matches a known model layout. Handle both native separators
            # and Windows-style backslashes even when a release is inspected on Linux.
            parts = list(raw.parts)
            normalized_parts = [x for x in str(value).replace('\\', '/').split('/') if x]
            marker_i = None
            for marker in ('models', 'active', 'inbox', 'merged', 'runs'):
                if marker in parts:
                    marker_i = parts.index(marker); break
                if marker in normalized_parts:
                    marker_i = normalized_parts.index(marker); break
            if marker_i is not None:
                tail = parts[marker_i:] if marker in parts else normalized_parts[marker_i:]
                candidates.append(self.root / Path(*tail))
            candidates.append(self.root / raw.name)
        else:
            # A Windows path can be serialized into a registry and later parsed by a
            # non-Windows maintenance tool as a relative string containing backslashes.
            normalized_parts = [x for x in str(value).replace('\\', '/').split('/') if x]
            marker_i = None
            for marker in ('models', 'active', 'inbox', 'merged', 'runs'):
                if marker in normalized_parts:
                    marker_i = normalized_parts.index(marker); break
            if marker_i is not None:
                candidates.append(self.root / Path(*normalized_parts[marker_i:]))
            candidates.append(self.root / raw)
            candidates.append(self.root / 'models' / raw)
        for c in candidates:
            try:
                if c.exists():
                    return c.resolve()
            except Exception:
                continue