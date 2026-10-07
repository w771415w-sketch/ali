$ErrorActionPreference = "Stop"
$report = [ordered]@{}
$report.timestamp = (Get-Date).ToString("o")
$report.os = (Get-CimInstance Win32_OperatingSystem).Caption
$report.cpu = (Get-CimInstance Win32_Processor | Select-Object -First 1).Name
$report.ram_gb = [math]::Round(((Get-CimInstance Win32_ComputerSystem).TotalPhysicalMemory / 1GB), 2)
$report.gpu = @((Get-CimInstance Win32_VideoController | Select-Object -ExpandProperty Name))
$report.python = (Get-Command python -ErrorAction SilentlyContinue).Source
$report.git = (Get-Command git -ErrorAction SilentlyContinue).Source
$report.node = (Get-Command node -ErrorAction SilentlyContinue).Source

$python = Get-Command python -ErrorAction Stop
$env:PYTHONPATH = Join-Path $PSScriptRoot "..\backend"

& $python.Source (Join-Path $PSScriptRoot "..\backend\main.py") --self-test
if ($LASTEXITCODE -ne 0) { throw "ALI control-plane self-test failed" }

& $python.Source (Join-Path $PSScriptRoot "..\backend\main.py") --target-p50
if ($LASTEXITCODE -ne 0) { throw "ALI P50 deterministic gate failed" }

$report.result = "pass"
$report | ConvertTo-Json -Depth 5
