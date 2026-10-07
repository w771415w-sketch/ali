# ALI Target Hardware — Lenovo ThinkPad P50 (User-provided profile)

## System
- Manufacturer: LENOVO
- Model: ThinkPad P50 — 20EQS2L900
- Chassis serial: L1HF6CH036A
- Product ID: PC0J8H3F
- System UUID: DFBD464C-2222-11B2-A85C-ED47CEA099E4
- Device type: Mobile Workstation, x64
- Motherboard: LENOVO 20EQS2L900 — SDK0J40697 WIN
- BIOS: LENOVO N1EETA2W, version 1.75 (18 Mar 2024)

## Operating system
- Windows 11 Pro, build 10.0.26200, 64-bit
- UI/input locale: ar-SA
- User report installation date: 27 Jul 2026
- User report last boot: 30 Sep 2026, 19:39

## CPU
- Intel Core i7-6820HQ, Skylake
- 4 physical cores / 8 logical threads
- Base 2.70 GHz; reported current 1.51 GHz
- VT-x enabled
- L1 128 KB/core, L2 1 MB, L3 8 MB
- Processor ID: BFEBFBFF000506E3
- Socket: U3E1
- Reported CPU temperature: 41.05 C
- Raw temperature reading: 3142 in Kelvin x10; 314.2 K -> 41.05 C

## RAM
- 32 GB DDR4, 2 x 16 GB
- 2133 MHz PC4-17000
- SK Hynix HMA82GS6AFR8N-UH
- SODIMM, dual channel

## Storage
- SSD: WDC PC SN720 SDAPNTW-512G-1006, 512 GB NVMe, GPT
- User report partitions: C 152 GB, D 322 GB
- SSD health: reported Healthy
- HDD: WDC WD20SPZX-22UA7T0, 2 TB SATA 5400 RPM, MBR
- User report partitions: F 1.67 TB, G 194 GB
- HDD health: reported Healthy

## GPU
- NVIDIA Quadro M1000M, Maxwell GM107
- 2 GB GDDR5
- PCI: VEN_10DE & DEV_13B1
- User report driver: 31.0.15.3818
- Compute capability used by ALI policy: 5.0
- Intel HD Graphics 530 integrated GPU
- Intel iGPU shared memory: reported 1 GB

## Display / I/O / Network
- 1920x1080 @ 60 Hz, IPS FlexView
- Lenovo display model LEN40BA
- Realtek High Definition Audio
- Arabic Enhanced 101/102 keyboard
- Synaptics TrackPoint + Touchpad
- Intel Wireless-AC 8260; reported active speed 72.2 Mbps; max 867 Mbps
- Intel I219-LM Ethernet
- Bluetooth available

## Power
- Lenovo battery 00NY493, reported 90 Wh original
- User report at measurement: 38%, about 42 minutes remaining

## Engineering policy
- Auto compute mode must never assume the entire 2 GB VRAM is free.
- Probe actual CUDA operation and free VRAM before GPU training.
- When VRAM is shared, select a smaller workload rather than stealing all memory.
- On 2 GB-class GPUs use batch 1, bounded sequence length, gradient accumulation and memory headroom.
- If CUDA or memory allocation fails in Auto mode, fall back to CPU and report the reason.

## Measurement limits
The following are not to be invented from this report alone: Intel iGPU VRAM type, SSD TBW/SMART endurance, exact battery cell count, and exact CUDA-core count from WMI alone. Dedicated tools are required for those measurements.
