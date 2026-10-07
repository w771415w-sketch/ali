# -*- coding: utf-8 -*-
"""Deprecated compatibility module.

The old NumPy TinyTransformer implementation was removed because it did not train
real language-model weights. Use model.ali_lm.ALIForCausalLM instead.
"""
from .ali_lm import AliConfig, ALIForCausalLM
ModelConfig = AliConfig
TinyTransformer = ALIForCausalLM
__all__=['ModelConfig','TinyTransformer']
