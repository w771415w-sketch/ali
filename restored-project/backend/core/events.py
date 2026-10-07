# -*- coding: utf-8 -*-
"""نظام أحداث بسيط وآمن للخيوط.

- thread-safe عبر Lock.
- callbacks تُنفّذ متسلسلة (لا تبعثر).
- لا يلزم async — يمكن للـ UI أن يستمع وينفّذ في main thread.

استخدام:
    bus = EventBus()
    bus.subscribe("message.user", lambda e: print(e.data))
    bus.publish(Event("message.user", {"content": "hi"}))
"""

from __future__ import annotations

import threading
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List


@dataclass
class Event:
    """حدث مجرد يحمل نوعاً وبيانات."""
    type: str
    data: Dict[str, Any] = field(default_factory=dict)
    source: str = ""


Handler = Callable[[Event], None]


class EventBus:
    """ناقل أحداث بسيط — Subscribe/Publish/Unsub."""

    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._handlers: Dict[str, List[Handler]] = {}

    def subscribe(self, event_type: str, handler: Handler) -> None:
        with self._lock:
            self._handlers.setdefault(event_type, []).append(handler)

    def unsubscribe(self, event_type: str, handler: Handler) -> None:
        with self._lock:
            if event_type in self._handlers:
                try:
                    self._handlers[event_type].remove(handler)
                except ValueError:
                    pass

    def publish(self, event: Event) -> None:
        """نشر الحدث — ينسخ قائمة المعالجات لتفادي التعديل أثناء المرور."""
        with self._lock:
            handlers = list(self._handlers.get(event.type, []))
        for h in handlers:
            try:
                h(event)
            except Exception:
                # لا نسمح لـ handler مكسور بإسقاط البقية.
                # الخطأ يُسجَّل في logging الذي سيُضَاف لاحقاً.
                pass

    def clear(self) -> None:
        with self._lock:
            self._handlers.clear()


# أنواع الأحداث الموحدة داخل ALI Studio
class Events:
    """ثوابت أسماء الأحداث لتقليل الأخطاء الإملائية."""
    USER_MESSAGE = "message.user"
    ASSISTANT_MESSAGE = "message.assistant"
    TOOL_START = "tool.start"
    TOOL_FINISH = "tool.finish"
    PERMISSION_REQUEST = "permission.request"
    PERMISSION_GRANT = "permission.grant"
    PERMISSION_DENY = "permission.deny"
    THREAD_NEW = "thread.new"
    THREAD_OPEN = "thread.open"
    CONFIG_CHANGED = "config.changed"
    ERROR = "error"


__all__ = ["EventBus", "Event", "Events"]
