# Windows / ThinkPad P50 deployment profile

This build is tuned around a 4-core / 8-thread Intel Core i7-6820HQ class workstation with 32 GB DDR4 and a 2 GB Quadro M1000M class GPU.

Default policy:
- training device: CPU
- PyTorch threads: 6
- inter-op threads: 1
- batch size: 1
- gradient accumulation: 16
- sequence length: 256
- inference context: 384
- new tokens: 192
- AMP: disabled
- bootstrap scale: micro
- local research scale: small

The application never requires Hermes for normal ALI operation. The external path is configurable, with the default `D:\AI ALI\Hermes\`.

Hardware identifiers such as serial numbers, UUIDs and MAC addresses are intentionally not stored in the project configuration.
