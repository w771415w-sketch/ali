# -*- coding: utf-8 -*-
"""ALI neural model package.

Heavy lifecycle modules are imported lazily to avoid package-level circular imports.
"""
from .ali_lm import AliConfig, ALIForCausalLM
from .importer import WeightReport, inspect_weights, import_compatible, load_into
from .registry import ModelRegistry
__all__=['AliConfig','ALIForCausalLM','WeightReport','inspect_weights','import_compatible','load_into','ModelRegistry','ModelManager']
def __getattr__(name):
    if name=='ModelManager':
        from .manager import ModelManager
        return ModelManager
    raise AttributeError(name)
