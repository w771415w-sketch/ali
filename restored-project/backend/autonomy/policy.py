# -*- coding: utf-8 -*-
from __future__ import annotations
from dataclasses import dataclass, asdict

@dataclass
class SelfTrainingPolicy:
    min_new_samples:int=32
    require_all_regression_tests:bool=True
    require_validation_improvement:bool=True
    min_improvement:float=0.002
    auto_download:bool=False
    auto_apply_code_changes:bool=False
    allow_internet_research:bool=False
    def to_dict(self): return asdict(self)
