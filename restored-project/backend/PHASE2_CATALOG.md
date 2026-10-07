# ALI AI 2.5.0 — Phase-2 Capability Catalog

هذه القائمة محفوظة داخل المشروع كعقدة تحضير للمرحلة التالية فقط. العناصر الخارجية والامتدادات ذات الصلاحيات لا تعمل تلقائيًا في إصدار 2.5.0.

## Image / Video providers

Images: `openai`, `openai-codex`, `deepinfra`, `fal`, `krea`, `openrouter`, `xai`

Video: `xai`, `deepinfra`, `fal`

## Search engines

`brave_free`, `ddgs`, `exa`, `firecrawl`, `keenable`, `parallel`, `searxng`, `tavily`, `xai`

## MCP servers

The project records the 46 server names explicitly supplied in the request. The request states 65 total, so the remaining 19 names are intentionally left unassigned rather than invented.

## Skills

The supplied list is stored exactly by category in `phase2/skills.json` and contains 58 named skills across the requested categories.

## Toolsets

The named toolsets supplied in the request are recorded in `phase2/toolsets.json`. The request states 58 toolsets overall, but only the names provided in the request are recorded.

## Messaging platforms

The request states 22 platforms but does not provide their names. The project keeps 22 reserved slots in `phase2/platforms.json` without inventing connector names.

## Future runtime surfaces

Prepared contracts include: terminal, browser/CDP, computer-use with confirmation gates, cron scheduling, subagents, memory/session search, skills loader, provider router, MCP gateway, multimodal analysis/generation, voice, messaging connectors and an educational/self-improvement loop.

## Security rule

No API keys, OAuth tokens, passwords, private `.env` values, `auth.json`, machine UUIDs or personal connector credentials are included in this project bundle.
