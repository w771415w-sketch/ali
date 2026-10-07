# -*- coding: utf-8 -*-
"""Conversation-to-runtime admission boundary."""
from conversation_intelligence.v6_router import frame, update_state
from runtime.device_policy import choose_policy

class RequestPipeline:
    def __init__(self, hardware): self.hardware=hardware
    def prepare(self,user_text,state=None):
        request=frame(user_text,state); new_state=update_state(state,request); policy=choose_policy(self.hardware)
        # Training admission is independent from normal file/code execution.
        execution_allowed = not (
            request.mode == "execute" and
            request.risk_level in {"high","external_side_effect"} and
            not policy.get("training_enabled", True)
        )
        return {"request":request.to_dict(),"state":new_state,"runtime_policy":policy,"execution_allowed":execution_allowed}
