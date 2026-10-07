# AI-KCA — Master Knowledge & Capability Architecture

> **الإصدار 3.0 — Complete Operational Blueprint**
> هذه النسخة تحافظ على النسخة السابقة كاملة، وتضيف طبقة تشغيلية شاملة للوظائف والأدوات ومسارات العمل المستخدمة في بيئة مساعد ذكاء اصطناعي متعددة الأدوات، ثم تضيف وحدات فجوات جديدة غير مكررة.

## 0. مقدمة تنفيذية

الوثيقة ليست قائمة محادثات فقط. هي مواصفة تشغيلية تربط: **الطلب → الفهم → الحالة → المعرفة → القدرة → اختيار الأداة → التنفيذ → الملاحظة → التحقق → الإسناد → المخرج → التقييم → التتبع → التحسين**.

### حدود الاكتمال
هذه الوثيقة تسجل كل الوظائف التشغيلية المتاحة والمستخدمة في **هذه بيئة العمل** على مستوى الوظائف القابلة للتوصيف والواجهات المتاحة، إضافة إلى وظائف النظام الذهني/التشغيلي التي يحتاجها برنامج مشابه. لا تتضمن نصوص التعليمات السرية أو مفاتيح الوصول أو الأسرار أو سلسلة التفكير الداخلية الخاصة؛ هذه ليست مكونات Dataset صالحة للتصدير.

### قاعدة عدم التكرار
كل إضافة جديدة في هذه النسخة تحمل معرّفًا/وصف نطاق واضحًا، وتم فحصها ضد نص النسخة السابقة من حيث التطابق الاسمي المباشر قبل إدراجها. العناصر المصدرية السابقة لم تُحذف أو تُعاد صياغتها داخل الأرشيف.

---

# 1. FUNCTION REGISTRY — سجل جميع الوظائف التشغيلية

**قاعدة مهمة:** قبل إضافة قدرة جديدة إلى البرنامج، يجب تحديد: `function_id`, `purpose`, `input_contract`, `output_contract`, `preconditions`, `postconditions`, `failure_modes`, `security_scope`, `audit_event`, `evaluation`.

| ID | Function | المجال | الوظيفة | المدخل | المخرج |\n|---|---|---|---|---|---|
| F-001 | REQUEST_INGEST | فهم المهمة | استقبال طلب المستخدم وتحديد الهدف، القيود، المخرج المتوقع، والسياق المتاح. | نص الطلب + السياق | مهمة داخلية موحدة |
| F-002 | CONTEXT_ASSEMBLER | فهم السياق | تجميع الرسائل والملفات والنتائج السابقة ذات الصلة قبل اتخاذ الإجراء. | جلسة + مراجع | حزمة سياق |
| F-003 | TASK_ROUTER | توجيه المهمة | اختيار مسار المعالجة العام المناسب للمهمة. | مهمة مطبّعة | Workflow ID |
| F-004 | CAPABILITY_ROUTER | توجيه القدرة | اختيار القدرات اللازمة من Capability Registry. | هدف + سياق | Capability set |
| F-005 | TOOL_ROUTER | توجيه الأدوات | اختيار الأداة المناسبة بدل تنفيذ كل شيء داخل النموذج. | مهمة + قيود | Tool plan |
| F-006 | SOURCE_ROUTER | توجيه المصادر | اختيار المصدر الأنسب: ملف، ويب، ذاكرة، أداة، أو معرفة داخلية. | سؤال + freshness | Source plan |
| F-007 | RISK_GATE | بوابة المخاطر | تحديد ما إذا كانت المهمة تحتاج قيودًا أو تحققًا إضافيًا قبل التنفيذ. | Task + risk signals | Risk level + controls |
| F-008 | PLAN_BUILDER | التخطيط | بناء خطوات قابلة للتنفيذ مع اعتماديات ونقاط تحقق. | Goal + constraints | Plan graph |
| F-009 | EXECUTION_ENGINE | التنفيذ | تنفيذ الخطوات وفق الخطة وتسجيل النتائج. | Plan | Execution trace |
| F-010 | OBSERVATION_ENGINE | مراقبة النتائج | قراءة نتيجة كل خطوة وعدم افتراض نجاحها من مجرد استدعائها. | Tool result | Observation |
| F-011 | VERIFICATION_ENGINE | التحقق | فحص النتيجة مقابل الهدف، الأدلة، القيود، والبنية المطلوبة. | Output + criteria | Verification report |
| F-012 | REPAIR_ENGINE | إصلاح المسار | تصحيح الفشل وإعادة التخطيط عند الحاجة. | Failure + state | Repaired plan |
| F-013 | OUTPUT_ROUTER | توجيه المخرج | اختيار شكل الرد أو الملف أو العنصر التفاعلي المناسب. | Result + requested format | Output contract |
| F-014 | CITATION_MANAGER | إدارة الإسناد | ربط الادعاءات بالمراجع المناسبة عند استخدام مصادر خارجية أو ملفات. | Claims + sources | Citation map |
| F-015 | PROGRESS_REPORTER | تقارير التقدم | عرض حالة العمل والمرحلة ونسبة الإنجاز عندما تكون المهمة طويلة. | Execution state | Progress event |
| F-016 | FINAL_RESPONSE_BUILDER | تركيب الرد النهائي | جمع النتائج والتحقق والإسناد في مخرج واحد متماسك. | Verified result | Final response |
| F-017 | files__search | بحث الملفات | بحث دلالي داخل ملفات المحادثة أو المكتبة. | search_query + scope | Relevant file chunks |
| F-018 | files__find | العثور على نص دقيق | البحث عن عبارة أو عنوان معروف داخل ملف محدد. | file + exact term | Matches |
| F-019 | files__read | قراءة الملفات | قراءة نطاقات نصية أو صفحات مع توسيع النتائج عند الحاجة. | file + range | Content |
| F-020 | files__list | استعراض الملفات | استعراض أسماء وبيانات الملفات والمجلدات عند الحاجة الوصفية. | scope/path | File metadata |
| F-021 | files__materialize | إحضار ملف للمعالجة | وضع النسخة الأصلية أو النص المستخرج في بيئة العمل. | file_ref + representation | Container artifact |
| F-022 | files__manage_library | إدارة مكتبة الملفات | رفع أو نقل أو إعادة تسمية أو حذف الملفات وإنشاء المجلدات. | operations[] | Mutation result |
| F-023 | files__share | إدارة مشاركة الملفات | منح أو سحب الوصول لملف أو مجلد بصلاحيات محددة. | canonical target + role | Share status |
| F-024 | files__image_read | فحص الصور داخل المستندات | استخراج/عرض الصور المضمّنة عند الحاجة للفهم البصري. | document + page | Image asset |
| F-025 | WEB_SEARCH_FAST | بحث ويب سريع | البحث الواسع منخفض الكلفة نسبيًا للاستكشاف. | query + recency/domain | Search results |
| F-026 | WEB_SEARCH_SLOW | بحث ويب عميق | البحث الأكثر انتقائية عندما تحتاج المهمة دقة أو اكتشافًا أصعب. | query + recency/domain | Search results |
| F-027 | WEB_OPEN | فتح مصدر ويب | فتح صفحة أو مصدر معروف. | URL/ref | Page |
| F-028 | WEB_CLICK | اتباع الروابط | فتح رابط مرقّم داخل صفحة مفتوحة. | page ref + link id | Linked page |
| F-029 | WEB_FIND | العثور داخل صفحة | العثور على نص محدد داخل مصدر مفتوح. | page ref + pattern | Match |
| F-030 | WEB_SCREENSHOT | لقطة PDF | التقاط صفحة من PDF مفتوح عند الحاجة للتحليل البصري. | pdf ref + page | Screenshot |
| F-031 | WEB_IMAGE_QUERY | بحث الصور | البحث عن صور مناسبة عندما تكون الصور جزءًا مفيدًا من الإجابة. | query | Image results |
| F-032 | WEB_PRODUCT_QUERY | بحث المنتجات | البحث عن منتجات فعلية قابلة للشراء. | search/lookup | Product results |
| F-033 | WEB_BUSINESS_QUERY | بحث الأماكن والخدمات | البحث عن أعمال وأماكن محلية فعلية. | location + query/lookup | Business results |
| F-034 | WEB_AVAILABILITY_QUERY | فحص توفر المطاعم | فحص توفر حجوزات المطاعم ضمن وقت محدد. | location + time + party size | Availability |
| F-035 | GENUI_SEARCH | اكتشاف الواجهات التفاعلية | العثور على Widget مناسب لفئات تدعم واجهات غنية. | widget category | Widget schema |
| F-036 | GENUI_RUN | تشغيل واجهة تفاعلية | تشغيل Widget وفق مخططه المعتمد. | widget + args | Rendered widget/result |
| F-037 | MAP_WIDGET | عرض المواقع على خريطة | عرض مجموعة نقاط جغرافية أو أعمال مترابطة. | points[] | Interactive map |
| F-038 | IMAGE_GEN | توليد/تحرير الصور | إنشاء صورة أو تعديل صورة موجودة عند توفر هدف بصري واضح. | visual request | Generated image |
| F-039 | python_analysis | تحليل خاص غير معروض | تنفيذ حسابات وتحليل داخلي للبيانات دون إظهار خطوات التفكير السرية. | data/code | Computed result |
| F-040 | python_user_visible | تنفيذ كود مرئي للمستخدم | إنشاء بيانات/رسومات/ملفات يريد المستخدم رؤيتها مع إخراج رابط عند إنشاء ملف. | code | Visible output/artifact |
| F-041 | container_exec | تشغيل أوامر النظام | فحص الملفات، البناء، التحقق، والمعالجة البرمجية في بيئة العمل. | command | stdout/stderr/files |
| F-042 | container_download | تنزيل ملف إلى بيئة العمل | إحضار ملف من عنوان خارجي عند السماح بذلك. | URL + path | Local file |
| F-043 | container_open_image | عرض صورة محلية | فتح صورة محلية للفحص البصري. | image path | Image |
| F-044 | functions.exec | تنسيق/تنفيذ استدعاءات الأدوات | تنسيق عمليات الأدوات المتاحة في بيئة orchestration واحدة. | JavaScript tool plan | Tool results |
| F-045 | summary_reader.read | استرجاع ملخصات قابلة للمشاركة | قراءة معلومات آمنة من ملخصات المحادثة السابقة عند طلب تتبع كيفية الوصول لإجابة. | limit/offset | Safe summary |
| F-046 | bio.update | إدارة الذاكرة الصريحة | حفظ أو حذف معلومات طلب المستخدم تذكرها مستقبلًا. | memory instruction | Memory status |
| F-047 | safety_settings.get_family_info | قراءة حالة الرقابة العائلية | قراءة حالة Parental Controls قبل أي إجراء متعلق بها. | none | Family state |
| F-048 | safety_settings.get_parental_controls | قراءة إعدادات عضو | قراءة ضوابط عضو مصرح به بعد الحصول على الحالة العامة. | user_id | Controls |
| F-049 | safety_settings.update_parental_control | تحديث ضابط عائلي | تغيير ضابط بعد تحقق التفويض والموافقة الصريحة. | authorized user/control/value | Update result |
| F-050 | safety_settings.get_trusted_contact | إدارة حالة جهة الاتصال الموثوقة | قراءة حالة Trusted Contact قبل أسئلة الإعداد أو الخصوصية. | none | Status |
| F-051 | user_settings__get_user_settings | قراءة الإعدادات الشخصية | قراءة الخيارات الحالية والقيم المسموح بها قبل تغييرها. | none | Settings |
| F-052 | user_settings__set_setting | تغيير الإعدادات الشخصية | تغيير المظهر أو اللون أو الشخصية ضمن القيم المسموح بها. | setting name/value | Update result |
| F-053 | mcp__Automations__create | إنشاء أتمتة | إنشاء مهمة مجدولة وفق القواعد المدعومة. | title + prompt + schedule | Automation status |
| F-054 | mcp__Automations__list | عرض الأتمتة | عرض الأتمتة عندما يطلب المستخدم رؤيتها. | none | Automation list |
| F-055 | mcp__Automations__peek | فحص الأتمتة داخليًا | قراءة أتمتة من دون عرض القائمة للمستخدم. | none | Automation metadata |
| F-056 | mcp__Automations__run_now | تشغيل أتمتة الآن | تشغيل مهمة موجودة فورًا بطلب المستخدم. | jawbone_id | Run status |
| F-057 | mcp__Automations__update | تعديل الأتمتة | تعديل مهمة مجدولة وفق المخطط المسموح. | automation update | Update status |
| F-058 | mcp__Automations__list_event_sources | اكتشاف مصادر أحداث الأتمتة | اكتشاف التطبيقات التي تعرض أحداثًا قابلة للاستخدام في الأتمتة. | none | Event sources |
| F-059 | mcp__Automations__notify_parent | إرسال إشعار لسياق أب | إرسال إشعار إلى الهدف الأب في بيئة الخيوط المتداخلة عند السماح بذلك. | prompt | Notification status |
| F-060 | mcp__Plugin_Management__search_plugins | البحث عن إضافات | اكتشاف Plugin مناسب عندما تحتاج المهمة خدمة خارجية. | query | Plugin results |
| F-061 | mcp__Plugin_Management__suggest_plugins | اقتراح إضافة | اقتراح تثبيت Plugin ملائم يتطلب فعل المستخدم الصريح. | plugin_ids | Suggestion |
| F-062 | mcp__Plugin_Management__get_app_permissions | قراءة صلاحيات التطبيق | فحص صلاحيات تطبيق متصل قبل الاستخدامات التي تحتاجها. | app | Permissions |
| F-063 | mcp__Plugin_Management__get_plugin_dependencies | فحص تبعيات الإضافة | معرفة الاعتماديات اللازمة قبل التفعيل. | plugin | Dependencies |
| F-064 | mcp__Plugin_Management__update_app_permissions | تحديث صلاحيات التطبيق | تغيير الصلاحيات وفق تفويض المستخدم. | app + permissions | Update status |
| F-065 | mcp__Plugin_Management__uninstall_app | إزالة تطبيق متصل | إلغاء تكامل خارجي عند طلب المستخدم. | app | Uninstall status |
| F-066 | skills__list | استعراض المهارات | معرفة المهارات المتاحة قبل الاستفادة من Skill. | none | Skill registry |
| F-067 | skills__read | قراءة تعليمات المهارة | تحميل تعليمات Skill المحددة واستخدامها كعقد تشغيل. | skill URI | Skill instructions |
| F-068 | WRITING_BLOCK_EMITTER | إخراج نص قابل لإعادة الاستخدام | تسليم نص نهائي ضمن Writing Block وبالنوع المناسب. | finished artifact | Writing block |
| F-069 | ARTIFACT_VALIDATOR | فحص الملفات المنشأة | التأكد من وجود الملف وصحة المسار والبنية قبل إرساله. | artifact path | Validation report |
| F-070 | SANDBOX_LINK_EMITTER | إنشاء رابط ملف | إنتاج رابط sandbox فقط بعد التحقق من وجود الملف. | verified path | Sandbox link |
| F-071 | FILE_CITATION_EMITTER | إسناد محتوى الملفات | إرفاق citation خطي أو marker مطابق لمصدر الملف. | file source + lines | filecite |
| F-072 | WEB_CITATION_EMITTER | إسناد مصادر الويب | ربط الفقرات بالمصادر المستخدمة. | web refs | cite/url citation |
| F-073 | BUSINESS_ENTITY_EMITTER | عرض كيان عمل محلي | إخراج كيان عمل من نتائج البحث المحلي بصيغته المناسبة. | business ref | Business entity UI |
| F-074 | PRODUCT_UI_EMITTER | عرض منتجات بشكل غني | إظهار كيان أو مقارنة أو carousel عند توفر نتائج تسوق. | product refs | Product UI |
| F-075 | IMAGE_GROUP_EMITTER | عرض مجموعة صور | عرض الصور في مجموعة عندما تضيف قيمة بصرية. | image refs | Image group |
| F-076 | VIDEO_EMITTER | عرض فيديو | عرض مشغل فيديو عند وجود مصدر مناسب. | video ref | Video UI |
| F-077 | NAVLIST_EMITTER | تنسيق ملاحي للمصادر | عرض قائمة مصادر حديثة عندما يكون السؤال إخباريًا ويكون ذلك مفيدًا. | news refs | Navlist |
| F-078 | POLICY_GATE | تطبيق قواعد المجال | تحديد القيود السلوكية الخاصة بالمجال قبل التوليد. | task + policy set | Policy decision |
| F-079 | PRIVATE_REASONING_BOUNDARY | حماية التفكير الخاص | فصل التحليل الداخلي غير القابل للتصدير عن المخرجات التي يجوز عرضها. | internal state | Public-safe explanation |
| F-080 | MEMORY_CITATION_CONTROL | ضبط إسناد الذاكرة | تحديد متى يلزم إسناد معلومة إلى ذاكرة صريحة. | memory-derived claim | Memory citation marker |
| F-081 | ARTIFACT_SKILL_ROUTER | توجيه مهارات المستندات | اختيار Skill المناسبة لمستندات PDF/DOCX/Slides/Spreadsheets عند الحاجة. | artifact type | Skill plan |
| F-082 | DOCX_ARTIFACT_PIPELINE | إنشاء/تحرير DOCX | تخطيط إنشاء مستند Word مع فحصه بصريًا وبنيويًا. | document spec | DOCX artifact |
| F-083 | PDF_ARTIFACT_PIPELINE | إنشاء/تحرير PDF | تخطيط PDF مع تطبيق متطلبات الفحص البصري للصفحات. | PDF spec | PDF artifact |
| F-084 | SLIDES_ARTIFACT_PIPELINE | إنشاء/تحرير العروض | تخطيط الشرائح وتطبيق مهارات العروض ثم التحقق. | slide spec | PPTX artifact |
| F-085 | SPREADSHEET_ARTIFACT_PIPELINE | إنشاء/تحرير الجداول | تخطيط XLSX/CSV عبر أدوات الجداول المخصصة وعدم استبدالها بـLibreOffice عند المنع. | sheet spec | Spreadsheet artifact |
| F-086 | CONNECTOR_ACTION_DISCOVERY | اكتشاف إجراء الموصل | اختيار إجراء connector مطابق لمخطط الرابط أو الخدمة بدل افتراض API. | URL/service context | Connector action |
| F-087 | CONNECTOR_ID_REUSE | إعادة استخدام المعرفات | استخدام document_id/content_location المحصل سابقًا بدل إعادة إرسال الرابط عند دعم ذلك. | connector result | Stable reference |
| F-088 | EXTERNAL_ACTION_CONFIRMATION | تأكيد الأفعال الخارجية | اشتراط تأكيد المستخدم للأفعال المؤثرة عندما يقتضي السياق ذلك. | action + authorization | Authorization gate |
| F-089 | TOOL_SCHEMA_VALIDATOR | التحقق من مخطط الأداة | فحص أسماء الحقول والأنواع قبل الاستدعاء. | tool schema + args | Valid/invalid |
| F-090 | TOOL_RESULT_NORMALIZER | توحيد نتائج الأدوات | تحويل النتائج المختلفة إلى صيغة موحدة يمكن لباقي النظام استخدامها. | raw tool result | Normalized result |
| F-091 | TOOL_TRACE_RECORDER | تسجيل استدعاءات الأدوات | تسجيل الأداة والوسيطات والنتيجة والزمن والحالة دون أسرار غير لازمة. | call event | Trace record |
| F-092 | SOURCE_FRESHNESS_CHECK | فحص حداثة المصدر | تحديد هل المعلومة تحتاج بحثًا حديثًا قبل عرضها. | claim + timestamp | Freshness decision |
| F-093 | SOURCE_AUTHORITY_CHECK | فحص سلطة المصدر | تقييم ملاءمة المصدر لطبيعة الادعاء. | claim + sources | Source quality |
| F-094 | CROSS_SOURCE_RECONCILER | مصالحة المصادر | مقارنة مصادر متعددة وكشف التعارض وعدم دمجها بلا تحقق. | sources[] | Reconciled evidence |
| F-095 | DATA_PROVENANCE_TRACKER | تتبع أصل البيانات | ربط كل عنصر بمصدره ومعالجته وإصداره. | data lineage | Provenance graph |
| F-096 | SCHEMA_MIGRATION_ENGINE | ترحيل المخططات | تحديث مخطط البيانات مع الحفاظ على قابلية القراءة من الإصدارات السابقة. | schema vN→vN+1 | Migration |
| F-097 | CONFIG_RESOLVER | حل الإعدادات | دمج إعدادات النظام والمنتج والمستخدم والمهمة مع أولوية واضحة. | config layers | Resolved config |
| F-098 | FEATURE_FLAG_ENGINE | إدارة الميزات المرحلية | تشغيل/إيقاف وظائف حسب إصدار أو شريحة أو تجربة. | flags + context | Feature state |
| F-099 | AUDIT_EVENT_WRITER | كتابة سجل التدقيق | تسجيل الأفعال المؤثرة ومصدرها والوقت والنتيجة. | action event | Audit record |
| F-100 | INCIDENT_ROUTER | توجيه الحوادث | فتح سجل حادثة وربط الأثر والسبب والإصلاح والتحقق. | incident signals | Incident record |

## 1.1 مبدأ دورة الوظيفة
