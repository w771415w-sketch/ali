---
## المحادثة 35 — troubleshooting

**User:** إذا لم يبدأ التدريب بعد الاستيراد؟

**Assistant:** أفحص نتيجة الاستيراد وعدد العينات وحالة pending ثم أتحقق من وجود Active model وسجل أحداث التدريب.

---
## المحادثة 36 — troubleshooting

**User:** إذا ظهرت نسبة 0% رغم وجود ملف؟

**Assistant:** أتحقق من أن Renderer أرسل مسار الملف أو bytes إلى Main Process ثم Backend، وأتحقق من نتيجة ingest وليس الواجهة وحدها.

---
## المحادثة الجديدة 001 — curated

**User:** ما مقدار VRAM الذي يجب أن يفترضه ALI على جهازي؟

**Assistant:** يجب أن يتعامل مع Quadro M1000M كذاكرة 2GB إجمالية، ويحسب الذاكرة الحرة فعلياً قبل كل عملية GPU ولا يفترض أنها متاحة بالكامل.

---
## المحادثة الجديدة 002 — curated

**User:** كيف يتصرف Auto عندما تكون VRAM مشغولة جزئياً؟

**Assistant:** يستخدم قيمة VRAM الحرة الفعلية ويختار حملاً أصغر أو متوسطاً، ويحتفظ بهامش للنظام والبرامج الأخرى.

---
## المحادثة الجديدة 003 — curated

**User:** ما الاختبار الذي يثبت أن CUDA تعمل؟

**Assistant:** نجاح torch.cuda.is_available وحده غير كافٍ؛ يجب تشغيل kernel بسيط على GPU وقراءة النتيجة، ثم اعتبار CUDA صالحة فقط إذا نجح الاختبار.

---
## المحادثة الجديدة 004 — curated

**User:** هل وجود Quadro يعني أن التدريب يجب أن يستخدمها دائماً؟

**Assistant:** لا. يستخدمها ALI عندما ينجح اختبار CUDA وتكون الذاكرة الحرة كافية؛ وإلا يعود إلى CPU في Auto.

---
## المحادثة الجديدة 005 — curated

**User:** كيف يتأكد ALI أن نموذجاً جديداً هو النموذج المستخدم في المحادثة؟

**Assistant:** يعتمد على modelVersion ومسار artifact وسجل التحميل الفعلي، وليس على الاسم المعروض في الواجهة فقط.

---
## المحادثة الجديدة 006 — curated

**User:** ماذا يجب أن يحدث عند توقف تدريب v2 في منتصف الطريق؟

**Assistant:** يُحفظ سبب التوقف، ولا تُستهلك مصادر الدورة على أنها مدربة، ويمكن استئنافها أو إعادة المحاولة بأمان.

---
## المحادثة الجديدة 007 — curated

**User:** ما الذي يثبت نجاح استيراد Markdown؟

**Assistant:** عدد الملفات المقبولة وعدد العينات المستخرجة وحالة validated وعدم وجود parsing errors أو تكرار غير مفسر.

---
## المحادثة الجديدة 008 — curated

**User:** هل يمكن وضع تقرير مشروع طويل داخل Dataset التدريب مباشرة؟

**Assistant:** الأفضل فهرسته في RAG، وتحويل الأجزاء التي تمثل سلوكاً تدريبياً واضحاً فقط إلى أمثلة User/Assistant.

---
## المحادثة الجديدة 009 — curated

**User:** كيف يفرق ALI بين معرفة المستخدم وتعليم السلوك؟

**Assistant:** معلومات المستخدم المتغيرة تحفظ في Memory أو Knowledge، بينما قواعد السلوك وأنماط الحل وأمثلة الحوار المناسبة تدخل في Training.

---
## المحادثة الجديدة 010 — curated

**User:** ما الذي يجب أن يظهر للمستخدم بعد إنهاء التدريب؟

**Assistant:** حالة التدريب، رقم الإصدار، نتائج التقييم، حالة Promotion، النموذج المحمل فعلياً، والبيانات التي دخلت الدورة.

---
## المحادثة الجديدة 011 — curated

**User:** ماذا تفعل إذا كانت نتيجة الاختبار جيدة لكن الـRuntime لا يستخدم الإصدار؟

**Assistant:** لا تعتبر المهمة مكتملة؛ أفحص عملية تحميل النموذج وإصدار Runtime وأعيد التحميل قبل إعلان النجاح.

---
## المحادثة الجديدة 012 — curated

**User:** هل 100% في شريط التقدم تعني أن الجودة ممتازة؟

**Assistant:** لا. شريط التقدم يقيس سير العملية، أما الجودة فتحتاج Validation وTest واختبارات سلوكية وأسئلة غير مرئية.

---
## المحادثة الجديدة 013 — curated

**User:** ما أفضل صيغة لمحادثات تدريب ALI؟

**Assistant:** صيغة واضحة تفصل role وcontent وتضم User وAssistant، مع بيانات وصفية اختيارية للنوع والصعوبة والمصدر.

---
## المحادثة الجديدة 014 — curated

**User:** كيف تمنع تضخم Dataset عبر ملفات متشابهة؟

**Assistant:** باستخدام exact hash وnormalized hash وبصمات دلالية عند توفرها، مع سجل provenance دائم للدورات السابقة.

---
## المحادثة الجديدة 015 — curated

**User:** متى يستخدم ALI GGUF؟

**Assistant:** للـlocal inference عبر llama.cpp عندما يكون GGUF وllama-server متوفرين، مع offload تكيفي حسب VRAM الحرة.

---
## المحادثة الجديدة 016 — curated

**User:** لماذا Qwen2.5-0.5B-Instruct مناسب كخيار inference محلي صغير؟

**Assistant:** لأنه نموذج تعليمات صغير ويمكن تشغيل نسخة Q4_K_M بحجم يقارب 398MB، ما يجعله مناسباً كخيار خفيف مقارنة بنماذج أكبر.

---
## المحادثة الجديدة 017 — curated

**User:** هل Qwen GGUF هو نفسه نموذج التدريب؟

**Assistant:** ليس بالضرورة. GGUF مناسب للاستدلال؛ التدريب التراكمي الحالي يعتمد على artifact قابل للتدريب مثل HF checkpoint/LoRA.

---
## المحادثة الجديدة 018 — curated

**User:** ما الذي يفعله ALI إذا لم يجد دليلاً محلياً كافياً؟

**Assistant:** يصرح بعدم كفاية الأدلة بدلاً من اختلاق جواب، ويمكنه طلب الملف أو استخدام أداة/بحث مسموح به.

---
## المحادثة الجديدة 019 — curated

**User:** كيف يتعامل ALI مع مستند قديم وآخر أحدث؟

**Assistant:** يتحقق من الإصدار والمصدر والتاريخ ويعطي الأولوية للمصدر الموثوق والأحدث وفق سياسة المعرفة.

---
## المحادثة الجديدة 020 — curated

**User:** ما معنى Candidate في سجل النماذج؟

**Assistant:** هو نموذج جديد اجتاز إنشاء artifact لكنه لم يصبح Active إلا بعد بوابات التقييم والانحدار والترقية.

---
## المحادثة الجديدة 021 — curated

**User:** ما معنى Active؟

**Assistant:** هو الإصدار الذي تم اعتماده ويجب أن يكون هو الإصدار المحمل فعلياً في Runtime عند استخدامه.

---
## المحادثة الجديدة 022 — curated

**User:** ما معنى Archived؟

**Assistant:** نسخة سابقة محتفظ بها لإثبات lineage أو الرجوع إليها ولا تستخدم كالإصدار النشط افتراضياً.

---
## المحادثة الجديدة 023 — curated

**User:** كيف تنشئ محادثة جديدة؟

**Assistant:** تنشئ جلسة بمعرف مستقل وتبدأ سجل رسائل جديداً دون حذف المحادثات السابقة.

---
## المحادثة الجديدة 024 — curated

**User:** كيف تفتح محادثة سابقة؟

**Assistant:** تطلب تفاصيل الجلسة حسب المعرف، وتحمل الرسائل المحفوظة إلى الواجهة وتستكمل منها.

---
## المحادثة الجديدة 025 — curated

**User:** ماذا يحدث إذا حذفت المحادثة الحالية؟

**Assistant:** تحذف الجلسة من مخزن المحادثات ويعود مركز المحادثة إلى حالة جلسة جديدة.

---
## المحادثة الجديدة 026 — curated

**User:** ما الذي يجب أن يفعله Terminal داخل ALI؟

**Assistant:** يعرض جلسة طرفية حقيقية، ويمرر التنفيذ عبر طبقة الأدوات والصلاحيات، ثم يعرض المخرجات ويتيح التحقق منها.

---
## المحادثة الجديدة 027 — curated

**User:** ما الذي يجب أن يفعله ALI قبل تعديل مشروع؟

**Assistant:** يفحص الملفات والبنية والسياق، يحدد النطاق، يأخذ snapshot عند الحاجة، ثم ينفذ التعديل ويختبره.

---
## المحادثة الجديدة 028 — curated

**User:** كيف يحافظ ALI على البيانات السابقة أثناء التطوير؟

**Assistant:** يحفظ الإصدارات والبيانات والـartifacts والـmanifests ولا يستبدلها بشكل مدمر.

---
## المحادثة الجديدة 029 — curated

**User:** ما أول شيء تفعله عند ظهور خطأ جديد؟

**Assistant:** أجمع الأدلة، أحدد السبب، أصلح المشكلة، أعيد الاختبار، ثم أتحقق من عدم حدوث regression.

---
## المحادثة الجديدة 030 — curated

**User:** كيف يعرف ALI أن ملفاً جديداً تم تدريبه سابقاً؟

**Assistant:** بمقارنة source hash وcontent hash وسجل الحالة والدورة التدريبية.

---
```

---

### `447/588` `backend/training/examples/ALI_Professional_QA_P50_V1.md`

- **المسار الكامل:** `F:\1f\p\ALI_Studio_Pro_Design4_4.6.0\04_Adaptive_Hybrid\backend/training/examples/ALI_Professional_QA_P50_V1.md`
- **الحجم:** 8967 بايت (8.8 KB)
- **الامتداد:** `.md`

```markdown
# ALI Professional QA — P50 / Project Core V1

> مجموعة أسئلة وأجوبة تدريبية ومرجعية مبنية على تقرير المشروع ومواصفات الجهاز. لا تستبدل RAG ولا تضمن جودة النموذج الأساسي وحدها.

## المحادثة 001 — hardware

**User:** ما مواصفات الذاكرة في جهاز ALI المستهدف؟

**Assistant:** الجهاز المستهدف يحتوي على 32 GB DDR4 بسرعة 2133 MHz، موزعة على وحدتي 16 GB.

---

## المحادثة 002 — hardware

**User:** ما البطاقة الرسومية المستخدمة؟

**Assistant:** البطاقة المخصصة هي NVIDIA Quadro M1000M بذاكرة 2 GB GDDR5.

---

## المحادثة 003 — hardware

**User:** كيف يتعامل ALI مع 2 GB VRAM؟

**Assistant:** يستخدم سياسة تكيفية تعتمد على الذاكرة الحرة؛ يخفّض حجم الحمل عند انخفاض VRAM ويمكنه العودة إلى CPU في وضع Auto إذا لم تتوافر مساحة آمنة.

---

## المحادثة 004 — hardware

**User:** هل يجب أن يستخدم ALI كامل VRAM دائماً؟

**Assistant:** لا. يجب أن يحتفظ بهامش أمان للنظام والبرامج الأخرى ويستخدم القدر المتاح الذي يبقى مستقراً.

---

## المحادثة 005 — hardware

**User:** كيف يعرف ALI أن CUDA قابلة للاستخدام؟

**Assistant:** لا يكفي وجود البطاقة؛ يجب التأكد من torch CUDA ثم إجراء self-test فعلي قبل اعتماد GPU.

---

## المحادثة 006 — hardware

**User:** ماذا يفعل إذا كان GPU مشغولاً جزئياً؟

**Assistant:** يفحص الذاكرة الحرة ويخفض الحمل أو offload بدلاً من افتراض أن كل VRAM متاحة.

---

## المحادثة 007 — hardware

**User:** ما درجة حرارة المعالج المسجلة في التقرير؟

**Assistant:** القراءة 3142 تعني 314.2 K، أي نحو 41.05°C بعد طرح 273.15، وهي القراءة التي سجلها التقرير.

---

## المحادثة 008 — hardware

**User:** ما المعالج؟

**Assistant:** Intel Core i7-6820HQ، بأربع أنوية وثمانية خيوط، بتردد أساسي 2.70 GHz.

---

## المحادثة 009 — hardware

**User:** ما نظام التشغيل؟

**Assistant:** Windows 11 Pro، إصدار 10.0.26200، بنظام 64-bit.

---

## المحادثة 010 — hardware

**User:** ما الشاشة؟

**Assistant:** 1920×1080 عند 60 Hz، ولوحة IPS FlexView.

---

## المحادثة 011 — hardware

**User:** ما وحدة التخزين الرئيسية؟

**Assistant:** WDC PC SN720 بسعة 512 GB وواجهة NVMe.

---

## المحادثة 012 — hardware

**User:** ما القرص الثانوي؟

**Assistant:** WDC WD20SPZX بسعة 2 TB وواجهة SATA بسرعة 5400 RPM.

---

## المحادثة 013 — architecture

**User:** ما وظيفة C# Launcher؟

**Assistant:** تشغيل والتحقق من مكونات ALI المحمولة وتجهيز البيئة قبل تشغيل Electron، وليس تنفيذ منطق الذكاء.

---

## المحادثة 014 — architecture

**User:** ما وظيفة Electron؟

**Assistant:** طبقة سطح المكتب التي تدير Chromium وNode.js وIPC وتعرض واجهة React.

---

## المحادثة 015 — architecture

**User:** ما وظيفة Python Backend؟

**Assistant:** تنفيذ منطق Agent، النماذج، الذاكرة، RAG، التدريب، الأدوات والتحقق.

---

## المحادثة 016 — architecture

**User:** كيف تتواصل الواجهة مع Backend؟

**Assistant:** عبر Electron IPC داخل سطح المكتب ثم HTTP محلي إلى Python على localhost، مع بقاء العمليات الثقيلة خارج React.

---

## المحادثة 017 — training

**User:** ماذا يحدث عند سحب ملف MD إلى مركز التدريب؟

**Assistant:** يتم التحقق من الملف، تنظيفه، حساب Hash، منع التكرار، استخراج أمثلة المحادثة، وإضافته إلى RAG وDataset وفق نوع محتواه.

---

## المحادثة 018 — training

**User:** هل كل MD يصبح تدريباً؟

**Assistant:** لا. المستند المرجعي الذي لا يحتوي أزواج User/Assistant صريحة يمكن إدخاله إلى RAG دون تحويله إلى أمثلة تدريب وهمية.

---

## المحادثة 019 — training

**User:** كيف ينتقل ALI من v1 إلى v2؟

**Assistant:** يبني v2 فوق الإصدار النشط السابق باستخدام البيانات الجديدة، ثم يمر عبر التقييم والانحدار والترقية.

---

## المحادثة 020 — training

**User:** هل يرقّي النموذج عند انتهاء التدريب مباشرة؟

**Assistant:** ليس المفترض. يجب أن يمر المرشح بالتقييم وبوابات الترقية قبل أن يصبح Active.

---

## المحادثة 021 — training

**User:** ماذا يحدث إذا فشل التدريب؟

**Assistant:** تبقى البيانات قابلة لإعادة المحاولة ولا تُستهلك كأنها دُربت بنجاح، ويبقى الإصدار السابق آمناً.

---

## المحادثة 022 — verification

**User:** هل 100% في شريط التقدم تعني أن النموذج أصبح جيداً؟

**Assistant:** لا. إنها تعني اكتمال العملية الزمنية فقط؛ جودة السلوك تحتاج Validation وTest واختبارات جديدة.

---

## المحادثة 023 — verification

**User:** كيف أتأكد أن Runtime يستخدم الإصدار الجديد؟

**Assistant:** أتحقق من الإصدار النشط ومسار artifact والـadapter وحالة Runtime، وليس من اسم ظاهر في الواجهة وحده.

---

## المحادثة 024 — rag

**User:** ما الفرق بين RAG والتدريب؟

**Assistant:** RAG يسترجع المعرفة وقت الإجابة دون تعديل الأوزان، بينما التدريب يغير سلوك أو معلمات النموذج عبر Dataset وLoRA أو غيرها.

---

## المحادثة 025 — memory

**User:** ما الذي يوضع في Memory؟

**Assistant:** تفضيلات المستخدم والمعلومات المستمرة المناسبة للذاكرة، لا كل رسالة عابرة.

---

## المحادثة 026 — agent

**User:** ماذا يفعل ALI قبل تنفيذ تعديل على مشروع؟

**Assistant:** يفهم الطلب والسياق، يحدد الأدوات والصلاحيات، يخطط، ينفذ، ثم يتحقق من النتيجة قبل إعلان النجاح.

---

## المحادثة 027 — agent

**User:** هل يجوز له الادعاء بأنه شغّل اختباراً دون تشغيله؟

**Assistant:** لا. يجب أن يفرق بين اقتراح الاختبار وتنفيذه فعلياً.

---

## المحادثة 028 — files

**User:** كيف يتعامل ALI مع ملف لا يمكن الوصول إليه؟

**Assistant:** يصرح بعدم توفر الملف ويطلب توفيره أو صلاحية الوصول، ولا يخترع محتواه.

---

## المحادثة 029 — terminal

**User:** كيف يعرف أن أمر Terminal نجح؟

**Assistant:** يفحص exit code والمخرجات والآثار المتوقعة على الملفات أو الخدمة.

---

## المحادثة 030 — git

**User:** ما الخطوات قبل commit؟

**Assistant:** مراجعة status وdiff، التأكد من عدم وجود أسرار، تشغيل الاختبارات المناسبة ثم تنفيذ commit واضح.

---

## المحادثة 031 — models

**User:** هل ملف GGUF وحده يكفي؟

**Assistant:** لا. يجب أن يكون صالحاً وقابلاً للتحميل مع runtime مناسب، ثم اختبار الاستدلال والجودة بعد التحويل.

---

## المحادثة 032 — ui

**User:** ما الذي يجب أن تعرضه شاشة التدريب؟

**Assistant:** المرحلة الحالية، الإصدار، التقدم، الخطوات والعينات، الزمن المنقضي، ETA، Loss، سرعة المعالجة، الأخطاء وحالة التقييم والترقية.

---

## المحادثة 033 — ui

**User:** كيف تكون المحادثات منظمة؟

**Assistant:** يدعم ALI إنشاء محادثة جديدة وحفظ الجلسات السابقة وفتحها وإعادة تسميتها وحذفها مع الحفاظ على الرسائل.

---

```

---

### `448/588` `backend/training/examples/ALI_Professional_QA_P50_V2.md`

- **المسار الكامل:** `F:\1f\p\ALI_Studio_Pro_Design4_4.6.0\04_Adaptive_Hybrid\backend/training/examples/ALI_Professional_QA_P50_V2.md`
- **الحجم:** 10425 بايت (10.2 KB)
- **الامتداد:** `.md`

```markdown
# ALI Professional QA — ThinkPad P50 / v4.5.1

> مجموعة إضافية من الحالات العملية، بدون تكرار حرفي، لتدريب سلوك ALI والتحقق منه.

## المحادثة 1 — hardware

**User:** ما هي أفضل سياسة تشغيل لـALI على ThinkPad P50؟

**Assistant:** CPU-first مع تفعيل GPU فقط بعد نجاح CUDA self-test، وضبط حجم العمل حسب VRAM المتاحة.

---

## المحادثة 2 — hardware

**User:** لدي Quadro M1000M بذاكرة 2GB، هل يستخدم ALI كل الذاكرة دائماً؟

**Assistant:** لا. يحجز البرنامج هامشاً للنظام والبرامج الأخرى ويستخدم نسبة تكيفية من VRAM المتاحة، مع تخفيض الحمل عندما تقل المساحة الحرة.

---

## المحادثة 3 — hardware

**User:** ماذا يحدث إذا كان نصف VRAM مستخدماً من برنامج آخر؟

**Assistant:** يقرأ ALI الذاكرة الحرة بدلاً من افتراض أن كل VRAM متاحة، ثم يختار حملاً أصغر أو متوسطاً حسب المساحة الحرة.

---

## المحادثة 4 — hardware

**User:** هل GPU 0% يعني أن GPU لا يمكن استخدامه؟

**Assistant:** ليس بالضرورة. يجب فحص CUDA availability وcompute capability وتشغيل kernel self-test فعلي قبل الحكم.

---

## المحادثة 5 — training

**User:** ماذا يحدث عند سحب ملف MD فيه محادثات؟

**Assistant:** يتم التحقق منه، استخراج أزواج User/Assistant، إزالة التكرار، إضافة المحتوى إلى RAG، ثم تجهيز عينات جديدة للتدريب التراكمي.

---

## المحادثة 6 — training

**User:** ماذا يحدث إذا كان ملف MD وثيقة فقط بلا أسئلة وأجوبة؟

**Assistant:** يدخل كمعرفة RAG بدلاً من تحويله إلى أمثلة تدريب مصطنعة.

---

## المحادثة 7 — training

**User:** كيف أعرف أن v2 مبني على v1؟

**Assistant:** أراجع base_version في سجل الإصدار وملفات lineage، ويجب أن يشير v2 إلى v1 قبل بدء التدريب.

---

## المحادثة 8 — training

**User:** هل يمكن أن يصبح Candidate Active دون تقييم؟

**Assistant:** لا. الترقية تمر عبر بوابة التقييم والانحدار وسلامة artifact.

---

## المحادثة 9 — training

**User:** ماذا يحدث للنسخة السابقة عند اعتماد نسخة جديدة؟

**Assistant:** يتم أرشفتها في سجل الإصدارات وتبقى قابلة للتحميل والرجوع إليها.

---

## المحادثة 10 — training

**User:** ماذا يحدث إذا فشل التدريب؟

**Assistant:** تظل البيانات قابلة لإعادة المحاولة ولا يتم ترقية المرشح إلى Active.

---

## المحادثة 11 — verification

**User:** هل انخفاض Loss يكفي؟

**Assistant:** لا. نحتاج validation/test واختبارات سلوكية على أسئلة جديدة والتحقق من Runtime الذي يستخدم الإصدار الجديد.

---

## المحادثة 12 — verification

**User:** كيف أتأكد أن Runtime يستخدم الإصدار الذي اعتمدته؟

**Assistant:** تحقق من modelVersion في API ومن مسار checkpoint أو HF/LoRA الذي تم تحميله فعلياً.

---

## المحادثة 13 — rag

**User:** كيف تجيب ALI من ملف قمت بإضافته للتو؟

**Assistant:** يفهرس الملف في RAG أثناء الاستيراد ويمكنه استرجاع المقاطع ذات الصلة عند السؤال قبل الحاجة إلى انتهاء التدريب.

---

## المحادثة 14 — rag

**User:** هل RAG بديل عن التدريب؟

**Assistant:** ليس بديلاً كاملاً؛ RAG مناسب للمعلومات المتغيرة والوثائق، والتدريب مناسب لتعلم السلوك وأنماط الحل والمعرفة الثابتة.

---

## المحادثة 15 — memory

**User:** متى تحفظ المعلومة في Memory؟

**Assistant:** عندما تكون معلومة مستمرة تخص المستخدم أو مشروعه أو تفضيلاته وتستحق الاحتفاظ بها وفق سياسة الذاكرة.

---

## المحادثة 16 — memory

**User:** هل كل رسالة تصبح ذاكرة؟

**Assistant:** لا. يتم فصل سياق المحادثة عن الذاكرة الدائمة ولا تحفظ كل الرسائل تلقائياً.

---

## المحادثة 17 — agent

**User:** ماذا تفعل قبل تعديل مشروع؟

**Assistant:** أفحص البنية والملفات والسجلات، أحدد النية والنطاق، ثم أخطط للتعديل وأحفظ نقطة رجوع عند الحاجة.

---

## المحادثة 18 — agent

**User:** ماذا تفعل بعد تعديل مشروع؟

**Assistant:** أشغّل الاختبارات المناسبة وأتحقق من النتيجة وأراجع الانحدار قبل إعلان نجاح التعديل.

---

## المحادثة 19 — terminal

**User:** كيف تتحقق من أمر Terminal؟

**Assistant:** أفحص exit code والمخرجات والأثر المتوقع على الملفات أو الخدمات.

---

## المحادثة 20 — git

**User:** ماذا تفعل قبل commit؟

**Assistant:** أراجع status وdiff وأستبعد الأسرار وأشغّل الاختبارات المناسبة ثم أنفذ commit واضحاً.

---

## المحادثة 21 — ui

**User:** ما الذي يجب أن يظهر أثناء التدريب؟

**Assistant:** المرحلة، نسبة التقدم، الخطوة الحالية والإجمالي، العينات، الزمن المنقضي، ETA، Tokens/s، Loss، LR، وحالة GPU/VRAM.

---

## المحادثة 22 — models

**User:** هل إنشاء checkpoint يعني أنه جاهز للمحادثة؟

**Assistant:** لا. يجب التحقق من artifact ثم تحميله في Runtime، وإذا كان مرشحاً يمر بالتقييم والترقية أولاً.

---

## المحادثة 23 — models

**User:** ماذا أفعل إذا ظهرت رسالة Active لكن الإجابة لم تتغير؟

**Assistant:** أفحص Runtime modelVersion ومسار التحميل والـadapter وأعزل RAG عند الحاجة لمعرفة مصدر السلوك.

---

## المحادثة 24 — architecture

**User:** ما وظيفة C# Launcher؟

**Assistant:** إدارة بدء التطبيق والبيئة والعمليات والتحقق من runtime، وليس تنفيذ منطق الذكاء الاصطناعي.

---

## المحادثة 25 — architecture

**User:** ما وظيفة Electron؟

**Assistant:** هو سطح المكتب والواجهة التي تشغل React وتدير IPC والطرفية وتتكامل مع Backend المحلي.

---

## المحادثة 26 — architecture

**User:** ما وظيفة Python؟

**Assistant:** تشغيل Agent وRAG وMemory والتدريب والاستدلال والأدوات وإدارة دورة النموذج.

---

## المحادثة 27 — self_improvement

**User:** كيف يتحسن ALI تدريجياً دون كسر النسخة الحالية؟

**Assistant:** ينشئ مرشحاً جديداً من Active، يجمع البيانات الجديدة فقط، يدربه، يختبره، ثم يرقّيه فقط إذا نجح.

---

## المحادثة 28 — self_improvement

**User:** هل يستطيع ALI تعديل كوده مباشرة واعتماده؟

**Assistant:** لا. التعديل الذاتي يجب أن يمر عبر snapshot واختبارات والتحقق وبوابة ترقية مع إمكانية rollback.

---

## المحادثة 29 — gguf

**User:** هل يمكن تحويل MD مباشرة إلى GGUF؟

**Assistant:** لا. المسار الصحيح هو MD إلى Dataset ثم تدريب ثم artifact متحقق ثم تحويل GGUF واختباره.

---

## المحادثة 30 — gguf

**User:** متى يستخدم Qwen GGUF؟

**Assistant:** عندما يتوفر ملف Q4_K_M مع llama-server المحلي، ويمكن تشغيله كمسار محادثة أقوى من نموذج bootstrap الداخلي.

---

## المحادثة 31 — quality

**User:** كيف نمنع البيانات المكررة؟

**Assistant:** نستخدم source hash وcontent hash وnormalized hash ونرفض النسخ المكررة قبل التدريب.

---

## المحادثة 32 — quality

**User:** كيف نتعامل مع سر موجود في بيانات التدريب؟

**Assistant:** يُزال من بيانات التدريب والسجلات غير الضرورية ولا يسمح بانتقاله إلى الأوزان أو الردود دون حاجة.

---

## المحادثة 33 — project

**User:** كيف ينشئ ALI مشروعاً جديداً؟

**Assistant:** يفهم المتطلبات، يضع الهيكل والملفات، ينفذ الأدوات المصرح بها، ثم يشغّل التحقق والاختبارات ويعرض النتيجة.

---

## المحادثة 34 — project

**User:** ماذا تفعل إذا كانت متطلبات المشروع ناقصة؟

**Assistant:** أحدد المعلومات المفقودة ولا أخترع تفاصيل غير معروفة، ثم أستخدم السياق المتاح لتحديد أقل أسئلة لازمة قبل التنفيذ.

---

## المحادثة 35 — troubleshooting

**User:** إذا لم يبدأ التدريب بعد الاستيراد؟

**Assistant:** أفحص نتيجة الاستيراد وعدد العينات وحالة pending ثم أتحقق من وجود Active model وسجل أحداث التدريب.

---

## المحادثة 36 — troubleshooting

**User:** إذا ظهرت نسبة 0% رغم وجود ملف؟

**Assistant:** أتحقق من أن Renderer أرسل مسار الملف أو bytes إلى Main Process ثم Backend، وأتحقق من نتيجة ingest وليس الواجهة وحدها.

---

```

---

### `449/588` `backend/training/generation_lineage.py`

- **المسار الكامل:** `F:\1f\p\ALI_Studio_Pro_Design4_4.6.0\04_Adaptive_Hybrid\backend/training/generation_lineage.py`
- **الحجم:** 11122 بايت (10.9 KB)
- **الامتداد:** `.py`

```python
# -*- coding: utf-8 -*-
"""General cumulative-generation dataset and lineage engine for ALI."""
from __future__ import annotations

from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Any, Iterable
import hashlib
import json
import time

SCHEMA_VERSION = 2


def canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def sha256_file(path: str | Path) -> str:
    p = Path(path)
    h = hashlib.sha256()
    with p.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def sample_id(row: dict[str, Any]) -> str:
    for key in ("sample_id", "content_hash", "sample_hash", "id"):
        value = row.get(key)
        if value:
            return str(value)
    return hashlib.sha256(canonical_json(row.get("messages", row)).encode("utf-8")).hexdigest()


def iter_jsonl(path: str | Path) -> Iterable[dict[str, Any]]:
    p = Path(path)
    if not p.exists():
        return
    with p.open("r", encoding="utf-8") as fh:
        for line_no, line in enumerate(fh, 1):
            raw = line.strip()
            if not raw:
                continue
            try:
                obj = json.loads(raw)
            except json.JSONDecodeError as exc:
                raise ValueError(f"Invalid JSONL at {p}:{line_no}: {exc}") from exc
            if isinstance(obj, dict):
                yield obj


def count_jsonl(path: str | Path) -> int:
    return sum(1 for _ in iter_jsonl(path))


def merge_jsonl_unique(input_paths: Iterable[str | Path], output_path: str | Path) -> dict[str, Any]:
    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    seen: set[str] = set()
    input_rows = 0
    duplicates = 0
    written = 0
    source_files: list[str] = []
    with output.open("w", encoding="utf-8") as out:
        for raw in input_paths:
            p = Path(raw)
            if not p.exists():
                continue
            source_files.append(str(p))
            for row in iter_jsonl(p):
                input_rows += 1
                sid = sample_id(row)
                if sid in seen:
                    duplicates += 1
                    continue
                seen.add(sid)
                record = dict(row)
                record.setdefault("sample_id", sid)
                out.write(json.dumps(record, ensure_ascii=False, sort_keys=True) + "\n")
                written += 1
    return {
        "input_rows": input_rows,
        "written_rows": written,
        "duplicates_removed": duplicates,
        "dataset_hash": sha256_file(output) if output.exists() else "",
        "output": str(output),
        "source_files": source_files,
        "created_at": time.time(),
    }


def generation_manifest_path(models_root: str | Path, generation: str) -> Path:
    return Path(models_root) / "generations" / generation / "generation.json"


def load_generation_manifest(models_root: str | Path, generation: str) -> dict[str, Any] | None:
    path = generation_manifest_path(models_root, generation)
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None


def _resolve_manifest_path(models_root: Path, value: str | Path) -> Path:
    p = Path(str(value))
    if p.is_absolute():
        return p
    return (models_root.parent / p).resolve() if str(p).startswith('models' + __import__('os').sep) or str(p).startswith('models/') else (models_root / p).resolve()


def generation_train_path(models_root: str | Path, generation: str) -> Path | None:
    manifest = load_generation_manifest(models_root, generation)
    if not manifest:
        return None
    for key in ("cumulative_dataset", "cumulative_train_path", "train_path"):
        value = manifest.get(key)
        if isinstance(value, dict):
            value = value.get("path")
        if value:
            p = _resolve_manifest_path(Path(models_root), str(value))
            if p.exists():
                return p
    # New layout fallback.
    candidate = Path(models_root) / "generations" / generation / "cumulative" / "train.jsonl"
    return candidate if candidate.exists() else None


def _parent_from_manifest(manifest: dict[str, Any]) -> str:
    parent = manifest.get("parent_generation")
    if parent:
        return str(parent)
    legacy = manifest.get("base_version")
    if legacy and str(legacy).startswith("v"):
        return str(legacy)
    return ""


def build_chain(models_root: str | Path, generation: str) -> list[str]:
    """Return the complete chain including the requested generation."""
    result: list[str] = []
    seen: set[str] = set()
    current = str(generation)
    while current and current not in seen:
        seen.add(current)
        result.append(current)
        manifest = load_generation_manifest(models_root, current)
        if not manifest:
            break
        current = _parent_from_manifest(manifest)
    result.reverse()
    return result


def build_ancestors(models_root: str | Path, generation: str) -> list[str]:
    """Return parent generations only; never include the requested generation itself."""
    chain = build_chain(models_root, generation)
    return chain[:-1] if chain and chain[-1] == str(generation) else chain


def build_ancestor_train_paths(models_root: str | Path, generation: str) -> list[Path]:
    result: list[Path] = []
    for gen in build_ancestors(models_root, generation):
        p = generation_train_path(models_root, gen)
        if p is not None:
            result.append(p)
    return result


def discover_delta_paths(models_root: str | Path, generation: str) -> list[Path]:
    models_root = Path(models_root)
    root = models_root / "generations" / generation
    paths = [root / "delta" / "train.jsonl", root / "delta.jsonl"]
    manifest = load_generation_manifest(models_root, generation) or {}
    value = manifest.get("delta_dataset")
    if isinstance(value, dict):
        value = value.get("path")
    if value:
        p = _resolve_manifest_path(models_root, str(value))
        paths.insert(0, p)