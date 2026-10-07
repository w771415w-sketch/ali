    p.add_argument("--keep-diacritics", action="store_true")
    p.add_argument("--no-alef-norm", action="store_true")
    p.add_argument("--no-yaa-norm", action="store_true")
    p.add_argument("--no-taa-norm", action="store_true")
    args = p.parse_args()

    # Add project root to path for module imports.
    project_root = Path(__file__).resolve().parent.parent
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))

    from tokenizer.config import TokenizerConfig
    from tokenizer.trainer import BPETrainer
    from tokenizer.serialization import save_tokenizer

    cfg = TokenizerConfig(
        vocab_size=args.vocab_size,
        min_frequency=args.min_freq,
        normalize_arabic=not args.no_arabic_norm,
        strip_diacritics=not args.keep_diacritics,
        normalize_alef=not args.no_alef_norm,
        normalize_yaa=not args.no_yaa_norm,
        normalize_taa_marbuta=not args.no_taa_norm,
    )

    print(f"[load] reading corpus from {args.input} (format={args.format})")
    t0 = time.time()
    corpus, stats = load_corpus(Path(args.input), args.format)
    t_load = time.time() - t0
    print(f"[load] {stats.as_dict()} in {t_load:.2f}s")
    if stats.invalid:
        print(
            f"[warn] {stats.invalid} invalid record(s) skipped",
            file=sys.stderr,
        )
    if stats.empty:
        print(
            f"[warn] {stats.empty} empty record(s) skipped",
            file=sys.stderr,
        )

    if not corpus:
        print("[error] no valid records to train on", file=sys.stderr)
        return 1

    print(f"[train] vocab_size={cfg.vocab_size} min_freq={cfg.min_frequency}")
    t0 = time.time()
    trainer = BPETrainer(cfg)
    vocab, merges = trainer.train(corpus)
    t_train = time.time() - t0
    print(f"[train] vocab={len(vocab)} merges={len(merges)} in {t_train:.2f}s")

    print(f"[save] writing to {args.output}")
    from tokenizer.tokenizer import ALITokenizer
    tok = ALITokenizer(cfg, vocab, merges)
    save_tokenizer(tok, Path(args.output))
    print(f"[done] {args.output}/{{config.json, vocab.json, merges.txt}}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
```

---

### `423/588` `backend/tokenizer/trainer.py`

- **المسار الكامل:** `F:\1f\p\ALI_Studio_Pro_Design4_4.6.0\04_Adaptive_Hybrid\backend/tokenizer/trainer.py`
- **الحجم:** 9688 بايت (9.5 KB)
- **الامتداد:** `.py`

```python
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
```

---

### `424/588` `backend/tokenizer/vocabulary.py`

- **المسار الكامل:** `F:\1f\p\ALI_Studio_Pro_Design4_4.6.0\04_Adaptive_Hybrid\backend/tokenizer/vocabulary.py`
- **الحجم:** 7079 بايت (6.9 KB)
- **الامتداد:** `.py`

```python
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
```

---

### `425/588` `backend/tools/__init__.py`

- **المسار الكامل:** `F:\1f\p\ALI_Studio_Pro_Design4_4.6.0\04_Adaptive_Hybrid\backend/tools/__init__.py`
- **الحجم:** 673 بايت (0.7 KB)
- **الامتداد:** `.py`

```python
# -*- coding: utf-8 -*-
"""tools/__init__.py — حزمة Tools.

تعريض الـ Registry كأهم عنصر عام.
"""

from tools.base import Tool, ToolResult, ToolPermission
from tools.registry import ToolRegistry, get_registry
from tools.filesystem import (
    ReadFileTool, ListDirTool, WriteFileTool, SearchFilesTool,
)
from tools.terminal import RunShellTool
from tools.git import GitStatusTool, GitDiffTool, GitCommitTool

__all__ = [
    "Tool", "ToolResult", "ToolPermission",
    "ToolRegistry", "get_registry",
    "ReadFileTool", "ListDirTool", "WriteFileTool", "SearchFilesTool",
    "RunShellTool",
    "GitStatusTool", "GitDiffTool", "GitCommitTool",
]
```

---

### `426/588` `backend/tools/base.py`

- **المسار الكامل:** `F:\1f\p\ALI_Studio_Pro_Design4_4.6.0\04_Adaptive_Hybrid\backend/tools/base.py`
- **الحجم:** 2592 بايت (2.5 KB)
- **الامتداد:** `.py`

```python
# -*- coding: utf-8 -*-
"""أدوات ALI Studio — الطبقة الأساسية.

كل Tool يجب أن يملك:
- name: اسم مميز (snake_case)
- description: وصف مختصر
- permission: مستوى الصلاحية (read-only / default / full-access)
- input_schema: dict يصف المعاملات (للـ UI / Agent)
- execute(ctx, **kwargs) -> ToolResult

الـ ToolResult يحتوي:
- ok: bool
- data: dict (output منظم)
- error: str | None
- error_code: str | None (PARSE / PATH_BLOCKED / IO_ERROR / DENIED ...)

لا يحتوي Tool على منطق permission check — ذلك مسؤولية PermissionManager
في security/permissions.py (يُحقن في الـ Registry).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, Optional


class ToolPermission(str, Enum):
    """مستوى الصلاحية المطلوب لتشغيل الأداة."""
    READ_ONLY = "read-only"        # قراءة فقط
    DEFAULT = "default"            # كتابة/تعديل يحتاج إذن المستخدم
    FULL_ACCESS = "full-access"    # تعديل/حذف يحتاج full-access


@dataclass
class ToolResult:
    """نتيجة موحدة من تنفيذ أي أداة."""
    ok: bool
    data: Dict[str, Any] = field(default_factory=dict)
    error: Optional[str] = None
    error_code: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "ok": self.ok,
            "data": self.data,
            "error": self.error,
            "error_code": self.error_code,
        }

    @staticmethod
    def ok_payload(**data: Any) -> "ToolResult":
        return ToolResult(ok=True, data=data)

    @staticmethod
    def fail(error: str, code: str = "ERROR", **data: Any) -> "ToolResult":
        return ToolResult(ok=False, data=data, error=error, error_code=code)


class Tool:
    """الفئة الأساسية للأداة. تُورث منها كل أداة."""
    name: str = ""
    description: str = ""
    permission: ToolPermission = ToolPermission.READ_ONLY
    input_schema: Dict[str, Any] = {}

    def execute(self, ctx: Any, **kwargs: Any) -> ToolResult:
        """يجب أن يُنفّذ في subclasses."""
        raise NotImplementedError

    # اختياري: فحص الـ input قبل التنفيذ.
    def validate_input(self, kwargs: Dict[str, Any]) -> Optional[str]:
        """يرجع None إذا الـ input سليم، أو رسالة خطأ."""
        return None


__all__ = ["Tool", "ToolResult", "ToolPermission"]
```

---

### `427/588` `backend/tools/filesystem.py`

- **المسار الكامل:** `F:\1f\p\ALI_Studio_Pro_Design4_4.6.0\04_Adaptive_Hybrid\backend/tools/filesystem.py`
- **الحجم:** 8488 بايت (8.3 KB)
- **الامتداد:** `.py`

```python
# -*- coding: utf-8 -*-
"""أدوات Filesystem: read_file, list_dir, write_file, search_files.

تحترم حدود الـ project_dir (workspace). أي محاولة للخروج تُرفض بـ PATH_BLOCKED.
"""

from __future__ import annotations

import os
import re
from pathlib import Path
from typing import Any, List

from tools.base import Tool, ToolResult, ToolPermission
from security.paths import safe_project_path


# حد أقصى لقراءة ملف — يحمي من OOM على ملفات ضخمة.
MAX_FILE_BYTES = 2 * 1024 * 1024    # 2 MiB
MAX_LIST_ENTRIES = 1000
MAX_SEARCH_RESULTS = 200


class ReadFileTool(Tool):
    name = "read_file"
    description = "قراءة محتوى ملف داخل workspace."
    permission = ToolPermission.READ_ONLY
    input_schema = {
        "type": "object",
        "properties": {
            "path": {"type": "string", "description": "مسار نسبي للملف"},
            "max_bytes": {"type": "integer", "description": "حد أقصى للقراءة"},
        },
        "required": ["path"],
    }

    def execute(self, ctx: Any, **kwargs: Any) -> ToolResult:
        rel = kwargs.get("path", "")
        if not rel:
            return ToolResult.fail("path is required", code="PARSE")
        try:
            resolved = safe_project_path(ctx.project_dir, rel)
        except PermissionError as e:
            return ToolResult.fail(str(e), code="PATH_BLOCKED")

        if not resolved.exists():
            return ToolResult.fail("file not found: " + str(resolved),
                                    code="NOT_FOUND")
        if not resolved.is_file():
            return ToolResult.fail("not a file: " + str(resolved),
                                    code="NOT_A_FILE")

        limit = int(kwargs.get("max_bytes", MAX_FILE_BYTES))
        try:
            size = resolved.stat().st_size
            with open(resolved, "rb") as f:
                raw = f.read(limit + 1)
            truncated = len(raw) > limit
            if truncated:
                raw = raw[:limit]
            try:
                text = raw.decode("utf-8")
            except UnicodeDecodeError:
                text = raw.decode("utf-8", "replace")
            return ToolResult.ok_payload(
                path=str(resolved),
                content=text,
                size=size,
                truncated=truncated,
                bytes_read=len(raw),
            )
        except OSError as e:
            return ToolResult.fail(str(e), code="IO_ERROR")


class ListDirTool(Tool):
    name = "list_dir"
    description = "سرد محتويات مجلد داخل workspace."
    permission = ToolPermission.READ_ONLY
    input_schema = {
        "type": "object",
        "properties": {
            "path": {"type": "string", "description": "مسار نسبي للمجلد"},
        },
        "required": [],
    }

    def execute(self, ctx: Any, **kwargs: Any) -> ToolResult:
        rel = kwargs.get("path", "")
        try:
            resolved = safe_project_path(ctx.project_dir, rel)
        except PermissionError as e:
            return ToolResult.fail(str(e), code="PATH_BLOCKED")
        if not resolved.exists():
            return ToolResult.fail("not found: " + str(resolved),
                                    code="NOT_FOUND")
        if not resolved.is_dir():
            return ToolResult.fail("not a directory: " + str(resolved),
                                    code="NOT_A_DIR")

        try:
            entries: List[dict] = []
            for p in sorted(resolved.iterdir()):
                if len(entries) >= MAX_LIST_ENTRIES:
                    break
                st = p.stat()
                entries.append({
                    "name": p.name,
                    "is_dir": p.is_dir(),
                    "size": st.st_size,
                })
            return ToolResult.ok_payload(
                path=str(resolved),
                entries=entries,
                truncated=len(entries) >= MAX_LIST_ENTRIES,
            )
        except OSError as e:
            return ToolResult.fail(str(e), code="IO_ERROR")


class WriteFileTool(Tool):
    """كتابة ملف كامل (overwrite). يحتاج Permission DEFAULT+."""
    name = "write_file"
    description = "كتابة ملف داخل workspace (يستبدل المحتوى)."
    permission = ToolPermission.DEFAULT
    input_schema = {
        "type": "object",
        "properties": {
            "path": {"type": "string", "description": "مسار نسبي للملف"},
            "content": {"type": "string", "description": "المحتوى الكامل"},
        },
        "required": ["path", "content"],
    }

    def execute(self, ctx: Any, **kwargs: Any) -> ToolResult:
        rel = kwargs.get("path", "")
        content = kwargs.get("content", "")
        if not rel:
            return ToolResult.fail("path is required", code="PARSE")
        try:
            resolved = safe_project_path(ctx.project_dir, rel)
        except PermissionError as e:
            return ToolResult.fail(str(e), code="PATH_BLOCKED")
        try:
            resolved.parent.mkdir(parents=True, exist_ok=True)
            with open(resolved, "w", encoding="utf-8", newline="") as f:
                f.write(content)
            return ToolResult.ok_payload(path=str(resolved),
                                         bytes_written=len(content.encode("utf-8")))
        except OSError as e:
            return ToolResult.fail(str(e), code="IO_ERROR")


class SearchFilesTool(Tool):
    """بحث regex داخل ملفات المشروع."""
    name = "search_files"
    description = "بحث regex داخل الملفات النصية داخل workspace."
    permission = ToolPermission.READ_ONLY
    input_schema = {
        "type": "object",
        "properties": {
            "pattern": {"type": "string", "description": "regex pattern"},
            "path": {"type": "string", "description": "مجلد بداية (نسبي)"},
        },
        "required": ["pattern"],
    }

    _SKIP_DIRS = {".git", "__pycache__", "node_modules", ".venv", "venv",
                  "checkpoints", "weights", ".pytest_cache"}

    def execute(self, ctx: Any, **kwargs: Any) -> ToolResult:
        pattern = kwargs.get("pattern", "")
        rel = kwargs.get("path", "")
        if not pattern:
            return ToolResult.fail("pattern is required", code="PARSE")
        try:
            rx = re.compile(pattern)
        except re.error as e:
            return ToolResult.fail("invalid regex: " + str(e), code="PARSE")
        try:
            base = safe_project_path(ctx.project_dir, rel)
        except PermissionError as e:
            return ToolResult.fail(str(e), code="PATH_BLOCKED")

        results: List[dict] = []
        try:
            for root, dirs, files in os.walk(base):
                # prune skip-dirs
                dirs[:] = [d for d in dirs if d not in self._SKIP_DIRS]
                for fn in files:
                    if len(results) >= MAX_SEARCH_RESULTS:
                        break
                    p = Path(root) / fn
                    try:
                        if p.stat().st_size > MAX_FILE_BYTES:
                            continue
                    except OSError:
                        continue
                    try:
                        with open(p, "r", encoding="utf-8",
                                  errors="replace") as f:
                            for ln, line in enumerate(f, 1):
                                if rx.search(line):
                                    results.append({
                                        "path": str(p),
                                        "line": ln,
                                        "text": line.rstrip(),
                                    })
                                    if len(results) >= MAX_SEARCH_RESULTS:
                                        break
                    except (OSError, UnicodeDecodeError):
                        continue
                if len(results) >= MAX_SEARCH_RESULTS:
                    break
            return ToolResult.ok_payload(
                pattern=pattern,
                matches=results,
                truncated=len(results) >= MAX_SEARCH_RESULTS,
            )
        except Exception as e:
            return ToolResult.fail(str(e), code="IO_ERROR")


__all__ = ["ReadFileTool", "ListDirTool", "WriteFileTool", "SearchFilesTool"]
```

---

### `428/588` `backend/tools/gguf.py`

- **المسار الكامل:** `F:\1f\p\ALI_Studio_Pro_Design4_4.6.0\04_Adaptive_Hybrid\backend/tools/gguf.py`
- **الحجم:** 4678 بايت (4.6 KB)
- **الامتداد:** `.py`

```python
# -*- coding: utf-8 -*-
"""GGUF conversion, validation and local llama.cpp bridge."""
from __future__ import annotations
from pathlib import Path
import subprocess, os, hashlib, json, struct
from typing import Dict,Any

class GGUFManager:
    def __init__(self,llama_dir:str|Path="vendor/llama.cpp"):
        self.root=Path(llama_dir)
    def converter(self):
        for n in ("convert_hf_to_gguf.py","convert-hf-to-gguf.py"):
            p=self.root/n
            if p.exists(): return p
        return None
    def quantizer(self):
        for n in ("llama-quantize.exe","llama-quantize","quantize.exe","quantize"):
            for b in (self.root,self.root/"build"/"bin",self.root/"bin"):
                p=b/n
                if p.exists():return p
        for p in self.root.glob("**/llama-quantize*"):
            if p.is_file() and p.suffix.lower() in {"",".exe"}:return p
        return None
    def server(self):
        for n in ("llama-server.exe","llama-server"):
            for b in (self.root,self.root/"build"/"bin",self.root/"bin"):
                p=b/n
                if p.exists():return p
        return None
    def cli(self):
        for n in ("llama-cli.exe","llama-cli"):
            for b in (self.root,self.root/"build"/"bin",self.root/"bin"):
                p=b/n
                if p.exists():return p
        return None
    def _sha256(self,path):
        h=hashlib.sha256(); p=Path(path)
        with p.open("rb") as f:
            for b in iter(lambda:f.read(1024*1024),b""):h.update(b)
        return h.hexdigest()
    def _write_sidecar(self,path,meta):
        p=Path(path); data=dict(meta,sha256=self._sha256(p),size=p.stat().st_size); p.with_suffix(p.suffix+".json").write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding="utf-8")
    def validate(self,path:str|Path)->Dict[str,Any]:
        p=Path(path); out={"path":str(p),"exists":p.exists(),"size":0,"magic":False,"version":None,"valid":False}
        if not p.exists():return out
        out["size"]=p.stat().st_size
        if out["size"]<24:return out
        with p.open("rb") as f:
            out["magic"]=f.read(4)==b"GGUF"
            if out["magic"]:
                raw=f.read(4); out["version"]=struct.unpack("<I",raw)[0] if len(raw)==4 else None
                out["valid"]=out["version"] in {1,2,3,4}
        return out
    def convert(self,hf_dir,outfile,outtype="f16"):
        conv=self.converter()
        if not conv:raise FileNotFoundError(f"llama.cpp converter not found: {self.root}")
        hf=Path(hf_dir); out=Path(outfile); out.parent.mkdir(parents=True,exist_ok=True)
        cmd=[os.environ.get("PYTHON",os.sys.executable),str(conv),str(hf),"--outfile",str(out),"--outtype",str(outtype)]
        p=subprocess.run(cmd,capture_output=True,text=True,timeout=3600,cwd=str(self.root))
        if p.returncode!=0:raise RuntimeError((p.stderr or p.stdout)[-6000:])
        check=self.validate(out)
        if not check["valid"]:raise RuntimeError("Converter returned success but GGUF validation failed")
        meta={"path":str(out),"format":"GGUF","outtype":outtype,"validation":check,"stdout":p.stdout[-4000:]}; self._write_sidecar(out,meta); return meta
    def quantize(self,src,dst,ftype="Q4_K_M"):
        q=self.quantizer()
        if not q:raise FileNotFoundError("llama-quantize not found in vendor/llama.cpp")
        src=Path(src); dst=Path(dst); dst.parent.mkdir(parents=True,exist_ok=True)
        p=subprocess.run([str(q),str(src),str(dst),ftype],capture_output=True,text=True,timeout=3600,cwd=str(self.root))
        if p.returncode!=0:raise RuntimeError((p.stderr or p.stdout)[-6000:])
        check=self.validate(dst)
        if not check["valid"]:raise RuntimeError("Quantizer returned success but GGUF validation failed")
        meta={"path":str(dst),"quantization":ftype,"validation":check,"stdout":p.stdout[-4000:]}; self._write_sidecar(dst,meta); return meta
    def check(self):return {"llama_dir":str(self.root.resolve()),"converter":str(self.converter() or ""),"quantizer":str(self.quantizer() or ""),"llama_cli":str(self.cli() or ""),"llama_server":str(self.server() or "")}
    def run(self,model,prompt,max_tokens=256,temperature=.7):
        cli=self.cli()
        if not cli:raise FileNotFoundError("llama-cli not found in vendor/llama.cpp")
        p=subprocess.run([str(cli),"-m",str(model),"-p",prompt,"-n",str(max_tokens),"--temp",str(temperature),"--no-display-prompt","--no-show-timings"],capture_output=True,text=True,timeout=3600)
        if p.returncode!=0:raise RuntimeError((p.stderr or p.stdout)[-6000:])
        return {"text":p.stdout,"model":str(model),"max_tokens":max_tokens,"temperature":temperature}
```

---

### `429/588` `backend/tools/git.py`

- **المسار الكامل:** `F:\1f\p\ALI_Studio_Pro_Design4_4.6.0\04_Adaptive_Hybrid\backend/tools/git.py`
- **الحجم:** 3675 بايت (3.6 KB)
- **الامتداد:** `.py`

```python
# -*- coding: utf-8 -*-
"""أدوات Git: status, diff, commit.

- git_status: read-only — يعرض حالة الـ repo.
- git_diff:   read-only — يعرض التعديلات.
- git_commit: default — يحتاج إذن صريح.
"""

from __future__ import annotations

import subprocess
from typing import Any