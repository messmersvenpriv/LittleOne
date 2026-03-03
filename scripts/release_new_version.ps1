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

function Write-Step([string]$Text) {
    Write-Host "[STEP] $Text" -ForegroundColor DarkCyan
}

function Write-Ok([string]$Text) {
    Write-Host "[OK]   $Text" -ForegroundColor Green
}

function Write-Warn([string]$Text) {
    Write-Host "[WARN] $Text" -ForegroundColor Yellow
}

function Confirm-Action([string]$Question, [bool]$DefaultYes = $true) {
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

function Require-Command([string]$Name) {
    $cmd = Get-Command $Name -ErrorAction SilentlyContinue
    if (-not $cmd) {
        throw "Command '$Name' not found."
    }
}

function Resolve-GhCommand([string]$RepoRoot) {
    $fromPath = Get-Command "gh" -ErrorAction SilentlyContinue
    if ($fromPath) {
        return "gh"
    }

    $toolsRoot = Join-Path $RepoRoot "tools"
    $ghRoot = Join-Path $toolsRoot "gh"
    $localGh = Join-Path $ghRoot "bin\gh.exe"
    if (Test-Path $localGh) {
        return $localGh
    }

    if (-not (Test-Path $toolsRoot)) {
        New-Item -ItemType Directory -Path $toolsRoot -Force | Out-Null
    }
    if (-not (Test-Path $ghRoot)) {
        New-Item -ItemType Directory -Path $ghRoot -Force | Out-Null
    }

    $releaseInfo = Invoke-RestMethod -Uri "https://api.github.com/repos/cli/cli/releases/latest"
    $asset = $releaseInfo.assets |
        Where-Object { $_.name -match '^gh_.*_windows_amd64\.zip$' } |
        Select-Object -First 1

    if (-not $asset) {
        throw "Could not find a windows_amd64 gh zip asset in latest release metadata."
    }

    $tmpZip = Join-Path $env:TEMP $asset.name
    $extractDir = Join-Path $env:TEMP ("gh_extract_{0}" -f [guid]::NewGuid().ToString("N"))

    Invoke-WebRequest -Uri $asset.browser_download_url -OutFile $tmpZip -UseBasicParsing
    if (Test-Path $extractDir) {
        Remove-Item $extractDir -Recurse -Force
    }
    Expand-Archive -Path $tmpZip -DestinationPath $extractDir -Force

    $candidate = Get-ChildItem -Path $extractDir -Recurse -File -Filter "gh.exe" |
        Select-Object -First 1
    if (-not $candidate) {
        throw "Downloaded gh package did not contain gh.exe"
    }

    $sourceBin = Split-Path $candidate.FullName -Parent
    $targetBin = Join-Path $ghRoot "bin"
    if (-not (Test-Path $targetBin)) {
        New-Item -ItemType Directory -Path $targetBin -Force | Out-Null
    }
    Copy-Item -Path (Join-Path $sourceBin "*") -Destination $targetBin -Recurse -Force

    if (-not (Test-Path $localGh)) {
        throw "gh bootstrap failed: $localGh not found"
    }

    return $localGh
}

function Get-VersionFromInit([string]$Path) {
    if (-not (Test-Path $Path)) {
        throw "File not found: $Path"
    }
    $content = Get-Content -Path $Path -Raw
    $match = [regex]::Match($content, "__version__\s*=\s*'(?<ver>[^']+)'")
    if (-not $match.Success) {
        $match = [regex]::Match($content, '__version__\s*=\s*"(?<ver>[^"]+)"')
    }
    if (-not $match.Success) {
        throw "Could not read __version__ from $Path"
    }
    return $match.Groups["ver"].Value
}

function Get-VersionFromPyProject([string]$Path) {
    if (-not (Test-Path $Path)) {
        throw "File not found: $Path"
    }
    $content = Get-Content -Path $Path -Raw
    $match = [regex]::Match($content, '(?m)^version\s*=\s*"(?<ver>[^"]+)"')
    if (-not $match.Success) {
        throw "Could not read version from $Path"
    }
    return $match.Groups["ver"].Value
}

function Write-TextFile([string]$Path, [string]$Content) {
    $dir = Split-Path -Path $Path -Parent
    if (-not (Test-Path $dir)) {
        New-Item -ItemType Directory -Path $dir -Force | Out-Null
    }
    Set-Content -Path $Path -Value $Content -Encoding UTF8
}

function New-ReleaseInstructions(
    [string]$Version,
    [string]$Tag,
    [string]$Branch,
    [string]$SetupPath,
    [string]$ReleaseIndexPath,
    [string[]]$Packages
) {
    $lines = New-Object System.Collections.Generic.List[string]
    $lines.Add("# LittleOne Release Guide ($Version)")
    $lines.Add("")
    $lines.Add(("Generated: {0}" -f (Get-Date -Format "yyyy-MM-dd HH:mm")))
    $lines.Add("")
    $lines.Add("## Developer steps")
    $lines.Add("1. Bump version in src/LittleOne/__init__.py and pyproject.toml")
    $lines.Add("2. Run: powershell -ExecutionPolicy Bypass -File .\\scripts\\release_new_version.ps1")
    $lines.Add("3. Verify artifacts:")
    $lines.Add(("   - {0}" -f $SetupPath))
    $lines.Add(("   - {0}" -f $ReleaseIndexPath))
    if ($Packages -and $Packages.Count -gt 0) {
        foreach ($pkg in $Packages) {
            $lines.Add(("   - {0}" -f $pkg))
        }
    } else {
        $lines.Add("   - (no .nupkg files found)")
    }
    $lines.Add(("4. Verify GitHub release/tag: {0} on branch {1}" -f $Tag, $Branch))
    $lines.Add("5. Send mail/LittleOne-Setup.exe to users")
    $lines.Add("")
    $lines.Add("## End-user install")
    $lines.Add("1. Download LittleOne-Setup.exe")
    $lines.Add("2. Double-click the installer")
    $lines.Add("3. Confirm Windows security dialog if shown")
    $lines.Add("4. Start LittleOne from Start Menu")
    $lines.Add("")
    $lines.Add("## How updates work")
    $lines.Add("- In app: Einstellungen -> Nach Updates suchen")
    $lines.Add("- App checks latest GitHub release")
    $lines.Add("- App downloads Setup*.exe and starts installer")
    $lines.Add("- Keep Setup.exe, RELEASES and .nupkg assets in release")

    return ($lines -join "`r`n")
}

function New-ReleaseNotesTemplate([string]$Version, [string]$Tag) {
    $lines = @(
        ("# LittleOne {0}" -f $Tag),
        "",
        "## Highlights",
        "- ",
        "",
        "## Fixes",
        "- ",
        "",
        "## Installation",
        "- New users: download and run LittleOne-Setup.exe",
        "- Existing users: use Einstellungen -> Nach Updates suchen",
        "",
        "## Assets",
        "- Setup.exe or LittleOneSetup.exe",
        "- RELEASES",
        ("- LittleOne.{0}-full.nupkg" -f $Version),
        ("- optional LittleOne.{0}-delta.nupkg" -f $Version)
    )
    return ($lines -join "`r`n")
}

Write-Headline "LittleOne one-click release"

$repoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
Set-Location $repoRoot

$initPath = Join-Path $repoRoot "src\LittleOne\__init__.py"
$pyprojectPath = Join-Path $repoRoot "pyproject.toml"
$buildScript = Join-Path $repoRoot "scripts\build_gui_exe.ps1"
$squirrelScript = Join-Path $repoRoot "scripts\squirrel_releasify.ps1"

Write-Step "Check requirements"
Require-Command "git"
$ghCmd = $null
if (-not $SkipGithub) {
    try {
        $ghCmd = Resolve-GhCommand -RepoRoot $repoRoot
        Write-Ok ("GitHub CLI: {0}" -f $ghCmd)
    } catch {
        Write-Warn ("GitHub CLI could not be resolved: {0}" -f $_.Exception.Message)
        Write-Warn "Skipping GitHub release step."
        $SkipGithub = $true
    }
}

$versionInit = Get-VersionFromInit $initPath
$versionPyProject = Get-VersionFromPyProject $pyprojectPath
if ($versionInit -ne $versionPyProject) {
    throw "Version mismatch: __init__=$versionInit, pyproject=$versionPyProject"
}

$version = $versionInit
$tag = "v$version"
$branch = (& git rev-parse --abbrev-ref HEAD).Trim()

Write-Ok ("Version: {0}" -f $version)
Write-Ok ("Branch : {0}" -f $branch)

$statusShort = (& git status --porcelain)
if ($statusShort -and -not $NoPrompt) {
    Write-Warn "Uncommitted changes exist before release build."
    if (-not (Confirm-Action "Continue anyway?" $false)) {
        throw "Aborted by user."
    }
}

Write-Step "Build portable exe"
if (-not (Test-Path $buildScript)) {
    throw "Missing script: $buildScript"
}
& powershell -ExecutionPolicy Bypass -File $buildScript

Write-Step "Build installer/update artifacts"
if (-not (Test-Path $squirrelScript)) {
    throw "Missing script: $squirrelScript"
}
& powershell -ExecutionPolicy Bypass -File $squirrelScript

$releaseRoot = Join-Path $repoRoot "Releases"
$releaseDir = Join-Path $releaseRoot "squirrel"
$mailSetup = Join-Path $releaseRoot "mail\LittleOne-Setup.exe"
$releaseIndex = Join-Path $releaseDir "RELEASES"

if (-not (Test-Path (Join-Path $repoRoot "dist\LittleOne.exe"))) {
    throw "Build failed: dist\\LittleOne.exe missing"
}
if (-not (Test-Path $releaseDir)) {
    throw "Missing release directory: $releaseDir"
}

$nupkgs = @(Get-ChildItem -Path $releaseDir -File -Filter "*.nupkg" -ErrorAction SilentlyContinue | ForEach-Object { $_.Name })

Write-Step "Write release guides"
$instructionsPath = Join-Path $releaseRoot "release_instructions.md"
$mailGuidePath = Join-Path $releaseRoot "mail\INSTALLATION_ANLEITUNG.txt"
$notesPath = Join-Path $releaseRoot ("release_notes_{0}.md" -f $tag)

$instructions = New-ReleaseInstructions -Version $version -Tag $tag -Branch $branch -SetupPath $mailSetup -ReleaseIndexPath $releaseIndex -Packages $nupkgs
Write-TextFile -Path $instructionsPath -Content $instructions

$mailGuide = @(
    ("LittleOne Installation (Version {0})" -f $version),
    "",
    "1) Download LittleOne-Setup.exe",
    "2) Double-click installer",
    "3) Confirm security prompt",
    "4) Start LittleOne from Start Menu",
    "",
    "Updates:",
    "- In app: Einstellungen -> Nach Updates suchen",
    "- Confirm update dialog when newer version exists",
    "",
    "Support:",
    "- GitHub: https://github.com/messmersvenpriv/LittleOne"
) -join "`r`n"
Write-TextFile -Path $mailGuidePath -Content $mailGuide

if (-not (Test-Path $notesPath)) {
    Write-TextFile -Path $notesPath -Content (New-ReleaseNotesTemplate -Version $version -Tag $tag)
}

Write-Ok ("Guide created: {0}" -f $instructionsPath)
Write-Ok ("User guide : {0}" -f $mailGuidePath)
Write-Ok ("Release note: {0}" -f $notesPath)

if (-not $SkipGit) {
    Write-Step "Git add/commit/tag/push"
    & git add -A

    $staged = (& git diff --cached --name-only)
    if ($staged) {
        $message = "release: $tag"
        if (-not $NoPrompt) {
            $custom = Read-Host "Commit message (Enter for '$message')"
            if (-not [string]::IsNullOrWhiteSpace($custom)) {
                $message = $custom.Trim()
            }
        }
        & git commit -m $message
        Write-Ok "Commit done"
    } else {
        Write-Warn "No staged changes for commit"
    }

    $existingTag = (& git tag --list $tag)
    if (-not $existingTag) {
        & git tag -a $tag -m "Release $tag"
        Write-Ok ("Tag created: {0}" -f $tag)
    } else {
        Write-Warn ("Tag already exists: {0}" -f $tag)
    }

    if (Confirm-Action ("Push branch '{0}' and tag '{1}'?" -f $branch, $tag) $true) {
        & git push origin $branch
        & git push origin $tag
        Write-Ok "Git push done"
    } else {
        Write-Warn "Git push skipped"
    }
}

if (-not $SkipGithub) {
    Write-Step "GitHub release create/update"
    & $ghCmd auth status 1>$null 2>$null
    if ($LASTEXITCODE -ne 0) {
        Write-Warn "gh not authenticated. Run: gh auth login"
    } else {
        $assets = @()
        $setupCandidates = @(
            (Join-Path $releaseDir "Setup.exe"),
            (Join-Path $releaseDir "LittleOneSetup.exe"),
            $mailSetup,
            $releaseIndex
        ) | Where-Object { Test-Path $_ }

        $assets += $setupCandidates
        $assets += @(Get-ChildItem -Path $releaseDir -File -Filter "*.nupkg" -ErrorAction SilentlyContinue | ForEach-Object { $_.FullName })
        $assets = @($assets | Select-Object -Unique)

        if ($assets.Count -eq 0) {
            Write-Warn "No release assets found. Skip GitHub release."
        } else {
            $releaseExists = $false
            try {
                & $ghCmd release view $tag --json name 1>$null 2>$null
                $releaseExists = ($LASTEXITCODE -eq 0)
            } catch {
                $releaseExists = $false
            }

            if (-not $releaseExists) {
                & $ghCmd release create $tag --title ("LittleOne {0}" -f $tag) --notes-file $notesPath @assets
                Write-Ok ("GitHub release created: {0}" -f $tag)
            } else {
                & $ghCmd release upload $tag @assets --clobber
                Write-Ok ("GitHub release assets updated: {0}" -f $tag)
            }
        }
    }
}

Write-Headline "Done"
Write-Host ("Version: {0}" -f $version)
Write-Host ("Branch : {0}" -f $branch)
Write-Host ("Guide  : {0}" -f $instructionsPath)
Write-Host ("User   : {0}" -f $mailGuidePath)
Write-Host ("Assets : {0}" -f $releaseDir)

if ($OpenReleaseFolder) {
    Start-Process explorer.exe $releaseRoot
}
