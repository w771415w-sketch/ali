# -*- coding: utf-8 -*-
"""ALI Tokenizer — BPE tokenizer مستقل، يدعم العربية، بدون أي نموذج خارجي.

PUBLIC API (stable for V0.8):
    ALITokenizer(config, vocab, merges)
        .encode(text, add_bos, add_eos, special_tokens) -> List[int]
        .decode(ids, skip_special) -> str
        .normalize(text) -> str
        .save(path)
        ALITokenizer.load(path)
        .vocab_size, .special_tokens
        .pad_id, .bos_id, .eos_id, .unk_id
        .user_id, .assistant_id, .system_id
        .token_to_id(...), .id_to_token(...)
        .is_special_token(...), .is_byte_token(...)

ARCHITECTURE:
    config     →  TokenizerConfig
    vocabulary →  Vocabulary (token <-> id)
    trainer    →  BPETrainer (corpus → vocab + merges)
    tokenizer  →  ALITokenizer (encode/decode + normalize)
    serialization → save/load (atomic writes + manifest + hashes)
"""

from tokenizer.config import TokenizerConfig, DEFAULT_SPECIAL_TOKENS
from tokenizer.vocabulary import Vocabulary
from tokenizer.trainer import (
    BPETrainer, pretokenize,
    _word_to_symbols, _is_valid_byte_token, _merge_to_token,
)
from tokenizer.tokenizer import (
    ALITokenizer,
    normalize_arabic_text,
)
from tokenizer.serialization import (
    TokenizerPaths,
    save_tokenizer, load_tokenizer,
    save_merges, load_merges,
    TOKENIZER_VERSION, ALGORITHM,
)

DEFAULT_TOKENIZER_DIR = "weights/tokenizer"


def get_default_tokenizer():
    """Lazy load للـ tokenizer الافتراضي (يستخدم في الـ inference).

    Returns None إذا لم يُدرَّب بعد.
    """
    from config.paths import APP_PATHS
    root = APP_PATHS.project_root() / DEFAULT_TOKENIZER_DIR
    if not root.exists():
        return None
    try:
        return load_tokenizer(root)
    except Exception:
        return None


__all__ = [
    "TokenizerConfig", "DEFAULT_SPECIAL_TOKENS",
    "Vocabulary",
    "BPETrainer", "pretokenize",
    "_word_to_symbols", "_is_valid_byte_token", "_merge_to_token",
    "ALITokenizer",
    "normalize_arabic_text",
    "TokenizerPaths",
    "save_tokenizer", "load_tokenizer",
    "save_merges", "load_merges",
    "TOKENIZER_VERSION", "ALGORITHM",
    "DEFAULT_TOKENIZER_DIR",
    "get_default_tokenizer",
]
