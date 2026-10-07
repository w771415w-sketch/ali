# -*- coding: utf-8 -*-
"""Text normalization, secret redaction and stable hashes."""
from __future__ import annotations
import hashlib, re, unicodedata
from typing import Tuple

SECRET_PATTERNS = [
    re.compile(r'(?i)\b(api[_-]?key|secret|token|password|passwd|access[_-]?token)\s*[:=]\s*["\']?[^\s"\']{8,}["\']?'),
    re.compile(r'-----BEGIN [A-Z ]+ PRIVATE KEY-----.*?-----END [A-Z ]+ PRIVATE KEY-----', re.S),
    re.compile(r'(?i)\bsk-[A-Za-z0-9_-]{20,}\b'),
    re.compile(r'(?i)\bgh[pousr]_[A-Za-z0-9_]{20,}\b'),
]

def normalize_text(text: str) -> str:
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = unicodedata.normalize("NFKC", text)
    text = re.sub(r'[ \t]+', ' ', text)
    text = re.sub(r'\n{3,}', '\n\n', text)
    return text.strip()

def redact_secrets(text: str) -> Tuple[str, bool]:
    changed = False
    out = text
    for p in SECRET_PATTERNS:
        out2, n = p.subn('[REDACTED_SECRET]', out)
        if n: changed = True; out = out2
    return out, changed

def normalized_hash(text: str) -> str:
    return hashlib.sha256(normalize_text(text).encode('utf-8')).hexdigest()

def fingerprint_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()
