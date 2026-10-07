# -*- coding: utf-8 -*-
"""Dataset separation and minimum metadata policy."""
from dataclasses import dataclass
@dataclass(frozen=True)
class DatasetSplitPolicy:
    train_name:str="train"; validation_name:str="validation"; test_name:str="test"
    evaluation_isolated:bool=True; synthetic_behavior_separate_from_knowledge:bool=True
    require_unique_ids:bool=True; require_lineage:bool=True
def validate_record(record):
    if not isinstance(record,dict): return False,"record_not_object"
    if not record.get("id"): return False,"missing_id"
    if not isinstance(record.get("messages"),list) or not record["messages"]: return False,"missing_messages"
    meta=record.get("metadata") or {}
    required=("generator_version","family","topic","language_mode","difficulty","risk","turn_pattern","synthetic","eligible_for_behavior_training")
    missing=[k for k in required if k not in meta]
    return (False,"missing_metadata:"+",".join(missing)) if missing else (True,"")
