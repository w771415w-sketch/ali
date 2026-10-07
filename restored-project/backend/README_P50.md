# ALI AI 2.5 — ThinkPad P50 profile / Professional Assistant

This profile is tuned for the supplied ThinkPad P50 class: 4 physical / 8 logical CPU threads, 32 GB RAM and a 2 GB Quadro M1000M.

## Defaults

- Training: CPU-first
- Torch threads: 6
- Torch inter-op threads: 1
- Batch size: 1
- Gradient accumulation: 16
- Sequence length: 256
- Inference context: 384
- New tokens: 192
- AMP: disabled
- Bootstrap model: `micro`
- Local research model: `small`

## Data

`data/training/device_p50/` is included in this source bundle as a deterministic 600-record subset of the curriculum (480 train / 60 validation / 60 test). The full curriculum dataset is also included for longer training.

## Storage recommendation

Use the NVMe drive for active models, checkpoints and datasets. Use the HDD for archived checkpoints and older datasets. Do not put training checkpoints on the Windows system partition when a fast data partition is available.

## Commands
