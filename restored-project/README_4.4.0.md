# ALI Studio Pro 4.5.0 — Complete Professional Desktop

## Architecture
C#/.NET 8 Portable Launcher → Electron 40.10.2/Chromium → React 19 → Electron IPC → Python Runtime → ALI Agent/Model/RAG/Memory/Tools/Training.

## Training
Drop Markdown or supported documents into the cumulative learning center. The importer validates, normalizes, removes secrets, hashes for deduplication, indexes knowledge into RAG, extracts conversation samples, and creates an incremental dataset. Training runs from the current active model and produces v1/v2/v3... candidates. Evaluation and regression run before promotion.

## Chat sessions
Use **محادثة جديدة** to create an independent saved session. Use **المحادثات السابقة** to open, rename, or delete saved sessions. Streaming and non-streaming responses stay in the same session.

## Adaptive GPU
Select Auto/CPU/GPU from the top bar. Auto runs a CUDA availability check plus a real kernel self-test and uses free VRAM to choose a workload. On a 2 GB legacy GPU, the workload reduces sequence length as free VRAM falls and falls back to CPU if safe headroom is unavailable. Forced GPU reports a clear diagnostic instead of silently switching to CPU.

## Windows setup
For the requested Python 3.11 line, `backend/SETUP.bat` creates the development environment. Legacy NVIDIA hardware is routed to `requirements-windows-legacy-gpu.txt`. The final Portable build still requires a Windows machine with .NET 8, Node.js 22, native node-pty tooling, Embedded Python 3.11.9 and the required model/runtime binaries.
