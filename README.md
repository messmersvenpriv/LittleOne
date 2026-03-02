# LittleOne – KMZ/KML zu DJI Mission Converter

**LittleOne** ist ein Windows-Desktop-Tool für Drohnenpiloten und Surveyor, die **Missionsflächen aus GIS-Tools** (wie ArcGIS, QGIS, Survey123, Google Earth) direkt in **DJI Pilot 2** oder andere Drohnen-Apps importieren möchten.

Das Programm konvertiert **KMZ/KML-Dateien** in **DJI-kompatible Formate** (KML & WPMZ) und normalisiert die Geometrie automatisch – keine komplizierte manuelle Bearbeitung nötig.

**Kurzfassung:**  
Polygone rein → Geometrie normalisiert und DJI-ready raus

---

## Schnelleinstieg (2 Minuten)

1. **LittleOne.exe** herunterladen & starten (keine Installation!)
2. KMZ/KML-Datei auswählen
3. Ausgabeordner festlegen
4. Optional: **Karte aktualisieren** und Flächen prüfen
5. Optional: **Tagesplan** drücken (optimierte Fahrreihenfolge + Routenanzeige)
6. Drohnenmodell, Flughöhe & weitere Parameter setzen
7. **Konvertieren** → Fertig!

Die Dateien sind sofort in **DJI Pilot 2** importierbar.

---

## Neue Funktionen (Stand aktuell)

- **Integrierte Satellitenkarte** direkt in der App
- **Neuer Button: Konvertieren & Hochladen**
  - zeigt beim Klick ein Dropdown mit verfügbaren Zielgeräten
  - filtert nach gewähltem Drohnentyp (M4T/M3T/M2EA)
  - konvertiert und lädt die erzeugten KMZ-Dateien direkt hoch
- **Flächen im Popup ausschließen/wieder aufnehmen**
  - ausgeschlossene Flächen werden grau dargestellt
  - ausgeschlossene Flächen werden nicht konvertiert
- **Neuer Button: Tagesplan**
  - berechnet **Autofahrtrouten zwischen Flächen**
  - optimiert die **Anfahr-Reihenfolge** auf geringe Gesamtstrecke
  - nummeriert die Flächen in Besuchsreihenfolge auf der Karte
  - zeigt Fahrzeiten direkt auf den Routenlinien
  - öffnet ein extra Fenster mit dem detaillierten Tagesplan
- **Update-Prüfung im Menü**: `Einstellungen → Nach Updates suchen`
- **Windows-Icon integriert** (Titelleiste + EXE)

---

## Was LittleOne macht

### Input (Eingang)
- **ArcGIS-KMZ** (z.B. aus Feldskizzen, Feature Services)
- **Google My Maps KML/KMZ**
- **Survey123 KMZ** (Esri Mobile App)
- **QGIS KML/KMZ**
- Beliebige KML/KMZ mit Polygonen

### Automatische Verarbeitung
1. **Geometrie-Validierung**
   - Schließt offene/defekte Ringe
   - Entfernt Selbstüberschneidungen
   - Konvertiert zu OGC-Standard (z.B. Counter-Clockwise Orientierung)

2. **Höhendaten (3D)**
   - Liest vorhandene Z-Werte aus Input
   - Falls nicht vorhanden: Z=0 (auf Meereshöhe)
   - Berechnet sichere Einsatzentfernung basierend auf Flughöhe

3. **Drohnen-Optimierung**
   - DJI-taugliches KML-Format
   - Optional: WPMZ-Format (für Wayline-Missionen)
   - Automatische Fluglinien-Berechnung möglich

### Output (Ausgang)
**Für jedes Polygon wird eine separate Datei erstellt:**
- `Gebiet_001.kml` → Import in DJI Pilot 2
- `Gebiet_001_mission.wpmz` → DJI Standard Mission Format (optional)

Die KML-Dateien können direkt in DJI Pilot 2 als **Missionsfläche** importiert werden.

---

## Ausführliche Bedienung

### Parameter erklären

| Parameter | Bedeutung | Beispiel |
|-----------|-----------|---------|
| **KMZ/KML-Datei** | Input-Datei mit Polygonen | `feld_2026.kmz` |
| **Ausgabeverzeichnis** | Zielordner für konvertierte Dateien | `C:\Missionen\2026` |
| **Polygon-Basisname** | Präfix für Ausgabedateien | `Feld01` → `Feld01_001.kml` |
| **Drohnenmodell** | Für Optimierung & Validierung | M3T, M4T, M300 RTK, ... |
| **Flughöhe (Altitude)** | Geplante Einsatzhöhe über Grund | 50 m, 120 m, 200 m |
| **Sichere Einsatzentfernung** | Mindestabstand zu Hindernissen | = Flughöhe oder höher |
| **Fluggeschwindigkeit** | Für Zeitmessungen | 10–15 m/s empfohlen |
| **Sicherheitsmarge** | Puffer um Polygonkanten | 5–10 m typisch |
| **Angle Optimization** | Orientierung optimieren (falls berechnbar) | Nicht bei allen Gebieten möglich |
| **Elevation Optimization** | Höhenoptimierung (optional) | Standard: aus |

**Standard-Optimierungen:**
- Winkeloptimierung: **an**
- Elevation-Optimierung: **aus**

### Schritt-für-Schritt

```
1. KMZ-Datei öffnen
   ├─ Klick auf "Datei auswählen"
   └─ z.B. "Kartenskizze_Survey123.kmz" wählen

2. Parameter setzen
   ├─ Drohnenmodell: "M4T" oder "M3T"
   ├─ Flughöhe: z.B. "100 m"
   ├─ Ausgabeverzeichnis: z.B. "C:\Missionen"
   └─ Polygon-Name: z.B. "Weide2026"

3. Conversion starten
   ├─ "Konvertieren" drücken
   ├─ Fortschrittsbalken zeigt Verarbeitung
   └─ Nach ca. 1–3 Sekunden: Fertig!

4. Output checken
   ├─ Ordner öffnen: C:\Missionen
   ├─ Dateien: Weide2026_001.kml, Weide2026_002.kml, ...
   └─ In DJI Pilot 2 importieren
```

### Tagesplan-Funktion (neu)

Wenn eine KMZ/KML geladen ist, kannst du über **Tagesplan** vor der Konvertierung die Reihenfolge der Flächen planen:

1. **Tagesplan** klicken
2. LittleOne berechnet die Fahrmatrix zwischen Flächenzentren
3. Reihenfolge wird auf minimale Fahrtzeit/-strecke optimiert
4. Karte zeigt:
  - nummerierte Flächen (1, 2, 3, ...)
  - Fahrtrouten zwischen den Flächen
  - Fahrzeitlabel direkt auf der Route
5. Zusätzlich öffnet sich ein eigenes Fenster mit:
  - genauer Reihenfolge aller Flächen
  - Segmentliste mit Strecke und Fahrzeit pro Abschnitt

Hinweis: Für echte Straßenrouten nutzt LittleOne OSRM (Online). Wenn kein Routing-Dienst erreichbar ist, wird automatisch ein Luftlinien-Fallback mit Durchschnittsgeschwindigkeit verwendet.

### Konvertieren und Hochladen (FlightHub-Workflow)

- **Konvertieren**: erzeugt nur lokale KMZ-Dateien
- **Konvertieren und Hochladen**:
  1. Dropdown für Zielgerät (passend zum ausgewählten Drohnentyp)
  2. Konvertierung
  3. Upload der erzeugten KMZ-Dateien
  4. Optionales Mission-Assignment (wenn Endpoint konfiguriert)

Benötigte Datei: `config/flighthub2.json`  
Vorlage: `config/flighthub2.json.example`

Pflichtfelder in der Config:

- `base_url`
- `endpoints.upload`
- `devices[]` mit `id`, `name`, `model`, optional `workspace_id`, `enabled`

Optional (empfohlen):

- `endpoints.devices` für Live-Geräteliste aus API
- `endpoints.assign` für Mission-Zuweisung nach Upload

Credentials (eine Variante):

- `auth.access_token` **oder**
- `auth.token_url` + `auth.client_id` + `auth.client_secret`

Welche Werte du konkret eintragen musst:

- `auth.access_token`: Bearer Token eures FlightHub-Backends (falls statischer Token)
- `auth.token_url`: OAuth-Token-Endpoint (falls Client-Credentials genutzt werden)
- `auth.client_id` / `auth.client_secret`: OAuth Client-Credentials
- `devices[].id`: eindeutige Geräte-ID aus eurem System
- `devices[].model`: exakt `M4T`, `M3T` oder `M2EA` (für den Typfilter im Dropdown)

---

## Einstellungen (Menü → Design/Sprache/Einheiten)

### Design (Theme)
- **Light Mode**: Helles Design für tagsüber
- **Dark Mode**: Dunkles Design für Nacht/Outdoor

### Sprache
- **Deutsch** (Standard)
- **English**
- **Français**
- **Suomi**

Alle Menüs, Felder & Meldungen passen sich automatisch an.

### Einheiten
- **Metric** (m, m/s) – Standard weltweit
- **Imperial** (ft, ft/s) – USA
- **Metric + kmh** (m, km/h) – Deutschland, Österreich
- **Nautical** (m, kts) – Maritim/Luftfahrt

### Updates
- Menüpunkt: **Einstellungen → Nach Updates suchen**
- Die App-Version kommt aus `src/LittleOne/__init__.py` (`__version__`)
- Empfohlener Ablauf vor Release:
  1. Version in `src/LittleOne/__init__.py` erhöhen
  2. Vollautomatisch per 1-Klick starten (Doppelklick):
    - `START_RELEASE.cmd`
    - (alternativ im Terminal) `powershell -ExecutionPolicy Bypass -File .\scripts\release_silent.ps1`
  3. Das Silent-Skript synchronisiert automatisch `pyproject.toml` auf die Version aus `__init__.py` und startet danach den Release-Flow ohne Rückfragen.
  4. Optional manuell mit Assistent starten:
    - `powershell -ExecutionPolicy Bypass -File .\scripts\release_assistent.ps1`
  5. Der automatische Flow erledigt:
    - EXE-Build + Squirrel-Artefakte
    - Git (`add`, `commit`, `tag`, `push`)
    - GitHub-Release (wenn `gh` installiert und eingeloggt)
    - Anleitung für Entwickler + Anwender
  6. Ergebnis prüfen in `Releases/`:
    - `mail/LittleOne-Setup.exe`
    - `squirrel/RELEASES`
    - `squirrel/*.nupkg`
    - `release_instructions.md`
  7. Detaillierte Setup- und Release-Anleitung: `RELEASE_ANLEITUNG.md`

Hinweis: Der Update-Button bevorzugt automatisch den Installer (`Setup*.exe`) aus dem neuesten Release.

---

## Häufige Fehler & Lösungen

### „Keine Polygone gefunden"
**Ursache:** Datei enthält nur Punkte oder Linien, keine Flächen.

**Lösung:**
1. KMZ in Google Earth öffnen → Geometrie prüfen
2. In QGIS öffnen: `Layer → Properties → Geometry Type` prüfen
3. Ggf. in Survey123 oder ArcGIS als Polygon zeichnen

### „Encoding-Fehler" / „Ungültiges KML"
**Ursache:** KML-Datei ist beschädigt oder mit falschem Encoding gespeichert.

**Lösung:**
1. KMZ entpacken (`.zip` umbenennen) → `doc.kml` öffnen
2. In **Notepad++** mit UTF-8 Encoding speichern
3. Erneut in ZIP packen und `.kmz` umbenennen
4. Oder: `Fehler-Log` prüfen (unten im Fenster)

### Polygon sieht in DJI Pilot „schief" aus
**Ursache:** Ursprüngliches Polygon hatte ungültige Geometrie (Selbstüberschneidung, falsche Reihenfolge).

**Lösung:**
LittleOne versucht zu korrigieren, aber bei sehr komplexen Gebieten kann eine manuelle Nachbearbeitung nötig sein:
1. Polygon vor Export vereinfachen (in QGIS: `Vector → Simplify` oder `Buffer(0)`)
2. Neu konvertieren

### Ausgabedatei ist leer
**Ursache:** Ausgabeverzeichnis existiert nicht oder ist schreibgeschützt.

**Lösung:**
1. Verzeichnis manuell erstellen (z.B. `C:\Missionen`)
2. Berechtigungen prüfen (Rechtsklick → Eigenschaften)
3. Admin-Rechte ggf. erforderlich

### „Too many points" Warning
**Ursache:** Polygon hat zu viele Koordinaten (z.B. > 2000 Punkte) – DJI kann das ggf. nicht verarbeiten.

**Lösung:**
1. In QGIS vereinfachen: `Vector → Simplify (Douglas-Peucker, tolerance 0.5–1 m)`
2. Oder: Survey123 mit weniger Detail zeichnen
3. Erneut konvertieren

---

## Installation & Download

### Option A: Installer (Empfohlen für Teams + Updates)
- **Download:** `LittleOne-Setup.exe` (kleine Versanddatei für Mail/Chat)
- **Aktuelle Release-Version:** `v0.2.2` (März 2026)
- **Installation:** Doppelklick, automatische Benutzer-Installation
- **System:** Windows 10/11 64-Bit
- **Admin-Rechte:** Nicht nötig
- **Updatefähig:** Ja, über **Einstellungen → Nach Updates suchen**

### Option B: Portable Exe
- **Download:** `LittleOne.exe`
- **Installation:** Keine – direkt startbar
- **Updatefähig:** Nein (für Updates neue EXE verteilen)

### Option B: Python Source Code
Für Entwickler:

```bash
# 1. Repository klonen
git clone https://github.com/messmersvenpriv/LittleOne.git
cd LittleOne

# 2. Virtual Environment
python -m venv .venv
.venv\Scripts\activate

# 3. Dependencies
pip install -r requirements.txt

# 4. GUI starten
python src/ui_app.py
```

---

## Input-Anforderungen

### Unterstützte Formate
- **KMZ** (Compressed KML)
- **KML** (uncompressed)

### Polygon-Anforderungen
| Kriterium | Anforderung |
|-----------|------------|
| Gaußförmig | Einfache Polygon (keine Donut-Holes erlaubt) |
| Geschlossen | Erste & letzte Koordinate = Punkt |
| Ausrichtung | Beliebig (wird normalisiert) |
| Z-Werte | Optional (werden auf 0m gesetzt, wenn fehlend) |
| Koordinaten-System | WGS84 (EPSG:4326) |

**Beispiel-Input aus Survey123:**
```xml
<Polygon>
  <outerBoundaryIs>
    <LinearRing>
      <coordinates>
        8.1234,48.5678,50 8.1235,48.5678,50 8.1235,48.5679,50 8.1234,48.5679,50 8.1234,48.5678,50
      </coordinates>
    </LinearRing>
  </outerBoundaryIs>
</Polygon>
```

---

## Output-Formate

### Datei: `Gebietname_XXX.kml`
```xml
<?xml version="1.0" encoding="UTF-8"?>
<kml xmlns="http://www.opengis.net/kml/2.2">
  <Document>
    <Folder>
      <name>Gebietname_001</name>
      <Placemark>
        <Polygon>
          <outerBoundaryIs>
            <LinearRing>
              <coordinates>
                8.1234,48.5678,0 8.1235,48.5678,0 ...
              </coordinates>
            </LinearRing>
          </outerBoundaryIs>
        </Polygon>
      </Placemark>
    </Folder>
  </Document>
</kml>
```

→ Diese Datei kann in **DJI Pilot 2 → Mission → Import** geladen werden.

### Optional: WPMZ-Format
DJI Standard Missions Format (für Waylines, Kamerabefehle, etc.):
- `Gebietname_XXX_mission.wpmz`
- Enthält: `doc.kml`, `template.kml`, `waylines.wpml`
- Erweiterte Drohnen-Software erforderlich

---

## Typische Anwendungsfälle

### 1. Feldskizze in DJI Pilot importieren
```
Survey123 (Tablet) → Polygon zeichnen → KMZ exportieren 
→ LittleOne → doc.kml → DJI Pilot 2 importieren 
→ Flugmission erstellen
```

### 2. Verschiedene Flugpläne für unterschiedliche Höhen
```
Selbe Fläche, aber:
- Orthofoto: 50 m Höhe
- Wärmebild: 100 m Höhe
- Struktur-Scan: 80 m Höhe

Jede Höhe einzeln mit LittleOne konvertieren
→ 3 KML-Dateien für 3 Missionen
```

### 3. ArcGIS Server Feature Service exportieren
```
ArcGIS Online → export as KML 
→ LittleOne konvertieren 
→ Team-Drohne importieren
```

---

## Technische Details

### Abhängigkeiten
- **PySide6**: Moderne GUI (Windows, Mac, Linux)
- **Shapely**: Geometrie-Verarbeitung
- **fastkml**: KML-Parsing
- **lxml**: XML-Verarbeitung

### Verarbeitungs-Logik
1. File I/O: `.kmz` → entpacken → `doc.kml` lesen
2. KML-Parsing: fastkml (mit fallback zu XML)
3. Polygon-Normalisierung:
   - Geschlossene Ringe sicherstellen
   - Selbstüberschneidungen korrigieren
   - Z-Werte validieren
   - OGC-konforme Ausrichtung
4. DJI-Formatierung: KML mit DJI-Extensions
5. WPMZ-Paketierung: ZIP mit `doc.kml` + `template.kml` + `waylines.wpml`
6. Output: Separate Dateien für jedes Polygon

### Performance
- **Kleine Gebiete** (< 100 Punkte): < 100 ms
- **Mittlere Gebiete** (100–1000 Punkte): 100–500 ms
- **Komplexe Gebiete** (> 1000 Punkte): Bis 3–5 Sekunden

---

## FAQ

**F: Kann ich mehrere Dateien auf einmal konvertieren?**  
A: Aktuell nicht – bitte einzeln konvertieren. In Zukunft mit Batch-Verarbeitung geplant.

**F: Funktioniert das auch mit Donut-Polygonen (Loch in der Mitte)?**  
A: Nein – LittleOne unterstützt nur einfache Polygone. Löcher müssen manuell entfernt werden.

**F: Kann ich die KML nach der Konvertierung noch weitere Parameter (Waylines, Kameras) hinzufügen?**  
A: Ja – DJI Pilot 2 erlaubt Nachbearbeitung vor der Mission-Erstellung.

**F: Funktioniert das auch auf Mac/Linux?**  
A: Die Python-Version ja. Eine native Mac/Linux GUI ist geplant, aber aktuell Windows-only.

**F: Wie kann ich die Position eines Fehlers debuggen?**  
A: `Fehler-Log` unten im Fenster anschauen oder Datei an Support senden.

**F: Welche Koordinatenformate werden unterstützt?**  
A: Nur **WGS84 (EPSG:4326)** – das ist der Standard für KML/KMZ.

**F: Brauche ich Internet zum Starten?**  
A: Für die reine Konvertierung nein. Für Satellitenkarten-Tiles und den Tagesplan mit realen Straßenrouten ist Internet sinnvoll. Ohne Routing-Dienst nutzt LittleOne automatisch einen Offline-Fallback (Luftlinie).

---

## Fehlerberichte & Support

Bugs oder Feature-Requests?

→ **GitHub Issues:** https://github.com/messmersvenpriv/LittleOne/issues

Bitte mitincludieren:
- **Output-Log** (Copy aus dem Fenster)
- **Beispiel-KMZ-Datei** (bei Parsing-Fehlern)
- **Betriebssystem + Windows-Version**
- **Schritte zum Reproduzieren**

---

## Lizenz

**MIT License** – Kostenlos für private & kommerzielle Nutzung.

---

## Versionshistorie

| Version | Datum | Änderungen |
|---------|-------|-----------|
| 1.4 | März 2026 | Release `v0.2.2`, Korrektur der DJI-Kartierungslinien beim Import, Export vereinfacht (keine Debug-KMLs, keine Sammel-KMZ) |
| 1.3 | Feb 2026 | Tagesplan-Button, Fahrreihenfolge-Optimierung, Fahrtrouten mit Zeitlabels, Tagesplan-Fenster |
| 1.2 | Feb 2026 | Mehrsprachen-GUI, WPMZ-Support, Units-System |
| 1.1 | Jan 2026 | Dark Mode, Fehler-Handling verbessert |
| 1.0 | Dez 2025 | Initial Release |

---

**Letzte Aktualisierung:** März 2026  
**Entwicklung:** GitHub  
**Support:** Issues & Discussions
