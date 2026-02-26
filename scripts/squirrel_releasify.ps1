<#
Squirrel.Windows Packaging (Template)
Erzeugt Installations- und Update-Artefakte unter Releases\squirrel
#>
$ErrorActionPreference = "Stop"

function Get-AppVersion {
	$initFile = Join-Path $PWD "src\LittleOne\__init__.py"
	if (-not (Test-Path $initFile)) {
		throw "Versionsdatei nicht gefunden: $initFile"
	}
	$content = Get-Content $initFile -Raw
	$match = [regex]::Match($content, "__version__\s*=\s*'(?<ver>[^']+)'")
	if (-not $match.Success) {
		$match = [regex]::Match($content, '__version__\s*=\s*"(?<ver>[^"]+)"')
	}
	if (-not $match.Success) {
		throw "Konnte __version__ aus $initFile nicht lesen."
	}
	return $match.Groups['ver'].Value
}

function Resolve-SquirrelCommand {
	$fromPath = Get-Command "Squirrel" -ErrorAction SilentlyContinue
	if ($fromPath) {
		return "Squirrel"
	}

	$toolsRoot = Join-Path $PWD "tools"
	$squirrelRoot = Join-Path $toolsRoot "squirrel"
	$localExe = Join-Path $squirrelRoot "Squirrel.exe"
	if (Test-Path $localExe) {
		return $localExe
	}

	if (-not (Test-Path $toolsRoot)) { New-Item -ItemType Directory -Path $toolsRoot | Out-Null }
	if (-not (Test-Path $squirrelRoot)) { New-Item -ItemType Directory -Path $squirrelRoot | Out-Null }

	$nugetUrl = "https://www.nuget.org/api/v2/package/squirrel.windows"
	$tmpNupkg = Join-Path $env:TEMP "squirrel.windows.nupkg"
	$tmpZip = Join-Path $env:TEMP "squirrel.windows.zip"
	$extractDir = Join-Path $env:TEMP "squirrel.windows.extract"

	Invoke-WebRequest -Uri $nugetUrl -OutFile $tmpNupkg -UseBasicParsing
	if (Test-Path $tmpZip) { Remove-Item $tmpZip -Force }
	Copy-Item $tmpNupkg $tmpZip -Force
	if (Test-Path $extractDir) { Remove-Item $extractDir -Recurse -Force }
	Expand-Archive -Path $tmpZip -DestinationPath $extractDir -Force

	$candidate = Get-ChildItem -Path $extractDir -Recurse -File -Filter "Squirrel.exe" |
		Sort-Object FullName |
		Select-Object -First 1
	if (-not $candidate) {
		throw "Konnte Squirrel.exe im NuGet-Paket nicht finden."
	}

	$sourceDir = Split-Path $candidate.FullName -Parent
	Copy-Item (Join-Path $sourceDir "*") -Destination $squirrelRoot -Recurse -Force
	if (-not (Test-Path $localExe)) {
		throw "Squirrel.exe konnte nicht nach $localExe kopiert werden."
	}
	return $localExe
}

function Resolve-NuGetCommand {
	$fromPath = Get-Command "nuget" -ErrorAction SilentlyContinue
	if ($fromPath) {
		return "nuget"
	}

	$toolsRoot = Join-Path $PWD "tools"
	$nugetDir = Join-Path $toolsRoot "nuget"
	$nugetExe = Join-Path $nugetDir "nuget.exe"
	if (Test-Path $nugetExe) {
		return $nugetExe
	}

	if (-not (Test-Path $nugetDir)) { New-Item -ItemType Directory -Path $nugetDir -Force | Out-Null }
	$nugetUrl = "https://dist.nuget.org/win-x86-commandline/latest/nuget.exe"
	Invoke-WebRequest -Uri $nugetUrl -OutFile $nugetExe -UseBasicParsing
	return $nugetExe
}

$distExe = Join-Path $PWD "dist\LittleOne.exe"
if (-not (Test-Path $distExe)) {
	Write-Host "dist\LittleOne.exe fehlt. Bitte zuerst build_gui_exe.ps1 ausführen." -ForegroundColor Red
	exit 1
}

$stage = Join-Path $PWD "stage"
if (Test-Path $stage) { Remove-Item $stage -Recurse -Force }
New-Item -ItemType Directory -Path $stage | Out-Null

$appVersion = Get-AppVersion
$pkgRoot = Join-Path $stage "pkg"
$libDir = Join-Path $pkgRoot "lib\net45"
New-Item -ItemType Directory -Path $libDir -Force | Out-Null
Copy-Item $distExe -Destination (Join-Path $libDir "LittleOne.exe") -Force

$nuspecPath = Join-Path $pkgRoot "LittleOne.nuspec"
@"
<?xml version="1.0"?>
<package>
	<metadata>
		<id>LittleOne</id>
		<version>$appVersion</version>
		<title>LittleOne</title>
		<authors>LittleOne Team</authors>
		<description>LittleOne Installer Package</description>
	</metadata>
	<files>
		<file src="lib\net45\LittleOne.exe" target="lib\net45" />
	</files>
</package>
"@ | Set-Content -Path $nuspecPath -Encoding UTF8

$nuget = Resolve-NuGetCommand
& $nuget pack $nuspecPath -BasePath $pkgRoot -OutputDirectory $stage -NoPackageAnalysis | Out-Host
$pkgNupkg = Join-Path $stage "LittleOne.$appVersion.nupkg"
if (-not (Test-Path $pkgNupkg)) {
	throw "NuGet-Paket wurde nicht erstellt: $pkgNupkg"
}

$releaseRoot = Join-Path $PWD "Releases"
if (-not (Test-Path $releaseRoot)) { New-Item -ItemType Directory -Path $releaseRoot | Out-Null }

$releaseDir = Join-Path $releaseRoot "squirrel"
if (Test-Path $releaseDir) { Remove-Item $releaseDir -Recurse -Force }
New-Item -ItemType Directory -Path $releaseDir | Out-Null

$sq = Resolve-SquirrelCommand
& $sq --releasify $pkgNupkg --releaseDir $releaseDir 2>&1 | Write-Host

$setupCandidates = @()
$setupCandidates += Join-Path $releaseDir "Setup.exe"
$setupCandidates += Join-Path $releaseDir "LittleOneSetup.exe"
$setupCandidates = @($setupCandidates | Where-Object { Test-Path $_ })

if ($setupCandidates.Count -gt 0) {
	$mailDir = Join-Path $releaseRoot "mail"
	if (-not (Test-Path $mailDir)) { New-Item -ItemType Directory -Path $mailDir | Out-Null }
	$mailSetup = Join-Path $mailDir "LittleOne-Setup.exe"
	Copy-Item $setupCandidates[0] -Destination $mailSetup -Force
	Write-Host "Fertig:"
	Write-Host " - Installer für Versand: $mailSetup"
	Write-Host " - Update-Artefakte: $releaseDir (RELEASES + *.nupkg)"
} else {
	Write-Host "Squirrel lief durch, aber Setup.exe wurde nicht gefunden. Prüfe Squirrel-Output in: $releaseDir" -ForegroundColor Yellow
}
