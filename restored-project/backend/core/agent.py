# -*- coding: utf-8 -*-
"""Professional AI Agent — local multi-step reasoning loop.

المسؤوليات:
- Intent Analysis: يصنف النص إلى intent (read, write, search, command, git, code, question).
- Plan: يبني sequence من tool calls.
- Execute: ينفذ كل tool بترتيب.
- Reflect: يلخص النتائج في رد نهائي.
- Smart Fallback: إذا لا توجد tools، يعطي إجابة مفيدة.

يعمل بدون أي نموذج خارجي — logic محلي + tokenizer للـ token counting.
"""

from __future__ import annotations

import re
import time
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple


# ============================================================================
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
