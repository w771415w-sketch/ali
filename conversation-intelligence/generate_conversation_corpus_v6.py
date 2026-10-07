# -*- coding: utf-8 -*-
"""Deterministic streaming generator for the ALI V6 conversation corpus.

Default target: 10,000,000 records.
It writes sharded JSONL and never needs to hold the whole corpus in RAM.

The generated records are synthetic behavior examples. They are not a replacement
for verified factual knowledge, RAG sources, or human-reviewed benchmark data.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Iterable


FAMILIES = [
"qa","definition","explanation","how_to","clarification","context_followup",
"topic_switch","pronoun_resolution","instruction_following","summarization",
"translation","rewriting","proofreading","extraction","classification",
"comparison","recommendation","decision_support","brainstorming","planning",
"project_requirements","architecture","project_build","code_generation",
"code_review","debugging","troubleshooting","testing","file_operation",
"database","api","git","devops","deployment","release","ai_concepts",
"model_selection","fine_tuning","lora","qlora","rag","evaluation",
"model_conversion","tool_use","web_research","fact_check","memory",
"correction_recovery","safety_confirmation",
"product_thinking",
"ux_research",
"user_stories",
"acceptance_criteria",
"team_collaboration",
"role_handoff",
"release_management",
"change_management",
"cost_optimization",
"capacity_planning",
"observability",
"incident_response",
"business_process",
"workflow_automation",
"localization_numbers_currency",
"content_moderation",
"knowledge_provenance",
"source_quality",
"fact_checking",
"meeting_notes",
"customer_support",
"requirements_traceability",
"compatibility",
"maintainability",
"clean_architecture",
"load_testing",
"fuzz_testing",
"rollback_recovery",
"backup_restore",
"sandbox_execution",
"environment_config",
"long_context",
"project_state",
"task_management",
"priority",
"dependency_management",
"versioning",
"decision_request",
"user_preferences",
"tone_adaptation",
"expertise_adaptation",
"output_schema",
"structured_output",
"code_patch",
"partial_completion",
"false_completion_recovery",
"unknown_answer",
"missing_input",
"conflicting_requirements",
"stale_information",
"evidence_conflict",
"citation_quality",
"source_recency",
"tool_choice",
"tool_arguments",
"tool_postcondition",
"tool_retry",
"tool_alternative",
"tool_stop_condition",
"memory_boundary",
"memory_forget",
"memory_update",
"conversation_resume",
"topic_return",
"topic_switch",
"ordinal_resolution",
"pronoun_resolution",
"implicit_request",
"explicit_request",
"safety_boundary",
"permission_boundary",
"confirmation_boundary",
"progress_reporting",
"status_reporting",
"delivery_checklist",
"regression_prevention",
"change_impact",
"dependency_graph",
"resource_constraints",
"offline_mode",
"arabic_typo",
"arabic_colloquial",
"arabic_mixed"
]

TOPICS = [
"python","javascript","typescript","react","electron","fastapi","sqlite","postgresql",
"git","github","windows","linux","android","firmware","security","apis","databases",
"rag","llm","transformers","lora","gguf","evaluation","testing","performance",
"project_management","documentation","education","mathematics","statistics",
"translation","technical_writing","data_analysis","files","automation","deployment",
"debugging","architecture","user_interface","memory","web_research","citations",
"model_lifecycle","configuration","backup","monitoring","quality"
]

USER_STYLES = [
"formal","simple","colloquial","typo_noisy","very_short","very_long","technical",
"beginner","expert","mixed_ar_en","directive","exploratory","urgent","polite",
"frustrated","corrective","decision_focused","result_only"
]

LANGUAGE_MODES = ["ar_fusha","ar_simple","ar_colloquial","en","mixed_ar_en","technical_mixed"]
DIFFICULTIES = ["basic","intermediate","advanced","expert","multi_stage"]
AMBIGUITIES = ["none","low","medium","high","dangerous"]
RISKS = ["none","low","medium","high","external_side_effect"]
FORMATS = ["answer","steps","code","patch","table","json","markdown","sources"]
TURN_PATTERNS = ["single","two_turn","three_turn","clarify","correction","project","tool_recovery","requirement_change","multi_intent","final_verification"]
REPAIR_STATES = ["clean","typo","missing_context","wrong_assumption","tool_failure","user_correction"]

AR_TOPIC = {
"python":"Python","javascript":"JavaScript","typescript":"TypeScript","react":"React",
"electron":"Electron","fastapi":"FastAPI","sqlite":"SQLite","postgresql":"PostgreSQL",
"git":"Git","github":"GitHub","windows":"Windows","linux":"Linux","android":"Android",
"firmware":"Firmware","security":"الأمن البرمجي","apis":"واجهات API","databases":"قواعد البيانات",
"rag":"RAG","llm":"النماذج اللغوية","transformers":"Transformers","lora":"LoRA",
"qlora":"QLoRA","gguf":"GGUF","evaluation":"التقييم","testing":"الاختبارات",
"performance":"الأداء","project_management":"إدارة المشاريع","documentation":"التوثيق",
"education":"التعليم","mathematics":"الرياضيات","statistics":"الإحصاء","translation":"الترجمة",
"technical_writing":"الكتابة التقنية","data_analysis":"تحليل البيانات","files":"الملفات",
"automation":"الأتمتة","deployment":"النشر","debugging":"تصحيح الأخطاء",
"architecture":"الهندسة المعمارية","user_interface":"واجهة المستخدم","memory":"الذاكرة",
"web_research":"البحث عبر الويب","citations":"المصادر والاستشهادات",
"model_lifecycle":"دورة حياة النموذج","configuration":"الإعدادات","backup":"النسخ الاحتياطي",
"monitoring":"المراقبة","quality":"جودة الإجابة"
}

def _choice(seq: list[str], n: int) -> str:
    return seq[n % len(seq)]


def _hash_id(seed: int, row: int, *parts: str) -> str:
    raw = "|".join([str(seed),str(row),*parts]).encode("utf-8")
    return "CI-V6.1-" + hashlib.sha256(raw).hexdigest()[:24]


def _user(topic: str, style: str, lang_mode: str, family: str, row: int) -> str:
    name = AR_TOPIC.get(topic, topic)
    ar = [
        f"أريد المساعدة في {name}. ما الطريقة الأفضل؟",
        f"عندي مشكلة في {name} وأريد حلاً عملياً خطوة بخطوة.",
        f"اشرح لي {name} بطريقة واضحة ثم أعطني مثالاً.",
        f"كمل العمل على {name} من حيث توقفنا.",
        f"عدّل الحل السابق في {name} بدون تغيير ما يعمل حالياً.",
        f"راجع النتيجة السابقة في {name} وتأكد من صحتها.",
        f"ابحث عن أحدث المعلومات المتعلقة بـ {name} واذكر المصادر.",
        f"ظهر خطأ في {name}. حدد السبب والحل وطريقة التحقق.",
    ]
    en = [
        f"I need help with {topic}. What is the best approach?",
        f"I have a problem with {topic}; give me a practical step-by-step fix.",
        f"Explain {topic} clearly and include an example.",
        f"Continue the previous work on {topic}.",
        f"Modify the previous {topic} solution without breaking working parts.",
        f"Review the previous result for {topic} and verify it.",
        f"Research the latest information about {topic} and cite sources.",
        f"A {topic} error occurred. Diagnose the cause, fix, and verification.",
    ]
    base = en[row % len(en)] if lang_mode=="en" else ar[row % len(ar)]
    if lang_mode in {"mixed_ar_en","technical_mixed"}:
        base = ar[row % len(ar)] + f" استخدم {topic} terminology where useful."
    if style=="very_short":
        return ["اشرحها","كمل","عدّلها","راجعها","حل المشكلة","ابحث عنها"][row % 6] + " في " + name
    if style=="typo_noisy":
        return base.replace("أ","ا").replace("إ","ا").replace("ة","ه").replace(" ", "  ", 1)
    if style=="directive":
        return base + " ولا تكتفِ بكلام عام."
    if style=="result_only":
        return base + " وأعطني النتيجة النهائية أولاً."
    if style=="expert":
        return base + " مع ذكر القيود والمخاطر ونقاط التحقق."
    if style=="beginner":
        return base + " أنا مبتدئ، فابدأ من الأساسيات."
    return base


def _assistant(topic: str, fmt: str, family: str, row: int) -> str:
    name = AR_TOPIC.get(topic, topic)
    opening = {
      "qa":f"سأجيب مباشرة عن {name} مع توضيح النقاط التي قد تؤثر في النتيجة.",
      "clarification":f"السياق الحالي لا يحدد الهدف في {name} بشكل كافٍ، لذا سأطلب متغيراً واحداً مؤثراً فقط.",
      "context_followup":f"سأربط الطلب بالسياق النشط السابق في {name} وأحافظ على القيود المتفق عليها.",
      "pronoun_resolution":f"سأفسر الإحالة إلى العنصر السابق في {name} من حالة الحوار قبل المتابعة.",
      "instruction_following":f"سأحوّل طلب {name} إلى مخرجات واضحة وألتزم بالتنسيق المطلوب.",
      "summarization":f"سأستخرج الأفكار الأساسية من مادة {name} وأحافظ على المعنى دون حشو.",
      "translation":f"سأترجم محتوى {name} مع الحفاظ على السياق والمصطلحات والنبرة.",
      "rewriting":f"سأعيد صياغة محتوى {name} مع الحفاظ على المعنى وتحسين البنية.",
      "comparison":f"سأقارن خيارات {name} وفق معايير واضحة ثم أعطي توصية مشروطة.",
      "recommendation":f"سأربط توصية {name} بالهدف والقيود بدلاً من اختيار عشوائي.",
      "planning":f"سأحوّل مهمة {name} إلى مراحل: فهم، تخطيط، تنفيذ، اختبار، تحقق.",
      "debugging":f"سأحدد أعراض مشكلة {name} ثم أرجع للسبب الأقرب وأقترح إصلاحاً قابلاً للتحقق.",
      "code_review":f"سأراجع {name} من ناحية الصحة والأمن والأداء والصيانة وقابلية الاختبار.",
      "project_build":f"سأتعامل مع مشروع {name} كمسار كامل من المتطلبات حتى الاختبار والإصدار.",
      "testing":f"سأبني اختبارات لـ {name} تشمل النجاح والفشل والحالات الحدية.",
      "web_research":f"سأبحث عن معلومات حديثة حول {name} وأربط الادعاءات بالمصادر المتاحة.",
      "fact_check":f"سأفصل الادعاء الخاص بـ {name} عن الأدلة ثم أعطي حكم التحقق وحدوده.",
      "memory":f"سأميز بين سياق الجلسة والذاكرة الدائمة عند التعامل مع {name}.",
      "correction_recovery":f"سأعتبر التصحيح إشارة لإعادة التحقق من الجزء المتأثر في {name} ثم أتابع من الحالة المصححة.",
      "safety_confirmation":f"قبل الإجراء عالي الأثر في {name} سأثبت الهدف والنطاق وأتحقق من الحاجة إلى موافقة صريحة.",
    }
    text = opening.get(family, f"سأتعامل مع طلب {name} وفق الهدف والسياق والقيود.")
    if fmt=="steps": text += " سأعرضه كخطوات مرتبة."
    elif fmt=="code": text += " وسأضع الكود في كتلة مستقلة."
    elif fmt=="table": text += " وسأستخدم جدولاً عندما يفيد المقارنة."
    elif fmt=="json": text += " وسأعيده بصيغة JSON صالحة."
    elif fmt=="sources": text += " وسأرفق المصادر في نفس الرد عند توفرها."
    return text


def build_record(seed: int, row: int) -> dict:
    family = _choice(FAMILIES, row * 7 + seed)
    topic = _choice(TOPICS, row * 11 + seed // 3)
    style = _choice(USER_STYLES, row * 13 + seed // 5)
    language = _choice(LANGUAGE_MODES, row * 17 + seed // 7)
    difficulty = _choice(DIFFICULTIES, row * 19 + seed // 11)
    ambiguity = _choice(AMBIGUITIES, row * 23 + seed // 13)
    risk = _choice(RISKS, row * 29 + seed // 17)
    fmt = _choice(FORMATS, row * 31 + seed // 19)
    turns = _choice(TURN_PATTERNS, row * 37 + seed // 23)
    repair = _choice(REPAIR_STATES, row * 41 + seed // 29)
    uid = _hash_id(seed,row,family,topic,style,language,difficulty,ambiguity,risk,fmt,turns,repair)

    user = _user(topic,style,language,family,row)
    assistant = _assistant(topic,fmt,family,row)

    messages = [
        {"role":"user","content":user},
        {"role":"assistant","content":assistant},
    ]
    if turns in {"two_turn","three_turn","clarify","correction","project","tool_recovery"}:
        messages.append({"role":"user","content":"المطلوب أن نكمل بناءً على النتيجة السابقة ونحافظ على القيود المهمة."})
    if turns in {"three_turn","project","tool_recovery"}:
        messages.append({"role":"assistant","content":"مفهوم. سأستعيد حالة المهمة، أفصل ما تم التحقق منه عما لم يتحقق، ثم أنفذ المرحلة التالية فقط."})
    if turns=="correction":
        messages.append({"role":"user","content":"النتيجة السابقة غير صحيحة. راجع الافتراض أو الخطوة التي سببت المشكلة."})
    if turns=="project":
        messages.append({"role":"user","content":"حوّل ذلك إلى خطة تنفيذ ثم اختبر كل مرحلة قبل إعلان اكتمالها."})
    if turns=="tool_recovery":
        messages.append({"role":"user","content":"حدث فشل في أداة التنفيذ؛ حافظ على الحالة الناجحة وأصلح الجزء المتأثر فقط."})
    if turns=="requirement_change":
        messages.append({"role":"user","content":"أضفت شرطًا جديدًا بعد بدء التنفيذ. حدّث الخطة والآثار المتأثرة ولا تهدم ما تحقق."})
    if turns=="multi_intent":
        messages.append({"role":"user","content":"لدي عدة أهداف في نفس الرسالة؛ رتبها إلى مراحل وحافظ على القيود المشتركة."})
    if turns=="final_verification":
        messages.append({"role":"user","content":"قبل التسليم النهائي، راجع المتطلبات والاختبارات والأدلة واذكر ما لم يتحقق."})
    if turns=="clarify":
        messages[0]["content"] += " ولا تفترض تفاصيل غير مذكورة."
    record = {
        "id":uid,
        "messages":messages,
        "metadata":{
            "generator_version":"6.1.0",
            "source":"synthetic_composition_v6_1",
            "seed":seed,
            "row":row,
            "family":family,
            "topic":topic,
            "user_style":style,
            "language_mode":language,
            "difficulty":difficulty,
            "ambiguity":ambiguity,
            "risk":risk,
            "output_format":fmt,
            "turn_pattern":turns,
            "repair_state":repair,
            "eligible_for_behavior_training":True,
            "synthetic":True,
        }
    }
    return record


def generate(count:int, seed:int, out_dir:Path, shard_size:int=100_000) -> dict:
    out_dir.mkdir(parents=True,exist_ok=True)
    shards=0
    generated=0
    seen=set()
    current=None
    fh=None
    try:
        for i in range(count):
            if i % shard_size == 0:
                if fh: fh.close()
                shards += 1
                current = out_dir / f"conversation_v6_{shards:04d}.jsonl"
                fh = current.open("w",encoding="utf-8")
            rec = build_record(seed,i)
            if rec["id"] in seen:
                raise RuntimeError(f"duplicate deterministic id at row {i}: {rec['id']}")
            seen.add(rec["id"])
            fh.write(json.dumps(rec,ensure_ascii=False,separators=(",",":"))+"\n")
            generated += 1
    finally:
        if fh: fh.close()
    manifest={
        "generator_version":"6.1.0",
        "seed":seed,
        "requested_count":count,
        "generated_count":generated,
        "unique_id_count":len(seen),
        "duplicate_id_count":generated-len(seen),
        "shard_count":shards,
        "schema":"conversation/messages + metadata",
    }
    (out_dir/"CORPUS_MANIFEST_V6.json").write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding="utf-8")
    return manifest


def main() -> int:
    ap=argparse.ArgumentParser()
    ap.add_argument("--count",type=int,default=10_000_000)
    ap.add_argument("--seed",type=int,default=6_061_007)
    ap.add_argument("--out",type=Path,default=Path("artifacts/conversation_corpus_v6"))
    ap.add_argument("--shard-size",type=int,default=100_000)
    args=ap.parse_args()
    if args.count < 1: raise SystemExit("--count must be >= 1")
    if args.shard_size < 1: raise SystemExit("--shard-size must be >= 1")
    m=generate(args.count,args.seed,args.out,args.shard_size)
    print(json.dumps(m,ensure_ascii=False))
    return 0


if __name__=="__main__":
    raise SystemExit(main())
