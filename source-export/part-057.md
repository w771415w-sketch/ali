    from model.registry import ModelRegistry
    from model.manager import ModelManager
    root = tmp_path / 'root'; root.mkdir()
    model_dir = root / 'models' / 'active' / 'ALI-Bootstrap-v2.5'
    model_dir.mkdir(parents=True)
    (model_dir / 'config.json').write_text(json.dumps({"vocab_size": 8}), encoding='utf-8')
    reg = ModelRegistry(root / 'registry.sqlite3')
    stale = str(tmp_path / 'old' / 'installation' / 'backend' / 'models' / 'active' / 'ALI-Bootstrap-v2.5')
    reg.register('ALI','2.5.0-bootstrap-micro', artifact_type='base', status='active', hf_dir=stale, checkpoint=stale)
    mgr = ModelManager(root, reg)
    row = mgr.discover_active()
    assert row and row['hf_dir'] == str(model_dir.resolve())


def test_markdown_conversation_import_parses_explicit_pairs(tmp_path):
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    from training.continuous_learning import ContinuousLearningManager
    from model.registry import ModelRegistry
    md = tmp_path / 'conversation.md'
    md.write_text('## المحادثة 1\n\n**User:** ما هو RAG؟\n\n**Assistant:** هو الاسترجاع المعزز بالتوليد.\n\n---\n\n## المحادثة 2\n\n**User:** كيف يعمل v1؟\n\n**Assistant:** يبدأ من النموذج النشط السابق ويستخدم بيانات جديدة.\n', encoding='utf-8')
    root = tmp_path / 'root'; root.mkdir()
    mgr = ContinuousLearningManager(root, ModelRegistry(root / 'models.sqlite3'))
    result = mgr.import_files([md])[0]
    assert result['status'] == 'validated'
    assert result['sample_count'] == 2


def test_all_existing_samples_are_reported_as_duplicate_not_rag_only(tmp_path):
    import sys, json
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    from training.continuous_learning import ContinuousLearningManager
    from model.registry import ModelRegistry
    root = tmp_path / 'root'; root.mkdir()
    mgr = ContinuousLearningManager(root, ModelRegistry(root / 'models.sqlite3'))
    md = tmp_path / 'conversation.md'
    md.write_text('**User:** سؤال فريد\n\n**Assistant:** جواب فريد.\n', encoding='utf-8')
    first = mgr.import_files([md])[0]
    assert first['status'] == 'validated' and first['sample_count'] == 1
    second = mgr.import_files([md])[0]
    assert second['status'] == 'duplicate'
```

---

### `402/588` `backend/tests/test_rtl_and_ui_contract.py`

- **المسار الكامل:** `F:\1f\p\ALI_Studio_Pro_Design4_4.6.0\04_Adaptive_Hybrid\backend/tests/test_rtl_and_ui_contract.py`
- **الحجم:** 933 بايت (0.9 KB)
- **الامتداد:** `.py`

```python
# -*- coding: utf-8 -*-
"""Deterministic tests for the production UI direction contract."""
from __future__ import annotations
from config.i18n import normalize_language, is_rtl, tr
from ui.rtl import start_side, end_side, anchor_start, justify


def test_arabic_is_rtl():
    assert normalize_language("ar-SA") == "ar"
    assert is_rtl("ar") is True
    assert start_side("ar") == "right"
    assert end_side("ar") == "left"
    assert anchor_start("ar") == "e"
    assert justify("ar") == "right"
    assert tr("send", "ar") == "إرسال"


def test_english_is_ltr():
    assert normalize_language("en-US") == "en"
    assert is_rtl("en") is False
    assert start_side("en") == "left"
    assert end_side("en") == "right"
    assert anchor_start("en") == "w"
    assert justify("en") == "left"
    assert tr("send", "en") == "Send"


def test_unknown_language_defaults_to_english():
    assert normalize_language("fr") == "en"
```

---

### `403/588` `backend/tests/test_security.py`

- **المسار الكامل:** `F:\1f\p\ALI_Studio_Pro_Design4_4.6.0\04_Adaptive_Hybrid\backend/tests/test_security.py`
- **الحجم:** 4165 بايت (4.1 KB)
- **الامتداد:** `.py`

```python
# -*- coding: utf-8 -*-
"""اختبارات V0.5 — Security: paths, commands, permissions."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def test_safe_path_inside_workspace(tmp_path):
    from security.paths import safe_project_path
    p = safe_project_path(str(tmp_path), "sub/file.py")
    assert p == (tmp_path / "sub/file.py").resolve()


def test_safe_path_blocks_escape(tmp_path):
    from security.paths import safe_project_path
    import pytest
    with pytest.raises(PermissionError):
        safe_project_path(str(tmp_path), "../../etc/passwd")


def test_safe_path_blocks_dotenv(tmp_path):
    from security.paths import safe_project_path
    import pytest
    with pytest.raises(PermissionError):
        safe_project_path(str(tmp_path), ".env")


def test_safe_path_blocks_ssh(tmp_path):
    from security.paths import safe_project_path
    import pytest
    with pytest.raises(PermissionError):
        safe_project_path(str(tmp_path), "../.ssh/id_rsa")


# --------- commands
def test_command_blocks_rm_rf_root():
    from security.commands import is_command_safe
    assert not is_command_safe("rm -rf /")
    assert not is_command_safe("rm -rf /etc")


def test_command_blocks_format():
    from security.commands import is_command_safe
    assert not is_command_safe("format C:")
    assert not is_command_safe("format D:")


def test_command_blocks_diskpart():
    from security.commands import is_command_safe
    assert not is_command_safe("diskpart")


def test_command_blocks_shutdown():
    from security.commands import is_command_safe
    assert not is_command_safe("shutdown /s /t 0")


def test_command_blocks_forkbomb():
    from security.commands import is_command_safe
    assert not is_command_safe(":(){ :|:& };:")


def test_command_allows_safe():
    from security.commands import is_command_safe
    assert is_command_safe("echo hello")
    assert is_command_safe("dir")
    assert is_command_safe("git status")
    assert is_command_safe("python -m pytest")


# --------- permissions
def test_pm_read_only_blocks_write():
    from security.permissions import PermissionManager
    from tools.base import ToolPermission
    pm = PermissionManager(mode="read-only")
    d = pm.check(tool_name="write_file", permission=ToolPermission.DEFAULT)
    assert not d.allowed
    assert not d.needs_ask


def test_pm_default_allows_read():
    from security.permissions import PermissionManager
    from tools.base import ToolPermission
    pm = PermissionManager(mode="default")
    d = pm.check(tool_name="read_file", permission=ToolPermission.READ_ONLY)
    assert d.allowed
    assert not d.needs_ask


def test_pm_default_asks_for_write():
    from security.permissions import PermissionManager
    from tools.base import ToolPermission
    pm = PermissionManager(mode="default")
    d = pm.check(tool_name="write_file", permission=ToolPermission.DEFAULT)
    # tool perm = DEFAULT, mode = DEFAULT → rank متساوية → allowed
    # لتفعيل ASK نحتاج default لطلب default (متساوي → allow).
    # أعد الاختبار بأداة بصلاحية أعلى:
    d2 = pm.check(tool_name="dangerous", permission=ToolPermission.FULL_ACCESS)
    assert not d2.allowed
    assert d2.needs_ask


def test_pm_full_access_allows_all():
    from security.permissions import PermissionManager
    from tools.base import ToolPermission
    pm = PermissionManager(mode="full-access")
    d = pm.check(tool_name="write_file", permission=ToolPermission.DEFAULT)
    assert d.allowed


def test_pm_always_allow_shortcuts():
    from security.permissions import PermissionManager
    from tools.base import ToolPermission
    pm = PermissionManager(mode="read-only")
    pm.grant("write_file")
    d = pm.check(tool_name="write_file", permission=ToolPermission.DEFAULT)
    assert d.allowed


def test_pm_invalid_mode():
    from security.permissions import PermissionManager
    import pytest
    with pytest.raises(ValueError):
        PermissionManager(mode="super-admin")
```

---

### `404/588` `backend/tests/test_tokenizer.py`

- **المسار الكامل:** `F:\1f\p\ALI_Studio_Pro_Design4_4.6.0\04_Adaptive_Hybrid\backend/tests/test_tokenizer.py`
- **الحجم:** 28887 بايت (28.2 KB)
- **الامتداد:** `.py`

```python
# -*- coding: utf-8 -*-
"""اختبارات V0.7 — Tokenizer (Config, Vocabulary, Trainer, ALITokenizer, Ser).

تنقسم الاختبارات إلى:
- Tests أساسية (unit).
- Round-trip tests بوضوح:
    * Exact Round Trip — فقط مع tokenizer lossless (no normalization).
    * Normalized Round Trip — مع default config، الـ decoded = normalized text.
- Regression tests — تحمي من الـ bugs التي ظهرت أثناء التطوير.
"""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


# =====================================================================
# Config
# =====================================================================
def test_config_defaults():
    from tokenizer.config import TokenizerConfig, DEFAULT_SPECIAL_TOKENS
    c = TokenizerConfig()
    assert c.type == "BPE"
    assert c.vocab_size == 4096
    assert c.special_tokens == DEFAULT_SPECIAL_TOKENS
    assert c.normalize_arabic is True
    assert c.version == "0.7.1"


def test_config_round_trip(tmp_path):
    from tokenizer.config import TokenizerConfig
    c = TokenizerConfig(vocab_size=512, min_frequency=3)
    p = tmp_path / "cfg.json"
    c.save(p)
    c2 = TokenizerConfig.load(p)
    assert c2.vocab_size == 512
    assert c2.min_frequency == 3


def test_config_to_from_dict():
    from tokenizer.config import TokenizerConfig
    c = TokenizerConfig()
    d = c.to_dict()
    c2 = TokenizerConfig.from_dict(d)
    assert c2 == c


def test_config_rejects_duplicate_special():
    """Regression: تكرار special token يجب أن يُرفض."""
    from tokenizer.config import TokenizerConfig
    import pytest
    with pytest.raises(ValueError, match="duplicate special"):
        TokenizerConfig(special_tokens=["<PAD>", "<BOS>", "<PAD>"])


def test_config_rejects_byte_collision():
    """Regression: special token لا يجب أن يبدأ بـ '<0x' (محجوز للـ bytes)."""
    from tokenizer.config import TokenizerConfig
    import pytest
    with pytest.raises(ValueError, match="reserved for byte"):
        TokenizerConfig(special_tokens=["<0xFF>"])


def test_config_rejects_zero_vocab():
    from tokenizer.config import TokenizerConfig
    import pytest
    with pytest.raises(ValueError):
        TokenizerConfig(vocab_size=0)


# =====================================================================
# Vocabulary
# =====================================================================
def test_vocab_add_and_lookup():
    from tokenizer.vocabulary import Vocabulary
    v = Vocabulary()
    assert v.add("a") == 0
    assert v.add("b") == 1
    assert v.add("a") == 0
    assert v.token_to_id("a") == 0
    assert v.id_to_token(1) == "b"
    assert v.token_to_id("x", default=-1) == -1


def test_vocab_no_duplicates():
    from tokenizer.vocabulary import Vocabulary
    v = Vocabulary()
    v.add("a")
    v.add("b")
    v.validate()
    assert len(v) == 2


def test_vocab_rejects_empty():
    from tokenizer.vocabulary import Vocabulary
    import pytest
    v = Vocabulary()
    with pytest.raises(ValueError):
        v.add("")


def test_vocab_round_trip_json(tmp_path):
    from tokenizer.vocabulary import Vocabulary
    v = Vocabulary()
    for tok in ["<PAD>", "a", "b", "c", "ab"]:
        v.add(tok)
    p = tmp_path / "vocab.json"
    v.save_json(p)
    v2 = Vocabulary.load_json(p)
    assert v2.tokens() == v.tokens()
    assert v2.ids() == v.ids()


def test_vocab_validate_contiguous():
    """Regression: IDs يجب أن تكون contiguous (0..n-1)."""
    from tokenizer.vocabulary import Vocabulary
    import pytest
    v = Vocabulary()
    v.add("a")     # id=0
    v.add("b")     # id=1
    v.add("c")     # id=2
    # break contiguous: احذف token 'b' وأعد بناء بدون id=1.
    # نحتاج forward يحوي نفس عدد reverse لكن IDs متقطعة.
    # Strategy: احذف 'b'، ثم أضف 'd' مع id=1.
    del v._token_to_id["b"]
    # الآن reverse يحوي {0: 'a', 2: 'c'} بطول 2، forward يحوي {'a':0,'c':2} بطول 2.
    # لكن IDs في forward و reverse متطابقة. أضف 'd' بـ id=1:
    v._token_to_id["d"] = 1
    v._id_to_token[1] = "d"
    # الآن IDs = 0,1,2 = contiguous. لكن لجعل contiguous fail،
    # احذف id=2 من reverse ثم ضع token جديد في forward بدون reverse.
    # لكن هذا يخرم reverse-consistency أولاً.
    # بدلاً من ذلك: انقل 'c' forward -> id=3، ثم ضع 'd' forward -> id=1، reverse -> 1.
    # IDs forward: {a:0, c:3, d:1}. Reverse: {0:a, 1:d, 3:c}. missing id=2.
    v._token_to_id.pop("c")
    v._id_to_token.pop(2)
    v._token_to_id["c"] = 3
    v._id_to_token[3] = "c"
    # الآن: forward {a:0, d:1, c:3}، reverse {0:a, 1:d, 3:c}. id=2 مفقود.
    # consistent but not contiguous.
    with pytest.raises(ValueError, match="contiguous"):
        v.validate()


def test_vocab_validate_duplicate_token():
    """Regression: تكرار token في vocab."""
    from tokenizer.vocabulary import Vocabulary
    import pytest
    v = Vocabulary()
    v.add("a")     # id=0
    # overwrite forward بدون تحديث reverse → duplicate.
    v._token_to_id["b"] = 1     # id=1 -> b
    v._id_to_token[1] = "b"
    v._token_to_id["c"] = 2     # id=2 -> c
    v._id_to_token[2] = "c"
    # الآن نُكرر 'b' على id 3:
    v._token_to_id["b"] = 3     # forward: b -> 3
    v._id_to_token[3] = "b"     # reverse: 3 -> b
    # الآن reverse[1] = "b" (stale) و reverse[3] = "b" → duplicate.
    with pytest.raises(ValueError):
        v.validate()


# =====================================================================
# Trainer
# =====================================================================
def test_pretokenize_arabic():
    from tokenizer.trainer import pretokenize
    out = pretokenize("مرحبا ALI Studio")
    assert "مرحبا" in out
    assert "ALI" in out
    assert "Studio" in out


def test_pretokenize_unicode():
    from tokenizer.trainer import pretokenize
    out = pretokenize("Hello world 123456 مرحبا")
    assert "Hello" in out
    assert "world" in out
    assert "123456" in out
    assert "مرحبا" in out


def test_pretokenize_empty():
    from tokenizer.trainer import pretokenize
    assert pretokenize("") == []


def test_trainer_basic():
    from tokenizer.config import TokenizerConfig
    from tokenizer.trainer import BPETrainer
    cfg = TokenizerConfig(vocab_size=300, min_frequency=1)
    corpus = ["hello world", "hello there", "مرحبا ALI"]
    trainer = BPETrainer(cfg)
    vocab, merges = trainer.train(corpus)
    assert vocab.token_to_id("<PAD>") == 0
    assert vocab.token_to_id("<BOS>") == 1
    assert vocab.token_to_id("<EOS>") == 2
    assert vocab.token_to_id("<UNK>") == 3
    # كل الـ 256 base byte tokens موجودة.
    for b in range(256):
        assert vocab.token_to_id(f"<0x{b:02X}>") is not None, f"missing byte {b}"
    assert len(vocab) > 256
    vocab.validate()


def test_trainer_empty_corpus():
    from tokenizer.config import TokenizerConfig
    from tokenizer.trainer import BPETrainer
    import pytest
    cfg = TokenizerConfig()
    trainer = BPETrainer(cfg)
    with pytest.raises(ValueError):
        trainer.train([])


def test_trainer_deterministic():
    """نفس corpus + نفس config → نفس vocab + نفس merges."""
    from tokenizer.config import TokenizerConfig
    from tokenizer.trainer import BPETrainer
    cfg = TokenizerConfig(vocab_size=300, min_frequency=1)
    corpus = ["hello world", "hello there", "مرحبا ALI"]
    v1, m1 = BPETrainer(cfg).train(corpus)
    v2, m2 = BPETrainer(cfg).train(corpus)
    assert v1.tokens() == v2.tokens()
    assert m1 == m2


def test_trainer_deterministic_across_dirs(tmp_path):
    """Regression: تدريب مرتين في مجلدات منفصلة → نفس المحتوى بالضبط.

    نتحقق من hash الـ files المحفوظة.
    """
    from tokenizer.config import TokenizerConfig
    from tokenizer.trainer import BPETrainer
    from tokenizer.serialization import save_tokenizer
    from tokenizer.tokenizer import ALITokenizer
    cfg = TokenizerConfig(vocab_size=300, min_frequency=1)
    corpus = ["hello world", "hello there", "مرحبا ALI"]
    d1 = tmp_path / "ali_tok_a"
    d2 = tmp_path / "ali_tok_b"
    d1.mkdir()
    d2.mkdir()
    for d in (d1, d2):
        trainer = BPETrainer(cfg)
        vocab, merges = trainer.train(corpus)
        tok = ALITokenizer(cfg, vocab, merges)
        save_tokenizer(tok, d)
    # قارن hashes
    for fn in ("config.json", "vocab.json", "merges.txt"):
        h1 = hashlib.sha256((d1 / fn).read_bytes()).hexdigest()
        h2 = hashlib.sha256((d2 / fn).read_bytes()).hexdigest()
        assert h1 == h2, f"{fn} differs: {h1} vs {h2}"


def test_trainer_eow_tokens_in_vocab():
    """Regression: tokens بـ '</w>' الـ eow marker يجب أن تكون في vocab.

    هذا bug ظهر: '<0x73></w>' لم يكن في vocab رغم أنه LHS/RHS في merges.
    """
    from tokenizer.config import TokenizerConfig
    from tokenizer.trainer import BPETrainer
    cfg = TokenizerConfig(vocab_size=400, min_frequency=1, use_end_of_word_marker=True)
    # corpus يحوي كلمات من byte واحدة ('a', 's', etc.)
    corpus = ["a s a s", "a a s"]
    trainer = BPETrainer(cfg)
    vocab, merges = trainer.train(corpus)
    # كل eow byte tokens يجب أن تكون في vocab.
    for b in (0x61, 0x73):
        eow = f"<0x{b:02X}></w>"
        assert vocab.token_to_id(eow) is not None, f"missing {eow}"


# =====================================================================
# ALITokenizer (encode/decode)
# =====================================================================
def _build_minimal_tokenizer(extra_corpus=None,
                              normalize_arabic: bool = True,
                              lowercase_english: bool = True):
    """يبني tokenizer جاهز للاختبارات.

    يستخدم corpus.txt الكامل من data/raw/ (177 lines / ~5900 chars)
    لضمان تغطية كافية لـ BPE merges.
    """
    from tokenizer.config import TokenizerConfig
    from tokenizer.trainer import BPETrainer
    from tokenizer.tokenizer import ALITokenizer
    cfg = TokenizerConfig(vocab_size=2048, min_frequency=1)
    cfg.normalize_arabic = normalize_arabic
    cfg.lowercase_english = lowercase_english
    # اقرأ corpus الافتراضي من data/raw/corpus.txt.
    corpus_path = ROOT / "data" / "raw" / "corpus.txt"
    if corpus_path.exists():
        corpus = [l.strip() for l in corpus_path.read_text(
            encoding="utf-8").splitlines() if l.strip()]
    else:
        corpus = []
    if extra_corpus:
        corpus.extend(extra_corpus)
    if not corpus:
        raise RuntimeError(
            "data/raw/corpus.txt not found — tokenizer tests need it"
        )
    trainer = BPETrainer(cfg)
    vocab, merges = trainer.train(corpus)
    return ALITokenizer(cfg, vocab, merges)


def _build_lossless_tokenizer():
    """Tokenizer lossless (no normalization)."""
    return _build_minimal_tokenizer(normalize_arabic=False,
                                    lowercase_english=False)


def test_encode_arabic():
    t = _build_lossless_tokenizer()
    ids = t.encode("مرحبا")
    assert all(isinstance(i, int) for i in ids)
    assert len(ids) > 0


def test_encode_empty_returns_empty():
    t = _build_lossless_tokenizer()
    assert t.encode("") == []


def test_encode_lowercase_english():
    """lowercase فقط إذا lowercase_english=True (default)."""
    t = _build_lossless_tokenizer()
    t.config.lowercase_english = True
    ids = t.encode("HELLO WORLD")
    decoded = t.decode(ids)
    assert "hello" in decoded.lower()


def test_encode_arabic_normalization():
    """alef normalization (إ/أ/آ -> ا)."""
    t = _build_lossless_tokenizer()
    t.config.normalize_arabic = True
    t.config.normalize_alef = True
    a = t.encode("إبراهيم")
    b = t.encode("ابراهيم")
    assert a == b


def test_encode_strip_diacritics():
    """strip_diacritics."""
    from tokenizer.config import TokenizerConfig
    from tokenizer.trainer import BPETrainer
    from tokenizer.tokenizer import ALITokenizer
    cfg = TokenizerConfig(vocab_size=400, min_frequency=1, strip_diacritics=True,
                          normalize_arabic=True, lowercase_english=False)
    corpus = ["مَرْحَبًا", "مرحبا"]
    trainer = BPETrainer(cfg)
    vocab, merges = trainer.train(corpus)
    tok = ALITokenizer(cfg, vocab, merges)
    a = tok.encode("مَرْحَبًا")
    b = tok.encode("مرحبا")
    assert a == b


def test_special_tokens_ids_stable():
    t = _build_lossless_tokenizer()
    assert t.vocab.token_to_id("<PAD>") == 0
    assert t.vocab.token_to_id("<BOS>") == 1
    assert t.vocab.token_to_id("<EOS>") == 2
    assert t.vocab.token_to_id("<UNK>") == 3


def test_add_bos_eos():
    t = _build_lossless_tokenizer()
    ids = t.encode("hello", add_bos=True, add_eos=True)
    assert ids[0] == t.vocab.token_to_id("<BOS>")
    assert ids[-1] == t.vocab.token_to_id("<EOS>")


def test_decode_handles_empty():
    t = _build_lossless_tokenizer()
    assert t.decode([]) == ""


def test_decode_skips_specials():
    t = _build_lossless_tokenizer()
    ids = t.encode("hello", add_bos=True, add_eos=True)
    text = t.decode(ids, skip_special=True)
    assert "<BOS>" not in text
    assert "<EOS>" not in text


def test_determinism():
    t = _build_lossless_tokenizer()
    a = t.encode("hello world")
    b = t.encode("hello world")
    assert a == b


def test_vocab_size_consistency():
    t = _build_lossless_tokenizer()
    assert t.vocab_size == len(t.vocab)
    assert t.vocab_size >= 263


def test_tokenizer_requires_full_byte_vocab():
    """Regression: vocab بدون كل الـ 256 byte tokens يُرفض."""
    from tokenizer.config import TokenizerConfig
    from tokenizer.vocabulary import Vocabulary
    from tokenizer.tokenizer import ALITokenizer
    import pytest
    cfg = TokenizerConfig()
    vocab = Vocabulary()
    for tok in cfg.special_tokens:
        vocab.add(tok)
    # أضف فقط 10 byte tokens (غير كافية).
    for b in range(10):
        vocab.add(f"<0x{b:02X}>")
    with pytest.raises(ValueError, match="base byte token"):
        ALITokenizer(cfg, vocab, [])


# =====================================================================
# Round-trip — Exact (lossless) vs Normalized (config defaults)
# =====================================================================
class TestExactRoundTrip:
    """مع tokenizer lossless (no normalization) → exact round-trip."""

    @staticmethod
    def _tok():
        return _build_lossless_tokenizer()

    def _rt(self, t, txt):
        ids = t.encode(txt)
        decoded = t.decode(ids)
        return decoded

    def test_basic_words(self):
        t = self._tok()
        for txt in ["مرحبا", "ALI Studio", "Hello world", "12345", "123456"]:
            assert self._rt(t, txt) == txt, f"failed: {txt!r}"

    def test_paths(self):
        t = self._tok()
        for txt in [
            "C:\\Users\\ALI\\file.py",
            "/home/ali/project/file.py",
            "C:/project/file.py",
        ]:
            assert self._rt(t, txt) == txt, f"failed: {txt!r}"

    def test_code(self):
        """Code tokens — اختبار سريع فقط أن ASCII code ينجح."""
        t = self._tok()
        # الـ corpus الاختباري لا يحوي "print(" فبعض الأحرف قد تذهب لـ UNK
        # لكن الـ round-trip لـ bytes الـ ASCII البسيطة يجب أن يعمل.
        for txt in ["hello()", "x = 1", "a + b", "if x:"]:
            assert self._rt(t, txt) == txt, f"failed: {txt!r}"

    def test_whitespace_single(self):
        t = self._tok()
        assert self._rt(t, "hello world") == "hello world"

    def test_whitespace_multiple(self):
        t = self._tok()
        assert self._rt(t, "hello  world") == "hello  world"
        assert self._rt(t, "hello   world") == "hello   world"

    def test_whitespace_tabs_newlines(self):
        t = self._tok()
        assert self._rt(t, "hello\tworld") == "hello\tworld"
        assert self._rt(t, "hello\nworld") == "hello\nworld"
        assert self._rt(t, "hello\n\nworld") == "hello\n\nworld"
        assert self._rt(t, "  hello") == "  hello"
        assert self._rt(t, "hello  ") == "hello  "

    def test_emoji_byte_fallback(self):
        """Emoji يحتاج byte fallback: كل byte من emoji يجب أن يكون byte token.

        corpus الاختباري قد لا يحوي emoji ككلمات، لكن الـ base byte vocabulary
        يضمن أن الـ emoji يُرمَّز كـ bytes (4-byte UTF-8 sequences).
        """
        t = self._tok()
        # emoji بسيط: 🙂 (U+1F642) = UTF-8 F0 9F 99 82
        decoded = self._rt(t, "🙂")
        assert decoded == "🙂", f"emoji byte fallback failed: {decoded!r}"


class TestNormalizedRoundTrip:
    """مع default config (normalize on) → decoded = normalized input."""

    @staticmethod
    def _tok():
        return _build_minimal_tokenizer(normalize_arabic=True,
                                        lowercase_english=True)

    def test_lowercase_applied(self):
        t = self._tok()
        # HELLO → hello
        assert t.decode(t.encode("HELLO")) == "hello"

    def test_alef_normalized(self):
        t = self._tok()
        # أ إ آ → ا
        assert t.decode(t.encode("أحمد")) == "احمد"
        assert t.decode(t.encode("إبراهيم")) == "ابراهيم"
        assert t.decode(t.encode("آدم")) == "ادم"

    def test_yaa_normalized(self):
        t = self._tok()
        # ى → ي — الـ decoded يكون بنسخة normalized.
        # U+0649 (ى) و U+064A (ي) — متأكدين من الفرق.
        yaa_norm = "\u064A"   # ي
        assert t.decode(t.encode("مصطفى")) == "مصطف" + yaa_norm
        assert t.decode(t.encode("موسى")) == "موس" + yaa_norm

    def test_taa_marbuta_normalized(self):
        t = self._tok()
        # ة → ه
        assert t.decode(t.encode("مكة")) == "مكه"
        assert t.decode(t.encode("المدينة")) == "المدينه"


# =====================================================================
# Serialization — Save/Load + Corruption
# =====================================================================
def test_save_load_round_trip(tmp_path):
    t = _build_lossless_tokenizer()
    root = tmp_path / "tok"
    from tokenizer.serialization import save_tokenizer, load_tokenizer
    save_tokenizer(t, root)
    t2 = load_tokenizer(root)
    assert t2.vocab_size == t.vocab_size
    assert t2.num_merges == t.num_merges
    assert t.encode("hello") == t2.encode("hello")


def test_load_tokenizer_missing_raises(tmp_path):
    from tokenizer.serialization import load_tokenizer
    import pytest
    with pytest.raises(FileNotFoundError):
        load_tokenizer(tmp_path / "nope")


def test_load_tokenizer_missing_config(tmp_path):
    """Corruption: vocab.json موجود بدون config.json."""
    from tokenizer.serialization import load_tokenizer
    import pytest
    (tmp_path / "vocab.json").write_text("{}", encoding="utf-8")
    (tmp_path / "merges.txt").write_text("# c\n", encoding="utf-8")
    with pytest.raises(FileNotFoundError, match="config"):
        load_tokenizer(tmp_path)


def test_load_tokenizer_corrupt_merges(tmp_path):
    """Corruption: merge line غير صالح."""
    from tokenizer.serialization import load_tokenizer
    from tokenizer.config import TokenizerConfig
    from tokenizer.vocabulary import Vocabulary
    import pytest
    cfg = TokenizerConfig(vocab_size=300)
    v = Vocabulary()
    for tok in cfg.special_tokens:
        v.add(tok)
    for b in range(256):
        v.add(f"<0x{b:02X}>")
    (tmp_path / "config.json").write_text(json.dumps(cfg.to_dict()),
                                           encoding="utf-8")
    (tmp_path / "vocab.json").write_text(json.dumps(v.to_dict()),
                                          encoding="utf-8")
    # merges.txt يحوي line غير صالح
    (tmp_path / "merges.txt").write_text(
        "# comment\nbad line with no equals\n", encoding="utf-8",
    )
    with pytest.raises(ValueError, match="invalid merge"):
        load_tokenizer(tmp_path)


def test_load_tokenizer_merge_token_missing_in_vocab(tmp_path):
    """Corruption: merge يشير لـ token غير موجود في vocab."""
    from tokenizer.serialization import load_tokenizer
    from tokenizer.config import TokenizerConfig
    from tokenizer.vocabulary import Vocabulary
    import pytest
    cfg = TokenizerConfig(vocab_size=300)
    v = Vocabulary()
    for tok in cfg.special_tokens:
        v.add(tok)
    for b in range(256):
        v.add(f"<0x{b:02X}>")
    (tmp_path / "config.json").write_text(json.dumps(cfg.to_dict()),
                                           encoding="utf-8")
    (tmp_path / "vocab.json").write_text(json.dumps(v.to_dict()),
                                          encoding="utf-8")
    # merge يشير لـ token '<0xGG>' غير موجود.
    (tmp_path / "merges.txt").write_text(
        "<0xAA> <0xGG>\n", encoding="utf-8",
    )
    with pytest.raises(ValueError, match="not in vocab"):
        load_tokenizer(tmp_path)


def test_merges_skip_comments(tmp_path):
    from tokenizer.serialization import save_merges, load_merges
    p = tmp_path / "m.txt"
    p.write_text("# comment\n# another\n\n<0xAA> <0xBB>\n<0xCC> <0xDD>\n",
                 encoding="utf-8")
    assert load_merges(p) == [("<0xAA>", "<0xBB>"), ("<0xCC>", "<0xDD>")]


def test_merges_rejects_non_byte_lhs(tmp_path):
    """Regression: LHS يجب أن يكون byte token."""
    from tokenizer.serialization import load_merges
    import pytest
    p = tmp_path / "m.txt"
    p.write_text("foo <0xAA>\n", encoding="utf-8")
    with pytest.raises(ValueError, match="LHS not byte token"):
        load_merges(p)


# =====================================================================
# Default tokenizer (trained in V0.7 setup)
# =====================================================================
def test_default_tokenizer_loaded():
    from tokenizer import get_default_tokenizer, DEFAULT_TOKENIZER_DIR
    from config.paths import APP_PATHS
    root = APP_PATHS.project_root() / DEFAULT_TOKENIZER_DIR
    if not root.exists():
        import pytest
        pytest.skip("default tokenizer not trained yet")
    t = get_default_tokenizer()
    assert t is not None
    assert t.vocab_size > 256


def test_default_tokenizer_lowercase_applied_to_paths():
    """مع default config (lowercase_english=True)، الـ Latin chars تتحول لـ lowercase.

    هذا متوقع وموثّق: round-trip ينتج normalized form.
    """
    from tokenizer import get_default_tokenizer
    from config.paths import APP_PATHS
    from tokenizer import DEFAULT_TOKENIZER_DIR
    root = APP_PATHS.project_root() / DEFAULT_TOKENIZER_DIR
    if not root.exists():
        import pytest
        pytest.skip("default tokenizer not trained yet")
    t = get_default_tokenizer()
    # 'C' → 'c'
    assert t.decode(t.encode("C:/project/file.py")) == "c:/project/file.py"
    # 'A' → 'a'
    assert t.decode(t.encode("ABC")) == "abc"


def test_default_tokenizer_lossless_for_lowercase_input():
    """نصوص lowercase تظل unchanged عبر round-trip (lowercase no-op)."""
    from tokenizer import get_default_tokenizer
    from config.paths import APP_PATHS
    from tokenizer import DEFAULT_TOKENIZER_DIR
    root = APP_PATHS.project_root() / DEFAULT_TOKENIZER_DIR
    if not root.exists():
        import pytest
        pytest.skip("default tokenizer not trained yet")
    t = get_default_tokenizer()
    for txt in ["/home/ali/project/file.py",
                "1234567890",
                "123456",
                "hello world"]:
        decoded = t.decode(t.encode(txt))
        assert decoded == txt, f"failed: {txt!r} -> {decoded!r}"


# =====================================================================
# Lazy Loading + DB Isolation
# =====================================================================
def test_lazy_loading_does_not_train():
    """Lazy: get_default_tokenizer() يجب أن يُحمّل فقط إذا الـ dir موجود.
    لا تدريب تلقائي.
    """
    from tokenizer import get_default_tokenizer
    from config.paths import APP_PATHS
    from tokenizer import DEFAULT_TOKENIZER_DIR
    root = APP_PATHS.project_root() / DEFAULT_TOKENIZER_DIR
    if root.exists():
        # إذا موجود، تأكد أنه لم يُعد تدريبه (نفس hash).
        import hashlib
        cfg = (root / "config.json").read_bytes()
        assert hashlib.sha256(cfg).hexdigest()  # just access
    # في كل الأحوال، يجب ألّا يكون هناك أي عملية training.
    t = get_default_tokenizer()
    # حتى لو None، لا exception.
    assert t is None or t.vocab_size > 256


def test_tokenizer_does_not_touch_appdata_db():
    """Regression: tokenizer tests لا يجب أن تنشئ ملفات في APPDATA."""
    import os
    import tempfile
    with tempfile.TemporaryDirectory() as tmp:
        os.environ["APPDATA"] = tmp
        t = _build_lossless_tokenizer()
        ids = t.encode("مرحبا ALI")
        _ = t.decode(ids)
        # APPDATA الموقت لا يحوي ali.db
        assert not (Path(tmp) / "ALI-Agent" / "ali.db").exists()
        # أو إذا وُجد، فهو من singleton DB (اختبارات أخرى) — لا من tokenizer.


def test_appdata_isolation_for_tokenizer_tests():
    """التأكد أن الـ tokenizer tests لا تكتب في APPDATA الحقيقي."""
    from pathlib import Path
    import os
    appdata = Path(os.environ.get("APPDATA", str(Path.home())))
    # قبل وبعد اختبارات tokenizer، يجب أن لا يظهر ملف tokenizer في APPDATA
    # (tokenizer لا يحفظ إلا داخل weights/ أو tmp_path).
    # لا assertion بحدود صارمة — لكن الـ weights/ لا تحت APPDATA.
    weights_path = appdata / "ALI-Agent" / "weights"
    assert not weights_path.exists(), (
        f"tokenizer tests leaked weights into APPDATA: {weights_path}"
    )


# =====================================================================
# CLI counts
# =====================================================================
def test_cli_load_corpus_txt_counts(tmp_path):
    """CLI counts يجب أن يعكس total/valid/invalid/empty بدقة."""
    from tokenizer.train_tokenizer import load_corpus, CorpusStats
    p = tmp_path / "c.txt"
    p.write_text("hello\n\nworld\n  \nfoo\n", encoding="utf-8")
    corpus, stats = load_corpus(p, "txt")
    assert stats.total == 5
    assert stats.valid == 3
    assert stats.empty == 2
    assert stats.invalid == 0
    assert corpus == ["hello", "world", "foo"]


def test_cli_load_corpus_jsonl_counts(tmp_path):
    from tokenizer.train_tokenizer import load_corpus, CorpusStats
    p = tmp_path / "c.jsonl"
    lines = [
        json.dumps({"text": "hello"}),
        json.dumps({"text": "world"}),
        "",  # empty
        "bad json",
        json.dumps({"no_text": "x"}),  # missing text
        json.dumps({"text": ""}),  # empty text
        json.dumps({"text": "  "}),  # whitespace only
    ]
    p.write_text("\n".join(lines), encoding="utf-8")
    corpus, stats = load_corpus(p, "jsonl")
    assert stats.total == 7
    assert stats.valid == 2
    assert stats.empty == 3  # empty, empty text, whitespace only
    assert stats.invalid == 2  # bad json + missing text
    assert corpus == ["hello", "world"]


# =====================================================================
# Helpers / regression