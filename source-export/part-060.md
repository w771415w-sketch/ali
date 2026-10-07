
def _atomic_write_text(path: Path, text: str, encoding: str = "utf-8") -> None:
    _atomic_write_bytes(path, text.encode(encoding))


# ------------------------------------------------------------------
# Hashes
# ------------------------------------------------------------------
def _file_hash(path: Path) -> str:
    """SHA-256 of file content (hex digest)."""
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


# ------------------------------------------------------------------
# Merges I/O
# ------------------------------------------------------------------
def save_merges(merges: List[Tuple[str, str]], path: Path) -> None:
    path = Path(path)
    lines = [
        "# ALI Studio — BPE merges",
        "# version: 1",
        "# format: <a> <b>",
    ]
    for a, b in merges:
        lines.append(f"{a} {b}")
    _atomic_write_text(path, "\n".join(lines) + "\n")


def load_merges(path: Path) -> List[Tuple[str, str]]:
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(str(path))
    out: List[Tuple[str, str]] = []
    line_no = 0
    with open(path, "r", encoding="utf-8") as f:
        for raw in f:
            line_no += 1
            line = raw.rstrip("\n\r")
            if not line or line.startswith("#"):
                continue
            parts = line.split(" ")
            if len(parts) != 2:
                raise ValueError(
                    f"invalid merge line at {path}:{line_no}: {line!r}"
                )
            a, b = parts
            if not (a.startswith("<0x") and a.endswith(">")):
                raise ValueError(
                    f"merge LHS not byte token at {path}:{line_no}: {a!r}"
                )
            if not (b.startswith("<0x") and (b.endswith(">") or b.endswith("</w>"))):
                raise ValueError(
                    f"merge RHS not byte token at {path}:{line_no}: {b!r}"
                )
            out.append((a, b))
    return out


# ------------------------------------------------------------------
# Tokenizer I/O
# ------------------------------------------------------------------
def save_tokenizer(tokenizer: ALITokenizer, root: Path) -> None:
    """Save tokenizer artifact with atomic writes + manifest.

    Writes:
        config.json
        vocab.json
        merges.txt
        manifest.json (with SHA-256 hashes of the above three files)
    """
    paths = TokenizerPaths(root)
    paths.root.mkdir(parents=True, exist_ok=True)
    tokenizer.config.save(paths.config)
    tokenizer.vocab.save_json(paths.vocab)
    save_merges(tokenizer.merges, paths.merges)
    # Manifest
    manifest = {
        "tokenizer_version": TOKENIZER_VERSION,
        "algorithm": ALGORITHM,
        "vocab_size": len(tokenizer.vocab),
        "merge_count": len(tokenizer.merges),
        "special_token_count": len(tokenizer.config.special_tokens),
        "special_tokens": list(tokenizer.config.special_tokens),
        "config_hash": _file_hash(paths.config),
        "vocab_hash": _file_hash(paths.vocab),
        "merges_hash": _file_hash(paths.merges),
    }
    _atomic_write_text(
        paths.manifest,
        json.dumps(manifest, indent=2, ensure_ascii=False) + "\n",
    )


def _validate_tokenizer(tokenizer: ALITokenizer) -> None:
    """Full integrity check: vocab + merges + required specials + byte base.

    Checks (بالترتيب):
        1) Vocabulary: contiguous IDs, reserved_count, required_tokens.
        2) كل merge LHS موجود في vocab.
        3) كل merge RHS موجود في vocab.
        4) كل merge OUTPUT موجود في vocab.
        5) merge output = a + b هو byte-only valid (مع أو بدون </w>).
        6) merge order: merge #i output يجب أن يكون قد أُضيف قبل أو عند #i.
           (نتحقق أنه موجود في vocab الآن — لكن لا نضمن ترتيب زمني.)
    """
    # 1) Vocabulary strict.
    tokenizer.vocab.validate(
        reserved_count=len(tokenizer.config.special_tokens),
        required_tokens=tokenizer.config.special_tokens
                       + [f"<0x{b:02X}>" for b in range(256)],
    )

    # 2/3/4) merge operands + output in vocab.
    from tokenizer.trainer import _is_valid_byte_token
    for i, (a, b) in enumerate(tokenizer.merges):
        # LHS exists.
        if not tokenizer.vocab.contains(a):
            raise ValueError(f"merge #{i} LHS {a!r} not in vocab")
        # RHS exists.
        if not tokenizer.vocab.contains(b):
            raise ValueError(f"merge #{i} RHS {b!r} not in vocab")
        # Output = a + b. يجب أن يكون في vocab.
        output = a + b
        if not tokenizer.vocab.contains(output):
            raise ValueError(
                f"merge #{i} output {output!r} not in vocab "
                f"(LHS={a!r}, RHS={b!r})"
            )
        # Output should be parseable byte-only (مع أو بدون </w>).
        if not _is_valid_byte_token(output):
            # Exception: لو a ينتهي بـ </w>، الـ merged يكون a_body + b + </w>
            # والذي هو _is_valid_byte_token(a_body + b + </w>) — يفحص body.
            # الـ logic صحيح. لكن لو a لا ينتهي بـ </w> و b ينتهي → نفس الشيء.
            # لو كلاهما بدون </w> → body = a + b (no </w>) → يفحص كـ base bytes.
            # Edge case: لو merged شيء آخر — raise.
            raise ValueError(
                f"merge #{i} produces malformed token: {output!r}"
            )


def load_tokenizer(root: Path) -> ALITokenizer:
    """تحميل tokenizer مع validation كامل + manifest integrity check."""
    paths = TokenizerPaths(root)
    if not paths.exists():
        missing = paths.which_missing()
        raise FileNotFoundError(
            f"tokenizer not found at {paths.root} (missing: {missing})"
        )
    config = TokenizerConfig.load(paths.config)
    vocab = Vocabulary.load_json(paths.vocab)
    merges = load_merges(paths.merges)
    tok = ALITokenizer(config, vocab, merges)
    # Strict integrity validation.
    _validate_tokenizer(tok)
    # Manifest: اختياري (لا نفشل إذا غير موجود — backward-compat).
    if paths.manifest.exists():
        try:
            manifest = json.loads(paths.manifest.read_text(encoding="utf-8"))
            # تحقق من تطابق الـ hashes (إذا البيانات المحفوظة تطابق).
            current_hashes = {
                "config_hash": _file_hash(paths.config),
                "vocab_hash": _file_hash(paths.vocab),
                "merges_hash": _file_hash(paths.merges),
            }
            for key, expected in [
                ("config_hash", manifest.get("config_hash")),
                ("vocab_hash", manifest.get("vocab_hash")),
                ("merges_hash", manifest.get("merges_hash")),
            ]:
                if expected and expected != current_hashes[key]:
                    raise ValueError(
                        f"manifest mismatch for {key}: "
                        f"expected {expected[:12]}..., got {current_hashes[key][:12]}..."
                    )
            # Algorithm check.
            if manifest.get("algorithm") != ALGORITHM:
                raise ValueError(
                    f"manifest algorithm mismatch: "
                    f"{manifest.get('algorithm')} != {ALGORITHM}"
                )
        except json.JSONDecodeError as e:
            raise ValueError(f"manifest.json is malformed: {e}") from e
    return tok


__all__ = [
    "TokenizerPaths",
    "save_tokenizer", "load_tokenizer",
    "save_merges", "load_merges",
    "TOKENIZER_VERSION", "ALGORITHM",
]
```

---

### `420/588` `backend/tokenizer/spm.py`

- **المسار الكامل:** `F:\1f\p\ALI_Studio_Pro_Design4_4.6.0\04_Adaptive_Hybrid\backend/tokenizer/spm.py`
- **الحجم:** 2495 بايت (2.4 KB)
- **الامتداد:** `.py`

```python
# -*- coding: utf-8 -*-
"""SentencePiece tokenizer trained locally for ALI's decoder model."""
from __future__ import annotations
from pathlib import Path
import json, os, re

SPECIAL = ['<pad>','<s>','</s>','<|system|>','<|user|>','<|assistant|>','<|eot|>']

class AliTokenizer:
    def __init__(self, model_path:str|Path):
        import sentencepiece as spm
        self.model_path=Path(model_path); self.sp=spm.SentencePieceProcessor(model_file=str(self.model_path))
    @property
    def vocab_size(self): return int(self.sp.get_piece_size())
    @property
    def bos_id(self): return int(self.sp.bos_id())
    @property
    def eos_id(self): return int(self.sp.eos_id())
    @property
    def pad_id(self): return int(self.sp.pad_id())
    def special_id(self,piece:str)->int:return int(self.sp.piece_to_id(piece))
    def encode(self,text:str,add_bos=True,add_eos=True):
        ids=self.sp.encode(text,out_type=int); return ([self.bos_id] if add_bos else [])+ids+([self.eos_id] if add_eos else [])
    def decode(self,ids): return self.sp.decode(list(map(int,ids)))

def train_sentencepiece(input_files:list[str]|str, output_dir:str|Path, vocab_size:int=4096, character_coverage:float=0.9995)->Path:
    import sentencepiece as spm
    out=Path(output_dir); out.mkdir(parents=True,exist_ok=True); prefix=out/'tokenizer'; files=','.join(input_files) if isinstance(input_files,list) else str(input_files); vocab_size=max(512,int(vocab_size))
    spm.SentencePieceTrainer.Train(input=files,model_prefix=str(prefix),vocab_size=vocab_size,model_type='unigram',character_coverage=character_coverage,bos_id=1,eos_id=2,unk_id=0,pad_id=3, user_defined_symbols='<|system|>,<|user|>,<|assistant|>,<|eot|>',normalization_rule_name='nmt_nfkc',remove_extra_whitespaces=False,byte_fallback=True,hard_vocab_limit=False)
    (out/'tokenizer_config.json').write_text(json.dumps({'model_type':'llama','add_bos_token':True,'add_eos_token':False,'bos_token':'<s>','eos_token':'</s>','pad_token':'<pad>','unk_token':'<unk>','chat_template':"<s>{% for message in messages %}<|{{ message['role'] }}|>\n{{ message['content'] }}<|eot|>\n{% endfor %}<|assistant|>\n"} ,ensure_ascii=False,indent=2),encoding='utf-8')
    (out/'special_tokens_map.json').write_text(json.dumps({'bos_token':'<s>','eos_token':'</s>','pad_token':'<pad>','unk_token':'<unk>','additional_special_tokens':['<|system|>','<|user|>','<|assistant|>','<|eot|>']},ensure_ascii=False,indent=2),encoding='utf-8')
    return out/'tokenizer.model'
```

---

### `421/588` `backend/tokenizer/tokenizer.py`

- **المسار الكامل:** `F:\1f\p\ALI_Studio_Pro_Design4_4.6.0\04_Adaptive_Hybrid\backend/tokenizer/tokenizer.py`
- **الحجم:** 23187 بايت (22.6 KB)
- **الامتداد:** `.py`

```python
# -*- coding: utf-8 -*-
"""ALITokenizer — واجهة Encode/Decode مع contract صارم.

============================================================
PUBLIC API (مستقر لـ V0.8):
============================================================
    tok.encode(text, add_bos, add_eos, special_tokens) -> List[int]
    tok.decode(ids, skip_special) -> str
    tok.normalize(text) -> str         # contract صريح لـ normalization
    tok.save(path)                     # يكتب config.json + vocab.json + merges.txt + manifest.json
    tok.vocab_size                     # int
    tok.special_tokens                 # Dict[str, int]  (name -> id)
    tok.pad_id, tok.bos_id, tok.eos_id, tok.unk_id  # int
    tok.token_to_id(token, default)    # int
    tok.id_to_token(id_, default)      # str
    tok.is_special_token(token)        # bool
    tok.is_byte_token(token)           # bool

    ALITokenizer.load(path) -> ALITokenizer  # classmethod

============================================================
WORD-BOUNDARY CONTRACT (الخيار A):
============================================================
الـ `</w>` هو internal BPE representation:
- لا يظهر أبداً في الـ IDs النهائية بعد encode/decode (round-trip
  lossless عند إيقاف normalization).
- يحفظ في vocab فقط كـ metadata لتدريب BPE + discriminator.
- في decode: bytes الـ word تُجمَّع، تُفك، ثم تُلصق بدون `</w>`.
- في encode fallback: `</w>` يضيع (loss في الـ boundary metadata،
  لا في الـ bytes).

============================================================
NORMALIZATION CONTRACT:
============================================================
1) Exact mode (normalize_arabic=False, lowercase_english=False):
       decode(encode(text)) == text       (للـ bytes الـ UTF-8 كاملة)

2) Normalized mode (defaults):
       decode(encode(text)) == normalize(text)

   normalize(text) = يُطبّق:
     - NFC + Arabic normalizations (opt-in per flag)
     - lowercase_latin (Latin فقط)
   normalize() كدالة عامة متاحة عبر tok.normalize(text).

============================================================
SPECIAL TOKENS CONTRACT:
============================================================
- special_tokens تُعرَّف في TokenizerConfig.special_tokens (list[str]).
- IDs ثابتة في 0..N-1 (validation في Vocabulary.validate).
- عند encode(special_tokens=True) (default)، أي ظهور للسلسلة الحرفية
  الكاملة لأحد الـ special tokens داخل النص → يُستبدل بـ special ID
  تلقائياً (لا يتفكك لـ bytes).
- النص الذي يبدأ بـ "<" وينتهي بـ ">" لكن ليس في الـ special_tokens
  list → يُعامل كنص عادي (byte tokens).

============================================================
WHITESPACE CONTRACT:
============================================================
كل whitespace char (space=0x20, tab=0x09, newline=0x0A, cr=0x0D)
يُرمَّز كـ byte token منفصل، ثم يُجمَّع ويُفك في decode.
- " ".join(pieces) ممنوع في decode.
- round-trip lossless في exact mode.
"""

from __future__ import annotations

import unicodedata
from typing import Dict, List, Sequence, Set, Tuple

from tokenizer.config import TokenizerConfig
from tokenizer.vocabulary import Vocabulary
from tokenizer.trainer import _is_valid_byte_token


# ------------------------------------------------------------------
# Normalization
# ------------------------------------------------------------------
_ARABIC_DIACRITICS = frozenset({
    "\u064B", "\u064C", "\u064D", "\u064E", "\u064F",
    "\u0650", "\u0651", "\u0652", "\u0653", "\u0654",
    "\u0655", "\u0656", "\u0657", "\u0658",
    "\u0670",  # superscript alef
})


def normalize_arabic_text(text: str,
                          strip_diacritics: bool,
                          normalize_alef: bool,
                          normalize_yaa: bool,
                          normalize_taa_marbuta: bool) -> str:
    """تطبيع النص العربي — irreversible (lossy).

    لتجنب الفقد، استخدم normalize_arabic=False في الـ config.
    """
    if not text:
        return text
    s = unicodedata.normalize("NFC", text)
    if strip_diacritics:
        s = "".join(c for c in s if c not in _ARABIC_DIACRITICS)
    if normalize_alef:
        s = s.replace("\u0623", "\u0627")
        s = s.replace("\u0622", "\u0627")
        s = s.replace("\u0625", "\u0627")
    if normalize_yaa:
        s = s.replace("\u0649", "\u064A")
    if normalize_taa_marbuta:
        s = s.replace("\u0629", "\u0647")
    return s


def _lowercase_latin(text: str) -> str:
    """lowercase لـ Latin chars فقط (Arabic يبقى كما هو)."""
    out = []
    for c in text:
        if "A" <= c <= "Z":
            out.append(c.lower())
        else:
            out.append(c)
    return "".join(out)


def _byte_token_str(b: int) -> str:
    """byte → token string '<0xFF>'."""
    return f"<0x{b:02X}>"


def _extract_byte_values(token_str: str) -> List[int]:
    """استخراج bytes من token string (مدمج أو مفرد).

    يقبل: '<0xAA>', '<0xAA></w>', '<0xAA><0xBB>', '<0xAA><0xBB></w>'.
    """
    out: List[int] = []
    i = 0
    n = len(token_str)
    body_end = n
    if token_str.endswith("</w>"):
        body_end = n - len("</w>")
    while i + 6 <= body_end:
        if token_str[i:i + 3] != "<0x" or token_str[i + 5] != ">":
            return []   # malformed → empty (caller treats as UNK)
        try:
            out.append(int(token_str[i + 3:i + 5], 16))
        except ValueError:
            return []
        i += 6
    if i != body_end:
        return []
    return out


def _split_text_into_runs(text: str) -> List[Tuple[str, str]]:
    """قسّم النص إلى runs: ('word', text) أو ('space', chars).

    الـ whitespace يظهر في 'space' كحرف منفصل لكل byte (lossless).
    """
    out: List[Tuple[str, str]] = []
    word_buf: List[str] = []
    space_buf: List[str] = []

    def flush_word() -> None:
        if word_buf:
            out.append(("word", "".join(word_buf)))
            word_buf.clear()

    def flush_space() -> None:
        if space_buf:
            out.append(("space", "".join(space_buf)))
            space_buf.clear()

    for c in text:
        if c.isspace():
            flush_word()
            space_buf.append(c)
        else:
            flush_space()
            word_buf.append(c)
    flush_word()
    flush_space()
    return out


# ------------------------------------------------------------------
# Special Token Parsing
# ------------------------------------------------------------------
def _find_special_token_at(text: str, pos: int,
                            special_set: Set[str]) -> Tuple[int, str] | None:
    """ابحث عن special token في text بدءاً من pos.

    Returns: (length, token_string) أو None إذا لم يُعثر.
    """
    for tok in special_set:
        if text.startswith(tok, pos):
            return len(tok), tok
    return None


def _emit_units(text: str, special_set: Set[str]) -> List[Tuple[str, str]]:
    """قسّم النص إلى units: ('special', token_string) أو ('char', chars).

    'char' يجمع consecutive chars (لا special token) في run واحد.
    """
    out: List[Tuple[str, str]] = []
    i = 0
    n = len(text)
    char_buf: List[str] = []

    def flush_chars() -> None:
        if char_buf:
            out.append(("char", "".join(char_buf)))
            char_buf.clear()

    while i < n:
        found = _find_special_token_at(text, i, special_set)
        if found is not None:
            flush_chars()
            length, tok = found
            out.append(("special", tok))
            i += length
        else:
            char_buf.append(text[i])
            i += 1
    flush_chars()
    return out


# ------------------------------------------------------------------
# Main Tokenizer
# ------------------------------------------------------------------
class ALITokenizer:
    """Tokenizer BPE مع دعم عربي + lossless byte-level."""

    def __init__(self, config: TokenizerConfig, vocab: Vocabulary,
                 merges: Sequence[Tuple[str, str]] | None = None) -> None:
        self.config = config
        self.vocab = vocab
        self.merges: List[Tuple[str, str]] = list(merges or [])
        self._merge_rank: Dict[Tuple[str, str], int] = {
            pair: i for i, pair in enumerate(self.merges)
        }
        # روابط سريعة
        self._unk_id = vocab.token_to_id("<UNK>")
        self._bos_id = vocab.token_to_id("<BOS>")
        self._eos_id = vocab.token_to_id("<EOS>")
        self._pad_id = vocab.token_to_id("<PAD>")
        self._user_id = vocab.token_to_id("<USER>")
        self._assistant_id = vocab.token_to_id("<ASSISTANT>")
        self._system_id = vocab.token_to_id("<SYSTEM>")
        if self._unk_id is None or self._pad_id is None:
            raise ValueError("vocab missing <UNK> or <PAD>")
        # Sanity: vocab must contain all 256 byte tokens for byte fallback.
        for b in range(256):
            if vocab.token_to_id(_byte_token_str(b)) is None:
                raise ValueError(
                    f"vocab missing base byte token {_byte_token_str(b)}; "
                    f"lossless decode impossible"
                )
        # Precompute special token strings → IDs.
        self._special_to_id: Dict[str, int] = {}
        for st in config.special_tokens:
            tid = vocab.token_to_id(st)
            if tid is None:
                raise ValueError(f"special token {st!r} not in vocab")
            self._special_to_id[st] = tid
        # Special tokens as set for fast lookup.
        # بعد lowercase normalization، الـ special tokens قد تكون lowercase
        # (e.g. '<USER>' → '<user>'). لذا نضيف نسختين: original + lowercased
        # (Latin chars only).
        self._special_set: Set[str] = set(config.special_tokens)
        for st in config.special_tokens:
            self._special_set.add(_lowercase_latin(st))

    # ==========================================================
    # PUBLIC API
    # ==========================================================

    # ---------------- normalize ----------------
    def normalize(self, text: str) -> str:
        """تطبيق نفس normalization الذي سيُطبَّق في encode.

        Contract:
            decode(encode(text)) == normalize(text)
            (في exact mode: normalize(text) == text)
        """
        if not text:
            return text
        if self.config.normalize_arabic:
            text = normalize_arabic_text(
                text,
                strip_diacritics=self.config.strip_diacritics,
                normalize_alef=self.config.normalize_alef,
                normalize_yaa=self.config.normalize_yaa,
                normalize_taa_marbuta=self.config.normalize_taa_marbuta,
            )
        if self.config.lowercase_english:
            text = _lowercase_latin(text)
        return text

    # ---------------- encode ----------------
    def encode(self, text: str,
               add_bos: bool = False,
               add_eos: bool = False,
               special_tokens: bool = True) -> List[int]:
        """Encode text → IDs.

        Parameters:
            text: النص المُدخَل.
            add_bos: إضافة <BOS> في البداية.
            add_eos: إضافة <EOS> في النهاية.
            special_tokens: استبدال special token strings في النص بـ IDs.

        Returns:
            list of int IDs.

        Algorithm:
            1) normalize(text)
            2) split text into a sequence of (kind, value) units where
               kind ∈ {special, char_run}.
               char_run = consecutive chars (لا special).
               special = special token string.
            3) لكل char_run: حوّل إلى byte tokens + </w>، طبّق BPE،
               حوّل إلى IDs مع byte fallback.
            4) لكل special: ضيف الـ special ID مباشرة (لا BPE).
            5) add_bos/add_eos → IDs في البداية/النهاية.
        """
        if not text:
            ids: List[int] = []
            if add_bos:
                ids.append(self._bos_id)
            if add_eos:
                ids.append(self._eos_id)
            return ids

        # 1) Normalize.
        text = self.normalize(text)

        # 2) Split into (kind, value) sequence.
        units: List[Tuple[str, str]]
        if special_tokens:
            units = _emit_units(text, self._special_set)
        else:
            units = [("char", text)]

        # 3,4) لكل unit: IDs.
        ids = []
        if add_bos:
            ids.append(self._bos_id)
        for kind, value in units:
            if kind == "special":
                # إذا الـ value lowercase (post-normalization) → map إلى
                # special token الأصلي (case-insensitive).
                original = self._resolve_special_token(value)
                if original is None:
                    # لا mapping → نُعامل كنص عادي (نادر، يحدث فقط
                    # إذا الـ special_token كان معدّل بعد lowercase).
                    symbols = self._chars_to_byte_symbols(value)
                    bpe_symbols = self._apply_bpe(symbols)
                    for sym in bpe_symbols:
                        tid = self.vocab.token_to_id(sym, default=None)
                        if tid is None:
                            ids.extend(self._byte_fallback(sym))
                        else:
                            ids.append(tid)
                else:
                    ids.append(self._special_to_id[original])
            else:
                # char run → byte tokens → BPE → IDs.
                symbols = self._chars_to_byte_symbols(value)
                bpe_symbols = self._apply_bpe(symbols)
                for sym in bpe_symbols:
                    tid = self.vocab.token_to_id(sym, default=None)
                    if tid is None:
                        ids.extend(self._byte_fallback(sym))
                    else:
                        ids.append(tid)
        if add_eos:
            ids.append(self._eos_id)
        return ids

    def _resolve_special_token(self, matched: str) -> str | None:
        """Map matched special token (lowercased) إلى canonical name."""
        if matched in self._special_to_id:
            return matched
        # lowercase version → original.
        for original in self._special_to_id:
            if _lowercase_latin(original) == matched:
                return original
        return None

    def _chars_to_byte_symbols(self, chars: str) -> List[str]:
        """تحويل string من chars إلى list of byte symbol tokens + eow."""
        symbols: List[str] = []
        if not chars:
            return symbols
        raw_bytes = chars.encode("utf-8")
        for b in raw_bytes:
            symbols.append(_byte_token_str(b))
        if self.config.use_end_of_word_marker and symbols \
                and not symbols[-1].endswith("</w>"):
            symbols[-1] = symbols[-1] + "</w>"
        return symbols

    # ---------------- decode ----------------
    def decode(self, ids: Sequence[int], skip_special: bool = True) -> str:
        """Decode IDs → text.

        Strategy:
            - byte tokens → accumulate bytes
            - special tokens → skip (default) أو emit literal
            - unk → '?'
            - في النهاية: flush bytes، decode UTF-8 (errors='replace')
        """
        if not ids:
            return ""

        pieces: List[str] = []
        buf: bytearray = bytearray()

        def flush() -> None:
            if not buf:
                return
            pieces.append(bytes(buf).decode("utf-8", errors="replace"))
            buf.clear()

        for tid in ids:
            tok = self.vocab.id_to_token(int(tid))
            if tok is None:
                flush()
                pieces.append("?")
                continue
            if skip_special and self.is_special_token(tok):
                flush()
                continue
            if tok.endswith("</w>"):
                base = tok[: -len("</w>")]
                values = _extract_byte_values(base)
                if not values:
                    # malformed token → UNK placeholder
                    flush()
                    pieces.append("?")
                    continue
                buf.extend(values)
                flush()
                continue
            if self.is_byte_token(tok):
                values = _extract_byte_values(tok)
                if not values:
                    flush()
                    pieces.append("?")
                    continue
                buf.extend(values)
                continue
            # literal token (special emitted via skip_special=False).
            flush()
            pieces.append(tok)

        flush()
        return "".join(pieces)

    # ---------------- save / load ----------------
    def save(self, path) -> None:
        """احفظ الـ tokenizer (config + vocab + merges + manifest) بشكل ذرّي."""
        from tokenizer.serialization import save_tokenizer
        save_tokenizer(self, Path_safe(path))

    @classmethod
    def load(cls, path) -> "ALITokenizer":
        """تحميل tokenizer مع validation كامل."""
        from tokenizer.serialization import load_tokenizer
        return load_tokenizer(Path_safe(path))

    # ==========================================================
    # Convenience API (proxy لـ Vocabulary)
    # ==========================================================

    @property
    def vocab_size(self) -> int:
        """int: حجم الـ vocabulary (شامل special + base bytes + merges)."""
        return len(self.vocab)

    @property
    def num_merges(self) -> int:
        """int: عدد الـ merges."""
        return len(self.merges)

    @property
    def special_tokens(self) -> Dict[str, int]:
        """dict: special token string → id (مرآة للـ config)."""
        return dict(self._special_to_id)

    @property
    def pad_id(self) -> int:
        return self._pad_id if self._pad_id is not None else -1

    @property
    def bos_id(self) -> int:
        return self._bos_id if self._bos_id is not None else -1

    @property
    def eos_id(self) -> int:
        return self._eos_id if self._eos_id is not None else -1

    @property
    def unk_id(self) -> int:
        return self._unk_id if self._unk_id is not None else -1

    @property
    def user_id(self) -> int:
        return self._user_id if self._user_id is not None else -1

    @property
    def assistant_id(self) -> int:
        return self._assistant_id if self._assistant_id is not None else -1

    @property
    def system_id(self) -> int:
        return self._system_id if self._system_id is not None else -1

    def token_to_id(self, token: str, default: int | None = None) -> int | None:
        return self.vocab.token_to_id(token, default=default)

    def id_to_token(self, id_: int, default: str | None = None) -> str | None:
        return self.vocab.id_to_token(id_, default=default)

    def is_special_token(self, token: str) -> bool:
        """هل هذا token من الـ special tokens؟"""
        return token in self._special_to_id

    def is_byte_token(self, token: str) -> bool:
        """هل هذا token byte token (مفرد '<0xFF>' أو مدمج '<0xAA><0xBB>...')؟"""
        return _is_valid_byte_token(token)

    # ==========================================================
    # Internals
    # ==========================================================
    def _byte_fallback(self, token: str) -> List[int]:
        """تفكيك token مفقود في vocab → base byte IDs.

        الـ token يجب أن يكون byte token (validated by caller).
        إذا فشل التحليل (malformed) → UNK placeholder.
        الـ `</w>` marker يضيع (word-boundary metadata، لا bytes).
        """
        values = _extract_byte_values(token)
        if not values:
            # malformed → UNK
            return [self._unk_id]
        return [self.vocab.token_to_id(_byte_token_str(v), default=self._unk_id)
                for v in values]

    def _apply_bpe(self, symbols: List[str]) -> List[str]:
        """تطبيق BPE merges بالترتيب بدون انفجار زمني على النصوص الطويلة.

        BPETrainer لا ينشئ merges عبر whitespace لأن pretokenize يفصل الـ whitespace
        قبل التدريب. لذلك يمكننا تقسيم سلسلة الرموز عند whitespace bytes ثم تطبيق
        الخوارزمية على كل مقطع مستقل. هذا يحافظ على نفس النتيجة تماماً، ويمنع
        المسح التربيعي O(n²) الذي كان يجعل نصاً طويلاً جداً بطيئاً بشكل غير مقبول.
        """
        if len(symbols) < 2:
            return list(symbols)

        rank = self._merge_rank
        whitespace = {"<0x09>", "<0x0A>", "<0x0D>", "<0x20>"}

        def merge_segment(segment: List[str]) -> List[str]:
            if len(segment) < 2:
                return list(segment)
            work = list(segment)
            # Every successful merge reduces the sequence length by one, so at most
            # len(segment)-1 successful merges can occur.
            while len(work) >= 2:
                best_rank = None
                best_i = -1
                for i in range(len(work) - 1):
                    r = rank.get((work[i], work[i + 1]))
                    if r is not None and (best_rank is None or r < best_rank):
                        best_rank = r
                        best_i = i
                if best_rank is None:
                    break
                work = work[:best_i] + [work[best_i] + work[best_i + 1]] + work[best_i + 2:]
            return work

        out: List[str] = []
        segment: List[str] = []
        for sym in symbols:
            if sym in whitespace:
                if segment:
                    out.extend(merge_segment(segment))
                    segment.clear()
                out.append(sym)
            else:
                segment.append(sym)
        if segment:
            out.extend(merge_segment(segment))
        return out


# ------------------------------------------------------------------
# Helpers (used by save/load)
# ------------------------------------------------------------------
def Path_safe(p):
    """Helper: تحويل str|Path → Path بدون imports إضافية في module-level."""
    from pathlib import Path as _P
    return _P(p) if not isinstance(p, _P) else p


__all__ = [
    "ALITokenizer",
    "normalize_arabic_text",
    "Path_safe",
]
```

---

### `422/588` `backend/tokenizer/train_tokenizer.py`

- **المسار الكامل:** `F:\1f\p\ALI_Studio_Pro_Design4_4.6.0\04_Adaptive_Hybrid\backend/tokenizer/train_tokenizer.py`
- **الحجم:** 6279 بايت (6.1 KB)
- **الامتداد:** `.py`

```python
#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""CLI لتدريب ALI Tokenizer من ملف corpus.

الاستخدام:
    python -m tokenizer.train_tokenizer \\
        --input data/raw/corpus.txt \\
        --output weights/tokenizer \\
        --vocab-size 4096 \\
        --min-freq 2

أو من ملف JSONL (حقل "text"):
    python -m tokenizer.train_tokenizer \\
        --input data/raw/corpus.jsonl \\
        --format jsonl \\
        --output weights/tokenizer

يقبل ملفات .txt و .jsonl.
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path
from typing import List, Tuple


# ------------------------------------------------------------------
# Corpus loaders with explicit counts
# ------------------------------------------------------------------
class CorpusStats:
    """Counts لـ corpus: total/valid/invalid/empty records."""

    def __init__(self) -> None:
        self.total = 0
        self.valid = 0
        self.invalid = 0
        self.empty = 0

    def as_dict(self) -> dict:
        return {
            "total_lines": self.total,
            "valid_records": self.valid,
            "invalid_records": self.invalid,
            "empty_records": self.empty,
        }


def load_corpus_txt(path: Path, stats: CorpusStats) -> List[str]:
    out: List[str] = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            stats.total += 1
            s = line.strip()
            if not s:
                stats.empty += 1
                continue
            out.append(s)
            stats.valid += 1
    return out


def load_corpus_jsonl(path: Path, stats: CorpusStats,
                      warn_every: int = 1000) -> List[str]:
    """JSONL كل سطر = {text: '...'} (الحقول الأخرى مهملة)."""
    out: List[str] = []
    invalid_since_warn = 0
    with open(path, "r", encoding="utf-8") as f:
        for line_no, raw in enumerate(f, 1):
            stats.total += 1
            line = raw.strip()
            if not line:
                stats.empty += 1
                continue
            try:
                obj = json.loads(line)
            except json.JSONDecodeError as e:
                stats.invalid += 1
                invalid_since_warn += 1
                if invalid_since_warn <= 5 or invalid_since_warn % warn_every == 0:
                    print(
                        f"[warn] JSONL parse error at line {line_no}: {e}",
                        file=sys.stderr,
                    )
                continue
            if not isinstance(obj, dict):
                stats.invalid += 1
                continue
            txt = obj.get("text")
            if not isinstance(txt, str):
                stats.invalid += 1
                continue
            s = txt.strip()
            if not s:
                stats.empty += 1
                continue
            out.append(s)
            stats.valid += 1
    return out


def load_corpus(path: Path, fmt: str) -> Tuple[List[str], CorpusStats]:
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(str(path))
    stats = CorpusStats()
    if fmt == "txt":
        corpus = load_corpus_txt(path, stats)
    elif fmt == "jsonl":
        corpus = load_corpus_jsonl(path, stats)
    else:
        raise ValueError("format must be 'txt' or 'jsonl'")
    return corpus, stats


# ------------------------------------------------------------------
# Main
# ------------------------------------------------------------------
def main() -> int:
    p = argparse.ArgumentParser(description="Train ALI Tokenizer (BPE)")
    p.add_argument("--input", required=True, help="corpus file (.txt or .jsonl)")
    p.add_argument("--output", required=True, help="output directory for tokenizer files")
    p.add_argument("--format", choices=["txt", "jsonl"], default="txt")
    p.add_argument("--vocab-size", type=int, default=4096)
    p.add_argument("--min-freq", type=int, default=2)
    p.add_argument("--no-arabic-norm", action="store_true")