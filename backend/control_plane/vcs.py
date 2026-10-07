from __future__ import annotations
import subprocess
from pathlib import Path
class GitRepo:
    def __init__(self,root):self.root=Path(root).resolve()
    def _run(self,args):return subprocess.run(["git",*args],cwd=self.root,capture_output=True,text=True)
    def available(self):return self._run(["--version"]).returncode==0
    def is_repo(self):return (self.root/".git").exists()
    def status(self):r=self._run(["status","--short"]);return {"ok":r.returncode==0,"stdout":r.stdout,"stderr":r.stderr}
    def diff(self):r=self._run(["diff","--"]);return {"ok":r.returncode==0,"stdout":r.stdout,"stderr":r.stderr}
    def head(self):r=self._run(["rev-parse","HEAD"]);return r.stdout.strip() if r.returncode==0 else None
    def checkpoint_commit(self,message,approved=False):
        if not approved:return {"ok":False,"error":"approval_required"}
        if not self.is_repo():return {"ok":False,"error":"not_a_git_repository"}
        a=self._run(["add","-A"]); 
        if a.returncode!=0:return {"ok":False,"error":a.stderr}
        c=self._run(["commit","-m",message]);return {"ok":c.returncode==0,"commit":self.head(),"stdout":c.stdout,"stderr":c.stderr}
    def rollback(self,commit,approved=False):
        if not approved:return {"ok":False,"error":"approval_required"}
        if not self.is_repo():return {"ok":False,"error":"not_a_git_repository"}
        r=self._run(["reset","--hard",commit]);return {"ok":r.returncode==0,"stdout":r.stdout,"stderr":r.stderr}