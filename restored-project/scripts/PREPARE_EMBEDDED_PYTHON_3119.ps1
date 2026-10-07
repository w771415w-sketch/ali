$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $PSScriptRoot
$runtime = Join-Path $root "runtime\python"
$url = "https://www.python.org/ftp/python/3.11.9/python-3.11.9-embed-amd64.zip"
$tmp = Join-Path $env:TEMP "python-3.11.9-embed-amd64.zip"
New-Item -ItemType Directory -Force $runtime | Out-Null
Write-Host "Preparing Embedded CPython 3.11.9..."
Invoke-WebRequest -Uri $url -OutFile $tmp -UseBasicParsing
Expand-Archive -Path $tmp -DestinationPath $runtime -Force
Remove-Item $tmp -Force
$pth = Get-ChildItem $runtime -Filter "python*._pth" | Select-Object -First 1
if (-not $pth) { throw "Embedded Python ._pth file not found." }
$lines = Get-Content $pth.FullName
if ($lines -notcontains "Lib\site-packages") { Add-Content $pth.FullName "Lib\site-packages" }
if ($lines -notcontains "import site") { Add-Content $pth.FullName "import site" }
Write-Host "Embedded Python prepared: $runtime"
