# -*- coding: utf-8 -*-
"""Streaming shell runner used by the Desktop terminal tab.
Security checks are identical to the regular terminal tool."""
from __future__ import annotations
from pathlib import Path
import subprocess
from typing import Iterator
from security.commands import is_command_safe


def stream_command(project_dir: str | Path, command: str, timeout: int = 120) -> Iterator[str]:
    command=command.strip()
    if not command: raise ValueError('command is required')
    if not is_command_safe(command): raise PermissionError('command blocked by safety filter')
    p=subprocess.Popen(command,shell=True,cwd=str(Path(project_dir).resolve()),stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True,encoding='utf-8',errors='replace',bufsize=1,creationflags=getattr(subprocess,'CREATE_NO_WINDOW',0))
    assert p.stdout is not None
    try:
        for line in p.stdout: yield line.rstrip('\n')
        rc=p.wait(timeout=timeout)
    finally:
        if p.poll() is None: p.kill()
    yield f'[exit code: {rc}]'
