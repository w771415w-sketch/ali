# ALI AI — Knowledge Base

Project-specific knowledge accumulated during development.
Updated: 30 September 2026 (V0.7.2 audit)

---

## Architecture Decisions

### Word Boundary Contract (Option A)

**Decision:** `</w>` is internal BPE representation, NEVER in decoded text.

**Rationale:**
- BPE training uses `</w>` to mark word boundaries (GPT-2 style)
- After encode→decode round-trip, `</w>` is stripped
- This is documented and tested

**Evidence:** `tokenizer/tokenizer.py:24-29` (docstring), 13/13 round-trip tests pass.

---

### Special Tokens Case Insensitivity

**Decision:** When `lowercase_english=True` (default), special tokens are matched case-insensitively.

**Behavior:**
- `<USER>`, `<user>`, `<User>`, `<UsEr>` all → `[user_id]`
- `<UNKNOWN>`, `<USER123>` → bytes (NOT special)

**Evidence:** `tests/test_tokenizer_v072.py::TestSpecialTokensReal`

---

### Byte Fallback for Lossless Decoding

**Decision:** When BPE produces a token not in vocab, decompose it to its constituent byte tokens.

**Rationale:**
- Guarantees byte-level losslessness for any Unicode input
- Trade-off: word-boundary metadata is lost in fallback
- This is the only way to handle unseen text without corpus-specific vocab

**Evidence:** `tokenizer/tokenizer.py::_byte_fallback`, 18/18 unseen texts round-trip losslessly.

---

### Manifest-Based Integrity

**Decision:** All artifact integrity verified through `manifest.json` with SHA-256 hashes.

**Behavior:**
- `config.json`, `vocab.json`, `merges.txt` are hashed on save
- `manifest.json` records hashes + metadata (version, algorithm, counts)
- `load_tokenizer()` rejects artifact if any hash mismatches

**Evidence:** `tokenizer/serialization.py::_validate_tokenizer`, 4/4 corruption scenarios rejected.

---

## Tokenizer Bug Fixes (V0.7.2 Audit)

### Dead Imports Removed

**Before:**
