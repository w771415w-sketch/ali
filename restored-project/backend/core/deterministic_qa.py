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
