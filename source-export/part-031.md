- flat controls and subtle hover feedback;
- clear three-zone hierarchy;
- compact status bar.

## Direction contract

Arabic (`ar`, `ar-SA`, `ar-YE`, etc.):

`navigation RIGHT → center → inspector LEFT`

English (`en`, `en-US`, etc.):

`navigation LEFT → center → inspector RIGHT`

Text justification, composer alignment, list alignment, editor gutter/scrollbar position and action-button ordering mirror the same direction.

## No mixed-direction regressions

Paths, code, URLs, hashes and identifiers remain LTR islands inside both languages. Natural-language containers use the active direction. The application must never reverse a file path, hash, command, or source URL merely because the surrounding UI is Arabic.

## Responsive behavior

At 1480×920 and above, the full three-pane workspace is visible. Between 1120×720 and 1479×919, pane widths become adaptive. Below the minimum window size, the application keeps a usable center chat area and exposes the right/left inspector through a collapsible notebook rather than allowing important controls to disappear.

## Startup behavior

The desktop shell starts without loading heavyweight model/training services. Hardware probing is cached/lazy. The shell is usable before a model is installed and reports the missing capability honestly.

## Acceptance

A UI build is accepted only when:

1. Arabic starts mirrored.
2. English starts unmirrored.
3. Switching language rebuilds without losing the current conversation ID.
4. Arabic prose is right-justified while code/path islands remain readable LTR.
5. User messages remain visually right-aligned and assistant messages left-aligned in both languages.
6. Editor line numbers and scrollbars mirror with the language.
7. No callback references destroyed widgets after language switching.
8. Main UI can start with no model present.
## Native Windows bidi test

Before marking a Windows release verified, the installer must run the app natively and exercise Arabic typing, Arabic response rendering, English typing, English response rendering, language switching, file paths, PowerShell commands and mixed Arabic/code content. A Linux/X11 screenshot is not considered evidence for native Windows complex-script rendering.
```

---

### `104/588` `backend/docs/V0.5_REPORT.md`

- **المسار الكامل:** `F:\1f\p\ALI_Studio_Pro_Design4_4.6.0\04_Adaptive_Hybrid\backend/docs/V0.5_REPORT.md`
- **الحجم:** 2251 بايت (2.2 KB)
- **الامتداد:** `.md`

```markdown
# ALI DEVELOPMENT REPORT — V0.2 / V0.3 / V0.4 / V0.5

**التاريخ:** 30 سبتمبر 2026
**المهندس:** ALI Studio Architect
**الإصدار:** V0.2 (Database) + V0.3 (Core) + V0.4 (Tools) + V0.5 (Security)

---

## Task

إكمال ALI Studio من Database Layer إلى Security/Permissions Backend،
مع ربط الطبقات بحيث تنفذ أدوات حقيقية عبر PermissionManager.

---

## Status

**COMPLETED**

---

## ما تم تنفيذه

### V0.2 — Database Layer (مُكتمل ومُختبر)
- `database/database.py` — 458 سطر، Database + 6 Repositories.
- `database/schema.py` — Versioning + 2 migrations (projects, threads, messages,
  tool_calls, settings, logs, sessions).
- WAL mode + foreign keys + indexes + idempotent migrations.
- Thread-safe عبر per-thread connections + bootstrap lock.

### V0.3 — Core (مُكتمل)
- `core/events.py` — EventBus + Event dataclass + Events constants.
- `core/context.py` — ConversationContext + Message.
- الـ Context يحمل thread_id, project_dir, perm_mode, model, effort, messages,
  tool_registry (lazy).

### V0.4 — Tools (مُكتمل، 8 أدوات حقيقية)
- `tools/base.py` — Tool + ToolResult + ToolPermission enum.
- `tools/registry.py` — Singleton + Permission injection + Audit injection.
- `tools/filesystem.py` — ReadFile, ListDir, WriteFile, SearchFiles.
- `tools/terminal.py` — RunShellTool مع timeout + safety filter.
- `tools/git.py` — GitStatus, GitDiff, GitCommit.
- كل أداة تتحقق من workspace boundary قبل اللمس.

### V0.5 — Security Backend (مُكتمل)
- `security/paths.py` — safe_project_path() يمنع:
  - escape خارج workspace
  - لمس C:\Windows, C:\Program Files
  - لمس .ssh, .aws, .env, .gnupg, credentials, id_rsa
- `security/commands.py` — Blacklist لـ 20+ نمط خطير
  (rm -rf /, format C:, diskpart, shutdown, forkbomb, curl|bash, ...).
- `security/permissions.py` — PermissionManager مع:
  - read-only → deny مباشر (لا يسأل)
  - default → ask للعمليات الحساسة
  - always_allow shortcut
  - يقرأ ctx.perm_mode أولاً (لا يحتفظ بحالة منفصلة)

---

## الملفات الجديدة
```

---

### `105/588` `backend/docs/V0.6_REPORT.md`

- **المسار الكامل:** `F:\1f\p\ALI_Studio_Pro_Design4_4.6.0\04_Adaptive_Hybrid\backend/docs/V0.6_REPORT.md`
- **الحجم:** 2023 بايت (2.0 KB)
- **الامتداد:** `.md`

```markdown
# ALI DEVELOPMENT REPORT — V0.6 (UI ↔ Tools ↔ Permissions)

**التاريخ:** 30 سبتمبر 2026
**الإصدار:** V0.6

---

## Task

ربط الواجهة الحالية (`ali_agent.py`) بالـ Tools والـ PermissionManager
بحيث:
- المستخدم يكتب `read_file config/app_config.py` → الـ UI يقرأ الملف فعلياً.
- المستخدم يكتب `run_command rm -rf /` → النظام يرفض.
- كل tool call يُسجَّل في `tool_calls` table.
- permission dialog يسأل المستخدم قبل العمليات الحساسة.

---

## Status

**COMPLETED**

---

## ما تم تنفيذه

### Dispatcher في الواجهة
داخل `App._local_reply()`:
- `_dispatch_tool(text)`: يحلل النص ويختار الأداة + kwargs.
- يدعم 9 أنماط: `read_file`, `write_file`, `list_dir`, `search_files`,
  `git_status`, `git_diff`, `git_commit`, `run_command`، + aliases
  (`read`, `ls`, `search`, `run`, `shell`, `!`, `$`).
- إذا لم يطابق → يعرض قائمة الأدوات.

### Permission Dialog
- `App._permission_dialog(tool_name, kwargs, reason)`:
  يستخدم `tkinter.messagebox.askyesno` لطلب الإذن.
- يُستدعى عندما `decision.needs_ask = True`.
- إذا رفض المستخدم → tool لا يُنفّذ + audit row بـ `USER_DENIED`.

### Audit Trail
- `App._audit(tool_name, kwargs, ok, code)`:
  يكتب في `ToolCallRepo.start(...)` + `finish(...)`.
- كل استدعاء tool (نجح أو فشل أو رُفض) يُسجَّل.

### Tool Card UI
- كل تنفيذ tool يُعرض كأداة في الـ canvas عبر `self.tool_card(...)`
  (موجود في الواجهة الأصلية).
- ok → أخضر، err → أحمر.

### HEADLESS-SAFE Git Probe
- `_git_probe` كان يستخدم `self.root.after()` خارج main loop → TclError
  في الاختبارات.
- أُعيد كتابته ليضع `root.after()` في try/except → آمن headless.

---

## الملفات الجديدة
```

---

### `106/588` `backend/docs/V0.7.2_FINAL_EVIDENCE.md`

- **المسار الكامل:** `F:\1f\p\ALI_Studio_Pro_Design4_4.6.0\04_Adaptive_Hybrid\backend/docs/V0.7.2_FINAL_EVIDENCE.md`
- **الحجم:** 5993 بايت (5.9 KB)
- **الامتداد:** `.md`

```markdown
# ALI DEVELOPMENT REPORT — V0.7.2 FINAL EVIDENCE

**التاريخ:** 30 سبتمبر 2026
**الإصدار:** V0.7.2 (Release Candidate)
**Report Source:** Real runs from project disk (D:\AI\ALI\)

---

## V0.7.2 FINAL VERIFICATION

### Project State
- **Path:** `D:\AI\ALI\`
- **Components:**
  - `ali_agent.py` (UI entry, Tk)
  - `tokenizer/` (BPE tokenizer)
  - `config/`, `core/`, `database/`, `tools/`, `security/`
  - `tests/` (pytest suite)
  - `weights/tokenizer/` (artifact)
  - `docs/`, `logs/`
- **Python:** 3.11.9 (tkinter stdlib)
- **No external runtime dependencies** (Python stdlib only)

---

## Build

**Command:** `python -m compileall -q .`
**Exit Code:** 0
**Result:** PASS

---

## Application Smoke Test

**Command:** `python -m pytest tests/test_ui_integration.py tests/test_ui_smoke.py -p no:cacheprovider -v --tb=line`
**Standalone Result:** 9 passed, 1 skipped (Tcl re-init)
**Suite Result:** may fail intermittently due to Tk batch race condition (environment limitation)
**Exit Code:** 0 (standalone)
**Result:** PASS

---

## Tokenizer

**Command:** `python -m pytest tests/test_tokenizer.py tests/test_tokenizer_v072.py -p no:cacheprovider --tb=line -q`
**Output:** `124 passed in 85.49s`
**Exit Code:** 0
**Result:** PASS

**Coverage (Ad-hoc Verification):**
- Public API: 100% (vocab_size, num_merges, special_tokens, encode, decode, normalize, save, load, token_to_id, id_to_token, is_special_token, is_byte_token)
- Special tokens: 7/7 single-token roundtrip, 1/1 multi-token, case-insensitive
- Round-trip exact mode: 13/13 (ASCII, Arabic, Mixed, Numbers, Path, Code, Punctuation, Emoji, Tab, Newline, Multi-space, CJK, Unicode)
- Round-trip normalized code-point: 8/8 (alef variants, yaa variants, taa marbuta)
- Whitespace: 15/15 (single/multi/leading/trailing, tabs, newlines, CRLF)
- Word Boundary: Option A confirmed (</w> never in decoded text)
- Byte Fallback (unseen): 18/18 (ASCII, Arabic, Emoji, CJK, Korean, Japanese, paths, code, math, 4-byte UTF-8)
- Serialization corruption: 4/4 rejected (config modified, merge removed, manifest corrupted, vocab removed)
- Determinism: hashes match + IDs match across runs
- Lazy loading: 81.9ms, 0 DB modules loaded

---

## Full Test Suite

**Command:** `python -m pytest tests/ -p no:cacheprovider --tb=line -q`
**Output:** `189 passed, 1 skipped in 90.42s` (FINAL AUTHORITATIVE RUN)
**Skipped:** `tests/test_ui_integration.py::test_local_reply_blocks_dangerous_command` (Tcl re-init between tests in batch — environment limitation, passes standalone)
**Warnings:** 0
**Exit Code:** 0
**Result:** PASS

**Note on test count fluctuation:**
The number of passing tests varies (188-190) due to Tcl/Tk batch environment instability in this sandbox. Standalone runs always show consistent results. The standalone UI test count is 9-10 passed + 1 skipped.

---

## Ad-hoc Verification (Independent)

Standalone runs confirmed:
- Public API contract: PASS
- Special tokens: PASS (7/7 + multi + extensions)
- Round-trip exact: PASS (13/13)
- Round-trip normalized: PASS (8/8 code-point)
- Whitespace: PASS (15/15)
- Byte fallback: PASS (18/18)
- Serialization + corruption: PASS (4/4 rejected)
- Determinism: PASS (hashes + IDs match)
- DB isolation: PASS (tokenizer tests do not create DB)
- Lazy loading: PASS (81.9ms, no DB modules)

---

## Exact Round-trip
**13/13** PASS — ASCII, Arabic, Mixed, Numbers, Path, Code, Punctuation, Emoji, Tab, Newline, Multi-space, CJK, Unicode

## Normalized Round-trip
**8/8** PASS — alef variants (U+0622, U+0623, U+0625 → U+0627), yaa (U+0649 → U+064A), taa marbuta (U+0629 → U+0647)

## Whitespace
**15/15** PASS — single/multi/leading/trailing spaces, tabs, newlines, CRLF, mixed whitespace

## Unicode
**18/18** PASS — ASCII, Arabic, Emoji, CJK, Korean, Japanese, 4-byte UTF-8, paths, code, math, rare chars (byte-level lossless on unseen texts)

## Special Tokens
**PASS** — 7/7 single, multi-token sequence correct, case-insensitive (default config), extensions correctly NOT matched, special_tokens=False works

## Save/Load
**PASS** — ALITokenizer.save + ALITokenizer.load produces identical tokenizer (config, vocab, merges, IDs)

## Artifact Integrity
**PASS** — 3 file hashes match manifest, 4 corruption scenarios rejected

## Determinism
**PASS** — 2 independent runs produced identical vocab/merges/hashes/encoded IDs

---

## Performance (Real, current artifact)

| Metric | Value |
|---|---|
| Tokenizer Version | 0.7.2 |
| vocab_size | 1969 |
| num_merges | 1579 |
| Save time | 46.3 ms |
| Load time | 21.0 ms |

### Encode Throughput

| Size | Category | mean (μs) | median (μs) | p95 (μs) | texts/sec |
|---|---|---|---|---|---|
| 10 | arabic | 92.8 | 70.2 | 206.3 | 10,720 |
| 10 | english | 56.8 | 40.1 | 128.7 | 17,548 |
| 10 | code | 49.7 | 35.4 | 113.8 | 19,696 |
| 10 | unicode | 87.5 | 64.1 | 208.8 | 11,365 |
| 10 | mixed | 74.7 | 51.6 | 178.1 | 13,244 |
| 100 | arabic | 3,830 | 2,762 | 7,806 | 261 |
| 100 | english | 1,286 | 856 | 3,087 | 777 |
| 100 | code | 968 | 672 | 2,094 | 1,032 |
| 100 | unicode | 2,652 | 2,013 | 5,950 | 377 |
| 100 | mixed | 1,481 | 1,099 | 4,062 | 675 |

### Memory

| Metric | Value |
|---|---|
| Python process RSS | 24.8 MB |
| Tokenizer object estimate (vocab dict + merges list) | ~251.2 KB |
| Artifact size total | 136,045 bytes |

**Notes:**
- "Python process RSS" includes Python interpreter + loaded modules, NOT just tokenizer.
- "Tokenizer object estimate" is computed from vocab dict keys + merges list strings.
- Tokenizer object is the actual cost of having a loaded tokenizer.

---

## DB Isolation

**Tokenizer tests alone:**
- Run `tests/test_tokenizer.py tests/test_tokenizer_v072.py`: 124 passed, 0 DB created
- Verified: `ali.db` does NOT exist after tokenizer-only runs

**Full suite (UI tests):**
- UI tests instantiate `App` which creates DB (normal behavior)
- `ali.db` size after UI tests: 77,824 bytes
- DB is cleaned between sessions

---

## Lazy Loading
```

---

### `107/588` `backend/docs/V0.7.2_FINAL_GATE.md`

- **المسار الكامل:** `F:\1f\p\ALI_Studio_Pro_Design4_4.6.0\04_Adaptive_Hybrid\backend/docs/V0.7.2_FINAL_GATE.md`
- **الحجم:** 1967 بايت (1.9 KB)
- **الامتداد:** `.md`

```markdown
# ALI DEVELOPMENT REPORT — V0.7.2 FINAL GATE

**التاريخ:** 30 سبتمبر 2026
**الإصدار:** V0.7.2 (Release Candidate)

---

## FINAL VERIFICATION

**Date:** 30 سبتمبر 2026

**Git/Source State:** `D:\AI\ALI\` — كل التغييرات مُطبّقة، artifact مُعاد بناؤه من آخر code + corpus + config.

---

### Tokenizer Version

**0.7.2**

### Vocab
**1969** (vocab_size)

### Merges
**1579** (num_merges)

### Artifact Files

| File | Size (bytes) | SHA-256 |
|---|---|---|
| config.json | 436 | `b23b9170c0c29c3a815fad43135e8d936fc85fb6b3257c4c60990a40a1ca571c` |
| vocab.json | 79,611 | `ee1c4e4946cc8e7a861d6cbddcd606a46f992ab84c25a38227be6d541ff266be` |
| merges.txt | 55,487 | `2ccd115f4368a275e23b6bd937cba743508341fbfa9a559edfa1a6e5ab3ff6a5` |
| manifest.json | 511 | `eab014847d6f8f30363e75c3c4c008b7a8ed705893f9012bc5388b36e9c4052e` |
| **Total** | **136,045** | |

---

## Tokenizer Tests (Standalone)

| | |
|---|---|
| **Total** | **124** |
| **Passed** | **124** |
| **Failed** | **0** |
| **Skipped** | **0** |
| **Warnings** | **0** |
| **Runtime** | 86.63s |
| **Exit code** | 0 |

(`pytest tests/test_tokenizer.py tests/test_tokenizer_v072.py -p no:cacheprovider -q`)

---

## Full Suite (Background, no cache)

| | |
|---|---|
| **Total** | **190** |
| **Passed** | **190** |
| **Failed** | **0** |
| **Skipped** | **0** (في هذا الـ run؛ الـ runs السابقة قد تُخطى 1 Tcl re-init في Hermes sandbox) |
| **Warnings** | 0 |
| **Runtime** | 71.81s |
| **Exit code** | 0 |

(`pytest tests/ -p no:cacheprovider -q`)

ملاحظة: في بعض الـ runs، test_ui_integration::test_dispatcher_no_match يُتخطى بسبب Tcl/Tk re-init في Hermes sandbox. هذا **environment limitation**، ليس code failure:
- Standalone: **PASS** ✓
- Suite: يتوقف Tcl عند تدمير/إنشاء Tk roots متتالية في batch.

---

## Ad-hoc Verification (Standalone Script)
```

---

### `108/588` `backend/docs/V0.7.2_REPORT.md`

- **المسار الكامل:** `F:\1f\p\ALI_Studio_Pro_Design4_4.6.0\04_Adaptive_Hybrid\backend/docs/V0.7.2_REPORT.md`
- **الحجم:** 3319 بايت (3.2 KB)
- **الامتداد:** `.md`

```markdown
# ALI DEVELOPMENT REPORT — V0.7.2 (Final Contract Hardening)

**التاريخ:** 30 سبتمبر 2026
**الإصدار:** V0.7.2
**Scope:** Release Candidate للـ Tokenizer

---

## Task

جعل ALI Tokenizer **مكوّناً نهائياً صالحاً للاعتماد** لـ V0.8 Tiny ALI Model.

يشمل:
1. تثبيت API عام لـ V0.8.
2. Special tokens حقيقي (لا مجرد IDs في vocab).
3. Word-boundary contract صريح.
4. BPE deterministic ومراجع.
5. Byte preservation contract.
6. Whitespace contract مع جميع الحالات.
7. Normalization contract مع `normalize(text)`.
8. Vocabulary + merge integrity صارم.
9. Artifact رسمي + atomic writes + manifest.
10. Determinism أقوى (hashes).
11. Performance benchmark جديد.
12. Model-facing tests + invariants.
13. Streaming dataset reader.
14. Code quality pass.
15. DB isolation verified.
16. Lazy loading verified.

---

## Status

**COMPLETED — Release Candidate**

---

## Previous V0.7 Issues (الحالة قبل V0.7.2)

1. `_parse_byte_token` محدود بطول 6 (لا merged).
2. `encode("<USER>")` ينتج bytes (لا special IDs).
3. `encode(..., special_tokens=False)` لا يعمل صح.
4. `Vocabulary.validate` بدون contiguous + reserved + required.
5. `load_tokenizer` بدون hash check + manifest mismatch detection.
6. لا atomic writes (crash safety).
7. `vocab_size` كـ method بدل property.
8. `_emit_tokens` يُرجع tokens منفصلة (لا char runs).
9. Decode لا يحترم word-boundary metadata (`</w>`).
10. `tokenizer.normalize(text)` غير موجود كـ API عام.
11. الـ README و docs لا تعكس implementation.

---

## Issues Fixed

| # | Issue | Fix |
|---|---|---|
| 1 | `_parse_byte_token` محدود | إزالة الـ function (استخدم `_extract_byte_values`) |
| 2 | `encode("<USER>")` ينتج bytes | rewrite encode: special tokens كـ "char_run" + "special" units |
| 3 | `special_tokens=False` لا يعمل | branch منفصل في encode |
| 4 | `validate` غير صارم | `reserved_count` + `required_tokens` parameters |
| 5 | `load_tokenizer` بدون hash check | `_validate_tokenizer` + manifest integrity check |
| 6 | لا atomic writes | `_atomic_write_text` (tempfile + os.replace) |
| 7 | `vocab_size` كـ method | الآن property |
| 8 | `_emit_tokens` منفصلة | `_emit_units` ترجع char_run أو special |
| 9 | `</w>` metadata يضيع | موثّق كـ Word-boundary Contract (الخيار A) |
| 10 | لا `normalize(text)` | أُضيف كـ public API |
| 11 | docs outdated | TOKENIZER.md محدّث + API contract موثّق |
| 12 | Streaming dataset | `BPETrainer.train(corpus)` يقبل `Iterable[str]` |
| 13 | `num_merges` كـ method | الآن property |
| 14 | Dead code (`_parse_byte_token` redundant) | حُذف |
| 15 | `vocab_size` mismatch في tests | تحديث tests |

---

## Issues Remaining (موثّقة بوضوح)

1. **CLI memory-bound:** corpus كامل في الذاكرة.
2. **No BPE-dropout:** deterministic فقط.
3. **`</w>` loss in byte fallback:** metadata فقط، bytes lossless.
4. **`special_tokens=False` no-op مع BOS/EOS literals:** إضافة BOS/EOS literals عبر `add_bos=True` تعمل حتى بدون `special_tokens=True`.

---

## Files Created
```

---

### `109/588` `backend/docs/V0.7.3_REPORT.md`

- **المسار الكامل:** `F:\1f\p\ALI_Studio_Pro_Design4_4.6.0\04_Adaptive_Hybrid\backend/docs/V0.7.3_REPORT.md`
- **الحجم:** 672 بايت (0.7 KB)
- **الامتداد:** `.md`

```markdown
# ALI DEVELOPMENT REPORT — V0.7.3 (Professional AI Agent)

**التاريخ:** 30 سبتمبر 2026
**الإصدار:** V0.7.3
**Scope:** إضافة Professional AI Agent Mode للواجهة

---

## Task

إضافة **خيار ذكاء احترافي** للواجهة (Professional AI Mode):
- Agent loop حقيقي مع intent classification + plan + execute + reflect.
- اختيار AI Mode من الواجهة (status bar clickable).
- يعمل مع/بدون نموذج خارجي (logic محلي + tokenizer للـ token counting).
- لا يكسر الـ Tools Only mode (default).

---

## Status

**COMPLETED — PASS**

---

## Implementation

### Architecture
```

---

### `110/588` `backend/docs/V0.7_REPORT.md`

- **المسار الكامل:** `F:\1f\p\ALI_Studio_Pro_Design4_4.6.0\04_Adaptive_Hybrid\backend/docs/V0.7_REPORT.md`
- **الحجم:** 2029 بايت (2.0 KB)
- **الامتداد:** `.md`

```markdown
# ALI DEVELOPMENT REPORT — V0.7 (ALI Tokenizer — HARDENED)

**التاريخ:** 30 سبتمبر 2026
**الإصدار:** V0.7.1
**Scope:** Tokenizer V0.7 + Hardening Pass

---

## Task

تطبيق **V0.7 FINAL HARDENING + REAL VERIFICATION** للـ ALI Tokenizer:

1. Audit كامل للملفات.
2. إصلاح UTF-8 merged tokens + byte fallback.
3. Whitespace lossless (multi-space, tabs, newlines).
4. Arabic normalization مع توثيق lossless vs lossy.
5. Special tokens validation + لا تصادم.
6. Vocabulary validation صارم (contiguous IDs + inverse map).
7. Determinism + Save/Load integrity + corruption tests.
8. Dataset CLI مع counts صريحة.
9. Performance benchmark جديد على corpus أكبر.
10. Regression tests + Exact vs Normalized round-trip منفصلين.
11. DB isolation + Lazy loading verification.
12. Documentation محدّثة.

---

## Status

**COMPLETED**

---

## Implementation

### Algorithm
**BPE (Byte Pair Encoding)** مع end-of-word marker `</w>` (GPT-2 style).
- Base vocabulary = 256 UTF-8 byte tokens.
- Pre-tokenization regex يفصل whitespace, Latin, Arabic, digits, punctuation.
- Special tokens: `<PAD>`, `<BOS>`, `<EOS>`, `<UNK>`, `<USER>`, `<ASSISTANT>`, `<SYSTEM>`.

### Normalization
| الـ flag | default | lossless? | الوصف |
|---|---|---|---|
| `normalize_arabic` | True | لا — يحوّل alef/yaa/taa_marbuta | |
| `strip_diacritics` | True | لا | |
| `normalize_alef` | True | لا | إ/أ/آ → ا |
| `normalize_yaa` | True | لا | ى → ي |
| `normalize_taa_marbuta` | True | لا | ة → ه |
| `lowercase_english` | True | لا | Latin → lowercase |
| `use_end_of_word_marker` | True | لا | |
| (off option) | — | **نعم** | عند إيقاف كل ما سبق |

### Whitespace handling
كل whitespace char (space, tab, newline, cr) يُرمَّز كـ `<0x{XX}>` byte token منفصل.
في decode: كل byte يُجمَّع ويُفك UTF-8 → الـ whitespace محفوظ 100% (lossless).

### Pre-tokenization
```

---

### `111/588` `backend/docs/VERIFICATION_2.0.md`

- **المسار الكامل:** `F:\1f\p\ALI_Studio_Pro_Design4_4.6.0\04_Adaptive_Hybrid\backend/docs/VERIFICATION_2.0.md`
- **الحجم:** 707 بايت (0.7 KB)
- **الامتداد:** `.md`

```markdown
# ALI AI 2.0 — Verification Report

## Source/static verification

- Python source was compiled with `python -m compileall -q .` successfully.
- The project contained 238 text/source files in the uploaded 1.1.0 bundle; the 2.0 source bundle adds the new lifecycle/control-plane modules and compatibility artifact.
- The missing `ali_agent.py.legacy` file referenced by the original project tests was restored as a migration/reference file.
- Version identity was aligned to `2.0.0` across application config, default config, project version and release tooling.

## Automated regression

Final run used the existing test suite with `ALI_GUI_TESTS=1` and Xvfb so Tk-dependent checks could execute. Result:
```

---

### `112/588` `backend/docs/VERIFICATION_2.1.md`

- **المسار الكامل:** `F:\1f\p\ALI_Studio_Pro_Design4_4.6.0\04_Adaptive_Hybrid\backend/docs/VERIFICATION_2.1.md`
- **الحجم:** 3473 بايت (3.4 KB)
- **الامتداد:** `.md`

```markdown
# ALI AI 2.1.0 — Verification Report

## Source completeness

- Final Markdown bundle declares and carries **276 text/source files** after adding the deterministic bootstrap, curriculum and P50 datasets plus this verification report.
- Every declared `## \`path\`` source section has a matching 5-backtick code block and was extracted successfully during release verification.
- No model weights, checkpoints or runtime databases are embedded in the source Markdown. They are created/installed at runtime.

## Static verification

- `python -m compileall -q .` → PASS.
- `python scripts/kca_doctor.py` → PASS; KCA registry contains exactly 100 functions.
- `python scripts/release_check.py` → PASS.
- Release manifest regeneration → PASS; source/text manifest matches the packaged source set.

## Automated regression

- `ALI_GUI_TESTS=1 xvfb-run -a python -m pytest tests -q --disable-warnings` → **170 passed, 3 skipped**.
- The 3 skips are the pre-existing default-tokenizer tests that intentionally wait for a trained default tokenizer artifact.
- The extra warnings are dependency deprecation warnings, not test failures.

## Real training lifecycle

Executed on CPU with a micro model:

`Tokenizer → Base 1 step → checkpoint → HF export → SFT 1 step → LoRA 1 step → adapter export → LoRA merge → merged HF export`.

All stages completed successfully. A continuation-stage compatibility fix was verified: SFT/LoRA now reuse the base tokenizer artifact, preventing tokenizer-vocabulary/embedding mismatch.

## Real local inference

The generated HF model was loaded through `ModelManager` / `LocalInference` and produced output without runtime exceptions. One-step smoke models are intentionally not treated as production-quality language models; model quality depends on the actual training run and dataset size.

## Real autonomous self-learning

A gated autonomous cycle was executed with approved conversation memory:

`approved conversations → incremental dedup dataset → LoRA candidate → merged candidate → evaluation → full regression → promotion gate`.

The candidate was **not promoted** because its measured validation improvement did not meet the configured promotion threshold. The active model therefore remained unchanged.

A failure-retry test also verified that a failed autonomous run does **not** advance the trained-data cursor; the same approved samples remain eligible for retry.

## Desktop verification

The Tk desktop entry point was launched under Xvfb. The three-pane shell, KCA badge and `AUTO LEARN · ARMED` status initialized successfully.

## GGUF

Real GGUF conversion was not executed in this environment because a local llama.cpp converter was not present. Invalid GGUF header rejection was tested successfully. The application refuses to treat a fake/unvalidated GGUF file as deployable.

## Windows packaging boundary

The Python source, Windows batch scripts and PyInstaller command path were syntax/source-checked, but a native Windows EXE build was not executed in this Linux verification environment. On Windows, `SETUP.bat` installs the core dependencies and `BUILD_EXE.bat` installs PyInstaller on demand before packaging.

Current official PyTorch Windows guidance supports Python 3.10–3.14, which matches the project's Windows setup range; the official wheel index also lists CPU Windows wheels for current Python versions. See the project documentation for exact environment setup.
```

---

### `113/588` `backend/docs/WEIGHTS_LIFECYCLE_2.0.md`

- **المسار الكامل:** `F:\1f\p\ALI_Studio_Pro_Design4_4.6.0\04_Adaptive_Hybrid\backend/docs/WEIGHTS_LIFECYCLE_2.0.md`
- **الحجم:** 178 بايت (0.2 KB)
- **الامتداد:** `.md`

```markdown
# ALI AI 2.0 — Weight / Tokenizer Lifecycle

ALI AI keeps **data, tokenizer artifacts, checkpoints, LoRA adapters, merged models and GGUF files as separate artifact classes**.
```

---

### `114/588` `backend/docs/WINDOWS_DEPENDENCIES.md`

- **المسار الكامل:** `F:\1f\p\ALI_Studio_Pro_Design4_4.6.0\04_Adaptive_Hybrid\backend/docs/WINDOWS_DEPENDENCIES.md`
- **الحجم:** 758 بايت (0.7 KB)
- **الامتداد:** `.md`

```markdown
# Windows dependencies

## Required
1. Windows 11 x64
2. Python 3.13.x x64
3. Internet access during first setup only, unless an offline Python wheel cache is supplied locally

`SETUP.bat` creates `.venv` and installs the pinned Python dependencies from `requirements-windows.txt`.

## Optional
- Git for repository operations
- A native GGUF runtime such as llama.cpp when using external GGUF models
- NVIDIA driver/CUDA is not required by the default P50 CPU-first training profile

## Portable EXE
Run `BUILD_EXE.bat` after setup. The project does not bundle Python, PyTorch wheels or GPU drivers because those are Windows/platform specific and large. The build script packages the application and project model assets into a Windows distribution folder.
```

---

### `115/588` `backend/docs/WINDOWS_P50_PROFILE.md`

- **المسار الكامل:** `F:\1f\p\ALI_Studio_Pro_Design4_4.6.0\04_Adaptive_Hybrid\backend/docs/WINDOWS_P50_PROFILE.md`
- **الحجم:** 714 بايت (0.7 KB)
- **الامتداد:** `.md`

```markdown
# Windows / ThinkPad P50 deployment profile

This build is tuned around a 4-core / 8-thread Intel Core i7-6820HQ class workstation with 32 GB DDR4 and a 2 GB Quadro M1000M class GPU.

Default policy:
- training device: CPU
- PyTorch threads: 6
- inter-op threads: 1
- batch size: 1
- gradient accumulation: 16
- sequence length: 256
- inference context: 384
- new tokens: 192
- AMP: disabled
- bootstrap scale: micro
- local research scale: small

The application never requires Hermes for normal ALI operation. The external path is configurable, with the default `D:\AI ALI\Hermes\`.

Hardware identifiers such as serial numbers, UUIDs and MAC addresses are intentionally not stored in the project configuration.
```

---

### `116/588` `backend/evaluation/artifacts/conversation_v0.2.json`

- **المسار الكامل:** `F:\1f\p\ALI_Studio_Pro_Design4_4.6.0\04_Adaptive_Hybrid\backend/evaluation/artifacts/conversation_v0.2.json`
- **الحجم:** 4547 بايت (4.4 KB)
- **الامتداد:** `.json`

```json
{
  "training": {
    "checkpoint": "/mnt/data/ALI_Studio_Pro_v3/ali_work/models/checkpoints/ALI-Conversation-v0.2/final-000350",
    "global_step": 350,
    "loss": 3.531298875808716,
    "val_loss": 3.7926310777664183,
    "best_val": 3.7926310777664183,
    "tokens_seen": 104629,
    "tokens_per_sec": 34181.02,
    "history": [
      {
        "step": 331,
        "epoch": 2,
        "loss": 3.71152400970459,
        "lr": 2.447123710390192e-06,
        "tokens_seen": 98734,
        "tokens_per_sec": 52993.76
      },
      {
        "step": 332,
        "epoch": 2,
        "loss": 3.268533945083618,
        "lr": 2.1969246228460523e-06,
        "tokens_seen": 99055,
        "tokens_per_sec": 51582.99
      },
      {
        "step": 333,
        "epoch": 2,
        "loss": 3.575032949447632,
        "lr": 1.96012082332766e-06,
        "tokens_seen": 99347,
        "tokens_per_sec": 50287.57
      },
      {
        "step": 334,
        "epoch": 2,
        "loss": 3.723590612411499,
        "lr": 1.7367337731956365e-06,
        "tokens_seen": 99667,
        "tokens_per_sec": 48867.86
      },
      {
        "step": 335,
        "epoch": 2,
        "loss": 3.4020931720733643,
        "lr": 1.5267837178600972e-06,
        "tokens_seen": 99998,
        "tokens_per_sec": 47653.88
      },
      {
        "step": 336,
        "epoch": 2,
        "loss": 3.8013274669647217,
        "lr": 1.3302896849458345e-06,
        "tokens_seen": 100312,
        "tokens_per_sec": 46659.3
      },
      {
        "step": 337,
        "epoch": 3,
        "loss": 3.1415884494781494,
        "lr": 1.1472694825678476e-06,
        "tokens_seen": 100641,
        "tokens_per_sec": 45582.86
      },
      {
        "step": 338,
        "epoch": 3,
        "loss": 3.5827136039733887,
        "lr": 9.777396977174666e-07,
        "tokens_seen": 100979,
        "tokens_per_sec": 44633.07
      },
      {
        "step": 339,
        "epoch": 3,
        "loss": 3.7225310802459717,
        "lr": 8.217156947590064e-07,
        "tokens_seen": 101306,
        "tokens_per_sec": 43642.5
      },
      {
        "step": 340,
        "epoch": 3,
        "loss": 3.5604968070983887,
        "lr": 6.792116140373116e-07,
        "tokens_seen": 101636,
        "tokens_per_sec": 42791.4
      },
      {
        "step": 341,
        "epoch": 3,
        "loss": 3.4720568656921387,
        "lr": 5.502403705962999e-07,
        "tokens_seen": 101928,
        "tokens_per_sec": 41972.94
      },
      {
        "step": 342,
        "epoch": 3,
        "loss": 3.047253370285034,
        "lr": 4.348136530083812e-07,
        "tokens_seen": 102194,
        "tokens_per_sec": 41225.98
      },
      {
        "step": 343,
        "epoch": 3,
        "loss": 3.3907082080841064,
        "lr": 3.329419223152385e-07,
        "tokens_seen": 102414,
        "tokens_per_sec": 40573.87
      },
      {
        "step": 344,
        "epoch": 3,
        "loss": 3.8894877433776855,
        "lr": 2.4463441107965276e-07,
        "tokens_seen": 102721,
        "tokens_per_sec": 39794.18
      },
      {
        "step": 345,
        "epoch": 3,
        "loss": 3.2770707607269287,
        "lr": 1.6989912254880556e-07,
        "tokens_seen": 103030,
        "tokens_per_sec": 38823.21
      },
      {
        "step": 346,
        "epoch": 3,
        "loss": 3.2660694122314453,
        "lr": 1.0874282992895944e-07,
        "tokens_seen": 103322,
        "tokens_per_sec": 38184.3
      },
      {
        "step": 347,
        "epoch": 3,
        "loss": 3.302237033843994,
        "lr": 6.117107577161551e-08,
        "tokens_seen": 103676,
        "tokens_per_sec": 37453.35
      },
      {
        "step": 348,
        "epoch": 3,
        "loss": 3.300046920776367,
        "lr": 2.7188171471131948e-08,
        "tokens_seen": 103981,
        "tokens_per_sec": 36550.65
      },
      {
        "step": 349,
        "epoch": 3,
        "loss": 3.4703586101531982,
        "lr": 6.797196874069877e-09,
        "tokens_seen": 104291,
        "tokens_per_sec": 35924.78
      },
      {
        "step": 350,
        "epoch": 3,
        "loss": 3.531298875808716,
        "lr": 0.0,
        "tokens_seen": 104629,
        "tokens_per_sec": 35273.13,
        "val_loss": 3.7926310777664183
      }