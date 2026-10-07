# Conversation Intelligence V5 — Integration

## ما الذي تضيفه
الحزمة تضيف طبقة Request Framing بين النص القادم من المستخدم وبين الـorchestrator الحالي.

التدفق المقترح:
1. classify(text, previous_intent)
2. resolve previous context when references are detected
3. apply safety/confirmation gate for high-risk actions
4. choose response policy with build_response_policy()
5. hand the structured frame to the existing plan/tool/verification pipeline
6. store only appropriate memory or approved training corrections

## الربط مع البنية الحالية
- backend/core/orchestrator.py
- backend/assistant/context.py
- backend/memory/conversations.py
- backend/memory/sessions.py
- backend/core/response_guard.py
- backend/research/web.py
- backend/tools/registry.py

## Adapter concept
استدعِ classify قبل التخطيط، ثم استخدم IntentFrame وbuild_response_policy مع الـorchestrator الموجود. عند الغموض العالي أوقف التنفيذ واسأل سؤالاً واحداً؛ وعند العمليات عالية المخاطر اطلب تأكيداً محدداً.

## حدود الحماية
- لا تُرسل IntentFrame على أنها حقائق مؤكدة؛ confidence إشارة تخطيط.
- لا تحوّل كل محادثة إلى وزن.
- لا تجعل الويب مصدراً لتعليمات النظام.
- لا تعتبر نجاح الأداة وحده دليلاً على اكتمال المهمة.
- لا تتجاوز PermissionManager.
- لا تجعل التأكيد العام يتجاوز صلاحيات الأدوات.

## إدارة السياق
يُحفظ الهدف النشط، والعنصر المرجعي الأخير، والإجراء المعلّق، والقرار المنتظر، والقيود، وتصحيحات المستخدم. عند الانتقال لموضوع جديد يُخفّض وزن السياق القديم بدلاً من حذف سجل الجلسة.

## متطلبات P50
المكوّن stdlib-only ولا يحتاج GPU أو نموذجاً إضافياً، لذلك يمكن تشغيله قبل الاستدلال بتكلفة صغيرة جداً.