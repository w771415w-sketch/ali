$ErrorActionPreference = 'Stop'
$root = Split-Path -Parent $PSScriptRoot
Set-Location $root
$checks = @()
function Check($name, $ok, $detail) {
  $checks += [pscustomobject]@{ Name=$name; Status=($(if($ok){'PASS'}else{'FAIL'})); Detail=$detail }
  $script:results += [pscustomobject]@{ Name=$name; Status=($(if($ok){'PASS'}else{'FAIL'})); Detail=$detail }
}
$results=@()

$pyExe = Join-Path $root 'runtime\python\python.exe'
if (Test-Path $pyExe) {
  $ver = & $pyExe --version 2>&1
  Check 'Embedded Python' ($ver -match '3\.11\.9') $ver
} else { Check 'Embedded Python' $false 'runtime\python\python.exe missing' }

$node = Get-Command node -ErrorAction SilentlyContinue
if ($node) { Check 'Node 22' ((& node --version) -match '^v22\.') (& node --version) } else { Check 'Node 22' $false 'node.exe not found' }
$npm = Get-Command npm -ErrorAction SilentlyContinue
Check 'npm' ([bool]$npm) ($(if($npm){& npm --version}else{'npm.exe not found'}))
$dotnet = Get-Command dotnet -ErrorAction SilentlyContinue
if ($dotnet) {
  $dv = & dotnet --version
  Check '.NET 8 SDK' ($dv -match '^8\.') $dv
} else { Check '.NET 8 SDK' $false 'dotnet.exe not found' }

$nvidia = Get-Command nvidia-smi -ErrorAction SilentlyContinue
if ($nvidia) {
  $gpu = & nvidia-smi --query-gpu=name,memory.total,driver_version --format=csv,noheader,nounits 2>$null
  $ok = [bool]($gpu -match 'Quadro M1000M')
  Check 'NVIDIA Quadro M1000M' $ok $gpu
} else { Check 'NVIDIA Quadro M1000M' $false 'nvidia-smi not found' }

$nodeModules = Join-Path $root 'desktop\node_modules'
Check 'Electron dependencies' (Test-Path (Join-Path $nodeModules 'electron')) ($(if(Test-Path $nodeModules){'desktop\node_modules exists'}else{'run npm install in desktop'}))
Check 'node-pty native module' (Test-Path (Join-Path $nodeModules 'node-pty')) 'desktop\node_modules\node-pty'
Check 'Embedded Python site-packages' (Test-Path (Join-Path $root 'runtime\python\Lib\site-packages')) 'runtime\python\Lib\site-packages'
Check 'Required project folders' ((Test-Path 'backend') -and (Test-Path 'desktop') -and (Test-Path 'launcher') -and (Test-Path 'runtime')) 'backend/desktop/launcher/runtime'

$report = Join-Path $root 'FINAL_WINDOWS_RELEASE_GATE_REPORT.txt'
$results | Format-Table -AutoSize | Out-File -Encoding utf8 $report
$failed = @($results | Where-Object { $_.Status -eq 'FAIL' }).Count
$passed = @($results | Where-Object { $_.Status -eq 'PASS' }).Count
Write-Host "ALI Studio Pro 4.5.8 Windows Release Gate: PASS=$passed FAIL=$failed"
Write-Host "Report: $report"
if ($failed -gt 0) { exit 1 }
exit 0
