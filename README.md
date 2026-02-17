# Kitzrettung KML/ KMZ Tool (Grundgerüst)

Dieses Projekt konvertiert **ArcGIS‑KMZ** in **DJI‑kompatible KML‑Grenzen** (Boundary), optional mit **Winkel‑Optimierung** (Minimum Rotated Rectangle) für effiziente Mapping‑Routen in **DJI Pilot 2**. Anschließend kann Pilot 2 die Grid‑Mission automatisch aus dem KML‑Polygon erzeugen.

## Features (aktuell)
- **KMZ → KML**: Extrahiert KML aus KMZ und speichert je Polygon eine KML‑Datei
- **DJI‑Normalisierung**: schließt Ringe, erzwingt `lon,lat,alt` (Z=0), sauberes `Polygon`
- **Winkel‑Optimierung**: ermittelt den **MRR‑Azimut** als Startwinkel für die Grid‑Orientierung
- **CLI**: `kmz2dji convert` & `kmz2dji optimize`
- **.exe‑Build** via PyInstaller (Windows)

> **Hinweise aus Quellen**:
> - **Pilot 2** importiert **KML/KMZ** als Missionsgrenze; Route wird im Controller generiert. (Propeller Aero: *Importing and Exporting Missions with DJI Pilot 2*) citeturn1search51
> - **KML‑Spezifikation** verlangt Koordinaten als **`longitude,latitude,altitude`** (Z optional, in der Praxis oft nötig). (OGC KML 2.3 / GIS SE) citeturn1search22turn1search26
> - **ArcGIS Layer to KML** exportiert in **WGS84**, passend für KML/Pilot. (ArcGIS Pro Docs) citeturn1search44
> - Community‑Berichte: Direkt aus ArcGIS/QGIS exportierte KML funktionieren teils nicht in Pilot 2; Neuformatierung (Z=0, Polygon) hilft. (Farmwissen & Reddit‑Thread) citeturn1search54turn1search52
> - **Winkel‑Heuristik**: Shapely `minimum_rotated_rectangle` / Azimut des längeren Kantenpaares. (Shapely Docs / StackOverflow) citeturn1search92turn1search91

## Installation (Entwicklung)
```bash
python -m venv .venv
# Windows
.venv\Scriptsctivate
# macOS/Linux
# source .venv/bin/activate

pip install -e .
# oder
pip install -r requirements.txt
```

## CLI
```bash
kmz2dji --help
kmz2dji convert path	o\export.kmz --out out --name feld
kmz2dji optimize out/feld_001.kml --out out --mode mrr
```

## Struktur
```
kitzrettung-kml/
├─ .vscode/
├─ config/
├─ scripts/
├─ src/
│  ├─ kitzkmz/
│  └─ main.py
├─ tests/
├─ pyproject.toml
├─ requirements.txt
└─ README.md
```

## Build (Windows .exe)
```powershell
powershell -ExecutionPolicy Bypass -File scriptsuild_win_exe.ps1
# Ergebnis: dist\kmz2dji.exe
```

## Nutzung in DJI Pilot 2
1. **KML** aus `out/` auf den Controller kopieren (SD‑Karte oder MTP).
2. **Pilot 2 → Flight Route → Import Route (KMZ/KML)** und KML wählen. (Details siehe Propeller Aero‑Anleitung) citeturn1search51
3. Pilot 2 erzeugt die **Mapping‑Route**; Missionseinstellungen (Überlappung, Höhe etc.) im Controller konfigurieren (siehe Pilot 2 Tutorials). citeturn1search10

## Bekannte Stolpersteine
- **Invalid format / Task type error**: KML ohne Z‑Werte oder als geschlossene **Polyline** statt `Polygon`. Workaround: Z hinzufügen, Polygon sicherstellen, ggf. via Google Earth neu speichern. (Community‑Threads) citeturn1search52
- **CRS**: KML erwartet **WGS84**; ArcGIS exportiert das automatisch in `Layer To KML`. (ArcGIS Docs) citeturn1search44

## Roadmap
- Tiling großer Polygone (z. B. Streifenlängenbegrenzung)
- GUI‑Frontend
- Optionaler .NET‑Wrapper (Squirrel.Windows) für Installation & Auto‑Update (GitHub Releases) citeturn1search58

## Lizenz
MIT (für dieses Grundgerüst)
