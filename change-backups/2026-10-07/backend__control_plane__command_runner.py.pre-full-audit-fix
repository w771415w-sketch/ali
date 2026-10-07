from __future__
import os, subprocess, time
from dataclasses import dataclass
from .policy import Policy

@dataclass
class CommandResult:
    command: str
    returncode: int
    stdout: str
    stderr: str
    elapsed_s: float
    timed_out: bool=False
    cancelled: bool=False
    def to_dict(self): return self.__dict__.copy()

class CommandRunner:
    def __init__(self,workspace,policy=None):
        self.workspace=workspace; self.policy=policy or Policy(workspace)
    def run(self,command,approved=False,timeout_s=60,env=None,cwd=None):
        if not approved: return CommandResult(command,-126,"","approval required",0.0)
        if not self.policy.command_allowed(command): return CommandResult(command,-127,"","blocked by safety policy",0.0)
        start=time.time(); run_cwd=self.policy.workspace if cwd is None else self.policy.workspace/cwd
        run_cwd=run_cwd.resolve()
        if not self.policy.path_allowed(run_cwd): return CommandResult(command,-128,"","cwd outside workspace",0.0)
        try:
            proc=subprocess.run(command,shell=True,cwd=str(run_cwd),env={**os.environ,**(env or {})},capture_output=True,text=True,timeout=float(timeout_s))
            return CommandResult(command,proc.returncode,proc.stdout,proc.stderr,time.time()-start)
        except subprocess.TimeoutExpired as e:
            return CommandResult(command,124,e.stdout or "",e.stderr or "",time.time()-start,timed_out=True)
