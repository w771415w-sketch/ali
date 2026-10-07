@echo off
setlocal
cd /d "%~dp0.."
where dotnet >nul 2>&1 || (echo .NET 8 SDK is required.&exit /b 20)
if not exist runtime\python\python.exe echo WARNING: Embedded Python 3.11.9 is not present.
dotnet publish launcher\ALI.Portable.Launcher.csproj -c Release -r win-x64 --self-contained true /p:PublishSingleFile=true /p:IncludeNativeLibrariesForSelfExtract=true -o release\Launcher || exit /b 21
if not exist desktop\release\win-unpacked\ALI Studio Pro.exe (echo Build the Electron unpacked target first.&exit /b 22)
mkdir release\ALI-Studio-Pro >nul 2>&1
robocopy desktop\release\win-unpacked release\ALI-Studio-Pro\Desktop /E >nul
robocopy backend release\ALI-Studio-Pro\backend /E >nul
if exist runtime robocopy runtime release\ALI-Studio-Pro\runtime /E >nul
copy /Y release\Launcher\ALI-Portable.exe release\ALI-Studio-Pro\ALI-Portable.exe >nul
echo Portable package prepared at release\ALI-Studio-Pro\
