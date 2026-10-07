@echo off
setlocal
cd /d "%~dp0..\desktop"
where node >nul 2>&1 || (echo Node.js 22 is required.&exit /b 10)
where npm >nul 2>&1 || (echo npm is required.&exit /b 11)
if not exist node_modules call npm install || exit /b 12
call npm run dist || exit /b 13
echo Electron portable package created under desktop\release\
