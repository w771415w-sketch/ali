@echo off
setlocal EnableExtensions
cd /d "%~dp0"
if not exist ".venv\Scripts\python.exe" (
  echo [START] Offline venv is missing. Run Install\SETUP-ALL-OFFLINE.bat first.
  pause
  exit /b 1
)
.venv\Scripts\python.exe scripts\windows_preflight.py >nul 2>&1 || (
  echo [ERROR] Offline dependencies are incomplete.
  echo Run Install\SETUP-ALL-OFFLINE.bat after populating Offline_Packages.
  pause
  exit /b 1
)
.venv\Scripts\python.exe ali_ai.py
