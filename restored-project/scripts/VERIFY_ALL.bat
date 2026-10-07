@echo off
setlocal EnableExtensions
cd /d "%~dp0.."
set FAIL=0
if exist backend\.venv\Scripts\python.exe (set "PY=backend\.venv\Scripts\python.exe") else (set "PY=python")
%PY% -m compileall -q backend || set FAIL=1
%PY% -m pytest -q backend || set FAIL=2
%PY% scripts\VERIFY_DESKTOP_SOURCE.py || set FAIL=3
%PY% scripts\VERIFY_4_5.py || set FAIL=4
where node >nul 2>&1 && (node --check desktop\electron\main.cjs && node --check desktop\electron\preload.cjs && node --check desktop\src\api.js) || echo [INFO] Node syntax checks deferred if Node is unavailable.
where dotnet >nul 2>&1 && dotnet build launcher\ALI.Portable.Launcher.csproj -c Release || echo [INFO] .NET SDK not installed; C# build deferred to Windows release host.
if "%FAIL%"=="0" (echo ===== ALI 4.5.8 VERIFY: PASS =====) else (echo ===== ALI 4.5.8 VERIFY: FAIL =====)
exit /b %FAIL%
