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
4. Drohnenmodell, Flughöhe & weitere Parameter setzen
5. **Konvertieren** → Fertig!

Die Dateien sind sofort in **DJI Pilot 2** importierbar.

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

### Option A: Portable Exe (Empfohlen)
- **Download:** `LittleOne.exe` (ca. 150 MB)
- **Installation:** Keine – einfach starten
- **System:** Windows 10/11 64-Bit
- **Admin-Rechte:** Nicht nötig (außer für schreibgeschützte Ordner)

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
A: Nein – alles läuft lokal. GitHub-Links im Help-Menü brauchen Internet.

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
| 1.2 | Feb 2026 | Mehrsprachen-GUI, WPMZ-Support, Units-System |
| 1.1 | Jan 2026 | Dark Mode, Fehler-Handling verbessert |
| 1.0 | Dez 2025 | Initial Release |

---

**Letzte Aktualisierung:** Feb 2026  
**Entwicklung:** GitHub  
**Support:** Issues & Discussions
