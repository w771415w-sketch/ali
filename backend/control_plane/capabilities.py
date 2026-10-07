from __future__ import annotations
import os, platform, shutil, sys

class CapabilityInspector:
    def inspect(self):
        return {"os":platform.platform(),"python":sys.version.split()[0],"git":shutil.which("git"),"node":shutil.which("node"),"npm":shutil.which("npm"),"docker":shutil.which("docker"),"powershell":shutil.which("powershell") or shutil.which("pwsh"),"cwd":os.getcwd()}
    def tool_available(self,name): return shutil.which(name) is not None
