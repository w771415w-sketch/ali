# Next Operation Queue — ALI Conversation Intelligence V6.1 + P50

## COMPLETED IN THIS OPERATION
- Added executable P50 hardware profile and runtime detection.
- Added CPU-first training policy for 4C/8T, 32 GB RAM, Quadro M1000M 2 GB.
- Added AC/battery/thermal/free-RAM admission gates.
- Added workspace containment, dangerous-command screening and permission hard ceiling.
- Added Agent state/checkpoints/postcondition verification.
- Added persistent one-heavy-job admission and audit redaction.
- Added executable conversation request framing and a conversation-to-runtime admission boundary.
- Added dataset governance primitives and P50 regression tests.
- Local regression: 7/7 passed.

## P0 — real training
- Materialize needed V6.1 shards on active training storage.
- Build SFT batches from train range only.
- Continue from the current verified checkpoint lineage.
- Evaluate on disjoint validation data and a held-out behavioral suite.
- Run Arabic, tool-use, project completion, uncertainty, safety and regression gates.
- Promote only after artifact and postcondition verification.
- Enforce P50 device admission before each heavy job.

## P1 — runtime integration
- Wire V6.1 framing into the primary chat request path.
- Persist the V6 state through the existing session/project stores.
- Surface intent, missing information, tool requirements, risk and completion state in the UI.
- Add human-reviewed preference pairs from real feedback.
- Expand evaluation reports by capability family.
- Connect the executable runtime policy to the existing desktop training controls.

## P1 — release verification
- Run native Windows Electron/.NET/node-pty/llama.cpp gates on the ThinkPad P50.
- Verify CPU/GPU runtime selection and GGUF loading.
- Verify checkpoint resume and real tool execution.
- Re-run full release audit and produce final release evidence.
- Verify source-export reassembly before treating the Git repository as binary-complete.

## P2 — Hermes
Hermes stays inactive. Do not enable its external connection until a separate integration-and-verification operation explicitly authorizes it.
