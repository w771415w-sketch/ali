\
@echo off
setlocal EnableExtensions
chcp 65001 >nul
cd /d "%~dp0"
title ALI AI - Windows Setup / Repair
where py >nul 2>nul
if errorlevel 1 (
  echo [ERROR] Python Launcher (py) was not found.
  echo Install Python 3.11.x 64-bit or use the bundled embedded runtime on a production build.
  pause
  exit /b 1
)
if not exist ".venv\Scripts\python.exe" (
  echo [SETUP] Creating Python 3.11 virtual environment...
  py -3.11 -m venv .venv
  if errorlevel 1 goto fail
)
call ".venv\Scripts\activate.bat"
if errorlevel 1 goto fail
python -m pip install --upgrade pip
if errorlevel 1 goto fail

echo [SETUP] Installing safe CPU baseline dependencies...
python -m pip install --disable-pip-version-check --prefer-binary "numpy>=2.0,<3" "psutil>=7,<8" "safetensors>=0.7,<1" "sentencepiece>=0.2,<1" "pytest>=9,<10"
if errorlevel 1 goto fail

echo [SETUP] Probing NVIDIA GPU...
where nvidia-smi >nul 2>nul
if not errorlevel 1 (
  nvidia-smi --query-gpu=name,memory.total,driver_version --format=csv,noheader > "%TEMP%\ali_gpu.txt" 2>nul
  findstr /i "M1000M Maxwell Quadro" "%TEMP%\ali_gpu.txt" >nul 2>nul
  if not errorlevel 1 (
    echo [SETUP] Legacy NVIDIA GPU detected. Trying PyTorch CUDA wheel...
    python -m pip install --disable-pip-version-check --prefer-binary -r requirements-windows-legacy-gpu.txt
    if errorlevel 1 (
      echo [WARN] CUDA wheel could not be installed. Falling back to CPU torch so the app remains usable.
      python -m pip install --disable-pip-version-check --prefer-binary "torch==2.14.0" --index-url https://download.pytorch.org/whl/cpu
      if errorlevel 1 goto fail
    )
    goto deps
  )
)
echo [SETUP] Installing PyTorch CPU fallback...
python -m pip install --disable-pip-version-check --prefer-binary "torch==2.14.0" --index-url https://download.pytorch.org/whl/cpu
if errorlevel 1 goto fail
:deps
python -m pip install --disable-pip-version-check --prefer-binary -r requirements-windows.txt
if errorlevel 1 goto fail
python scripts\windows_preflight.py
if errorlevel 1 goto fail
python scripts\configure_device.py
if errorlevel 1 goto fail
python scripts\doctor.py
if errorlevel 1 goto fail
python scripts\kca_doctor.py
if errorlevel 1 goto fail
python scripts\release_check.py
if errorlevel 1 goto fail
python -m pip check
if errorlevel 1 goto fail
echo.
echo [OK] ALI AI Windows environment is ready.
echo Run START.bat to launch.
exit /b 0
:fail
echo.
echo [ERROR] Setup/repair failed. The application was not launched.
pause
exit /b 1
