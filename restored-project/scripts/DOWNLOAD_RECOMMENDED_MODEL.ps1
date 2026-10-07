$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $PSScriptRoot
$modelDir = Join-Path $root "backend\models\gguf"
New-Item -ItemType Directory -Force $modelDir | Out-Null
$url = "https://huggingface.co/second-state/Qwen2.5-0.5B-Instruct-GGUF/resolve/main/Qwen2.5-0.5B-Instruct-Q4_K_M.gguf?download=true"
$out = Join-Path $modelDir "Qwen2.5-0.5B-Instruct-Q4_K_M.gguf"
$expectedSha256 = "750f8f144f0504208add7897f01c7d2350a7363d8855eab59e137a1041e90394"
Write-Host "Downloading Qwen2.5-0.5B-Instruct Q4_K_M (398 MB)..."
Invoke-WebRequest -Uri $url -OutFile $out -UseBasicParsing
$size = (Get-Item $out).Length
if ($size -lt 380MB) { throw "Downloaded model looks incomplete: $size bytes" }
$hash = (Get-FileHash -Algorithm SHA256 -Path $out).Hash.ToLowerInvariant()
if ($hash -ne $expectedSha256) { throw "SHA256 mismatch: $hash" }
Write-Host "Model verified: $out ($([math]::Round($size/1MB,1)) MB)"
