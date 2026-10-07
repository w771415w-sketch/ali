param(
  [ValidateSet("dev", "start")]
  [string]$Mode = "dev"
)

$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
$Desktop = Join-Path $Root "restored-project\desktop"
$Package = Join-Path $Desktop "package.json"

if (-not (Test-Path $Package)) {
  throw "ALI desktop package was not found: $Package"
}

$Node = Get-Command node -ErrorAction SilentlyContinue
$Npm = Get-Command npm -ErrorAction SilentlyContinue
if (-not $Node -or -not $Npm) {
  throw "Node.js and npm are required. Install a supported Node.js LTS release first."
}

Set-Location $Desktop
if ($Mode -eq "dev") {
  npm run dev
} else {
  npm run start
}
