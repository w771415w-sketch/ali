# ALI Studio Pro 4.3.0 — Training Update v1

تم تضمين تحديث تدريب حقيقي v1 داخل المشروع كـCandidate، مبني فوق `ALI-Bootstrap-v2.5` باستخدام LoRA.

## ما يحتويه التحديث
- 504 أمثلة محادثة عربية/إنجليزية.
- Train / Validation / Test منفصلة.
- أمثلة لفهم النية، التخطيط، المشاريع، الكود، Terminal، Git، Memory، RAG، التدريب، GGUF، التحقق، الأمان، والتطوير الذاتي المقيد.
- Adapter LoRA جاهز.
- نموذج `merged_hf` جاهز للتحميل في Runtime الحالي.

## دورة التطوير
`Active vN → New Data → Validate/Deduplicate → LoRA → Candidate vN+1 → Evaluation → Promotion`

عند فشل التقييم تبقى النسخة السابقة Active، ولا يتم فقد بيانات الدفعة الجديدة.

## قاعدة مهمة
الوثائق المرجعية والمعلومات المتغيرة تدخل RAG. المعلومات الشخصية تدخل Memory. السلوك وطريقة العمل والأمثلة تدخل Training. GGUF هو Artifact نشر بعد اكتمال التقييم.

## ملفات مهمة
- `backend/training/updates/v1/data/train.jsonl`
- `backend/training/updates/v1/data/validation.jsonl`
- `backend/training/updates/v1/data/test.jsonl`
- `backend/training/updates/v1/docs/CONVERSATIONS_V1.md`
- `backend/training/updates/v1/docs/EVALUATION_REPORT.md`
- `backend/models/adapters/pending/ALI-v1/`
- `backend/models/inbox/ALI-v1/`

## الحالة
`v1` مثبت في Inbox كـCandidate ولا يتم جعله Active تلقائياً. هذا يمنع استبدال النموذج السليم قبل اختبار Windows الفعلي.
