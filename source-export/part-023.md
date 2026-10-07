      "domain": "تقارير التقدم",
      "purpose": "عرض حالة العمل والمرحلة ونسبة الإنجاز عندما تكون المهمة طويلة.",
      "input_contract": "Execution state",
      "output_contract": "Progress event"
    },
    {
      "id": "F-016",
      "name": "FINAL_RESPONSE_BUILDER",
      "domain": "تركيب الرد النهائي",
      "purpose": "جمع النتائج والتحقق والإسناد في مخرج واحد متماسك.",
      "input_contract": "Verified result",
      "output_contract": "Final response"
    },
    {
      "id": "F-017",
      "name": "files__search",
      "domain": "بحث الملفات",
      "purpose": "بحث دلالي داخل ملفات المحادثة أو المكتبة.",
      "input_contract": "search_query + scope",
      "output_contract": "Relevant file chunks"
    },
    {
      "id": "F-018",
      "name": "files__find",
      "domain": "العثور على نص دقيق",
      "purpose": "البحث عن عبارة أو عنوان معروف داخل ملف محدد.",
      "input_contract": "file + exact term",
      "output_contract": "Matches"
    },
    {
      "id": "F-019",
      "name": "files__read",
      "domain": "قراءة الملفات",
      "purpose": "قراءة نطاقات نصية أو صفحات مع توسيع النتائج عند الحاجة.",
      "input_contract": "file + range",
      "output_contract": "Content"
    },
    {
      "id": "F-020",
      "name": "files__list",
      "domain": "استعراض الملفات",
      "purpose": "استعراض أسماء وبيانات الملفات والمجلدات عند الحاجة الوصفية.",
      "input_contract": "scope/path",
      "output_contract": "File metadata"
    },
    {
      "id": "F-021",
      "name": "files__materialize",
      "domain": "إحضار ملف للمعالجة",
      "purpose": "وضع النسخة الأصلية أو النص المستخرج في بيئة العمل.",
      "input_contract": "file_ref + representation",
      "output_contract": "Container artifact"
    },
    {
      "id": "F-022",
      "name": "files__manage_library",
      "domain": "إدارة مكتبة الملفات",
      "purpose": "رفع أو نقل أو إعادة تسمية أو حذف الملفات وإنشاء المجلدات.",
      "input_contract": "operations[]",
      "output_contract": "Mutation result"
    },
    {
      "id": "F-023",
      "name": "files__share",
      "domain": "إدارة مشاركة الملفات",
      "purpose": "منح أو سحب الوصول لملف أو مجلد بصلاحيات محددة.",
      "input_contract": "canonical target + role",
      "output_contract": "Share status"
    },
    {
      "id": "F-024",
      "name": "files__image_read",
      "domain": "فحص الصور داخل المستندات",
      "purpose": "استخراج/عرض الصور المضمّنة عند الحاجة للفهم البصري.",
      "input_contract": "document + page",
      "output_contract": "Image asset"
    },
    {
      "id": "F-025",
      "name": "WEB_SEARCH_FAST",
      "domain": "بحث ويب سريع",
      "purpose": "البحث الواسع منخفض الكلفة نسبيًا للاستكشاف.",
      "input_contract": "query + recency/domain",
      "output_contract": "Search results"
    },
    {
      "id": "F-026",
      "name": "WEB_SEARCH_SLOW",
      "domain": "بحث ويب عميق",
      "purpose": "البحث الأكثر انتقائية عندما تحتاج المهمة دقة أو اكتشافًا أصعب.",
      "input_contract": "query + recency/domain",
      "output_contract": "Search results"
    },
    {
      "id": "F-027",
      "name": "WEB_OPEN",
      "domain": "فتح مصدر ويب",
      "purpose": "فتح صفحة أو مصدر معروف.",
      "input_contract": "URL/ref",
      "output_contract": "Page"
    },
    {
      "id": "F-028",
      "name": "WEB_CLICK",
      "domain": "اتباع الروابط",
      "purpose": "فتح رابط مرقّم داخل صفحة مفتوحة.",
      "input_contract": "page ref + link id",
      "output_contract": "Linked page"
    },
    {
      "id": "F-029",
      "name": "WEB_FIND",
      "domain": "العثور داخل صفحة",
      "purpose": "العثور على نص محدد داخل مصدر مفتوح.",
      "input_contract": "page ref + pattern",
      "output_contract": "Match"
    },
    {
      "id": "F-030",
      "name": "WEB_SCREENSHOT",
      "domain": "لقطة PDF",
      "purpose": "التقاط صفحة من PDF مفتوح عند الحاجة للتحليل البصري.",
      "input_contract": "pdf ref + page",
      "output_contract": "Screenshot"
    },
    {
      "id": "F-031",
      "name": "WEB_IMAGE_QUERY",
      "domain": "بحث الصور",
      "purpose": "البحث عن صور مناسبة عندما تكون الصور جزءًا مفيدًا من الإجابة.",
      "input_contract": "query",
      "output_contract": "Image results"
    },
    {
      "id": "F-032",
      "name": "WEB_PRODUCT_QUERY",
      "domain": "بحث المنتجات",
      "purpose": "البحث عن منتجات فعلية قابلة للشراء.",
      "input_contract": "search/lookup",
      "output_contract": "Product results"
    },
    {
      "id": "F-033",
      "name": "WEB_BUSINESS_QUERY",
      "domain": "بحث الأماكن والخدمات",
      "purpose": "البحث عن أعمال وأماكن محلية فعلية.",
      "input_contract": "location + query/lookup",
      "output_contract": "Business results"
    },
    {
      "id": "F-034",
      "name": "WEB_AVAILABILITY_QUERY",
      "domain": "فحص توفر المطاعم",
      "purpose": "فحص توفر حجوزات المطاعم ضمن وقت محدد.",
      "input_contract": "location + time + party size",
      "output_contract": "Availability"
    },
    {
      "id": "F-035",
      "name": "GENUI_SEARCH",
      "domain": "اكتشاف الواجهات التفاعلية",
      "purpose": "العثور على Widget مناسب لفئات تدعم واجهات غنية.",
      "input_contract": "widget category",
      "output_contract": "Widget schema"
    },
    {
      "id": "F-036",
      "name": "GENUI_RUN",
      "domain": "تشغيل واجهة تفاعلية",
      "purpose": "تشغيل Widget وفق مخططه المعتمد.",
      "input_contract": "widget + args",
      "output_contract": "Rendered widget/result"
    },
    {
      "id": "F-037",
      "name": "MAP_WIDGET",
      "domain": "عرض المواقع على خريطة",
      "purpose": "عرض مجموعة نقاط جغرافية أو أعمال مترابطة.",
      "input_contract": "points[]",
      "output_contract": "Interactive map"
    },
    {
      "id": "F-038",
      "name": "IMAGE_GEN",
      "domain": "توليد/تحرير الصور",
      "purpose": "إنشاء صورة أو تعديل صورة موجودة عند توفر هدف بصري واضح.",
      "input_contract": "visual request",
      "output_contract": "Generated image"
    },
    {
      "id": "F-039",
      "name": "python_analysis",
      "domain": "تحليل خاص غير معروض",
      "purpose": "تنفيذ حسابات وتحليل داخلي للبيانات دون إظهار خطوات التفكير السرية.",
      "input_contract": "data/code",
      "output_contract": "Computed result"
    },
    {
      "id": "F-040",
      "name": "python_user_visible",
      "domain": "تنفيذ كود مرئي للمستخدم",
      "purpose": "إنشاء بيانات/رسومات/ملفات يريد المستخدم رؤيتها مع إخراج رابط عند إنشاء ملف.",
      "input_contract": "code",
      "output_contract": "Visible output/artifact"
    },
    {
      "id": "F-041",
      "name": "container_exec",
      "domain": "تشغيل أوامر النظام",
      "purpose": "فحص الملفات، البناء، التحقق، والمعالجة البرمجية في بيئة العمل.",
      "input_contract": "command",
      "output_contract": "stdout/stderr/files"
    },
    {
      "id": "F-042",
      "name": "container_download",
      "domain": "تنزيل ملف إلى بيئة العمل",
      "purpose": "إحضار ملف من عنوان خارجي عند السماح بذلك.",
      "input_contract": "URL + path",
      "output_contract": "Local file"
    },
    {
      "id": "F-043",
      "name": "container_open_image",
      "domain": "عرض صورة محلية",
      "purpose": "فتح صورة محلية للفحص البصري.",
      "input_contract": "image path",
      "output_contract": "Image"
    },
    {
      "id": "F-044",
      "name": "functions.exec",
      "domain": "تنسيق/تنفيذ استدعاءات الأدوات",
      "purpose": "تنسيق عمليات الأدوات المتاحة في بيئة orchestration واحدة.",
      "input_contract": "JavaScript tool plan",
      "output_contract": "Tool results"
    },
    {
      "id": "F-045",
      "name": "summary_reader.read",
      "domain": "استرجاع ملخصات قابلة للمشاركة",
      "purpose": "قراءة معلومات آمنة من ملخصات المحادثة السابقة عند طلب تتبع كيفية الوصول لإجابة.",
      "input_contract": "limit/offset",
      "output_contract": "Safe summary"
    },
    {
      "id": "F-046",
      "name": "bio.update",
      "domain": "إدارة الذاكرة الصريحة",
      "purpose": "حفظ أو حذف معلومات طلب المستخدم تذكرها مستقبلًا.",
      "input_contract": "memory instruction",
      "output_contract": "Memory status"
    },
    {
      "id": "F-047",
      "name": "safety_settings.get_family_info",
      "domain": "قراءة حالة الرقابة العائلية",
      "purpose": "قراءة حالة Parental Controls قبل أي إجراء متعلق بها.",
      "input_contract": "none",
      "output_contract": "Family state"
    },
    {
      "id": "F-048",
      "name": "safety_settings.get_parental_controls",
      "domain": "قراءة إعدادات عضو",
      "purpose": "قراءة ضوابط عضو مصرح به بعد الحصول على الحالة العامة.",
      "input_contract": "user_id",
      "output_contract": "Controls"
    },
    {
      "id": "F-049",
      "name": "safety_settings.update_parental_control",
      "domain": "تحديث ضابط عائلي",
      "purpose": "تغيير ضابط بعد تحقق التفويض والموافقة الصريحة.",
      "input_contract": "authorized user/control/value",
      "output_contract": "Update result"
    },
    {
      "id": "F-050",
      "name": "safety_settings.get_trusted_contact",
      "domain": "إدارة حالة جهة الاتصال الموثوقة",
      "purpose": "قراءة حالة Trusted Contact قبل أسئلة الإعداد أو الخصوصية.",
      "input_contract": "none",
      "output_contract": "Status"
    },
    {
      "id": "F-051",
      "name": "user_settings__get_user_settings",
      "domain": "قراءة الإعدادات الشخصية",
      "purpose": "قراءة الخيارات الحالية والقيم المسموح بها قبل تغييرها.",
      "input_contract": "none",
      "output_contract": "Settings"
    },
    {
      "id": "F-052",
      "name": "user_settings__set_setting",
      "domain": "تغيير الإعدادات الشخصية",
      "purpose": "تغيير المظهر أو اللون أو الشخصية ضمن القيم المسموح بها.",
      "input_contract": "setting name/value",
      "output_contract": "Update result"
    },
    {
      "id": "F-053",
      "name": "mcp__Automations__create",
      "domain": "إنشاء أتمتة",
      "purpose": "إنشاء مهمة مجدولة وفق القواعد المدعومة.",
      "input_contract": "title + prompt + schedule",
      "output_contract": "Automation status"
    },
    {
      "id": "F-054",
      "name": "mcp__Automations__list",
      "domain": "عرض الأتمتة",
      "purpose": "عرض الأتمتة عندما يطلب المستخدم رؤيتها.",
      "input_contract": "none",
      "output_contract": "Automation list"
    },
    {
      "id": "F-055",
      "name": "mcp__Automations__peek",
      "domain": "فحص الأتمتة داخليًا",
      "purpose": "قراءة أتمتة من دون عرض القائمة للمستخدم.",
      "input_contract": "none",
      "output_contract": "Automation metadata"
    },
    {
      "id": "F-056",
      "name": "mcp__Automations__run_now",
      "domain": "تشغيل أتمتة الآن",
      "purpose": "تشغيل مهمة موجودة فورًا بطلب المستخدم.",
      "input_contract": "jawbone_id",
      "output_contract": "Run status"
    },
    {
      "id": "F-057",
      "name": "mcp__Automations__update",
      "domain": "تعديل الأتمتة",
      "purpose": "تعديل مهمة مجدولة وفق المخطط المسموح.",
      "input_contract": "automation update",
      "output_contract": "Update status"
    },
    {
      "id": "F-058",
      "name": "mcp__Automations__list_event_sources",
      "domain": "اكتشاف مصادر أحداث الأتمتة",
      "purpose": "اكتشاف التطبيقات التي تعرض أحداثًا قابلة للاستخدام في الأتمتة.",
      "input_contract": "none",
      "output_contract": "Event sources"
    },
    {
      "id": "F-059",
      "name": "mcp__Automations__notify_parent",
      "domain": "إرسال إشعار لسياق أب",
      "purpose": "إرسال إشعار إلى الهدف الأب في بيئة الخيوط المتداخلة عند السماح بذلك.",
      "input_contract": "prompt",
      "output_contract": "Notification status"
    },
    {
      "id": "F-060",
      "name": "mcp__Plugin_Management__search_plugins",
      "domain": "البحث عن إضافات",
      "purpose": "اكتشاف Plugin مناسب عندما تحتاج المهمة خدمة خارجية.",
      "input_contract": "query",
      "output_contract": "Plugin results"
    },
    {
      "id": "F-061",
      "name": "mcp__Plugin_Management__suggest_plugins",
      "domain": "اقتراح إضافة",
      "purpose": "اقتراح تثبيت Plugin ملائم يتطلب فعل المستخدم الصريح.",
      "input_contract": "plugin_ids",
      "output_contract": "Suggestion"
    },
    {
      "id": "F-062",
      "name": "mcp__Plugin_Management__get_app_permissions",
      "domain": "قراءة صلاحيات التطبيق",
      "purpose": "فحص صلاحيات تطبيق متصل قبل الاستخدامات التي تحتاجها.",
      "input_contract": "app",
      "output_contract": "Permissions"
    },
    {
      "id": "F-063",
      "name": "mcp__Plugin_Management__get_plugin_dependencies",
      "domain": "فحص تبعيات الإضافة",
      "purpose": "معرفة الاعتماديات اللازمة قبل التفعيل.",
      "input_contract": "plugin",
      "output_contract": "Dependencies"
    },
    {
      "id": "F-064",
      "name": "mcp__Plugin_Management__update_app_permissions",
      "domain": "تحديث صلاحيات التطبيق",
      "purpose": "تغيير الصلاحيات وفق تفويض المستخدم.",
      "input_contract": "app + permissions",
      "output_contract": "Update status"
    },
    {
      "id": "F-065",
      "name": "mcp__Plugin_Management__uninstall_app",
      "domain": "إزالة تطبيق متصل",
      "purpose": "إلغاء تكامل خارجي عند طلب المستخدم.",
      "input_contract": "app",
      "output_contract": "Uninstall status"
    },
    {
      "id": "F-066",
      "name": "skills__list",
      "domain": "استعراض المهارات",
      "purpose": "معرفة المهارات المتاحة قبل الاستفادة من Skill.",
      "input_contract": "none",
      "output_contract": "Skill registry"
    },
    {
      "id": "F-067",
      "name": "skills__read",
      "domain": "قراءة تعليمات المهارة",
      "purpose": "تحميل تعليمات Skill المحددة واستخدامها كعقد تشغيل.",
      "input_contract": "skill URI",
      "output_contract": "Skill instructions"
    },
    {
      "id": "F-068",
      "name": "WRITING_BLOCK_EMITTER",
      "domain": "إخراج نص قابل لإعادة الاستخدام",
      "purpose": "تسليم نص نهائي ضمن Writing Block وبالنوع المناسب.",
      "input_contract": "finished artifact",
      "output_contract": "Writing block"
    },
    {
      "id": "F-069",
      "name": "ARTIFACT_VALIDATOR",
      "domain": "فحص الملفات المنشأة",
      "purpose": "التأكد من وجود الملف وصحة المسار والبنية قبل إرساله.",
      "input_contract": "artifact path",
      "output_contract": "Validation report"
    },
    {
      "id": "F-070",
      "name": "SANDBOX_LINK_EMITTER",
      "domain": "إنشاء رابط ملف",
      "purpose": "إنتاج رابط sandbox فقط بعد التحقق من وجود الملف.",
      "input_contract": "verified path",
      "output_contract": "Sandbox link"
    },
    {
      "id": "F-071",
      "name": "FILE_CITATION_EMITTER",
      "domain": "إسناد محتوى الملفات",
      "purpose": "إرفاق citation خطي أو marker مطابق لمصدر الملف.",
      "input_contract": "file source + lines",
      "output_contract": "filecite"
    },
    {
      "id": "F-072",
      "name": "WEB_CITATION_EMITTER",
      "domain": "إسناد مصادر الويب",
      "purpose": "ربط الفقرات بالمصادر المستخدمة.",
      "input_contract": "web refs",
      "output_contract": "cite/url citation"
    },
    {
      "id": "F-073",
      "name": "BUSINESS_ENTITY_EMITTER",
      "domain": "عرض كيان عمل محلي",
      "purpose": "إخراج كيان عمل من نتائج البحث المحلي بصيغته المناسبة.",
      "input_contract": "business ref",
      "output_contract": "Business entity UI"
    },
    {
      "id": "F-074",
      "name": "PRODUCT_UI_EMITTER",
      "domain": "عرض منتجات بشكل غني",
      "purpose": "إظهار كيان أو مقارنة أو carousel عند توفر نتائج تسوق.",
      "input_contract": "product refs",
      "output_contract": "Product UI"
    },
    {
      "id": "F-075",
      "name": "IMAGE_GROUP_EMITTER",
      "domain": "عرض مجموعة صور",
      "purpose": "عرض الصور في مجموعة عندما تضيف قيمة بصرية.",
      "input_contract": "image refs",
      "output_contract": "Image group"
    },
    {
      "id": "F-076",
      "name": "VIDEO_EMITTER",
      "domain": "عرض فيديو",
      "purpose": "عرض مشغل فيديو عند وجود مصدر مناسب.",
      "input_contract": "video ref",
      "output_contract": "Video UI"
    },
    {
      "id": "F-077",
      "name": "NAVLIST_EMITTER",
      "domain": "تنسيق ملاحي للمصادر",
      "purpose": "عرض قائمة مصادر حديثة عندما يكون السؤال إخباريًا ويكون ذلك مفيدًا.",
      "input_contract": "news refs",
      "output_contract": "Navlist"
    },
    {
      "id": "F-078",
      "name": "POLICY_GATE",
      "domain": "تطبيق قواعد المجال",
      "purpose": "تحديد القيود السلوكية الخاصة بالمجال قبل التوليد.",
      "input_contract": "task + policy set",
      "output_contract": "Policy decision"
    },
    {
      "id": "F-079",
      "name": "PRIVATE_REASONING_BOUNDARY",
      "domain": "حماية التفكير الخاص",
      "purpose": "فصل التحليل الداخلي غير القابل للتصدير عن المخرجات التي يجوز عرضها.",
      "input_contract": "internal state",
      "output_contract": "Public-safe explanation"
    },
    {
      "id": "F-080",
      "name": "MEMORY_CITATION_CONTROL",
      "domain": "ضبط إسناد الذاكرة",
      "purpose": "تحديد متى يلزم إسناد معلومة إلى ذاكرة صريحة.",
      "input_contract": "memory-derived claim",
      "output_contract": "Memory citation marker"
    },
    {
      "id": "F-081",
      "name": "ARTIFACT_SKILL_ROUTER",
      "domain": "توجيه مهارات المستندات",
      "purpose": "اختيار Skill المناسبة لمستندات PDF/DOCX/Slides/Spreadsheets عند الحاجة.",
      "input_contract": "artifact type",
      "output_contract": "Skill plan"
    },
    {
      "id": "F-082",
      "name": "DOCX_ARTIFACT_PIPELINE",
      "domain": "إنشاء/تحرير DOCX",
      "purpose": "تخطيط إنشاء مستند Word مع فحصه بصريًا وبنيويًا.",
      "input_contract": "document spec",
      "output_contract": "DOCX artifact"
    },
    {
      "id": "F-083",
      "name": "PDF_ARTIFACT_PIPELINE",
      "domain": "إنشاء/تحرير PDF",
      "purpose": "تخطيط PDF مع تطبيق متطلبات الفحص البصري للصفحات.",
      "input_contract": "PDF spec",
      "output_contract": "PDF artifact"
    },
    {
      "id": "F-084",
      "name": "SLIDES_ARTIFACT_PIPELINE",
      "domain": "إنشاء/تحرير العروض",
      "purpose": "تخطيط الشرائح وتطبيق مهارات العروض ثم التحقق.",
      "input_contract": "slide spec",
      "output_contract": "PPTX artifact"
    },
    {
      "id": "F-085",
      "name": "SPREADSHEET_ARTIFACT_PIPELINE",
      "domain": "إنشاء/تحرير الجداول",
      "purpose": "تخطيط XLSX/CSV عبر أدوات الجداول المخصصة وعدم استبدالها بـLibreOffice عند المنع.",
      "input_contract": "sheet spec",
      "output_contract": "Spreadsheet artifact"
    },
    {
      "id": "F-086",
      "name": "CONNECTOR_ACTION_DISCOVERY",
      "domain": "اكتشاف إجراء الموصل",
      "purpose": "اختيار إجراء connector مطابق لمخطط الرابط أو الخدمة بدل افتراض API.",
      "input_contract": "URL/service context",
      "output_contract": "Connector action"
    },
    {
      "id": "F-087",
      "name": "CONNECTOR_ID_REUSE",
      "domain": "إعادة استخدام المعرفات",
      "purpose": "استخدام document_id/content_location المحصل سابقًا بدل إعادة إرسال الرابط عند دعم ذلك.",
      "input_contract": "connector result",
      "output_contract": "Stable reference"
    },
    {
      "id": "F-088",
      "name": "EXTERNAL_ACTION_CONFIRMATION",
      "domain": "تأكيد الأفعال الخارجية",
      "purpose": "اشتراط تأكيد المستخدم للأفعال المؤثرة عندما يقتضي السياق ذلك.",
      "input_contract": "action + authorization",
      "output_contract": "Authorization gate"
    },
    {
      "id": "F-089",
      "name": "TOOL_SCHEMA_VALIDATOR",
      "domain": "التحقق من مخطط الأداة",
      "purpose": "فحص أسماء الحقول والأنواع قبل الاستدعاء.",
      "input_contract": "tool schema + args",
      "output_contract": "Valid/invalid"
    },
    {
      "id": "F-090",
      "name": "TOOL_RESULT_NORMALIZER",
      "domain": "توحيد نتائج الأدوات",
      "purpose": "تحويل النتائج المختلفة إلى صيغة موحدة يمكن لباقي النظام استخدامها.",
      "input_contract": "raw tool result",
      "output_contract": "Normalized result"
    },
    {
      "id": "F-091",
      "name": "TOOL_TRACE_RECORDER",
      "domain": "تسجيل استدعاءات الأدوات",
      "purpose": "تسجيل الأداة والوسيطات والنتيجة والزمن والحالة دون أسرار غير لازمة.",
      "input_contract": "call event",
      "output_contract": "Trace record"
    },
    {
      "id": "F-092",
      "name": "SOURCE_FRESHNESS_CHECK",
      "domain": "فحص حداثة المصدر",
      "purpose": "تحديد هل المعلومة تحتاج بحثًا حديثًا قبل عرضها.",
      "input_contract": "claim + timestamp",
      "output_contract": "Freshness decision"
    },
    {
      "id": "F-093",
      "name": "SOURCE_AUTHORITY_CHECK",
      "domain": "فحص سلطة المصدر",
      "purpose": "تقييم ملاءمة المصدر لطبيعة الادعاء.",
      "input_contract": "claim + sources",
      "output_contract": "Source quality"
    },
    {
      "id": "F-094",
      "name": "CROSS_SOURCE_RECONCILER",
      "domain": "مصالحة المصادر",
      "purpose": "مقارنة مصادر متعددة وكشف التعارض وعدم دمجها بلا تحقق.",
      "input_contract": "sources[]",
      "output_contract": "Reconciled evidence"
    },
    {
      "id": "F-095",
      "name": "DATA_PROVENANCE_TRACKER",
      "domain": "تتبع أصل البيانات",
      "purpose": "ربط كل عنصر بمصدره ومعالجته وإصداره.",
      "input_contract": "data lineage",
      "output_contract": "Provenance graph"
    },
    {
      "id": "F-096",
      "name": "SCHEMA_MIGRATION_ENGINE",
      "domain": "ترحيل المخططات",
      "purpose": "تحديث مخطط البيانات مع الحفاظ على قابلية القراءة من الإصدارات السابقة.",
      "input_contract": "schema vN→vN+1",
      "output_contract": "Migration"
    },
    {
      "id": "F-097",
      "name": "CONFIG_RESOLVER",
      "domain": "حل الإعدادات",
      "purpose": "دمج إعدادات النظام والمنتج والمستخدم والمهمة مع أولوية واضحة.",
      "input_contract": "config layers",
      "output_contract": "Resolved config"
    },
    {
      "id": "F-098",
      "name": "FEATURE_FLAG_ENGINE",
      "domain": "إدارة الميزات المرحلية",
      "purpose": "تشغيل/إيقاف وظائف حسب إصدار أو شريحة أو تجربة.",
      "input_contract": "flags + context",
      "output_contract": "Feature state"
    },
    {
      "id": "F-099",
      "name": "AUDIT_EVENT_WRITER",
      "domain": "كتابة سجل التدقيق",
      "purpose": "تسجيل الأفعال المؤثرة ومصدرها والوقت والنتيجة.",
      "input_contract": "action event",
      "output_contract": "Audit record"
    },
    {
      "id": "F-100",
      "name": "INCIDENT_ROUTER",
      "domain": "توجيه الحوادث",
      "purpose": "فتح سجل حادثة وربط الأثر والسبب والإصلاح والتحقق.",
      "input_contract": "incident signals",
      "output_contract": "Incident record"
    }
  ]
}

```

---

### `50/588` `backend/control_plane/kca_registry.py`

- **المسار الكامل:** `F:\1f\p\ALI_Studio_Pro_Design4_4.6.0\04_Adaptive_Hybrid\backend/control_plane/kca_registry.py`
- **الحجم:** 1027 بايت (1.0 KB)
- **الامتداد:** `.py`

```python
# -*- coding: utf-8 -*-
"""Load the source-derived 100-function AI-KCA registry without hard-coding it in UI code."""
from __future__ import annotations
from pathlib import Path
import json
from typing import Any

ROOT = Path(__file__).resolve().parent
REGISTRY_PATH = ROOT / "function_registry.json"


def load_function_registry(path: str | Path = REGISTRY_PATH) -> dict[str, dict[str, Any]]:
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    rows = data.get("functions") or []
    return {str(row["id"]): row for row in rows if row.get("id")}


FUNCTIONS = load_function_registry()
BY_NAME = {row["name"]: row for row in FUNCTIONS.values()}


def function_by_name(name: str) -> dict[str, Any] | None:
    return BY_NAME.get(str(name))


def summary() -> dict[str, Any]:
    domains: dict[str, int] = {}
    for row in FUNCTIONS.values():
        d = str(row.get("domain") or "unknown")
        domains[d] = domains.get(d, 0) + 1
    return {"version": "3.0", "functions": len(FUNCTIONS), "domains": domains}

```

---

### `51/588` `backend/control_plane/README.md`

- **المسار الكامل:** `F:\1f\p\ALI_Studio_Pro_Design4_4.6.0\04_Adaptive_Hybrid\backend/control_plane/README.md`
- **الحجم:** 189 بايت (0.2 KB)
- **الامتداد:** `.md`

```markdown
# ALI AI 2.1 — Unified KCA Control Plane

This layer integrates the 3.0 AI-KCA operational architecture with the existing ALI runtime without replacing the proven runtime/tool contracts.
```

---

### `52/588` `backend/control_plane/router.py`

- **المسار الكامل:** `F:\1f\p\ALI_Studio_Pro_Design4_4.6.0\04_Adaptive_Hybrid\backend/control_plane/router.py`
- **الحجم:** 5284 بايت (5.2 KB)
- **الامتداد:** `.py`

```python
# -*- coding: utf-8 -*-
"""Deterministic KCA request router: normalize -> intent -> capabilities -> plan."""
from __future__ import annotations
from dataclasses import dataclass, asdict
from typing import Any
import re

from control_plane.contracts import RequestEnvelope, TaskState, PlanStep
from control_plane.kca_registry import function_by_name

_AR = re.compile(r"[\u0600-\u06ff]")


@dataclass(frozen=True)
class RouteResult:
    intent: str
    confidence: float
    language: str
    goal: str
    constraints: tuple[str, ...] = ()


class KCARequestRouter:
    """Small deterministic router intended as the stable front-controller.

    Learned routing can be plugged in later; the output contract stays unchanged.
    """

    RULES = [
        (re.compile(r"^(read_file|read|اقرأ\s+ملف|افتح\s+ملف)\s+", re.I), "read_file", .98),
        (re.compile(r"^(write_file|write|أنشئ\s+ملف|اكتب\s+في\s+ملف)\s+", re.I), "write_file", .98),
        (re.compile(r"^(list_dir|ls|استعرض\s+المجلد)(?:\s+.*)?$", re.I), "list_dir", .96),
        (re.compile(r"^(search_files|search|ابحث\s+في\s+الملفات)\s+", re.I), "search_files", .94),
        (re.compile(r"^(run_command|run|شغّل\s+الأمر)\s+", re.I), "run_command", .96),
        (re.compile(r"^git\s+(status|diff|log|branch|commit)", re.I), "git", .99),
        (re.compile(r"(درّب|تدريب|train|fine.?tun|lora)", re.I), "training", .82),
        (re.compile(r"(gguf|quantiz|حوّل.*gguf|تكميم)", re.I), "gguf", .90),
        (re.compile(r"(حلل\s+المشروع|analy[sz]e\s+project)", re.I), "analyze_project", .88),
    ]

    def route(self, envelope: RequestEnvelope) -> RouteResult:
        text = (envelope.raw_text or "").strip()
        language = envelope.language if envelope.language != "auto" else ("ar" if _AR.search(text) else "en")
        for rule, intent, conf in self.RULES:
            if rule.search(text):
                return RouteResult(intent, conf, language, text)
        return RouteResult("question", .70 if text else 0.0, language, text)

    def build_state(self, envelope: RequestEnvelope) -> TaskState:
        routed = self.route(envelope)
        rest = envelope.raw_text.strip()
        params: dict[str, Any] = {}
        parts = rest.split(maxsplit=1)
        tail = parts[1] if len(parts) > 1 else ""
        if routed.intent == "read_file" and tail.startswith(("ملف ", "file ")):
            tail = tail.split(" ", 1)[1]
        if routed.intent in {"read_file", "list_dir"}:
            params["path"] = tail
        elif routed.intent == "search_files":
            params["pattern"] = tail
        elif routed.intent == "run_command":
            params["command"] = tail
        state = TaskState(
            request_id=envelope.request_id,
            intent=routed.intent,
            confidence=routed.confidence,
            goal=routed.goal,
            implicit_intent=self._implicit_intent(envelope.raw_text),
        )
        state.task_state["language"] = routed.language
        state.task_state["params"] = params
        state.candidate_actions = self.candidates(routed.intent, params)
        if state.candidate_actions:
            state.selected_action = state.candidate_actions[0]
        return state

    def candidates(self, intent: str, params: dict[str, Any]) -> list[dict[str, Any]]:
        mapping = {
            "read_file": ["read_file", "CONTEXT_ASSEMBLER", "VERIFICATION_ENGINE"],
            "write_file": ["write_file", "RISK_GATE", "VERIFICATION_ENGINE", "REPAIR_ENGINE"],
            "list_dir": ["list_dir", "VERIFICATION_ENGINE"],
            "search_files": ["search_files", "CONTEXT_ASSEMBLER"],
            "run_command": ["run_command", "RISK_GATE", "VERIFICATION_ENGINE"],
            "git": ["git_status", "VERIFICATION_ENGINE"],
            "training": ["DATA_PROVENANCE_TRACKER", "PLAN_BUILDER", "EXECUTION_ENGINE", "VERIFICATION_ENGINE"],
            "gguf": ["GGUF_CONVERSION", "VERIFICATION_ENGINE"],
            "analyze_project": ["CONTEXT_ASSEMBLER", "PLAN_BUILDER", "VERIFICATION_ENGINE"],
            "question": ["SOURCE_ROUTER", "FINAL_RESPONSE_BUILDER"],
        }
        out = []
        for name in mapping.get(intent, ["FINAL_RESPONSE_BUILDER"]):
            row = function_by_name(name)
            if row:
                out.append({"id": row["id"], "name": row["name"], "purpose": row["purpose"], "params": params})
            else:
                out.append({"id": None, "name": name, "params": params})
        return out

    def function_count(self) -> int:
        from control_plane.kca_registry import FUNCTIONS
        return len(FUNCTIONS)

    @staticmethod
    def _implicit_intent(text: str) -> str | None:
        low = (text or "").lower()
        if any(x in low for x in ("professional", "احترافي", "بدون أخطاء", "without errors")):
            return "deliver verified, production-oriented result"
        if any(x in low for x in ("compare", "قارن", "مقارنة")):
            return "compare alternatives with evidence"
        if any(x in low for x in ("explain", "اشرح", "وضح")):
            return "understand and learn"
        return None


__all__ = ["KCARequestRouter", "RouteResult"]

```

---

### `53/588` `backend/control_plane/state_store.py`

- **المسار الكامل:** `F:\1f\p\ALI_Studio_Pro_Design4_4.6.0\04_Adaptive_Hybrid\backend/control_plane/state_store.py`
- **الحجم:** 2265 بايت (2.2 KB)
- **الامتداد:** `.py`

```python
# -*- coding: utf-8 -*-
"""SQLite trace/state store for the unified KCA control plane."""
from __future__ import annotations
import json, sqlite3, time
from pathlib import Path
from typing import Any


class KCAStateStore:
    def __init__(self, path: str | Path):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with sqlite3.connect(self.path) as c:
            c.execute("PRAGMA journal_mode=WAL")
            c.execute("""
                CREATE TABLE IF NOT EXISTS kca_operations(
                    operation_id TEXT PRIMARY KEY,
                    request_id TEXT NOT NULL,
                    status TEXT NOT NULL,
                    intent TEXT,
                    state_json TEXT NOT NULL,
                    trace_json TEXT,
                    created_at REAL NOT NULL,
                    updated_at REAL NOT NULL
                )
            """)
            c.execute("CREATE INDEX IF NOT EXISTS idx_kca_request ON kca_operations(request_id)")
            c.execute("CREATE INDEX IF NOT EXISTS idx_kca_status ON kca_operations(status)")

    def upsert(self, operation_id: str, request_id: str, status: str, state: dict[str, Any], trace: dict[str, Any] | None = None) -> None:
        now = time.time()
        with sqlite3.connect(self.path) as c:
            c.execute("""
                INSERT INTO kca_operations(operation_id,request_id,status,intent,state_json,trace_json,created_at,updated_at)
                VALUES(?,?,?,?,?,?,?,?)
                ON CONFLICT(operation_id) DO UPDATE SET status=excluded.status,intent=excluded.intent,
                    state_json=excluded.state_json,trace_json=excluded.trace_json,updated_at=excluded.updated_at
            """, (operation_id, request_id, status, state.get("intent", ""), json.dumps(state, ensure_ascii=False),
                  json.dumps(trace, ensure_ascii=False) if trace is not None else None, now, now))

    def recent(self, limit: int = 50) -> list[dict[str, Any]]:
        with sqlite3.connect(self.path) as c:
            c.row_factory = sqlite3.Row
            rows = c.execute("SELECT * FROM kca_operations ORDER BY updated_at DESC LIMIT ?", (max(1, int(limit)),)).fetchall()
        return [dict(row) for row in rows]

```

---

### `54/588` `backend/core/__init__.py`

- **المسار الكامل:** `F:\1f\p\ALI_Studio_Pro_Design4_4.6.0\04_Adaptive_Hybrid\backend/core/__init__.py`
- **الحجم:** 738 بايت (0.7 KB)
- **الامتداد:** `.py`

```python
# -*- coding: utf-8 -*-
"""core/__init__.py — حزمة core.

تحتوي:
- events: نظام EventBus بسيط وآمن للخيوط.
- context: ConversationContext الذي يجمع thread + messages + tools + perm.
- agent: Professional AI Agent (intent classification + plan + execute + reflect).
"""

from core.events import EventBus, Event
from core.context import ConversationContext
from core.agent import (
    Intent,
    Plan,
    ToolCall,
    ExecutionResult,
    classify_intent,
    plan_actions,
    execute_plan,
    count_tokens,
)

__all__ = [
    "EventBus", "Event", "ConversationContext",
    "Intent", "Plan", "ToolCall", "ExecutionResult",
    "classify_intent", "plan_actions", "execute_plan", "count_tokens",
]
```

---

### `55/588` `backend/core/agent.py`

- **المسار الكامل:** `F:\1f\p\ALI_Studio_Pro_Design4_4.6.0\04_Adaptive_Hybrid\backend/core/agent.py`
- **الحجم:** 14713 بايت (14.4 KB)
- **الامتداد:** `.py`

```python
# -*- coding: utf-8 -*-
"""Professional AI Agent — local multi-step reasoning loop.

المسؤوليات:
- Intent Analysis: يصنف النص إلى intent (read, write, search, command, git, code, question).
- Plan: يبني sequence من tool calls.
- Execute: ينفذ كل tool بترتيب.
- Reflect: يلخص النتائج في رد نهائي.
- Smart Fallback: إذا لا توجد tools، يعطي إجابة مفيدة.

يعمل بدون أي نموذج خارجي — logic محلي + tokenizer للـ token counting.
"""

from __future__ import annotations

import re
import time
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple


# ============================================================================