# -*- coding: utf-8 -*-
"""security/__init__.py — حزمة Security.

- paths: حماية مسارات الملفات (workspace containment).
- commands: فلتر الأوامر الخطيرة.
- permissions: PermissionManager — يربط بين perm_mode والـ tool permission.
"""

from security.paths import safe_project_path
from security.commands import is_command_safe
from security.permissions import (
    PermissionManager, Decision, get_permission_manager,
)

__all__ = [
    "safe_project_path",
    "is_command_safe",
    "PermissionManager", "Decision", "get_permission_manager",
]
