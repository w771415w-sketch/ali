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
