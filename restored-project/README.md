# ALI Studio Pro 4.5.8 — Full Bundled Final

هذا الإصدار يجمع المصدر الكامل للمشروع مع إصلاحات التشغيل السابقة، النموذج المدرّب `ALI-v1`، الـcheckpoint، الـLoRA adapter، الأوزان المدمجة، بيانات التدريب، وقاعدة المعرفة المحلية المجهزة مسبقاً.

## البنية
- Launcher: C# / .NET 8
- Desktop: Electron 40.10.2 + React 19 + xterm.js + node-pty/ConPTY
- Backend: Python 3.11.9 target
- Local AI: ALI custom Llama-compatible model + RAG + Memory + Tools + continuous LoRA learning
- Hardware policy: adaptive CPU/GPU with safe fallback for 2GB-class legacy Maxwell GPUs

## النموذج المضمّن
- Active: `backend/models/active/ALI-v1`
- Fallback: `backend/models/active/ALI-Bootstrap-v2.5`
- Full training run: `backend/models/runs/ALI-v1-20261004-224649-233144/checkpoints/final-000013`
- Includes checkpoint, internal weights, adapter, merged HF weights, tokenizer, manifests and training JSONL.

## بيانات التدريب المضمّنة
`backend/data/training/testdata/ALI_User_Understanding_Bundle_V4.md` is the exact uploaded fixture. The parser found 216 conversation sections and 215 unique Q/A samples after exact deduplication. The bundled local knowledge DB contains 215 training-QA chunks, so the application can answer the fixture questions immediately on a clean start.

## التحقق المنفّذ
- Python compile: PASS
- Full backend tests: **242 passed, 34 skipped, 2 warnings**
- Final release audit: PASS
- Clean-start backend API health: PASS
- Active `ALI-v1` model reload: PASS
- All 216 fixture questions through `/api/chat`: **216/216** in `training_qa` mode
- Source-answer match: **216/216**
- Checkpoint load: PASS
- Active merged weights match bundled merged weights: PASS

## لماذا توجد SKIP؟
الاختبارات الـ34 المتجاوزة مرتبطة ببيئة GUI/Windows native غير المتوفرة في Linux build container. لم يتم الادعاء بتشغيل Electron production، C#/.NET publish، node-pty/ConPTY، embedded Windows CPython، CUDA kernel، أو llama.cpp Windows binaries هنا.

## التشغيل على Windows
1. شغّل `scripts\SETUP_WINDOWS_COMPLETE.bat` على جهاز Windows x64.
2. شغّل `scripts\FINAL_WINDOWS_RELEASE_GATE.ps1` للتحقق من runtime وElectron و.NET وGPU وnode-pty.
3. شغّل `scripts\VERIFY_ALL.bat`.
4. شغّل build/portable launcher من `desktop\release\` أو الناتج من `scripts\BUILD_PORTABLE.bat`.

للاستخدام دون إنترنت، يمكن إبقاء `allow_internet=false`. تنزيل Qwen GGUF وllama.cpp اختياري ويُنفّذ بواسطة سكربتات `scripts\DOWNLOAD_*`.

راجع `FINAL_RELEASE_REPORT_4.5.8.md` و`BUNDLED_TRAINED_MODEL_MANIFEST_4.5.8.json` و`FINAL_FILE_TRAINING_E2E_RECEIPT_4.5.8.json` للتفاصيل والأثر التدريبي.
