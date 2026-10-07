@echo off
setlocal EnableExtensions EnableDelayedExpansion
chcp 65001 >nul
cd /d "%~dp0"
title ALI Studio Pro — Adaptive Hybrid
echo.
echo ================================================
echo   ALI Studio Pro — Adaptive Hybrid 4.6.0
echo   design4 UI
echo ================================================
echo.
if not exist "backend\scripts\desktop_server.py" (
  echo [ERROR] Backend files are missing.
  pause
  exit /b 1
)
if not exist "desktop\package.json" (
  echo [ERROR] Desktop files are missing.
  pause
  exit /b 1
)
if exist "runtime\python\python.exe" (
  echo [OK] Embedded Python runtime found.
) else (
  echo [WARN] Embedded Python runtime not found. Development fallback may be required.
)
if not exist "desktop\dist\index.html" (
  echo [INFO] Renderer build is not present.
  echo [INFO] Run scripts\BUILD_DESKTOP.bat on Windows once to create it.
)
if exist "launcher\ALI.Portable.Launcher.csproj" (
  echo [OK] Portable launcher source found.
)

where node >nul 2>&1
if errorlevel 1 (
  echo [ERROR] Node.js/npm was not found in PATH.
  echo         Install Node.js 20+ on Windows, then run this file again.
  pause
  exit /b 1
)
where npm >nul 2>&1
if errorlevel 1 (
  echo [ERROR] npm was not found in PATH.
  pause
  exit /b 1
)

if not exist "desktop\node_modules" (
  echo [INFO] Installing desktop dependencies...
  pushd desktop
  call npm install --no-audit --no-fund
  if errorlevel 1 (popd & echo [ERROR] npm install failed. & pause & exit /b 1)
  popd
)

if not exist "desktop\dist\index.html" (
  echo [INFO] Building the renderer...
  pushd desktop
  call npm run build
  if errorlevel 1 (popd & echo [ERROR] Renderer build failed. & pause & exit /b 1)
  popd
)

echo [INFO] Starting ALI Studio Pro...
pushd desktop
call npm start
set RC=!errorlevel!
popd
exit /b !RC!

if exist "python.exe" (
  python -m http.server 5173 --directory desktop
  exit /b !errorlevel!
)

echo [ERROR] No usable local launcher was found.
echo        Build the desktop renderer with scripts\BUILD_DESKTOP.bat.
pause
exit /b 1
