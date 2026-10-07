# -*- coding: utf-8 -*-
"""TokenizerConfig — إعدادات ALI Tokenizer.

تحتوي:
- نوع الخوارزمية (BPE حالياً).
- حجم الـ vocab المستهدف.
- min_frequency لزوج BPE قبل اعتماده.
- special tokens (مرتّبة لتحديد IDs بشكل deterministic).
- خيارات normalization للعربية.
- إعدادات pre-tokenization.

الـ config قابل للحفظ/التحميل كـ JSON.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import List


# ------------------------------------------------------------------
# الافتراضي
# ------------------------------------------------------------------
DEFAULT_SPECIAL_TOKENS: List[str] = [
    "<PAD>",
    "<BOS>",
    "<EOS>",
    "<UNK>",
    "<USER>",
    "<ASSISTANT>",
    "<SYSTEM>",
]


@dataclass
class TokenizerConfig:
    """إعدادات Tokenizer قابلة للتسلسل JSON."""

    type: str = "BPE"
    vocab_size: int = 4096
    min_frequency: int = 2

    # Special tokens (الترتيب يحدد الـ IDs: index 0 -> id 0).
    special_tokens: List[str] = field(
        default_factory=lambda: list(DEFAULT_SPECIAL_TOKENS)
    )

    # تطبيع العربية
    normalize_arabic: bool = True
    strip_diacritics: bool = True
    normalize_alef: bool = True       # إ/أ/آ -> ا
    normalize_yaa: bool = True        # ى -> ي
    normalize_taa_marbuta: bool = True # ة -> ه (مفعّل = آمن للنماذج)

    # Pre-tokenization
    lowercase_english: bool = True

    # End-of-word marker (GPT-2 style).
    # عند التدريب، أي token ليس في بداية الكلمة يُلحق بـ "</w>".
    use_end_of_word_marker: bool = True

    # إصدار الـ tokenizer
    version: str = "0.7.1"

    def __post_init__(self) -> None:
        """validation عند البناء."""
        if self.type not in ("BPE",):
            raise ValueError(f"unsupported tokenizer type: {self.type}")
        if self.vocab_size <= 0:
            raise ValueError("vocab_size must be positive")
        if self.min_frequency < 1:
            raise ValueError("min_frequency must be >= 1")
        if not self.special_tokens:
            raise ValueError("special_tokens cannot be empty")
        seen = set()
        for tok in self.special_tokens:
            if not tok:
                raise ValueError("empty string in special_tokens")
            if tok in seen:
                raise ValueError(f"duplicate special token: {tok!r}")
            seen.add(tok)
        # byte token prefixes must not collide with special tokens.
        for special in self.special_tokens:
            if special.startswith("<0x"):
                raise ValueError(
                    f"special token {special!r} starts with '<0x' "
                    f"(reserved for byte tokens)"
                )

    # ------------------------------------------------------------
    # Dict / JSON helpers
    # ------------------------------------------------------------
    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, d: dict) -> "TokenizerConfig":
        # تصفية المفاتيح الزائدة (forward-compat).
        known = {f for f in cls.__dataclass_fields__}
        clean = {k: v for k, v in d.items() if k in known}
        return cls(**clean)

    # ------------------------------------------------------------
    # Save / Load
    # ------------------------------------------------------------
    def save(self, path: Path) -> None:
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(self.to_dict(), f, ensure_ascii=False, indent=2)

    @classmethod
    def load(cls, path: Path) -> "TokenizerConfig":
        with open(path, "r", encoding="utf-8") as f:
            return cls.from_dict(json.load(f))


__all__ = ["TokenizerConfig", "DEFAULT_SPECIAL_TOKENS"]
