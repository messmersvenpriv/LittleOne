# LittleOne Release-Anleitung

Diese Anleitung beschreibt:
- was du **einmalig installieren** musst
- was du **bei jedem Release** ausführen musst

---

## 1) Einmalige Einrichtung (nur beim ersten Mal)

### 1.1 Voraussetzungen installieren

1. **Python 3.10+** installieren
2. **Git** installieren
3. **GitHub CLI (`gh`)** installieren

Prüfen im Terminal:

```powershell
python --version
git --version
gh --version
```

### 1.2 GitHub CLI anmelden

```powershell
gh auth login
```

Danach ist das automatische GitHub-Release möglich.

### 1.3 Python-Abhängigkeiten im Projekt installieren

Im Projektordner `C:\LittleOne`:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
pip install pyinstaller
```

Hinweis: `nuget.exe` und `Squirrel.exe` werden vom Skript bei Bedarf automatisch geladen.

---

## 2) Standard-Release (ein Klick)

### 2.1 Version ändern

In `src/LittleOne/__init__.py` den Wert von `__version__` erhöhen, z. B.:

```python
__version__ = "1.2.3"
```

### 2.2 Release starten

Einfach **Doppelklick** auf:

`START_RELEASE.cmd`

Alternativ im Terminal:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\release_silent.ps1
```

### 2.3 Was automatisch passiert

Das Skript erledigt ohne Rückfragen:

1. synchronisiert `pyproject.toml` auf die Version aus `__init__.py`
2. baut `dist\LittleOne.exe`
3. erstellt Installer + Update-Dateien (Squirrel)
4. erstellt Versanddatei `Releases\mail\LittleOne-Setup.exe`
5. macht Git: `add`, `commit`, `tag`, `push`
6. erstellt/aktualisiert GitHub-Release mit Assets
7. erzeugt Anleitungen in `Releases\`

---

## 3) Ergebnis prüfen

Nach erfolgreichem Lauf prüfen:

- `Releases\mail\LittleOne-Setup.exe` (an Anwender verschicken)
- `Releases\squirrel\RELEASES`
- `Releases\squirrel\*.nupkg`
- `Releases\release_instructions.md`

---

## 4) Was der Anwender machen muss

1. `LittleOne-Setup.exe` herunterladen
2. Doppelklick auf den Installer
3. ggf. Windows-Sicherheitsdialog bestätigen
4. LittleOne über Startmenü starten
5. Für Updates später in der App: **Einstellungen → Nach Updates suchen**

---

## 5) Fehlerbehebung (kurz)

- **`gh` fehlt / nicht eingeloggt**
  - installieren: GitHub CLI
  - anmelden: `gh auth login`
- **Git Push schlägt fehl**
  - Remote/Rechte prüfen: `git remote -v`
- **Build schlägt fehl**
  - venv aktivieren und Pakete neu installieren
  - prüfen: `pip install -r requirements.txt pyinstaller`
