# -*- coding: utf-8 -*-
"""BPE Trainer — Byte Pair Encoding من الصفر (Python خالص).

المسار:
    1) corpus: Iterable[str] (List أو generator)
    2) pre-tokenize -> List[List[str]] من الكلمات
    3) تهيئة vocab بـ: special tokens + base chars (UTF-8 bytes)
    4) تكرار حتى vocab_size أو لا مزيد من الـ merges:
       - حساب bigram counts
       - اختيار أعلى bigram (lex tie-break)
       - تسجيل merge (a, b) -> ab
       - تطبيق الـ merge على كل الكلمات
       - إضافة ab للـ vocab
    5) إرجاع: Vocabulary + List[Tuple[str, str]] merges

ملاحظات:
- GPT-2 style: نستخدم end-of-word marker "</w>".
- Base chars = كل UTF-8 byte (0..255) لضمان تغطية كاملة لأي نص.
- deterministic: ترتيب الـ merges حسب (frequency desc, lex asc).
- streaming: يقبل Iterable[str] (generator friendly).
"""

from __future__ import annotations

import re
from collections import Counter
from typing import Dict, Iterable, List, Tuple

from tokenizer.config import TokenizerConfig
from tokenizer.vocabulary import Vocabulary


# Pre-tokenization regex: يفصل حسب:
# - whitespace (يُلتهم)
# - كلمات Latin
# - أرقام
# - كلمات عربية (Unicode range)
# - أي رمز آخر (حرف حرفاً)
_PRETOKEN_RE = re.compile(
    r"""
    \s+                                |   # whitespace
    [A-Za-z]+(?:['_-][A-Za-z]+)*       |   # كلمات Latin (مع hyphen/underscore داخلي)
    [0-9]+                             |   # أرقام
    [\u0600-\u06FF]+                   |   # Arabic block (الحروف الأساسية)
    [\u0750-\u077F]+                   |   # Arabic Supplement
    [\uFB50-\uFDFF]+                   |   # Arabic Presentation Forms-A
    [\uFE70-\uFEFF]+                   |   # Arabic Presentation Forms-B
    [^\sA-Za-z0-9]                         # أي رمز آخر (حرفاً حرفاً)
    """,
    re.VERBOSE | re.UNICODE,
)


def _utf8_bytes() -> List[str]:
    """قائمة كل UTF-8 byte كـ token: 256 رمز."""
    return [f"<0x{b:02X}>" for b in range(256)]


def pretokenize(text: str) -> List[str]:
    """تقسيم النص إلى كلمات قبل BPE.

    الـ whitespace يُعالَج بشكل منفصل في tokenizer.encode عبر
    _split_text_into_runs لضمان lossless preservation.
    """
    if not text:
        return []
    return _PRETOKEN_RE.findall(text)


def _word_to_symbols(word: str, use_eow: bool) -> Tuple[str, ...]:
    """تحويل كلمة إلى tuple من الـ symbols (UTF-8 bytes).

    الـ symbols دائماً byte tokens ('<0xFF>').
    إذا use_eow=True، آخر byte يُلحق بـ '</w>'.
    """
    raw = word.encode("utf-8")
    if not use_eow:
        return tuple(f"<0x{b:02X}>" for b in raw)
    syms = [f"<0x{b:02X}>" for b in raw]
    if not syms:
        return tuple()
    syms[-1] = syms[-1] + "</w>"
    return tuple(syms)


def _is_valid_byte_token(tok: str) -> bool:
    """هل هذا byte token صالح؟

    يقبل byte token واحد ('<0xFF>' بطول 6) أو مدمج ('<0xAA><0xBB>...').
    يقبل أيضاً end-of-word marker '<0xAA><0xBB></w>'.
    """
    if not tok.startswith("<0x"):
        return False
    if not (tok.endswith(">") or tok.endswith("</w>")):
        return False
    if tok.endswith("</w>"):
        base = tok[: -len("</w>")]
    else:
        base = tok
    if len(base) < 6 or (len(base) - 6) % 6 != 0:
        return False
    i = 0
    while i < len(base):
        if base[i:i + 3] != "<0x":
            return False
        if base[i + 5] != ">":
            return False
        try:
            int(base[i + 3:i + 5], 16)
        except ValueError:
            return False
        i += 6
    return True


def _merge_to_token(a: str, b: str) -> str | None:
    """دمج token strings مع الحفاظ على </w> في النهاية.

    الـ merges يجب أن تكون byte-only tokens (يبدأ بـ '<0x').
    الـ </w> marker (إن وُجد) ينتقل للنهاية دائماً.
    """
    if not (_is_valid_byte_token(a) and _is_valid_byte_token(b)):
        return None
    a_has_eow = a.endswith("</w>")
    b_has_eow = b.endswith("</w>")
    a_body = a[: -len("</w>")] if a_has_eow else a
    b_body = b[: -len("</w>")] if b_has_eow else b
    merged_body = a_body + b_body
    if a_has_eow or b_has_eow:
        return merged_body + "</w>"
    return merged_body


class BPETrainer:
    """يحوّل corpus إلى Vocabulary + merges.

    يقبل `Iterable[str]` (List أو generator) لكن الـ BPE algorithm نفسه
    يحتاج `word_freqs` كاملاً في الذاكرة (هذا قيد BPE الكلاسيكي).

    Memory model:
        corpus → iterate once → word_freqs (Counter, in-memory) →
        → words (Dict[Tuple[symbols], freq]) → merges (List) → vocab

    لا يوجد streaming حقيقي في BPE — نحتاج statistics كاملة قبل أي merge.
    لكن الـ iteration على corpus نفسه stream-friendly (لا يحوّل لـ list).
    """

    def __init__(self, config: TokenizerConfig) -> None:
        self.config = config

    # ----------------------------------------------------------- public
    def train(self, corpus: Iterable[str]) -> Tuple[Vocabulary, List[Tuple[str, str]]]:
        """التدريب. يرجع (vocabulary, merges).

        corpus: Iterable[str] — List أو generator.
        """
        cfg = self.config

        vocab = Vocabulary()
        # 1) special tokens أولاً (تحديد IDs 0..N-1).
        for tok in cfg.special_tokens:
            if not tok:
                raise ValueError("empty special token in config")
            vocab.add(tok)
        if len(vocab) != len(set(cfg.special_tokens)):
            raise ValueError("duplicate special tokens in config")

        # 2) base chars (UTF-8 bytes).
        for byte_tok in _utf8_bytes():
            vocab.add(byte_tok)

        # 3) Pre-tokenize + بناء word_freqs (streaming).
        word_freqs: Counter = Counter()
        seen_any = False
        for text in corpus:
            seen_any = True
            if not isinstance(text, str):
                continue
            for word in pretokenize(text):
                word_freqs[word] += 1

        if not seen_any:
            raise ValueError("empty corpus (no texts provided)")
        if not word_freqs:
            vocab.validate(reserved_count=len(cfg.special_tokens))
            return vocab, []

        # 4) تحويل كل كلمة إلى symbols.
        words: Dict[Tuple[str, ...], int] = {}
        all_symbols: set = set()
        for word, freq in word_freqs.items():
            symbols = _word_to_symbols(word, cfg.use_end_of_word_marker)
            words[symbols] = words.get(symbols, 0) + freq
            for sym in symbols:
                all_symbols.add(sym)
        for sym in all_symbols:
            if sym not in vocab._token_to_id:
                vocab.add(sym)

        merges: List[Tuple[str, str]] = []

        # 5) BPE iterations.
        target = cfg.vocab_size
        max_merges = target - len(vocab)
        if max_merges <= 0:
            vocab.validate(reserved_count=len(cfg.special_tokens))
            return vocab, merges

        existing = set(vocab.tokens())

        for _ in range(max_merges):
            # حساب bigram counts مع frequency weighting.
            pairs: Counter = Counter()
            for symbols, freq in words.items():
                if len(symbols) < 2:
                    continue
                for i in range(len(symbols) - 1):
                    pairs[(symbols[i], symbols[i + 1])] += freq
            if not pairs:
                break

            # اختيار الأكثر تكراراً، مع tie-break lex على الـ pair.
            best_pair, best_count = max(
                pairs.items(),
                key=lambda kv: (kv[1], kv[0])
            )
            if best_count < cfg.min_frequency:
                break

            new_token = _merge_to_token(best_pair[0], best_pair[1])
            if new_token is None:
                # merge غير صالح (نظرياً لا يحدث إذا الـ symbols كلها bytes).
                break
            if new_token not in existing:
                vocab.add(new_token)
                existing.add(new_token)

            # تطبيق الـ merge على كل الكلمات.
            new_words: Dict[Tuple[str, ...], int] = {}
            a, b = best_pair
            for symbols, freq in words.items():
                if len(symbols) < 2 or a not in symbols:
                    new_words[symbols] = new_words.get(symbols, 0) + freq
                    continue
                merged: List[str] = []
                i = 0
                while i < len(symbols):
                    if (i < len(symbols) - 1
                            and symbols[i] == a
                            and symbols[i + 1] == b):
                        merged.append(new_token)
                        i += 2
                    else:
                        merged.append(symbols[i])
                        i += 1
                key = tuple(merged)
                new_words[key] = new_words.get(key, 0) + freq
            words = new_words
            merges.append(best_pair)

            if len(vocab) >= target:
                break

        vocab.validate(reserved_count=len(cfg.special_tokens))
        return vocab, merges


__all__ = ["BPETrainer", "pretokenize",
           "_word_to_symbols", "_is_valid_byte_token", "_merge_to_token"]
