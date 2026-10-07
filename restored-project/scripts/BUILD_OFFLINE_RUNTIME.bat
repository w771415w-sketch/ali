@echo off
setlocal EnableExtensions
cd /d "%~dp0.."
echo [ALI] Preparing embedded Python 3.11.9 runtime and offline wheelhouse.
if not exist runtime\python\python.exe (
  echo [ERROR] Place the official Windows embeddable Python 3.11.9 package under runtime\python\ first.
  echo [ERROR] Then run this script again.
  exit /b 20
)
if not exist backend\wheelhouse mkdir backend\wheelhouse
if not exist backend\requirements-windows-legacy-gpu.txt (
  echo [ERROR] GPU requirements file missing.
  exit /b 22
)
echo [ALI] Runtime present. Use backend\SETUP-OFFLINE.bat after wheelhouse is populated.
exit /b 0
