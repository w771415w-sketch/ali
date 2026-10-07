# ALI — Executable Runtime Spine (P50)

تمت إضافة طبقة تنفيذية فعلية مرتبطة بمواصفات Lenovo ThinkPad P50:
- Hardware detection and fallback profile
- CPU-first training policy for Quadro M1000M 2 GB
- RAM/thermal/battery/AC admission guards
- Workspace containment and sensitive-path blocking
- Dangerous-command screening
- Permission confirmation semantics
- Agent state/checkpoints and postcondition verification
- Persistent heavy-job admission
- Audit redaction
- Conversation request framing
- Dataset split/metadata validation

الملف canonical للجهاز لا يحتوي UUID/Serial/MAC.

التحقق المحلي:
python -m compileall -q backend
pytest -q backend/tests/test_p50_runtime.py
نتيجة النسخة المحلية: 6/6 passed.

ملاحظة: source-export يبقى المرجع النصي الكامل للمشروع؛ هذه الإضافة تعيد تثبيت النواة التنفيذية الحرجة في شجرة ملفات فعلية ولا تدّعي إعادة بناء كل الـ588 ملفًا القديم دون فحص تشغيل مستقل لكل ملف.
