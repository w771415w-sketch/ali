# ALI Studio Pro 4.4.0 — Adaptive GPU/VRAM Policy

## الهدف
استخدام GPU عندما تكون CUDA قابلة للاستخدام فعلياً، مع الحفاظ على مساحة VRAM للنظام والبرامج الأخرى. لا يعتمد Auto على GPU utilization وحده.

## القرار
1. فحص CUDA عبر `torch.cuda.is_available()`.
2. تنفيذ kernel self-test حقيقي.
3. قراءة free VRAM عبر CUDA/`nvidia-smi`.
4. اختيار workload مناسب للـVRAM.
5. عند عدم كفاية VRAM في Auto يتم التحول إلى CPU.
6. عند إجبار GPU وعدم توفر CUDA أو VRAM كافية يظهر خطأ واضح بدلاً من التحول الصامت إلى CPU.

## ملف تعريف 2GB
- >= 1.35 GB free: sequence 256 / grad accumulation 24
- >= 0.95 GB free: sequence 192 / grad accumulation 32
- >= 0.65 GB free: sequence 128 / grad accumulation 48
- أقل من ذلك: CPU في Auto

Batch size في هذا الملف يبقى 1 لتقليل ذروة VRAM.

## ملاحظة Windows/Maxwell
مسار Windows legacy GPU يستخدم `requirements-windows-legacy-gpu.txt`، بينما Auto runtime لا يختار GPU إلا بعد self-test حقيقي.
