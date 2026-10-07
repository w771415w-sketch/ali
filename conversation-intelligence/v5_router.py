# -*- coding: utf-8 -*-
"""ALI Conversation Intelligence V5 router.

Stdlib-only request framing layer. It does not execute tools, modify files, or make
network calls. It converts natural language into a deterministic request frame
that can be consumed by the existing orchestrator/runtime.
"""
from __future__ import annotations
from dataclasses import dataclass, asdict
import re
import unicodedata
from typing import Any, Iterable


AR_DIACRITICS = re.compile(r"[\u0610-\u061a\u064b-\u065f\u0670\u06d6-\u06ed]")
WS = re.compile(r"\s+")
WORD = re.compile(r"[A-Za-z0-9_\u0600-\u06ff]+")


def normalize(text: str) -> str:
    s = unicodedata.normalize("NFKC", str(text or ""))
    s = AR_DIACRITICS.sub("", s).replace("ـ", "")
    s = s.casefold()
    return WS.sub(" ", s).strip()


def contains_any(text: str, values: Iterable[str]) -> bool:
    t = normalize(text)
    return any(normalize(v) in t for v in values)


def detect_language(text: str) -> str:
    t = str(text or "")
    ar = len(re.findall(r"[\u0600-\u06ff]", t))
    en = len(re.findall(r"[A-Za-z]", t))
    if ar and en:
        return "mixed"
    if ar:
        return "ar"
    if en:
        return "en"
    return "unknown"


@dataclass
class IntentFrame:
    intent: str
    confidence: float
    mode: str
    language: str
    domain: str
    freshness_required: bool
    continuation: bool
    confirmation: bool
    correction: bool
    cancellation: bool
    high_risk: bool
    ambiguity_score: float
    asks_for_sources: bool
    asks_for_execution: bool
    references_previous_context: bool
    requested_depth: str
    deliverable: str
    constraints: list[str]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


_INTENT_PATTERNS = [
    (("ترجم", "translation", "translate"), "translation", "transform", 0.93),
    (("لخص", "لخّص", "summary", "summarize"), "summarization", "transform", 0.92),
    (("اشرح", "فسر", "فسّر", "explain"), "explanation", "answer", 0.91),
    (("ما هو", "ما هي", "ما معنى", "define", "definition"), "definition", "answer", 0.94),
    (("اعد صياغ", "أعد صياغ", "rewrite", "rephrase"), "rewriting", "transform", 0.94),
    (("صحح", "صححه", "دقق", "تدقيق", "proofread"), "proofreading", "transform", 0.94),
    (("قارن", "مقارنة", "compare", "versus", "vs"), "comparison", "decision", 0.93),
    (("انصح", "نصيحتك", "بماذا تنصح", "recommend", "recommendation"), "recommendation", "decision", 0.86),
    (("ما الافضل", "الأفضل", "افضل", "best", "which should"), "decision_support", "decision", 0.84),
    (("ابحث", "بحث ويب", "الانترنت", "الإنترنت", "search web", "research"), "web_research", "research", 0.94),
    (("تحقق", "هل هذا صحيح", "verify", "fact check", "صحيح ام"), "fact_check", "verify", 0.90),
    (("نفذ", "شغل", "شغّل", "طبق", "طبّق", "execute", "run"), "execution", "execute", 0.90),
    (("عدّل", "عدل", "تعديل", "edit", "modify"), "modification", "execute", 0.91),
    (("انشئ", "أنشئ", "اكتب", "create", "generate"), "creation", "create", 0.88),
    (("حلل المشروع", "تحليل المشروع", "analyze project"), "project_analysis", "review", 0.96),
    (("راجع الكود", "مراجعة الكود", "code review"), "code_review", "review", 0.96),
    (("خطأ", "bug", "debug", "صحح الخطأ", "اصلح الخطأ", "أصلح الخطأ"), "debugging", "execute", 0.88),
    (("لا يعمل", "لا يشتغل", "مشكلة", "عطل", "troubleshoot", "not working"), "troubleshooting", "diagnose", 0.87),
    (("شغل الامر", "شغّل الأمر", "terminal", "powershell", "cmd"), "terminal_operation", "execute", 0.95),
    (("git ", "git status", "git commit", "git push", "git pull", "github"), "git_operation", "execute", 0.95),
    (("ملف", "folder", "directory", "read file", "write file"), "file_operation", "execute", 0.80),
    (("تدريب", "درّب", "train", "fine-tune", "lora"), "model_training", "train", 0.93),
    (("gguf", "تكميم", "quantize", "convert model"), "model_conversion", "execute", 0.94),
    (("اختبر", "اختبار", "test", "tests"), "testing", "verify", 0.86),
    (("تحقق من النتيجة", "verify result", "ثبت النتيجة", "اثبت"), "verification", "verify", 0.90),
    (("احفظ", "تذكر", "تذكّر", "remember", "save this"), "memory_save", "memory", 0.92),
    (("انس", "انسى", "احذف الذاكرة", "forget", "remove memory"), "memory_forget", "memory", 0.95),
    (("ماذا تتذكر", "ماذا تحفظ", "what do you remember"), "memory_recall", "memory", 0.95),
    (("كمل", "تابع", "اكمل", "أكمل", "من حيث توقفنا", "continue"), "follow_up", "continue", 0.98),
    (("نعم", "تمام", "موافق", "نفذها", "go ahead", "yes"), "confirmation", "confirm", 0.86),
    (("الغ", "ألغ", "توقف", "cancel", "stop"), "cancellation", "cancel", 0.97),
    (("هذا خطأ", "غير صحيح", "غير صحيحة", "wrong", "incorrect"), "correction", "recover", 0.97),
    (("كيف", "how ", "ما هي الخطوات", "steps", "طريقة"), "question_answering", "answer", 0.72),
]

_DOMAIN_PATTERNS = [
    ("software", ("python","javascript","typescript","react","electron","api","backend","frontend","كود","برمجة")),
    ("hardware", ("cpu","gpu","ram","nvme","ssd","hdd","laptop","معالج","ذاكرة","بطاقة شاشة")),
    ("windows", ("windows","win11","powershell","cmd","registry","ويندوز")),
    ("android", ("android","apk","adb","fastboot","سامسونج","اندرويد")),
    ("firmware", ("firmware","bootloader","preloader","mtk","mediatek","فلاش","فريموير")),
    ("ai", ("ai","llm","rag","embedding","نموذج","ذكاء اصطناعي")),
    ("security", ("security","permission","token","secret","credential","أمن","صلاحيات")),
    ("web", ("http","https","website","browser","موقع","ويب")),
    ("data", ("csv","json","database","sqlite","بيانات","قاعدة بيانات")),
    ("git", ("git","github","commit","branch","pull request")),
    ("models", ("model","checkpoint","gguf","weights","tokenizer","نموذج","أوزان")),
]


def _domain(text: str) -> str:
    t = normalize(text)
    best, score = "general", 0
    for name, words in _DOMAIN_PATTERNS:
        hits = sum(1 for w in words if normalize(w) in t)
        if hits > score:
            best, score = name, hits
    return best


def _depth(text: str) -> str:
    t = normalize(text)
    if contains_any(t, ("بالتفصيل", "تفصيلي", "شامل", "كامل", "بعمق", "comprehensive", "deep")):
        return "detailed"
    if contains_any(t, ("باختصار", "مختصر", "مختصرا", "short", "brief")):
        return "concise"
    return "adaptive"


def _deliverable(text: str, mode: str, intent: str) -> str:
    t = normalize(text)
    if contains_any(t, ("كود", "code", "script")):
        return "code"
    if contains_any(t, ("جدول", "table")):
        return "table"
    if contains_any(t, ("تقرير", "report")):
        return "report"
    if contains_any(t, ("قائمة", "list")):
        return "list"
    if contains_any(t, ("ملف", "file", "document")) and mode in {"create","execute","transform"}:
        return "file"
    if intent in {"comparison","decision_support"}:
        return "comparison"
    if intent in {"web_research","fact_check","current_information"}:
        return "researched_answer"
    if mode in {"execute","train","verify"}:
        return "action_result"
    return "answer"


def classify(text: str, *, previous_intent: str | None = None) -> IntentFrame:
    raw = str(text or "")
    t = normalize(raw)
    lang = detect_language(raw)
    continuation = contains_any(t, ("كمل","تابع","اكمل","أكمل","من حيث توقفنا","واصل","continue","same as before"))
    confirmation = contains_any(t, ("نعم","ايوه","أيوه","تمام","موافق","نفذها","go ahead","yes"))
    correction = contains_any(t, ("هذا خطأ","غير صحيح","غير صحيحة","صحح","صححه","wrong","incorrect"))
    cancellation = contains_any(t, ("إلغاء","الغ","ألغ","توقف","لا تكمل","cancel","stop"))
    freshness = contains_any(t, ("اليوم","الآن","حاليا","حاليًا","آخر","الأحدث","حديث","مؤخرا","مؤخرًا","today","now","latest","recent","2026"))
    asks_sources = contains_any(t, ("مصدر","مصادر","مرجع","مراجع","استشهاد","cite","citation","sources"))
    asks_execution = contains_any(t, ("نفذ","شغّل","شغل","عدّل","عدل","أنشئ","انشئ","اكتب","احذف","ارفع","ثبّت","طبق","run","execute","edit","create","upload","install"))
    high_risk = contains_any(t, ("احذف","دمر","استبدل","ارفع","انشر","أرسل","نشر","deploy","delete","overwrite","publish"))
    refs_previous = continuation or contains_any(t, ("هذا","هذه","ذلك","السابق","المذكور","الملف نفسه","نفسه","كما سبق","as above","that","previous"))
    intent, mode, confidence = "question_answering", "answer", 0.60
    if continuation and previous_intent:
        intent, mode, confidence = "follow_up", "continue", 0.98
    else:
        best = None
        for patterns, i, m, c in _INTENT_PATTERNS:
            hits = sum(1 for p in patterns if normalize(p) in t)
            if hits and (best is None or (hits, c) > best[0]):
                best = ((hits, c), i, m, c)
        if best:
            _, intent, mode, confidence = best
        if freshness and intent == "question_answering":
            intent, mode, confidence = "current_information", "research", 0.86
        if asks_sources and intent == "question_answering":
            intent, mode, confidence = "source_request", "research", 0.87

    # Multi-step requests are first-class: preserve the dominant goal but elevate orchestration.
    step_markers = len(re.findall(r"\b(ثم|بعدها|وبعد|and then|then)\b", t))
    separators = len(re.findall(r"[؛;]|\s+و\s+", t))
    if step_markers + separators >= 3 or contains_any(t, ("من البداية للنهاية","بالكامل","end to end","fully")):
        if intent not in {"cancellation","confirmation","correction"}:
            intent = "multi_step_task"
            mode = "orchestrate"
            confidence = max(confidence, 0.88)

    ambiguity = 0.0
    if not t:
        ambiguity = 1.0
    elif len(t) < 12:
        ambiguity += 0.35
    if refs_previous and not previous_intent:
        ambiguity += 0.30
    if high_risk and len(t) < 40:
        ambiguity += 0.45
    if intent == "unknown":
        ambiguity += 0.35
    ambiguity = min(1.0, ambiguity)

    constraints = []
    if lang != "unknown":
        constraints.append(f"language={lang}")
    if freshness:
        constraints.append("freshness_required")
    if asks_sources:
        constraints.append("sources_requested")
    if high_risk:
        constraints.append("high_risk_confirmation")
    if refs_previous:
        constraints.append("resolve_previous_context")
    if asks_execution:
        constraints.append("execution_requested")

    return IntentFrame(
        intent=intent,
        confidence=round(float(confidence), 3),
        mode=mode,
        language=lang,
        domain=_domain(raw),
        freshness_required=freshness,
        continuation=continuation,
        confirmation=confirmation,
        correction=correction,
        cancellation=cancellation,
        high_risk=high_risk,
        ambiguity_score=round(ambiguity, 3),
        asks_for_sources=asks_sources,
        asks_for_execution=asks_execution,
        references_previous_context=refs_previous,
        requested_depth=_depth(raw),
        deliverable=_deliverable(raw, mode, intent),
        constraints=constraints,
    )


def needs_clarification(frame: IntentFrame) -> bool:
    if frame.cancellation or frame.correction:
        return False
    return frame.ambiguity_score >= 0.72 or (
        frame.high_risk and frame.ambiguity_score >= 0.45
    )


def build_response_policy(frame: IntentFrame) -> dict[str, Any]:
    """Return presentation constraints; never includes hidden reasoning."""
    style = {
        "answer": "direct_first",
        "research": "evidence_first",
        "execute": "result_first",
        "orchestrate": "progressive_steps",
        "diagnose": "symptoms_causes_fix_verify",
        "transform": "preserve_meaning",
        "decision": "criteria_comparison_recommendation",
        "verify": "claim_evidence_verdict",
        "recover": "acknowledge_correct_retest",
        "memory": "state_saved_or_not",
        "continue": "resume_active_goal",
        "clarify": "one_targeted_question",
        "confirm": "confirm_target_and_scope",
        "cancel": "stop_and_report_state",
        "create": "deliver_artifact",
        "train": "dataset_checkpoint_evaluate_gate",
    }.get(frame.mode, "direct_first")

    return {
        "language": frame.language,
        "requested_depth": frame.requested_depth,
        "style": style,
        "citations": frame.freshness_required or frame.asks_for_sources,
        "show_assumptions": frame.ambiguity_score >= 0.40,
        "ask_clarification": needs_clarification(frame),
        "confirmation_required": frame.high_risk,
        "deliverable": frame.deliverable,
        "avoid_hidden_reasoning": True,
    }


__all__ = [
    "IntentFrame",
    "normalize",
    "detect_language",
    "classify",
    "needs_clarification",
    "build_response_policy",
]
