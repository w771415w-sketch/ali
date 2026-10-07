# -*- coding: utf-8 -*-
"""Deterministic project-change state machine; every transition needs evidence."""
from __future__ import annotations
from enum import Enum
from dataclasses import dataclass,asdict
from typing import Dict,Any

class Phase(str,Enum): INSPECT='inspect'; PLAN='plan'; SNAPSHOT='snapshot'; APPLY='apply'; TEST='test'; VERIFY='verify'; REVIEW='review'; COMPLETE='complete'; FAILED='failed'

@dataclass
class WorkflowState:
    task:str; phase:str=Phase.INSPECT.value; approved:bool=False; tests_passed:bool=False; verified:bool=False; notes:str=''
    def to_dict(self):return asdict(self)

class ChangeWorkflow:
    def __init__(self,task:str):self.state=WorkflowState(task=task)
    def transition(self,phase:Phase,**evidence):
        current=Phase(self.state.phase); allowed={Phase.INSPECT:Phase.PLAN,Phase.PLAN:Phase.SNAPSHOT,Phase.SNAPSHOT:Phase.APPLY,Phase.APPLY:Phase.TEST,Phase.TEST:Phase.VERIFY,Phase.VERIFY:Phase.REVIEW,Phase.REVIEW:Phase.COMPLETE}
        if phase not in {Phase.FAILED,allowed.get(current)}:raise ValueError(f'invalid transition {current}->{phase}')
        if phase is Phase.APPLY and not self.state.approved:raise PermissionError('apply requires explicit approval')
        if phase is Phase.REVIEW and not self.state.verified:raise ValueError('review requires successful verification')
        self.state.phase=phase.value; self.state.tests_passed=bool(evidence.get('tests_passed',self.state.tests_passed)); self.state.verified=bool(evidence.get('verified',self.state.verified)); self.state.notes=str(evidence.get('notes',self.state.notes)); return self.state
    def approve(self):self.state.approved=True; return self.state
