# -*- coding: utf-8 -*-
"""أدوات ALI Studio — الطبقة الأساسية.

كل Tool يجب أن يملك:
- name: اسم مميز (snake_case)
- description: وصف مختصر
- permission: مستوى الصلاحية (read-only / default / full-access)
- input_schema: dict يصف المعاملات (للـ UI / Agent)
- execute(ctx, **kwargs) -> ToolResult

الـ ToolResult يحتوي:
- ok: bool
- data: dict (output منظم)
- error: str | None
- error_code: str | None (PARSE / PATH_BLOCKED / IO_ERROR / DENIED ...)

لا يحتوي Tool على منطق permission check — ذلك مسؤولية PermissionManager
في security/permissions.py (يُحقن في الـ Registry).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, Optional


class ToolPermission(str, Enum):
    """مستوى الصلاحية المطلوب لتشغيل الأداة."""
    READ_ONLY = "read-only"        # قراءة فقط
    DEFAULT = "default"            # كتابة/تعديل يحتاج إذن المستخدم
    FULL_ACCESS = "full-access"    # تعديل/حذف يحتاج full-access


@dataclass
class ToolResult:
    """نتيجة موحدة من تنفيذ أي أداة."""
    ok: bool
    data: Dict[str, Any] = field(default_factory=dict)
    error: Optional[str] = None
    error_code: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "ok": self.ok,
            "data": self.data,
            "error": self.error,
            "error_code": self.error_code,
        }

    @staticmethod
    def ok_payload(**data: Any) -> "ToolResult":
        return ToolResult(ok=True, data=data)

    @staticmethod
    def fail(error: str, code: str = "ERROR", **data: Any) -> "ToolResult":
        return ToolResult(ok=False, data=data, error=error, error_code=code)


class Tool:
    """الفئة الأساسية للأداة. تُورث منها كل أداة."""
    name: str = ""
    description: str = ""
    permission: ToolPermission = ToolPermission.READ_ONLY
    input_schema: Dict[str, Any] = {}

    def execute(self, ctx: Any, **kwargs: Any) -> ToolResult:
        """يجب أن يُنفّذ في subclasses."""
        raise NotImplementedError

    # اختياري: فحص الـ input قبل التنفيذ.
    def validate_input(self, kwargs: Dict[str, Any]) -> Optional[str]:
        """يرجع None إذا الـ input سليم، أو رسالة خطأ."""
        return None


__all__ = ["Tool", "ToolResult", "ToolPermission"]
