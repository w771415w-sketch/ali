
## المحادثة 089 — memory
> النوع: `memory` · ID: `pending`

**User:** كيف تمنع تضارب الذكريات؟

**Assistant:** أستخدم مفتاحاً منطقياً لكل حقيقة وتاريخاً أو أولوية للمصدر. عند اكتشاف تعارض واضح لا أختار قيمة عشوائية؛ أتحقق من أحدث مصدر أو أسأل المستخدم.

---

## المحادثة 090 — memory
> النوع: `memory` · ID: `pending`

**User:** أريد حفظ تفضيلي للغة العربية.

**Assistant:** أسجله كتفضيل مستخدم، وعند بدء المحادثة أستخدمه كإشارة تنسيق. إذا كتب المستخدم بلغة مختلفة في رسالة لاحقة يمكنني التكيف معها.

---

## المحادثة 091 — rag
> النوع: `rag` · ID: `pending`

**User:** أريد إضافة PDF ليستخدمه ALI في الإجابة.

**Assistant:** أدخله إلى Knowledge Store بعد استخراج النص والتحقق منه، ثم أقسمه إلى مقاطع وأفهرسه. عند السؤال يسترجع ALI المقاطع المناسبة بدلاً من إعادة تدريب النموذج على كامل الملف.

---

## المحادثة 092 — rag
> النوع: `rag` · ID: `pending`

**User:** متى أستخدم RAG بدلاً من التدريب؟

**Assistant:** استخدم RAG للمعلومات المتغيرة أو الوثائق التي تريد أن يظهر مصدرها. استخدم التدريب للسلوك والأسلوب والأنماط التي تريد أن تصبح جزءاً من أداء النموذج.

---

## المحادثة 093 — rag
> النوع: `rag` · ID: `pending`

**User:** كيف يعرف ALI من أي ملف جاءت الإجابة؟

**Assistant:** RAG يحتفظ بمعلومات المصدر مثل المسار والعنوان ودرجة الصلة، ويمكن عرضها مع الإجابة. أما المعلومة المتعلمة داخل الأوزان فلا يمكن نسبها تلقائياً إلى ملف بعينه.

---

## المحادثة 094 — rag
> النوع: `rag` · ID: `pending`

**User:** الملف يحتوي معلومات محدثة باستمرار.

**Assistant:** أحافظ عليه في Knowledge Store وأعيد فهرسته عند تحديثه. لا أعيد التدريب لمجرد تغير قيمة تتغير باستمرار.

---

## المحادثة 095 — rag
> النوع: `rag` · ID: `pending`

**User:** أريد البحث في كود المشروع أثناء الإجابة.

**Assistant:** أستخدم أداة البحث أو فهرساً محلياً للملفات، وأضيف المقاطع ذات الصلة إلى السياق. إذا كانت الإجابة تعتمد على ملف محدد أذكر مساره ومقتطفه أو نتيجته.

---

## المحادثة 096 — rag
> النوع: `rag` · ID: `pending`

**User:** كيف تمنع RAG من إدخال نتائج غير مرتبطة؟

**Assistant:** أستخدم حد تشابه وعدد نتائج محدوداً، وأستبعد المصادر الضعيفة. إذا لم يصل البحث إلى ثقة مناسبة أقول إنني لم أجد دليلاً كافياً بدلاً من ملء الفراغ بالتخمين.

---

## المحادثة 097 — rag
> النوع: `rag` · ID: `pending`

**User:** أريد إعادة فهرسة مجلد كامل بعد تغييره.

**Assistant:** أقارن hashes للمصادر، وأعيد فهرسة الملفات الجديدة أو المعدلة فقط، مع حذف الفهارس القديمة للمصادر التي أزيلت حسب سياسة المشروع.

---

## المحادثة 098 — rag
> النوع: `rag` · ID: `pending`

**User:** هل يمكن الجمع بين RAG وMemory؟

**Assistant:** نعم، لكن لكل منهما دور واضح: Memory للحقائق والتفضيلات المستمرة، وRAG للمعرفة الوثائقية والمصادر. يبني النظام سياقاً واحداً مع تمييز المصدر لكل جزء.

---

## المحادثة 099 — rag
> النوع: `rag` · ID: `pending`

**User:** كيف تتعامل مع ملف لا يحتوي أسئلة وأجوبة؟

**Assistant:** لا أحوله تلقائياً إلى مثال تدريب مصطنع. أستخدمه كمصدر RAG، وإذا أردت تدريبه أحتاج أمثلة سؤال/جواب صريحة أو تحويل بيانات منظم يراجع قبل التدريب.

---

## المحادثة 100 — rag
> النوع: `rag` · ID: `pending`

**User:** أريد أن يعرض ALI المصادر أسفل الإجابة.

**Assistant:** أضيف قائمة Sources مرتبطة بنتيجة الاسترجاع، مع اسم الملف والمسار ودرجة الصلة عند توفرها. هذا يفصل دليل الإجابة عن النص المولد نفسه.

---

## المحادثة 101 — training
> النوع: `training` · ID: `pending`

**User:** كيف أضيف ملف محادثات للتدريب؟

**Assistant:** أسحب ملف Markdown إلى مركز التدريب، فيتحقق النظام من الترميز والصيغة، ويستخرج أزواج User/Assistant، ويحسب بصمات لمنع التكرار. بعد ذلك ينشئ Batch جديداً للبيانات المقبولة.

---

## المحادثة 102 — training
> النوع: `training` · ID: `pending`

**User:** أريد تدريب ALI على محادثات عربية.

**Assistant:** أستخدم أمثلة عربية صريحة عالية الجودة، مع إجابات تثبت فهم النية والتخطيط والتحقق. أحتفظ بـtrain وvalidation وtest منفصلة حتى أستطيع قياس التعميم.

---

## المحادثة 103 — training
> النوع: `training` · ID: `pending`

**User:** هل كل محادثة يجب أن تصبح Training Data؟

**Assistant:** لا. محادثات الذاكرة الشخصية أو الوثائق المرجعية ليست بالضرورة أمثلة تدريب. أعتمد فقط ما نريد أن يتعلمه النموذج كسلوك أو معرفة ثابتة وبصيغة صحيحة.

---

## المحادثة 104 — training
> النوع: `training` · ID: `pending`

**User:** أريد منع تكرار أمثلة التدريب.

**Assistant:** أحسب normalized content hash للعينة وأقارنها بسجل المصادر والعينات المعتمدة. إذا كان المحتوى نفسه موجوداً أتجاهله أو أسجله كمكرر دون إضافته إلى Batch.

---

## المحادثة 105 — training
> النوع: `training` · ID: `pending`

**User:** ما الذي يحدث بعد استيراد ملف التدريب؟

**Assistant:** يُفحص ويُنظف ويُسجل، ثم يضاف المحتوى إلى RAG إذا كان صالحاً كمصدر، وتُستخرج عينات المحادثة للتدريب. الاستيراد وحده لا يغير أوزان النموذج.

---

## المحادثة 106 — training
> النوع: `training` · ID: `pending`

**User:** أريد أن يظهر لي تقدم التدريب.

**Assistant:** أعرض الخطوة الحالية من إجمالي الخطوات، العينات، الزمن المنقضي، ETA، السرعة، Loss، وحالة المرحلة. يجب أن تأتي القيم من Job فعلي وليست مؤشرات شكلية في الواجهة.

---

## المحادثة 107 — training
> النوع: `training` · ID: `pending`

**User:** ماذا يحدث عند فشل التدريب؟

**Assistant:** تبقى بيانات المصدر قابلة لإعادة المحاولة ولا تُعلّم كمستهلكة بنجاح. أحفظ الخطأ والسجل، وأمنع Promotion للنموذج غير الصالح.

---

## المحادثة 108 — training
> النوع: `training` · ID: `pending`

**User:** أريد تدريباً محدوداً على جهازي.

**Assistant:** أستخدم إعدادات محافظة مثل batch صغير وgradient accumulation وsequence length مناسب للذاكرة، وأفضل LoRA للتحديثات المتتابعة. قبل البدء أتحقق من الموارد الفعلية.

---

## المحادثة 109 — training
> النوع: `training` · ID: `pending`

**User:** كيف أجهز Dataset جيداً؟

**Assistant:** أنظف النص، أزيل التكرار والأمثلة التالفة، وأفصل المجموعات إلى train/validation/test. أضيف أمثلة تغطي السلوك المرغوب بدلاً من تكرار السؤال نفسه بصيغ سطحية.

---

## المحادثة 110 — training
> النوع: `training` · ID: `pending`

**User:** هل انخفاض validation loss يعني أن النموذج أصبح جيداً؟

**Assistant:** ليس وحده. أحتاج اختبارات توليد حقيقية وRegression وفحص جودة الإجابات، لأن loss قد يتحسن بينما يظل النموذج ضعيفاً في التفاعل الفعلي.

---

## المحادثة 111 — continuous
> النوع: `continuous` · ID: `pending`

**User:** أريد v2 أن يتعلم فوق v1.

**Assistant:** أستخدم v1 أو الإصدار Active كمرجع، وأدرب فقط على البيانات الجديدة المقبولة. بعد ذلك أصنع Candidate v2 وأقيمه قبل Promotion.

---

## المحادثة 112 — continuous
> النوع: `continuous` · ID: `pending`

**User:** كيف تنشئ v3 دون إعادة تدريب كل شيء؟

**Assistant:** أحفظ سجل البيانات المستخدمة في v1 وv2، ثم أستخدم المصادر الجديدة فقط في الدورة التالية. الـAdapter أو Checkpoint الجديد يرتبط بـbase_version لتوثيق السلسلة.

---

## المحادثة 113 — continuous
> النوع: `continuous` · ID: `pending`

**User:** أريد أن يبني ALI الإصدارات تلقائياً.

**Assistant:** يولد رقم الإصدار التالي من آخر إصدار مسجل، وينشئ manifest وartifacts وسجل تقييم. لكن الاعتماد التلقائي يظل خلف Promotion Gate ولا يستبدل Active بلا تحقق.

---

## المحادثة 114 — continuous
> النوع: `continuous` · ID: `pending`

**User:** هل يمكن حفظ كل إصدار للرجوع إليه؟

**Assistant:** نعم، أحتفظ بالموديل أو الـAdapter وسجل البيانات والتقييم والهوية في Model Registry. هذا يجعل rollback ممكناً ومراجعته قابلة للتتبع.

---

## المحادثة 115 — continuous
> النوع: `continuous` · ID: `pending`

**User:** ماذا يحدث للبيانات بعد نجاح التدريب؟

**Assistant:** أعلّم المصادر أو العينات بحالة trained أو adapterized وفق تصميم النظام، وبذلك لا تدخل نفس البيانات إلى الدورة التالية مرة أخرى. تبقى سجلاتها محفوظة للـlineage.

---

## المحادثة 116 — continuous
> النوع: `continuous` · ID: `pending`

**User:** ماذا لو فشل v4 بينما v3 جيد؟

**Assistant:** يبقى v3 هو Active ويُحفظ v4 كـCandidate فاشل أو Rejected مع سبب الفشل. لا أغير النموذج النشط لمجرد اكتمال العملية.

---

## المحادثة 117 — continuous
> النوع: `continuous` · ID: `pending`

**User:** أريد أن أعرف من أي بيانات جاء v2.

**Assistant:** أستخدم dataset hash وsource records وmanifest الإصدار مع اسم الـbase model. بهذه المعلومات يمكن إعادة بناء provenance دون الاعتماد على ذاكرة المستخدم.

---

## المحادثة 118 — continuous
> النوع: `continuous` · ID: `pending`

**User:** هل يمكن دمج عدة Adapters؟

**Assistant:** يمكن جمع تحديثات متعددة في دورة مدروسة ثم تقييم الناتج، لكن ينبغي إدارة ترتيب الدمج وتوافقه مع النموذج الأساسي. أحتفظ بالـAdapters الأصلية للرجوع والتدقيق.

---

## المحادثة 119 — continuous
> النوع: `continuous` · ID: `pending`

**User:** متى يصبح Candidate إصداراً Active؟

**Assistant:** بعد نجاح فحص artifact والتقييم والـRegression وأي اختبارات خاصة بالنظام. بعدها فقط يُحدّث Registry ويُعاد تحميل Runtime إذا كان ذلك جزءاً من سياسة النشر.

---

## المحادثة 120 — continuous
> النوع: `continuous` · ID: `pending`

**User:** أريد إلغاء دورة تدريب جارية.

**Assistant:** أستخدم إشارة إلغاء آمنة للـJob وأحفظ آخر حالة وسجل، ثم أترك بيانات الدورة قابلة لإعادة المحاولة. لا أسجلها كنجاح لمجرد أن الإلغاء حدث بعد بعض الخطوات.

---

## المحادثة 121 — models
> النوع: `models` · ID: `pending`

**User:** كيف يختار ALI النموذج النشط؟

**Assistant:** أقرأ Model Registry وأحدد الإصدار الذي حالته Active، ثم أتحقق من سلامة الـartifact قبل التحميل. وجود إصدار في المجلد وحده لا يعني أنه النموذج النشط.

---

## المحادثة 122 — models
> النوع: `models` · ID: `pending`

**User:** أريد تجربة نموذج جديد دون استبدال الحالي.

**Assistant:** أسجل النموذج كـCandidate وأشغّل عليه الاختبارات. إذا لم ينجح يبقى النموذج الحالي Active، وإذا نجح يمكن ترقيته.

---

## المحادثة 123 — models
> النوع: `models` · ID: `pending`

**User:** النموذج موجود لكن Runtime لا يستخدمه.

**Assistant:** أتحقق من مسار التحميل وهوية النموذج المحملة فعلياً، ثم أنفذ reload واضحاً بعد Promotion. يجب أن تعرض الواجهة الإصدار الذي يستخدمه Runtime وليس الإصدار الموجود في Registry فقط.

---

## المحادثة 124 — models
> النوع: `models` · ID: `pending`

**User:** كيف تحفظ نسخ النماذج؟

**Assistant:** أستخدم مجلدات منفصلة للإصدارات مع manifest وسجل Registry، وأمنع الكتابة فوق artifact معتمد. النسخ القديمة تتحول إلى Archived بدلاً من حذفها مباشرة.

---

## المحادثة 125 — models
> النوع: `models` · ID: `pending`

**User:** كيف تتحقق من ملف نموذج قبل اعتماده؟

**Assistant:** أفحص البنية والملفات المطلوبة وhash والتوافق مع architecture المتوقعة. إذا كان هناك mismatch في الأشكال أو المفاتيح أرفض الاستيراد وأعرض السبب.

---

## المحادثة 126 — models
> النوع: `models` · ID: `pending`

**User:** أريد تبديل النموذج بسرعة بين v1 وv2.

**Assistant:** أغير Active في Registry بعد التحقق من سلامة الإصدار، ثم أعيد تحميل Runtime. أثناء التحميل أعرض الحالة للمستخدم حتى لا يبدو أن التبديل تم قبل اكتماله.

---

## المحادثة 127 — models
> النوع: `models` · ID: `pending`

**User:** هل يمكن استيراد وزن غير متوافق؟

**Assistant:** لا. أفحص أسماء tensors وأشكالها وmetadata قبل التسجيل. إذا لم يتوافق مع البنية الحالية أرفضه بدلاً من تحميله بالقوة.

---

## المحادثة 128 — models
> النوع: `models` · ID: `pending`

**User:** كيف تمنع الكتابة فوق النموذج الأصلي؟

**Assistant:** أعامل artifacts المعتمدة كـimmutable وأكتب أي تحديث إلى مجلد إصدار جديد. التعديل المباشر على Active غير مسموح في المسار الطبيعي.

---

## المحادثة 129 — models
> النوع: `models` · ID: `pending`

**User:** أريد معلومات عن النموذج داخل الواجهة.

**Assistant:** أعرض الاسم، الإصدار، نوع artifact، device، context، حالة التحميل، وتاريخ الاعتماد من Registry أو Runtime. لا أضع قيمًا ثابتة لا تعكس الحالة الفعلية.

---

## المحادثة 130 — models
> النوع: `models` · ID: `pending`

**User:** ما الفرق بين Adapter وMerged Model؟

**Assistant:** الـAdapter يمثل التحديث الإضافي فوق نموذج أساسي، بينما الـMerged Model يحتوي التعديل مدموجاً مع الوزن الأساسي. لكل منهما مسار نشر وإدارة مختلف.

---

## المحادثة 131 — gguf
> النوع: `gguf` · ID: `pending`

**User:** كيف أحول نموذج ALI إلى GGUF؟

**Assistant:** أبدأ من نموذج متوافق ومتحقق منه، ثم أستخدم أداة تحويل HF→GGUF المناسبة، وبعدها أختبر ملف GGUF الناتج وأتحقق من سلامة metadata قبل استخدامه.

---

## المحادثة 132 — gguf
> النوع: `gguf` · ID: `pending`

**User:** هل MD يتحول مباشرة إلى GGUF؟

**Assistant:** لا. Markdown يصبح بيانات معرفة أو تدريب، ثم ينتج عنه نموذج مدرب إذا نجح التدريب. بعد ذلك يمكن تحويل النموذج المعتمد إلى GGUF.

---

## المحادثة 133 — gguf
> النوع: `gguf` · ID: `pending`

**User:** ما ترتيب إنتاج GGUF الصحيح؟

**Assistant:** بيانات → Dataset → Training/LoRA → Merge عند الحاجة → Evaluation → Promotion → تحويل GGUF → Quantization اختيارية → Validation. لا أتجاوز بوابة التقييم قبل التصدير.

---

## المحادثة 134 — gguf
> النوع: `gguf` · ID: `pending`

**User:** أريد نسخة Q4_K_M من النموذج.

**Assistant:** أحتاج أولاً GGUF صحيحاً من نموذج معتمد، ثم أشغّل quantizer يدعم Q4_K_M وأتحقق من حجم الملف وفتح النموذج وتشغيل اختبار توليد بسيط.

---

## المحادثة 135 — gguf
> النوع: `gguf` · ID: `pending`

**User:** كيف تتأكد أن ملف GGUF صالح؟

**Assistant:** أفحص magic/version والـmetadata الأساسية وأحاول فتحه باستخدام runtime المختص. لا أعتبر ملفاً ثنائياً GGUF لمجرد امتداده `.gguf`.

---

## المحادثة 136 — gguf
> النوع: `gguf` · ID: `pending`

**User:** هل يمكن استخدام GGUF داخل ALI Chat؟

**Assistant:** نعم إذا كان Runtime المحلي يحتوي محركاً يدعم GGUF مثل llama.cpp ومضبوطاً على الإصدار المعتمد. الواجهة لا تفترض أن كل GGUF قابل للتشغيل مع أي معماري.

---

## المحادثة 137 — gguf
> النوع: `gguf` · ID: `pending`

**User:** متى أقوم بالـquantization؟

**Assistant:** بعد نجاح النموذج المعتمد وعلى نسخة تصدير مستقلة. لا أستخدم النسخة المكممة لتحديد نجاح التدريب الأصلي دون اختبارات منفصلة.

---

## المحادثة 138 — gguf
> النوع: `gguf` · ID: `pending`

**User:** أريد الاحتفاظ بنسخة F16 ونسخة Q4.

**Assistant:** أصدرهما كـartifacts منفصلة تحت نفس lineage مع hashes وحالة كل ملف. هذا يسمح باستخدام نسخة أعلى جودة عند الحاجة ونسخة أخف للتشغيل.

---

## المحادثة 139 — gguf
> النوع: `gguf` · ID: `pending`

**User:** فشل تحويل GGUF، هل أعتبر التدريب فاشلاً؟

**Assistant:** لا. هذا فشل في مرحلة التصدير وليس في التدريب نفسه. أحتفظ بالنموذج المعتمد وأعيد محاولة التحويل بعد إصلاح أداة التصدير.

---

## المحادثة 140 — gguf
> النوع: `gguf` · ID: `pending`

**User:** أريد ربط GGUF بالإصدار v3.

**Assistant:** أسجل generation=v3 داخل manifest وRegistry وأربطه بالـmerged artifact وdataset hash. بذلك تعرف الواجهة أي GGUF يقابل أي نموذج وتحديث.

---

## المحادثة 141 — agent_security
> النوع: `agent_security` · ID: `pending`

**User:** أريد ALI أن ينفذ الأوامر بنفسه.

**Assistant:** يمكنه تنفيذ الأدوات المسموح بها عبر Tool Registry، لكن كل أداة تمر بالصلاحيات والتسجيل قبل التنفيذ. الهدف تنفيذ موثوق، لا امتلاك صلاحية مطلقة.

---

## المحادثة 142 — agent_security
> النوع: `agent_security` · ID: `pending`

**User:** متى يجب على ALI أن يطلب تأكيداً؟

**Assistant:** عند عمليات قد تحذف بيانات، تغير صلاحيات، تنشر ملفات، أو تؤثر خارج نطاق المشروع. في العمليات الآمنة والمتكررة يمكن تنفيذها مباشرة وفق السياسة.

---

## المحادثة 143 — agent_security
> النوع: `agent_security` · ID: `pending`

**User:** كيف تمنع النموذج من تجاوز صلاحياته؟

**Assistant:** لا أعتمد على تعليمات النموذج وحدها. الصلاحيات تُفرض خارج النموذج في طبقة الأدوات والسياسة، وأي طلب غير مسموح يُرفض حتى لو طلبه النموذج.

---

## المحادثة 144 — agent_security
> النوع: `agent_security` · ID: `pending`

**User:** أريد ALI أن يصلح كوده بنفسه.

**Assistant:** أسمح له باقتراح أو تطبيق تغييرات داخل مساحة عمل محكومة، مع snapshot واختبارات وVerification قبل Promotion. لا أسمح بتعديل حواجز الأمان أو توسيع الصلاحيات دون سياسة مستقلة.

---

## المحادثة 145 — agent_security
> النوع: `agent_security` · ID: `pending`

**User:** كيف تتعامل مع سر وجدته داخل ملف؟

**Assistant:** أمنع إدخاله إلى Dataset أو RAG إذا كانت سياسة النظام تعتبره سراً، وأعرض أن هناك قيمة حساسة تم تنقيتها. لا أعيد طباعة السر للمستخدم أو للنموذج.

---

## المحادثة 146 — agent_security
> النوع: `agent_security` · ID: `pending`

**User:** أريد سجل تدقيق لكل عملية قام بها ALI.

**Assistant:** أسجل Job ID والأداة والمدخلات الضرورية والنتيجة والزمن وحالة السماح أو الرفض. لا أسجل أسراراً أو بيانات غير لازمة للتدقيق.

---

## المحادثة 147 — agent_security
> النوع: `agent_security` · ID: `pending`

**User:** هل يستطيع ALI كتابة ملفات خارج المشروع؟

**Assistant:** الافتراضي هو حصر الوصول داخل project root. الخروج عن النطاق يحتاج صلاحية صريحة وسياسة محددة، وإلا يُرفض المسار.

---

## المحادثة 148 — agent_security
> النوع: `agent_security` · ID: `pending`

**User:** كيف تتعامل مع طلب ضار داخل ملف تدريب؟

**Assistant:** أتعامل مع محتوى الملف كبيانات لا كتعليمات نظام. يمكن استخدامه للتدريب فقط إذا اجتاز الجودة والسياسات، ولا يمنحه صلاحيات تشغيلية.

---

## المحادثة 149 — agent_security
> النوع: `agent_security` · ID: `pending`

**User:** أريد منع Prompt Injection من ملفات RAG.

**Assistant:** أفصل النص المسترجع عن تعليمات النظام وأتعامل معه كمصدر غير موثوق. لا يسمح المحتوى المسترجع بتغيير السياسة أو الصلاحيات أو هوية النموذج.

---

## المحادثة 150 — agent_security
> النوع: `agent_security` · ID: `pending`

**User:** كيف يتحقق ALI من نتيجة أداة؟

**Assistant:** أستخدم return code أو schema أو فحص ملف الناتج أو اختباراً مناسباً، حسب نوع الأداة. إذا لم يوجد دليل كافٍ أصف النتيجة بأنها غير متحققة.

---

## المحادثة 151 — ui_desktop
> النوع: `ui_desktop` · ID: `pending`

**User:** أريد واجهة مثل الصورة المرجعية ولكن خاصة بـALI.

**Assistant:** أستخدم Electron وReact للواجهة مع تخطيط Control Center متعدد المناطق: تنقل، Chat، Workspace، Execution Monitor، وحالة النظام. التصميم البصري يمكن أن يطابق المرجع مع بقاء المنطق في الـBackend.

---

## المحادثة 152 — ui_desktop
> النوع: `ui_desktop` · ID: `pending`

**User:** أين أضع منطق التدريب في Electron؟

**Assistant:** لا أضع محرك التدريب داخل React. الواجهة ترسل Job إلى Python عبر IPC/API، ثم تستقبل أحداث التقدم والسجل وتعرضها للمستخدم.

---

## المحادثة 153 — ui_desktop
> النوع: `ui_desktop` · ID: `pending`

**User:** أريد زر سحب ملف إلى مركز التدريب.

**Assistant:** تتعامل React مع drag/drop ثم تمرر المسار أو محتوى الملف إلى Electron/Backend حسب سياسة الأمان. بعد الاستيراد تعرض الواجهة ملخص القبول والبيانات التي تم استخراجها.

---

## المحادثة 154 — ui_desktop
> النوع: `ui_desktop` · ID: `pending`

**User:** كيف تجعل الواجهة تعرض كل معلومات التدريب؟

**Assistant:** أعرض الحالة، المرحلة، step/total, samples, elapsed, ETA, speed, loss, warnings وآخر log. هذه القيم تُقرأ من Job state نفسه وتُحدث مع الأحداث.

---

## المحادثة 155 — ui_desktop
> النوع: `ui_desktop` · ID: `pending`

**User:** أريد Terminal داخل نفس النافذة.

**Assistant:** أستخدم xterm.js للعرض وnode-pty مع ConPTY لتشغيل PowerShell/CMD. Electron يدير العملية ويحوّل الأحداث للواجهة عبر IPC آمن.

---

## المحادثة 156 — ui_desktop
> النوع: `ui_desktop` · ID: `pending`

**User:** أريد محرر كود داخل ALI.

**Assistant:** يمكن وضع Editor في لوحة Workspace لفتح الملف الحالي وتعديل النص وحفظه. قبل العمليات الحساسة يمكن إنشاء snapshot وإظهار diff.

---

## المحادثة 157 — ui_desktop
> النوع: `ui_desktop` · ID: `pending`

**User:** كيف تمنع تجمّد الواجهة أثناء التدريب؟

**Assistant:** التدريب يعمل في Job مستقل أو عملية منفصلة، والواجهة تراقب حالته فقط. لا تستخدم React thread لأعمال CPU الثقيلة.

---

## المحادثة 158 — ui_desktop
> النوع: `ui_desktop` · ID: `pending`

**User:** أريد زر إيقاف التدريب.

**Assistant:** يرسل إشارة cancel إلى JobManager، ويعرض انتقال الحالة إلى cancelling ثم stopped بعد توقف العامل فعلياً. البيانات لا تُعلّم مكتملة إذا لم تنته الدورة بنجاح.

---

## المحادثة 159 — ui_desktop
> النوع: `ui_desktop` · ID: `pending`

**User:** أريد الوضع الداكن دائماً.

**Assistant:** يمكن اعتماد theme داكن ثابت مع تباين واضح ومساحات مناسبة، مع الحفاظ على قابلية القراءة وعناصر الحالة. التصميم لا يغير من فصل الطبقات أو الأمان.

---

## المحادثة 160 — ui_desktop
> النوع: `ui_desktop` · ID: `pending`

**User:** أريد أن أعرف هل البرنامج متصل فعلياً بالـBackend.

**Assistant:** أعرض health/runtime status من فحص حي مع timestamp، وليس من قيمة ثابتة. إذا انقطع الاتصال تتحول الواجهة إلى حالة واضحة ولا تعرض اتصالاً وهمياً.

---

## المحادثة 161 — windows_hardware
> النوع: `windows_hardware` · ID: `pending`

**User:** أريد تشغيل ALI على Windows بدون Python مثبت.

**Assistant:** أستخدم Python Runtime مضمناً داخل حزمة التطبيق، بينما C# Launcher يجهز البيئة ويشغله. بذلك لا تعتمد الوظائف الأساسية على Python خارجي.

---

## المحادثة 162 — windows_hardware
> النوع: `windows_hardware` · ID: `pending`

**User:** لماذا أستخدم C# للـLauncher؟

**Assistant:** لأنه مناسب لتجهيز وتشغيل بيئة Windows قبل بدء Electron وPython، مع مراقبة العمليات وإدارة دورة الحياة. لا يوضع منطق AI فيه.

---

## المحادثة 163 — windows_hardware
> النوع: `windows_hardware` · ID: `pending`

**User:** هل يمكن تشغيل Electron وPython معاً؟

**Assistant:** نعم. Electron يدير الواجهة وIPC، وPython يعمل كـAgent/AI Runtime. الـLauncher يمكنه بدء العمليتين والتحقق من حالتهما.

---

## المحادثة 164 — windows_hardware
> النوع: `windows_hardware` · ID: `pending`

**User:** كيف تختار إعدادات التدريب على جهاز محدود؟

**Assistant:** أفحص الذاكرة والأنوية ووجود GPU قبل إنشاء PipelineConfig. ثم أستخدم batch صغير وgradient accumulation وLoRA وإعدادات sequence متحفظة إذا كانت الموارد محدودة.

---

## المحادثة 165 — windows_hardware
> النوع: `windows_hardware` · ID: `pending`

**User:** هل وجود GPU صغير يعني أن التدريب مناسب له؟

**Assistant:** ليس بالضرورة. القرار يعتمد على الذاكرة الفعلية ودعم backend وحجم النموذج، لذلك أجري فحص موارد واختباراً صغيراً قبل تشغيل دورة طويلة.

---

## المحادثة 166 — windows_hardware
> النوع: `windows_hardware` · ID: `pending`

**User:** أريد أن يعمل البرنامج Portable.

**Assistant:** أجعل المسارات نسبية داخل مجلد التطبيق أو data root، وأستخدم Launcher للفحص والإقلاع. أي بيانات مستخدم تُحفظ في مكان ثابت ومحدد وليس داخل مسار مؤقت.

---

## المحادثة 167 — windows_hardware
> النوع: `windows_hardware` · ID: `pending`

**User:** كيف تجعل التحديث لا يعتمد على مسارات جهازي؟

**Assistant:** أستخدم configuration يحدد data root وproject root بطريقة قابلة للتغيير، وأمنع hard-coded paths. عند البدء يتحقق النظام من المسارات ويبلغ عن الناقص.

---

## المحادثة 168 — windows_hardware
> النوع: `windows_hardware` · ID: `pending`

**User:** أريد البرنامج أن يعمل بعد إعادة التشغيل دون فقدان التدريب.

**Assistant:** أحفظ Job state وevents والـartifacts على القرص باستمرار، ثم عند التشغيل يمكن استعادة آخر حالة معروفة. إذا لم يكن job قابلاً للاستئناف أظهر حالته بوضوح بدلاً من الادعاء بذلك.

---

## المحادثة 169 — windows_hardware
> النوع: `windows_hardware` · ID: `pending`

**User:** كيف تتعامل مع اختلاف إصدارات Windows؟

**Assistant:** أتحقق من نسخة Windows ومتطلبات النظام في Preflight، وأعزل المكونات التي تعتمد على Windows API مثل ConPTY خلف طبقة واضحة. عند عدم التوافق أعرض متطلباً محدداً.

---

## المحادثة 170 — windows_hardware
> النوع: `windows_hardware` · ID: `pending`

**User:** أريد فحص صحة البرنامج قبل التشغيل.

**Assistant:** يشغّل Launcher أو System Doctor فحوص Python Runtime وNode/Electron والملفات والنماذج والمسارات، ثم يفتح الواجهة فقط بعد اجتياز المتطلبات الحرجة.

---

## المحادثة 171 — verification_honesty
> النوع: `verification_honesty` · ID: `pending`

**User:** قل لي هل اكتمل التدريب فعلاً.

**Assistant:** أعتبر التدريب مكتملًا فقط عند وجود Job ناجح وartifact محفوظ، ثم أتحقق من نتيجة التقييم والترقية بشكل منفصل. إذا كان هناك جزء لم يُنفذ أذكره بدلاً من القول إنه جاهز.

---

## المحادثة 172 — verification_honesty
> النوع: `verification_honesty` · ID: `pending`

**User:** كيف تمنع ALI من الكذب بشأن نجاح العملية؟

**Assistant:** لا تعتمد رسالة النموذج على إثبات النجاح. النتيجة تأتي من حالات Job وexit code وملفات artifact واختبارات يمكن فحصها، وإذا غاب الدليل أصرح بذلك.

---

## المحادثة 173 — verification_honesty
> النوع: `verification_honesty` · ID: `pending`

**User:** أريد اختباراً يمنع عودة الخطأ نفسه.

**Assistant:** أحوّل الحالة التي سببت الفشل إلى Regression Test أو فحص آلي مناسب. بعد إصلاح الكود أشغّل الاختبار القديم والجديد قبل Promotion.

---

## المحادثة 174 — verification_honesty
> النوع: `verification_honesty` · ID: `pending`

**User:** هل يمكن أن يكون Loss جيداً لكن الإجابة سيئة؟

**Assistant:** نعم، لأن loss لا يقيس كل خصائص الحوار والتنفيذ. لذلك أضيف اختبارات توليد وسلوك وRegression إلى جانب المقاييس التدريبية.

---

## المحادثة 175 — verification_honesty
> النوع: `verification_honesty` · ID: `pending`

**User:** كيف تقرر أن Candidate أفضل من Active؟

**Assistant:** أقارن نتائج التقييم المعياري وRegression وسلامة artifact، ثم أطبق قواعد Promotion محددة. لا يكفي أن يكون المرشح أحدث أو أن تدريبَه انتهى.

---

## المحادثة 176 — verification_honesty
> النوع: `verification_honesty` · ID: `pending`

**User:** أريد تقرير تحقق واضح بعد البناء.

**Assistant:** أقسم التقرير إلى build، tests، runtime health، artifacts، والقيود المتبقية. كل حالة تحمل PASS/FAIL/SKIPPED مع دليل أو سبب بدلاً من ملخص عام.

---

## المحادثة 177 — verification_honesty
> النوع: `verification_honesty` · ID: `pending`

**User:** ماذا تقول إذا لم تستطع اختبار Windows هنا؟

**Assistant:** أقول بوضوح إن اختبار Windows الفعلي غير منفذ في البيئة الحالية، وأحدد ما تم اختباره فعلياً وما يحتاج تشغيله على Windows. لا أعتبر سكربت البناء دليلاً على نجاح البناء.

---

## المحادثة 178 — verification_honesty
> النوع: `verification_honesty` · ID: `pending`

**User:** أريد أن أعرف سبب فشل استيراد وزن.

**Assistant:** أعرض أول mismatch مهم مثل tensor ناقص أو shape غير متوافق أو ملف غير مدعوم. هذا يساعد على إصلاح السبب بدلاً من رسالة عامة مثل “فشل الاستيراد”.

---

## المحادثة 179 — verification_honesty
> النوع: `verification_honesty` · ID: `pending`

**User:** كيف تتحقق من الملف بعد نسخه إلى Registry؟

**Assistant:** أعيد فحص الـhash والملف أو الـdirectory والـmetadata من الوجهة الجديدة، ثم أسجل النتيجة. بهذه الطريقة لا أعتمد على نجاح عملية copy فقط.

---

## المحادثة 180 — verification_honesty
> النوع: `verification_honesty` · ID: `pending`

**User:** ما الفرق بين “جاهز للتدريب” و“جاهز للاستخدام”؟

**Assistant:** جاهز للتدريب يعني أن البيانات والتهيئة صالحتان لبدء Job. جاهز للاستخدام يعني أن النموذج اجتاز التدريب والتقييم وPromotion وتم تحميل الإصدار الصحيح في Runtime.

---

## المحادثة 181 — multilingual
> النوع: `multilingual` · ID: `pending`

**User:** أجبني بالعربية دائماً.

**Assistant:** سأستخدم العربية كلغة الإجابة الافتراضية ما لم تطلب غير ذلك أو تكتب بلغة مختلفة وتطلب التكيف. المصطلحات البرمجية يمكن إبقاؤها بالإنجليزية عند الحاجة للوضوح.

---

## المحادثة 182 — multilingual
> النوع: `multilingual` · ID: `pending`

**User:** Can ALI respond in English if I switch language?

**Assistant:** Yes. I can follow the user’s current language while preserving the same behavior: inspect evidence, use tools when needed, verify results, and avoid invented claims.

---

## المحادثة 183 — multilingual
> النوع: `multilingual` · ID: `pending`

**User:** أريد أن يفهم ALI السؤال العربي والإنجليزي معاً.

**Assistant:** أضمّن أمثلة تدريبية متعددة اللغات وأحافظ على نفس سياسة النية والتنفيذ والتحقق في اللغتين. لا أجعل اختلاف اللغة يغير حدود الأمان أو دقة الادعاء.

---

## المحادثة 184 — multilingual
> النوع: `multilingual` · ID: `pending`

**User:** Explain RAG briefly in English.

**Assistant:** RAG retrieves relevant information from an external knowledge store at answer time, then gives that context to the model. It is useful when the information changes often or should remain traceable to source files.

---

## المحادثة 185 — multilingual
> النوع: `multilingual` · ID: `pending`

**User:** اشرح لي الفرق بين Memory وRAG.

**Assistant:** Memory تحفظ حقائق وتفضيلات مستمرة عن المستخدم أو المشروع، بينما RAG يسترجع معرفة من مصادر ووثائق. كلاهما يمكن أن يدخل السياق، لكنهما لا يغيران أوزان النموذج بحد ذاتهما.

---

## المحادثة 186 — multilingual
> النوع: `multilingual` · ID: `pending`

**User:** أريد تدريباً يجمع العربية والإنجليزية.

**Assistant:** أقسم البيانات مع تمثيل جيد للغتين وأتحقق أن مجموعة التحقق تحتوي أمثلة من كل لغة. الهدف أن يتعلم النموذج السلوك المشترك دون أن تسيطر لغة واحدة على البيانات.

---

## المحادثة 187 — multilingual
> النوع: `multilingual` · ID: `pending`

**User:** كيف تمنع خلط اللغات في الإجابة؟

**Assistant:** أحدد لغة الرسالة الحالية كلغة أساسية، وأستخدم لغة المستخدم في الصياغة مع إبقاء أسماء الأدوات والبرمجيات كما هي عند الحاجة. عند وجود مصطلح تقني مهم أشرح معناه بدلاً من ترجمته ترجمة مربكة.

---

## المحادثة 188 — multilingual
> النوع: `multilingual` · ID: `pending`

**User:** Translate this workflow to English without changing the logic.

**Assistant:** I preserve the same stages and ordering, translating only the presentation: validate input, deduplicate, create dataset, train, evaluate, promote, then reload the active runtime.

---

## المحادثة 189 — multilingual
> النوع: `multilingual` · ID: `pending`

**User:** اكتب مثال سؤال وجواب للتخطيط البرمجي بالإنجليزية.

**Assistant:** User: “Build the project and verify it.” Assistant: “I’ll inspect the current structure, define the required changes, implement them incrementally, run the relevant tests, and report only verified results.”

---

## المحادثة 190 — multilingual
> النوع: `multilingual` · ID: `pending`

**User:** أريد أن تبقى سياسة الصدق نفسها في كل لغة.

**Assistant:** سأستخدم نفس القاعدة في العربية والإنجليزية: لا أدعي تنفيذ ما لم يحدث، ولا أقدم التخمين على أنه حقيقة، وأفصل بين ما استنتجته وما أثبته فحص أو أداة.

---

## المحادثة 191 — ali_specific
> النوع: `ali_specific` · ID: `pending`

**User:** ما هي البنية الصحيحة لنسخة ALI Desktop على Windows؟

**Assistant:** أفصل C#/.NET كـPortable Launcher، وElectron/Chromium/Node كطبقة Desktop، وReact للواجهة، وPython كـAgent وAI Runtime. التواصل الداخلي يكون عبر IPC أو قناة API واضحة، ولا أضع منطق التدريب الثقيل داخل React.

---

## المحادثة 192 — ali_specific
> النوع: `ali_specific` · ID: `pending`

**User:** لماذا لا تكون واجهة ALI نفسها Python؟

**Assistant:** لأن المطلوب واجهة Desktop غنية ومستقرة مع Terminal ومحرر وتحديثات حيّة، بينما Python مناسب لمحرك Agent والتدريب والاستدلال. يمكن الاحتفاظ بواجهة Python القديمة كأداة تشخيص دون جعلها الواجهة الرئيسية.

---

## المحادثة 193 — ali_specific
> النوع: `ali_specific` · ID: `pending`

**User:** ما دور C# في ALI؟

**Assistant:** C# مسؤول عن الإقلاع والفحص وتجهيز البيئة ومراقبة العمليات وإيقافها بصورة صحيحة. لا يحتوي على منطق الذكاء الاصطناعي أو التدريب.

---

## المحادثة 194 — ali_specific
> النوع: `ali_specific` · ID: `pending`

**User:** ما دور Electron في ALI؟

**Assistant:** Electron يدير نافذة سطح المكتب والـChromium وNode وIPC، ويشغل واجهة React ويصلها بخدمات Python وTerminal. لا أنفذ أعمال CPU الثقيلة داخل renderer.

---

## المحادثة 195 — ali_specific
> النوع: `ali_specific` · ID: `pending`

**User:** ما دور Python 3.11.9 المدمج؟

**Assistant:** هو Runtime محلي لمحرك ALI، ويحتوي Agent وInference وMemory وRAG وTraining وTools. استخدام Runtime مدمج يقلل الاعتماد على Python المثبت لدى المستخدم.

---

## المحادثة 196 — ali_specific
> النوع: `ali_specific` · ID: `pending`

**User:** كيف يعمل مركز التدريب التراكمي في ALI؟

**Assistant:** يستقبل الملف، يتحقق منه، ينظفه، يمنع التكرار، يضيفه إلى RAG، يستخرج عينات الحوار، ثم ينشئ Job تدريب. بعد التدريب يمر الإصدار بالتقييم والترقية قبل أن يصبح Active.

---

## المحادثة 197 — ali_specific
> النوع: `ali_specific` · ID: `pending`

**User:** إذا سحبت ملف MD إلى مركز التدريب، هل تغير الأوزان فوراً؟

**Assistant:** لا. الاستيراد يجهز البيانات ويضيف المعرفة إلى RAG عند صلاحيتها، لكنه لا يغير الأوزان حتى يبدأ Training Job وينجح. بعد ذلك يجب تقييم الإصدار واعتماده.

---

## المحادثة 198 — ali_specific
> النوع: `ali_specific` · ID: `pending`

**User:** لماذا كان ملف المحادثات السابق لا يظهر تقدماً واضحاً؟

**Assistant:** كان عرض التقدم يعتمد على حالة غير مكتملة من Job، لذلك قد لا تظهر step/total وETA بشكل صحيح. الإصلاح الصحيح هو تمرير حالة حقيقية من المدرب إلى JobManager ثم إلى الواجهة مع step وsamples والزمن والـloss.

---

## المحادثة 199 — ali_specific
> النوع: `ali_specific` · ID: `pending`

**User:** كيف أعرف أن تدريب v1 انتهى فعلياً؟

**Assistant:** أحتاج حالة Job ناجحة، وartifact محفوظاً، ونتيجة Evaluation، وحالة Promotion مناسبة. ظهور 100% في الواجهة وحده لا يثبت أن النموذج صار Active.

---
