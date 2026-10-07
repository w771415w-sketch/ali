@echo off
setlocal EnableExtensions
chcp 65001 >nul
cd /d "%~dp0"
if exist ".venv\Scripts\python.exe" (
  set "PY=.venv\Scripts\python.exe"
) else if exist "..\runtime\python\python.exe" (
  set "PY=..\runtime\python\python.exe"
) else (
  set "PY=py -3.11"
)
echo ================================================
echo ALI Studio Pro 4.5.2 - GPU Doctor
echo ================================================
%PY% -c "from runtime.hardware import detect,training_profile; import json; h=detect(force=True, probe_torch=True); print(json.dumps(h.to_dict(),ensure_ascii=False,indent=2)); print(json.dumps(training_profile(h),ensure_ascii=False,indent=2))"
if errorlevel 1 (
  echo [ERROR] GPU Doctor could not start the Python runtime.
  exit /b 1
)
echo.
echo Auto mode will use the GPU only after a real CUDA self-test and enough free VRAM.
echo On a 2GB Maxwell card the policy preserves headroom for Windows and other GPU processes.
pause
exit /b 0
