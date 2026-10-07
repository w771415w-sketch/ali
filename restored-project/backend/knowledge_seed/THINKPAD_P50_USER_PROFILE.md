# ALI Target Hardware Profile

## Lenovo ThinkPad P50
- Model: 20EQS2L900
- OS: Windows 11 Pro 10.0.26200 x64
- CPU: Intel Core i7-6820HQ, 4C/8T, 2.70 GHz
- RAM: 32 GB DDR4 2133 MHz
- GPU: NVIDIA Quadro M1000M, 2 GB GDDR5, Maxwell GM107, compute capability 5.0 reported for policy purposes
- iGPU: Intel HD Graphics 530
- Display: 1920x1080, 60 Hz, IPS FlexView
- SSD: WDC SN720 512 GB NVMe
- HDD: WDC WD20SPZX 2 TB SATA 5400 RPM
- Wi-Fi: Intel Dual Band Wireless-AC 8260
- CPU temperature reading from the report: 41.05 C
- Battery: 38%, approximately 42 minutes at the time of measurement

## Engineering policy
Use conservative GPU memory budgets. Prefer small quantized models for inference. Never assume all 2 GB VRAM is free. Probe CUDA with a real kernel self-test before GPU training. Fall back to CPU in Auto mode if CUDA initialization or memory allocation fails.

## Known measurement limits
Some values in the report (SSD TBW, Intel VRAM type, exact battery cell count) require dedicated tools and must not be invented.
