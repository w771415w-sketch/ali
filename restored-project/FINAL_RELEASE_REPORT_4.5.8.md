# ALI Studio Pro 4.5.8 — Final Full Bundle Verification

## الحكم
تم تجميع إصدار كامل يضم المصدر + الإصلاحات + نموذج ALI-v1 المدرّب + الـcheckpoint + LoRA adapter + merged HF weights + بيانات التدريب + قاعدة المعرفة المحلية.

## نتائج التحقق
- Full backend suite: **242 passed, 34 skipped, 2 warnings**
- Release audit: **PASS**
- Clean-start server health: **PASS**
- Active model: **ALI-v1**, reload: **PASS**
- Fixture: 216 parsed conversation sections
- Unique Q/A samples: 215
- Pre-seeded training-QA chunks: 215
- Full fixture quiz via API: **216/216**
- Source-answer match: **216/216**
- Re-import protection remains covered by existing tests (`duplicate_source`)
- Checkpoint loads successfully and reports global step 13
- Active merged model weights equal bundled merged HF weights byte-for-byte (SHA256 identical)

## الأوزان
تم تضمين: `checkpoint.pt`, `internal_model.safetensors`, `adapter_model.safetensors`, `adapter/adapter_model.safetensors`, `adapter/adapter_config.json`, و`merged_hf/model.safetensors`، إضافة إلى tokenizer/config/manifests.

## الإصلاحات المضمّنة
1. إصلاح مسار الـbase checkpoint النسبي لمنع إعادة تدريب tokenizer وحدوث embedding index mismatch.
2. أولوية deterministic local QA على الذاكرة القديمة.
3. مسار training-QA deterministic من ملفات المحادثات.
4. إصلاح bridge الخاص بـllama-server و`-ngl` وstreaming.
5. منفذ llama-server ديناميكي عند تعارض المنفذ المفضل.
6. تماسك الإصدار 4.5.8.
7. نموذج مدرّب Active مع fallback إلى bootstrap.
8. قاعدة معرفة محلية مهيأة مسبقاً لتعمل النسخة النظيفة دون إعادة استيراد.
9. تنظيف قواعد بيانات المحادثات/الذاكرة القابلة للتغيير عند الشحن.

## حدود Windows
لم تُنفّذ بوابات Windows-native داخل Linux: Electron production، .NET publish، embedded CPython 3.11.9، node-pty/ConPTY، CUDA، llama.cpp Windows binaries، وGGUF inference. المشروع يحتوي على سكربتات التشغيل والتحقق اللازمة على Windows.
