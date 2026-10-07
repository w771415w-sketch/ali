from __future__ import annotations
import shutil,subprocess
from pathlib import Path
class ModelConversionError(RuntimeError): pass
class GGUFConverter:
    def __init__(self,llama_root=None,python_executable="python"):
        self.llama_root=Path(llama_root).resolve() if llama_root else None;self.python=python_executable
    def discover(self):
        script=(self.llama_root/"convert_hf_to_gguf.py") if self.llama_root else None
        script=script if script and script.is_file() else None;quant=None
        if self.llama_root:
            for c in (self.llama_root/"build/bin/llama-quantize",self.llama_root/"build/bin/llama-quantize.exe"):
                if c.is_file():quant=c;break
        if quant is None:quant=shutil.which("llama-quantize") or shutil.which("llama-quantize.exe")
        return {"converter_script":str(script) if script else None,"quantizer":str(quant) if quant else None,"python":shutil.which(self.python) or self.python}
    def convert(self,source_dir,outfile,outtype="f16",approved=False,timeout_s=3600,mmproj=False):
        source=Path(source_dir);out=Path(outfile)
        if source.suffix.lower()==".gguf":raise ModelConversionError("GGUF is runtime/export only, not a training source")
        if not source.is_dir():raise ModelConversionError("Hugging Face model directory not found")
        d=self.discover()
        if not d["converter_script"]:raise ModelConversionError("convert_hf_to_gguf.py not found")
        cmd=[self.python,d["converter_script"],str(source),"--outfile",str(out),"--outtype",outtype]+(["--mmproj"] if mmproj else [])
        if not approved:return {"ok":False,"status":"approval_required","dry_run_command":cmd}
        r=subprocess.run(cmd,capture_output=True,text=True,timeout=timeout_s,check=False)
        return {"ok":r.returncode==0,"status":"converted" if r.returncode==0 else "failed","command":cmd,"stdout":r.stdout,"stderr":r.stderr,"output":str(out) if r.returncode==0 else None}
    def quantize(self,input_gguf,output_gguf,quant_type="Q4_K_M",approved=False,timeout_s=3600,threads=2):
        src=Path(input_gguf);out=Path(output_gguf)
        if src.suffix.lower()!=".gguf":raise ModelConversionError("quantizer input must be GGUF")
        d=self.discover()
        if not d["quantizer"]:raise ModelConversionError("llama-quantize executable not found")
        cmd=[str(d["quantizer"]),str(src),str(out),quant_type,"-t",str(max(1,int(threads)))]
        if not approved:return {"ok":False,"status":"approval_required","dry_run_command":cmd}
        r=subprocess.run(cmd,capture_output=True,text=True,timeout=timeout_s,check=False)
        return {"ok":r.returncode==0,"status":"quantized" if r.returncode==0 else "failed","command":cmd,"stdout":r.stdout,"stderr":r.stderr,"output":str(out) if r.returncode==0 else None}
    @staticmethod
    def verify_gguf(path):
        p=Path(path)
        if not p.is_file():return {"ok":False,"status":"not_found"}
        with p.open("rb") as f:magic=f.read(4)
        return {"ok":magic==b"GGUF","status":"valid" if magic==b"GGUF" else "invalid_magic","path":str(p),"bytes":p.stat().st_size}
