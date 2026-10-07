# -*- coding: utf-8 -*-
"""أدوات Filesystem: read_file, list_dir, write_file, search_files.

تحترم حدود الـ project_dir (workspace). أي محاولة للخروج تُرفض بـ PATH_BLOCKED.
"""

from __future__ import annotations

import os
import re
from pathlib import Path
from typing import Any, List

from tools.base import Tool, ToolResult, ToolPermission
from security.paths import safe_project_path


# حد أقصى لقراءة ملف — يحمي من OOM على ملفات ضخمة.
MAX_FILE_BYTES = 2 * 1024 * 1024    # 2 MiB
MAX_LIST_ENTRIES = 1000
MAX_SEARCH_RESULTS = 200


class ReadFileTool(Tool):
    name = "read_file"
    description = "قراءة محتوى ملف داخل workspace."
    permission = ToolPermission.READ_ONLY
    input_schema = {
        "type": "object",
        "properties": {
            "path": {"type": "string", "description": "مسار نسبي للملف"},
            "max_bytes": {"type": "integer", "description": "حد أقصى للقراءة"},
        },
        "required": ["path"],
    }

    def execute(self, ctx: Any, **kwargs: Any) -> ToolResult:
        rel = kwargs.get("path", "")
        if not rel:
            return ToolResult.fail("path is required", code="PARSE")
        try:
            resolved = safe_project_path(ctx.project_dir, rel)
        except PermissionError as e:
            return ToolResult.fail(str(e), code="PATH_BLOCKED")

        if not resolved.exists():
            return ToolResult.fail("file not found: " + str(resolved),
                                    code="NOT_FOUND")
        if not resolved.is_file():
            return ToolResult.fail("not a file: " + str(resolved),
                                    code="NOT_A_FILE")

        limit = int(kwargs.get("max_bytes", MAX_FILE_BYTES))
        try:
            size = resolved.stat().st_size
            with open(resolved, "rb") as f:
                raw = f.read(limit + 1)
            truncated = len(raw) > limit
            if truncated:
                raw = raw[:limit]
            try:
                text = raw.decode("utf-8")
            except UnicodeDecodeError:
                text = raw.decode("utf-8", "replace")
            return ToolResult.ok_payload(
                path=str(resolved),
                content=text,
                size=size,
                truncated=truncated,
                bytes_read=len(raw),
            )
        except OSError as e:
            return ToolResult.fail(str(e), code="IO_ERROR")


class ListDirTool(Tool):
    name = "list_dir"
    description = "سرد محتويات مجلد داخل workspace."
    permission = ToolPermission.READ_ONLY
    input_schema = {
        "type": "object",
        "properties": {
            "path": {"type": "string", "description": "مسار نسبي للمجلد"},
        },
        "required": [],
    }

    def execute(self, ctx: Any, **kwargs: Any) -> ToolResult:
        rel = kwargs.get("path", "")
        try:
            resolved = safe_project_path(ctx.project_dir, rel)
        except PermissionError as e:
            return ToolResult.fail(str(e), code="PATH_BLOCKED")
        if not resolved.exists():
            return ToolResult.fail("not found: " + str(resolved),
                                    code="NOT_FOUND")
        if not resolved.is_dir():
            return ToolResult.fail("not a directory: " + str(resolved),
                                    code="NOT_A_DIR")

        try:
            entries: List[dict] = []
            for p in sorted(resolved.iterdir()):
                if len(entries) >= MAX_LIST_ENTRIES:
                    break
                st = p.stat()
                entries.append({
                    "name": p.name,
                    "is_dir": p.is_dir(),
                    "size": st.st_size,
                })
            return ToolResult.ok_payload(
                path=str(resolved),
                entries=entries,
                truncated=len(entries) >= MAX_LIST_ENTRIES,
            )
        except OSError as e:
            return ToolResult.fail(str(e), code="IO_ERROR")


class WriteFileTool(Tool):
    """كتابة ملف كامل (overwrite). يحتاج Permission DEFAULT+."""
    name = "write_file"
    description = "كتابة ملف داخل workspace (يستبدل المحتوى)."
    permission = ToolPermission.DEFAULT
    input_schema = {
        "type": "object",
        "properties": {
            "path": {"type": "string", "description": "مسار نسبي للملف"},
            "content": {"type": "string", "description": "المحتوى الكامل"},
        },
        "required": ["path", "content"],
    }

    def execute(self, ctx: Any, **kwargs: Any) -> ToolResult:
        rel = kwargs.get("path", "")
        content = kwargs.get("content", "")
        if not rel:
            return ToolResult.fail("path is required", code="PARSE")
        try:
            resolved = safe_project_path(ctx.project_dir, rel)
        except PermissionError as e:
            return ToolResult.fail(str(e), code="PATH_BLOCKED")
        try:
            resolved.parent.mkdir(parents=True, exist_ok=True)
            with open(resolved, "w", encoding="utf-8", newline="") as f:
                f.write(content)
            return ToolResult.ok_payload(path=str(resolved),
                                         bytes_written=len(content.encode("utf-8")))
        except OSError as e:
            return ToolResult.fail(str(e), code="IO_ERROR")


class SearchFilesTool(Tool):
    """بحث regex داخل ملفات المشروع."""
    name = "search_files"
    description = "بحث regex داخل الملفات النصية داخل workspace."
    permission = ToolPermission.READ_ONLY
    input_schema = {
        "type": "object",
        "properties": {
            "pattern": {"type": "string", "description": "regex pattern"},
            "path": {"type": "string", "description": "مجلد بداية (نسبي)"},
        },
        "required": ["pattern"],
    }

    _SKIP_DIRS = {".git", "__pycache__", "node_modules", ".venv", "venv",
                  "checkpoints", "weights", ".pytest_cache"}

    def execute(self, ctx: Any, **kwargs: Any) -> ToolResult:
        pattern = kwargs.get("pattern", "")
        rel = kwargs.get("path", "")
        if not pattern:
            return ToolResult.fail("pattern is required", code="PARSE")
        try:
            rx = re.compile(pattern)
        except re.error as e:
            return ToolResult.fail("invalid regex: " + str(e), code="PARSE")
        try:
            base = safe_project_path(ctx.project_dir, rel)
        except PermissionError as e:
            return ToolResult.fail(str(e), code="PATH_BLOCKED")

        results: List[dict] = []
        try:
            for root, dirs, files in os.walk(base):
                # prune skip-dirs
                dirs[:] = [d for d in dirs if d not in self._SKIP_DIRS]
                for fn in files:
                    if len(results) >= MAX_SEARCH_RESULTS:
                        break
                    p = Path(root) / fn
                    try:
                        if p.stat().st_size > MAX_FILE_BYTES:
                            continue
                    except OSError:
                        continue
                    try:
                        with open(p, "r", encoding="utf-8",
                                  errors="replace") as f:
                            for ln, line in enumerate(f, 1):
                                if rx.search(line):
                                    results.append({
                                        "path": str(p),
                                        "line": ln,
                                        "text": line.rstrip(),
                                    })
                                    if len(results) >= MAX_SEARCH_RESULTS:
                                        break
                    except (OSError, UnicodeDecodeError):
                        continue
                if len(results) >= MAX_SEARCH_RESULTS:
                    break
            return ToolResult.ok_payload(
                pattern=pattern,
                matches=results,
                truncated=len(results) >= MAX_SEARCH_RESULTS,
            )
        except Exception as e:
            return ToolResult.fail(str(e), code="IO_ERROR")


__all__ = ["ReadFileTool", "ListDirTool", "WriteFileTool", "SearchFilesTool"]
