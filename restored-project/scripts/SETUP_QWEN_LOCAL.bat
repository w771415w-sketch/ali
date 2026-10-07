@echo off
setlocal
cd /d "%~dp0.."
if not exist "backend\models\gguf" mkdir "backend\models\gguf"
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0DOWNLOAD_RECOMMENDED_MODEL.ps1"
if errorlevel 1 goto :fail
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0DOWNLOAD_LLAMA_CPP_WIN_CPU.ps1"
if errorlevel 1 goto :fail
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0DOWNLOAD_LLAMA_CPP_WIN_CUDA12.ps1"
if errorlevel 1 echo [WARN] CUDA llama.cpp download failed; CPU llama.cpp remains available.
echo.
echo [OK] Local Qwen + llama.cpp setup complete.
exit /b 0
:fail
echo [FAIL] Local Qwen setup failed. Read the message above.
exit /b 1
