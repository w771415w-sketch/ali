from __future__ import annotations
from pathlib import Path
from .training_settings import TrainingSettingsManager
from .language_settings import LanguageSettingsManager
class ProjectSettingsService:
    def __init__(self,config_dir=None):
        root=Path(config_dir or Path(__file__).resolve().parent)
        self.training=TrainingSettingsManager(root/"training_methods.json",root/"desktop_settings.json")
        self.language=LanguageSettingsManager(root/"language_profiles.json",root/"desktop_settings.json")
    def snapshot(self,hardware,model_metadata=None):
        return {"current":self.training.current(),"language_profile":self.language.current_id(),"language_profiles":self.language.available(),"training_methods":self.training.training_methods(hardware,model_metadata),"conversion_profiles":self.training.conversion_profiles(),"dataset_strategies":self.training.dataset_strategies()}
    def choose_training(self,hardware,method_id=None,conversion_id=None,model_metadata=None):
        chosen=self.training.choose(hardware,model_metadata) if not (method_id or conversion_id) else self.training.validate(method_id,conversion_id,hardware,model_metadata)
        return {"ok":True,"selection":chosen}
    def save_training(self,hardware,method_id,conversion_id,model_metadata=None): return {"ok":True,"settings":self.training.save_selection(method_id,conversion_id,hardware,model_metadata)}
    def save_language(self,profile_id): return {"ok":True,"settings":self.language.save(profile_id)}
