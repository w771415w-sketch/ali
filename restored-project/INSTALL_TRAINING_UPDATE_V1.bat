@echo off
setlocal
cd /d "%~dp0"
set "PY=%~dp0runtime\python\python.exe"
if not exist "%PY%" set "PY=py -3.11"
if not exist "%~dp0backend\models\models.sqlite3" (
  echo [ERROR] ALI backend was not found.
  exit /b 1
)
echo [ALI] Installing Training Update v1 as Candidate...
%PY% "%~dp0backend\training\updates\v1\install_update_v1.py" "%~dp0"
if errorlevel 1 (
  echo [ERROR] Update installation failed.
  exit /b 1
)
echo [OK] v1 is installed as a Candidate. It was not promoted automatically.
pause
