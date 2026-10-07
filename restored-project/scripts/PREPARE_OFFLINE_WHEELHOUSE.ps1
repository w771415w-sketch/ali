$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $PSScriptRoot
$wheel = Join-Path $root "offline\wheels\py311-win_amd64"
New-Item -ItemType Directory -Force $wheel | Out-Null
$py = Join-Path $root "backend\.venv\Scripts\python.exe"
if (-not (Test-Path $py)) { $py = "py" }
Write-Host "Downloading Windows CPython 3.11 wheels into $wheel"
& $py -m pip download --only-binary=:all: --platform win_amd64 --python-version 311 --implementation cp --abi cp311 -r (Join-Path $root "backend\requirements-windows.txt") -d $wheel
Write-Host "Downloading PyTorch CUDA/CPU wheel(s) separately according to your chosen policy."
Write-Host "For offline CUDA, use backend/requirements-windows-legacy-gpu.txt on a connected Windows build host."
Write-Host "Wheelhouse ready. Copy the whole offline folder with the release." 
