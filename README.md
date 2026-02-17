# Kitzrettung KMZ/KML Tool – GUI

## Entwicklung: GUI schnell starten
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python .\src\ui_app.py
```
Oder in VS Code: **Run and Debug → „Run GUI (PySide6)“**.

## EXE bauen (zum Weitergeben)
```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\build_gui_exe.ps1
# Ergebnis: .\dist\Kitzrettung.exe
```

## Installer & Updates (Squirrel – Template)
```powershell
# Voraussetzung: Squirrel.Windows im PATH
powershell -ExecutionPolicy Bypass -File .\scripts\squirrel_releasify.ps1
# Ergebnis: .\Releases\Setup.exe, RELEASES, Delta-Pakete
```

## CLI (optional)
```powershell
python .\src\main.py --help
kmz2dji convert C:\pfad\export.kmz --out out --name feld
```
