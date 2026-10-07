@echo off
setlocal
chcp 65001 >nul
cd /d "%~dp0"
if not exist ".venv\Scripts\python.exe" call SETUP.bat
call ".venv\Scripts\activate.bat"
python scripts\hermes_doctor.py
if errorlevel 2 (
  echo.
  echo Hermes is not available at D:\AI ALI\Hermes\ yet.
  echo ALI AI remains usable independently.
)
pause
