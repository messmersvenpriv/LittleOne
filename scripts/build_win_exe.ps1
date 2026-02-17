
# Nutzung: powershell -ExecutionPolicy Bypass -File scripts/build_win_exe.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt pyinstaller

# Clean
if (Test-Path dist) { Remove-Item dist -Recurse -Force }
if (Test-Path build) { Remove-Item build -Recurse -Force }

# Single-file EXE
pyinstaller --onefile --name kmz2dji src/main.py
Write-Host "Fertig: dist\kmz2dji.exe"
