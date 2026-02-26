param(
    [switch]$OpenReleaseFolder
)

$ErrorActionPreference = "Stop"

function Write-Headline([string]$Text) {
    Write-Host "`n=== $Text ===" -ForegroundColor Cyan
}

function Write-Info([string]$Text) {
    Write-Host "[INFO] $Text" -ForegroundColor DarkCyan
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
        throw "Konnte __version__ in $Path nicht lesen."
    }
    return $match.Groups['ver'].Value
}

function Get-VersionFromPyProject([string]$Path) {
    if (-not (Test-Path $Path)) {
        throw "Datei nicht gefunden: $Path"
    }
    $content = Get-Content -Path $Path -Raw
    $match = [regex]::Match($content, '(?m)^version\s*=\s*"(?<ver>[^"]+)"')
    if (-not $match.Success) {
        throw "Konnte version in $Path nicht lesen."
    }
    return $match.Groups['ver'].Value
}

function Sync-PyProjectVersion([string]$Path, [string]$Version) {
    $content = Get-Content -Path $Path -Raw
    $updated = [regex]::Replace(
        $content,
        '(?m)^version\s*=\s*"[^"]+"',
        ("version = `"{0}`"" -f $Version),
        1
    )

    if ($updated -eq $content) {
        throw "Konnte version-Zeile in $Path nicht aktualisieren."
    }

    Set-Content -Path $Path -Value $updated -Encoding UTF8
}

Write-Headline "LittleOne Silent Release"

$repoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
Set-Location $repoRoot

$initPath = Join-Path $repoRoot "src\LittleOne\__init__.py"
$pyprojectPath = Join-Path $repoRoot "pyproject.toml"
$releaseScript = Join-Path $PSScriptRoot "release_new_version.ps1"

if (-not (Test-Path $releaseScript)) {
    throw "release_new_version.ps1 nicht gefunden: $releaseScript"
}

$versionInit = Get-VersionFromInit -Path $initPath
$versionPyproject = Get-VersionFromPyProject -Path $pyprojectPath

if ($versionPyproject -ne $versionInit) {
    Write-Info ("Synchronisiere pyproject.toml: {0} -> {1}" -f $versionPyproject, $versionInit)
    Sync-PyProjectVersion -Path $pyprojectPath -Version $versionInit
} else {
    Write-Info ("Version bereits synchron: {0}" -f $versionInit)
}

$releaseArgs = @("-NoPrompt")
if ($OpenReleaseFolder) {
    $releaseArgs += "-OpenReleaseFolder"
}

Write-Info "Starte automatischen Release-Flow (Build + Installer + Git + GitHub + Anleitungen)"
& powershell -ExecutionPolicy Bypass -File $releaseScript @releaseArgs

Write-Headline "Silent Release abgeschlossen"
