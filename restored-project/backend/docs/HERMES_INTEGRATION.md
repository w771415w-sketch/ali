# ALI AI 2.5 + Hermes Integration Revision 2.6 — Hermes Integration

## Independence
ALI AI remains independently runnable. Hermes is an external system.

## External root
`D:\AI ALI\Hermes\`

## Read-only boundary
Allowed: `SOUL.md`, `memories/*.md`, `skills/**/SKILL.md`, `skills/.bundled_manifest`, `config.yaml`, `projects.db`, `kanban.db` (SELECT/PRAGMA only).
Blocked: `.env`, `auth.json`, credentials, keys, certificates and anything outside the root.

## Routing
ALI consults Hermes context only when a request contains a deterministic Hermes-related intent. Otherwise the ALI-local memory/RAG path remains unchanged.

## Phase-2 API/MCP
The repository contains interfaces for later API/MCP wiring, but no undocumented Hermes endpoint is fabricated. Set the actual endpoint/protocol only after confirming it.
