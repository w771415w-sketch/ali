# -*- coding: utf-8 -*-
"""tools/__init__.py — حزمة Tools.

تعريض الـ Registry كأهم عنصر عام.
"""

from tools.base import Tool, ToolResult, ToolPermission
from tools.registry import ToolRegistry, get_registry
from tools.filesystem import (
    ReadFileTool, ListDirTool, WriteFileTool, SearchFilesTool,
)
from tools.terminal import RunShellTool
from tools.git import GitStatusTool, GitDiffTool, GitCommitTool

__all__ = [
    "Tool", "ToolResult", "ToolPermission",
    "ToolRegistry", "get_registry",
    "ReadFileTool", "ListDirTool", "WriteFileTool", "SearchFilesTool",
    "RunShellTool",
    "GitStatusTool", "GitDiffTool", "GitCommitTool",
]
