# -*- coding: utf-8 -*-
"""Deterministic, stdlib-only conversation understanding layer for ALI V6.

The router creates a request frame and updates dialogue state. It does not
execute tools or expose hidden reasoning.
"""
from __future__ import annotations

from dataclasses import dataclass, asdict
import re
import unicodedata
from typing import Any, Mapping


AR_DIACRITICS = re.compile(r"[\u0610-\u061a\u064b-\u065f\u0670\u06d6-\u06ed]")
WS = re.compile(r"\s+")
AR = re.compile(r"[\u0600-\u06ff]")
EN = re.compile(r"[A-Za-z]")
NUM = re.compile(r"\b\d+(?:[.,]\d+)?\b")


def normalize(text: str) -> str:
    s = unicodedata.normalize("NFKC", str(text or ""))
    s = AR_DIACRITICS.sub("", s).replace("ـ", "")
    return WS.sub(" ", s.casefold()).strip()


def lang(text: str) -> str:
    s = str(text or "")
    a, e = len(AR.findall(s)), len(EN.findall(s))
    if a and e: return "mixed"
    if a: return "ar"
    if e: return "en"
    return "unknown"


def hit(text: str, words: tuple[str, ...]) -> bool:
    s = normalize(text)
    return any(normalize(w) in s for w in words)


CONTINUE = ("كمل","اكمل","أكمل","تابع","واصل","استمر","من حيث توقفنا","نفس السابق","continue")
CONFIRM = ("نعم","ايوه","أيوه","تمام","موافق","نفذها","ابدأ","go ahead","yes")
CANCEL = ("توقف","أوقف","الغ","ألغ","إلغاء","cancel","stop")
CORRECT = ("هذا خطأ","هذا غير صحيح","غير صحيح","غير صحيحة","صحح","صححه","incorrect","wrong")
RESEARCH = ("ابحث","بحث ويب","الانترنت","الإنترنت","مصادر","تحقق عبر الإنترنت","search web","research")
EXECUTE = ("نفذ","شغل","شغّل","طبق","طبّق","أنشئ","انشئ","عدّل","عدل","احذف","ارفع","ثبت","run","execute","create","edit")
CURRENT = ("اليوم","الآن","حاليا","حاليًا","آخر","الأحدث","حديث","مؤخرا","مؤخرًا","latest","current","today","now")
HIGH_RISK = ("احذف","دمر","استبدل","اكتب فوق","overwrite","delete","publish","انشر","ارفع","deploy","إرسال","أرسل")
MULTI = ("ثم","وبعدها","ثم بعد","وأيضا","وكذلك","ثم قم","and then","after that","also")
DEPTH_DEEP = ("بالتفصيل","تفصيلي","عميق","شامل","منهجي","deep","detailed","comprehensive")
DEPTH_BRIEF = ("باختصار","مختصر","فقط النتيجة","brief","concise","just the answer")


@dataclass(frozen=True)
class Frame:
    intent: str
    sub_intent: str | None
    speech_act: str
    mode: str
    language: str
    domain: str
    user_goal: str
    confidence: float
    freshness_required: bool
    continuation: bool
    confirmation: bool
    correction: bool
    cancellation: bool
    multi_intent: bool
    ambiguity_level: str
    risk_level: str
    requested_depth: str
    output_format: str | None
    references: list[str]
    constraints: list[str]
    evidence_required: bool
    confirmation_required: bool
    required_tools: list[str]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _domain(s: str) -> str:
    t = normalize(s)
    groups = {
        "software": ("python","javascript","typescript","react","electron","api","backend","frontend","كود","برمجة"),
        "ai": ("ai","llm","rag","embedding","lora","qlora","gguf","نموذج","ذكاء اصطناعي","تدريب"),
        "data": ("sql","sqlite","postgres","mysql","csv","json","بيانات","قاعدة بيانات","جدول"),
        "git": ("git","github","commit","branch","pull request","مستودع","جيت"),
        "windows": ("windows","powershell","cmd","ويندوز"),
        "android": ("android","adb","fastboot","سامسونج","اندرويد"),
        "firmware": ("firmware","bootloader","preloader","mtk","mediatek","فلاش","فريموير"),
        "hardware": ("cpu","gpu","ram","nvme","ssd","hdd","معالج","رام","بطاقة شاشة"),
        "security": ("security","token","secret","credential","permission","أمن","صلاحيات"),
        "web": ("http","https","browser","website","ويب","موقع"),
        "writing": ("رسالة","ايميل","بريد","مقال","تقرير","write","email","report"),
        "translation": ("ترجم","translation","translate"),
    }
    counts = {k: sum(1 for w in v if normalize(w) in t) for k,v in groups.items()}
    best = max(counts, key=counts.get)
    return best if counts[best] else "general"


def _intent(s: str) -> tuple[str, str | None, str, float]:
    t = normalize(s)
    tests = [
        (("ترجم","translate"),"translation",None,"transform",.96),
        (("لخص","لخّص","summarize"),"summarization",None,"transform",.95),
        (("اشرح","فسر","explain"),"explanation",None,"answer",.94),
        (("ما هو","ما هي","ما معنى","define"),"definition",None,"answer",.95),
        (("قارن","مقارنة","compare","versus"),"comparison",None,"decision",.94),
        (("ابحث","بحث ويب","research","search web"),"web_research",None,"research",.97),
        (("تحقق","fact check","هل هذا صحيح"),"fact_check",None,"verify",.94),
        (("راجع الكود","code review"),"code_review",None,"review",.97),
        (("حلل المشروع","تحليل المشروع"),"project_analysis",None,"review",.97),
        (("خطأ","لا يعمل","bug","debug","أصلح الخطأ"),"debugging",None,"execute",.92),
        (("اختبر","اختبار","test"),"testing",None,"verify",.90),
        (("تدريب","درّب","train","fine-tune","lora"),"model_training",None,"train",.95),
        (("gguf","تكميم","quantize"),"model_conversion",None,"execute",.96),
        (("احفظ","تذكر","remember"),"memory_save",None,"memory",.95),
        (("انس","انسى","احذف الذاكرة","forget"),"memory_forget",None,"memory",.97),
        (("كمل","اكمل","تابع","من حيث توقفنا","continue"),"follow_up","continue_active_goal","continue",.99),
        (("هذا خطأ","غير صحيح","incorrect","wrong"),"correction",None,"recover",.99),
        (("توقف","ألغ","إلغاء","cancel","stop"),"cancellation",None,"cancel",.99),
        (("نعم","تمام","موافق","نفذها","yes"),"confirmation",None,"confirm",.91),
        (("نفذ","شغل","طبق","أنشئ","عدل","احذف","ارفع","execute","run","create","edit"),"execution",None,"execute",.88),
    ]
    for words,name,sub,mode,c in tests:
        if any(normalize(w) in t for w in words):
            return name,sub,mode,c
    if t.startswith(("كيف","how")):
        return "question","how_to","answer",.78
    if "؟" in s or "?" in s:
        return "question_answering",None,"answer",.80
    return "unknown",None,"clarify",.45


def _speech(s: str, continuation: bool, confirmation: bool, correction: bool, cancellation: bool) -> str:
    if cancellation: return "cancellation"
    if correction: return "correction"
    if confirmation: return "confirmation"
    if continuation: return "continuation"
    if hit(s, EXECUTE): return "command"
    if "؟" in s or "?" in s or normalize(s).startswith(("كيف","لماذا","ما ","ماذا ","why","what ","how ")): return "question"
    return "request"


def _references(s: str) -> list[str]:
    t = normalize(s)
    refs=[]
    for x in ("هذا","هذه","ذلك","تلك","السابق","السابقة","الأول","الثاني","نفسه","نفس السابق","it","that","same"):
        if normalize(x) in t: refs.append(x)
    return refs


def _depth(s: str) -> str:
    if hit(s, DEPTH_DEEP): return "deep"
    if hit(s, DEPTH_BRIEF): return "brief"
    return "normal"


def frame(user_text: str, state: Mapping[str, Any] | None = None) -> Frame:
    s = str(user_text or "")
    continuation = hit(s, CONTINUE)
    confirmation = hit(s, CONFIRM)
    correction = hit(s, CORRECT)
    cancellation = hit(s, CANCEL)
    domain = _domain(s)
    intent, sub, mode, conf = _intent(s)
    refs = _references(s)
    multi = hit(s, MULTI) or len(re.findall(r"\b(?:و|ثم|also|and)\b", normalize(s))) >= 2
    freshness = hit(s, RESEARCH) or hit(s, CURRENT)
    risk = "none"
    if hit(s, HIGH_RISK):
        risk = "external_side_effect" if hit(s, ("ارفع","انشر","أرسل","publish","deploy")) else "high"
    ambiguity = "none"
    if len(s.strip()) < 8 or intent == "unknown": ambiguity = "medium"
    if refs and not (state or {}).get("active_goal"): ambiguity = "high"
    if risk in {"high","external_side_effect"} and not (state or {}).get("active_goal"): ambiguity = "dangerous"
    output = None
    low = normalize(s)
    if "json" in low: output="json"
    elif "markdown" in low: output="markdown"
    elif "جدول" in low or "table" in low: output="table"
    elif "كود" in low or "code" in low: output="code"
    tools=[]
    if freshness: tools.append("web")
    if domain in {"software","ai","data","git","windows","android","firmware","hardware"} and hit(s, EXECUTE): tools.append("terminal_or_project")
    if domain in {"software","data","ai"} and intent in {"question_answering","explanation","debugging","project_analysis"}: tools.append("files_or_rag")
    if intent in {"execution","model_training","model_conversion","testing","debugging","project_analysis","code_review"}: tools.append("project")
    return Frame(
        intent=intent, sub_intent=sub, speech_act=_speech(s,continuation,confirmation,correction,cancellation),
        mode=mode, language=lang(s), domain=domain,
        user_goal=("continue" if continuation else "recover" if correction else "cancel" if cancellation else "execute" if mode=="execute" else "research" if mode=="research" else "understand"),
        confidence=conf, freshness_required=freshness,
        continuation=continuation, confirmation=confirmation, correction=correction,
        cancellation=cancellation, multi_intent=multi,
        ambiguity_level=ambiguity, risk_level=risk, requested_depth=_depth(s),
        output_format=output, references=refs,
        constraints=[], evidence_required=(freshness or intent in {"fact_check","comparison"}),
        confirmation_required=(risk in {"high","external_side_effect"}),
        required_tools=sorted(set(tools)),
    )


def update_state(previous: Mapping[str, Any] | None, request: Frame) -> dict[str, Any]:
    prev = dict(previous or {})
    state = {
        "active_goal": prev.get("active_goal"),
        "active_domain": prev.get("active_domain"),
        "stage": prev.get("stage","discover"),
        "constraints": list(prev.get("constraints",[])),
        "decisions": list(prev.get("decisions",[])),
        "active_entities": list(prev.get("active_entities",[])),
        "rejected_options": list(prev.get("rejected_options",[])),
        "missing_requirements": list(prev.get("missing_requirements",[])),
        "pending_confirmation": prev.get("pending_confirmation"),
        "pending_tool_action": prev.get("pending_tool_action"),
        "last_verified_result": prev.get("last_verified_result"),
        "corrections": list(prev.get("corrections",[])),
    }
    if request.cancellation:
        state["stage"]="cancelled"
        state["pending_confirmation"]=None
        state["pending_tool_action"]=None
        return state
    if request.correction:
        state["stage"]="recover"
    elif request.confirmation and prev.get("pending_confirmation"):
        state["stage"]="execute"
        state["pending_tool_action"]=prev.get("pending_confirmation")
        state["pending_confirmation"]=None
    elif request.continuation:
        state["stage"]=prev.get("stage","execute") if prev.get("active_goal") else "clarify"
    else:
        state["active_goal"]=request.intent
        state["active_domain"]=request.domain
        state["stage"]="clarify" if request.ambiguity_level in {"high","dangerous"} else "plan" if request.multi_intent else "discover"
    if request.confirmation_required and not request.confirmation:
        state["pending_confirmation"]=request.intent
    return state


__all__ = ["Frame","frame","update_state","normalize","lang"]
