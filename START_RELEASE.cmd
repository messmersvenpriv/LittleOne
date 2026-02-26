@echo off
setlocal
cd /d "%~dp0"

echo ======================================
echo LittleOne - Silent Release Start
echo ======================================
echo.

powershell -NoProfile -ExecutionPolicy Bypass -File ".\scripts\release_silent.ps1" -OpenReleaseFolder
set EXITCODE=%ERRORLEVEL%

echo.
if %EXITCODE%==0 (
    echo Release erfolgreich abgeschlossen.
) else (
    echo Release fehlgeschlagen. ExitCode: %EXITCODE%
)

pause
exit /b %EXITCODE%
