@echo off
setlocal EnableExtensions
chcp 65001 >nul
cd /d "%~dp0"
echo ============================================================
echo ALI AI - Repair missing Python dependencies
echo ============================================================
call SETUP.bat
exit /b %errorlevel%
