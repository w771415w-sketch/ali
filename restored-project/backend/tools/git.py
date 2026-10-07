# -*- coding: utf-8 -*-
"""أدوات Git: status, diff, commit.

- git_status: read-only — يعرض حالة الـ repo.
- git_diff:   read-only — يعرض التعديلات.
- git_commit: default — يحتاج إذن صريح.
"""

from __future__ import annotations

import subprocess
from typing import Any

from tools.base import Tool, ToolResult, ToolPermission


def _git(cmd: list, cwd: str, timeout: int = 8) -> dict:
    """تنفيذ git subcommand وإرجاع نتيجة موحدة."""
    try:
        p = subprocess.run(
            ["git"] + cmd,
            cwd=cwd,
            capture_output=True,
            timeout=timeout,
            creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
        )
        return {
            "code": p.returncode,
            "stdout": p.stdout.decode("utf-8", "replace"),
            "stderr": p.stderr.decode("utf-8", "replace"),
        }
    except subprocess.TimeoutExpired:
        return {"code": -2, "stdout": "", "stderr": "git timeout"}
    except FileNotFoundError:
        return {"code": -1, "stdout": "", "stderr": "git not installed"}
    except Exception as e:
        return {"code": -1, "stdout": "", "stderr": str(e)}


class GitStatusTool(Tool):
    name = "git_status"
    description = "يعرض حالة git للـ repo الحالي."
    permission = ToolPermission.READ_ONLY
    input_schema = {"type": "object", "properties": {}}

    def execute(self, ctx: Any, **kwargs: Any) -> ToolResult:
        r = _git(["status", "--short", "--branch"], ctx.project_dir)
        return ToolResult.ok_payload(
            code=r["code"],
            stdout=r["stdout"],
            stderr=r["stderr"],
        )


class GitDiffTool(Tool):
    name = "git_diff"
    description = "يعرض diff للملفات المعدلة."
    permission = ToolPermission.READ_ONLY
    input_schema = {
        "type": "object",
        "properties": {
            "staged": {"type": "boolean"},
        },
    }

    def execute(self, ctx: Any, **kwargs: Any) -> ToolResult:
        args = ["diff"]
        if kwargs.get("staged"):
            args.append("--staged")
        r = _git(args, ctx.project_dir)
        return ToolResult.ok_payload(
            code=r["code"],
            stdout=r["stdout"],
            stderr=r["stderr"],
        )


class GitCommitTool(Tool):
    name = "git_commit"
    description = "عمل commit للتعديلات الحالية."
    permission = ToolPermission.DEFAULT
    input_schema = {
        "type": "object",
        "properties": {
            "message": {"type": "string"},
            "add_all": {"type": "boolean"},
        },
        "required": ["message"],
    }

    def execute(self, ctx: Any, **kwargs: Any) -> ToolResult:
        if ctx.perm_mode == "read-only":
            return ToolResult.fail(
                "read-only mode forbids commit", code="DENIED",
            )
        message = kwargs.get("message", "").strip()
        if not message:
            return ToolResult.fail("commit message is required", code="PARSE")

        steps: list = []
        if kwargs.get("add_all"):
            r = _git(["add", "-A"], ctx.project_dir)
            steps.append(("add", r))
            if r["code"] != 0:
                return ToolResult.fail(
                    "git add failed: " + r["stderr"], code="GIT_ERROR",
                )

        r = _git(["commit", "-m", message], ctx.project_dir)
        steps.append(("commit", r))
        return ToolResult.ok_payload(
            code=r["code"],
            stdout=r["stdout"],
            stderr=r["stderr"],
        )


__all__ = ["GitStatusTool", "GitDiffTool", "GitCommitTool"]
