# LittleOne – KMZ/KML Konverter (Desktop‑App)

**LittleOne** ist eine Windows‑Desktop-Anwendung zum einfachen Umwandeln von  
**ArcGIS‑KMZ** oder **KML‑Flächen** in **DJI‑kompatible KML‑Dateien**, die direkt in  
**DJI Pilot 2** importiert werden können.

DJI Pilot 2 akzeptiert nur bestimmte KML‑Formate.  
LittleOne sorgt dafür, dass deine Flächen **sauber, geschlossen und DJI‑konform** sind.

---

# Funktionen (für Anwender)

- Öffnen von **KMZ** und **KML** Dateien  
- Automatisches Extrahieren von Polygonen  
- Korrektur & Normalisierung:
  - geschlossene äußere Kanten (Ringe)
  - Höhenwert Z=0 ergänzen
  - OGC‑/DJI‑kompatible Polygonorientierung
- Export von DJI‑tauglichen **KML‑Einzelflächen**  
- Einfache, übersichtliche **grafische Benutzeroberfläche (GUI)**  
- Keine Installation nötig (portable EXE)

**Kein Python erforderlich**  
**Kein Setup nötig**, wenn die portable Version benutzt wird

---

# Bedienung (für Nutzer)

1. **LittleOne.exe** starten  
2. Eine **KMZ** oder **KML**‑Datei auswählen  
3. Ausgabeordner wählen  
4. Basisname (z. B. „Feld01“) eingeben  
5. **Konvertieren** drücken  

Die erzeugten DJI‑KML‑Dateien findest du im gewählten Ausgabeverzeichnis.

---

# Entwickler‑Abschnitt  
*(Dieser Teil ist für dich, nicht für normale Nutzer.)*

Dieser Abschnitt erklärt:

- wie du LittleOne entwickelst  
- wie du aus dem Code eine **EXE** erzeugst  
- wie du einen **Installer** mit **Squirrel.Windows** baust  
- wie Updates funktionieren  
- was Nutzer bei Updates tun müssen  

---

# 🛠️ 1. Entwicklungsumgebung

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1

python -m pip install -r requirements.txt