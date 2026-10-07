from __future__ import annotations
import json
from copy import deepcopy
from pathlib import Path

class LanguageSettingsError(ValueError): pass

class LanguageSettingsManager:
    def __init__(self,catalog_path,settings_path=None):
        self.catalog_path=Path(catalog_path); self.settings_path=Path(settings_path or self.catalog_path.with_name("desktop_settings.json"))
        self.catalog=json.loads(self.catalog_path.read_text(encoding="utf-8")); self.settings=self._load()
    def _load(self):
        try:
            x=json.loads(self.settings_path.read_text(encoding="utf-8")); return x if isinstance(x,dict) else {}
        except (FileNotFoundError,json.JSONDecodeError): return {}
    def profiles(self): return deepcopy(self.catalog.get("profiles",{}))
    def available(self): return [{"id":k,**v,"available":bool(v.get("enabled",True))} for k,v in self.catalog.get("profiles",{}).items()]
    def current_id(self): return str(self.settings.get("language_profile") or self.catalog.get("default_profile","ar-SA"))
    def validate(self,profile_id):
        p=self.catalog.get("profiles",{}).get(profile_id)
        if not p: raise LanguageSettingsError(f"unknown language profile: {profile_id}")
        if p.get("enabled") is False: raise LanguageSettingsError(f"language profile disabled: {profile_id}")
        return {"id":profile_id,**deepcopy(p)}
    def save(self,profile_id):
        profile=self.validate(profile_id); d=deepcopy(self.settings); d["language_profile"]=profile_id; d.setdefault("ai",{}).setdefault("language",{})["profile"]=profile_id
        self.settings_path.parent.mkdir(parents=True,exist_ok=True); tmp=self.settings_path.with_suffix(self.settings_path.suffix+".tmp")
        tmp.write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding="utf-8"); tmp.replace(self.settings_path); self.settings=d
        return {"saved":True,"profile":profile}
