# تشغيل ALI Studio Pro — طبقة التشغيل الاحترافية

هذه الحزمة لا تستبدل `backend/` أو `restored-project/`. هي طبقة تشغيل موحّدة تجعل تلك المكوّنات قابلة للفحص من مكان واحد، وتضع حدودًا واضحة بين التخطيط والتنفيذ.

## Windows / ThinkPad P50

الملف الشخصي المضمن هو CPU-first للتدريب الثقيل: 8 خيوط CPU، ترك 2 خيط للنظام، حد 6 خيوط تدريب، مهمة ثقيلة واحدة، واشتراط طاقة AC. بطاقة Quadro M1000M ذات 2 GB تعامل كـ optional inference offload وليست هدف تدريب ثقيل.

ابدأ بفحص النظام:

```powershell
python ALI\run.py doctor
python ALI\run.py health
python ALI\self_check.py
python -m unittest discover -s ALI\tests -p "test_*.py"
```

لبدء API محلي:

```powershell
python ALI\run.py serve
```

يستمع افتراضيًا على `127.0.0.1:8787`. الوصول البعيد لا يُفعل دون رمز Bearer صريح.

لتشغيل الواجهة الحالية:

```cmd
ALI\desktop\launch.cmd dev
```

## حدود التنفيذ

طلبات تغيير الملفات لا تنفذ مباشرةً من دون `approved=true`. الوضع `dry_run` للتخطيط فقط. كل طلب تنفيذي يمر عبر idempotency + audit + الـControl Plane الموجود أصلًا.

لا تعتبر هذه الملفات دليلًا على أن Electron أو نموذج GGUF أو تدريب LoRA الحقيقي قد نُفّذ على جهاز Windows فعلي. مهمة `doctor` تعرض الحالة الفعلية للمستودع، وتبقي البوابات غير المثبتة واضحة.
