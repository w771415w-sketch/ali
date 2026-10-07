# -*- coding: utf-8 -*-
"""core/__init__.py — حزمة core.

تحتوي:
- events: نظام EventBus بسيط وآمن للخيوط.
- context: ConversationContext الذي يجمع thread + messages + tools + perm.
- agent: Professional AI Agent (intent classification + plan + execute + reflect).
"""

from core.events import EventBus, Event
from core.context import ConversationContext
from core.agent import (
    Intent,
    Plan,
    ToolCall,
    ExecutionResult,
    classify_intent,
    plan_actions,
    execute_plan,
    count_tokens,
)

__all__ = [
    "EventBus", "Event", "ConversationContext",
    "Intent", "Plan", "ToolCall", "ExecutionResult",
    "classify_intent", "plan_actions", "execute_plan", "count_tokens",
]
