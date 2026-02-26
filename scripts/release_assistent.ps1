param(
    [switch]$SkipGit,
    [switch]$SkipGithub,
    [switch]$NoPrompt,
    [switch]$OpenReleaseFolder
)

$ErrorActionPreference = "Stop"

function Write-Headline([string]$Text) {
    Write-Host "`n=== $Text ===" -ForegroundColor Cyan
}

function Write-Info([string]$Text) {
    Write-Host "[INFO] $Text" -ForegroundColor DarkCyan
}

function Write-Ok([string]$Text) {
    Write-Host "[OK]   $Text" -ForegroundColor Green
}

function Write-Warn([string]$Text) {
    Write-Host "[WARN] $Text" -ForegroundColor Yellow
}

function Confirm-Continue([string]$Question, [bool]$DefaultYes = $true) {
    if ($NoPrompt) {
        return $true
    }

    $suffix = if ($DefaultYes) { "[Y/n]" } else { "[y/N]" }
    $answer = Read-Host "$Question $suffix"
    if ([string]::IsNullOrWhiteSpace($answer)) {
        return $DefaultYes
    }

    $normalized = $answer.Trim().ToLowerInvariant()
    return ($normalized -eq "y" -or $normalized -eq "yes" -or $normalized -eq "j" -or $normalized -eq "ja")
}

function Get-VersionValue([string]$Path, [string]$RegexPattern, [string]$Label) {
    if (-not (Test-Path $Path)) {
        throw "Datei nicht gefunden: $Path"
    }
    $content = Get-Content -Path $Path -Raw
    $match = [regex]::Match($content, $RegexPattern)
    if (-not $match.Success) {
        throw "Konnte $Label nicht auslesen: $Path"
    }
    return $match.Groups["ver"].Value
}

function Get-VersionFromInit([string]$Path) {
    if (-not (Test-Path $Path)) {
        throw "Datei nicht gefunden: $Path"
    }
    $content = Get-Content -Path $Path -Raw
    $match = [regex]::Match($content, "__version__\s*=\s*'(?<ver>[^']+)'")
    if (-not $match.Success) {
        $match = [regex]::Match($content, '__version__\s*=\s*"(?<ver>[^"]+)"')
    }
    if (-not $match.Success) {
        throw "Konnte __version__ nicht auslesen: $Path"
    }
    return $match.Groups["ver"].Value
}

Write-Headline "LittleOne Release-Assistent"

$repoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
Set-Location $repoRoot

$initPath = Join-Path $repoRoot "src\LittleOne\__init__.py"
$pyprojectPath = Join-Path $repoRoot "pyproject.toml"
$releaseScript = Join-Path $PSScriptRoot "release_new_version.ps1"

if (-not (Test-Path $releaseScript)) {
    throw "release_new_version.ps1 nicht gefunden: $releaseScript"
}

$versionInit = Get-VersionFromInit -Path $initPath
$versionPyProject = Get-VersionValue -Path $pyprojectPath -RegexPattern '(?m)^version\s*=\s*"(?<ver>[^"]+)"' -Label "pyproject version"

if ($versionInit -ne $versionPyProject) {
    throw "Versionskonflikt: __init__=$versionInit, pyproject=$versionPyProject"
}

$tag = "v$versionInit"

Write-Info "Gefundene Version: $versionInit"
Write-Info "Geplanter Tag     : $tag"

Write-Headline "Was dieses Programm automatisch macht"
Write-Host "1) Build von LittleOne.exe"
Write-Host "2) Erzeugt Installer + Update-Dateien (Squirrel)"
Write-Host "3) Erzeugt Versanddatei: Releases\\mail\\LittleOne-Setup.exe"
Write-Host "4) Git: add, commit, tag, push"
Write-Host "5) GitHub: Release mit Assets erstellen/aktualisieren"
Write-Host "6) Anleitung erzeugen: Releases\\release_instructions.md"

Write-Headline "Vor dem Start prüfen"
Write-Host "- Version wurde in src/LittleOne/__init__.py und pyproject.toml erhöht"
Write-Host "- Optional: gh auth login (für GitHub Release)"
Write-Host "- Optional: git status ist sauber"

if (-not (Confirm-Continue "Release jetzt starten?" $true)) {
    throw "Abgebrochen durch Benutzer."
}

$releaseArgs = @()
if ($SkipGit) { $releaseArgs += "-SkipGit" }
if ($SkipGithub) { $releaseArgs += "-SkipGithub" }
if ($NoPrompt) { $releaseArgs += "-NoPrompt" }
if ($OpenReleaseFolder) { $releaseArgs += "-OpenReleaseFolder" }

Write-Headline "Release läuft"
& powershell -ExecutionPolicy Bypass -File $releaseScript @releaseArgs

$releaseRoot = Join-Path $repoRoot "Releases"
$instructionsPath = Join-Path $releaseRoot "release_instructions.md"
$mailGuidePath = Join-Path $releaseRoot "mail\INSTALLATION_ANLEITUNG.txt"

Write-Headline "Nächste Schritte"
Write-Host "1) Prüfe die erzeugten Dateien in Releases\\"
Write-Host "2) Lies die Entwickleranleitung: $instructionsPath"
Write-Host "3) Sende an Anwender: Releases\\mail\\LittleOne-Setup.exe"
Write-Host "4) Sende optional mit: $mailGuidePath"
Write-Host "5) Anwender installiert per Doppelklick und nutzt später: Einstellungen -> Nach Updates suchen"

Write-Ok "Release-Assistent abgeschlossen."
