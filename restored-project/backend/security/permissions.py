# -*- coding: utf-8 -*-
"""PermissionManager — Backend الحقيقي للصلاحيات.

القرارات:
- read-only: قراءة فقط. أي شيء >= DEFAULT مرفوض.
- default:   Tool بصلاحية read-only مسموح. >= DEFAULT يحتاج موافقة المستخدم
             (Ask) — الـ UI يحصل على dialog. القرار يُسجَّل في always_allow
             لتفادي تكرار السؤال.
- full-access: كل الأدوات مسموحة تلقائياً.

الـ Manager غير مرتبط بـ UI. الـ UI تستدعي `ask_user(...)` فقط عندما
يكون القرار "ask"، وإذا وافق المستخدم تستدعي `grant(tool_name, session=True)`.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List, Optional


class PermMode(str, Enum):
    READ_ONLY = "read-only"
    DEFAULT = "default"
    FULL_ACCESS = "full-access"


# ترتيب الصلاحيات (أدنى → أعلى).
_PERM_RANK = {
    PermMode.READ_ONLY.value:    0,
    PermMode.DEFAULT.value:      1,
    PermMode.FULL_ACCESS.value:  2,
}


@dataclass
class Decision:
    allowed: bool
    reason: str = ""
    needs_ask: bool = False       # True = الواجهة يجب أن تسأل المستخدم

    @staticmethod
    def allow(reason: str = "") -> "Decision":
        return Decision(allowed=True, reason=reason, needs_ask=False)

    @staticmethod
    def deny(reason: str) -> "Decision":
        return Decision(allowed=False, reason=reason, needs_ask=False)

    @staticmethod
    def ask(reason: str) -> "Decision":
        return Decision(allowed=False, reason=reason, needs_ask=True)


class PermissionManager:
    """Backend للصلاحيات — يفحص كل طلب tool.

    الاستخدام:
        pm = PermissionManager(mode="default")
        decision = pm.check(tool_name="write_file", permission=DEFAULT, ...)
        if decision.needs_ask:
            ... dialog ...
            if user_says_yes:
                pm.grant("write_file", session=True)
                # ثم استدعِ check مرة أخرى أو سمّ بالتنفيذ مباشرة.
    """

    def __init__(self, mode: str = "default",
                 always_allow: Optional[List[str]] = None) -> None:
        self.set_mode(mode)
        self._always_allow: set = set(always_allow or [])

    # ------------------------------------------------------------ config
    def set_mode(self, mode: str) -> None:
        if mode not in _PERM_RANK:
            raise ValueError("invalid mode: " + mode)
        self.mode = mode

    def grant(self, tool_name: str, session: bool = True) -> None:
        """إضافة أداة إلى الاستثناءات الحالية.

        لا تلغي هذه القائمة وضع read-only؛ الانتقال إلى read-only يجب أن
        يبقى حاجزاً نهائياً حتى لو مُنحت الأداة سابقاً.
        """
        self._always_allow.add(tool_name)

    def revoke(self, tool_name: str) -> None:
        self._always_allow.discard(tool_name)

    def always_allow_snapshot(self) -> List[str]:
        return sorted(self._always_allow)

    # ------------------------------------------------------------ core
    def check(self, *, tool_name: str, permission: Any,
              ctx: Any = None, kwargs: Optional[Dict[str, Any]] = None,
              user: Any = None) -> Decision:
        """يرجع القرار النهائي لطلب تشغيل الأداة."""
        effective_mode = self.mode
        if ctx is not None and getattr(ctx, "perm_mode", None):
            effective_mode = ctx.perm_mode

        if effective_mode not in _PERM_RANK:
            return Decision.deny(f"invalid permission mode: {effective_mode}")

        permission_value = (
            permission.value if hasattr(permission, "value") else str(permission)
        )
        if permission_value not in _PERM_RANK:
            return Decision.deny(
                f"invalid tool permission: {permission_value}"
            )

        tool_rank = _PERM_RANK[permission_value]
        user_rank = _PERM_RANK[effective_mode]

        # read-only is an absolute boundary and cannot be bypassed by grants.
        if effective_mode == PermMode.READ_ONLY.value and tool_rank > user_rank:
            return Decision.deny(
                f"read-only mode forbids '{tool_name}' "
                f"(requires '{permission_value}')"
            )

        # Explicitly granted tools are allowed only after the hard boundary above.
        if tool_name in self._always_allow:
            return Decision.allow("always_allow")

        if effective_mode == PermMode.FULL_ACCESS.value:
            return Decision.allow("full-access")

        if permission_value == PermMode.READ_ONLY.value:
            return Decision.allow("mode permits")

        # In default mode, DEFAULT and FULL_ACCESS actions require an explicit
        # user approval unless that tool was granted for the session.
        return Decision.ask(
            f"tool '{tool_name}' requires '{permission_value}' "
            f"and current mode is '{effective_mode}'"
        )

# Singleton helper (اختياري — يمكن إنشاء instance محلي أيضاً).
_PM_SINGLETON: Optional[PermissionManager] = None


def get_permission_manager(mode: str = "default") -> PermissionManager:
    global _PM_SINGLETON
    if _PM_SINGLETON is None:
        _PM_SINGLETON = PermissionManager(mode=mode)
    return _PM_SINGLETON


def reset_permission_manager_for_tests() -> None:
    global _PM_SINGLETON
    _PM_SINGLETON = None


__all__ = [
    "PermMode", "Decision", "PermissionManager",
    "get_permission_manager", "reset_permission_manager_for_tests",
]
