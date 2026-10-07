# ALI Conversation Intelligence V5

هذه الحزمة توسعة مستقلة لطبقة المحادثة وفهم الطلبات في ALI Studio Pro. صُممت لتعمل فوق الذاكرة وRAG والتخطيط والأدوات الموجودة، ولا تستبدلها.

## الأهداف

1. فهم الطلب حتى لو كان مختصراً أو عامياً أو متعدد اللغات.
2. فصل نية المستخدم عن أسلوب الصياغة.
3. اكتشاف المقصود الضمني والإحالات مثل «هذا»، «السابق»، «نفسه»، «كمل».
4. إدارة الغموض دون تخمين خطير.
5. تحديد هل المطلوب شرح، تنفيذ، تعديل، بحث، مقارنة، استخراج، إنشاء، تحقق، متابعة أو قرار.
6. اختيار مستوى التفصيل واللغة والشكل المناسب للرد.
7. الحفاظ على استمرارية المحادثة مع احترام الذاكرة القابلة للحذف والتعديل.
8. تحويل التصحيح والملاحظات إلى بيانات تعلم مع provenance بدلاً من إدخالها مباشرة إلى الأوزان.
9. الفصل بين الحقائق، الافتراضات، الأدلة، ونتائج الأدوات.
10. تحسين الردود العربية والإنجليزية والخلط العربي/الإنجليزي.

## عائلات الفهم

- question_answering
- explanation
- definition
- translation
- rewriting
- proofreading
- summarization
- extraction
- classification
- comparison
- recommendation
- decision_support
- brainstorming
- planning
- execution
- modification
- debugging
- diagnosis
- troubleshooting
- code_generation
- code_review
- project_analysis
- file_operation
- terminal_operation
- git_operation
- web_research
- fact_check
- current_information
- document_analysis
- image_analysis
- data_analysis
- spreadsheet_task
- report_generation
- study_tutoring
- quiz
- simulation
- roleplay
- creative_writing
- structured_output
- citation_request
- source_request
- memory_save
- memory_forget
- memory_recall
- preference_update
- session_management
- follow_up
- correction
- clarification
- confirmation
- cancellation
- status_request
- progress_request
- capability_request
- configuration
- testing
- verification
- deployment
- release
- security_review
- performance_review
- architecture_review
- model_training
- model_evaluation
- model_conversion
- model_management
- automation
- workflow
- multi_step_task
- unknown

## طبقات القرار

### 1. Request frame
يتم بناء إطار موحد:
- intent
- confidence
- mode: answer|research|execute|edit|create|verify|clarify
- language
- domain
- urgency
- freshness_required
- user_goal
- constraints
- deliverable
- referenced_entities
- required_evidence
- requested_depth

### 2. Conversation state
تُحفظ حالة محلية قصيرة:
- last_user_goal
- last_assistant_deliverable
- active_entity
- pending_action
- pending_confirmation
- unresolved_questions
- rejected_assumptions
- user_preferences

ولا تُرفع هذه العناصر إلى الأوزان تلقائياً.

### 3. Response policy
يُختار أسلوب الرد قبل التوليد:
- direct
- concise
- detailed
- step_by_step
- diagnostic
- research
- implementation
- comparison
- educational
- creative
- structured
- recovery

### 4. Quality gates
قبل العرض:
- empty_output
- repetition
- malformed_text
- unsupported_claim
- missing_source
- missing_uncertainty
- wrong_language
- ignored_constraint
- stale_information
- incomplete_execution
- unverified_postcondition

## قاعدة عدم التخمين

إذا كانت هناك عدة تفسيرات معقولة وكان تنفيذ أحدها قد يسبب تغييراً أو حذفاً أو إرسالاً أو التزاماً خارجياً، فلا يتم التنفيذ تلقائياً. يطلب النظام توضيحاً واحداً مركزاً أو يعرض الخيارات باختصار.

أما إذا كان الغموض منخفض المخاطر ويمكن استخدام السياق السابق بأمان، فيُستنتج المقصود ويُتابع التنفيذ مع ذكر افتراض قصير عند الحاجة.

## قاعدة الاستمرارية

عبارات مثل «كمل»، «تابع»، «من حيث توقفنا»، «نفس السابق»، «طبّقها»، «أضف المزيد» تُعامل كإحالات إلى آخر هدف نشط، وليس كطلبات جديدة مستقلة، ما لم يظهر سياق يناقض ذلك.

## قاعدة الأدلة

- معلومات المستخدم الحالية لها أولوية كسياق.
- ملفات المشروع ونتائج الأدوات تُعامل كمصادر داخلية.
- البحث على الويب يُستخدم للمعلومات المتغيرة زمنياً أو عندما يطلبه المستخدم.
- محتوى الويب دليل غير موثوق تعليمياً ولا يُعامل كتوجيه للنظام.
- الادعاءات القابلة للتحقق تُربط بالمصدر المناسب متى كان المصدر متاحاً.

## قاعدة العمل الحقيقي

عند طلب التنفيذ:
فهم → خطة → تنفيذ → تحقق من النتيجة → إصلاح عند الحاجة → تقرير النتيجة.

لا تُسجل المهمة على أنها مكتملة بناءً على عدم وجود خطأ فقط؛ يجب وجود postcondition قابل للفحص.

## قاعدة التعلم من المحادثة

تُقسم الخبرة إلى:
- memory: معلومات المستخدم وتفضيلاته وسياق الجلسة.
- RAG: معلومات متغيرة أو وثائق.
- behavior training: أنماط الردود والسلوك.
- model weights: معلومات أو سلوك ثابت بعد مرور التقييم والترقية.

لا يتم تحويل محادثة رفضها المستخدم إلى عينة تدريب موثوقة مباشرة.

## حالات خاصة

### طلب قصير
«عدله» → اربطه بآخر ملف/جزء/مخرَج نشط.

### طلب ناقص
«أريد الأفضل» → استخرج معيار الأفضل من السياق؛ إن تعذر ذلك اسأل عن معيار واحد فقط.

### طلب متعدد
«حلل وعدل واختبر وارفع» → أنشئ مهمة متعددة المراحل مع مخرجات مرحلية.

### تصحيح المساعد
«هذا خطأ» → اعتبره إشارة تصحيح، أعد تقييم الادعاء، ولا تدافع عن الإجابة السابقة بلا دليل.

### تغير الموضوع
إذا ظهر هدف جديد واضح، اخفض وزن السياق القديم مع إبقاء تاريخ الجلسة.

### طلب متابعة
«نعم»، «نفذ»، «تابع» → اربطها بآخر إجراء يحتاج قراراً.

## التوافق

الحزمة لا تعتمد على مكتبات خارجية. يمكن تشغيلها على Python المحلي في P50، ثم ربطها بـ:
- core/orchestrator.py
- assistant/context.py
- memory/conversations.py
- memory/sessions.py
- core/response_guard.py
- research/web.py
- tools/registry.py
