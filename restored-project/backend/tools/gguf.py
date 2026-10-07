# -*- coding: utf-8 -*-
"""GGUF conversion, validation and local llama.cpp bridge."""
from __future__ import annotations
from pathlib import Path
import subprocess, os, hashlib, json, struct
from typing import Dict,Any

class GGUFManager:
    def __init__(self,llama_dir:str|Path="vendor/llama.cpp"):
        self.root=Path(llama_dir)
    def converter(self):
        for n in ("convert_hf_to_gguf.py","convert-hf-to-gguf.py"):
            p=self.root/n
            if p.exists(): return p
        return None
    def quantizer(self):
        for n in ("llama-quantize.exe","llama-quantize","quantize.exe","quantize"):
            for b in (self.root,self.root/"build"/"bin",self.root/"bin"):
                p=b/n
                if p.exists():return p
        for p in self.root.glob("**/llama-quantize*"):
            if p.is_file() and p.suffix.lower() in {"",".exe"}:return p
        return None
    def server(self):
        for n in ("llama-server.exe","llama-server"):
            for b in (self.root,self.root/"build"/"bin",self.root/"bin"):
                p=b/n
                if p.exists():return p
        return None
    def cli(self):
        for n in ("llama-cli.exe","llama-cli"):
            for b in (self.root,self.root/"build"/"bin",self.root/"bin"):
                p=b/n
                if p.exists():return p
        return None
    def _sha256(self,path):
        h=hashlib.sha256(); p=Path(path)
        with p.open("rb") as f:
            for b in iter(lambda:f.read(1024*1024),b""):h.update(b)
        return h.hexdigest()
    def _write_sidecar(self,path,meta):
        p=Path(path); data=dict(meta,sha256=self._sha256(p),size=p.stat().st_size); p.with_suffix(p.suffix+".json").write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding="utf-8")
    def validate(self,path:str|Path)->Dict[str,Any]:
        p=Path(path); out={"path":str(p),"exists":p.exists(),"size":0,"magic":False,"version":None,"valid":False}
        if not p.exists():return out
        out["size"]=p.stat().st_size
        if out["size"]<24:return out
        with p.open("rb") as f:
            out["magic"]=f.read(4)==b"GGUF"
            if out["magic"]:
                raw=f.read(4); out["version"]=struct.unpack("<I",raw)[0] if len(raw)==4 else None
                out["valid"]=out["version"] in {1,2,3,4}
        return out
    def convert(self,hf_dir,outfile,outtype="f16"):
        conv=self.converter()
        if not conv:raise FileNotFoundError(f"llama.cpp converter not found: {self.root}")
        hf=Path(hf_dir); out=Path(outfile); out.parent.mkdir(parents=True,exist_ok=True)
        cmd=[os.environ.get("PYTHON",os.sys.executable),str(conv),str(hf),"--outfile",str(out),"--outtype",str(outtype)]
        p=subprocess.run(cmd,capture_output=True,text=True,timeout=3600,cwd=str(self.root))
        if p.returncode!=0:raise RuntimeError((p.stderr or p.stdout)[-6000:])
        check=self.validate(out)
        if not check["valid"]:raise RuntimeError("Converter returned success but GGUF validation failed")
        meta={"path":str(out),"format":"GGUF","outtype":outtype,"validation":check,"stdout":p.stdout[-4000:]}; self._write_sidecar(out,meta); return meta
    def quantize(self,src,dst,ftype="Q4_K_M"):
        q=self.quantizer()
        if not q:raise FileNotFoundError("llama-quantize not found in vendor/llama.cpp")
        src=Path(src); dst=Path(dst); dst.parent.mkdir(parents=True,exist_ok=True)
        p=subprocess.run([str(q),str(src),str(dst),ftype],capture_output=True,text=True,timeout=3600,cwd=str(self.root))
        if p.returncode!=0:raise RuntimeError((p.stderr or p.stdout)[-6000:])
        check=self.validate(dst)
        if not check["valid"]:raise RuntimeError("Quantizer returned success but GGUF validation failed")
        meta={"path":str(dst),"quantization":ftype,"validation":check,"stdout":p.stdout[-4000:]}; self._write_sidecar(dst,meta); return meta
    def check(self):return {"llama_dir":str(self.root.resolve()),"converter":str(self.converter() or ""),"quantizer":str(self.quantizer() or ""),"llama_cli":str(self.cli() or ""),"llama_server":str(self.server() or "")}
    def run(self,model,prompt,max_tokens=256,temperature=.7):
        cli=self.cli()
        if not cli:raise FileNotFoundError("llama-cli not found in vendor/llama.cpp")
        p=subprocess.run([str(cli),"-m",str(model),"-p",prompt,"-n",str(max_tokens),"--temp",str(temperature),"--no-display-prompt","--no-show-timings"],capture_output=True,text=True,timeout=3600)
        if p.returncode!=0:raise RuntimeError((p.stderr or p.stdout)[-6000:])
        return {"text":p.stdout,"model":str(model),"max_tokens":max_tokens,"temperature":temperature}
