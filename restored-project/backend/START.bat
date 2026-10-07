@echo off
setlocal EnableExtensions
chcp 65001 >nul
cd /d "%~dp0"
title ALI AI

if not exist ".venv\Scripts\python.exe" (
  echo [START] Virtual environment not found. Running SETUP...
  call SETUP.bat
  if errorlevel 1 exit /b 1
)

call ".venv\Scripts\activate.bat"
if errorlevel 1 exit /b 1

python scripts\windows_preflight.py >nul 2>&1
if errorlevel 1 (
  echo.
  echo [START] Python environment is incomplete. Running SETUP / REPAIR...
  call SETUP.bat
  if errorlevel 1 exit /b 1
  call ".venv\Scripts\activate.bat"
  python scripts\windows_preflight.py >nul 2>&1
  if errorlevel 1 (
    echo.
    echo [ERROR] PyTorch or another required dependency is still missing.
    echo ALI AI was NOT launched to prevent another traceback.
    pause
    exit /b 1
  )
)

echo [START] Environment OK. Launching ALI AI...
python ali_ai.py
if errorlevel 1 (
  echo.
  echo [ERROR] ALI AI exited with an error.
  echo Run RUN-DOCTOR.bat for diagnostics.
  pause
  exit /b 1
)
