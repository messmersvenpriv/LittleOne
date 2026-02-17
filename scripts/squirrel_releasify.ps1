<#
Squirrel.Windows Packaging (Template)
#>
$ErrorActionPreference = "Stop"
if (-not (Test-Path .\dist\LittleOne.exe)) { Write-Host "dist\LittleOne.exe fehlt" -ForegroundColor Red; exit 1 }
$stage = Join-Path $PWD "stage"
if (Test-Path $stage) { Remove-Item $stage -Recurse -Force }
New-Item -ItemType Directory -Path $stage | Out-Null
Copy-Item .\dist\LittleOne.exe -Destination (Join-Path $stage "LittleOne.exe")
$releaseDir = Join-Path $PWD "Releases"
if (-not (Test-Path $releaseDir)) { New-Item -ItemType Directory -Path $releaseDir | Out-Null }
$sq = "Squirrel"
& $sq --releasify (Join-Path $stage "LittleOne.exe") --releaseDir $releaseDir 2>&1 | Write-Host
Write-Host "Fertig → Releases/ (Setup.exe, RELEASES, Delta-Pakete)"
