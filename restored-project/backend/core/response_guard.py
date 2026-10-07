# -*- coding: utf-8 -*-
"""Output normalization and quality guard for ALI.

The guard is conservative: it strips invisible/control corruption, normalizes
Unicode, detects collapsed repetition/gibberish, and lets the runtime fall back
to grounded knowledge when the model output is not trustworthy.
"""
from __future__ import annotations

import re
import unicodedata


def sanitize_output(text: str) -> str:
    text = unicodedata.normalize("NFKC", str(text or ""))
    cleaned = []
    for ch in text:
        cat = unicodedata.category(ch)
        if cat.startswith("C") and ch not in "\n\r\t":
            continue
        cleaned.append(ch)
    text = "".join(cleaned).replace("\r\n", "\n").replace("\r", "\n")
    # Remove repeated blank noise while preserving readable paragraphs.
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{4,}", "\n\n", text)
    return text.strip()


def _metrics(compact: str) -> dict:
    words = re.findall(r"\w+", compact, flags=re.UNICODE)
    lowered = [w.casefold() for w in words]
    counts = {}
    for w in lowered:
        counts[w] = counts.get(w, 0) + 1
    unique = len(counts)
    repetition = unique / max(1, len(words))
    max_frequency = max(counts.values(), default=0) / max(1, len(words))
    alpha = len(re.findall(r"[A-Za-z\u0600-\u06ff]", compact))
    controls = len(re.findall(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]", compact))
    mixed_script_tokens = [w for w in words if re.search(r"[A-Za-z]", w) and re.search(r"[\u0600-\u06ff]", w)]
    q_ar = bool(re.search(r"[\u0600-\u06ff]", compact))
    short_ratio = sum(1 for w in words if len(w) <= 2) / max(1, len(words))
    # One repeated token dominating the answer is a particularly strong collapse signal.
    dominant_repeat = max(counts.values(), default=0) >= 6 and max_frequency >= 0.22
    return {
        "chars": len(compact),
        "words": len(words),
        "unique_ratio": round(repetition, 3),
        "max_word_frequency": round(max_frequency, 3),
        "short_ratio": round(short_ratio, 3),
        "mixed_script_tokens": len(mixed_script_tokens),
        "controls": controls,
        "dominant_repeat": dominant_repeat,
        "language_ok": q_ar,
    }


def useful(text: str, query: str = "") -> tuple[bool, dict]:
    raw = str(text or "")
    if "�" in raw:
        return False, {"chars": len(raw), "words": 0, "reason": "replacement-character"}
    compact = sanitize_output(raw)
    meta = _metrics(compact)
    if not compact:
        meta["reason"] = "empty"
        return False, meta
    words = meta["words"]
    q_ar = bool(re.search(r"[\u0600-\u06ff]", str(query)))
    a_ar = bool(re.search(r"[\u0600-\u06ff]", compact))
    meta["language_ok"] = (not q_ar) or a_ar
    alpha = len(re.findall(r"[A-Za-z\u0600-\u06ff]", compact))
    ok = (
        meta["chars"] >= 6
        and alpha >= 3
        and meta["controls"] == 0
        and meta["unique_ratio"] >= 0.16
        and meta["max_word_frequency"] <= 0.42
        and not meta["dominant_repeat"]
        and (words < 8 or meta["short_ratio"] <= 0.50)
        and meta["mixed_script_tokens"] <= max(3, words // 8)
        and meta["language_ok"]
    )
    if not ok and "reason" not in meta:
        if meta["dominant_repeat"]:
            meta["reason"] = "collapsed-repetition"
        elif meta["controls"]:
            meta["reason"] = "control-corruption"
        elif not meta["language_ok"]:
            meta["reason"] = "language-mismatch"
        else:
            meta["reason"] = "quality-threshold"
    return ok, meta


def stream_safe(text: str, query: str = "") -> bool:
    """Return True only when a partial model stream is safe to expose in the UI."""
    raw = str(text or "")
    if not raw:
        return False
    if "�" in raw or re.search(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]", raw):
        return False
    compact = sanitize_output(raw)
    if not compact:
        return False
    meta = _metrics(compact)
    # Do not expose long collapsed/repeated fragments while the model is generating.
    if len(compact) >= 80 and (meta["dominant_repeat"] or meta["unique_ratio"] < 0.10 or meta["max_word_frequency"] > 0.55):
        return False
    if len(compact) >= 140 and meta["mixed_script_tokens"] > max(5, meta["words"] // 5):
        return False
    # Arabic answers with an unusually high proportion of one/two-character
    # tokens are a strong signal of the tokenizer-collapse/gibberish failure
    # seen in partially generated output. Do not expose the stream in that case.
    if len(compact) >= 140 and bool(re.search(r"[\u0600-\u06ff]", str(query or ""))) and meta["short_ratio"] > 0.58:
        return False
    if re.search(r"(?:\b(?:svg){3,}|(?:ent){3,}|(?:set){3,})", compact, re.I):
        return False
    return True


__all__ = ["sanitize_output", "useful", "stream_safe"]
