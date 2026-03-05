# LittleOne

LittleOne ist ein Windows-Desktop-Tool zur Aufbereitung von KML/KMZ-Flächen für DJI-Missionen.
Der Schwerpunkt liegt auf einem schnellen Workflow für Kitzrettung und ähnliche Flächenbefliegungen:
Datei laden, Parameter setzen, missionstaugliche Dateien exportieren.

## Was LittleOne kann

- KMZ/KML einlesen und Polygonflächen extrahieren
- Geometrien für den Export normalisieren (Ringe schließen, Z-Werte ergänzen)
- DJI-kompatible Missions-KMZ erzeugen (inkl. `doc.kml`, `wpmz/template.kml`, `wpmz/waylines.wpml`)
- Flächen auf der Karte prüfen, temporär ausschließen und Startfläche festlegen
- Tagesplan mit Besuchsreihenfolge, Fahrstrecken und Zeitschätzung berechnen
- Optional: erzeugte Missionen direkt zu FlightHub hochladen

## Voraussetzungen

- Windows 10/11 (64 Bit)
- Für Entwicklung: Python 3.10+

## Schnellstart (Anwender)

1. `LittleOne-Setup.exe` aus einem Release starten
2. App öffnen
3. KMZ/KML-Datei auswählen
4. Ausgabeordner festlegen
5. Drohne, Flughöhe und weitere Parameter setzen
6. `Konvertieren und Exportieren` ausführen

Die erzeugten KMZ-Dateien liegen anschließend im gewählten Ausgabeordner.

## Entwicklung einrichten

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python -m pip install -e .
```

## Anwendung starten

GUI:

```powershell
.\scripts\run_ui.ps1
```

Alternativ direkt:

```powershell
python .\src\ui_app.py
```

CLI (Typer):

```powershell
kmz2dji convert .\data\start\beispiel.kmz --out .\out --name gebiet
kmz2dji angle .\out\gebiet-001.kml --out .\out
```

## Eingabe und Ausgabe

### Eingabe

- `.kmz` und `.kml`
- erwartet werden Polygon-Geometrien

### Ausgabe (GUI)

- pro Fläche eine `.kmz`-Datei
- Dateiname wird bereinigt und aus Flächeninformationen abgeleitet

In jeder erzeugten KMZ liegen u. a.:

- `doc.kml`
- `wpmz/template.kml`
- `wpmz/waylines.wpml`

### Ausgabe (CLI)

- pro Fläche eine `.kml`-Datei

## FlightHub-Upload konfigurieren

Für `Konvertieren und Hochladen` wird eine FlightHub-Konfiguration benötigt.

1. Vorlage kopieren:

```powershell
Copy-Item .\config\flighthub2.json.example .\config\flighthub2.json
```

2. In `config/flighthub2.json` mindestens folgende Bereiche befüllen:
   - `base_url`
   - `auth` (Token oder OAuth-Daten)
   - `endpoints.upload`
   - `devices` mit `id`, `name`, `model`

Wichtig:

- `model` muss zu einem unterstützten Typ passen (`M4T`, `M3T`, `M2EA`)
- Zugangsdaten nicht in öffentliche Repositories committen

## Karte und Tagesplan

- Kartenansicht nutzt Leaflet
- Routing nutzt bevorzugt OSRM
- Bei fehlender Online-Verbindung arbeitet LittleOne mit Fallbacks (Luftlinie + Durchschnittsgeschwindigkeit)

Für die erweiterte Tageszeitschätzung werden Kitzdaten aus
`data/Locations/Rehkitz_Fundort.csv` einbezogen (falls vorhanden).

## Build

Portable EXE erstellen:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\build_gui_exe.ps1
```

Ergebnis: `dist/LittleOne.exe`

## Release

Ein-Klick (Windows):

```powershell
.\START_RELEASE.cmd
```

Der Silent-Release-Flow erledigt unter anderem:

- Versionsabgleich zwischen `src/LittleOne/__init__.py` und `pyproject.toml`
- Build der EXE
- Squirrel-Artefakte für Updates
- optionale Git/GitHub-Release-Schritte

Ausgabe liegt in `Releases/`.

## Nützliche Dateien

- `src/ui_app.py` – GUI
- `src/LittleOne/cli.py` – CLI-Befehle
- `src/LittleOne/kmz_reader.py` – Import/Parsing
- `src/LittleOne/kml_writer.py` – Export nach KML/KMZ/WPML
- `config/default.yaml` – Standardparameter
- `RELEASE_ANLEITUNG.md` – detaillierte Release-Doku

## Troubleshooting (kurz)

- **Keine Polygone gefunden**: Datei enthält evtl. nur Punkte/Linien statt Flächen
- **Karte lädt nicht**: Online-Verbindung prüfen; Konvertierung funktioniert trotzdem
- **Upload schlägt fehl**: `config/flighthub2.json` auf Pflichtfelder und gültige Credentials prüfen

## Lizenz

MIT
