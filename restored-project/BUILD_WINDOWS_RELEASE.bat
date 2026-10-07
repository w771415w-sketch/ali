@echo off
setlocal EnableExtensions
chcp 65001 >nul
cd /d "%~dp0"
title ALI Studio Pro 4.6.0 - Windows Release Builder
set "BACKEND=%CD%\backend"
set "PY=%BACKEND%\.venv\Scripts\python.exe"
if not exist "%PY%" (
  call START_ALI_PRO.bat
  exit /b %errorlevel%
)
"%PY%" "%BACKEND%\scripts\windows_preflight.py"
if errorlevel 1 (
  call "%BACKEND%\SETUP.bat"
  if errorlevel 1 exit /b %errorlevel%
)
"%PY%" "%BACKEND%\scripts\verify_generation_lineage.py" --generation v4
if errorlevel 1 exit /b %errorlevel%
"%PY%" "%BACKEND%\scripts\package_generation.py" --generation v4
if errorlevel 1 exit /b %errorlevel%
echo.
echo [OK] V4 release package created under backend\releases\ALI-v4-Package
