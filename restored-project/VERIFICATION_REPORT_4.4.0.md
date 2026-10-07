# ALI Studio Pro 4.4.0 — Verification Report

## Automated tests
- Python test suite: **157 passed, 34 skipped, 2 warnings**
- Escaped/bold Markdown bundle import: **120/120 samples parsed and validated**
- Conversation session persistence: **PASS**
- Adaptive GPU policy unit tests: **PASS**
- Electron main syntax: **PASS**
- Electron preload syntax: **PASS**
- Desktop API module syntax: **PASS**

## Integration checks
- Backend health endpoint: **PASS**
- Conversation create/list/detail/rename path: **PASS**
- Training ingestion HTTP path: **PASS**
- Attached V2 behavior-training bundle: **validated / 120 samples / RAG=true**
- Real CPU continuous-learning smoke with 120-sample bundle: **completed v1 / 7 steps / ~10 sec in test environment**

## Important environment limits
- The current verification environment is Linux, not the target Windows workstation.
- Electron production build with Windows native `node-pty/ConPTY` and C#/.NET publishing was not executed here because the Windows SDK/native environment is not available.
- Actual CUDA execution on the user's Quadro M1000M cannot be certified from this environment. The release contains `RUN-GPU-DOCTOR.bat` and adaptive runtime checks for the Windows machine.
