from __future__ import annotations
from pathlib import Path
from config.settings_service import ProjectSettingsService
from .lifecycle import TrainingLifecycle
from .continual_dataset import ContinualDataset
class TrainingController:
    def __init__(self,root,config_dir=None):
        self.root=Path(root);self.settings=ProjectSettingsService(config_dir);self.lifecycle=TrainingLifecycle(self.root/"models");self.datasets=ContinualDataset(self.root/"datasets")
    def options(self,hardware,model_metadata=None): return self.settings.snapshot(hardware,model_metadata)
    def preflight(self,hardware,model_metadata=None,method_id=None,conversion_id=None):
        choice=self.settings.choose_training(hardware,method_id,conversion_id,model_metadata)
        return {"ok":True,"selection":choice["selection"],"hardware":getattr(hardware,"to_dict",lambda:hardware)()}
    def merge_datasets(self,old_dataset,new_dataset,version,replay_fraction=.25): return self.datasets.merge(old_dataset,new_dataset,version,replay_fraction=replay_fraction)
    def continue_training_plan(self,hardware,new_dataset,source=None,model_metadata=None,method_id=None,conversion_id=None):
        pre=self.preflight(hardware,model_metadata,method_id,conversion_id)
        return {**self.lifecycle.prepare_continued_training(new_dataset,source=source,method=pre["selection"]["training_method"]["id"]), "preflight":pre}
