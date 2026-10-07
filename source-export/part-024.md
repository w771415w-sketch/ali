# Intent Classification
# ============================================================================

# كلمات مفتاحية لكل intent — deterministic, no model required
_INTENT_PATTERNS: Dict[str, List[str]] = {
    "git": [
        "git ", "/git ", "git_", "git_", "commit", "status", "diff",
        "push", "pull", "branch", "merge", "log", "checkout",
    ],
    "read_file": [
        "read ", "/read ", "read_file", "افتح", "اقرأ", "اعرض",
        "show me", "cat ", "view ", "open file",
    ],
    "write_file": [
        "write ", "/write ", "write_file", "اكتب", "أنشئ ملف",
        "create file", "make file", "edit ", "modify file",
    ],
    "list_dir": [
        "list ", "/list ", "list_dir", "ls ", "اعرض المجلد",
        "show folder", "show files", "list directory",
    ],
    "search_files": [
        "search ", "/search ", "search_files", "find ", "ابحث",
        "grep", "regex", "pattern",
    ],
    "run_command": [
        "run ", "/run ", "run_command", "execute", "shell",
        "terminal", "cmd", "powershell", "bash",
    ],
    "code_question": [
        "?", "؟", "كيف", "لماذا", "explain", "what is",
        "what does", "how does", "why", "when", "where",
    ],
    "analyze_project": [
        "analyze", "structure", "overview", "summary",
        "ما هي", "بنية المشروع", "ملخص",
    ],
}

# Token counter cache (loaded lazily)
_token_counter = None


def _get_token_counter():
    """Lazy-load tokenizer for token counting. Returns None if unavailable."""
    global _token_counter
    if _token_counter is None:
        try:
            from tokenizer import load_tokenizer
            from config.paths import APP_PATHS
            tok_path = APP_PATHS.project_root() / "weights" / "tokenizer"
            if tok_path.exists():
                _token_counter = load_tokenizer(tok_path)
            else:
                _token_counter = False  # not available
        except Exception:
            _token_counter = False
    return _token_counter if _token_counter else None


def count_tokens(text: str) -> int:
    """عدّاد tokens باستخدام ALI Tokenizer إذا متاح."""
    if not text:
        return 0
    tok = _get_token_counter()
    if tok:
        try:
            return len(tok.encode(text))
        except Exception:
            pass
    # Fallback: تقدير تقريبي (1 token ≈ 4 chars for Arabic/English mix)
    return max(1, len(text) // 4)


@dataclass
class Intent:
    """نية مستخرجة من رسالة المستخدم."""
    primary: str
    confidence: float
    params: Dict[str, Any] = field(default_factory=dict)


def classify_intent(text: str) -> Intent:
    """يصنف النص إلى intent بناءً على كلمات مفتاحية.

    Returns: Intent(primary="read_file", confidence=0.9, params={...})
    """
    if not text or not text.strip():
        return Intent(primary="unknown", confidence=0.0)

    t = text.strip().lower()
    scores: Dict[str, float] = {}

    for intent, patterns in _INTENT_PATTERNS.items():
        score = 0.0
        for pat in patterns:
            if pat in t:
                # Longer match = higher score
                score += len(pat) / 10.0
                # Exact start match = bonus
                if t.startswith(pat):
                    score += 0.5
        if score > 0:
            scores[intent] = score

    if not scores:
        # No strong match — try to detect by content shape
        if re.search(r"[A-Za-z_]+\.\w+", t):
            return Intent(primary="read_file", confidence=0.4,
                          params={"hint": "mentioned filename"})
        if "?" in t or "؟" in t:
            return Intent(primary="code_question", confidence=0.5)
        if len(t.split()) <= 3 and t.replace(" ", "").isalpha():
            return Intent(primary="search_files", confidence=0.3,
                          params={"term": t.strip()})
        return Intent(primary="general", confidence=0.0)

    # Pick best
    primary = max(scores, key=scores.get)  # type: ignore
    total = sum(scores.values())
    confidence = scores[primary] / total if total > 0 else 0.0

    # Extract params based on intent
    params = _extract_params(text, primary)

    return Intent(primary=primary, confidence=confidence, params=params)


def _extract_params(text: str, intent: str) -> Dict[str, Any]:
    """يستخرج parameters من النص حسب الـ intent."""
    t = text.strip()
    params: Dict[str, Any] = {}

    if intent == "read_file":
        # Try to extract path
        m = re.search(r"(?:read(?:_file)?\s+|/read\s+|افتح\s+|اقرأ\s+)(.+)", t, re.I)
        if m:
            params["path"] = m.group(1).strip()

    elif intent == "write_file":
        m = re.search(r"(?:write(?:_file)?\s+|/write\s+|اكتب\s+)(.+?)(?:\s+(?:بمحتوى|with|بـ|:)\s+(.+))?$",
                       t, re.I)
        if m:
            params["path"] = m.group(1).strip()
            if m.group(2):
                params["content"] = m.group(2).strip()

    elif intent == "list_dir":
        m = re.search(r"(?:list(?:_dir)?\s+|/list\s+|ls\s+)?(.+)?", t, re.I)
        if m and m.group(1):
            params["path"] = m.group(1).strip()

    elif intent == "search_files":
        m = re.search(r"(?:search(?:_files)?\s+|/search\s+|find\s+|ابحث\s+(?:عن)?\s*)(.+)", t, re.I)
        if m:
            params["pattern"] = m.group(1).strip()

    elif intent == "run_command":
        m = re.search(r"(?:run(?:_command)?\s+|/run\s+)(.+)", t, re.I)
        if m:
            params["command"] = m.group(1).strip()

    elif intent == "git":
        parts = t.split(None, 2)
        if len(parts) >= 2:
            params["subcommand"] = parts[1]
            if len(parts) >= 3:
                params["args"] = parts[2]

    return params


# ============================================================================
# Plan: sequence of tool calls
# ============================================================================

@dataclass
class ToolCall:
    """استدعاء أداة مقرر في الخطة."""
    tool_name: str
    kwargs: Dict[str, Any]
    reason: str = ""


@dataclass
class Plan:
    """خطة agent: sequence من ToolCalls."""
    intent: Intent
    steps: List[ToolCall]
    fallback_message: str = ""

    def is_empty(self) -> bool:
        return len(self.steps) == 0


def plan_actions(intent: Intent) -> Plan:
    """يبني خطة بناءً على الـ intent."""
    steps: List[ToolCall] = []

    if intent.primary == "read_file":
        path = intent.params.get("path", "")
        if path:
            steps.append(ToolCall(
                tool_name="read_file",
                kwargs={"path": path},
                reason=f"قراءة الملف المطلوب: {path}",
            ))

    elif intent.primary == "write_file":
        path = intent.params.get("path", "")
        content = intent.params.get("content", "")
        if path:
            steps.append(ToolCall(
                tool_name="write_file",
                kwargs={"path": path, "content": content},
                reason=f"كتابة الملف: {path}",
            ))

    elif intent.primary == "list_dir":
        path = intent.params.get("path", "")
        steps.append(ToolCall(
            tool_name="list_dir",
            kwargs={"path": path} if path else {},
            reason=f"سرد محتويات المجلد: {path or 'الحالي'}",
        ))

    elif intent.primary == "search_files":
        pattern = intent.params.get("pattern", "")
        if pattern:
            steps.append(ToolCall(
                tool_name="search_files",
                kwargs={"pattern": pattern},
                reason=f"البحث عن: {pattern}",
            ))

    elif intent.primary == "run_command":
        cmd = intent.params.get("command", "")
        if cmd:
            steps.append(ToolCall(
                tool_name="run_command",
                kwargs={"command": cmd},
                reason=f"تنفيذ الأمر: {cmd}",
            ))

    elif intent.primary == "git":
        sub = intent.params.get("subcommand", "status")
        args = intent.params.get("args", "")
        if sub in ("status", "diff"):
            steps.append(ToolCall(
                tool_name=f"git_{sub}",
                kwargs={},
                reason=f"git {sub}",
            ))
        elif sub == "commit":
            steps.append(ToolCall(
                tool_name="git_commit",
                kwargs={"message": args or "update", "add_all": True},
                reason=f"git commit: {args or 'update'}",
            ))
        else:
            steps.append(ToolCall(
                tool_name="git_status",
                kwargs={},
                reason=f"git {sub} (default to status)",
            ))

    elif intent.primary == "analyze_project":
        # Plan: list_dir + search_files for overview
        steps.append(ToolCall(
            tool_name="list_dir",
            kwargs={},
            reason="سرد بنية المشروع",
        ))
        steps.append(ToolCall(
            tool_name="search_files",
            kwargs={"pattern": "\\.py$"},
            reason="البحث عن ملفات Python",
        ))

    elif intent.primary == "code_question":
        # No tools needed — answer from knowledge
        pass

    return Plan(intent=intent, steps=steps)


# ============================================================================
# Execute Plan
# ============================================================================

@dataclass
class ExecutionResult:
    """نتيجة تنفيذ الخطة."""
    plan: Plan
    tool_results: List[Dict[str, Any]]
    summary: str
    tokens_used: int
    duration_ms: float

    @property
    def ok(self) -> bool:
        return all(r.get("ok", False) for r in self.tool_results) if self.tool_results else True


def execute_plan(plan: Plan,
                 tool_runner,
                 user_text: str) -> ExecutionResult:
    """ينفذ الخطة باستخدام tool_runner.

    tool_runner: callable(tool_name, kwargs) -> result dict
    """
    if plan.is_empty():
        # No tools needed — return knowledge-based answer
        return ExecutionResult(
            plan=plan,
            tool_results=[],
            summary=_knowledge_answer(plan.intent, user_text),
            tokens_used=count_tokens(user_text),
            duration_ms=0.0,
        )

    t0 = time.time()
    tool_results: List[Dict[str, Any]] = []

    for step in plan.steps:
        try:
            result = tool_runner(step.tool_name, step.kwargs)
            tool_results.append({
                "tool": step.tool_name,
                "kwargs": step.kwargs,
                "ok": result.get("ok", False),
                "data": result.get("data", ""),
                "error": result.get("error", ""),
                "reason": step.reason,
            })
        except Exception as e:
            tool_results.append({
                "tool": step.tool_name,
                "kwargs": step.kwargs,
                "ok": False,
                "data": "",
                "error": str(e),
                "reason": step.reason,
            })

    duration = (time.time() - t0) * 1000.0

    # Build summary
    summary = _build_summary(plan, tool_results)

    # Token count
    tokens = count_tokens(user_text) + count_tokens(summary)

    return ExecutionResult(
        plan=plan,
        tool_results=tool_results,
        summary=summary,
        tokens_used=tokens,
        duration_ms=duration,
    )


def _build_summary(plan: Plan, results: List[Dict[str, Any]]) -> str:
    """يبني ملخص نهائي للرد."""
    if not results:
        return "✅ تم."

    lines = []
    all_ok = all(r.get("ok", False) for r in results)
    lines.append(f"{'✅' if all_ok else '⚠'} تنفيذ {len(results)} خطوة(s):")

    for i, r in enumerate(results, 1):
        tool = r.get("tool", "?")
        reason = r.get("reason", "")
        ok = r.get("ok", False)
        status = "✅" if ok else "❌"

        lines.append(f"\n{status} خطوة {i}: {tool}")
        if reason:
            lines.append(f"   السبب: {reason}")

        if ok:
            data = r.get("data", "")
            if isinstance(data, str):
                # Truncate for display
                preview = data[:200]
                if len(data) > 200:
                    preview += f"... ({len(data)} حرف)"
                lines.append(f"   النتيجة: {preview}")
        else:
            err = r.get("error", "unknown error")
            lines.append(f"   الخطأ: {err[:200]}")

    return "\n".join(lines)


def _knowledge_answer(intent: Intent, text: str) -> str:
    """إجابات قائمة على المعرفة للأسئلة العامة."""
    if intent.primary == "code_question" or intent.primary == "general":
        return (
            "🤖 أنا ALI Studio Agent (الوضع المحلي).\n\n"
            "الأسئلة العامة يمكنني تقديم إرشادات عنها، لكن لا يوجد نموذج لغوي مثبت حالياً.\n\n"
            "ما أستطيع فعله فعلياً:\n"
            "  • قراءة الملفات وسرد المجلدات\n"
            "  • تشغيل أوامر shell (إذا سمحت الصلاحيات)\n"
            "  • عمليات Git (status, diff, commit)\n"
            "  • البحث في الملفات بـ regex\n\n"
            "جرّب مثلاً:\n"
            "  • list_dir\n"
            "  • read_file ali_agent.py\n"
            "  • search_files class.*Agent\n"
            "  • git status\n\n"
            f"سؤالك: \"{text}\""
        )
    return "لا أدوات متاحة لهذا الطلب."
```

---

### `56/588` `backend/core/audit.py`

- **المسار الكامل:** `F:\1f\p\ALI_Studio_Pro_Design4_4.6.0\04_Adaptive_Hybrid\backend/core/audit.py`
- **الحجم:** 877 بايت (0.9 KB)
- **الامتداد:** `.py`

```python
# -*- coding: utf-8 -*-
"""Append-only local audit log in SQLite."""
from __future__ import annotations
from pathlib import Path
import sqlite3, json, time

class AuditLog:
    def __init__(self, db_path: str | Path):
        self.path=Path(db_path); self.path.parent.mkdir(parents=True,exist_ok=True)
        c=sqlite3.connect(self.path); c.execute("CREATE TABLE IF NOT EXISTS audit(id INTEGER PRIMARY KEY, ts REAL, event TEXT NOT NULL)"); c.commit(); c.close()
    def write(self,event:dict):
        c=sqlite3.connect(self.path); c.execute("INSERT INTO audit(ts,event) VALUES(?,?)",(time.time(),json.dumps(event,ensure_ascii=False))); c.commit(); c.close()
    def recent(self,limit=200):
        c=sqlite3.connect(self.path); c.row_factory=sqlite3.Row; r=[dict(x) for x in c.execute("SELECT * FROM audit ORDER BY id DESC LIMIT ?",(limit,)).fetchall()]; c.close(); return r
```

---

### `57/588` `backend/core/context.py`

- **المسار الكامل:** `F:\1f\p\ALI_Studio_Pro_Design4_4.6.0\04_Adaptive_Hybrid\backend/core/context.py`
- **الحجم:** 3022 بايت (3.0 KB)
- **الامتداد:** `.py`

```python
# -*- coding: utf-8 -*-
"""ConversationContext — سياق محادثة واحد.

يجمع:
- thread_id (تعريف المحادثة).
- messages (قائمة الأدوار والنصوص).
- perm_mode (read-only / default / full-access).
- tool_registry (مرجع للأدوات المتاحة في هذه المحادثة).
- project_dir (مسار العمل المرتبط بالمحادثة).
- extra (قاموس حر للحقول الإضافية مثل model_id, effort).

الـ Context هو ما يمر بين الطبقات (UI → Agent → Tools → Inference).
لا يحمل منطقاً، فقط حالة (state + behaviour خفيف).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class Message:
    """رسالة واحدة داخل محادثة."""
    role: str           # user | assistant | system | tool
    content: str
    ts: float = 0.0
    meta: Optional[Dict[str, Any]] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "role": self.role,
            "content": self.content,
            "ts": self.ts,
            "meta": self.meta or {},
        }


@dataclass
class ConversationContext:
    """سياق محادثة واحد — يمر بين الطبقات."""
    thread_id: str
    project_dir: str
    perm_mode: str = "default"          # read-only | default | full-access
    model: str = "ALI-Conversation (from-scratch)"
    effort: str = "Extra high"
    messages: List[Message] = field(default_factory=list)
    extra: Dict[str, Any] = field(default_factory=dict)
    tool_registry: Optional[Any] = None  # مرجع لـ ToolRegistry (نضعه في V0.4)

    # -------- message ops
    def add_user(self, content: str) -> None:
        import time
        self.messages.append(Message(role="user", content=content, ts=time.time()))

    def add_assistant(self, content: str) -> None:
        import time
        self.messages.append(
            Message(role="assistant", content=content, ts=time.time())
        )

    def add_system(self, content: str) -> None:
        import time
        self.messages.append(
            Message(role="system", content=content, ts=time.time())
        )

    def add_tool(self, content: str, meta: Optional[Dict[str, Any]] = None) -> None:
        import time
        self.messages.append(
            Message(role="tool", content=content, ts=time.time(), meta=meta)
        )

    def last_user(self) -> Optional[str]:
        for m in reversed(self.messages):
            if m.role == "user":
                return m.content
        return None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "thread_id": self.thread_id,
            "project_dir": self.project_dir,
            "perm_mode": self.perm_mode,
            "model": self.model,
            "effort": self.effort,
            "messages": [m.to_dict() for m in self.messages],
        }


__all__ = ["ConversationContext", "Message"]
```

---

### `58/588` `backend/core/deterministic_qa.py`

- **المسار الكامل:** `F:\1f\p\ALI_Studio_Pro_Design4_4.6.0\04_Adaptive_Hybrid\backend/core/deterministic_qa.py`
- **الحجم:** 7359 بايت (7.2 KB)
- **الامتداد:** `.py`

```python
# -*- coding: utf-8 -*-
"""Grounded deterministic Q&A router for local, high-confidence responses."""
from __future__ import annotations
from pathlib import Path
import re
from difflib import SequenceMatcher

_AR_DIACRITICS = re.compile(r"[\u064B-\u065F\u0670\u06D6-\u06ED]")
_STOP = {"ما","هو","هي","من","هل","كيف","كم","لدي","عندي","في","على","الى","إلى","عن","و","أريد","يمكن","لي","هذا","هذه","مع","معك","التي","الذي","الذين","اللاتي","اللواتي","بكم","بكم؟","كل","بعض","جدا","جداً","أيضا","أيضاً","هي","هما","هم","هن","أنا","نحن","انت","أنت","انتم","أنتم","كنت","سوف","قد","لقد","ليس","ليست","ليسوا","كلا","إن","ان","أن","لأن","لكن","حين","عندما","عندما","لقد","كلما","كما","بين","خلال","بعد","قبل","تحت","فوق","أمام","وراء","حول","عبر","الى","إلي","لدى","بدون","ضد","مع"}

# Aliases for synonyms (normalized form)
_SYNONYMS = {
    "معالج": "معالج",
    "المعالج": "معالج",
    "معالجي": "معالج",
    "معالجك": "معالج",
    "رسوم": "رسوم",
    "الرسوم": "رسوم",
    "الرسومي": "رسوم",
    "رسومي": "رسوم",
    "بطاقه": "بطاقة",
    "بطاقة": "بطاقة",
    "كرت": "بطاقة",
    "كارت": "بطاقة",
    "كرت": "كرت",
    # IMPORTANT: keep vram and ram as DISTINCT canonical forms
    "vram": "vram",
    "VRAM": "vram",
    "الرام": "ram",
    "رام": "ram",
    "الذاكرة": "ذاكرة",
    "ذاكره": "ذاكرة",
    "العشوائي": "ذاكرة",
    "العشوائية": "ذاكرة",
    "الوصول": "وصول",
    "وصول": "وصول",
    "القرص": "قرص",
    "قرص": "قرص",
    "ssd": "قرص",
    "هارد": "قرص",
    "الجهاز": "جهاز",
    "جهازي": "جهاز",
    "حاسوب": "جهاز",
    "كمبيوتر": "جهاز",
    "لابتوب": "لابتوب",
    "البطارية": "بطارية",
    "بطاريه": "بطارية",
    "البطاريه": "بطارية",
    "الشاشة": "شاشة",
    "شاشه": "شاشة",
    "الشاشه": "شاشة",
    "نظام": "نظام",
    "التشغيل": "تشغيل",
    "تشغيل": "تشغيل",
    "وندوز": "نظام",
    "ويندوز": "نظام",
    "windows": "نظام",
    "w10": "نظام",
    "w11": "نظام",
    "اصدار": "إصدار",
    "إصدار": "إصدار",
    "الانوية": "نواة",
    "انوية": "نواة",
    "الأنوية": "نواة",
    "نواة": "نواة",
    "نوا": "نواة",
    "cpu": "cpu",
    "gpu": "gpu",
    "ssd": "قرص",
    "اسمك": "اسم",
    "الاسم": "اسم",
    "اسم": "اسم",
    "اسمي": "اسم",
    "طراز": "طراز",
    "موديل": "طراز",
    "موديل": "طراز",
    "p50": "طراز",
    "ت50": "طراز",
    "ثينك": "طراز",
    "ثنك": "طراز",
}

# Question type hints for better routing
_QTYPE_HINTS = {
    "ما اسمك": "name",
    "ما اسم": "name",
    "من انت": "name",
    "من أنت": "name",
    "ما هي": "info",
    "ما هو": "info",
    "ما هو نظام": "system",
    "ما هي بطاقه": "gpu",
    "ما بطاقة": "gpu",
    "ما المعالج الرسوم": "gpu",  # الرسوم → GPU
    "ما المعالج المركزي": "cpu",  # المركزي → CPU
    "ما المعالج": "cpu",  # bare "المعالج" defaults to CPU
    "كم ذاكرة": "ram",
    "كم الرام": "ram",
    "كم ram": "ram",
    "كم العشوائي": "ram",
    "كم vram": "vram",  # explicit VRAM is GPU memory
    "ما الفرق بين ram و vram": "vram",
    "كم نواة": "cpu",
    "كم انوية": "cpu",
    "كم الأنوية": "cpu",
    "ما طراز": "model",
    "ما موديل": "model",
    "ما نظام": "system",
    "كم بطارية": "battery",
    "كم مساحة": "disk",
}


def _qtype(query_norm: str) -> str:
    """Return a question-type hint for the normalized query."""
    for pat, qtype in _QTYPE_HINTS.items():
        if pat in query_norm:
            return qtype
    return ""


def normalize(text: str) -> str:
    t = str(text or '').strip().lower()
    t = _AR_DIACRITICS.sub('', t).replace('ـ', '')
    t = t.translate(str.maketrans({
        'أ': 'ا', 'إ': 'ا', 'آ': 'ا', 'ى': 'ي', 'ؤ': 'و', 'ئ': 'ي',
        'ة': 'ه',  # taa marbuta -> haa to match common dialected forms
    }))
    t = re.sub(r'[^0-9a-z\u0600-\u06ff]+', ' ', t)
    t = ' '.join(t.split())
    # Apply synonyms (token-by-token to avoid breaking substrings)
    tokens = t.split()
    tokens = [_SYNONYMS.get(tok, tok) for tok in tokens]
    return ' '.join(tokens)


def tokens(text: str) -> set[str]:
    out = set()
    n = normalize(text)
    for t in n.split():
        if t in _STOP:
            continue
        if len(t) > 4 and t.startswith('ال'):
            out.add(t[2:])
        out.add(t)
    return out

class DeterministicQA:
    def __init__(self, root: str|Path):
        self.root=Path(root)
        self.items=[]
        for p in [self.root/'knowledge_seed'/'ALI_RUNTIME_FAQ_AR_V1.md', self.root/'knowledge_seed'/'ALI_DETERMINISTIC_FAQ_AR.md', self.root/'knowledge_seed'/'ALI_CORE_QA_AR.md']:
            if p.exists(): self._load(p)

    def _load(self, path: Path):
        text=path.read_text(encoding='utf-8',errors='replace')
        # Accept markdown bold role labels as well as plain labels.
        pat=re.compile(r'(?is)\*\*(?:User|المستخدم):\*\*\s*(.*?)\n\s*\*\*(?:Assistant|المساعد):\*\*\s*(.*?)(?=\n\s*\*\*(?:User|المستخدم):\*\*|\n\s*##|\Z)')
        for q,a in pat.findall(text):
            q=q.strip(); a=a.strip()
            if q and a: self.items.append((q,a,path.name))

    def match(self, query: str, threshold: float=0.55):
        qn=normalize(query); qt=tokens(query)
        if not qn or not qt: return None
        # Question-type routing: ensure the candidate question type matches the
        # query's qtype, otherwise the Jaccard-only match can route GPU question
        # to a CPU answer just because they share the word "معالج".
        qt_qtype = _qtype(qn)
        best=None
        for q,a,source in self.items:
            q2=normalize(q); qtok=tokens(q)
            if qn==q2:
                score=1.0
            else:
                inter=len(qt & qtok); union=max(1,len(qt|qtok))
                j=inter/union
                seq=SequenceMatcher(None,qn,q2).ratio()
                contain=sum(1 for x in qt if len(x)>=3 and any(x in y or y in x for y in qtok)) / max(1,len(qt))
                score=.45*seq+.35*j+.20*contain
                if qtok and (qt & qtok): score += .08
                # Penalize if question types don't match
                qt_cand = _qtype(q2)
                if qt_qtype and qt_cand and qt_qtype != qt_cand:
                    score -= 0.30
            if best is None or score>best[0]: best=(score,q,a,source)
        if best and best[0] >= threshold:
            return {'score':round(best[0],4),'question':best[1],'answer':best[2],'source':best[3]}
        return None
```

---

### `59/588` `backend/core/events.py`

- **المسار الكامل:** `F:\1f\p\ALI_Studio_Pro_Design4_4.6.0\04_Adaptive_Hybrid\backend/core/events.py`
- **الحجم:** 2688 بايت (2.6 KB)
- **الامتداد:** `.py`

```python
# -*- coding: utf-8 -*-
"""نظام أحداث بسيط وآمن للخيوط.

- thread-safe عبر Lock.
- callbacks تُنفّذ متسلسلة (لا تبعثر).
- لا يلزم async — يمكن للـ UI أن يستمع وينفّذ في main thread.

استخدام:
    bus = EventBus()
    bus.subscribe("message.user", lambda e: print(e.data))
    bus.publish(Event("message.user", {"content": "hi"}))
"""

from __future__ import annotations

import threading
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List


@dataclass
class Event:
    """حدث مجرد يحمل نوعاً وبيانات."""
    type: str
    data: Dict[str, Any] = field(default_factory=dict)
    source: str = ""


Handler = Callable[[Event], None]


class EventBus:
    """ناقل أحداث بسيط — Subscribe/Publish/Unsub."""

    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._handlers: Dict[str, List[Handler]] = {}

    def subscribe(self, event_type: str, handler: Handler) -> None:
        with self._lock:
            self._handlers.setdefault(event_type, []).append(handler)

    def unsubscribe(self, event_type: str, handler: Handler) -> None:
        with self._lock:
            if event_type in self._handlers:
                try:
                    self._handlers[event_type].remove(handler)
                except ValueError:
                    pass

    def publish(self, event: Event) -> None:
        """نشر الحدث — ينسخ قائمة المعالجات لتفادي التعديل أثناء المرور."""
        with self._lock:
            handlers = list(self._handlers.get(event.type, []))
        for h in handlers:
            try:
                h(event)
            except Exception:
                # لا نسمح لـ handler مكسور بإسقاط البقية.
                # الخطأ يُسجَّل في logging الذي سيُضَاف لاحقاً.
                pass

    def clear(self) -> None:
        with self._lock:
            self._handlers.clear()


# أنواع الأحداث الموحدة داخل ALI Studio
class Events:
    """ثوابت أسماء الأحداث لتقليل الأخطاء الإملائية."""
    USER_MESSAGE = "message.user"
    ASSISTANT_MESSAGE = "message.assistant"
    TOOL_START = "tool.start"
    TOOL_FINISH = "tool.finish"
    PERMISSION_REQUEST = "permission.request"
    PERMISSION_GRANT = "permission.grant"
    PERMISSION_DENY = "permission.deny"
    THREAD_NEW = "thread.new"
    THREAD_OPEN = "thread.open"
    CONFIG_CHANGED = "config.changed"
    ERROR = "error"


__all__ = ["EventBus", "Event", "Events"]
```

---

### `60/588` `backend/core/job_manager.py`

- **المسار الكامل:** `F:\1f\p\ALI_Studio_Pro_Design4_4.6.0\04_Adaptive_Hybrid\backend/core/job_manager.py`
- **الحجم:** 3151 بايت (3.1 KB)
- **الامتداد:** `.py`

```python
# -*- coding: utf-8 -*-
"""Small persistent background job manager used by the desktop UI and scripts."""
from __future__ import annotations
from dataclasses import dataclass, asdict
from pathlib import Path
import json, threading, time, traceback, uuid
from typing import Any, Callable, Dict, Optional

@dataclass
class Job:
    id: str
    name: str
    kind: str = "task"
    status: str = "queued"
    progress: float = 0.0
    message: str = ""
    created_at: float = 0.0
    started_at: float = 0.0
    finished_at: float = 0.0
    result: Any = None
    error: str = ""

class JobManager:
    def __init__(self, state_file: str | Path):
        self.path = Path(state_file)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._jobs: Dict[str, Job] = {}
        self._lock = threading.RLock()
        self._load()

    def _load(self):
        if not self.path.exists(): return
        try:
            raw = json.loads(self.path.read_text(encoding="utf-8"))
            for item in raw[-100:]:
                j = Job(**{k:item.get(k) for k in Job.__dataclass_fields__})
                self._jobs[j.id] = j
        except Exception:
            pass

    def _persist(self):
        with self._lock:
            data = [asdict(j) for j in list(self._jobs.values())[-100:]]
            self.path.write_text(json.dumps(data, ensure_ascii=False, indent=2, default=str), encoding="utf-8")

    def create(self, name: str, kind: str = "task") -> Job:
        j = Job(str(uuid.uuid4()), name, kind, "queued", 0.0, "queued", time.time())
        with self._lock: self._jobs[j.id] = j
        self._persist(); return j

    def update(self, job_id: str, **fields) -> Job:
        with self._lock:
            j = self._jobs[job_id]
            for k,v in fields.items():
                if hasattr(j,k): setattr(j,k,v)
        self._persist(); return j

    def snapshot(self):
        with self._lock: return [asdict(j) for j in list(self._jobs.values())[-100:]]

    def run(self, name: str, fn: Callable[[Callable[..., None]], Any], kind: str = "task") -> Job:
        job = self.create(name, kind)
        def progress(message: str = "", value: Optional[float] = None, **extra):
            fields = {"message": message, **extra}
            if value is not None: fields["progress"] = max(0.0, min(1.0, float(value)))
            self.update(job.id, **fields)
        def worker():
            self.update(job.id, status="running", started_at=time.time(), message="started")
            try:
                result = fn(progress)
                self.update(job.id, status="completed", progress=1.0, finished_at=time.time(), result=result, message="completed")
            except Exception as exc:
                err = "".join(traceback.format_exception(type(exc), exc, exc.__traceback__))[-12000:]
                self.update(job.id, status="failed", finished_at=time.time(), error=err, message=str(exc))
        threading.Thread(target=worker, name=f"ALI-{kind}-{job.id[:8]}", daemon=True).start()
        return job

    def get(self, job_id: str) -> Optional[Job]:
        with self._lock: return self._jobs.get(job_id)
```

---

### `61/588` `backend/core/logger.py`

- **المسار الكامل:** `F:\1f\p\ALI_Studio_Pro_Design4_4.6.0\04_Adaptive_Hybrid\backend/core/logger.py`
- **الحجم:** 2253 بايت (2.2 KB)
- **الامتداد:** `.py`

```python
# -*- coding: utf-8 -*-
"""طبقة الـ logging الموحدة.

- log إلى ملف يومي داخل APPDATA\\ALI-Agent\\logs\\.
- log إلى stderr أيضاً عند الحاجة.
- thread-safe.
- لا أسرار في الـ logs (token redaction بسيطة).
"""

from __future__ import annotations

import logging
import os
import re
import sys
import threading
from logging.handlers import RotatingFileHandler
from pathlib import Path

_LOCK = threading.Lock()
_INITIALIZED = False
_TOKEN_RE = re.compile(r"(token[\"'\\s:=]+)([A-Za-z0-9]{8,})", re.I)


class _RedactFilter(logging.Filter):
    """إخفاء أي token طويل يظهر في الرسالة."""

    def filter(self, record: logging.LogRecord) -> bool:
        try:
            msg = record.getMessage()
            msg = _TOKEN_RE.sub(r"\1***REDACTED***", msg)
            record.msg = msg
            record.args = ()
        except Exception:
            pass
        return True


def _init_once() -> None:
    global _INITIALIZED
    if _INITIALIZED:
        return
    with _LOCK:
        if _INITIALIZED:
            return
        from config.paths import APP_PATHS
        logs_dir = APP_PATHS.user_logs_dir()
        log_file = logs_dir / "ali_studio.log"

        root = logging.getLogger("ali")
        root.setLevel(logging.INFO)
        # تفادي تكرار handlers عند إعادة التحميل.
        root.handlers.clear()

        fmt = logging.Formatter(
            "%(asctime)s [%(levelname)s] %(name)s: %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        redactor = _RedactFilter()

        fh = RotatingFileHandler(
            str(log_file), maxBytes=1_000_000, backupCount=3,