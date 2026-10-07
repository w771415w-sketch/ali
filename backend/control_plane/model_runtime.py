from __future__ import annotations
from pathlib import Path
import shutil,subprocess
class ModelRuntime:
    def discover(self):
        return {"llama_cli":shutil.which("llama-cli"),"llama_server":shutil.which("llama-server"),"ollama":shutil.which("ollama")}
    def inspect_gguf(self,path):
        p=Path(path)
        if not p.is_file():return {"ok":False,"status":"not_found","path":str(p)}
        return {"ok":p.suffix.casefold()==".gguf","status":"file_detected","path":str(p),"bytes":p.stat().st_size}
    def run(self,executable,model,prompt,timeout_s=120):
        if not Path(executable).is_file() and shutil.which(executable) is None:return {"ok":False,"status":"runtime_not_available"}
        try:
            r=subprocess.run([executable,"-m",model,"-p",prompt],capture_output=True,text=True,timeout=timeout_s)
            return {"ok":r.returncode==0,"returncode":r.returncode,"stdout":r.stdout,"stderr":r.stderr}
        except Exception as e:return {"ok":False,"status":"failed","error":str(e)}
