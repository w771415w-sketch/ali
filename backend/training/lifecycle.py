from __future__ import annotations
import hashlib,json,time
from pathlib import Path
class TrainingLifecycleError(ValueError): pass
class TrainingLifecycle:
    def __init__(self,root):
        self.root=Path(root);self.base=self.root/"base";self.training=self.root/"training";self.checkpoints=self.training/"checkpoints";self.adapters=self.training/"adapters";self.gguf=self.root/"production"/"gguf";self.manifests=self.root/"manifests"
        for p in (self.base,self.checkpoints,self.adapters,self.gguf,self.manifests):p.mkdir(parents=True,exist_ok=True)
    @staticmethod
    def sha256(path):
        p=Path(path);h=hashlib.sha256()
        if p.is_file():
            with p.open("rb") as f:
                for chunk in iter(lambda:f.read(1024*1024),b""):h.update(chunk)
        else:
            for x in sorted(p.rglob("*")):
                if x.is_file():h.update(str(x.relative_to(p)).encode());h.update(TrainingLifecycle.sha256(x).encode())
        return h.hexdigest()
    def _candidates(self,root): return sorted([x for x in Path(root).glob("*") if x.is_dir()],key=lambda p:p.stat().st_mtime,reverse=True)
    def latest_checkpoint(self): return str(self._candidates(self.checkpoints)[0]) if self._candidates(self.checkpoints) else None
    def latest_adapter(self): return str(self._candidates(self.adapters)[0]) if self._candidates(self.adapters) else None
    def verify_training_source(self,source):
        p=Path(source)
        if p.suffix.lower()==".gguf":raise TrainingLifecycleError("GGUF cannot be used as a training source; use checkpoint/adapter")
        if not p.exists():raise TrainingLifecycleError("training source not found")
        allowed={".safetensors",".bin",".pt",".pth",".json"}
        if p.is_file() and p.suffix.lower() not in allowed:raise TrainingLifecycleError(f"unsupported training source: {p.suffix}")
        return {"ok":True,"source":str(p),"sha256":self.sha256(p)}
    def prepare_continued_training(self,new_dataset,source=None,method="lora_continue_cpu",dataset_strategy="cumulative_replay"):
        source=source or self.latest_adapter() or self.latest_checkpoint()
        if not source:raise TrainingLifecycleError("no verified checkpoint/adapter available")
        data=Path(new_dataset)
        if not data.exists():raise TrainingLifecycleError("new dataset not found")
        src=self.verify_training_source(source)
        return {"ok":True,"plan":{"method":method,"dataset_strategy":dataset_strategy,"training_source":src,"new_dataset":{"path":str(data),"sha256":self.sha256(data)},"created_at":time.time()}}
    def register_gguf(self,path,source_lineage):
        p=Path(path)
        if not p.is_file() or p.suffix.lower()!=".gguf":raise TrainingLifecycleError("valid GGUF file required")
        with p.open("rb") as f:
            if f.read(4)!=b"GGUF":raise TrainingLifecycleError("invalid GGUF magic")
        out={"artifact":str(p),"sha256":self.sha256(p),"lineage":source_lineage,"registered_at":time.time()}
        (self.manifests/f"{p.stem}.gguf.json").write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding="utf-8");return out
