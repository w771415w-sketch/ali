# Active Models

`ALI-Bootstrap-v2.5/` is the included functional micro checkpoint used for desktop startup, local inference smoke tests and validating the training/registry lifecycle.

It was trained from scratch for a small CPU bootstrap run. It is deliberately labeled as a development bootstrap, not as a production-scale general assistant.

Larger HF/Safetensors or validated GGUF models can be imported through `models/inbox/` and the model manager without changing the application shell.
