# Schnellstart der GUI im venv
if (-not (Test-Path ".venv\Scripts\Activate.ps1")) {
  Write-Host "venv nicht gefunden. Bitte zuerst: python -m venv .venv" -ForegroundColor Yellow
  exit 1
}
. .\.venv\Scripts\Activate.ps1
python .\src\ui_app.py
