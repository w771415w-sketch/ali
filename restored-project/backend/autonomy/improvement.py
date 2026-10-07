# -*- coding: utf-8 -*-
"""Controlled self-improvement loop.

The agent may inspect code, prepare a patch, run tests and evaluate a candidate,
but the final promotion gate is explicit and auditable. No arbitrary self-execution.
"""
from __future__ import annotations
from pathlib import Path
import subprocess, json, time
from typing import Dict,Any

class ImprovementLoop:
    def __init__(self, project: str|Path): self.project=Path(project).resolve()
    def run_tests(self, timeout=900)->Dict[str,Any]:
        cmd=['python','-m','pytest','tests','-q']
        try:
            p=subprocess.run(cmd,cwd=self.project,capture_output=True,text=True,timeout=timeout)
            return {'passed':p.returncode==0,'code':p.returncode,'stdout':p.stdout[-12000:],'stderr':p.stderr[-12000:]}
        except Exception as e: return {'passed':False,'code':-1,'stdout':'','stderr':str(e)}
    def inspect(self)->Dict[str,Any]:
        files=[str(p.relative_to(self.project)) for p in self.project.rglob('*') if p.is_file() and not any(x in p.parts for x in ('.git','.venv','__pycache__'))]
        return {'files':files,'count':len(files)}
    def propose_prompt(self, goal:str, test_report:Dict[str,Any])->str:
        return f"You are ALI's software improvement planner. Goal: {goal}\nTest report:\n{test_report}\nReturn a minimal patch plan, risks, files, and validation steps. Do not assume hidden APIs."
    def snapshot(self)->Dict[str,Any]:
        return self.inspect()
