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
