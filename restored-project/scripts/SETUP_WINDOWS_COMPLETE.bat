@echo off
setlocal EnableExtensions
chcp 65001 >nul
cd /d "%~dp0.."
echo ============================================================
echo ALI Studio Pro 4.5.8 - Complete Windows Setup
 echo ============================================================
where powershell >nul 2>&1 || (echo [ERROR] PowerShell is required.& exit /b 10)
where py >nul 2>&1 || (echo [ERROR] Python Launcher is required for build setup.& exit /b 11)
if not exist "runtime\python\python.exe" (
  echo [SETUP] Preparing embedded CPython 3.11.9...
  powershell -NoProfile -ExecutionPolicy Bypass -File "scripts\PREPARE_EMBEDDED_PYTHON_3119.ps1"
  if errorlevel 1 exit /b 12
)
call backend\SETUP.bat
if errorlevel 1 exit /b 20
call backend\SETUP-OPTIONAL.bat
if errorlevel 1 exit /b 21
call scripts\SETUP_QWEN_LOCAL.bat
if errorlevel 1 echo [WARN] Qwen/llama.cpp optional setup did not fully complete.
call scripts\VERIFY_ALL.bat
if errorlevel 1 exit /b 30
call scripts\BUILD_DESKTOP.bat
if errorlevel 1 exit /b 40
call scripts\BUILD_OFFLINE_RUNTIME.bat
if errorlevel 1 echo [WARN] Embedded runtime build step is a release-host task.
call scripts\BUILD_PORTABLE.bat
if errorlevel 1 exit /b 50
echo.
echo [OK] ALI Studio Pro 4.5.8 setup/build sequence completed.
exit /b 0
