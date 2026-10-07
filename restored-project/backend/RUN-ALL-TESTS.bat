@echo off
setlocal
chcp 65001 >nul
cd /d "%~dp0"
if not exist ".venv\Scripts\activate.bat" call SETUP.bat
if errorlevel 1 exit /b 1
call ".venv\Scripts\activate.bat"
python -m pytest tests -q --disable-warnings
if errorlevel 1 (
  echo.
  echo [ERROR] Test suite contains failures.
  pause & exit /b 1
)
echo.
echo [OK] Test suite passed.
pause
