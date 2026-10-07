from __future__ import annotations
import json
from copy import deepcopy
from pathlib import Path
class TrainingSettingsError(ValueError): pass
class TrainingSettingsManager:
    def __init__(self,catalog_path,settings_path=None):
        self.catalog_path=Path(catalog_path); self.settings_path=Path(settings_path or self.catalog_path.with_name("desktop_settings.json"))
        self.catalog=json.loads(self.catalog_path.read_text(encoding="utf-8")); self.settings=self._load()
    def _load(self):
        try:
            x=json.loads(self.settings_path.read_text(encoding="utf-8")); return x if isinstance(x,dict) else {}
        except (FileNotFoundError,json.JSONDecodeError): return {}
    @staticmethod
    def _hv(h):
        def g(k,d=0): return getattr(h,k,h.get(k,d) if isinstance(h,dict) else d)
        cap=g("cuda_capability",(0,0)); cap=tuple(int(x) for x in cap) if cap else (0,0)
        return float(g("ram_gb",0) or 0),float(g("vram_gb",0) or 0),int(g("cpu_threads",g("cpu_cores",0)) or 0),cap
    def training_methods(self,hardware,model_metadata=None):
        model_metadata=model_metadata or {}; params=int(model_metadata.get("parameter_count",0) or 0); ram,vram,threads,cap=self._hv(hardware); out=[]
        for raw in self.catalog.get("training_methods",[]):
            m=deepcopy(raw); reasons=[]
            if not m.get("enabled",True): reasons.append(m.get("reason","disabled"))
            if m.get("device")=="gpu" and (vram<3 or cap<(6,0)): reasons.append("GPU path is outside safe P50 limits")
            maxp=int(m.get("constraints",{}).get("max_parameter_count",0) or 0)
            if maxp and params>maxp: reasons.append("model exceeds method parameter limit")
            mint=int(m.get("constraints",{}).get("max_cpu_threads",0) or 0)
            if mint and threads and threads<mint: reasons.append("not enough CPU threads")
            m["available"]=not reasons; m["disabled_reason"]="; ".join(map(str,reasons)); out.append(m)
        return out
    def conversion_profiles(self): return deepcopy(self.catalog.get("conversion_profiles",[]))
    def dataset_strategies(self): return deepcopy(self.catalog.get("dataset_update_modes",[]))
    def validate(self,method_id,conversion_id,hardware,model_metadata=None):
        methods={x["id"]:x for x in self.training_methods(hardware,model_metadata)}; conv={x["id"]:x for x in self.conversion_profiles()}
        if method_id not in methods: raise TrainingSettingsError("unknown training method")
        if conversion_id not in conv: raise TrainingSettingsError("unknown conversion profile")
        if not methods[method_id]["available"]: raise TrainingSettingsError(methods[method_id]["disabled_reason"])
        if conv[conversion_id].get("enabled") is False: raise TrainingSettingsError("conversion disabled")
        return {"valid":True,"training_method":methods[method_id],"conversion":conv[conversion_id]}
    def choose(self,hardware,model_metadata=None):
        methods=[x for x in self.training_methods(hardware,model_metadata) if x["available"]]; conv=[x for x in self.conversion_profiles() if x.get("enabled",True)]
        tm=next((x for x in methods if x.get("recommended")),methods[0] if methods else None); cp=next((x for x in conv if x.get("recommended")),conv[0] if conv else None)
        if not tm or not cp: raise TrainingSettingsError("no usable options")
        return {"training_method":tm,"conversion":cp}
    def save_selection(self,method_id,conversion_id,hardware,model_metadata=None):
        v=self.validate(method_id,conversion_id,hardware,model_metadata); d=deepcopy(self.settings); d.setdefault("ai",{})
        d["ai"].setdefault("training",{}).update(method=method_id,device=v["training_method"].get("device"),continue_from=v["training_method"].get("checkpoint_source"))
        d["ai"].setdefault("conversion",{}).update(profile=conversion_id); self.settings_path.parent.mkdir(parents=True,exist_ok=True)
        tmp=self.settings_path.with_suffix(self.settings_path.suffix+".tmp"); tmp.write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding="utf-8"); tmp.replace(self.settings_path); self.settings=d; return d
    def current(self): return deepcopy(self.settings)
