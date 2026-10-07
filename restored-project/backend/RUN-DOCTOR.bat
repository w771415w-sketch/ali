@echo off
setlocal
chcp 65001 >nul
cd /d "%~dp0"
if not exist ".venv\Scripts\python.exe" call SETUP.bat
if errorlevel 1 exit /b 1
call ".venv\Scripts\activate.bat"
python scripts\windows_preflight.py
if errorlevel 1 exit /b 1
python scripts\doctor.py
pause
