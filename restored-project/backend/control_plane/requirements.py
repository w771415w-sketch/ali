from __future__ import annotations
import re
from .schemas import Requirement, AcceptanceCriterion, ProjectContract, new_id

_AR = {
    "platform": ["سطح المكتب", "ويندوز", "ويب", "موقع", "جوال", "هاتف", "اندرويد", "ios", "أكثر من منصة", "offline", "اونلاين", "عبر الإنترنت"],
    "users": ["مستخدم", "موظف", "مدير", "عميل", "مورد"],
    "features": ["مخزون", "مبيعات", "مشتريات", "منتجات", "عملاء", "موردين", "تقارير", "فواتير", "تسجيل الدخول", "المستخدمين", "صلاحيات"],
    "performance": ["سريع", "ما يعلق", "لا يعلق", "خفيف", "أداء", "زمن الاستجابة"],
    "security": ["آمن", "أمان", "صلاحيات", "تشفير", "كلمة مرور", "توثيق", "مصادقة"],
}

def _has(text: str, words: list[str]) -> bool:
    t=text.casefold()
    return any(w.casefold() in t for w in words)

def _extract_features(text: str) -> list[str]:
    out=[]
    mapping={
        "مخزون":"Inventory","مبيعات":"Sales","مشتريات":"Purchases","منتجات":"Products",
        "عملاء":"Customers","موردين":"Suppliers","تقارير":"Reports","فواتير":"Invoices",
        "تسجيل الدخول":"Authentication","المستخدمين":"Users","صلاحيات":"Authorization",
    }
    for k,v in mapping.items():
        if k in text and v not in out: out.append(v)
    return out

def _platform(text: str) -> str | None:
    low=text.casefold()
    if any(x in low for x in ["سطح المكتب","windows","ويندوز","desktop"]): return "desktop"
    if any(x in low for x in ["ويب","موقع","web"]): return "web"
    if any(x in low for x in ["جوال","هاتف","android","اندرويد","ios"]): return "mobile"
    if "offline" in low or "بدون إنترنت" in low or "بدون اتصال" in low: return "offline"
    return None

def extract_contract(text: str, previous: ProjectContract | None = None) -> ProjectContract:
    base = previous or ProjectContract(goal=text.strip())
    if not previous: base.goal=text.strip()
    feats=_extract_features(text)
    for f in feats:
        if f not in base.features: base.features.append(f)
    plat=_platform(text)
    if plat: base.platform=plat
    if _has(text,_AR["performance"]) and "fast and responsive" not in base.constraints: base.constraints.append("fast and responsive")
    if _has(text,_AR["security"]) and "secure" not in base.constraints: base.constraints.append("secure")
    low=text.casefold()
    if "python" in low: base.language="Python"
    elif "javascript" in low or "typescript" in low: base.language="JavaScript/TypeScript"
    for role in ["owner","employees","customers","suppliers","موظفين","موظف","مدير"]:
        if role.casefold() in low and role not in base.users: base.users.append(role)
    existing={r.text for r in base.requirements}
    for f in base.features:
        phrase=f"Support {f}"
        if phrase not in existing: base.requirements.append(Requirement(new_id("req"), phrase, kind="must", confidence=0.85))
    if plat and f"Platform must be {plat}" not in existing: base.requirements.append(Requirement(new_id("req"),f"Platform must be {plat}",confidence=0.98))
    if base.language and f"Implementation language: {base.language}" not in existing: base.requirements.append(Requirement(new_id("req"),f"Implementation language: {base.language}",confidence=0.98))
    if _has(text,_AR["performance"]) and "Performance must be responsive" not in existing: base.requirements.append(Requirement(new_id("req"),"Performance must be responsive",kind="should",confidence=0.72))
    existing_ac={a.text for a in base.acceptance}
    templates={
        "Inventory":"Inventory balances update after stock movement",
        "Sales":"A sale changes inventory correctly","Purchases":"A purchase increases inventory correctly",
        "Products":"A product can be created and edited","Authentication":"Invalid credentials are rejected",
        "Authorization":"Restricted actions are denied to unauthorized roles","Reports":"A report can be generated from stored data",
    }
    for f in base.features:
        if f in templates and templates[f] not in existing_ac: base.acceptance.append(AcceptanceCriterion(new_id("ac"),templates[f]))
    if _has(text,["offline","بدون إنترنت","بدون اتصال"]) and _has(text,["عبر الإنترنت","اونلاين","online","من أي مكان"]):
        msg="Offline requirement conflicts with remote-online access"
        if msg not in base.conflicts: base.conflicts.append(msg)
    missing=[]
    if not base.platform: missing.append("platform")
    if not base.users and ("Users" in base.features or "Authentication" in base.features): missing.append("user roles and permissions")
    if not base.features: missing.append("core features")
    if not base.language and base.features: missing.append("implementation technology/language")
    base.missing=list(dict.fromkeys(missing)); base.complete=not base.missing and not base.conflicts and bool(base.acceptance or base.requirements)
    return base

def clarification_questions(contract: ProjectContract) -> list[str]:
    mapping={
        "platform":"هل تريد النظام سطح مكتب، ويب، جوال، أم أكثر من منصة؟",
        "user roles and permissions":"من المستخدمون وما الصلاحيات التي يمتلكها كل نوع؟",
        "core features":"ما الوظائف الأساسية التي تريدها في النسخة الأولى؟",
        "implementation technology/language":"هل لديك لغة أو تقنية مفضلة، أم تريد أن أختار ما يناسب الجهاز والمشروع؟",
    }
    return [mapping[x] for x in contract.missing if x in mapping]
