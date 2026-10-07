# -*- coding: utf-8 -*-
"""Small deterministic bilingual UI dictionary. Runtime content remains model-generated."""
from __future__ import annotations

TEXT = {
    "ar": {
        "app_subtitle": "المساعد الذكي المحلي الاحترافي", "professional": "الوضع الاحترافي", "auto": "تلقائي (ذكي)",
        "connected": "متصل", "offline": "محلي · دون اتصال أولاً", "auto_learn": "التعلم الذاتي",
        "new_chat": "محادثة جديدة", "conversations": "المحادثات", "projects": "المشاريع", "files": "الملفات",
        "memory": "الذاكرة", "tools": "الأدوات", "web": "البحث والويب", "models": "النماذج", "datasets": "البيانات والتدريب",
        "settings": "الإعدادات", "overview": "نظرة عامة", "editor": "المحرر", "terminal": "الطرفية", "jobs": "المهام",
        "health": "الصحة", "sources": "المصادر", "context": "السياق", "send": "إرسال", "stop": "إيقاف", "ready": "جاهز",
        "open_project": "فتح مشروع", "doctor": "فحص النظام", "train": "تدريب", "self_learn": "تعلم ذاتي", "refresh": "تحديث",
        "analyze": "تحليل المشروع", "check_device": "فحص الجهاز", "inspect_model": "فحص النموذج", "train_tokenizer": "تدريب Tokenizer",
        "import_weights": "استيراد الأوزان", "write_here": "اكتب سؤالك هنا...", "copy": "نسخ", "system_health": "حالة النظام",
        "battery": "البطارية", "activity": "النشاط الحالي", "current_context": "السياق الحالي", "model": "النموذج",
        "cpu": "المعالج", "gpu": "GPU", "ram": "الذاكرة", "temp": "الحرارة", "disk": "التخزين",
        "language": "اللغة", "arabic": "العربية", "english": "English", "training_files": "ملفات التدريب",
    },
    "en": {
        "app_subtitle": "Professional Local AI Assistant", "professional": "Professional Mode", "auto": "Auto (Smart)",
        "connected": "Connected", "offline": "Local · Offline-first", "auto_learn": "Self Learning",
        "new_chat": "New conversation", "conversations": "Conversations", "projects": "Projects", "files": "Files",
        "memory": "Memory", "tools": "Tools", "web": "Web Research", "models": "Models", "datasets": "Data & Training",
        "settings": "Settings", "overview": "Overview", "editor": "Editor", "terminal": "Terminal", "jobs": "Jobs",
        "health": "Health", "sources": "Sources", "context": "Context", "send": "Send", "stop": "Stop", "ready": "Ready",
        "open_project": "Open Project", "doctor": "System Check", "train": "Train", "self_learn": "Self Learn", "refresh": "Refresh",
        "analyze": "Analyze project", "check_device": "Check device", "inspect_model": "Inspect model", "train_tokenizer": "Train tokenizer",
        "import_weights": "Import weights", "write_here": "Write your question here...", "copy": "Copy", "system_health": "System health",
        "battery": "Battery", "activity": "Current activity", "current_context": "Current context", "model": "Model",
        "cpu": "CPU", "gpu": "GPU", "ram": "RAM", "temp": "Temperature", "disk": "Storage",
        "language": "Language", "arabic": "العربية", "english": "English", "training_files": "Training files",
    },
}

def normalize_language(value: str | None) -> str:
    return "ar" if str(value or "").lower().split("-")[0] == "ar" else "en"

def tr(key: str, language: str = "ar") -> str:
    lang=normalize_language(language)
    return TEXT.get(lang, TEXT["ar"]).get(key, key)

def is_rtl(language: str) -> bool:
    return normalize_language(language) == "ar"
