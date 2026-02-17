# Build GUI-Exe (One-File, Icon, windowed)
python -m pip install --upgrade pip
python -m pip install -r requirements.txt pyinstaller
if (Test-Path dist) { Remove-Item dist -Recurse -Force }
if (Test-Path build) { Remove-Item build -Recurse -Force }
$iconParam = ""
if (Test-Path .\assets\app.ico) { $iconParam = "--icon .\assets\app.ico" }
pyinstaller --onefile --windowed --name Kitzrettung $iconParam .\src\ui_app.py
Write-Host "Fertig: dist\Kitzrettung.exe"
