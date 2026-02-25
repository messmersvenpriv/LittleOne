# Build GUI-Exe (One-File, Icon, windowed)
python -m pip install --upgrade pip
python -m pip install -r requirements.txt pyinstaller
if (Test-Path dist) { Remove-Item dist -Recurse -Force }
if (Test-Path build) { Remove-Item build -Recurse -Force }
$pyArgs = @("--onefile", "--windowed", "--name", "LittleOne")
if (Test-Path .\assets\app.ico) {
	$pyArgs += @("--icon", ".\assets\app.ico")
}
$pyArgs += ".\src\ui_app.py"
pyinstaller @pyArgs
Write-Host "Fertig: dist\LittleOne.exe"
