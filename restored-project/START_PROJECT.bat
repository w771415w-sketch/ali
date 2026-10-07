@echo off
setlocal EnableExtensions EnableDelayedExpansion
chcp 65001 >nul
title ALI Studio Pro 4.6.0 - Launcher

cd /d "%~dp0"
set "ROOT=%CD%"
set "BACKEND=%ROOT%\backend"
set "DESKTOP=%ROOT%\desktop"
set "VENV_PY=%BACKEND%\.venv\Scripts\python.exe"

 echo ============================================================
 echo  ALI Studio Pro 4.6.0 - Cumulative AI Workstation
 echo ============================================================
 echo.

echo [1/4] Checking Python runtime...
if exist "%VENV_PY%" goto :PY_OK
where py >nul 2>&1
if errorlevel 1 goto :ERR_PY
py -3.11 -m venv "%BACKEND%\.venv"
if errorlevel 1 goto :ERR_PY
:PY_OK

echo [2/4] Checking required Python packages...
"%VENV_PY%" -c "import torch,numpy,psutil,safetensors,sentencepiece" >nul 2>&1
if errorlevel 1 (
  echo       Installing/updating core packages...
  if exist "%BACKEND%\wheelhouse\*.whl" (
    "%VENV_PY%" -m pip install --no-index --find-links "%BACKEND%\wheelhouse" -r "%BACKEND%\requirements-core.txt"
  ) else (
    "%VENV_PY%" -m pip install --disable-pip-version-check --prefer-binary -r "%BACKEND%\requirements-core.txt"
  )
  if errorlevel 1 goto :ERR_DEPS
)
"%VENV_PY%" -c "import tkinterdnd2" >nul 2>&1
if errorlevel 1 "%VENV_PY%" -m pip install --disable-pip-version-check --prefer-binary tkinterdnd2==0.6.3 >nul 2>&1

echo [3/4] Running Windows preflight...
"%VENV_PY%" "%BACKEND%\scripts\windows_preflight.py"
if errorlevel 1 goto :ERR_PREFLIGHT

echo.
echo [4/4] Starting ALI Studio Pro...

set "PACKAGED=%DESKTOP%\release\win-unpacked\ALI Studio Pro.exe"
set "ELECTRON=%DESKTOP%\node_modules\.bin\electron.cmd"

if exist "%PACKAGED%" (
  echo       Found packaged desktop.
  start "ALI Studio Pro" /wait "%PACKAGED%"
  exit /b %errorlevel%
)

if exist "%ELECTRON%" (
  echo       Found local Electron dependencies.
  set "ALI_FORCE_PROD=1"
  pushd "%DESKTOP%"
  call "%ELECTRON%" .
  set "EC=%errorlevel%"
  popd
  exit /b %EC%
)

echo [WARN] Electron desktop is not built yet.
echo [WARN] Launching the canonical Python desktop control center.
pushd "%BACKEND%"
call START.bat
set "EC=%errorlevel%"
popd
exit /b %EC%

:ERR_PY
echo [ERROR] Python 3.11 x64 is required and could not be prepared.
echo         Install Python 3.11 from python.org, then run this file again.
pause
exit /b 10

:ERR_DEPS
echo [ERROR] Required Python packages could not be installed.
echo         Check backend\wheelhouse or Internet access.
pause
exit /b 11

:ERR_PREFLIGHT
echo [ERROR] ALI preflight failed. The application was not launched.
echo         Run backend\RUN-DOCTOR.bat for diagnostics.
pause
exit /b 12
