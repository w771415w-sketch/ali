# -*- coding: utf-8 -*-
"""Read-only Internet research tool for ALI.

No model/provider is used. It performs HTTP retrieval only when the runtime
explicitly enables Internet access.
"""
from __future__ import annotations
from typing import Any
from tools.base import Tool, ToolResult, ToolPermission

class WebResearchTool(Tool):
    name = 'web_research'
    description = 'Search the public web and return source-backed text; disabled unless Internet Research is enabled.'
    permission = ToolPermission.READ_ONLY
    input_schema = {
        'type':'object',
        'properties': {'query': {'type':'string'}, 'limit': {'type':'integer','minimum':1,'maximum':10}},
        'required':['query']
    }
    def execute(self, ctx: Any, **kwargs) -> ToolResult:
        if not bool(getattr(ctx, 'extra', {}).get('allow_internet', False)):
            return ToolResult.fail('Internet research is disabled.', code='INTERNET_DISABLED')
        q=str(kwargs.get('query','')).strip()
        if not q: return ToolResult.fail('query is required', code='PARSE')
        try:
            from research.web import research
            result=research(q, max(1,min(10,int(kwargs.get('limit',5)))))
            return ToolResult.ok_payload(**result)
        except Exception as e:
            return ToolResult.fail(str(e), code='NETWORK_ERROR')
