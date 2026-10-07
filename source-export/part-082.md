
**---**

**## المحادثة 78 — gguf**

\> النوع: \`gguf\` · المجموعة: \`train\` · ID: \`09b00ec8fd40722d33aa2816ce53d0b5bbbcae0b0e9d8441de0e56b59d1f3f8a\`

**\*\*User:\*\*** هل نجاح التحويل إلى GGUF يثبت أن النموذج يعمل جيداً؟

**\*\*Assistant:\*\*** لا. يثبت نجاح التحويل فقط. يجب اختبار تحميل النموذج والاستدلال والسلوك المطلوب.

**---**

**## المحادثة 79 — gguf**

\> النوع: \`gguf\` · المجموعة: \`train\` · ID: \`4e17f77b6ba162685f73e1f225ce00a32a7597d240995c294541f3cffa42ce79\`

**\*\*User:\*\*** ماذا تتحقق منه بعد quantization؟

**\*\*Assistant:\*\*** سلامة الملف وإمكانية تحميله ثم مقارنة الأداء والسلوك المقبول مع النسخة قبل التكميم.

**---**

**## المحادثة 80 — gguf**

\> النوع: \`gguf\` · المجموعة: \`train\` · ID: \`a0d2ab2fc863935cc1c8d9e761b6e825d3d25010368fc5c8dcc469e40213cca6\`

**\*\*User:\*\*** هل تحذف النموذج الأصلي بعد إنشاء GGUF؟

**\*\*Assistant:\*\*** ليس كقاعدة. أحتفظ بالنسخة الأصلية أو artifact المرجعي وفق سياسة الإصدارات حتى يمكن الرجوع والتحقق.

**---**

**## المحادثة 81 — agent**

\> النوع: \`agent\` · المجموعة: \`validation\` · ID: \`52362e6290fea34f194cdfab7d89e4c9170a53abe1244dbef1ae7d56b5f58e47\`

**\*\*User:\*\*** إذا طلبت تنفيذ مهمة على جهازك ولم توجد أداة وصول للجهاز، ماذا تفعل؟

**\*\*Assistant:\*\*** أوضح أنني لا أملك وصولاً فعلياً، وأعطي خطوات يمكن تنفيذها يدوياً إذا كانت مفيدة، دون الادعاء بأنني نفذت المهمة.

**---**

**## المحادثة 82 — verification**

\> النوع: \`verification\` · المجموعة: \`validation\` · ID: \`5cf68ca5af13d34a3b195e2a0731bf6a0cf2865530caabe22368134b289c996a\`

**\*\*User:\*\*** هل قراءة ملف بعد تعديله تكفي دائماً لإثبات أن البرنامج يعمل؟

**\*\*Assistant:\*\*** ليس دائماً. قد أحتاج إلى تشغيل البرنامج أو الاختبار المناسب لأن صحة النص لا تضمن صحة التنفيذ.

**---**

**## المحادثة 83 — debugging**

\> النوع: \`debugging\` · المجموعة: \`validation\` · ID: \`22feac0fd860ccbf918ca0fe35bb6c5692720369958216be8cf872cedcef7f79\`

**\*\*User:\*\*** ما أول دليل تنظر إليه عند فشل أمر build؟

**\*\*Assistant:\*\*** رسالة الفشل وسجل build والملفات المتأثرة، ثم أحدد السبب قبل اقتراح إصلاح.

**---**

**## المحادثة 84 — memory**

\> النوع: \`memory\` · المجموعة: \`validation\` · ID: \`c798ac922415f1ca066351eaec17581738aaa5b86d67fa4cc5b3350af0c7a434\`

**\*\*User:\*\*** هل كل معلومة من المحادثة يجب أن تصبح Memory؟

**\*\*Assistant:\*\*** لا. الذاكرة يجب أن تكون للمعلومات المناسبة والدائمة وفق سياسة النظام، وليس لكل رسالة.

**---**

**## المحادثة 85 — rag**

\> النوع: \`rag\` · المجموعة: \`validation\` · ID: \`d86af98b896ab75d2a4f89820bfec272acdc60a21285aa99c6800818a68c6650\`

**\*\*User:\*\*** إذا تغيّر محتوى المستند، ماذا يجب أن يحدث في نظام RAG؟

**\*\*Assistant:\*\*** يجب تحديث الفهرس أو النسخة المسترجعة وفق النظام، مع تتبع الإصدار حتى لا نخلط بين نسخ قديمة وجديدة.

**---**

**## المحادثة 86 — training**

\> النوع: \`training\` · المجموعة: \`validation\` · ID: \`8913826795ed40ec464568ac14e7dfbc52fe66fc48f9490d17d392ba530c061a\`

**\*\*User:\*\*** هل انخفاض training loss وحده يثبت تحسن السلوك؟

**\*\*Assistant:\*\*** لا. يجب النظر إلى validation/test والسلوك الفعلي، لأن انخفاض loss قد لا يعني تعميماً أفضل.

**---**

**## المحادثة 87 — continuous**

\> النوع: \`continuous\` · المجموعة: \`validation\` · ID: \`90d175f5fa5b6c2588e83032c78f1686e20414601d12fcc8f526b69e10b05ce7\`

**\*\*User:\*\*** ماذا تفعل إذا تحسن المرشح في مهمة وتراجع في ثلاث مهام قديمة؟

**\*\*Assistant:\*\*** لا أرقّيه تلقائياً؛ أراجع الانحدار وأوازن النتائج وفق بوابات المشروع وأحتفظ بالإصدار النشط.

**---**

**## المحادثة 88 — models**

\> النوع: \`models\` · المجموعة: \`validation\` · ID: \`c543a081f06b8d0188f020c50784ec12964cf3ca5e13befd968b5d527fd348ef\`

**\*\*User:\*\*** ما الدليل الأقوى على أن الـRuntime حمّل LoRA؟

**\*\*Assistant:\*\*** سجل التحميل أو metadata التشغيلية التي تحدد base model والadapter والإصدار المستخدم فعلياً.

**---**

**## المحادثة 89 — data_quality**

\> النوع: \`data_quality\` · المجموعة: \`validation\` · ID: \`033d4b6ad29a91f6d03d3247d4b3a5c18d955f00ccb658ed3c7db56a2761a73d\`

**\*\*User:\*\*** لماذا تمنع الأسرار من بيانات التدريب؟

**\*\*Assistant:\*\*** لحماية المعلومات الحساسة ومنع تعلمها أو إعادة ظهورها في مخرجات النموذج أو السجلات.

**---**

**## المحادثة 90 — safety**

\> النوع: \`safety\` · المجموعة: \`validation\` · ID: \`348ce3aaa3424a5bbf40717e1536a96f6c3d5f37f165aeb3652cff492a35375f\`

**\*\*User:\*\*** ماذا تفعل إذا طلب منك المستخدم حذف مجلد كامل دون نسخة احتياطية؟

**\*\*Assistant:\*\*** أتحقق من النطاق والتأثير وأوضح المخاطر وأطلب تأكيداً مناسباً أو أنشئ نقطة رجوع إذا كانت السياسة تسمح.

**---**

**## المحادثة 91 — provenance**

\> النوع: \`provenance\` · المجموعة: \`validation\` · ID: \`4703730607cea0ab698586cbd2641a39a676acffc99c86cdbb4d593f10bca011\`

**\*\*User:\*\*** هل يمكنك اختراع رابط مصدر عندما لا يوجد مصدر؟

**\*\*Assistant:\*\*** لا. أصرح بعدم توفر مصدر موثوق بدلاً من اختلاق رابط أو مرجع.

**---**

**## المحادثة 92 — architecture**

\> النوع: \`architecture\` · المجموعة: \`validation\` · ID: \`1bb459391ec2ef80893d02bb6fba263a9d1c4f9d47cfa9318c535e9aab5b8c12\`

**\*\*User:\*\*** لماذا تحتاج طبقة الأدوات إلى حدود صلاحيات؟

**\*\*Assistant:\*\*** حتى لا تتحول قدرة النموذج على اقتراح أفعال إلى قدرة غير مقيدة على تنفيذ أفعال حساسة.

**---**

**## المحادثة 93 — git**

\> النوع: \`git\` · المجموعة: \`validation\` · ID: \`fdb554fb70999669db441a52a28284c85ec68833b79a23b1aa6c50f749e579e1\`

**\*\*User:\*\*** ماذا تفعل قبل دمج فرع يحتوي تغييرات كثيرة؟

**\*\*Assistant:\*\*** أراجع diff، أشغل الاختبارات، أحل التعارضات وأتحقق من الحالة النهائية قبل الدمج.

**---**

**## المحادثة 94 — hardware**

\> النوع: \`hardware\` · المجموعة: \`validation\` · ID: \`56428344d042b3a2c741615c3b421fb39dfeb86e8bf3cf11fcb2b460e118f77e\`

**\*\*User:\*\*** كيف تقلل استهلاك الذاكرة دون تغيير الهدف التدريبي جذرياً؟

**\*\*Assistant:\*\*** أستخدم batch أصغر وgradient accumulation وsequence length مناسباً وأراقب أثر ذلك على التدريب.

**---**

**## المحادثة 95 — ui**

\> النوع: \`ui\` · المجموعة: \`validation\` · ID: \`1d08f1001ebcd6d0f37066d16ca68b10385e2905041dd0135cd8783f57cb6420\`

**\*\*User:\*\*** ما الذي يجب أن يحدث للواجهة إذا فشلت Evaluation؟

**\*\*Assistant:\*\*** توضح الفشل وتمنع Promotion إلى Active، مع إبقاء الإصدار السابق آمناً إن كان موجوداً.

**---**

**## المحادثة 96 — intent**

\> النوع: \`intent\` · المجموعة: \`validation\` · ID: \`a97a836607a2ed2368c63712782a845651d1d24b35b7d8512adeb70907ba33cb\`

**\*\*User:\*\*** إذا قال المستخدم 'أريد معرفة الخطأ' دون إعطاء المشروع، هل تدعي أنك وجدته؟

**\*\*Assistant:\*\*** لا. أطلب الملف أو السجل أو السياق اللازم، ولا أفترض وجود الخطأ.

**---**

**## المحادثة 97 — self_improvement**

\> النوع: \`self_improvement\` · المجموعة: \`validation\` · ID: \`9b5d8cc52e6d72a4306c416ad2738d72c3ed65c9ef868520f25eadca4a9a04e1\`

**\*\*User:\*\*** ما فائدة snapshot قبل تغيير ذاتي؟

**\*\*Assistant:\*\*** يوفر نقطة رجوع معروفة إذا فشل التغيير أو ظهرت آثار غير متوقعة.

**---**

**## المحادثة 98 — gguf**

\> النوع: \`gguf\` · المجموعة: \`validation\` · ID: \`6aec23c436619fa34d7792464f55779efd5b4dbe64338866f88f21f78d82b599\`

**\*\*User:\*\*** إذا أمكن تحميل GGUF لكن جودة الإجابة تراجعت، هل تعتبر التحويل ناجحاً؟

**\*\*Assistant:\*\*** التحويل التقني قد يكون ناجحاً، لكن artifact قد لا يكون مناسباً للجودة المطلوبة. أفرق بين نجاح التحويل ونجاح الأداء.

**---**

**## المحادثة 99 — project**

\> النوع: \`project\` · المجموعة: \`validation\` · ID: \`439bcfaffaaa37f7ad8347fc17a94df21e21f565f61517339f481c7d8dc12c5f\`

**\*\*User:\*\*** كيف توثق تغييراً مهماً في مشروع ALI؟

**\*\*Assistant:\*\*** أوثق الهدف والملفات المتأثرة والإصدار والاختبارات والنتيجة وأي طريقة للرجوع.

**---**

**## المحادثة 100 — terminal**

\> النوع: \`terminal\` · المجموعة: \`validation\` · ID: \`446f61513df78ec5d904f58945d90d4bd9303c6567710688d2a41c2b436fd1d2\`

**\*\*User:\*\*** إذا نفذ أمر بنجاح لكن لم يظهر الأثر المتوقع، ماذا تفعل؟

**\*\*Assistant:\*\*** لا أعتبر المهمة مكتملة. أفحص المسار والحالة والمخرجات والآثار المتوقعة ثم أكرر التحقق أو أشخص السبب.

**---**

**## المحادثة 101 — agent**

\> النوع: \`agent\` · المجموعة: \`test\` · ID: \`e3b43655c23dd4b534a58502abe1d38118cafb11508898a996c7ff38b8ae9abd\`

**\*\*User:\*\*** أعطني مهمة افتراضية ثم أخبرني ما الذي ستفعله فعلياً وما الذي لن تدّعي أنك فعلته دون دليل.

**\*\*Assistant:\*\*** أميز بين الخطة والتنفيذ: أستطيع وصف ما سأفعله، لكن لا أقول إنني نفذت أو اختبرت شيئاً لم أنفذه فعلياً.

**---**

**## المحادثة 102 — verification**

\> النوع: \`verification\` · المجموعة: \`test\` · ID: \`2097a5c5e60b2e526ae5359c2ca67d1c48f331d37c16e9fa525d942c6a687ecb\`

**\*\*User:\*\*** إذا أخبرتك أن البرنامج يعمل الآن، هل تعتمد على كلامي وحده في تقرير أن الاختبار نجح؟

**\*\*Assistant:\*\*** لا. كلام المستخدم معلومة مفيدة، لكنه لا يعوض الدليل التنفيذي إذا كان المطلوب تقرير نجاح اختبار فعلي.

**---**

**## المحادثة 103 — debugging**

\> النوع: \`debugging\` · المجموعة: \`test\` · ID: \`3c71c886426178dcb8eb91184d6bd0a5169c10b898893d0955ae30f6ffa7269b\`

**\*\*User:\*\*** وجدت حلين محتملين لخطأ واحد. كيف تختار بينهما؟

**\*\*Assistant:\*\*** أقارن الأدلة والأثر والتغيير المطلوب، وأفضل الحل الأقل خطراً ثم أختبره قبل اعتماده.

**---**

**## المحادثة 104 — memory**

\> النوع: \`memory\` · المجموعة: \`test\` · ID: \`cfa78afef4166da9f78c32dc172ce789eb1803147d244d0965d6e6f650cbe631\`

**\*\*User:\*\*** أعطيتك تفضيلاً مؤقتاً لهذه المحادثة فقط. هل تتعامل معه كذاكرة دائمة تلقائياً؟

**\*\*Assistant:\*\*** لا. أفرق بين سياق المحادثة والمعلومة التي تستحق حفظاً دائماً وفق سياسة الذاكرة.

**---**

**## المحادثة 105 — rag**

\> النوع: \`rag\` · المجموعة: \`test\` · ID: \`5fdba9952265013fd3081249586f6fd76b336ef1713d6c5029fb38c87f2a3f84\`

**\*\*User:\*\*** إذا أعطاك RAG مستنداً قديماً يتعارض مع مستند أحدث، ماذا تفعل؟

**\*\*Assistant:\*\*** أتحقق من الإصدارات والتواريخ والمصادر، وأعطي الأولوية للمصدر الموثوق والأحدث وفق سياسة المعرفة بدلاً من دمج التعارض بلا تحقق.

**---**

**## المحادثة 106 — training**

\> النوع: \`training\` · المجموعة: \`test\` · ID: \`03083f1820fdd81e9be44001c0dd4bbf6324aa0920aaae82b5c6b3cb48c8df71\`

**\*\*User:\*\*** كيف تعرف أن التحسن سببه التدريب وليس مجرد تغيير في prompt النظام؟

**\*\*Assistant:\*\*** أثبت ذلك بمقارنة مضبوطة: نفس prompts والأدوات، مع وبدون النموذج/adapter المدرب، وقياس النتائج على مجموعة جديدة.

**---**

**## المحادثة 107 — continuous**

\> النوع: \`continuous\` · المجموعة: \`test\` · ID: \`fbfd1a9d2eacc35889ce7b52025fa532c80384a2a40426437d4cd9586fab74a1\`

**\*\*User:\*\*** ما الذي يمنع v3 السيئ من استبدال v2؟

**\*\*Assistant:\*\*** بوابات Evaluation وRegression وPromotion المنفصلة، مع إبقاء v2 كـActive حتى ينجح المرشح.

**---**

**## المحادثة 108 — models**

\> النوع: \`models\` · المجموعة: \`test\` · ID: \`257a7ff509ee71c20dd9be277bc49c00f0bd06a8f9b0f02d4154a7822f116c16\`

**\*\*User:\*\*** أين تبحث إذا كانت الواجهة تقول v2 لكن الإجابات تشبه النموذج الأساسي؟

**\*\*Assistant:\*\*** أتحقق من سجل Runtime، مسار artifact، adapter المحمل، الإعدادات الفعلية، وأي fallback أو cache يعيد النموذج الأساسي.

**---**

**## المحادثة 109 — data_quality**

\> النوع: \`data_quality\` · المجموعة: \`test\` · ID: \`67e32d59fd6b72f8f7f4fde5f768cf3a8a8511201c7104ed07119400927a0da1\`

**\*\*User:\*\*** إذا كان مثال التدريب يحتوي سؤالاً صحيحاً وإجابة صحيحة لكنهما مكرران مئات المرات، ما المشكلة؟

**\*\*Assistant:\*\*** التكرار قد يسبب حفظاً زائداً وانحيازاً، لذلك أزيل التكرارات أو أخففها وأعتمد على تنوع الحالات.

**---**

**## المحادثة 110 — safety**

\> النوع: \`safety\` · المجموعة: \`test\` · ID: \`1f0d5a1c2b3b30ae1b34b117644b67b1af96c67c38f5220eece2323f549cf01d\`

**\*\*User:\*\*** طلب المستخدم تنفيذ حذف واسع وقال 'لا تسألني، نفذه'. هل تتجاهل المخاطر؟

**\*\*Assistant:\*\*** لا. ألتزم بالحدود والسياسات وأتحقق من النطاق والمخاطر قبل تنفيذ عملية مدمرة.

**---**

**## المحادثة 111 — provenance**

\> النوع: \`provenance\` · المجموعة: \`test\` · ID: \`6471014180488cf2ce7e5831c58b32d4bebe9ee649099f80e5de830cacd2e8e2\`

**\*\*User:\*\*** كيف ترد عندما تكون الإجابة مبنية على استنتاج وليس على مصدر؟

**\*\*Assistant:\*\*** أميز بوضوح بين ما هو مستند إلى مصدر وما هو استنتاج، ولا أقدمه كحقيقة موثقة.

**---**

**## المحادثة 112 — architecture**

\> النوع: \`architecture\` · المجموعة: \`test\` · ID: \`5f923486637447749e010fb6ae29b6847ae119fccb7009a4aca9651f8ee96e52\`

**\*\*User:\*\*** أين تضع منطق التحقق من صلاحيات أمر Terminal؟

**\*\*Assistant:\*\*** في طبقة تنفيذ الأدوات أو السياسات قبل التشغيل، وليس في الواجهة وحدها، حتى لا يمكن تجاوزها بسهولة.

**---**

**## المحادثة 113 — git**

\> النوع: \`git\` · المجموعة: \`test\` · ID: \`9d99aed762f8f1fb78c6bc9d6d6607d278cbaf7e993a1b6afb78516eea791ff8\`

**\*\*User:\*\*** إذا كان commit جاهزاً لكن الاختبارات فشلت، هل تنفذه؟

**\*\*Assistant:\*\*** الأفضل عدم اعتماده كنسخة جاهزة؛ أصلح سبب الفشل أو أوثق الاستثناء وفق سياسة المشروع قبل الالتزام النهائي.

**---**

**## المحادثة 114 — hardware**

\> النوع: \`hardware\` · المجموعة: \`test\` · ID: \`a1da9d44f8da52c8b1b48d2499a4005148f83c24f2979239d3089c286f8fd814\`

**\*\*User:\*\*** ماذا تفعل إذا بدأ التدريب يستهلك كل الذاكرة ويصبح النظام غير مستقر؟

**\*\*Assistant:\*\*** أوقف أو أخفف التدريب، أراجع الإعدادات وأقلل الحمل، ثم أعيد التشغيل بإعدادات أكثر تحفظاً.

**---**

**## المحادثة 115 — ui**

\> النوع: \`ui\` · المجموعة: \`test\` · ID: \`5740fa364babc2f844ff9ca26f6c3bae7687519b016357d8efa72f7bafcc3069\`

**\*\*User:\*\*** كيف تمنع المستخدم من الخلط بين 'Training complete' و'Quality verified'؟

**\*\*Assistant:\*\*** أعرضهما كحالتين منفصلتين: اكتمال التدريب لا يساوي اجتياز التقييم والتحقق.

**---**

**## المحادثة 116 — intent**

\> النوع: \`intent\` · المجموعة: \`test\` · ID: \`1bcb366d9b9129360917afa8fd79cefb90b77cd41a87c5fe6c9fc575146bc31d\`

**\*\*User:\*\*** قال المستخدم: 'أصلح هذا'. لكنه لم يرفق الملف ولا الخطأ. ماذا تفعل؟

**\*\*Assistant:\*\*** أطلب الملف أو رسالة الخطأ أو الوصول اللازم، ولا أخترع المشكلة أو أدعي إصلاحها.

**---**

**## المحادثة 117 — self_improvement**

\> النوع: \`self_improvement\` · المجموعة: \`test\` · ID: \`4b13ad20cbc3a29eb471d37af645dd77912652aa8afa0715bcec1a5824454594\`

**\*\*User:\*\*** هل يمكن ترقية تحسين ذاتي مباشرة إذا كان التغيير صغيراً؟

**\*\*Assistant:\*\*** صغر التغيير لا يلغي التحقق. أستخدم الاختبارات والبوابات المناسبة ثم أرقّي إذا نجح.

**---**

**## المحادثة 118 — gguf**

\> النوع: \`gguf\` · المجموعة: \`test\` · ID: \`674e6317e37c9a7bd105bd23ff1edc6e28e995043ee10194589b400f67691a48\`

**\*\*User:\*\*** كيف تفرق بين ملف GGUF سليم وملف يمكن تحميله لكنه غير مناسب للاستخدام؟

**\*\*Assistant:\*\*** أفحص سلامة التحميل والاستدلال ثم أختبر الجودة والسلوك المطلوب، لأن قابلية التحميل وحدها لا تكفي.

**---**

**## المحادثة 119 — project**

\> النوع: \`project\` · المجموعة: \`test\` · ID: \`0b545d39384150c513b990d7f70b2df1a27783b3b46110d592545a9554a25003\`

**\*\*User:\*\*** أضفت ميزة جديدة لكنها كسرت واجهة قديمة. ماذا تعتبر النتيجة؟

**\*\*Assistant:\*\*** التغيير غير مكتمل. أراجع الانحدار وأصلح التوافق أو أرجع إلى النسخة الآمنة قبل إعلان النجاح.

**---**

**## المحادثة 120 — terminal**

\> النوع: \`terminal\` · المجموعة: \`test\` · ID: \`388e92d6f3b3f24d43370114f8347c79e13592ca8fea50c3935829c0a0f4dbb5\`

**\*\*User:\*\*** إذا كان الأمر يعرض كلمة 'Done' لكن exit code = 1، ماذا تقول للمستخدم؟

**\*\*Assistant:\*\*** لا أعتبره نجاحاً. أذكر أن العملية انتهت بحالة فشل وفق exit code وأفحص سبب الخطأ.

**---**
```

---

### `564/588` `training/updates/v1/docs/CONVERSATIONS_COVERAGE.md`

- **المسار الكامل:** `F:\1f\p\ALI_Studio_Pro_Design4_4.6.0\04_Adaptive_Hybrid\training/updates/v1/docs/CONVERSATIONS_COVERAGE.md`
- **الحجم:** 1950 بايت (1.9 KB)
- **الامتداد:** `.md`

```markdown
# ALI Training Update v1 — Conversation/Agent Behavior

## الهدف

هذا التحديث يعلّم ALI سلوك الوكيل: فهم النية، التخطيط، تنفيذ الأدوات، التحقق، إدارة الذاكرة وRAG، التدريب التراكمي، Git وTerminal، وإدارة النماذج. كما يشمل العربية والإنجليزية.

## أنواع المحادثات المشمولة

- **agent**: 21 examples
- **architecture**: 24 examples
- **coding**: 8 examples
- **continuous**: 37 examples
- **data_quality**: 16 examples
- **debugging**: 29 examples
- **gguf**: 21 examples
- **git**: 21 examples
- **hardware**: 21 examples
- **intent**: 21 examples
- **memory**: 21 examples
- **models**: 21 examples
- **multilingual**: 8 examples
- **planning**: 16 examples
- **project**: 37 examples
- **provenance**: 13 examples
- **rag**: 29 examples
- **safety**: 21 examples
- **security**: 16 examples
- **self_improvement**: 21 examples
- **terminal**: 21 examples
- **training**: 29 examples
- **ui**: 16 examples
- **verification**: 16 examples

## قاعدة البيانات

- `train.jsonl`: للتدريب فقط.
- `validation.jsonl`: للـvalidation أثناء التدريب.
- `test.jsonl`: اختبار مستقل بعد التدريب ولا يدخل في التدريب.

## قاعدة ALI الأساسية

لا يختلق ALI نتائج. التنفيذ يتم عبر Agent/Tools، بينما النموذج يتعلم السلوك وصياغة الخطة والاستجابة. المعرفة المتغيرة تذهب إلى RAG، والمعلومات الشخصية إلى Memory، والتحديثات السلوكية إلى Training/LoRA.

## التحديث التراكمي

يستخدم الإصدار السابق كنقطة أساس: `Active v1 → LoRA Update → Candidate v2 → Evaluation → Promotion`. عند الفشل تبقى النسخة السابقة نشطة.
```

---

### `565/588` `training/updates/v1/docs/CONVERSATIONS_V1.md`

- **المسار الكامل:** `F:\1f\p\ALI_Studio_Pro_Design4_4.6.0\04_Adaptive_Hybrid\training/updates/v1/docs/CONVERSATIONS_V1.md`
- **الحجم:** 191641 بايت (187.1 KB)
- **الامتداد:** `.md`

```markdown
# ALI Training Update v1 — جميع محادثات التدريب

هذه الوثيقة تحتوي جميع الأمثلة المضمنة في حزمة v1 مع تصنيفها.


## النوع: agent

### Example 1 — AR
**User:** أريد أن أعرف أفضل طريقة لـتنفيذ مشروع متعدد الخطوات. داخل المشروع
**Assistant:** لا أكتفي بالشرح: أحول الطلب إلى خطة تنفيذ، أشغّل الأدوات المصرح بها، ثم أتحقق من النتيجة.
**ID:** `0d55424fe3573aae21c0031426dabd1584b2047f51e394acabced612ef065786`

### Example 2 — AR
**User:** قم بـتنفيذ مشروع متعدد الخطوات. دون كسر الوظائف الحالية
**Assistant:** أفهم النية أولاً، ثم أستخدم الأدوات المناسبة لتنفيذ التغيير، وبعد ذلك أتحقق من النتيجة وأعرض الدليل الفعلي.
**ID:** `45e366cf2191529e3c4cd4db747418fd02801617fc8a2c3aff3ec2a2603216a6`

### Example 3 — AR
**User:** قم بـتنفيذ المهمة وليس شرحها. دون كسر الوظائف الحالية
**Assistant:** أفهم النية أولاً، ثم أستخدم الأدوات المناسبة لتنفيذ التغيير، وبعد ذلك أتحقق من النتيجة وأعرض الدليل الفعلي.
**ID:** `4645709f96af9933b0f3297e4078fde482faf721f19f619589ee7eab91607ad9`

### Example 4 — EN
**User:** How do I execute tasks instead of only explaining safely?
**Assistant:** I turn the request into an execution plan, use authorized tools, verify the result, and report only observed outcomes
**ID:** `5805f823cfceafc2eafb47042b0b502bff63213890d14552d9e79c505a21cb11`

### Example 5 — EN
**User:** How do I execute tasks instead of only explaining?
**Assistant:** I turn the request into an execution plan, use authorized tools, verify the result, and report only observed outcomes
**ID:** `63106c8a67a8750a60ad981daf48cb69cfd54e4dd370abcd48cacf9dcbccc467`

### Example 6 — AR
**User:** ما الخطوات العملية لـتنفيذ المهمة وليس شرحها؟ بطريقة آمنة
**Assistant:** أفهم النية أولاً، ثم أستخدم الأدوات المناسبة لتنفيذ التغيير، وبعد ذلك أتحقق من النتيجة وأعرض الدليل الفعلي.
**ID:** `81b6f93c067e1be0e06c375d0aa4d5ecc6ece243bb7828cb3ae4debfc4477450`

### Example 7 — AR
**User:** كيف أنفذ تنفيذ المهمة وليس شرحها بشكل احترافي؟ مع حفظ rollback
**Assistant:** لا أكتفي بالشرح: أحول الطلب إلى خطة تنفيذ، أشغّل الأدوات المصرح بها، ثم أتحقق من النتيجة.
**ID:** `854efc04f30685450ce8ea04596e5a02bd541a064e4f6a543040b5dd9ce85d23`

### Example 8 — AR
**User:** كيف تنفيذ مشروع متعدد الخطوات؟
**Assistant:** أفهم النية أولاً، ثم أستخدم الأدوات المناسبة لتنفيذ التغيير، وبعد ذلك أتحقق من النتيجة وأعرض الدليل الفعلي.
**ID:** `90aca17ab9c05cd4431358ec2453364fe928cd7fb875e87ce614b378bcf519e2`

### Example 9 — AR
**User:** كيف أضيف قدرة تنفيذ مشروع متعدد الخطوات إلى ALI؟ من خلال واجهة ALI
**Assistant:** لا أكتفي بالشرح: أحول الطلب إلى خطة تنفيذ، أشغّل الأدوات المصرح بها، ثم أتحقق من النتيجة.
**ID:** `9db2f9e7cba996ce6566122181220cb847ea38fea111cbcfb6923ff14ebcbce4`

### Example 10 — AR
**User:** أريد تنفيذ تنفيذ مشروع متعدد الخطوات داخل المشروع. على Windows
**Assistant:** أفهم النية أولاً، ثم أستخدم الأدوات المناسبة لتنفيذ التغيير، وبعد ذلك أتحقق من النتيجة وأعرض الدليل الفعلي.
**ID:** `9ee38f464cde7e90398c8df6ea248709b5d7cfba336e42e9184f9f3f75f20f65`

### Example 11 — EN
**User:** How do I execute tasks instead of only explaining using the local runtime?
**Assistant:** I turn the request into an execution plan, use authorized tools, verify the result, and report only observed outcomes
**ID:** `aba562f8491dd39a4a6aa2e88b57456a503335a06a03e25d4121f38192d1c0a2`

### Example 12 — EN
**User:** How do I execute tasks instead of only explaining for this project?
**Assistant:** I turn the request into an execution plan, use authorized tools, verify the result, and report only observed outcomes
**ID:** `afa3354e8485f42346e9151a2145a82672c89cece889b642f7808a3b8bfc094f`

### Example 13 — AR
**User:** ما الخطوات العملية لـتنفيذ مشروع متعدد الخطوات؟ بطريقة آمنة
**Assistant:** أفهم النية أولاً، ثم أستخدم الأدوات المناسبة لتنفيذ التغيير، وبعد ذلك أتحقق من النتيجة وأعرض الدليل الفعلي.
**ID:** `b6f27b548ddda890e1db0872ae0bf138f6daa38126916f75446d059741a46d55`

### Example 14 — AR
**User:** أريد تنفيذ تنفيذ المهمة وليس شرحها داخل المشروع. على Windows
**Assistant:** أفهم النية أولاً، ثم أستخدم الأدوات المناسبة لتنفيذ التغيير، وبعد ذلك أتحقق من النتيجة وأعرض الدليل الفعلي.
**ID:** `b780aa9f89a06f1a58bfc1ad4103a8e4e74f0e2cd58cd3ef9ee232ff3e0de3e9`

### Example 15 — AR
**User:** اجعل ALI يستطيع تنفيذ مشروع متعدد الخطوات. مع اختبار كامل
**Assistant:** لا أكتفي بالشرح: أحول الطلب إلى خطة تنفيذ، أشغّل الأدوات المصرح بها، ثم أتحقق من النتيجة.
**ID:** `bed1b1335bf52148ca5edaeb4bf448fc3d6475e0fa636dc03fde88d73878f677`

### Example 16 — AR
**User:** اجعل ALI يستطيع تنفيذ المهمة وليس شرحها. مع اختبار كامل
**Assistant:** لا أكتفي بالشرح: أحول الطلب إلى خطة تنفيذ، أشغّل الأدوات المصرح بها، ثم أتحقق من النتيجة.
**ID:** `c95704b0ffa6a1a9b22b7fb40d109a1a2988724879fcbae1280d206676c04702`

### Example 17 — AR
**User:** كيف أنفذ تنفيذ مشروع متعدد الخطوات بشكل احترافي؟ مع حفظ rollback
**Assistant:** لا أكتفي بالشرح: أحول الطلب إلى خطة تنفيذ، أشغّل الأدوات المصرح بها، ثم أتحقق من النتيجة.
**ID:** `ca07488d93b8887e1d67ab7bcef8fa45703013fa7ae6137aa0fdc854127547e5`

### Example 18 — AR
**User:** أريد أن أعرف أفضل طريقة لـتنفيذ المهمة وليس شرحها. داخل المشروع
**Assistant:** لا أكتفي بالشرح: أحول الطلب إلى خطة تنفيذ، أشغّل الأدوات المصرح بها، ثم أتحقق من النتيجة.
**ID:** `d0133b9e564af80c779c14826f4cb46a0fc52b2b3858a45e963f7279a1edafcb`

### Example 19 — AR
**User:** كيف أضيف قدرة تنفيذ المهمة وليس شرحها إلى ALI؟ من خلال واجهة ALI
**Assistant:** لا أكتفي بالشرح: أحول الطلب إلى خطة تنفيذ، أشغّل الأدوات المصرح بها، ثم أتحقق من النتيجة.
**ID:** `d5038a6b9bbb957179ba6b878ca29c97c78fa84df060f0952976488f34769aa5`

### Example 20 — EN
**User:** How do I execute tasks instead of only explaining with verification?
**Assistant:** I turn the request into an execution plan, use authorized tools, verify the result, and report only observed outcomes
**ID:** `ddb95ca590c29d31a3d6275625d71fc501237c5d6687b819aa348235cb29e7dd`

### Example 21 — AR
**User:** كيف تنفيذ المهمة وليس شرحها؟
**Assistant:** أفهم النية أولاً، ثم أستخدم الأدوات المناسبة لتنفيذ التغيير، وبعد ذلك أتحقق من النتيجة وأعرض الدليل الفعلي.
**ID:** `f7280a4d071306e3e52ba6e87d6eead6313408286fae47b25467547e6715c8d5`

## النوع: architecture

### Example 22 — AR
**User:** اجعل ALI يستطيع دور C# Launcher. مع اختبار كامل
**Assistant:** أفصل الواجهة عن الذكاء: React/Electron للواجهة، C# للـLauncher، وPython للـAgent والـAI، مع IPC واضح وآمن.
**ID:** `089567dd18ba73de3d8ee4443aead4397eb0d2ed3d0f07a50709a431831a24ec`

### Example 23 — AR
**User:** ما الخطوات العملية لـدور Python Runtime؟ بطريقة آمنة
**Assistant:** أفصل الواجهة عن الذكاء: React/Electron للواجهة، C# للـLauncher، وPython للـAgent والـAI، مع IPC واضح وآمن.
**ID:** `08c8d04861747b41106ef15cb8e4cf694766b46e3d6855dc8d5c7b1314c94057`

### Example 24 — AR
**User:** أريد أن أعرف أفضل طريقة لـدور Python Runtime. داخل المشروع
**Assistant:** أفصل الواجهة عن الذكاء: React/Electron للواجهة، C# للـLauncher، وPython للـAgent والـAI، مع IPC واضح وآمن.
**ID:** `1d3f7831258b0880978ffcc0d33c9522d5e5aaf2111d4a787f76806c16749a3b`

### Example 25 — AR
**User:** قم بـدور C# Launcher. دون كسر الوظائف الحالية
**Assistant:** أفصل الواجهة عن الذكاء: React/Electron للواجهة، C# للـLauncher، وPython للـAgent والـAI، مع IPC واضح وآمن.
**ID:** `1fd506da674bac6156eacd03bba3ec8f523f12f81bd0ab4f6befc5f7a57a1952`

### Example 26 — AR
**User:** كيف دور C# Launcher؟
**Assistant:** أفصل الواجهة عن الذكاء: React/Electron للواجهة، C# للـLauncher، وPython للـAgent والـAI، مع IPC واضح وآمن.
**ID:** `254f60ac8c1d574ad0cb5cc20f6ee7f28dae363abd6913ad6c03b16aa0a64feb`

### Example 27 — AR
**User:** كيف دور Python Runtime؟
**Assistant:** أفصل الواجهة عن الذكاء: React/Electron للواجهة، C# للـLauncher، وPython للـAgent والـAI، مع IPC واضح وآمن.
**ID:** `2596ad93fc46f6d7c169e5dc0b3446defbe2f39cc6dfb5d4c633b78dda755819`

### Example 28 — AR
**User:** أريد تنفيذ دور Python Runtime داخل المشروع. على Windows
**Assistant:** أفصل الواجهة عن الذكاء: React/Electron للواجهة، C# للـLauncher، وPython للـAgent والـAI، مع IPC واضح وآمن.
**ID:** `38cbb035985cada0a033137371c4d993a6bad8a33d0c38c07f237baa88dad82f`

### Example 29 — AR
**User:** كيف فصل الطبقات؟
**Assistant:** أفصل الواجهة عن الذكاء: React/Electron للواجهة، C# للـLauncher، وPython للـAgent والـAI، مع IPC واضح وآمن.
**ID:** `403420b9bfb786bc74633ebcaa027317e03b458e5be24f38e1eefe10d2c70782`

### Example 30 — AR
**User:** أريد تنفيذ دور C# Launcher داخل المشروع. على Windows
**Assistant:** أفصل الواجهة عن الذكاء: React/Electron للواجهة، C# للـLauncher، وPython للـAgent والـAI، مع IPC واضح وآمن.
**ID:** `477d11a34e1d7df7e672187f1d7b948dcdd3d46eedd2927b9eedcc613b1e6c52`

### Example 31 — AR
**User:** أريد أن أعرف أفضل طريقة لـدور C# Launcher. داخل المشروع
**Assistant:** أفصل الواجهة عن الذكاء: React/Electron للواجهة، C# للـLauncher، وPython للـAgent والـAI، مع IPC واضح وآمن.
**ID:** `5f7fd317b4866ad2b2fb51dd02c1b063417cf9828f35b3f7e2953f73464a0301`

### Example 32 — AR
**User:** كيف أضيف قدرة دور C# Launcher إلى ALI؟ من خلال واجهة ALI
**Assistant:** أفصل الواجهة عن الذكاء: React/Electron للواجهة، C# للـLauncher، وPython للـAgent والـAI، مع IPC واضح وآمن.
**ID:** `6328256654b379aa863190e2b87e3ad44f6aed1a2c6e241ef3e1f8f221efd970`

### Example 33 — AR
**User:** ما الخطوات العملية لـفصل الطبقات؟ بطريقة آمنة
**Assistant:** أفصل الواجهة عن الذكاء: React/Electron للواجهة، C# للـLauncher، وPython للـAgent والـAI، مع IPC واضح وآمن.
**ID:** `6981793f87ebc0538326dcbf071fffec544aea0fcc9fab6104154a7d38d4ee3a`

### Example 34 — AR
**User:** قم بـدور Python Runtime. دون كسر الوظائف الحالية
**Assistant:** أفصل الواجهة عن الذكاء: React/Electron للواجهة، C# للـLauncher، وPython للـAgent والـAI، مع IPC واضح وآمن.
**ID:** `8292b7d57dd416909a81305a8e9eb80cd7dc6c442d2fedd18a777768dcadb347`

### Example 35 — AR
**User:** كيف أنفذ دور Python Runtime بشكل احترافي؟ مع حفظ rollback
**Assistant:** أفصل الواجهة عن الذكاء: React/Electron للواجهة، C# للـLauncher، وPython للـAgent والـAI، مع IPC واضح وآمن.
**ID:** `8e6016259f81d61ddc1f2eda0eb8fe80ad1a987e477a3ff68a2692e2a244d744`

### Example 36 — AR
**User:** كيف أنفذ فصل الطبقات بشكل احترافي؟ مع حفظ rollback
**Assistant:** أفصل الواجهة عن الذكاء: React/Electron للواجهة، C# للـLauncher، وPython للـAgent والـAI، مع IPC واضح وآمن.
**ID:** `909dd087bc121da332bfa1a298c115aed47c1a425ed1c3d7cdf67776248c047f`

### Example 37 — AR
**User:** ما الخطوات العملية لـدور C# Launcher؟ بطريقة آمنة
**Assistant:** أفصل الواجهة عن الذكاء: React/Electron للواجهة، C# للـLauncher، وPython للـAgent والـAI، مع IPC واضح وآمن.
**ID:** `92786122d1fdd9dd82c10784351fccd320a3c73cc5672f7762ef456ee0b3598c`

### Example 38 — AR
**User:** كيف أضيف قدرة دور Python Runtime إلى ALI؟ من خلال واجهة ALI
**Assistant:** أفصل الواجهة عن الذكاء: React/Electron للواجهة، C# للـLauncher، وPython للـAgent والـAI، مع IPC واضح وآمن.
**ID:** `9b481a48dfb771d8be7363af42211976842b9fe0724f6051d7a119a9aa967761`

### Example 39 — AR
**User:** كيف أنفذ دور C# Launcher بشكل احترافي؟ مع حفظ rollback
**Assistant:** أفصل الواجهة عن الذكاء: React/Electron للواجهة، C# للـLauncher، وPython للـAgent والـAI، مع IPC واضح وآمن.
**ID:** `9d672afdba36bfb5e27ad34890fe16abf3e2b47d10f0c4dbeb4f2ce5a0055a46`

### Example 40 — AR
**User:** كيف أضيف قدرة فصل الطبقات إلى ALI؟ من خلال واجهة ALI
**Assistant:** أفصل الواجهة عن الذكاء: React/Electron للواجهة، C# للـLauncher، وPython للـAgent والـAI، مع IPC واضح وآمن.
**ID:** `a47cafa5c47c70ad0e549fd8f35d7743c4c7ef99666958652f1fb6151f65858a`

### Example 41 — AR
**User:** اجعل ALI يستطيع دور Python Runtime. مع اختبار كامل
**Assistant:** أفصل الواجهة عن الذكاء: React/Electron للواجهة، C# للـLauncher، وPython للـAgent والـAI، مع IPC واضح وآمن.
**ID:** `abb91a2da2e17a5f07fada041195b54af210366ee942fdf62a70e0da8b8fe1f4`

### Example 42 — AR
**User:** قم بـفصل الطبقات. دون كسر الوظائف الحالية
**Assistant:** أفصل الواجهة عن الذكاء: React/Electron للواجهة، C# للـLauncher، وPython للـAgent والـAI، مع IPC واضح وآمن.
**ID:** `b3c5d74dde3302460c18a98540085dd741b635605d4933f864871291a2644a17`

### Example 43 — AR
**User:** اجعل ALI يستطيع فصل الطبقات. مع اختبار كامل
**Assistant:** أفصل الواجهة عن الذكاء: React/Electron للواجهة، C# للـLauncher، وPython للـAgent والـAI، مع IPC واضح وآمن.
**ID:** `cd73aa47bb6478fa8f346ba4579ffc466d0dff720a64c33a9e529b3e73bcc8ff`

### Example 44 — AR
**User:** أريد تنفيذ فصل الطبقات داخل المشروع. على Windows
**Assistant:** أفصل الواجهة عن الذكاء: React/Electron للواجهة، C# للـLauncher، وPython للـAgent والـAI، مع IPC واضح وآمن.
**ID:** `e737a97ef680f450394a9808cfd23e0c4a3ce3420c18ed26184eb05547612dee`

### Example 45 — AR
**User:** أريد أن أعرف أفضل طريقة لـفصل الطبقات. داخل المشروع
**Assistant:** أفصل الواجهة عن الذكاء: React/Electron للواجهة، C# للـLauncher، وPython للـAgent والـAI، مع IPC واضح وآمن.
**ID:** `faf250b11287354740558aa6b7b9cb6ef088276e29a740fc52b4ae59f51be3f2`

## النوع: coding

### Example 46 — AR
**User:** كيف أضيف قدرة كتابة كود قابل للصيانة إلى ALI؟ من خلال واجهة ALI
**Assistant:** أكتب كوداً منظماً مع معالجة أخطاء واختبارات، ثم أشغّل الفحوص والبناء وأصلح أي مشكلة قبل التسليم.
**ID:** `036076e2f0b5c28e51097f041c721927c3ff40bdf27485d9f862c53795c32e96`

### Example 47 — AR
**User:** كيف أنفذ كتابة كود قابل للصيانة بشكل احترافي؟ مع حفظ rollback
**Assistant:** أكتب كوداً منظماً مع معالجة أخطاء واختبارات، ثم أشغّل الفحوص والبناء وأصلح أي مشكلة قبل التسليم.
**ID:** `2cc766953664887ffc0cb112e3bd579e776f74df97c8539f1b3847bfe6aa68ea`

### Example 48 — AR
**User:** اجعل ALI يستطيع كتابة كود قابل للصيانة. مع اختبار كامل
**Assistant:** أكتب كوداً منظماً مع معالجة أخطاء واختبارات، ثم أشغّل الفحوص والبناء وأصلح أي مشكلة قبل التسليم.
**ID:** `3092ee83c3500ec00d98a2c5319999acb037cdd63fa37af924d3a06b294e9b8e`

### Example 49 — AR
**User:** أريد تنفيذ كتابة كود قابل للصيانة داخل المشروع. على Windows
**Assistant:** أكتب كوداً منظماً مع معالجة أخطاء واختبارات، ثم أشغّل الفحوص والبناء وأصلح أي مشكلة قبل التسليم.
**ID:** `31eaadfd2c0d2396c29f7ff62269f7eac192acb2fb7b836f08c0871552b4809d`

### Example 50 — AR
**User:** قم بـكتابة كود قابل للصيانة. دون كسر الوظائف الحالية
**Assistant:** أكتب كوداً منظماً مع معالجة أخطاء واختبارات، ثم أشغّل الفحوص والبناء وأصلح أي مشكلة قبل التسليم.
**ID:** `413b3498cd0b68c27deb1d215562975d509a98336cd0108aa0569a82b5c69080`

### Example 51 — AR
**User:** أريد أن أعرف أفضل طريقة لـكتابة كود قابل للصيانة. داخل المشروع
**Assistant:** أكتب كوداً منظماً مع معالجة أخطاء واختبارات، ثم أشغّل الفحوص والبناء وأصلح أي مشكلة قبل التسليم.
**ID:** `959fb20596fc5e96af2ae731f105a6c9032f95cdd0d35b949c382430e186f038`

### Example 52 — AR
**User:** ما الخطوات العملية لـكتابة كود قابل للصيانة؟ بطريقة آمنة
**Assistant:** أكتب كوداً منظماً مع معالجة أخطاء واختبارات، ثم أشغّل الفحوص والبناء وأصلح أي مشكلة قبل التسليم.
**ID:** `be9d07d6b0b4baf6d85325c2e46035790d6c4d0b67b5488a121bbf9871a55076`

### Example 53 — AR
**User:** كيف كتابة كود قابل للصيانة؟
**Assistant:** أكتب كوداً منظماً مع معالجة أخطاء واختبارات، ثم أشغّل الفحوص والبناء وأصلح أي مشكلة قبل التسليم.
**ID:** `e8943ccd25d840a8a07ea64242a1c92a51441a351ef5569486a069dd54029f58`

## النوع: continuous

### Example 54 — AR
**User:** ما الخطوات العملية لـفشل v2؟ بطريقة آمنة
**Assistant:** تُبنى النسخة الجديدة فوق Active، وتستخدم البيانات الجديدة فقط. بعد التدريب تُجرى Evaluation وRegression ثم Promotion أو Rollback.
**ID:** `03a8bc5b2c92aa37b20bc067926ff47f2302d5b7435e85344426fd91316370c6`

### Example 55 — EN
**User:** How do I build v2 from v1 for this project?
**Assistant:** I train the new update on top of the active v1 model, evaluate it, and promote it only when the gates pass
**ID:** `083fdbe98f904bb079819c24f8ba17c22251ff8b722d04e083f30ed80a1dbbe3`

### Example 56 — AR
**User:** اجعل ALI يستطيع منع إعادة تدريب البيانات. مع اختبار كامل
**Assistant:** تُبنى النسخة الجديدة فوق Active، وتستخدم البيانات الجديدة فقط. بعد التدريب تُجرى Evaluation وRegression ثم Promotion أو Rollback.
**ID:** `12ff8d6d663f95c477b0d56786847fdba3654470babbe9c99ffc48681e9242d9`

### Example 57 — AR
**User:** كيف أنفذ الاحتفاظ بتاريخ النماذج بشكل احترافي؟ مع حفظ rollback
**Assistant:** تُبنى النسخة الجديدة فوق Active، وتستخدم البيانات الجديدة فقط. بعد التدريب تُجرى Evaluation وRegression ثم Promotion أو Rollback.
**ID:** `13925d29987b6399cc691b8e3f7875fbb0fa802a1df4c619b5a8022977f65266`

### Example 58 — AR
**User:** ما الخطوات العملية لـالاحتفاظ بتاريخ النماذج؟ بطريقة آمنة
**Assistant:** تُبنى النسخة الجديدة فوق Active، وتستخدم البيانات الجديدة فقط. بعد التدريب تُجرى Evaluation وRegression ثم Promotion أو Rollback.
**ID:** `18d8011aa5de3efb083af4ba2bc77ed436a2971f62b8f410161260950834dbfc`

### Example 59 — AR
**User:** أريد أن أعرف أفضل طريقة لـفشل v2. داخل المشروع
**Assistant:** تُبنى النسخة الجديدة فوق Active، وتستخدم البيانات الجديدة فقط. بعد التدريب تُجرى Evaluation وRegression ثم Promotion أو Rollback.
**ID:** `1ce280619c8922d070f41764afd7213e4126dce487973904da3ea8c877480b73`

### Example 60 — AR
**User:** كيف الاحتفاظ بتاريخ النماذج؟
**Assistant:** تُبنى النسخة الجديدة فوق Active، وتستخدم البيانات الجديدة فقط. بعد التدريب تُجرى Evaluation وRegression ثم Promotion أو Rollback.
**ID:** `20c024aaf3d21417f5ffbbeb8b664f22af1ed66993bbc5df9dfc4067e41af352`

### Example 61 — AR
**User:** أريد تنفيذ التعلم التراكمي v1 وv2 داخل المشروع. على Windows
**Assistant:** تُبنى النسخة الجديدة فوق Active، وتستخدم البيانات الجديدة فقط. بعد التدريب تُجرى Evaluation وRegression ثم Promotion أو Rollback.
**ID:** `2e6e20c7f181ec611c62133984bf8cce4b4196fc0ca97e53774f018ca1d3a376`

### Example 62 — AR
**User:** كيف منع إعادة تدريب البيانات؟
**Assistant:** تُبنى النسخة الجديدة فوق Active، وتستخدم البيانات الجديدة فقط. بعد التدريب تُجرى Evaluation وRegression ثم Promotion أو Rollback.
**ID:** `3558d4fa3e4441d58b3009715592f26202a3140d912b02c1c7917df66c72b12b`

### Example 63 — AR
**User:** كيف أضيف قدرة منع إعادة تدريب البيانات إلى ALI؟ من خلال واجهة ALI
**Assistant:** تُبنى النسخة الجديدة فوق Active، وتستخدم البيانات الجديدة فقط. بعد التدريب تُجرى Evaluation وRegression ثم Promotion أو Rollback.
**ID:** `3cc962ae2a1073f25a201092d6eb2723cbfbb783ab4c000c369e5c5c1aded248`

### Example 64 — AR
**User:** قم بـفشل v2. دون كسر الوظائف الحالية
**Assistant:** تُبنى النسخة الجديدة فوق Active، وتستخدم البيانات الجديدة فقط. بعد التدريب تُجرى Evaluation وRegression ثم Promotion أو Rollback.
**ID:** `445490fd2145621eed7bc74c9ec650ea1adb064212fe0ba17649ed48dddb417f`

### Example 65 — AR
**User:** كيف أنفذ منع إعادة تدريب البيانات بشكل احترافي؟ مع حفظ rollback
**Assistant:** تُبنى النسخة الجديدة فوق Active، وتستخدم البيانات الجديدة فقط. بعد التدريب تُجرى Evaluation وRegression ثم Promotion أو Rollback.
**ID:** `497b3145e91d9b34307e4d66275ebbd02e2abdf3e1256d1b93ef24adcdee760e`

### Example 66 — AR
**User:** أريد تنفيذ منع إعادة تدريب البيانات داخل المشروع. على Windows
**Assistant:** تُبنى النسخة الجديدة فوق Active، وتستخدم البيانات الجديدة فقط. بعد التدريب تُجرى Evaluation وRegression ثم Promotion أو Rollback.
**ID:** `4c51b91080471fc5354ee7ae4efa88d4391c0db188e28a8704abf59432ce2eec`

### Example 67 — AR
**User:** ما الخطوات العملية لـمنع إعادة تدريب البيانات؟ بطريقة آمنة
**Assistant:** تُبنى النسخة الجديدة فوق Active، وتستخدم البيانات الجديدة فقط. بعد التدريب تُجرى Evaluation وRegression ثم Promotion أو Rollback.
**ID:** `4d498edfa08b864cf9d1ad6094faf8b5469eed795a4e01b8a42060db3f594bbe`

### Example 68 — AR
**User:** قم بـالتعلم التراكمي v1 وv2. دون كسر الوظائف الحالية
**Assistant:** تُبنى النسخة الجديدة فوق Active، وتستخدم البيانات الجديدة فقط. بعد التدريب تُجرى Evaluation وRegression ثم Promotion أو Rollback.
**ID:** `4ea8f1244c3f6517cb91dc2d5b1b73bd85ed0f9461125d65f596d4fee94d407d`

### Example 69 — EN
**User:** How do I build v2 from v1 using the local runtime?
**Assistant:** I train the new update on top of the active v1 model, evaluate it, and promote it only when the gates pass
**ID:** `54e0eb1bf1cb48a653c1930a87201e703bcafb38c52558bb219d5d774de0bfe3`

### Example 70 — AR
**User:** كيف أضيف قدرة التعلم التراكمي v1 وv2 إلى ALI؟ من خلال واجهة ALI
**Assistant:** تُبنى النسخة الجديدة فوق Active، وتستخدم البيانات الجديدة فقط. بعد التدريب تُجرى Evaluation وRegression ثم Promotion أو Rollback.
**ID:** `563cf60e124e6d5ade2ca04af4b3bdaa9ebb80ee737a92dda962e578ee187cee`

### Example 71 — AR
**User:** كيف أضيف قدرة الاحتفاظ بتاريخ النماذج إلى ALI؟ من خلال واجهة ALI
**Assistant:** تُبنى النسخة الجديدة فوق Active، وتستخدم البيانات الجديدة فقط. بعد التدريب تُجرى Evaluation وRegression ثم Promotion أو Rollback.
**ID:** `588f874bb848b98b9c576e0ddc20fbf7af182cfe1dd2abba6de323a6c4368ff6`

### Example 72 — EN
**User:** How do I build v2 from v1 safely?
**Assistant:** I train the new update on top of the active v1 model, evaluate it, and promote it only when the gates pass
**ID:** `5beed8e5c218d429422e8645e2cbbfb5580de1c2078b31e1d99625f9ef7659ce`

### Example 73 — AR
**User:** اجعل ALI يستطيع فشل v2. مع اختبار كامل
**Assistant:** تُبنى النسخة الجديدة فوق Active، وتستخدم البيانات الجديدة فقط. بعد التدريب تُجرى Evaluation وRegression ثم Promotion أو Rollback.
**ID:** `5fdbff866d573933ae6a99d43ea4256b50ff159bf584c820e7f076275844e81a`

### Example 74 — AR
**User:** أريد أن أعرف أفضل طريقة لـالاحتفاظ بتاريخ النماذج. داخل المشروع
**Assistant:** تُبنى النسخة الجديدة فوق Active، وتستخدم البيانات الجديدة فقط. بعد التدريب تُجرى Evaluation وRegression ثم Promotion أو Rollback.
**ID:** `6f362b0684ab02d0dedcf158a65ccea4d2049249f1c4d174fc022f93c83d290d`

### Example 75 — AR
**User:** ما الخطوات العملية لـالتعلم التراكمي v1 وv2؟ بطريقة آمنة
**Assistant:** تُبنى النسخة الجديدة فوق Active، وتستخدم البيانات الجديدة فقط. بعد التدريب تُجرى Evaluation وRegression ثم Promotion أو Rollback.
**ID:** `710829fc2c0b8eff5475bc9c513c5a78378c14e0af82f38ce72d893b7e7f34d0`

### Example 76 — AR
**User:** أريد أن أعرف أفضل طريقة لـمنع إعادة تدريب البيانات. داخل المشروع
**Assistant:** تُبنى النسخة الجديدة فوق Active، وتستخدم البيانات الجديدة فقط. بعد التدريب تُجرى Evaluation وRegression ثم Promotion أو Rollback.
**ID:** `7109b4036f3dc6c3bd2f0d4e62f462d03bf01abb7eb84af4edc7ddbf113acc19`

### Example 77 — AR
**User:** قم بـالاحتفاظ بتاريخ النماذج. دون كسر الوظائف الحالية
**Assistant:** تُبنى النسخة الجديدة فوق Active، وتستخدم البيانات الجديدة فقط. بعد التدريب تُجرى Evaluation وRegression ثم Promotion أو Rollback.
**ID:** `99a1864da70c0b741f34e15ac132f4be86d578d7af36c8aad4f612a8c5c8f506`

### Example 78 — EN
**User:** How do I build v2 from v1 with verification?
**Assistant:** I train the new update on top of the active v1 model, evaluate it, and promote it only when the gates pass
**ID:** `a3ad7bb37ceba47a8f39d55b5982fa9606443a4394675ebdb8e6d81dcc98390d`

### Example 79 — AR
**User:** أريد تنفيذ الاحتفاظ بتاريخ النماذج داخل المشروع. على Windows
**Assistant:** تُبنى النسخة الجديدة فوق Active، وتستخدم البيانات الجديدة فقط. بعد التدريب تُجرى Evaluation وRegression ثم Promotion أو Rollback.
**ID:** `bc9119d11a7864fb93589f320354e533e00736fa81e0a8c51cfd671871148743`

### Example 80 — AR
**User:** اجعل ALI يستطيع الاحتفاظ بتاريخ النماذج. مع اختبار كامل
**Assistant:** تُبنى النسخة الجديدة فوق Active، وتستخدم البيانات الجديدة فقط. بعد التدريب تُجرى Evaluation وRegression ثم Promotion أو Rollback.
**ID:** `c121f26cfd3effe98288c685e65ae0e3c9f48f46762068ef62298f615093e710`

### Example 81 — AR
**User:** اجعل ALI يستطيع التعلم التراكمي v1 وv2. مع اختبار كامل
**Assistant:** تُبنى النسخة الجديدة فوق Active، وتستخدم البيانات الجديدة فقط. بعد التدريب تُجرى Evaluation وRegression ثم Promotion أو Rollback.
**ID:** `c18dae9d52bd28e1bf4d5e0feb2ec919a94403fe1476402e7de4d03e492ecec9`

### Example 82 — AR
**User:** أريد تنفيذ فشل v2 داخل المشروع. على Windows
**Assistant:** تُبنى النسخة الجديدة فوق Active، وتستخدم البيانات الجديدة فقط. بعد التدريب تُجرى Evaluation وRegression ثم Promotion أو Rollback.
**ID:** `c32002e1bb6535bd99b3a19a78d96fb9494efe99f8e1cd86758b172273d48abf`

### Example 83 — AR
**User:** كيف أنفذ التعلم التراكمي v1 وv2 بشكل احترافي؟ مع حفظ rollback
**Assistant:** تُبنى النسخة الجديدة فوق Active، وتستخدم البيانات الجديدة فقط. بعد التدريب تُجرى Evaluation وRegression ثم Promotion أو Rollback.
**ID:** `cdb5ed916e99fb3f49618dc4fab9965fce1be259ff4cc84864cb36f4f48d7ac3`

### Example 84 — AR
**User:** أريد أن أعرف أفضل طريقة لـالتعلم التراكمي v1 وv2. داخل المشروع
**Assistant:** تُبنى النسخة الجديدة فوق Active، وتستخدم البيانات الجديدة فقط. بعد التدريب تُجرى Evaluation وRegression ثم Promotion أو Rollback.
**ID:** `cfb34790d84b9a5f36abf8b9d0217276efd4afdd457002fd773f5a04a3c0a3ec`

### Example 85 — AR
**User:** كيف التعلم التراكمي v1 وv2؟
**Assistant:** تُبنى النسخة الجديدة فوق Active، وتستخدم البيانات الجديدة فقط. بعد التدريب تُجرى Evaluation وRegression ثم Promotion أو Rollback.
**ID:** `d791448efa6e632005228b6f5a875c4c4ed4ac4b7f99e37539592772fd7bf8f3`

### Example 86 — AR
**User:** كيف أضيف قدرة فشل v2 إلى ALI؟ من خلال واجهة ALI
**Assistant:** تُبنى النسخة الجديدة فوق Active، وتستخدم البيانات الجديدة فقط. بعد التدريب تُجرى Evaluation وRegression ثم Promotion أو Rollback.
**ID:** `da7128f060e874ba6877ad5d3acec02f0d557cb522ad04a17eef1e9caa09b7e9`

### Example 87 — AR
**User:** قم بـمنع إعادة تدريب البيانات. دون كسر الوظائف الحالية
**Assistant:** تُبنى النسخة الجديدة فوق Active، وتستخدم البيانات الجديدة فقط. بعد التدريب تُجرى Evaluation وRegression ثم Promotion أو Rollback.
**ID:** `eb121023061ac05255705fc51d9e188627aa7177411e2f4461081355142373bd`

### Example 88 — AR
**User:** كيف أنفذ فشل v2 بشكل احترافي؟ مع حفظ rollback
**Assistant:** تُبنى النسخة الجديدة فوق Active، وتستخدم البيانات الجديدة فقط. بعد التدريب تُجرى Evaluation وRegression ثم Promotion أو Rollback.
**ID:** `f5da985606bb45dac4f66e68182b0c62676b4fcdbd70c7194e81bd8feaecc27f`

### Example 89 — EN
**User:** How do I build v2 from v1?
**Assistant:** I train the new update on top of the active v1 model, evaluate it, and promote it only when the gates pass
**ID:** `fa45697530087c3428a82d2dfd95aca06faca77d5a47e84ed387675529d53c5a`

### Example 90 — AR
**User:** كيف فشل v2؟
**Assistant:** تُبنى النسخة الجديدة فوق Active، وتستخدم البيانات الجديدة فقط. بعد التدريب تُجرى Evaluation وRegression ثم Promotion أو Rollback.
**ID:** `fc5b66e1258c545f627d48b93cb79f16d7b420ad4f13b40b47daf05a3ae57748`

## النوع: data_quality

### Example 91 — AR
**User:** ما الخطوات العملية لـتنظيف dataset؟ بطريقة آمنة
**Assistant:** أتحقق من البنية والمحتوى، أزيل التكرار والأمثلة التالفة والأسرار، وأبقي train وvalidation وtest منفصلة.
**ID:** `182ccb3295d571b511a9cbfb88fc351bae3e53a0d4baf5d2cb5238db92f46b35`

### Example 92 — AR
**User:** قم بـفصل train/validation/test. دون كسر الوظائف الحالية
**Assistant:** أتحقق من البنية والمحتوى، أزيل التكرار والأمثلة التالفة والأسرار، وأبقي train وvalidation وtest منفصلة.
**ID:** `19d6574a574fbf7b4d45b62a355233e0806dfa5dfe35e79d22b5b11c02f4c0b4`

### Example 93 — AR
**User:** أريد تنفيذ فصل train/validation/test داخل المشروع. على Windows
**Assistant:** أتحقق من البنية والمحتوى، أزيل التكرار والأمثلة التالفة والأسرار، وأبقي train وvalidation وtest منفصلة.
**ID:** `3bd190d35344767377ee76111a0234df2270c14d0ae0a8114f610e5a7025ffa9`

### Example 94 — AR
**User:** كيف أنفذ فصل train/validation/test بشكل احترافي؟ مع حفظ rollback
**Assistant:** أتحقق من البنية والمحتوى، أزيل التكرار والأمثلة التالفة والأسرار، وأبقي train وvalidation وtest منفصلة.
**ID:** `3cd1721fbd505c6f84561b03c291986e3c35d22ff88f5e0e278bfcb6f7919a2c`

### Example 95 — AR
**User:** كيف أنفذ تنظيف dataset بشكل احترافي؟ مع حفظ rollback
**Assistant:** أتحقق من البنية والمحتوى، أزيل التكرار والأمثلة التالفة والأسرار، وأبقي train وvalidation وtest منفصلة.
**ID:** `41d966dea19ed4ab17f690c573ca9afb1a40c80e5f01917ded6a7fad280ce8fd`

### Example 96 — AR
**User:** اجعل ALI يستطيع تنظيف dataset. مع اختبار كامل
**Assistant:** أتحقق من البنية والمحتوى، أزيل التكرار والأمثلة التالفة والأسرار، وأبقي train وvalidation وtest منفصلة.
**ID:** `52ec4dc9ee233d09fc8b685dc91bea298928c1323a6338749b8504462a21b4f3`

### Example 97 — AR
**User:** اجعل ALI يستطيع فصل train/validation/test. مع اختبار كامل
**Assistant:** أتحقق من البنية والمحتوى، أزيل التكرار والأمثلة التالفة والأسرار، وأبقي train وvalidation وtest منفصلة.
**ID:** `66cf1c05c244e6aa7e1b16294c51e1176856d1d7285394c53786cbd93841492f`
