# -*- coding: utf-8 -*-
"""Request understanding + independent runtime admission boundary."""
from conversation_intelligence.v6_router import frame, update_state
from runtime.device_policy import choose_policy

class RequestPipeline:
    def __init__(self, hardware):
        self.hardware = hardware
    def prepare(self, user_text, state=None):
        request = frame(user_text, state)
        new_state = update_state(state, request)
        policy = choose_policy(self.hardware)
        # Normal execution is not dependent on whether heavy training is admitted.
        # Training jobs use the policy separately through the training controller.
        return {
            "request": request.to_dict(),
            "state": new_state,
            "runtime_policy": policy,
            "execution_allowed": not bool(request.confirmation_required and not request.confirmation),
        }
