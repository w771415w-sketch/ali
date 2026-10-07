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
