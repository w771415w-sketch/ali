# -*- coding: utf-8 -*-
"""Serialization — حفظ/تحميل ALI Tokenizer إلى/من القرص.

Artifact layout (داخل مجلد tokenizer/):
    config.json     # TokenizerConfig
    vocab.json      # {token: id}
    merges.txt      # كل سطر "a b"
    manifest.json   # metadata: tokenizer_version, algorithm, hashes

Writes atomic (temp file + os.replace) حتى لا يترك crash ملفاً نصف مكتوب.
"""

from __future__ import annotations

import hashlib
import json
import os
import tempfile
from pathlib import Path
from typing import List, Tuple

from tokenizer.config import TokenizerConfig
from tokenizer.vocabulary import Vocabulary
from tokenizer.tokenizer import ALITokenizer


TOKENIZER_VERSION = "0.7.2"
ALGORITHM = "BPE"


# ------------------------------------------------------------------
class TokenizerPaths:
    """مسارات الملفات داخل مجلد الـ tokenizer."""

    def __init__(self, root: Path) -> None:
        self.root = Path(root)
        self.config = self.root / "config.json"
        self.vocab = self.root / "vocab.json"
        self.merges = self.root / "merges.txt"
        self.manifest = self.root / "manifest.json"

    def exists(self) -> bool:
        return self.config.exists() and self.vocab.exists() and self.merges.exists()

    def which_missing(self) -> List[str]:
        out = []
        for name, p in [("config", self.config), ("vocab", self.vocab),
                         ("merges", self.merges)]:
            if not p.exists():
                out.append(name)
        return out


# ------------------------------------------------------------------
# Atomic write helper
# ------------------------------------------------------------------
def _atomic_write_bytes(path: Path, data: bytes) -> None:
    """Write bytes to path atomically (temp + os.replace)."""
    path.parent.mkdir(parents=True, exist_ok=True)
    # tempfile in same dir for os.replace atomicity.
    fd, tmp_path = tempfile.mkstemp(
        dir=str(path.parent), prefix=f".{path.name}.", suffix=".tmp",
    )
    try:
        with os.fdopen(fd, "wb") as f:
            f.write(data)
        os.replace(tmp_path, path)
    except Exception:
        try:
            os.unlink(tmp_path)
        except OSError:
            pass
        raise


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
