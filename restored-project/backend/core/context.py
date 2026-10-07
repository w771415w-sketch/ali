# -*- coding: utf-8 -*-
"""ConversationContext — سياق محادثة واحد.

يجمع:
- thread_id (تعريف المحادثة).
- messages (قائمة الأدوار والنصوص).
- perm_mode (read-only / default / full-access).
- tool_registry (مرجع للأدوات المتاحة في هذه المحادثة).
- project_dir (مسار العمل المرتبط بالمحادثة).
- extra (قاموس حر للحقول الإضافية مثل model_id, effort).

الـ Context هو ما يمر بين الطبقات (UI → Agent → Tools → Inference).
لا يحمل منطقاً، فقط حالة (state + behaviour خفيف).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class Message:
    """رسالة واحدة داخل محادثة."""
    role: str           # user | assistant | system | tool
    content: str
    ts: float = 0.0
    meta: Optional[Dict[str, Any]] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "role": self.role,
            "content": self.content,
            "ts": self.ts,
            "meta": self.meta or {},
        }


@dataclass
class ConversationContext:
    """سياق محادثة واحد — يمر بين الطبقات."""
    thread_id: str
    project_dir: str
    perm_mode: str = "default"          # read-only | default | full-access
    model: str = "ALI-Conversation (from-scratch)"
    effort: str = "Extra high"
    messages: List[Message] = field(default_factory=list)
    extra: Dict[str, Any] = field(default_factory=dict)
    tool_registry: Optional[Any] = None  # مرجع لـ ToolRegistry (نضعه في V0.4)

    # -------- message ops
    def add_user(self, content: str) -> None:
        import time
        self.messages.append(Message(role="user", content=content, ts=time.time()))

    def add_assistant(self, content: str) -> None:
        import time
        self.messages.append(
            Message(role="assistant", content=content, ts=time.time())
        )

    def add_system(self, content: str) -> None:
        import time
        self.messages.append(
            Message(role="system", content=content, ts=time.time())
        )

    def add_tool(self, content: str, meta: Optional[Dict[str, Any]] = None) -> None:
        import time
        self.messages.append(
            Message(role="tool", content=content, ts=time.time(), meta=meta)
        )

    def last_user(self) -> Optional[str]:
        for m in reversed(self.messages):
            if m.role == "user":
                return m.content
        return None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "thread_id": self.thread_id,
            "project_dir": self.project_dir,
            "perm_mode": self.perm_mode,
            "model": self.model,
            "effort": self.effort,
            "messages": [m.to_dict() for m in self.messages],
        }


__all__ = ["ConversationContext", "Message"]
