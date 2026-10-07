@echo off
setlocal
chcp 65001 >nul
cd /d "%~dp0"
if not exist ".venv\Scripts\python.exe" (call SETUP.bat)
if errorlevel 1 exit /b 1
call ".venv\Scripts\activate.bat"
python -c "import PyInstaller, tkinterdnd2" >nul 2>nul
if errorlevel 1 (
  echo [INFO] Installing PyInstaller + TkDnD...
  python -m pip install "pyinstaller>=6" "tkinterdnd2==0.6.3" --prefer-binary
  if errorlevel 1 goto fail
)
if exist build rmdir /s /q build
if exist dist\ALI-AI rmdir /s /q dist\ALI-AI
python -m PyInstaller --noconfirm --clean --windowed --name ALI-AI --onedir ^
  --collect-all tkinterdnd2 ^
  --add-data "control_plane\function_registry.json;control_plane" ^
  --add-data "config\default_config.json;config" ^
  --add-data "models\active\ALI-Bootstrap-v2.5;models\active\ALI-Bootstrap-v2.5" ^
  --add-data "phase2;phase2" ^
  ali_ai.py
if errorlevel 1 goto fail
if exist config xcopy /E /I /Y /Q config dist\ALI-AI\config >nul
if exist control_plane xcopy /E /I /Y /Q control_plane dist\ALI-AI\control_plane >nul
if exist data xcopy /E /I /Y /Q data dist\ALI-AI\data >nul
if exist models xcopy /E /I /Y /Q models dist\ALI-AI\models >nul
if exist phase2 xcopy /E /I /Y /Q phase2 dist\ALI-AI\phase2 >nul
if exist README_WINDOWS.md copy /Y README_WINDOWS.md dist\ALI-AI\README_WINDOWS.md >nul
echo @echo off>dist\ALI-AI\START-ALI-AI.bat
echo cd /d "%%~dp0">>dist\ALI-AI\START-ALI-AI.bat
echo start "ALI AI" "ALI-AI.exe">>dist\ALI-AI\START-ALI-AI.bat
echo.
echo [OK] Portable app created at dist\ALI-AI\
echo Run dist\ALI-AI\ALI-AI.exe or START-ALI-AI.bat
pause
exit /b 0
:fail
echo [ERROR] EXE build failed.
pause
exit /b 1
