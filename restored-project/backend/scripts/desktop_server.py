# -*- coding: utf-8 -*-
"""ALI Studio Pro local desktop bridge.

All heavy work stays in the Python runtime; Electron/React is a control surface.
The server is localhost-only and exposes filesystem, model, memory, RAG, chat,
terminal-adjacent and continuous-learning operations required by the desktop UI.
"""
from __future__ import annotations

from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler
from pathlib import Path
import json
import os
import platform
import shutil
import subprocess
import sys
import threading
import time
import urllib.parse
import socket
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from core.runtime import ALIRuntime
from model.registry import ModelRegistry
from model.manager import ModelManager
from runtime.hardware import detect
from training.continuous_learning import ContinuousLearningManager
from memory.sessions import ConversationSessionStore
from inference.llama_engine import LlamaServerEngine

VERSION = "4.5.8"
PORT = int(os.environ.get("ALI_PORT", "8765"))
ENDPOINT_FILE = ROOT / "runtime_backend_endpoint.json"

def _free_port(start: int, stop: int = 8795) -> int:
    for candidate in range(max(1024, start), stop + 1):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            try:
                s.bind(("127.0.0.1", candidate))
                return candidate
            except OSError:
                continue
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("127.0.0.1", 0))
        return int(s.getsockname()[1])

SETTINGS_FILE = ROOT / "config" / "desktop_settings.json"

RUNTIME = ALIRuntime(ROOT, ROOT / "runtime_desktop.sqlite3", None, False)
REGISTRY = ModelRegistry(ROOT / "models" / "models.sqlite3")
MANAGER = ModelManager(ROOT, REGISTRY)
WORKSPACE = ROOT.resolve()
MODEL_LOADED = False
MODEL_ERROR = ""
LOADED_VERSION = ""
SELECTED_VERSION = ""
MODEL_LOCK = threading.RLock()
LEARNING = ContinuousLearningManager(ROOT, REGISTRY, on_promotion=lambda version: load_model_version(version))
SESSIONS = ConversationSessionStore(ROOT / "runtime_conversations.sqlite3")


def _load_settings() -> dict[str, Any]:
    if not SETTINGS_FILE.exists():
        return {"allow_internet": True}
    try:
        raw = json.loads(SETTINGS_FILE.read_text(encoding="utf-8"))
        return {"allow_internet": bool(raw.get("allow_internet", False))}
    except Exception:
        return {"allow_internet": False}


def _save_settings(settings: dict[str, Any]) -> dict[str, Any]:
    SETTINGS_FILE.parent.mkdir(parents=True, exist_ok=True)
    clean = {"allow_internet": bool(settings.get("allow_internet", False))}
    SETTINGS_FILE.write_text(json.dumps(clean, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return clean


RUNTIME.allow_internet = bool(_load_settings().get("allow_internet", True))

def _seed_local_knowledge() -> None:
    """Idempotently seed bundled project/device reference documents."""
    seed_dir = ROOT / "knowledge_seed"
    if not seed_dir.is_dir():
        return
    for p in sorted(seed_dir.glob("*.md")):
        try:
            raw = p.read_text(encoding="utf-8")
            chunks = [raw[i:i+1800] for i in range(0, len(raw), 1800) if raw[i:i+1800].strip()]
            priority = 120 if ('DETERMINISTIC_FAQ' in p.name or 'COMPLETE_USER_PROFILE' in p.name) else (100 if ('USER_PROFILE' in p.name or 'ARABIC_REFERENCE' in p.name) else 10)
            RUNTIME.knowledge.add_document(str(p.relative_to(ROOT)), p.name, "bundled-reference", {"source":"bundled","version":VERSION,"priority":priority}, chunks)
        except Exception:
            continue


def _seed_bundled_training_qa() -> None:
    """Seed bundled conversation Q/A into the deterministic training-QA index.

    This is deliberately separate from generic document chunks: training_qa_match
    needs explicit question/answer metadata so the included trained dataset is
    queryable immediately after a clean install, even when the runtime DB is empty.
    """
    fixture = ROOT / "data" / "training" / "testdata" / "ALI_User_Understanding_Bundle_V4.md"
    if not fixture.is_file():
        return
    try:
        samples, _safe, _warnings = LEARNING.parse_file(fixture)
        chunks = []
        chunk_meta = []
        for messages in samples:
            users = [m for m in messages if m.get("role") == "user"]
            assistants = [m for m in messages if m.get("role") == "assistant"]
            if not users or not assistants:
                continue
            question = str(users[-1].get("content", "")).strip()
            answer = str(assistants[-1].get("content", "")).strip()
            if not question or not answer:
                continue
            chunks.append(f"<|user|>\n{question}\n<|assistant|>\n{answer}")
            chunk_meta.append({
                "training_sample_id": LEARNING._sample_id(messages),
                "training_question": question,
                "training_answer": answer,
                "priority": 180,
            })
        if chunks:
            RUNTIME.knowledge.add_document(
                str(fixture.relative_to(ROOT)), fixture.name, "trained-bundle",
                {"source":"bundled-training", "version":VERSION, "priority":180, "unique_samples":len(chunks)},
                chunks, chunk_meta,
            )
    except Exception:
        # A knowledge-seed failure must never prevent the backend from starting.
        pass

_seed_local_knowledge()
_seed_bundled_training_qa()


def _gguf_model_info() -> dict[str, Any] | None:
    model_path = ROOT / "models" / "gguf" / "Qwen2.5-0.5B-Instruct-Q4_K_M.gguf"
    if not model_path.is_file():
        return None
    vendor = ROOT / "vendor" / "llama.cpp"
    exe_candidates = [
        vendor / "win-cuda" / "llama-server.exe",
        vendor / "win-cpu" / "llama-server.exe",
        vendor / "llama-server.exe",
    ]
    exe = next((x for x in exe_candidates if x.is_file()), None)
    if exe is None and vendor.is_dir():
        exe = next(iter(vendor.rglob("llama-server.exe")), None)
    if not exe:
        return {"version": "gguf:Qwen2.5-0.5B-Instruct-Q4_K_M", "name": "Qwen2.5-0.5B-Instruct-Q4_K_M", "artifact_type": "gguf", "status": "unavailable", "model": str(model_path), "reason": "llama-server.exe not installed"}
    return {"version": "gguf:Qwen2.5-0.5B-Instruct-Q4_K_M", "name": "Qwen2.5-0.5B-Instruct-Q4_K_M", "artifact_type": "gguf", "status": "external-ready", "model": str(model_path), "executable": str(exe)}


def load_model_version(version: str = "", compute_mode: str = "auto") -> bool:
    """Load a loadable model into the current runtime without changing registry state."""
    global MODEL_LOADED, MODEL_ERROR, LOADED_VERSION, SELECTED_VERSION
    with MODEL_LOCK:
        gguf = _gguf_model_info()
        if version.startswith("gguf:"):
            if not gguf or gguf.get("status") != "external-ready":
                MODEL_ERROR = str((gguf or {}).get("reason", "GGUF model not installed or llama-server missing"))
                MODEL_LOADED = False
                LOADED_VERSION = ""
                return False
            try:
                engine = LlamaServerEngine(gguf["executable"], gguf["model"], compute_mode=compute_mode, context=2048, model_version=gguf["version"])
                engine._ensure()
                RUNTIME.model_engine = engine
                MODEL_LOADED = True
                LOADED_VERSION = str(gguf["version"])
                SELECTED_VERSION = LOADED_VERSION
                MODEL_ERROR = ""
                return True
            except Exception as exc:
                MODEL_ERROR = str(exc)
                MODEL_LOADED = False
                LOADED_VERSION = ""
                return False
        target = REGISTRY.active("ALI") if not version else next((r for r in REGISTRY.list_loadable("ALI") if r.get("version") == version), None)
        target_version = str((target or {}).get("version", ""))
        if not target:
            MODEL_ERROR = f"Model not found or not loadable: {version or 'active'}"
            MODEL_LOADED = False
            LOADED_VERSION = ""
            return False
        if MODEL_LOADED and RUNTIME.model_engine is not None and LOADED_VERSION == target_version:
            SELECTED_VERSION = target_version if version else ""
            return True
        if MODEL_LOADED and RUNTIME.model_engine is not None and hasattr(RUNTIME.model_engine, "close"):
            try:
                RUNTIME.model_engine.close()
            except Exception:
                pass
        try:
            engine, _ = MANAGER.load(target, compute_mode=compute_mode)
            RUNTIME.model_engine = engine
            MODEL_LOADED = True
            LOADED_VERSION = target_version
            SELECTED_VERSION = target_version if version else ""
            MODEL_ERROR = ""
            return True
        except Exception as exc:
            MODEL_ERROR = str(exc)
            MODEL_LOADED = False
            LOADED_VERSION = ""
            return False


def load_active_model() -> bool:
    return load_model_version("")


def safe_path(value: str) -> Path:
    rel = str(value or "").replace("\\", "/").lstrip("/")
    p = (WORKSPACE / rel).resolve()
    if p == WORKSPACE or WORKSPACE in p.parents:
        return p
    raise ValueError("path escapes workspace")


def sample_hardware() -> dict[str, Any]:
    h = detect(probe_torch=True)
    out = h.to_dict()
    try:
        import psutil
        vm = psutil.virtual_memory()
        out.update({
            "ram_used_gb": round(vm.used / (1024**3), 2),
            "ram_percent": round(vm.percent, 1),
            "cpu_percent": round(psutil.cpu_percent(interval=0.03), 1),
        })
        disk = shutil.disk_usage(WORKSPACE)
        out.update({
            "disk_total_gb": round(disk.total / (1024**3), 1),
            "disk_used_gb": round((disk.total - disk.free) / (1024**3), 1),
            "disk_percent": round(((disk.total - disk.free) / disk.total) * 100, 1) if disk.total else 0,
        })
    except Exception:
        pass
    out["deviceName"] = out.get("device_name") or platform.node() or "Windows PC"
    out["osLabel"] = out.get("os_label") or out.get("os") or platform.platform()
    out["cpu_name"] = out.get("cpu_model") or platform.processor() or "CPU"
    out["gpu_percent"] = out.get("gpu_util_percent")
    out["gpu_temp"] = out.get("gpu_temp_c")
    out["cpu_temp"] = out.get("cpu_temp_c")
    out["battery_minutes"] = out.get("battery_minutes")
    out["screen"] = out.get("screen")
    out["internet_allowed"] = bool(RUNTIME.allow_internet)
    out["compute_policy"] = "auto-adaptive"
    return out


def send_json(handler: BaseHTTPRequestHandler, status: int, obj: dict[str, Any]) -> None:
    data = json.dumps(obj, ensure_ascii=False).encode("utf-8")
    handler.send_response(status)
    handler.send_header("Content-Type", "application/json; charset=utf-8")
    origin = handler.headers.get("Origin")
    if origin in {"http://127.0.0.1:5173", "http://localhost:5173", "file://", "null"}:
        handler.send_header("Access-Control-Allow-Origin", origin)
    handler.send_header("Vary", "Origin")
    handler.send_header("Access-Control-Allow-Headers", "Content-Type")
    handler.send_header("Access-Control-Allow-Methods", "GET,POST,OPTIONS")
    handler.send_header("Cache-Control", "no-store")
    handler.send_header("Content-Length", str(len(data)))
    handler.end_headers()
    handler.wfile.write(data)


def send_sse_headers(handler: BaseHTTPRequestHandler) -> None:
    handler.send_response(200)
    handler.send_header("Content-Type", "text/event-stream; charset=utf-8")
    origin = handler.headers.get("Origin")
    if origin in {"http://127.0.0.1:5173", "http://localhost:5173", "file://", "null"}:
        handler.send_header("Access-Control-Allow-Origin", origin)
    handler.send_header("Cache-Control", "no-cache, no-store, must-revalidate")
    handler.send_header("Connection", "close")
    handler.send_header("X-Accel-Buffering", "no")
    handler.end_headers()


def sse_write(handler: BaseHTTPRequestHandler, payload: dict[str, Any]) -> None:
    raw = json.dumps(payload, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
    handler.wfile.write(b"data: " + raw + b"\n\n")
    handler.wfile.flush()


def json_eval(value: Any) -> Any:
    try:
        return json.loads(value or "{}") if isinstance(value, str) else value
    except Exception:
        return {}


class Handler(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"

    def read_json(self) -> dict[str, Any]:
        size = int(self.headers.get("Content-Length", "0"))
        if size > 20 * 1024 * 1024:
            raise ValueError("request too large")
        raw = self.rfile.read(size)
        return json.loads(raw.decode("utf-8")) if raw else {}

    def do_OPTIONS(self):
        send_json(self, 204, {})

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        query = urllib.parse.parse_qs(parsed.query)
        try:
            if parsed.path == "/api/health":
                return send_json(self, 200, {"ok": True, "service": "ALI Studio Pro", "version": VERSION, "workspace": str(WORKSPACE)})
            if parsed.path == "/api/status":
                active = REGISTRY.active("ALI")
                return send_json(self, 200, {
                    "ok": True, "online": True, "version": VERSION, "workspace": str(WORKSPACE),
                    "modelLoaded": bool(RUNTIME.model_engine), "modelVersion": (active or {}).get("version", "No active model"),
                    "selectedVersion": SELECTED_VERSION, "modelError": MODEL_ERROR,
                    "loadedVersion": LOADED_VERSION, "computeMode": ("GPU" if sample_hardware().get("cuda_self_test") else "CPU"),
                    "mode": "محترف", "permission": RUNTIME.permission_manager.mode,
                    "hardware": sample_hardware(), "learning": LEARNING.status(), "modelReady": bool(RUNTIME.model_engine and LOADED_VERSION == (active or {}).get("version")), "settings": _load_settings(),
                })
            if parsed.path == "/api/hardware":
                return send_json(self, 200, {"ok": True, "hardware": sample_hardware()})
            if parsed.path == "/api/files":
                base = safe_path(query.get("path", [""])[0])
                if not base.is_dir(): raise ValueError("not a directory")
                entries = []
                for p in sorted(base.iterdir(), key=lambda x: (not x.is_dir(), x.name.lower())):
                    if p.name in {".git", "node_modules", ".venv", "__pycache__", ".pytest_cache"}: continue
                    stat = p.stat()
                    entries.append({"name": p.name, "path": str(p.relative_to(WORKSPACE)), "type": "directory" if p.is_dir() else "file", "size": stat.st_size if p.is_file() else None, "modified": stat.st_mtime})
                return send_json(self, 200, {"ok": True, "path": str(base.relative_to(WORKSPACE)) if base != WORKSPACE else "", "entries": entries})
            if parsed.path == "/api/file":
                p = safe_path(query.get("path", [""])[0])
                if not p.is_file(): raise ValueError("file not found")
                if p.stat().st_size > 4 * 1024 * 1024: raise ValueError("file too large for desktop editor")
                try: text = p.read_text(encoding="utf-8")
                except UnicodeDecodeError: raise ValueError("binary_or_non_utf8_file")
                return send_json(self, 200, {"ok": True, "path": str(p.relative_to(WORKSPACE)), "content": text, "size": p.stat().st_size, "modified": p.stat().st_mtime})
            if parsed.path == "/api/git":
                p = subprocess.run(["git", "-C", str(WORKSPACE), "status", "--short", "--branch"], capture_output=True, text=True, timeout=8)
                return send_json(self, 200, {"ok": p.returncode == 0, "output": p.stdout, "error": p.stderr, "branch": (p.stdout.splitlines()[0] if p.stdout else "")})
            if parsed.path == "/api/models":
                models = REGISTRY.list_loadable("ALI")
                gguf = _gguf_model_info()
                if gguf and gguf.get("status") == "external-ready":
                    models.append(gguf)
                return send_json(self, 200, {"ok": True, "models": models, "active": REGISTRY.active("ALI"), "selectedVersion": SELECTED_VERSION, "gguf": gguf})
            if parsed.path in {"/api/memory", "/api/memory/list"}:
                q = query.get("query", [""])[0]
                typ = query.get("type", [""])[0]
                memories = RUNTIME.memory.search(q, limit=80, type_=typ or None) if q or typ else RUNTIME.memory.search("", limit=80, type_=typ or None)
                conversations = RUNTIME.conversation_memory.search(q, limit=50, min_score=.0, min_quality=.0) if q else RUNTIME.conversation_memory._rows(50)
                return send_json(self, 200, {"ok": True, "memories": memories, "conversations": conversations})
            if parsed.path == "/api/search":
                q = query.get("q", [""])[0].strip()
                if not q: return send_json(self, 200, {"ok": True, "results": []})
                results = RUNTIME.knowledge.search(q, limit=12)
                return send_json(self, 200, {"ok": True, "results": results, "query": q})
            if parsed.path == "/api/conversations":
                return send_json(self, 200, {"ok": True, "conversations": SESSIONS.list(int(query.get("limit", [100])[0]))})
            if parsed.path == "/api/conversations/detail":
                sid = str(query.get("id", [""])[0]).strip()
                if not sid: raise ValueError("conversation id is required")
                row = SESSIONS.get(sid)
                if not row: return send_json(self, 404, {"ok": False, "error": "conversation not found"})
                return send_json(self, 200, {"ok": True, "conversation": row})
            if parsed.path in {"/api/training", "/api/training/status"}:
                return send_json(self, 200, {"ok": True, "status": LEARNING.status(), "pending": LEARNING.pending(), "versions": LEARNING.versions()})
            if parsed.path == "/api/training/versions":
                return send_json(self, 200, {"ok": True, "versions": LEARNING.versions()})
            if parsed.path == "/api/training/events":
                run_id = query.get("run_id", [""])[0]
                limit = max(1, min(500, int(query.get("limit", [100])[0])))
                with LEARNING._connect() as c:
                    if run_id:
                        rows = c.execute("SELECT * FROM events WHERE run_id=? ORDER BY id DESC LIMIT ?", (run_id, limit)).fetchall()
                    else:
                        rows = c.execute("SELECT * FROM events ORDER BY id DESC LIMIT ?", (limit,)).fetchall()
                return send_json(self, 200, {"ok": True, "events": [dict(r) for r in rows]})
            if parsed.path == "/api/settings":
                return send_json(self, 200, _load_settings())
            if parsed.path == "/api/doctor":
                return send_json(self, 200, {"ok": True, "checks": self._doctor()})
            if parsed.path == "/api/learning/errors":
                limit = max(1, min(500, int(query.get("limit", [100])[0])))
                return send_json(self, 200, {"ok": True, "stats": RUNTIME.error_learning.stats(), "incidents": RUNTIME.error_learning.pending(limit), "corrections": RUNTIME.error_learning.corrections("approved", limit)})
            if parsed.path == "/api/training/lineage":
                return send_json(self, 200, {"ok": True, "versions": LEARNING.versions(), "active": REGISTRY.active("ALI")})
            return send_json(self, 404, {"ok": False, "error": "not found"})
        except Exception as exc:
            return send_json(self, 500, {"ok": False, "error": str(exc)})

    def _doctor(self) -> list[dict[str, Any]]:
        active = REGISTRY.active("ALI")
        llama = ROOT / "vendor" / "llama.cpp"
        converter = next(iter(llama.rglob("convert_hf_to_gguf.py")), None) if llama.exists() else None
        quantizer = next((x for x in llama.rglob("llama-quantize*") if x.is_file()), None) if llama.exists() else None
        try:
            hw = detect(probe_torch=True, force=True)
            gpu_ok = bool(hw.cuda_self_test)
            gpu_detail = f"{hw.gpu_name} · VRAM {hw.gpu_mem_free_gb:.2f}/{hw.vram_gb:.2f} GB free · CUDA self-test={'PASS' if gpu_ok else 'FAIL'}"
        except Exception as exc:
            hw = None; gpu_ok = False; gpu_detail = str(exc)
        qwen = _gguf_model_info()
        checks = [
            ("Backend", True, f"Python {platform.python_version()}"),
            ("Adaptive GPU", True if gpu_ok else bool(hw and not hw.torch_cuda), gpu_detail),
            ("Workspace", WORKSPACE.is_dir(), str(WORKSPACE)),
            ("Model registry", (ROOT / "models" / "models.sqlite3").is_file(), "SQLite model registry"),
            ("Active model", bool(active), str((active or {}).get("version", "No active model"))),
            ("Active artifact", bool(active and (active.get("hf_dir") or active.get("checkpoint"))), str((active or {}).get("hf_dir") or (active or {}).get("checkpoint") or "—")),
            ("Knowledge DB", (ROOT / "runtime_knowledge.sqlite3").is_file(), "RAG store"),
            ("Memory DB", (ROOT / "runtime_memory.sqlite3").is_file(), "Memory store"),
            ("Learning DB", LEARNING.db_path.is_file(), "Continuous learning ledger"),
            ("GGUF converter", bool(converter), str(converter or "Not bundled; install llama.cpp converter in final Windows runtime")),
            ("GGUF quantizer", bool(quantizer), str(quantizer or "Not bundled; install llama.cpp quantizer in final Windows runtime")),
            ("Qwen GGUF", bool(qwen and qwen.get("status") == "external-ready"), str(qwen or "Qwen GGUF not downloaded yet; run SETUP_QWEN_LOCAL.bat")),
            ("Maxwell CUDA note", True, "Quadro M1000M is compute capability 5.0; GPU mode is enabled only after a real CUDA kernel self-test."),
        ]
        return [{"name": n, "ok": bool(ok), "detail": detail} for n, ok, detail in checks]

    def _stream_chat(self, body: dict[str, Any]) -> None:
        if not load_model_version(str(body.get("model_version") or SELECTED_VERSION or ""), str(body.get("compute_mode") or "auto")):
            send_sse_headers(self)
            sse_write(self, {"type":"error","text":MODEL_ERROR or "model_load_failed"})
            sse_write(self, {"type":"done"})
            return
        messages = body.get("messages") or []
        project = body.get("project_dir") or str(WORKSPACE)
        session_id = str(body.get("conversation_id") or "").strip()
        if not session_id:
            session = SESSIONS.create("محادثة جديدة", LOADED_VERSION)
            session_id = session["id"]
        send_sse_headers(self)
        final = None
        try:
            if messages and messages[-1].get("role") == "user":
                try: SESSIONS.append(session_id, "user", str(messages[-1].get("content") or ""), LOADED_VERSION)
                except Exception: pass
            for event in RUNTIME.stream_answer(messages, project):
                if event.get("type") == "final": final = event
                sse_write(self, event)
            if final and final.get("text"):
                try:
                    meta = {k: final.get(k) for k in ("mode", "confidence", "sources", "web", "steps", "tool") if k in final}
                    SESSIONS.append(session_id, "assistant", str(final.get("text")), LOADED_VERSION, meta=meta)
                except Exception: pass
            sse_write(self, {"type": "session", "conversation_id": session_id})
            sse_write(self, {"type": "done"})
        except BrokenPipeError:
            return
        except Exception as exc:
            try: sse_write(self, {"type": "error", "text": str(exc)})
            except Exception: pass

    def do_POST(self):
        global WORKSPACE, RUNTIME
        try:
            body = self.read_json()
        except Exception:
            return send_json(self, 400, {"ok": False, "error": "invalid json"})
        try:
            if self.path == "/api/workspace":
                p = Path(str(body.get("path", ""))).expanduser().resolve()
                if not p.is_dir(): raise ValueError("workspace directory not found")
                WORKSPACE = p
                return send_json(self, 200, {"ok": True, "workspace": str(WORKSPACE)})
            if self.path == "/api/chat/stream":
                return self._stream_chat(body)
            if self.path == "/api/chat":
                version = str(body.get("model_version") or SELECTED_VERSION or "")
                if not load_model_version(version, str(body.get("compute_mode") or "auto")):
                    raise RuntimeError(MODEL_ERROR or "model_load_failed")
                messages = body.get("messages") or []
                project = body.get("project_dir") or str(WORKSPACE)
                sid = str(body.get("conversation_id") or "").strip()
                if not sid: sid = SESSIONS.create("محادثة جديدة", LOADED_VERSION)["id"]
                if messages and messages[-1].get("role") == "user":
                    try: SESSIONS.append(sid, "user", str(messages[-1].get("content") or ""), LOADED_VERSION)
                    except Exception: pass
                result = RUNTIME.answer(messages, project)
                if result.get("text"):
                    try:
                        meta = {k: result.get(k) for k in ("mode", "confidence", "sources", "web", "steps", "tool") if k in result}
                        SESSIONS.append(sid, "assistant", str(result.get("text")), LOADED_VERSION, meta=meta)
                    except Exception: pass
                return send_json(self, 200, {"ok": True, "modelVersion": LOADED_VERSION, "conversation_id": sid, **result})
            if self.path == "/api/chat/feedback":
                user_text = str(body.get("user_text") or "")
                assistant_text = str(body.get("assistant_text") or "")
                accepted = bool(body.get("accepted"))
                result = RUNTIME.conversation_memory.feedback(user_text, assistant_text, accepted)
                return send_json(self, 200, {"ok": True, **result})
            if self.path == "/api/learning/correct":
                result = RUNTIME.error_learning.add_correction(
                    str(body.get("user_text") or ""),
                    str(body.get("bad_output") or ""),
                    str(body.get("corrected_output") or ""),
                    component=str(body.get("component") or "chat"),
                    reason=str(body.get("reason") or "user_correction"),
                    source=str(body.get("source") or "user"),
                )
                return send_json(self, 200, result)
            if self.path == "/api/models/select":
                version = str(body.get("version") or "").strip()
                compute_mode = str(body.get("compute_mode") or "auto")
                ok = load_model_version("", compute_mode) if not version or version == "Auto (Active)" else load_model_version(version, compute_mode)
                if not ok: raise ValueError(MODEL_ERROR or "model_load_failed")
                return send_json(self, 200, {"ok": True, "version": LOADED_VERSION})
            if self.path == "/api/models/promote":
                version = str(body.get("version") or "").strip()
                if not version: raise ValueError("version is required")
                row = next((r for r in REGISTRY.list("ALI") if r.get("version") == version), None)
                if not row: raise ValueError("version not found")
                evaluation = json_eval(row.get("eval_json"))
                gate = evaluation.get("gate", {}) if isinstance(evaluation, dict) else {}
                if row.get("status") != "candidate" or gate and gate.get("promote") is False: raise ValueError("candidate is not eligible for promotion")
                REGISTRY.promote("ALI", version)
                load_model_version(version)
                return send_json(self, 200, {"ok": True, "version": version})
            if self.path == "/api/conversations":
                row = SESSIONS.create(str(body.get("title") or "محادثة جديدة"), LOADED_VERSION)
                return send_json(self, 200, {"ok": True, "conversation": row})
            if self.path == "/api/conversations/rename":
                row = SESSIONS.rename(str(body.get("id") or ""), str(body.get("title") or "محادثة جديدة"))
                if not row: raise ValueError("conversation not found")
                return send_json(self, 200, {"ok": True, "conversation": row})
            if self.path == "/api/conversations/delete":
                ok = SESSIONS.delete(str(body.get("id") or ""))
                return send_json(self, 200, {"ok": ok})
            if self.path == "/api/conversations/clear":
                SESSIONS.clear(str(body.get("id") or ""))
                return send_json(self, 200, {"ok": True})
            if self.path == "/api/memory":
                typ = str(body.get("type") or "user")
                result = RUNTIME.memory.put(typ, str(body.get("key") or ""), str(body.get("content") or ""), str(body.get("source") or "user"), float(body.get("confidence", .9)))
                return send_json(self, 200, {"ok": True, "id": result})
            if self.path == "/api/memory/delete":
                RUNTIME.memory.delete(int(body.get("id")))
                return send_json(self, 200, {"ok": True})
            if self.path == "/api/training/ingest":
                paths = body.get("paths") or []
                if not isinstance(paths, list): raise ValueError("paths must be a list")
                result = LEARNING.import_files([str(x) for x in paths])
                return send_json(self, 200, {"ok": True, "results": result, "status": LEARNING.status()})
            if self.path == "/api/training/start":
                return send_json(self, 200, LEARNING.start(promote=bool(body.get("promote", True)), compute_mode=str(body.get("compute_mode") or "auto")))
            if self.path == "/api/training/cancel":
                return send_json(self, 200, LEARNING.cancel())
            if self.path == "/api/web/search":
                if not RUNTIME.allow_internet: raise PermissionError("البحث الخارجي متوقف من الإعدادات")
                from research.web import search
                q = str(body.get("query") or "").strip()
                return send_json(self, 200, {"ok": True, "results": [x.to_dict() for x in search(q, limit=8)]})
            if self.path == "/api/settings":
                settings = _save_settings({**_load_settings(), **body})
                RUNTIME.allow_internet = bool(settings.get("allow_internet"))
                return send_json(self, 200, {"ok": True, **settings})
            if self.path == "/api/file":
                p = safe_path(body.get("path", ""))
                content = str(body.get("content", ""))
                if p.exists() and not p.is_file(): raise ValueError("target is not a file")
                if len(content.encode("utf-8")) > 8 * 1024 * 1024: raise ValueError("file too large")
                p.parent.mkdir(parents=True, exist_ok=True)
                tmp = p.with_suffix(p.suffix + ".ali-tmp")
                tmp.write_text(content, encoding="utf-8")
                os.replace(tmp, p)
                return send_json(self, 200, {"ok": True, "path": str(p.relative_to(WORKSPACE)), "size": len(content.encode("utf-8"))})
            if self.path == "/api/file/delete":
                p = safe_path(body.get("path", ""))
                if p == WORKSPACE: raise ValueError("cannot delete workspace root")
                if not p.exists(): raise ValueError("file not found")
                if p.is_dir(): raise ValueError("directory deletion is disabled from the desktop editor")
                p.unlink()
                return send_json(self, 200, {"ok": True})
            return send_json(self, 404, {"ok": False, "error": "not found"})
        except Exception as exc:
            return send_json(self, 500, {"ok": False, "error": str(exc)})

    def log_message(self, *_args):
        return None


if __name__ == "__main__":
    requested_port = PORT
    # Catch every socket-bind failure (errno 98/48/10048 = "address in use",
    # WinError 10013 = "access forbidden" when another listener holds the port,
    # PermissionError on Windows for some firewalls). All mean: try the next port.
    try:
        server = ThreadingHTTPServer(("127.0.0.1", requested_port), Handler)
    except (OSError, PermissionError) as exc:
        errno = getattr(exc, "errno", None)
        winerr = getattr(exc, "winerror", None)
        if errno in {98, 48, 10048} or winerr in {10013, 10048}:
            PORT = _free_port(requested_port + 1)
            server = ThreadingHTTPServer(("127.0.0.1", PORT), Handler)
        else:
            raise
    try:
        # The endpoint file is a readiness contract for Electron. Write it only after
        # the model bootstrap probe has completed, so merely seeing the file never
        # means "port is alive" while the process is still loading.
        ENDPOINT_FILE.unlink(missing_ok=True)
    except Exception:
        pass
    print(f"ALI Studio Pro backend starting on 127.0.0.1:{PORT} · v{VERSION}", flush=True)
    load_active_model()
    try:
        ENDPOINT_FILE.write_text(json.dumps({"host":"127.0.0.1","port":PORT,"url":f"http://127.0.0.1:{PORT}","pid":os.getpid(),"ready":True}, ensure_ascii=False, indent=2), encoding="utf-8")
    except Exception:
        pass
    try:
        server.serve_forever()
    finally:
        try: ENDPOINT_FILE.unlink(missing_ok=True)
        except Exception: pass
