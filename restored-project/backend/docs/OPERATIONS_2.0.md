# ALI AI 2.0 — Operations Guide

## أول دورة تشغيل

1. `SETUP.bat`
2. `START.bat`
3. افتح **Knowledge** واختر مجلد البيانات.
4. راجع نتائج Harvest.
5. افتح **Dataset Review** واعتمد العينات التي تريد تدريبها.
6. افتح **Training** واختر `chat` للمحادثات أو `causal` للمعرفة النصية.
7. شغّل التدريب.
8. افحص المرشح في **Models**.
9. نفّذ Evaluation + Regression.
10. Promote فقط للمرشح الذي يمر بالبوابة.

## تدريب مستمر

كل checkpoint مستقل ويحتفظ بحالة optimizer/scheduler/RNG. لاستمرار التدريب استخدم مسار checkpoint نفسه مع `--resume`.

## التعلم من الكتب والوثائق

الوثائق العادية تدخل Knowledge/RAG أولًا. لا يصبح الكتاب تلقائيًا أوزانًا. عندما تكون هناك بيانات كافية يتم بناء Dataset تدريب من المصادر المقبولة، ثم التدريب والتقييم.

## Web Research

يُفعّل من System. البحث الشبكي لا يُنفّذ في الوضع Offline. عند تفعيله يستطيع ALI حفظ المصادر المفيدة في Knowledge Store.

## إدارة الذاكرة

- 2 GB VRAM: profile محافظ.
- batch 1.
- gradient accumulation مرتفع.
- sequence length منخفض نسبيًا.
- gradient checkpointing.
- CPU fallback إذا لم تتوفر CUDA.

## الاسترداد

عند توقف التدريب لا تحذف checkpoint. أعد التشغيل من `--resume`، وسيتم استعادة الحالة المحفوظة.

## GGUF

ضع llama.cpp محليًا في `vendor/llama.cpp` ثم استخدم:
