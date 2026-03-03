@echo off
setlocal
set "ROOT=%~dp0"
cd /d "%ROOT%"

set "PS_EXE=%SystemRoot%\System32\WindowsPowerShell\v1.0\powershell.exe"
if not exist "%PS_EXE%" (
    set "PS_EXE=pwsh"
)

echo ======================================
echo LittleOne - Silent Release Start
echo ======================================
echo.
echo Arbeitsordner: %CD%
echo Starte mit: %PS_EXE%

if not exist ".\scripts\release_silent.ps1" (
    echo [FEHLER] Skript nicht gefunden: .\scripts\release_silent.ps1
    pause
    exit /b 2
)

"%PS_EXE%" -NoLogo -NoProfile -ExecutionPolicy Bypass -File ".\scripts\release_silent.ps1" -OpenReleaseFolder
set EXITCODE=%ERRORLEVEL%

echo.
if %EXITCODE%==0 (
    echo [OK] Release erfolgreich abgeschlossen.
) else (
    echo [FEHLER] Release fehlgeschlagen. ExitCode: %EXITCODE%
    echo Hinweis: Details stehen in der PowerShell-Ausgabe oben.
)

pause
exit /b %EXITCODE%
