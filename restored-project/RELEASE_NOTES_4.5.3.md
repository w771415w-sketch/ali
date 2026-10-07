# ALI Studio Pro 4.5.3 — Continuation & Reliability Release

## Added
- Arabic P50 authoritative local knowledge reference.
- Arabic-aware lexical retrieval fallback.
- Dynamic backend port discovery between Electron and Python.
- Endpoint file for diagnostics.
- New release tests for Arabic retrieval and port collision.

## Fixed
- RAG queries in Arabic could miss English-only chunks.
- Electron and API client could remain hard-coded to 8765 when the port was busy.
- Standalone backend now falls forward to a free local port instead of failing on address-in-use.

## Hardware
Target: ThinkPad P50, i7-6820HQ, 32GB RAM, Quadro M1000M 2GB VRAM.

## Verification honesty
Linux checks can validate Python/source/backend behavior. Windows-native Electron/.NET/node-pty/CUDA gates still require the target Windows machine.
