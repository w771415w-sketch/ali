$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $PSScriptRoot
$vendor = Join-Path $root "backend\vendor\llama.cpp\win-cpu"
New-Item -ItemType Directory -Force $vendor | Out-Null
$url = "https://github.com/ggml-org/llama.cpp/releases/download/b10343/llama-b10343-bin-win-cpu-x64.zip"
$zip = Join-Path $env:TEMP "ali-llama-b10343-cpu.zip"
Write-Host "Downloading llama.cpp b10343 Windows x64 CPU..."
Invoke-WebRequest -Uri $url -OutFile $zip -UseBasicParsing
Expand-Archive -Path $zip -DestinationPath $vendor -Force
Remove-Item $zip -Force
Write-Host "CPU llama.cpp installed under $vendor"
