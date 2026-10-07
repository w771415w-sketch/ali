# ALI Studio Pro 4.5.8 — Full bundled trained release

تم إدراج الأوزان والتدريب الحقيقي داخل المشروع. `ALI-v1` هو النموذج المدرّب Active، و`ALI-Bootstrap-v2.5` احتياطي.

- Fixture: `backend/data/training/testdata/ALI_User_Understanding_Bundle_V4.md`
- SHA256: `371d2e0de7e109848ee8246801e4de80e1f339a9d3be9d0f5add36bc241087bb`
- Parsed sections: 216
- Unique Q/A after exact dedup: 215
- Pre-seeded training-QA chunks: 215
- Quiz: 216/216
- LoRA steps: 13
- Checkpoint, adapter, internal and merged HF weights: included
- Local knowledge DB: pre-seeded

## حدود البناء
GGUF وملفات Windows الأصلية (`Electron`, `.NET`, `node-pty/ConPTY`, Python embedded, CUDA) لم تُبنَ داخل بيئة Linux الحالية. سكربتات Windows موجودة داخل `scripts/`.
