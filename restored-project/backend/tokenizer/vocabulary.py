# -*- coding: utf-8 -*-
"""Vocabulary — token <-> id mapping مع validation ودeterminism.

التعريفات:
- id 0..N-1: special tokens (بالترتيب المحدد في Config).
- id N..M-1: base chars (UTF-8 bytes لكل char) — تُضاف تلقائياً قبل BPE.
- id M..: BPE merges بالترتيب الذي تُنتجه Trainer.

يضمن:
- لا duplicate IDs.
- لا empty tokens.
- JSON round-trip deterministic (ترتيب ثابت).
- access سريع O(1) في الاتجاهين.
"""

from __future__ import annotations

import json
from collections import OrderedDict
from pathlib import Path
from typing import Dict, Iterable, List, Tuple


class Vocabulary:
    """token -> id / id -> token mappings.

    الـ token يمكن أن يحتوي أي Unicode (بما فيه whitespace, "</w>" marker,
    multi-byte chars) — نخزّنها كما هي بدون escape.
    """

    __slots__ = ("_token_to_id", "_id_to_token")

    def __init__(self) -> None:
        # OrderedDict لضمان ترتيب ثابت عند الإخراج.
        self._token_to_id: "OrderedDict[str, int]" = OrderedDict()
        self._id_to_token: Dict[int, str] = {}

    # ------------------------------------------------------------------ size
    def __len__(self) -> int:
        return len(self._token_to_id)

    # ------------------------------------------------------------------ add
    def add(self, token: str) -> int:
        """إضافة token إذا لم يكن موجوداً. يرجع الـ id."""
        if not token:
            raise ValueError("cannot add empty token")
        existing = self._token_to_id.get(token)
        if existing is not None:
            return existing
        new_id = len(self._token_to_id)
        self._token_to_id[token] = new_id
        self._id_to_token[new_id] = token
        return new_id

    def add_many(self, tokens: Iterable[str]) -> List[int]:
        return [self.add(t) for t in tokens]

    # ------------------------------------------------------------------ lookup
    def token_to_id(self, token: str, default: int | None = None) -> int:
        return self._token_to_id.get(token, default)

    def id_to_token(self, id_: int, default: str | None = None) -> str:
        return self._id_to_token.get(id_, default)

    def contains(self, token: str) -> bool:
        return token in self._token_to_id

    def has_id(self, id_: int) -> bool:
        return id_ in self._id_to_token

    # ------------------------------------------------------------------ iterate
    def tokens(self) -> List[str]:
        return list(self._token_to_id.keys())

    def ids(self) -> List[int]:
        return list(self._id_to_token.keys())

    def items(self) -> List[Tuple[str, int]]:
        return list(self._token_to_id.items())

    # ------------------------------------------------------------------ validate
    def validate(self, *, reserved_count: int | None = None,
                 required_tokens: list[str] | None = None) -> None:
        """يرفع ValueError إذا الـ vocabulary غير صالح.

        يفحص:
        - لا token فارغ.
        - كل ID فريد.
        - كل ID متطابق في forward/reverse maps.
        - IDs contiguous من 0 إلى len-1 (لا فراغات).
        - إذا reserved_count معطى، الـ IDs [0..reserved_count-1] كلها
          يجب أن تكون tokens محفوظة (specials).
        - إذا required_tokens معطى، كل token منها يجب أن يكون في vocab.
        """
        n = len(self._token_to_id)
        if n != len(self._id_to_token):
            raise ValueError(
                f"vocab inconsistency: {n} forward vs "
                f"{len(self._id_to_token)} reverse"
            )
        seen_ids: set = set()
        seen_tokens: set = set()
        for tok, tid in self._token_to_id.items():
            if not tok:
                raise ValueError("empty token in vocab")
            if tok in seen_tokens:
                raise ValueError(f"duplicate token {tok!r}")
            seen_tokens.add(tok)
            if tid in seen_ids:
                raise ValueError(f"duplicate id {tid} for token {tok!r}")
            seen_ids.add(tid)
            if not (0 <= tid < n):
                raise ValueError(
                    f"id {tid} out of contiguous range [0, {n}) for {tok!r}"
                )
            if self._id_to_token[tid] != tok:
                raise ValueError(
                    f"reverse mismatch at id {tid}: "
                    f"forward={tok!r} reverse={self._id_to_token[tid]!r}"
                )
        # Contiguous check.
        if set(self._id_to_token.keys()) != set(range(n)):
            missing = set(range(n)) - set(self._id_to_token.keys())
            raise ValueError(
                f"non-contiguous ids: missing {sorted(missing)[:10]}"
            )
        # Reserved check (specials should occupy 0..reserved-1).
        if reserved_count is not None and reserved_count > 0:
            for i in range(reserved_count):
                tok = self._id_to_token.get(i)
                if tok is None:
                    raise ValueError(
                        f"reserved slot {i} empty (specials must be "
                        f"contiguous at the start)"
                    )
        # Required tokens check.
        if required_tokens:
            for tok in required_tokens:
                if tok not in self._token_to_id:
                    raise ValueError(f"required token {tok!r} missing")

    # ------------------------------------------------------------------ serialization
    def to_dict(self) -> Dict[str, int]:
        return dict(self._token_to_id)

    @classmethod
    def from_dict(cls, d: Dict[str, int]) -> "Vocabulary":
        v = cls()
        # ترتيب حسب الـ id عند الإدخال (يضمن deterministic).
        items = sorted(d.items(), key=lambda kv: kv[1])
        for tok, tid in items:
            if v._token_to_id.get(tok) == tid:
                continue
            if tok in v._token_to_id:
                raise ValueError(f"duplicate token in vocab: {tok!r}")
            if tid in v._id_to_token:
                raise ValueError(f"duplicate id in vocab: {tid}")
            v._token_to_id[tok] = tid
            v._id_to_token[tid] = tok
        v.validate()
        return v

    def save_json(self, path: Path) -> None:
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        # حفظ كـ {token: id} بترتيب الـ id (مفيد للقراءة البشرية).
        sorted_items = sorted(self._token_to_id.items(),
                              key=lambda kv: kv[1])
        with open(path, "w", encoding="utf-8") as f:
            json.dump({k: v for k, v in sorted_items},
                      f, ensure_ascii=False, indent=2)

    @classmethod
    def load_json(cls, path: Path) -> "Vocabulary":
        with open(path, "r", encoding="utf-8") as f:
            return cls.from_dict(json.load(f))


__all__ = ["Vocabulary"]
