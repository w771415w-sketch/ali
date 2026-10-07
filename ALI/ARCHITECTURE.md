# ALI Professional Runtime Architecture

```text
Desktop UI / CLI
      │
      ▼
ALI API / Orchestrator
      │
      ├── Config + hardware policy
      ├── Security / auth / rate limiting / path safety
      ├── Idempotency + audit (SQLite/WAL)
      ├── Diagnostics / health / doctor
      │
      ▼
Existing Professional Control Plane
      ├── requirements / planning / memory / RAG
      ├── tools / files / Git / verification
      ├── training / model / release controls
      └── recovery / governance / observability

Historical source export remains preserved under source-export/ and restored-project/.
```

The ALI directory is intentionally dependency-free at its boundary. If the existing control plane can be imported, the adapter uses it. If the dependency graph is unavailable, the runtime reports `control_plane_unavailable` instead of pretending the operation succeeded.
