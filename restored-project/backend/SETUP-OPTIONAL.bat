@echo off
setlocal
chcp 65001 >nul
cd /d "%~dp0"
if not exist ".venv\Scripts\python.exe" call SETUP.bat
call ".venv\Scripts\activate.bat"
python -m pip install -r requirements-optional.txt
if errorlevel 1 goto fail
echo [OK] Optional ALI AI packages installed.
pause
exit /b 0
:fail
echo [ERROR] Optional package installation failed.
pause
exit /b 1
