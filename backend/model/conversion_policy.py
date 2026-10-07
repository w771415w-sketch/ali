from __future__ import annotations
from pathlib import Path
from config.training_settings import TrainingSettingsManager
class ConversionPolicy:
    def __init__(self,config_dir=None):
        root=Path(config_dir or Path(__file__).resolve().parents[1]/"config");self.settings=TrainingSettingsManager(root/"training_methods.json",root/"desktop_settings.json")
    def profiles(self):return self.settings.conversion_profiles()
    def validate(self,conversion_id):return next((x for x in self.profiles() if x["id"]==conversion_id and x.get("enabled",True)),None)
