# -*- coding: utf-8 -*-
"""ToolRegistry — تسجيل + تشغيل الأدوات.

- Singleton (get_registry).
- يأخذ Tool instances أو classes.
- يشغّل بعد التحقق من PermissionManager (يُحقن عبر configure).
- يسجّل كل استدعاء في LogRepo (للـ audit).
"""

from __future__ import annotations

import re
import logging
from typing import Any, Dict, List, Optional, Type, Union

from tools.base import Tool, ToolPermission, ToolResult

log = logging.getLogger("ali.tools")


class ToolRegistry:
    def __init__(self) -> None:
        self._tools: Dict[str, Tool] = {}
        self._permission_manager: Optional[Any] = None
        self._audit_logger: Optional[Any] = None   # callable(event_dict)

    # ------------------------------------------------------------ registration
    def register(self, tool_or_cls: Union[Tool, Type[Tool]]) -> None:
        """تسجيل Tool instance أو class."""
        t = tool_or_cls if isinstance(tool_or_cls, Tool) else tool_or_cls()
        if not t.name:
            raise ValueError("Tool.name is required")
        if t.name in self._tools:
            raise ValueError("duplicate tool: " + t.name)
        self._tools[t.name] = t
        log.info("Tool registered: %s (perm=%s)", t.name, t.permission.value)

    def all(self) -> Dict[str, Tool]:
        return dict(self._tools)

    def names(self) -> List[str]:
        return sorted(self._tools.keys())

    def get(self, name: str) -> Optional[Tool]:
        return self._tools.get(name)

    # ------------------------------------------------------------ injection
    def set_permission_manager(self, pm: Any) -> None:
        """حقن PermissionManager (security/permissions.py)."""
        self._permission_manager = pm

    def set_audit_logger(self, fn) -> None:
        """حقن دالة استدعاء tool audit (event_dict) -> None."""
        self._audit_logger = fn

    # ------------------------------------------------------------ execution
    def _audit_kwargs(self, kwargs: Dict[str, Any]) -> Dict[str, Any]:
        """Return a log-safe copy of tool arguments."""
        sensitive = re.compile(
            r"(?:password|passwd|secret|token|api[_-]?key|authorization|cookie)",
            re.I,
        )
        safe: Dict[str, Any] = {}
        for key, value in kwargs.items():
            if sensitive.search(str(key)):
                safe[key] = "[REDACTED]"
            elif key == "command" and isinstance(value, str):
                # Avoid recording obvious inline credentials in shell commands.
                redacted = re.sub(
                    r"(?i)(bearer\s+)[A-Za-z0-9._~+/=-]+",
                    r"\1[REDACTED]",
                    value,
                )
                redacted = re.sub(
                    r"(?i)(--?(?:password|token|api[-_]?key|secret)=)\S+",
                    r"\1[REDACTED]",
                    redacted,
                )
                safe[key] = redacted
            else:
                safe[key] = value
        return safe

    def execute(self, name: str, ctx: Any, **kwargs: Any) -> ToolResult:
        """تنفيذ الأداة بعد فحص الصلاحيات والـ input."""
        tool = self._tools.get(name)
        if tool is None:
            return ToolResult.fail("unknown tool: " + name, code="UNKNOWN_TOOL")

        err = tool.validate_input(kwargs)
        if err:
            result = ToolResult.fail(err, code="PARSE")
            self._audit(name, kwargs, result)
            return result

        if self._permission_manager is not None:
            decision = self._permission_manager.check(
                user=None, tool_name=name,
                permission=tool.permission, ctx=ctx, kwargs=kwargs,
            )
            if not decision.allowed:
                result = ToolResult.fail(
                    "permission denied: " + (decision.reason or ""),
                    code="DENIED",
                )
                self._audit(name, kwargs, result)
                return result

        try:
            result = tool.execute(ctx, **kwargs)
        except Exception as e:
            log.exception("Tool %s raised: %s", name, e)
            result = ToolResult.fail(str(e), code="INTERNAL")

        self._audit(name, kwargs, result)
        return result

    def _audit(self, name: str, kwargs: Dict[str, Any], result: ToolResult) -> None:
        if self._audit_logger is None:
            return
        try:
            self._audit_logger({
                "tool": name,
                "kwargs": self._audit_kwargs(kwargs),
                "ok": result.ok,
                "error_code": result.error_code,
            })
        except Exception:
            # Audit failures must never break tool execution.
            pass
    def default_set(self) -> List[Union[Tool, Type[Tool]]]:
        """القائمة الافتراضية للأدوات المسجّلة عند البدء."""
        from tools.filesystem import (
            ReadFileTool, ListDirTool, WriteFileTool, SearchFilesTool,
        )
        from tools.terminal import RunShellTool
        from tools.git import GitStatusTool, GitDiffTool, GitCommitTool
        from tools.project import CreateProjectTool
        from tools.web import WebResearchTool
        return [
            ReadFileTool, ListDirTool, WriteFileTool, SearchFilesTool,
            RunShellTool, CreateProjectTool, WebResearchTool,
            GitStatusTool, GitDiffTool, GitCommitTool,
        ]


_REGISTRY_SINGLETON: Optional[ToolRegistry] = None


def get_registry() -> ToolRegistry:
    global _REGISTRY_SINGLETON
    if _REGISTRY_SINGLETON is None:
        reg = ToolRegistry()
        for t in reg.default_set():
            reg.register(t)
        _REGISTRY_SINGLETON = reg
    return _REGISTRY_SINGLETON


def reset_registry_for_tests() -> None:
    """إعادة تعيين الـ singleton (للاختبارات فقط)."""
    global _REGISTRY_SINGLETON
    _REGISTRY_SINGLETON = None


__all__ = ["ToolRegistry", "get_registry", "reset_registry_for_tests"]
