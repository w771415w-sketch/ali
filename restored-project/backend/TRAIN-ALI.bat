@echo off
setlocal
chcp 65001 >nul
cd /d "%~dp0"
if not exist ".venv\Scripts\python.exe" call SETUP.bat
call ".venv\Scripts\activate.bat"
python scripts\train_ali.py --scale small --train data\training\device_p50\chat_train.jsonl --validation data\training\device_p50\chat_validation.jsonl --output training\runs --dataset-mode chat
pause
