# ALI Training Update v1 — Evaluation Report

## Dataset
- Train: 394
- Validation: 55
- Test: 55

## Training
- Base: ALI-Bootstrap-v2.5
- Stage: LoRA
- Rank: 16
- Alpha: 32
- Max steps: 200
- Sequence length: 96
- Device used for this artifact: CPU
- Merged LoRA layers: 28

## Metrics
Baseline validation loss: 7.428376
V1 validation loss: 7.074097
Baseline test loss: 7.467803
V1 test loss: 7.085154

Validation loss improvement: 4.77%
Test loss improvement: 5.12%

## Important limitation
هذا تحسن في سلوك النموذج على مجموعة التحديث، لكنه ليس دليلاً على أن النموذج أصبح مساعداً عاماً قوياً. النموذج الأساسي صغير جداً، وتنفيذ المشاريع فعلياً يعتمد على Agent + Tools + RAG + Runtime.

## Promotion recommendation
استخدم `merged_hf` كـCandidate. لا تجعل v1 Active إلا بعد تشغيل اختبارات النظام الكاملة على Windows واختبار مهام حقيقية داخل مشروعك.
