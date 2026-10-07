$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $PSScriptRoot
$vendor = Join-Path $root "backend\vendor\llama.cpp\win-cuda"
New-Item -ItemType Directory -Force $vendor | Out-Null
$url = "https://github.com/ggml-org/llama.cpp/releases/download/b10343/llama-b10343-bin-win-cuda-12.4-x64.zip"
$zip = Join-Path $env:TEMP "ali-llama-b10343-cuda12.zip"
Write-Host "Downloading llama.cpp b10343 Windows x64 CUDA 12.4..."
Invoke-WebRequest -Uri $url -OutFile $zip
Expand-Archive -Path $zip -DestinationPath $vendor -Force
Remove-Item $zip -Force
Write-Host "llama.cpp installed under $vendor"
