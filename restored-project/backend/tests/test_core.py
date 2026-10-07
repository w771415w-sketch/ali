# -*- coding: utf-8 -*-
"""اختبارات V0.3 — core/events + core/context."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def test_event_publish_calls_subscribers():
    from core.events import EventBus, Event
    bus = EventBus()
    seen = []
    bus.subscribe("test.evt", lambda e: seen.append(e.data))
    bus.publish(Event("test.evt", {"x": 1}))
    bus.publish(Event("test.evt", {"x": 2}))
    assert len(seen) == 2
    assert seen[0]["x"] == 1
    assert seen[1]["x"] == 2


def test_event_unsubscribe():
    from core.events import EventBus, Event
    bus = EventBus()
    h = lambda e: None
    bus.subscribe("t", h)
    bus.unsubscribe("t", h)
    bus.publish(Event("t", {}))   # لا exception


def test_event_handler_error_does_not_break_others():
    from core.events import EventBus, Event
    bus = EventBus()
    results = []
    bus.subscribe("t", lambda e: (_ for _ in ()).throw(RuntimeError("boom")))
    bus.subscribe("t", lambda e: results.append("ok"))
    bus.publish(Event("t", {}))
    assert results == ["ok"]


def test_context_add_messages():
    from core.context import ConversationContext
    ctx = ConversationContext(thread_id="t1", project_dir=".")
    ctx.add_user("hi")
    ctx.add_assistant("hello")
    assert len(ctx.messages) == 2
    assert ctx.last_user() == "hi"


def test_context_to_dict():
    from core.context import ConversationContext
    ctx = ConversationContext(
        thread_id="t2", project_dir="/tmp",
        perm_mode="default", model="ALI-local",
    )
    ctx.add_user("q")
    d = ctx.to_dict()
    assert d["thread_id"] == "t2"
    assert d["perm_mode"] == "default"
    assert len(d["messages"]) == 1


def test_events_constants_present():
    from core.events import Events
    assert Events.USER_MESSAGE == "message.user"
    assert Events.TOOL_START == "tool.start"
    assert Events.PERMISSION_REQUEST == "permission.request"
