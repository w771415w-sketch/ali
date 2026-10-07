# ThinkPad P50 target profile — ALI AI 2.1

Target class supplied for this project:

- Lenovo ThinkPad P50
- Intel Core i7-6820HQ, 4 physical / 8 logical threads
- 32 GB DDR4 RAM
- NVIDIA Quadro M1000M, 2 GB VRAM, legacy Maxwell-class capability
- Full HD 1920×1080 display
- NVMe system/storage tier plus 2 TB SATA archive tier

## Runtime policy

- Training: CPU-first
- Torch threads: 6
- Inter-op threads: 1
- Batch: 1
- Gradient accumulation: 16
- Sequence length: 256
- Inference context: 384
- New tokens: 192
- AMP: disabled
- Bootstrap: `micro`
- Local research: `small`

## Storage

Prefer the fast NVMe data partition for active checkpoints/models/datasets. Use the HDD for archive workloads. The project falls back to the actual project directory when the preferred drive is unavailable.

## Privacy

Machine-unique identifiers supplied during diagnostics are not embedded in the source bundle or default hardware profile.
