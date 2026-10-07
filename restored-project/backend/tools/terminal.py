# -*- coding: utf-8 -*-
"""أداة Terminal: run_shell.

تحترم قواعد الأمان:
- في default: لا تنفّذ الأوامر الخطيرة (rm -rf /, format, del /f /q C:\\...).
- في read-only: ترفض كل تنفيذ.
- timeout صارم.
- لا تطبع tokens في الـ logs.
"""

from __future__ import annotations

import os
import subprocess
from typing import Any

from tools.base import Tool, ToolResult, ToolPermission
from security.commands import is_command_safe


# Allowed في كل الأوضاع (whitelist للـ shell commands الآمنة جداً).
SHELL_PREFIX = ""


class RunShellTool(Tool):
    name = "run_command"
    description = "تنفيذ أمر shell داخل workspace. يحتاج إذن صريح."
    permission = ToolPermission.DEFAULT
    input_schema = {
        "type": "object",
        "properties": {
            "command": {"type": "string", "description": "الأمر الكامل"},
            "timeout": {"type": "integer", "description": "مهلة بالثواني"},
        },
        "required": ["command"],
    }

    DEFAULT_TIMEOUT = 10
    MAX_TIMEOUT = 120

    def execute(self, ctx: Any, **kwargs: Any) -> ToolResult:
        # read-only: رفض كامل
        if ctx.perm_mode == "read-only":
            return ToolResult.fail(
                "read-only mode forbids shell execution",
                code="DENIED",
            )

        cmd = kwargs.get("command", "").strip()
        if not cmd:
            return ToolResult.fail("command is required", code="PARSE")

        # فحص القوائم السوداء للأنماط الخطيرة حتى في default.
        if not is_command_safe(cmd):
            return ToolResult.fail(
                "command blocked by safety filter (matches dangerous pattern)",
                code="DENIED",
            )

        timeout = int(kwargs.get("timeout", self.DEFAULT_TIMEOUT))
        timeout = max(1, min(timeout, self.MAX_TIMEOUT))

        try:
            p = subprocess.run(
                cmd,
                shell=True,
                cwd=ctx.project_dir,
                capture_output=True,
                timeout=timeout,
                creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
            )
            return ToolResult.ok_payload(
                code=p.returncode,
                stdout=p.stdout.decode("utf-8", "replace"),
                stderr=p.stderr.decode("utf-8", "replace"),
                timeout=timeout,
            )
        except subprocess.TimeoutExpired:
            return ToolResult.fail(
                f"command timed out after {timeout}s", code="TIMEOUT",
            )
        except Exception as e:
            return ToolResult.fail(str(e), code="IO_ERROR")


__all__ = ["RunShellTool", "SHELL_PREFIX"]
