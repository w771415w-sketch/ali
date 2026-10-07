# ALI Professional Control Plane

Executable local-first control layer around the model and conversation intelligence.

`user -> requirements -> ambiguity/conflicts -> memory/RAG -> plan -> policy/approval -> tools/project execution -> verification -> recovery/retest -> deliver`

Durable state, memory, knowledge, permissions, planning, execution, recovery, evaluation, lineage and release control stay outside model weights. A task is never marked successful from generated text alone.

## P50
The control plane is stdlib-first and SQLite-backed. Heavy training remains governed by the existing P50 hardware policy: CPU-first, six training threads maximum, one heavy job, AC/power/thermal/RAM admission and optional GPU inference offload.

## Native gates
Desktop Electron/node-pty, real model/GGUF/llama.cpp inference, real SFT/LoRA and checkpoint resume, UI-driven Git/filesystem execution, and native Windows release validation remain explicit gates until executed on the real P50.