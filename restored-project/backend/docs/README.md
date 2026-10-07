# ALI Studio Documentation

`ARCHITECTURE_2.0.md` describes the current system. Files named `V0.*` are historical reports from the original development stages.

The current release deliberately removes the old NumPy-only/fake-weight generator. The active training path is `model/ali_lm.py` + `training/` + `tokenizer/spm.py`.
