@echo off
setlocal
cd /d "%~dp0"
if not exist ".venv\Scripts\python.exe" call SETUP.bat
call ".venv\Scripts\activate.bat"
python -m pytest tests -q --disable-warnings
pause
