# Next Operation Queue — ALI Conversation Intelligence V6.1

## P0 — real training
- Materialize the needed V6.1 shards on the active training storage.
- Build SFT batches from the train range only.
- Continue training from the current verified checkpoint lineage.
- Evaluate on disjoint validation data and a held-out behavioral suite.
- Run Arabic, tool-use, project completion, uncertainty, safety and regression gates.
- Promote only after artifact and postcondition verification.

## P1 — runtime integration
- Wire V6.1 request framing into the primary chat request path.
- Persist dialogue state with the existing session/project stores.
- Surface intent, missing information, tool requirements, risk and completion state in the UI.
- Add human-reviewed preference pairs from real feedback.
- Expand evaluation reports by capability family.

## P1 — release verification
- Run native Windows Electron/.NET/node-pty/llama.cpp gates.
- Re-run full release audit and produce final release evidence.
- Verify source-export reassembly before treating the Git repository as a binary-complete project.

## P2 — Hermes
Hermes stays inactive. Do not enable its external connection until a separate integration-and-verification operation explicitly authorizes it.
