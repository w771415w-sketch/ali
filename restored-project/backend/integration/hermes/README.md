# ALI AI ↔ Hermes external integration

Hermes is **not copied into ALI AI**. The integration treats Hermes as an external installation at:

`D:\AI ALI\Hermes\`

Default access is read-only. ALI may inspect approved Markdown memory, the read-only project/kanban SQLite databases, and skill indexes. `.env`, `auth.json`, credential files and private keys are explicitly blocked.

API and MCP bridges are configuration boundaries only until the actual Hermes protocol endpoint is supplied. No fake endpoint or undocumented protocol is assumed.
