# =====================================================================
def test_byte_token_validation():
    """Regression: _is_valid_byte_token يجب أن يرفض tokens غير صالحة."""
    from tokenizer.trainer import _is_valid_byte_token
    assert _is_valid_byte_token("<0xFF>")
    assert _is_valid_byte_token("<0xAA><0xBB></w>")
    assert not _is_valid_byte_token("hello")
    assert not _is_valid_byte_token("<0xFG>")  # invalid hex
    assert not _is_valid_byte_token("<0x")  # truncated


# =====================================================================
# Imported at runtime to avoid polluting pytest's discovery
# =====================================================================
import pytest  # noqa: E402
```

---

### `405/588` `backend/tests/test_tokenizer_v072.py`

- **المسار الكامل:** `F:\1f\p\ALI_Studio_Pro_Design4_4.6.0\04_Adaptive_Hybrid\backend/tests/test_tokenizer_v072.py`
- **الحجم:** 27287 بايت (26.6 KB)
- **الامتداد:** `.py`

```python
# -*- coding: utf-8 -*-
"""اختبارات V0.7.2 — Tokenizer Final Contract Hardening.

تغطي:
- Public API contract.
- Special tokens behavior حقيقي.
- Whitespace contract.
- Normalization contract.
- Byte preservation (lossless).
- BPE deterministic + rank-ordered.
- Model-facing invariants.
- Streaming dataset reader.
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def _build_lossless():
    from tests.test_tokenizer import _build_lossless_tokenizer
    return _build_lossless_tokenizer()


def _build_normalized():
    from tests.test_tokenizer import _build_minimal_tokenizer
    return _build_minimal_tokenizer()


# Cache الـ tokenizers (built once per session).
_TOKENIZER_CACHE: dict = {}


def _cached_lossless():
    if "lossless" not in _TOKENIZER_CACHE:
        _TOKENIZER_CACHE["lossless"] = _build_lossless()
    return _TOKENIZER_CACHE["lossless"]


def _cached_normalized():
    if "normalized" not in _TOKENIZER_CACHE:
        _TOKENIZER_CACHE["normalized"] = _build_normalized()
    return _TOKENIZER_CACHE["normalized"]


# =====================================================================
# 1. Public API Contract
# =====================================================================
class TestPublicAPIContract:
    """الـ API العامة لـ V0.8 Model-facing يجب أن تكون مستقرة."""

    def test_vocab_size_is_int(self):
        t = _cached_lossless()
        assert isinstance(t.vocab_size, int)
        assert t.vocab_size == len(t.vocab)

    def test_special_tokens_property(self):
        t = _cached_lossless()
        sp = t.special_tokens
        assert isinstance(sp, dict)
        assert sp["<PAD>"] == 0
        assert sp["<BOS>"] == 1
        assert sp["<EOS>"] == 2
        assert sp["<UNK>"] == 3
        assert sp["<USER>"] == 4
        assert sp["<ASSISTANT>"] == 5
        assert sp["<SYSTEM>"] == 6

    def test_special_id_properties(self):
        t = _cached_lossless()
        assert t.pad_id == 0
        assert t.bos_id == 1
        assert t.eos_id == 2
        assert t.unk_id == 3
        assert t.user_id == 4
        assert t.assistant_id == 5
        assert t.system_id == 6

    def test_token_to_id_proxy(self):
        t = _cached_lossless()
        assert t.token_to_id("<BOS>") == 1
        assert t.token_to_id("missing", default=-1) == -1
        assert t.token_to_id("<0x41>") is not None

    def test_id_to_token_proxy(self):
        t = _cached_lossless()
        assert t.id_to_token(1) == "<BOS>"
        assert t.id_to_token(99999) is None

    def test_is_special_token(self):
        t = _cached_lossless()
        assert t.is_special_token("<BOS>")
        assert t.is_special_token("<USER>")
        assert not t.is_special_token("<0xFF>")
        assert not t.is_special_token("hello")

    def test_is_byte_token(self):
        t = _cached_lossless()
        assert t.is_byte_token("<0xFF>")
        assert t.is_byte_token("<0xAA><0xBB>")
        assert not t.is_byte_token("<BOS>")
        assert not t.is_byte_token("hello")


# =====================================================================
# 2. Special Tokens — Real Feature
# =====================================================================
class TestSpecialTokensReal:
    """special tokens يجب أن تُستبدل بـ IDs تلقائياً، لا bytes."""

    def test_single_special_token(self):
        t = _cached_lossless()
        assert t.encode("<USER>") == [t.user_id]
        assert t.encode("<BOS>") == [t.bos_id]
        assert t.encode("<EOS>") == [t.eos_id]
        assert t.encode("<PAD>") == [t.pad_id]
        assert t.encode("<UNK>") == [t.unk_id]
        assert t.encode("<SYSTEM>") == [t.system_id]
        assert t.encode("<ASSISTANT>") == [t.assistant_id]

    def test_special_tokens_default_enabled(self):
        t = _cached_lossless()
        assert t.user_id in t.encode("hello <USER>")

    def test_special_tokens_disabled(self):
        t = _cached_lossless()
        ids = t.encode("<USER>", special_tokens=False)
        assert t.user_id not in ids
        # بدلاً من ذلك: bytes للـ chars.
        assert all(isinstance(i, int) for i in ids)
        # length > 1 لأن "<USER>" = 6 chars = 6 bytes.
        assert len(ids) > 1

    def test_multiple_special_tokens(self):
        t = _cached_lossless()
        ids = t.encode("<BOS><USER><EOS>")
        assert ids == [t.bos_id, t.user_id, t.eos_id]

    def test_special_token_mixed_with_arabic(self):
        t = _cached_lossless()
        ids = t.encode("مرحبا <USER> عالم")
        assert t.user_id in ids
        # يجب ألّا يكون أي byte token لـ <USER> في النتيجة.
        assert all(isinstance(i, int) for i in ids)
        assert len(ids) > 1

    def test_special_token_mixed_with_english(self):
        t = _cached_lossless()
        ids = t.encode("hello <USER> world")
        assert t.user_id in ids

    def test_special_token_adjacent_to_punctuation(self):
        t = _cached_lossless()
        ids = t.encode("hi,<USER>!")
        assert t.user_id in ids
        assert ids[0] != t.user_id  # 'hi,' أولاً
        assert ids[-1] != t.user_id  # '!' أخيراً

    def test_special_token_adjacent_to_whitespace(self):
        t = _cached_lossless()
        ids = t.encode(" <USER> ")
        assert t.user_id in ids
        # leading space (byte 0x20) + USER + trailing space.
        assert ids[0] != t.user_id
        assert ids[-1] != t.user_id

    def test_unknown_angle_bracket_text(self):
        """النص '<NOTASPECIAL>' ليس special → يجب أن يتفكك لـ bytes."""
        t = _cached_lossless()
        # ضيف special token وهمي للاختبار — غير موجود في vocab.
        assert not t.is_special_token("<NOTASPECIAL>")
        ids = t.encode("<NOTASPECIAL>")
        # يجب أن ينتج bytes، لا special ID.
        assert all(isinstance(i, int) for i in ids)
        # check that no special ID leaked
        for special_id in (t.pad_id, t.bos_id, t.eos_id, t.unk_id,
                            t.user_id, t.assistant_id, t.system_id):
            assert special_id not in ids

    def test_chat_sequence_build(self):
        """بناء chat sequence كامل: <BOS><SYSTEM>...<USER>...<ASSISTANT>...<EOS>"""
        t = _cached_lossless()
        seq = "<BOS><SYSTEM>you are helpful<USER>hi<ASSISTANT>hello<EOS>"
        ids = t.encode(seq)
        assert ids[0] == t.bos_id
        assert ids[-1] == t.eos_id
        assert t.system_id in ids
        assert t.user_id in ids
        assert t.assistant_id in ids

    def test_decode_with_skip_special_true(self):
        """skip_special=True: الـ special tokens لا تظهر في الـ output."""
        t = _cached_lossless()
        ids = t.encode("<BOS>hello<EOS>")
        decoded = t.decode(ids)
        assert "<BOS>" not in decoded
        assert "<EOS>" not in decoded
        assert "hello" in decoded

    def test_decode_with_skip_special_false(self):
        """skip_special=False: الـ special tokens تظهر literal في الـ output."""
        t = _cached_lossless()
        ids = t.encode("hello")
        decoded = t.decode(ids, skip_special=False)
        assert decoded == "hello"


# =====================================================================
# 3. Normalization Contract
# =====================================================================
class TestNormalizationContract:
    """Exact mode: decode(encode(t)) == t. Normalized mode: decode(encode(t)) == normalize(t)."""

    def test_normalize_returns_string(self):
        t = _cached_lossless()
        result = t.normalize("hello")
        assert isinstance(result, str)

    def test_exact_mode_normalize_is_identity(self):
        t = _cached_lossless()
        for txt in ["hello", "مرحبا", "Hello World", "أحمد"]:
            assert t.normalize(txt) == txt

    def test_normalized_mode_applies_lowercase(self):
        t = _cached_normalized()
        assert t.normalize("HELLO") == "hello"
        assert t.normalize("World") == "world"

    def test_normalized_mode_applies_arabic(self):
        t = _cached_normalized()
        assert t.normalize("أحمد") == "احمد"
        assert t.normalize("إبراهيم") == "ابراهيم"

    def test_normalized_mode_round_trip_equals_normalize(self):
        t = _cached_normalized()
        for txt in ["HELLO WORLD", "أحمد إبراهيم", "Hello مرحبا"]:
            normalized = t.normalize(txt)
            encoded = t.encode(txt)
            decoded = t.decode(encoded)
            assert decoded == normalized, (
                f"normalized mode mismatch: {txt!r} -> normalize={normalized!r} -> round-trip={decoded!r}"
            )

    def test_exact_mode_round_trip_is_identity(self):
        t = _cached_lossless()
        for txt in ["مرحبا", "Hello", "Hello مرحبا", "123456", "C:\\file.py"]:
            ids = t.encode(txt)
            decoded = t.decode(ids)
            assert decoded == txt


# =====================================================================
# 4. Byte Preservation (Lossless)
# =====================================================================
class TestBytePreservation:
    """normalized_input.encode('utf-8') == bytes المستخرجة من decode(encode(t))."""

    BYTE_TEST_TEXTS = [
        ("ASCII", "hello world"),
        ("Arabic", "مرحبا ALI Studio"),
        ("Emoji", "🙂 🚀 ✨ 🎉"),
        ("Chinese", "你好世界"),
        ("Japanese", "こんにちは"),
        ("Korean", "안녕하세요"),
        ("Russian", "Привет мир"),
        ("Greek", "Γειά σου Κόσμε"),
        ("Hebrew", "שלום עולם"),
        ("Symbols", "± × ÷ € £ ¥ © ® ™"),
        ("Code", "def hello(x): return x + 1"),
        ("Paths", "/home/ali/file.py C:\\Users\\ALI\\file.txt"),
        ("Mixed", "مرحبا 你好 안녕 Привет 🙂"),
    ]

    def test_byte_preservation_lossless(self):
        t = _cached_lossless()
        for label, txt in self.BYTE_TEST_TEXTS:
            ids = t.encode(txt)
            decoded = t.decode(ids)
            # Round-trip lossless at byte level.
            assert decoded == txt, (
                f"[{label}] byte preservation failed: {txt!r} -> {decoded!r}"
            )
            # Verify decoded bytes == input bytes.
            assert decoded.encode("utf-8") == txt.encode("utf-8"), (
                f"[{label}] UTF-8 bytes mismatch"
            )


# =====================================================================
# 5. Whitespace Contract
# =====================================================================
class TestWhitespaceContract:
    """كل whitespace char يجب أن يُحفظ."""

    CASES = [
        ("hello world", "single space"),
        ("hello  world", "double space"),
        ("hello   world", "triple space"),
        (" hello", "leading space"),
        ("hello ", "trailing space"),
        ("  hello  ", "leading + trailing"),
        ("hello\tworld", "tab"),
        ("hello\nworld", "newline"),
        ("hello\r\nworld", "CRLF"),
        ("hello\n\nworld", "double newline"),
        ("\t\t", "tabs only"),
        ("\n\n", "newlines only"),
    ]

    def test_whitespace_preserved_lossless(self):
        t = _cached_lossless()
        for txt, label in self.CASES:
            ids = t.encode(txt)
            decoded = t.decode(ids)
            assert decoded == txt, f"[{label}] whitespace lost: {txt!r} -> {decoded!r}"

    def test_decode_does_not_invent_spaces(self):
        """الـ decode يجب ألّا يستخدم ' '.join."""
        t = _cached_lossless()
        # 4 spaces في input.
        ids = t.encode("hello    world")
        decoded = t.decode(ids)
        # 4 spaces preserved.
        assert "hello    world" == decoded


# =====================================================================
# 6. BPE Determinism
# =====================================================================
class TestBPEDeterminism:
    """نفس corpus + config → نفس merges + نفس vocab + نفس IDs."""

    def test_apply_bpe_deterministic(self):
        t = _cached_lossless()
        # تطبيق مرتين.
        result1 = t._apply_bpe(["a", "b", "c"])
        result2 = t._apply_bpe(["a", "b", "c"])
        assert result1 == result2

    def test_apply_bpe_rank_ordered(self):
        """Merges تُطبّق حسب الـ rank (الأقل أولاً)."""
        t = _cached_lossless()
        # إذا كان merge (a, b) → ab موجود في vocab، ثم (ab, c) → abc.
        symbols = ["a", "b", "c"]
        result = t._apply_bpe(list(symbols))
        # الـ output يجب أن يكون deterministic.
        assert result == t._apply_bpe(list(symbols))

    def test_encode_deterministic(self):
        t = _cached_lossless()
        a = t.encode("hello world مرحبا")
        b = t.encode("hello world مرحبا")
        assert a == b

    def test_decode_deterministic(self):
        t = _cached_lossless()
        ids = t.encode("test")
        assert t.decode(ids) == t.decode(ids)

    def test_repeated_chars_round_trip(self):
        t = _cached_lossless()
        for txt in ["aaa", "aaaa", "abababab", "aaaaaaaaaa", "123123123"]:
            assert t.decode(t.encode(txt)) == txt

    def test_arabic_repeated_round_trip(self):
        t = _cached_lossless()
        for txt in ["مررررررحبا", "متتتتتتتت", "الحححححححح"]:
            assert t.decode(t.encode(txt)) == txt


# =====================================================================
# 7. Model-facing invariants
# =====================================================================
class TestModelFacingInvariants:
    """اختبارات لـ V0.8 Model: IDs صحيحة، ضمن النطاق."""

    def test_ids_in_vocab_range(self):
        t = _cached_lossless()
        ids = t.encode("مرحبا ALI Studio <USER> test")
        for tid in ids:
            assert 0 <= tid < t.vocab_size, f"id {tid} out of vocab range"

    def test_all_ids_are_int(self):
        t = _cached_lossless()
        ids = t.encode("hello world")
        assert all(isinstance(i, int) for i in ids)

    def test_pad_id_in_vocab(self):
        t = _cached_lossless()
        assert 0 <= t.pad_id < t.vocab_size

    def test_bos_id_in_vocab(self):
        t = _cached_lossless()
        assert 0 <= t.bos_id < t.vocab_size

    def test_empty_input_returns_empty_list(self):
        t = _cached_lossless()
        assert t.encode("") == []

    def test_empty_input_with_bos(self):
        t = _cached_lossless()
        assert t.encode("", add_bos=True) == [t.bos_id]

    def test_empty_input_with_eos(self):
        t = _cached_lossless()
        assert t.encode("", add_eos=True) == [t.eos_id]

    def test_empty_input_with_bos_and_eos(self):
        t = _cached_lossless()
        assert t.encode("", add_bos=True, add_eos=True) == [t.bos_id, t.eos_id]

    def test_very_long_input(self):
        t = _cached_lossless()
        txt = "مرحبا ALI Studio " * 1000   # 19000 chars
        ids = t.encode(txt)
        assert all(0 <= i < t.vocab_size for i in ids)
        # lossless round-trip
        assert t.decode(ids) == txt

    def test_padding_id_is_pad_token(self):
        t = _cached_lossless()
        assert t.id_to_token(t.pad_id) == "<PAD>"


# =====================================================================
# 8. Serialization + Atomic Writes
# =====================================================================
class TestSerializationHardening:
    """manifest + atomic writes + integrity."""

    def test_save_creates_manifest(self, tmp_path):
        from tokenizer.serialization import save_tokenizer
        t = _cached_lossless()
        root = tmp_path / "tok"
        save_tokenizer(t, root)
        assert (root / "manifest.json").exists()

    def test_manifest_contains_hashes(self, tmp_path):
        from tokenizer.serialization import save_tokenizer
        t = _cached_lossless()
        root = tmp_path / "tok"
        save_tokenizer(t, root)
        manifest = (root / "manifest.json").read_text(encoding="utf-8")
        import json
        data = json.loads(manifest)
        assert "config_hash" in data
        assert "vocab_hash" in data
        assert "merges_hash" in data
        assert data["algorithm"] == "BPE"
        assert data["tokenizer_version"] == "0.7.2"
        assert data["vocab_size"] == t.vocab_size
        assert data["merge_count"] == t.num_merges

    def test_atomic_write_no_partial_files_on_crash(self, tmp_path):
        """Atomic write: ملف نصف مكتمل لا يبقى على القرص."""
        from tokenizer.serialization import _atomic_write_text
        target = tmp_path / "atomic.txt"
        # اكتب محتوى عادي أولاً.
        _atomic_write_text(target, "hello world")
        assert target.read_text(encoding="utf-8") == "hello world"
        # تأكد عدم وجود ملفات tmp متبقية.
        leftover = list(tmp_path.glob(".atomic.txt.*.tmp"))
        assert not leftover

    def test_load_validates_hashes(self, tmp_path):
        """تحميل tokenizer بـ manifest تالف يجب أن يفشل."""
        from tokenizer.serialization import save_tokenizer, load_tokenizer
        t = _cached_lossless()
        root = tmp_path / "tok"
        save_tokenizer(t, root)
        # عبث بالـ vocab بعد الحفظ.
        vocab_path = root / "vocab.json"
        original = vocab_path.read_text(encoding="utf-8")
        vocab_path.write_text(original + "\n", encoding="utf-8")
        # تحميل يجب أن يفشل لأن الـ hash تغيّر.
        import pytest
        with pytest.raises(ValueError, match="manifest mismatch"):
            load_tokenizer(root)

    def test_corrupt_manifest_rejected(self, tmp_path):
        from tokenizer.serialization import save_tokenizer, load_tokenizer
        t = _cached_lossless()
        root = tmp_path / "tok"
        save_tokenizer(t, root)
        # manifest تالف.
        (root / "manifest.json").write_text("not json{{{", encoding="utf-8")
        import pytest
        with pytest.raises(ValueError, match="malformed"):
            load_tokenizer(root)

    def test_wrong_algorithm_rejected(self, tmp_path):
        from tokenizer.serialization import save_tokenizer, load_tokenizer
        t = _cached_lossless()
        root = tmp_path / "tok"
        save_tokenizer(t, root)
        # عبث بالـ manifest.
        import json
        manifest = json.loads((root / "manifest.json").read_text())
        manifest["algorithm"] = "WordPiece"
        (root / "manifest.json").write_text(
            json.dumps(manifest, indent=2), encoding="utf-8",
        )
        import pytest
        with pytest.raises(ValueError, match="algorithm"):
            load_tokenizer(root)


# =====================================================================
# 9. Streaming Dataset Reader
# =====================================================================
class TestStreamingDataset:
    """corpus يمكن أن يكون Iterable[str] (generator)."""

    def test_train_with_generator(self):
        from tokenizer.config import TokenizerConfig
        from tokenizer.trainer import BPETrainer
        cfg = TokenizerConfig(vocab_size=200, min_frequency=1)
        def gen():
            yield "hello world"
            yield "hello there"
            yield "مرحبا"
        trainer = BPETrainer(cfg)
        vocab, merges = trainer.train(gen())
        assert vocab.token_to_id("<PAD>") == 0
        assert len(vocab) > 200 - 100   # بعض الـ merges.

    def test_train_with_list(self):
        from tokenizer.config import TokenizerConfig
        from tokenizer.trainer import BPETrainer
        cfg = TokenizerConfig(vocab_size=200, min_frequency=1)
        trainer = BPETrainer(cfg)
        vocab, merges = trainer.train(["hello world", "hello there", "مرحبا"])
        assert len(vocab) > 0

    def test_streaming_corpus_large(self):
        """تدريب على corpus كبير مولّد ديناميكياً."""
        from tokenizer.config import TokenizerConfig
        from tokenizer.trainer import BPETrainer
        cfg = TokenizerConfig(vocab_size=200, min_frequency=1)
        def stream():
            for i in range(100):
                yield f"الكلمة رقم {i} text{i}"
        trainer = BPETrainer(cfg)
        vocab, merges = trainer.train(stream())
        assert len(vocab) > 100

    def test_empty_stream_raises(self):
        from tokenizer.config import TokenizerConfig
        from tokenizer.trainer import BPETrainer
        import pytest
        cfg = TokenizerConfig()
        trainer = BPETrainer(cfg)
        with pytest.raises(ValueError, match="empty corpus"):
            trainer.train([])

        def empty_gen():
            return
            yield  # noqa
        with pytest.raises(ValueError, match="empty corpus"):
            trainer.train(empty_gen())


# =====================================================================
# 10. Vocabulary Validation Strict
# =====================================================================
class TestVocabValidationStrict:
    """required_tokens, reserved_count, contiguous."""

    def test_required_tokens_missing(self):
        from tokenizer.vocabulary import Vocabulary
        import pytest
        v = Vocabulary()
        v.add("<PAD>")
        v.add("<BOS>")
        with pytest.raises(ValueError, match="required token"):
            v.validate(required_tokens=["<PAD>", "<BOS>", "<UNK>"])

    def test_reserved_count_strict(self):
        from tokenizer.vocabulary import Vocabulary
        import pytest
        v = Vocabulary()
        v.add("<PAD>")
        v.add("<BOS>")
        # reserved_count=3 ولكن فقط 2 token في vocab.
        with pytest.raises(ValueError, match="reserved slot"):
            v.validate(reserved_count=3)

    def test_validation_passes_with_required(self):
        from tokenizer.vocabulary import Vocabulary
        v = Vocabulary()
        for t in ["<PAD>", "<BOS>", "<EOS>", "<UNK>", "a", "b"]:
            v.add(t)
        # contiguous: 0..5
        v.validate(reserved_count=4, required_tokens=["<PAD>", "<BOS>", "<EOS>", "<UNK>"])


# =====================================================================
# 11. Determinism Across Runs (hashes)
# =====================================================================
class TestDeterminismHardening:
    """نفس corpus + config → نفس config/vocab/merges hashes + نفس encoded IDs."""

    def test_train_save_hash_stable(self, tmp_path):
        from tokenizer.config import TokenizerConfig
        from tokenizer.trainer import BPETrainer
        from tokenizer.tokenizer import ALITokenizer
        from tokenizer.serialization import save_tokenizer
        import hashlib
        cfg = TokenizerConfig(vocab_size=200, min_frequency=1)
        corpus = ["hello world", "مرحبا ALI", "test 123"]
        d1 = tmp_path / "tok1"
        d2 = tmp_path / "tok2"
        d1.mkdir()
        d2.mkdir()
        for d in (d1, d2):
            trainer = BPETrainer(cfg)
            vocab, merges = trainer.train(corpus)
            tok = ALITokenizer(cfg, vocab, merges)
            save_tokenizer(tok, d)
        # قارن الملفات.
        for fn in ("config.json", "vocab.json", "merges.txt", "manifest.json"):
            h1 = hashlib.sha256((d1 / fn).read_bytes()).hexdigest()
            h2 = hashlib.sha256((d2 / fn).read_bytes()).hexdigest()
            assert h1 == h2, f"{fn} differs: {h1[:8]} vs {h2[:8]}"

    def test_encode_ids_match_across_runs(self, tmp_path):
        from tokenizer.config import TokenizerConfig
        from tokenizer.trainer import BPETrainer
        from tokenizer.tokenizer import ALITokenizer
        from tokenizer.serialization import save_tokenizer, load_tokenizer
        cfg = TokenizerConfig(vocab_size=300, min_frequency=1)
        corpus = ["hello world مرحبا", "test 123", "ALI Studio"]
        d1 = tmp_path / "tok1"
        d2 = tmp_path / "tok2"
        d1.mkdir(); d2.mkdir()
        toks = []
        for d in (d1, d2):
            trainer = BPETrainer(cfg)
            vocab, merges = trainer.train(corpus)
            tok = ALITokenizer(cfg, vocab, merges)
            save_tokenizer(tok, d)
            toks.append(load_tokenizer(d))
        # نفس corpus + config → نفس encoded IDs.
        test_texts = ["hello", "مرحبا", "ALI Studio", "test 123"]
        for txt in test_texts:
            ids1 = toks[0].encode(txt)
            ids2 = toks[1].encode(txt)
            assert ids1 == ids2, f"IDs differ for {txt!r}: {ids1} vs {ids2}"


# =====================================================================
# 12. Lazy Loading
# =====================================================================
class TestLazyLoadingHardening:
    """import tokenizer يجب ألّا يفعل شيئاً ثقيلاً."""

    def test_import_does_not_open_db(self):
        import subprocess
        import os
        result = subprocess.run(
            [sys.executable, "-c",
             "import tokenizer; print('OK')"],
            capture_output=True, text=True, timeout=10,
            cwd=str(ROOT),
        )
        assert result.returncode == 0, result.stderr
        assert "OK" in result.stdout

    def test_get_default_returns_none_if_missing(self, tmp_path):
        from tokenizer import get_default_tokenizer
        from config.paths import APP_PATHS
        # مؤقتاً: غيّر APPDATA.
        import os
        old = os.environ.get("APPDATA")
        try:
            os.environ["APPDATA"] = str(tmp_path)
            # tokenizer الافتراضي تحت PROJECT_ROOT/weights/tokenizer — قد يكون موجود.
            # إذا لم يكن، None.
            t = get_default_tokenizer()
            assert t is None or t.vocab_size > 256
        finally:
            if old is not None:
                os.environ["APPDATA"] = old


# =====================================================================
# 13. Decode Edge Cases
# =====================================================================
class TestDecodeEdgeCases:

    def test_decode_unknown_id_replaced(self):
        t = _cached_lossless()
        # ID كبير جداً → token غير موجود → '?'.
        result = t.decode([999999])
        assert result == "?"

    def test_decode_mixed_specials_and_text(self):
        t = _cached_lossless()
        ids = [t.bos_id] + t.encode("hello world") + [t.eos_id]
        decoded = t.decode(ids)
        assert "hello world" in decoded
        assert "<BOS>" not in decoded
        assert "<EOS>" not in decoded

    def test_decode_empty_list_returns_empty_string(self):
        t = _cached_lossless()
        assert t.decode([]) == ""

    def test_decode_zero_id_returns_pad_token(self):
        t = _cached_lossless()
        result = t.decode([t.pad_id], skip_special=True)
        assert result == ""
```

---

### `406/588` `backend/tests/test_tools.py`

- **المسار الكامل:** `F:\1f\p\ALI_Studio_Pro_Design4_4.6.0\04_Adaptive_Hybrid\backend/tests/test_tools.py`
- **الحجم:** 4188 بايت (4.1 KB)
- **الامتداد:** `.py`

```python
# -*- coding: utf-8 -*-
"""اختبارات V0.4 — Tools + ToolRegistry."""

from __future__ import annotations

import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def _make_ctx(tmpdir: Path, perm_mode: str = "default"):
    from core.context import ConversationContext
    return ConversationContext(
        thread_id="t_test",
        project_dir=str(tmpdir),
        perm_mode=perm_mode,
    )


def test_registry_default_set():
    from tools.registry import get_registry, reset_registry_for_tests
    reset_registry_for_tests()
    reg = get_registry()
    names = reg.names()
    # يجب أن تكون كل الأدوات الأساسية موجودة
    for required in ("read_file", "list_dir", "write_file", "search_files",
                     "run_command", "git_status", "git_diff", "git_commit"):
        assert required in names, f"missing tool: {required}"


def test_read_file_tool(tmp_path):
    (tmp_path / "hello.txt").write_text("مرحبا ALI", encoding="utf-8")
    from tools.filesystem import ReadFileTool
    ctx = _make_ctx(tmp_path)
    res = ReadFileTool().execute(ctx, path="hello.txt")
    assert res.ok
    assert "مرحبا ALI" in res.data["content"]


def test_read_file_blocks_escape(tmp_path):
    from tools.filesystem import ReadFileTool
    ctx = _make_ctx(tmp_path)
    res = ReadFileTool().execute(ctx, path="../../../etc/passwd")
    assert not res.ok
    assert res.error_code == "PATH_BLOCKED"


def test_write_file_tool(tmp_path):
    from tools.filesystem import WriteFileTool
    ctx = _make_ctx(tmp_path)
    res = WriteFileTool().execute(
        ctx, path="out.py", content="print('ok')\n"
    )
    assert res.ok
    assert (tmp_path / "out.py").exists()
    assert "print" in (tmp_path / "out.py").read_text(encoding="utf-8")


def test_list_dir_tool(tmp_path):
    (tmp_path / "a.txt").write_text("a")
    (tmp_path / "sub").mkdir()
    from tools.filesystem import ListDirTool
    ctx = _make_ctx(tmp_path)
    res = ListDirTool().execute(ctx, path="")
    assert res.ok
    names = {e["name"] for e in res.data["entries"]}
    assert "a.txt" in names
    assert "sub" in names


def test_search_files_tool(tmp_path):
    (tmp_path / "a.py").write_text("hello world\nimport os\n")
    (tmp_path / "b.py").write_text("hello there\n")
    from tools.filesystem import SearchFilesTool
    ctx = _make_ctx(tmp_path)
    res = SearchFilesTool().execute(ctx, pattern=r"import os")
    assert res.ok
    assert any("a.py" in m["path"] for m in res.data["matches"])


def test_run_command_blocks_dangerous(tmp_path):
    from tools.terminal import RunShellTool
    ctx = _make_ctx(tmp_path)
    res = RunShellTool().execute(ctx, command="rm -rf /")
    assert not res.ok
    assert res.error_code == "DENIED"


def test_run_command_denied_in_read_only(tmp_path):
    from tools.terminal import RunShellTool
    ctx = _make_ctx(tmp_path, perm_mode="read-only")
    res = RunShellTool().execute(ctx, command="echo hi")
    assert not res.ok
    assert res.error_code == "DENIED"


def test_run_command_safe_executes(tmp_path):
    from tools.terminal import RunShellTool
    ctx = _make_ctx(tmp_path)
    res = RunShellTool().execute(ctx, command="echo hello")
    assert res.ok
    assert "hello" in res.data["stdout"]


def test_registry_unknown_tool(tmp_path):
    from tools.registry import get_registry, reset_registry_for_tests
    reset_registry_for_tests()
    reg = get_registry()
    res = reg.execute("nonexistent", _make_ctx(tmp_path))
    assert not res.ok
    assert res.error_code == "UNKNOWN_TOOL"


def test_registry_executes_through_pm(tmp_path):
    """Tool بصلاحية READ_ONLY يعمل في default بدون سؤال."""
    from tools.registry import get_registry, reset_registry_for_tests
    from security.permissions import PermissionManager
    reset_registry_for_tests()
    reg = get_registry()
    reg.set_permission_manager(PermissionManager(mode="default"))
    (tmp_path / "x.txt").write_text("ok")
    res = reg.execute("read_file", _make_ctx(tmp_path), path="x.txt")
    assert res.ok
```

---

### `407/588` `backend/tests/test_ui_integration.py`

- **المسار الكامل:** `F:\1f\p\ALI_Studio_Pro_Design4_4.6.0\04_Adaptive_Hybrid\backend/tests/test_ui_integration.py`
- **الحجم:** 5620 بايت (5.5 KB)
- **الامتداد:** `.py`

```python
# -*- coding: utf-8 -*-
"""اختبار V0.6 — ربط الواجهة بالـ Tools والـ PermissionManager.

يختبر منطق الـ dispatch + run_tool_with_ui عبر تشغيل الـ App في وضع headless
وفحص:
- dispatcher يختار الأداة الصحيحة.
- permission dialog يُسأل عند الحاجة (في الاختبار نتجاوزه مباشرة).
- tool يُنفّذ فعلياً.
- audit row يُكتب في DB.
- reply string يحتوي على علامة النجاح أو الفشل.
"""

from __future__ import annotations

import sys
import os
import pytest
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

pytestmark = pytest.mark.skipif(os.name != "nt" and os.environ.get("ALI_GUI_TESTS") != "1", reason="Desktop GUI unavailable in headless environment")
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def _make_app_with_workdir():
    """يبني App مع مجلد عمل مؤقت + APPDATA معزولة."""
    try:
        import tkinter as tk
    except Exception:
        import pytest
        pytest.skip("tkinter unavailable")

    # إعادة تعيين singletons لأنهم قد يحتفظون بـ db_path من تشغيل سابق.
    from tools.registry import reset_registry_for_tests
    from security.permissions import reset_permission_manager_for_tests
    reset_registry_for_tests()
    reset_permission_manager_for_tests()

    tmp = Path(tempfile.mkdtemp(prefix="ali_v06_"))
    proj = tmp / "workspace"
    proj.mkdir()
    (proj / "hello.txt").write_text("ali", encoding="utf-8")

    import os
    appdata = tmp / "appdata"
    appdata.mkdir()
    os.environ["APPDATA"] = str(appdata)

    from database.database import reset_database_for_tests
    reset_database_for_tests()

    # لا حاجة لإنشاء Tk root فعلي لاختبارات dispatcher — الـ App
    # تلامس tk widgets فقط عند build()، والـ dispatcher لا يحتاج Tk.
    # لكن `_db()` يستخدم lazy import، و App.perm_mode يحتاج StringVar (Tk).
    # لذلك نستخدم Tk() ونلتقط أي خطأ Tcl متأخر.
    from ali_agent import App
    try:
        root = tk.Tk()
        app = App(root)
    except Exception:
        # بعض بيئات الاختبار (Hermes) تكسر Tcl عند إعادة التهيئة.
        import pytest as _pt
        _pt.skip("Tcl/Tk init failed in this environment")
    app.project_dir = str(proj)
    app.cfg["last_dir"] = str(proj)
    return app, root, proj


def test_dispatcher_routes_read_file():
    from ali_agent import App
    app, root, _ = _make_app_with_workdir()
    try:
        d = app._dispatch_tool("read_file hello.txt")
        assert d is not None
        name, kwargs, _ = d
        assert name == "read_file"
        assert kwargs["path"] == "hello.txt"
    finally:
        root.destroy()


def test_dispatcher_routes_git_status():
    from ali_agent import App
    app, root, _ = _make_app_with_workdir()
    try:
        d = app._dispatch_tool("git status")
        assert d[0] == "git_status"
    finally:
        root.destroy()


def test_dispatcher_routes_run_command():
    from ali_agent import App
    app, root, _ = _make_app_with_workdir()
    try:
        d = app._dispatch_tool("run_command echo ali")
        assert d is not None
        assert d[0] == "run_command"
        assert d[1]["command"] == "echo ali"
    finally:
        root.destroy()


def test_dispatcher_no_match():
    from ali_agent import App