# ALI 4.5.2 Knowledge & Training Index

## Authoritative local knowledge
1. `THINKPAD_P50_COMPLETE_USER_PROFILE.md` — user-provided hardware/system profile.
2. `ALI_V4_4_COMPLETE_REPORT.md` — prior project audit, implementation history, known defects and evidence.
3. `THINKPAD_P50_USER_PROFILE.md` — compact engineering profile.

## Curated behavior/training
1. `../training/examples/ALI_MASTER_TRAINING_4.5.2.md`
2. `../training/examples/ALI_Professional_QA_P50_V2.md`
3. root/import packs `ALI_Conversation_Training_Core_V2.md` and `ALI_Conversation_Training_V1.md`

## Routing rule
- Device/project facts and long documents -> RAG/Knowledge.
- Mutable user preferences -> Memory.
- General behavioral patterns, tool-use patterns, verification discipline and stable task procedures -> Training/LoRA.
- GGUF -> local inference artifact; it is never treated as a training source by itself.

## Truthfulness rule
The UI must distinguish imported, validated, trained, evaluated, promoted and runtime-loaded states. A progress bar or registry flag alone is not evidence of behavioral improvement.
