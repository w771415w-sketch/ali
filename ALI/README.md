# ALI Studio Pro — Professional Runtime Suite

هذه مجلد الإضافة الاحترافية الموحدة للمشروع `w771415w-sketch/ali`.

الهدف ليس نسخ المصدر التاريخي الضخم داخل مجلد جديد، بل إضافة طبقة تشغيل حقيقية فوق ما هو موجود بالفعل: API محلي آمن، orchestrator، حماية مسارات، idempotency، audit، health، doctor، اختبارات مستقلة، وLauncher للواجهة الحالية.

## ما الذي تمت إضافته؟

- `core/config.py`: إعدادات Windows/Linux عبر ملفات JSON ومتغيرات بيئة.
- `core/security.py`: Bearer auth، rate limiting، ومنع path traversal.
- `core/storage.py`: SQLite/WAL للـidempotency وaudit.
- `core/contracts.py`: عقود صارمة للطلبات والعمليات.
- `core/orchestrator.py`: نقطة الدخول الموحدة بين CLI/API والـControl Plane الحالي.
- `integrations/control_plane.py`: تكامل Lazy مع `backend.control_plane.runtime_facade.ProfessionalRuntime`.
- `api/server.py`: JSON API loopback-first مع حدود حجم الطلب والمصادقة.
- `ops/doctor.py`: كشف حالة المشروع والبوابات الأصلية غير المثبتة.
- `desktop/launch.ps1` + `launch.cmd`: تشغيل واجهة Electron الحالية.
- `tests/`: اختبارات مستقلة لا تعتمد على pytest أو حزم خارجية.

## التشغيل

```powershell
python ALI\run.py doctor
python ALI\run.py health
python ALI\self_check.py
python -m unittest discover -s ALI\tests -p "test_*.py"
```

API:

```powershell
python ALI\run.py serve
```

واجهة سطح المكتب:

```cmd
ALI\desktop\launch.cmd dev
```

## مبدأ الصدق التشغيلي

الطبقة الجديدة لا تعتبر أي ميزة “مكتملة” لمجرد وجود ملف يوثقها. إذا تعذر استيراد الـControl Plane أو لم توجد تبعيات Electron أو ملفات الإصدار الفعلي، تظهر الحالة كـpending/degraded بدل إعطاء نجاح وهمي.

للتفاصيل التشغيلية والأمنية راجع `OPERATIONS.md` و`SECURITY.md` و`ARCHITECTURE.md`.
