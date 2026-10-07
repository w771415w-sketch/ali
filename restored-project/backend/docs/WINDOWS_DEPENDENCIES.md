# Windows dependencies

## Required
1. Windows 11 x64
2. Python 3.13.x x64
3. Internet access during first setup only, unless an offline Python wheel cache is supplied locally

`SETUP.bat` creates `.venv` and installs the pinned Python dependencies from `requirements-windows.txt`.

## Optional
- Git for repository operations
- A native GGUF runtime such as llama.cpp when using external GGUF models
- NVIDIA driver/CUDA is not required by the default P50 CPU-first training profile

## Portable EXE
Run `BUILD_EXE.bat` after setup. The project does not bundle Python, PyTorch wheels or GPU drivers because those are Windows/platform specific and large. The build script packages the application and project model assets into a Windows distribution folder.
