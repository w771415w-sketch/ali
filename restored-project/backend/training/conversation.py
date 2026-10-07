# -*- coding: utf-8 -*-
"""Conversation-specialized ALI adaptation using real LoRA weights."""
from __future__ import annotations
from pathlib import Path
from typing import Any, Dict
import json
from model.ali_lm import ALIForCausalLM, AliConfig
from training.lora import apply_lora, save_lora_adapter, load_lora_adapter

def attach_conversation_adapter(model: ALIForCausalLM, rank:int=8, alpha:float=16.0, dropout:float=.05):
    return apply_lora(model,rank=rank,alpha=alpha,dropout=dropout)

def save_conversation_adapter(model, out_dir, meta:Dict[str,Any]|None=None):
    md={'specialization':'conversation','target':'assistant_response_and_tool_calling'}
    md.update(meta or {})
    return save_lora_adapter(model,out_dir,md)

def load_conversation_adapter(model, adapter_dir):
    load_lora_adapter(model,adapter_dir)
    return model
