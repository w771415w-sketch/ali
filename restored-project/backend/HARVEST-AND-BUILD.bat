@echo off
setlocal
chcp 65001 >nul
cd /d "%~dp0"
if not exist ".venv\Scripts\python.exe" call SETUP.bat
call ".venv\Scripts\activate.bat"
set "DATA_ROOT=%~1"
if "%DATA_ROOT%"=="" (
  echo Enter the folder that contains your books, conversations, documents or datasets.
  set /p "DATA_ROOT=Data folder: "
)
if "%DATA_ROOT%"=="" exit /b 1
python scripts\harvest.py "%DATA_ROOT%" --db artifacts\harvest.sqlite3 --export data\train
pause
