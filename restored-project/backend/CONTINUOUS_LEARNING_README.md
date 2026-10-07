# Continuous Learning Manager

`training/continuous_learning.py` is the Windows desktop training control layer.

It intentionally does not run training inside React. The Electron UI calls the local Python API, which queues a background training job. The real PyTorch/LoRA work remains in `training/pipeline.py` and `training/trainer.py`.

Generation aliases are stored in the normal `ModelRegistry` as `v1`, `v2`, ... and are promoted only after validation. The existing timestamped pipeline artifacts are kept underneath each generation for reproducibility.

The desktop UI starts the next cycle automatically by default after at least one new source is validated.
