# ALI Training Update v1

هذه حزمة بيانات تدريب سلوكي لوكيل ALI المحلي.

## الملفات
- `data/train.jsonl`
- `data/validation.jsonl`
- `data/test.jsonl`
- `docs/CONVERSATIONS_COVERAGE.md`
- `train_v1.py`

## الأعداد
Total: 504
Train: 394
Validation: 55
Test: 55

## التركيب
التحديث لا يستبدل النموذج النشط مباشرة. يدرّب LoRA فوق النموذج الحالي ثم ينتج candidate، ويجب أن يجتاز evaluation وregression قبل promotion.
