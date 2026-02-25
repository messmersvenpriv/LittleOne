from PySide6 import QtWidgets, QtGui, QtCore, QtWebChannel

try:
    from PySide6 import QtWebEngineWidgets
    from PySide6 import QtWebEngineCore

    WEBENGINE_AVAILABLE = True
except Exception:
    QtWebEngineWidgets = None
    QtWebEngineCore = None
    WEBENGINE_AVAILABLE = False

from pathlib import Path
import sys, traceback
import re
import types
import json
import hashlib
import math
import subprocess
import webbrowser
import urllib.request
import urllib.error
import urllib.parse
import tempfile

ENGINE_IMPORT_ERROR = None
optimize_angle_mod = None
APP_VERSION = "0.0.0"
GITHUB_REPO = "messmersvenpriv/LittleOne"

try:
    from LittleOne import __version__ as PACKAGE_VERSION

    APP_VERSION = str(PACKAGE_VERSION)
except Exception:
    pass

try:
    from LittleOne import kmz_reader, kml_writer, dji_rules, optimize_angle

    optimize_angle_mod = optimize_angle
except Exception as ex:
    ENGINE_IMPORT_ERROR = ex
    kmz_reader = kml_writer = dji_rules = optimize_angle_mod = None

# Theme-Konstanten
THEMES = {
    "Light": {
        "bg": "#FFFFFF",
        "fg": "#333333",
        "accent": "#0078D4",
        "button_bg": "#F3F3F3",
        "border": "#CCCCCC",
        "hover_bg": "#E5E5E5",
    },
    "Dark": {
        "bg": "#1E1E1E",
        "fg": "#FFFFFF",
        "accent": "#3CA0E0",
        "button_bg": "#2D2D2D",
        "border": "#404040",
        "hover_bg": "#3D3D3D",
    },
}

LANGUAGES = {
    "Deutsch": {
        "title": "LittleOne - Datenkonvertierungssoftware der Kitzrettung Rastatt Baden-Baden (warum liest du das bis hier?)",
        "file": "Datei",
        "settings": "Einstellungen",
        "help": "Hilfe",
        "about": "Über",
        "documentation": "Dokumentation",
        "exit": "Beenden",
        "kmz_file": "KMZ/KML-Datei",
        "output_dir": "Ausgabeordner",
        "altitude": "Flughöhe",
        "altitude_unit": "m",
        "overlap": "Seitlicher Überlapp",
        "overlap_unit": "%",
        "safe_height": "Sichere Starthöhe",
        "safe_height_unit": "m",
        "drone": "Drohne",
        "action": "Aktion beenden",
        "speed": "Geschwindigkeit",
        "speed_unit": "m/s",
        "margin": "Rand",
        "optimize_group": "Optimierungen",
        "optimize_dir": "Winkeloptimierung aktiv",
        "optimize_elev": "Elevation-Optimierung aktiv",
        "convert": "Konvertieren",
        "day_plan": "Tagesplan",
        "reset": "Zurücksetzen",
        "output": "Ausgabe",
        "ready": "Bereit.",
        "converting": "Konvertiere …",
        "done": "Fertig.",
        "select_kmz": "Bitte KMZ oder KML auswählen.",
        "select_kmz_empty": "Bitte wählen Sie zuerst eine KMZ/KML-Datei aus.",
        "file_not_found": "Die angegebene Datei existiert nicht:",
        "import_error": "Engine-Importfehler",
        "success": "Erfolgreich",
        "error": "Fehler",
        "found_features": "Features geladen",
        "found_polygons": "Polygone extrahiert",
        "parsing_kmz": "Parsing KMZ...",
        "normalizing": "Normalisiere Geometrien...",
        "normalized": "Geometrien normalisiert",
        "writing_kmz": "Schreibe KMZ-Dateien...",
        "no_polygons": "Keine Polygone gefunden.",
        "kmz_generated": "KMZ-Dateien generiert",
        "output_folder": "Ausgabeordner",
        "debug_kmls": "Debug-KMLs",
        "show_map": "Satellitenkarte",
        "map_refresh": "Karte aktualisieren",
        "map_title": "Satellitenkarte",
        "map_loading": "Lade Flächen für Kartenansicht...",
        "map_opened": "Satellitenkarte geöffnet",
        "map_no_polygons": "Keine Polygone für Kartenansicht gefunden.",
        "map_saved": "Karte gespeichert",
        "map_panel_fallback": "Kartenpanel benötigt QtWebEngine. Browser-Fallback ist aktiv.",
        "map_remove_area": "Fläche entfernen",
        "map_readd_area": "Fläche wieder aufnehmen",
        "map_controls_title": "Kartierungslinien",
        "map_controls_toggle": "Linien anzeigen",
        "map_opt_disabled": "Winkeloptimierung ist deaktiviert.",
        "map_stats_active_areas": "Flächen aktiv",
        "map_stats_distance": "Geschätzte Strecke",
        "map_stats_time": "Geschätzte Flugzeit",
        "map_stats_lines": "Linien",
        "map_stats_drone": "Drohne",
        "map_stats_altitude": "Höhe",
        "map_stats_overlap": "Überlapp",
        "map_stats_speed": "Speed",
        "map_leaflet_error": "Leaflet konnte nicht geladen werden (Offline/Netzwerk).",
        "link_survey_tip": "Survey123 öffnen",
        "link_arcgis_tip": "ArcGIS Map öffnen",
        "link_home_tip": "Homepage öffnen",
        "toilet_tip": "Klopapierrolle",
        "toilet_title": "🧻",
        "toilet_message": "Was hast du denn jetzt erwartet, dass passiert?\nWeiter machen!",
        "settings_title": "Einstellungen",
        "theme": "Design",
        "language": "Sprache",
        "units": "Einheiten",
        "ok": "OK",
        "cancel": "Abbrechen",
    },
    "English": {
        "title": "LittleOne - Datenkonvertierungssoftware der Kitzrettung Rastatt Baden-Baden (warum liest du das bis hier?)",
        "file": "File",
        "settings": "Settings",
        "help": "Help",
        "about": "About",
        "documentation": "Documentation",
        "exit": "Exit",
        "kmz_file": "KMZ/KML File",
        "output_dir": "Output Folder",
        "altitude": "Altitude",
        "altitude_unit": "m",
        "overlap": "Side Overlap",
        "overlap_unit": "%",
        "safe_height": "Safe Start Height",
        "safe_height_unit": "m",
        "drone": "Drone",
        "action": "End Action",
        "speed": "Speed",
        "speed_unit": "m/s",
        "margin": "Margin",
        "optimize_group": "Optimizations",
        "optimize_dir": "Angle Optimization",
        "optimize_elev": "Elevation Optimization",
        "convert": "Convert",
        "day_plan": "Day Plan",
        "reset": "Reset",
        "output": "Output",
        "ready": "Ready.",
        "converting": "Converting …",
        "done": "Done.",
        "select_kmz": "Please select KMZ or KML.",
        "select_kmz_empty": "Please select a KMZ/KML file first.",
        "file_not_found": "The specified file does not exist:",
        "import_error": "Import Error",
        "success": "Success",
        "error": "Error",
        "found_features": "Features loaded",
        "found_polygons": "Polygons extracted",
        "parsing_kmz": "Parsing KMZ...",
        "normalizing": "Normalizing geometries...",
        "normalized": "Geometries normalized",
        "writing_kmz": "Writing KMZ files...",
        "no_polygons": "No polygons found.",
        "kmz_generated": "KMZ files generated",
        "output_folder": "Output folder",
        "debug_kmls": "Debug KMLs",
        "show_map": "Satellite Map",
        "map_refresh": "Refresh Map",
        "map_title": "Satellite map",
        "map_loading": "Loading areas for map preview...",
        "map_opened": "Satellite map opened",
        "map_no_polygons": "No polygons found for map preview.",
        "map_saved": "Map saved",
        "map_panel_fallback": "Map panel needs QtWebEngine. Browser fallback is active.",
        "map_remove_area": "Remove area",
        "map_readd_area": "Include area again",
        "map_controls_title": "Mapping lines",
        "map_controls_toggle": "Show lines",
        "map_opt_disabled": "Angle optimization is disabled.",
        "map_stats_active_areas": "Active areas",
        "map_stats_distance": "Estimated distance",
        "map_stats_time": "Estimated flight time",
        "map_stats_lines": "Lines",
        "map_stats_drone": "Drone",
        "map_stats_altitude": "Altitude",
        "map_stats_overlap": "Overlap",
        "map_stats_speed": "Speed",
        "map_leaflet_error": "Leaflet could not be loaded (offline/network).",
        "link_survey_tip": "Open Survey123",
        "link_arcgis_tip": "Open ArcGIS Map",
        "link_home_tip": "Open Homepage",
        "toilet_tip": "Toilet roll",
        "toilet_title": "🧻",
        "toilet_message": "What did you expect to happen now?\nKeep going!",
        "settings_title": "Settings",
        "theme": "Theme",
        "language": "Language",
        "units": "Units",
        "ok": "OK",
        "cancel": "Cancel",
    },
    "Français": {
        "title": "LittleOne - Datenkonvertierungssoftware der Kitzrettung Rastatt Baden-Baden (warum liest du das bis hier?)",
        "file": "Fichier",
        "settings": "Paramètres",
        "help": "Aide",
        "about": "À propos",
        "documentation": "Documentation",
        "exit": "Quitter",
        "kmz_file": "Fichier KMZ/KML",
        "output_dir": "Dossier de sortie",
        "altitude": "Altitude",
        "altitude_unit": "m",
        "overlap": "Chevauchement latéral",
        "overlap_unit": "%",
        "safe_height": "Hauteur de démarrage sûre",
        "safe_height_unit": "m",
        "drone": "Drone",
        "action": "Action de fin",
        "speed": "Vitesse",
        "speed_unit": "m/s",
        "margin": "Marge",
        "optimize_group": "Optimisations",
        "optimize_dir": "Optimisation d'angle",
        "optimize_elev": "Optimisation d'élévation",
        "convert": "Convertir",
        "day_plan": "Plan du jour",
        "reset": "Réinitialiser",
        "output": "Sortie",
        "ready": "Prêt.",
        "converting": "Conversion …",
        "done": "Terminé.",
        "select_kmz": "Veuillez sélectionner un KMZ ou KML.",
        "select_kmz_empty": "Veuillez d'abord sélectionner un fichier KMZ/KML.",
        "file_not_found": "Le fichier spécifié n'existe pas:",
        "import_error": "Erreur d'importation",
        "success": "Succès",
        "error": "Erreur",
        "found_features": "Éléments chargés",
        "found_polygons": "Polygones extraits",
        "parsing_kmz": "Analyse du KMZ...",
        "normalizing": "Normalisation des géométries...",
        "normalized": "Géométries normalisées",
        "writing_kmz": "Écriture des fichiers KMZ...",
        "no_polygons": "Aucun polygone trouvé.",
        "kmz_generated": "Fichiers KMZ générés",
        "output_folder": "Dossier de sortie",
        "debug_kmls": "KMLs de débogage",
        "show_map": "Carte satellite",
        "map_refresh": "Actualiser la carte",
        "map_title": "Carte satellite",
        "map_loading": "Chargement des zones pour la carte...",
        "map_opened": "Carte satellite ouverte",
        "map_no_polygons": "Aucun polygone trouvé pour la carte.",
        "map_saved": "Carte enregistrée",
        "map_panel_fallback": "Le panneau carte nécessite QtWebEngine. Repli navigateur actif.",
        "map_remove_area": "Retirer la zone",
        "map_readd_area": "Réintégrer la zone",
        "map_controls_title": "Lignes de cartographie",
        "map_controls_toggle": "Afficher les lignes",
        "map_opt_disabled": "L'optimisation d'angle est désactivée.",
        "map_stats_active_areas": "Zones actives",
        "map_stats_distance": "Distance estimée",
        "map_stats_time": "Temps de vol estimé",
        "map_stats_lines": "Lignes",
        "map_stats_drone": "Drone",
        "map_stats_altitude": "Altitude",
        "map_stats_overlap": "Chevauchement",
        "map_stats_speed": "Vitesse",
        "map_leaflet_error": "Leaflet n'a pas pu être chargé (hors ligne/réseau).",
        "link_survey_tip": "Ouvrir Survey123",
        "link_arcgis_tip": "Ouvrir la carte ArcGIS",
        "link_home_tip": "Ouvrir la page d'accueil",
        "toilet_tip": "Rouleau de papier toilette",
        "toilet_title": "🧻",
        "toilet_message": "Tu t'attendais à quoi, exactement ?\nOn continue !",
        "settings_title": "Paramètres",
        "theme": "Thème",
        "language": "Langue",
        "units": "Unités",
        "ok": "OK",
        "cancel": "Annuler",
    },
    "Suomi": {
        "title": "LittleOne - Datenkonvertierungssoftware der Kitzrettung Rastatt Baden-Baden (warum liest du das bis hier?)",
        "file": "Tiedosto",
        "settings": "Asetukset",
        "help": "Ohje",
        "about": "Tietoa",
        "documentation": "Dokumentaatio",
        "exit": "Poistu",
        "kmz_file": "KMZ/KML-tiedosto",
        "output_dir": "Tulostuskansio",
        "altitude": "Korkeus",
        "altitude_unit": "m",
        "overlap": "Sivusuuntainen päällekkäisyys",
        "overlap_unit": "%",
        "safe_height": "Turvallinen lähtökorkeus",
        "safe_height_unit": "m",
        "drone": "Drooni",
        "action": "Lopetustoiminto",
        "speed": "Nopeus",
        "speed_unit": "m/s",
        "margin": "Marginaali",
        "optimize_group": "Optimoinnit",
        "optimize_dir": "Kulman optimointi",
        "optimize_elev": "Korkeuden optimointi",
        "convert": "Muunna",
        "day_plan": "Päiväsuunnitelma",
        "reset": "Palauta",
        "output": "Tuloste",
        "ready": "Valmis.",
        "converting": "Muunnetaan …",
        "done": "Valmis.",
        "select_kmz": "Valitse KMZ tai KML.",
        "select_kmz_empty": "Valitse ensin KMZ/KML-tiedosto.",
        "file_not_found": "Määritettyä tiedostoa ei ole olemassa:",
        "import_error": "Tuontivirhe",
        "success": "Onnistui",
        "error": "Virhe",
        "found_features": "Ominaisuudet ladattu",
        "found_polygons": "Polygonit uutettu",
        "parsing_kmz": "Jäsennetään KMZ:ää...",
        "normalizing": "Normalisoidaan geometrioita...",
        "normalized": "Geometriat normalisoitu",
        "writing_kmz": "Kirjoitetaan KMZ-tiedostoja...",
        "no_polygons": "Ei polygoneja löydetty.",
        "kmz_generated": "KMZ-tiedostot luotu",
        "output_folder": "Tulostuskansio",
        "debug_kmls": "Virheenkorjaus KML:t",
        "show_map": "Satelliittikartta",
        "map_refresh": "Päivitä kartta",
        "map_title": "Satelliittikartta",
        "map_loading": "Ladataan alueita karttaa varten...",
        "map_opened": "Satelliittikartta avattu",
        "map_no_polygons": "Karttaa varten ei löytynyt polygoneja.",
        "map_saved": "Kartta tallennettu",
        "map_panel_fallback": "Karttapaneeli tarvitsee QtWebEngine-moduulin. Selainvaratila on käytössä.",
        "map_remove_area": "Poista alue",
        "map_readd_area": "Lisää alue takaisin",
        "map_controls_title": "Kartoituslinjat",
        "map_controls_toggle": "Näytä linjat",
        "map_opt_disabled": "Kulmaoptimointi ei ole käytössä.",
        "map_stats_active_areas": "Aktiiviset alueet",
        "map_stats_distance": "Arvioitu etäisyys",
        "map_stats_time": "Arvioitu lentoaika",
        "map_stats_lines": "Linjat",
        "map_stats_drone": "Drooni",
        "map_stats_altitude": "Korkeus",
        "map_stats_overlap": "Päällekkäisyys",
        "map_stats_speed": "Nopeus",
        "map_leaflet_error": "Leafletin lataus epäonnistui (offline/verkko).",
        "link_survey_tip": "Avaa Survey123",
        "link_arcgis_tip": "Avaa ArcGIS-kartta",
        "link_home_tip": "Avaa kotisivu",
        "toilet_tip": "Vessapaperirulla",
        "toilet_title": "🧻",
        "toilet_message": "Mitä oikein odotit tapahtuvan?\nJatketaan!",
        "settings_title": "Asetukset",
        "theme": "Teema",
        "language": "Kieli",
        "units": "Yksiköt",
        "ok": "OK",
        "cancel": "Peruuta",
    },
}

# Einheiten-System
UNITS = {
    "Metric": {
        "altitude": ("m", 1.0),
        "safe_height": ("m", 1.0),
        "speed": ("m/s", 1.0),
        "label": "Metric (m, m/s)",
    },
    "Imperial": {
        "altitude": ("ft", 3.28084),
        "safe_height": ("ft", 3.28084),
        "speed": ("ft/s", 3.28084),
        "label": "Imperial (ft, ft/s)",
    },
    "Metric-kmh": {
        "altitude": ("m", 1.0),
        "safe_height": ("m", 1.0),
        "speed": ("km/h", 3.6),
        "label": "Metric (m, km/h)",
    },
    "Knots": {
        "altitude": ("m", 1.0),
        "safe_height": ("m", 1.0),
        "speed": ("kts", 1.94384),
        "label": "Metric (m, knots)",
    },
}

BASE_LIMITS = {
    "altitude": (0, 120),
    "safe_height": (0, 500),
    "speed": (1, 21),
}

BASE_DEFAULTS = {
    "altitude": 60.0,
    "safe_height": 60.0,
    "speed": 8.0,
}


def _ensure_engine_modules():
    global kmz_reader, kml_writer, dji_rules, optimize_angle_mod, ENGINE_IMPORT_ERROR
    if kmz_reader is not None and kml_writer is not None and dji_rules is not None:
        return True, None

    errors = []

    def _load_from_source(module_name: str, file_path: Path):
        source = file_path.read_text(encoding="utf-8")
        module = types.ModuleType(module_name)
        module.__file__ = str(file_path)
        exec(compile(source, str(file_path), "exec"), module.__dict__)
        return module

    loaded = None
    base_dirs = [
        Path(__file__).resolve().parent / "LittleOne",
        Path(__file__).resolve().parent.parent / "LittleOne",
    ]
    for base in base_dirs:
        kmz_file = base / "kmz_reader.py"
        writer_file = base / "kml_writer.py"
        rules_file = base / "dji_rules.py"
        optimize_file = base / "optimize_angle.py"
        if not (kmz_file.exists() and writer_file.exists() and rules_file.exists()):
            continue
        try:
            kmz = _load_from_source("LittleOne_kmz_reader_local", kmz_file)
            writer = _load_from_source("LittleOne_kml_writer_local", writer_file)
            rules = _load_from_source("LittleOne_dji_rules_local", rules_file)
            optimizer = None
            if optimize_file.exists():
                optimizer = _load_from_source(
                    "LittleOne_optimize_angle_local", optimize_file
                )
            loaded = (kmz, writer, rules, optimizer)
            break
        except Exception as inner:
            errors.append(inner)

    if loaded is None:
        last = errors[-1] if errors else ENGINE_IMPORT_ERROR
        return False, last

    kmz_reader, kml_writer, dji_rules, optimize_angle_mod = loaded
    ENGINE_IMPORT_ERROR = None
    return True, None


class SettingsDialog(QtWidgets.QDialog):
    """Settings/Preferences Dialog"""

    def __init__(
        self,
        parent=None,
        theme="Light",
        language="Deutsch",
        units="Metric",
        strings=None,
    ):
        super().__init__(parent)
        self.strings = strings or LANGUAGES.get("Deutsch", {})
        self.setWindowTitle(self.strings.get("settings_title", "Einstellungen"))
        self.setModal(True)
        self.resize(400, 180)

        layout = QtWidgets.QFormLayout(self)

        # Theme-Dropdown
        theme_combo = QtWidgets.QComboBox()
        theme_combo.addItems(list(THEMES.keys()))
        theme_combo.setCurrentText(theme)
        layout.addRow(self.strings.get("theme", "Design") + ":", theme_combo)

        # Language-Dropdown
        lang_combo = QtWidgets.QComboBox()
        lang_combo.addItems(list(LANGUAGES.keys()))
        lang_combo.setCurrentText(language)
        layout.addRow(self.strings.get("language", "Sprache") + ":", lang_combo)

        # Units-Dropdown
        units_combo = QtWidgets.QComboBox()
        for key in UNITS.keys():
            units_combo.addItem(UNITS[key]["label"], key)
        (
            units_combo.setCurrentText(units)
            if units in UNITS
            else units_combo.setCurrentIndex(0)
        )
        layout.addRow(self.strings.get("units", "Einheiten") + ":", units_combo)

        # Buttons
        btn_box = QtWidgets.QDialogButtonBox(
            QtWidgets.QDialogButtonBox.StandardButton.Ok
            | QtWidgets.QDialogButtonBox.StandardButton.Cancel
        )
        btn_box.accepted.connect(self.accept)
        btn_box.rejected.connect(self.reject)
        layout.addRow(btn_box)

        self.theme_combo = theme_combo
        self.lang_combo = lang_combo
        self.units_combo = units_combo

    def get_settings(self):
        return (
            self.theme_combo.currentText(),
            self.lang_combo.currentText(),
            self.units_combo.currentData() or self.units_combo.currentText(),
        )


class MapBridge(QtCore.QObject):
    def __init__(self, window):
        super().__init__(window)
        self.window = window

    @QtCore.Slot(str)
    def toggleArea(self, area_key: str):
        self.window.toggle_area_exclusion(area_key)


class MainWindow(QtWidgets.QMainWindow):
    def _resource_path(self, relative_path: str) -> Path:
        base = Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parent.parent))
        return base / relative_path

    def _badge_icon(
        self,
        text: str,
        bg_color: str,
        fg_color: str = "#FFFFFF",
        size: int = 40,
    ) -> QtGui.QIcon:
        pixmap = QtGui.QPixmap(size, size)
        pixmap.fill(QtCore.Qt.GlobalColor.transparent)

        painter = QtGui.QPainter(pixmap)
        painter.setRenderHint(QtGui.QPainter.RenderHint.Antialiasing, True)
        painter.setPen(QtCore.Qt.PenStyle.NoPen)
        painter.setBrush(QtGui.QColor(bg_color))
        painter.drawEllipse(1, 1, size - 2, size - 2)

        font = QtGui.QFont("Segoe UI", 9)
        font.setBold(True)
        painter.setFont(font)
        painter.setPen(QtGui.QPen(QtGui.QColor(fg_color)))
        painter.drawText(
            QtCore.QRectF(0, 0, size, size),
            int(QtCore.Qt.AlignmentFlag.AlignCenter),
            text,
        )
        painter.end()
        return QtGui.QIcon(pixmap)

    def _icon_from_url(
        self, url: str, fallback: QtGui.QIcon | None = None
    ) -> QtGui.QIcon:
        try:
            req = urllib.request.Request(
                url,
                headers={"User-Agent": "LittleOne/1.0"},
            )
            with urllib.request.urlopen(req, timeout=8) as resp:
                data = resp.read()
            pix = QtGui.QPixmap()
            if pix.loadFromData(data):
                return QtGui.QIcon(pix)
        except Exception:
            pass
        return fallback or QtGui.QIcon()

    def _circular_icon_from_pixmap(
        self, source: QtGui.QPixmap, size: int = 40
    ) -> QtGui.QIcon:
        if source.isNull():
            return QtGui.QIcon()

        side = min(source.width(), source.height())
        x = (source.width() - side) // 2
        y = (source.height() - side) // 2
        square = source.copy(x, y, side, side)

        out = QtGui.QPixmap(size, size)
        out.fill(QtCore.Qt.GlobalColor.transparent)

        painter = QtGui.QPainter(out)
        painter.setRenderHint(QtGui.QPainter.RenderHint.Antialiasing, True)

        path = QtGui.QPainterPath()
        path.addEllipse(1, 1, size - 2, size - 2)
        painter.setClipPath(path)
        painter.drawPixmap(
            QtCore.QRect(0, 0, size, size),
            square,
            square.rect(),
        )
        painter.end()
        return QtGui.QIcon(out)

    def _homepage_logo_icon(self, size: int = 40) -> QtGui.QIcon:
        local_logo_path = self._resource_path("data/Icon/homepage_round.PNG")
        if local_logo_path.exists():
            return QtGui.QIcon(str(local_logo_path))

        web_logo = self._icon_from_url(
            "https://www.arcgis.com/sharing/rest/content/items/b02e0603b52349d1bde490783c4c98e4/resources/logo_badische%20J%C3%A4ger.png"
        )
        if not web_logo.isNull():
            return web_logo
        return self._badge_icon("KR", "#2E7D32", size=size)

    def _show_toilet_message(self):
        QtWidgets.QMessageBox.information(
            self,
            self.strings.get("toilet_title", "🧻"),
            self.strings.get(
                "toilet_message",
                "Was hast du denn jetzt erwartet, dass passiert?\nWeiter machen!",
            ),
        )

    def _make_link_button(self, icon: QtGui.QIcon, tooltip: str, url: str):
        btn = QtWidgets.QToolButton()
        btn.setToolTip(tooltip)
        btn.setCursor(QtGui.QCursor(QtCore.Qt.CursorShape.PointingHandCursor))
        btn.setAutoRaise(True)
        btn.setIcon(icon)
        btn.setIconSize(QtCore.QSize(28, 28))
        btn.setFixedSize(34, 34)
        btn.clicked.connect(lambda checked=False, link=url: webbrowser.open(link))
        return btn

    def __init__(self):
        super().__init__()
        self.default_map_center = [48.77, 8.23]  # Landkreis Rastatt
        self.default_map_zoom = 11
        self.excluded_area_keys = set()
        self.current_map_html_path = None
        self.last_map_payload = None
        self.theme = self._detect_system_theme()
        self.language = "Deutsch"
        self.units = "Metric"
        self.strings = LANGUAGES[self.language]

        self.setWindowTitle(self.strings["title"])
        self.resize(1200, 800)

        ico_path = self._resource_path("assets/app.ico")
        if ico_path.exists():
            icon = QtGui.QIcon(str(ico_path))
            app = QtWidgets.QApplication.instance()
            if isinstance(app, QtWidgets.QApplication):
                app.setWindowIcon(icon)
            self.setWindowIcon(icon)

        # --- Menübar ---
        self._create_menu_bar()

        # --- Haupt-Widget (Splitter für Input/Output) ---
        central = QtWidgets.QWidget(self)
        self.setCentralWidget(central)
        main_layout = QtWidgets.QVBoxLayout(central)
        main_layout.setContentsMargins(0, 0, 0, 0)

        # Hauptaufteilung: links Eingaben, rechts Karte + Ausgabe
        main_splitter = QtWidgets.QSplitter(QtCore.Qt.Orientation.Horizontal)

        # --- Oberes Panel: Eingabeberereich ---
        input_panel = QtWidgets.QWidget()
        input_panel.setObjectName("inputPanel")
        input_layout = QtWidgets.QVBoxLayout(input_panel)

        # Formular
        form = QtWidgets.QFormLayout()
        form.setSpacing(8)
        form.setContentsMargins(10, 10, 10, 10)

        links_row = QtWidgets.QHBoxLayout()
        links_row.setContentsMargins(10, 4, 10, 2)
        links_row.setSpacing(8)

        survey_icon = self._icon_from_url(
            "https://survey123.arcgis.com/assets/img/Survey123_for_ArcGIS_220-ba28fef2.png",
            fallback=self._badge_icon("S123", "#6A1B9A"),
        )
        arcgis_icon = self._icon_from_url(
            "https://kitzrettungrabad.maps.arcgis.com/favicon.ico",
            fallback=self._badge_icon("AG", "#0079C1"),
        )
        home_icon = self._homepage_logo_icon()

        self.survey_link_btn = self._make_link_button(
            survey_icon,
            self.strings.get("link_survey_tip", "Survey123 öffnen"),
            "https://survey123.arcgis.com/surveys/e6d87e0a84674ec19e836aa14c1a259d/data",
        )
        links_row.addWidget(self.survey_link_btn)

        self.arcgis_link_btn = self._make_link_button(
            arcgis_icon,
            self.strings.get("link_arcgis_tip", "ArcGIS Map öffnen"),
            "https://kitzrettungrabad.maps.arcgis.com/apps/mapviewer/index.html?webmap=268bfe646cc34f0ca95800a6a85b9425",
        )
        links_row.addWidget(self.arcgis_link_btn)

        self.home_link_btn = self._make_link_button(
            home_icon,
            self.strings.get("link_home_tip", "Homepage öffnen"),
            "https://kitzrettung-kitzrettungrabad.hub.arcgis.com/",
        )
        links_row.addWidget(self.home_link_btn)

        self.toilet_btn = QtWidgets.QToolButton()
        self.toilet_btn.setToolTip(self.strings.get("toilet_tip", "Klopapierrolle"))
        self.toilet_btn.setCursor(
            QtGui.QCursor(QtCore.Qt.CursorShape.PointingHandCursor)
        )
        self.toilet_btn.setAutoRaise(True)
        self.toilet_btn.setText("🧻")
        toilet_font = self.toilet_btn.font()
        toilet_font.setPointSize(14)
        self.toilet_btn.setFont(toilet_font)
        self.toilet_btn.setFixedSize(34, 34)
        self.toilet_btn.clicked.connect(self._show_toilet_message)
        links_row.addWidget(self.toilet_btn)

        links_row.addStretch(1)
        input_layout.addLayout(links_row)

        # File selection rows
        self.kmz_edit = QtWidgets.QLineEdit()
        self.kmz_btn = QtWidgets.QPushButton("…")
        self.kmz_btn.setMaximumWidth(40)
        self.kmz_btn.clicked.connect(self.pick_kmz)

        row_kmz = QtWidgets.QHBoxLayout()
        row_kmz.addWidget(self.kmz_edit)
        row_kmz.addWidget(self.kmz_btn)

        self.out_edit = QtWidgets.QLineEdit(str(Path.cwd() / "out"))
        self.out_btn = QtWidgets.QPushButton("…")
        self.out_btn.setMaximumWidth(40)
        self.out_btn.clicked.connect(self.pick_out)

        row_out = QtWidgets.QHBoxLayout()
        row_out.addWidget(self.out_edit)
        row_out.addWidget(self.out_btn)

        # Create labels for file inputs
        self.kmz_file_label = QtWidgets.QLabel(self.strings["kmz_file"] + ":")
        self.output_dir_label = QtWidgets.QLabel(self.strings["output_dir"] + ":")

        form.addRow(self.kmz_file_label, row_kmz)
        form.addRow(self.output_dir_label, row_out)

        # --- Slider + SpinBox Helper ---
        def slider_spin_row(minv, maxv, default, suffix="", tick_int=5):
            slider = QtWidgets.QSlider(QtCore.Qt.Orientation.Horizontal)
            slider.setRange(minv, maxv)
            slider.setTickInterval(tick_int)
            slider.setTickPosition(QtWidgets.QSlider.TickPosition.TicksBelow)
            slider.setValue(default)

            spin = QtWidgets.QSpinBox()
            spin.setRange(minv, maxv)
            spin.setSuffix(suffix)
            spin.setValue(default)

            slider.valueChanged.connect(spin.setValue)
            spin.valueChanged.connect(slider.setValue)

            row = QtWidgets.QHBoxLayout()
            row.addWidget(slider, 1)
            row.addWidget(spin)
            return slider, spin, row

        # Flughöhe
        alt_unit = " " + self.strings.get("altitude_unit", "m")
        self.alt_slider, self.alt_spin, row_alt = slider_spin_row(
            0, 120, 60, alt_unit, 10
        )
        self.alt_label = QtWidgets.QLabel(self.strings["altitude"] + ":")
        form.addRow(self.alt_label, row_alt)

        # Seitlicher Überlapp
        overlap_unit = " " + self.strings.get("overlap_unit", "%")
        self.overlap_slider, self.overlap_spin, row_overlap = slider_spin_row(
            0, 100, 30, overlap_unit, 10
        )
        self.overlap_label = QtWidgets.QLabel(self.strings["overlap"] + ":")
        form.addRow(self.overlap_label, row_overlap)

        # Sichere Starthöhe
        safe_unit = " " + self.strings.get("safe_height_unit", "m")
        self.safe_slider, self.safe_spin, row_safe = slider_spin_row(
            0, 500, 60, safe_unit, 20
        )
        self.safe_height_label = QtWidgets.QLabel(self.strings["safe_height"] + ":")
        form.addRow(self.safe_height_label, row_safe)

        # Drohne
        self.drone_combo = QtWidgets.QComboBox()
        self.drone_combo.addItems(["M4T", "M3T", "M2EA"])
        self.drone_label = QtWidgets.QLabel(self.strings["drone"] + ":")
        form.addRow(self.drone_label, self.drone_combo)

        # Aktion beenden
        self.action_combo = QtWidgets.QComboBox()
        self.action_combo.addItems(
            [
                "Routenmodus verlassen",
                "Rückkehrfunktion",
                "Landen",
                "Zur Startposition zurückkehren und schweben",
            ]
        )
        self.action_combo.setCurrentText("Rückkehrfunktion")
        self.action_label = QtWidgets.QLabel(self.strings["action"] + ":")
        form.addRow(self.action_label, self.action_combo)

        # Geschwindigkeit
        speed_unit = " " + self.strings.get("speed_unit", "m/s")
        self.speed_slider, self.speed_spin, row_speed = slider_spin_row(
            1, 21, 8, speed_unit, 2
        )
        self.speed_label = QtWidgets.QLabel(self.strings["speed"] + ":")
        form.addRow(self.speed_label, row_speed)

        # Rand
        self.margin_slider, self.margin_spin, row_margin = slider_spin_row(
            0, 100, 0, "", 10
        )
        self.margin_label = QtWidgets.QLabel(self.strings["margin"] + ":")
        form.addRow(self.margin_label, row_margin)

        # Optimierungen
        self.optimize_group = QtWidgets.QGroupBox(self.strings["optimize_group"])
        opt_layout = QtWidgets.QVBoxLayout()

        self.optimize_direction_check = QtWidgets.QCheckBox(
            self.strings["optimize_dir"]
        )
        self.optimize_direction_check.setChecked(True)
        opt_layout.addWidget(self.optimize_direction_check)

        self.elevation_optimize_check = QtWidgets.QCheckBox(
            self.strings["optimize_elev"]
        )
        self.elevation_optimize_check.setChecked(False)
        opt_layout.addWidget(self.elevation_optimize_check)

        self.optimize_group.setLayout(opt_layout)
        form.addRow(self.optimize_group)

        # Kopplungslogik
        self.alt_slider.valueChanged.connect(self._sync_safe_with_alt)

        input_layout.addLayout(form)

        # --- Progressbar (initial versteckt) ---
        self.progress = QtWidgets.QProgressBar()
        self.progress.setMaximum(100)
        self.progress.setValue(0)
        self.progress.setTextVisible(False)
        self.progress.setFixedHeight(8)
        self.progress.setVisible(False)
        input_layout.addWidget(self.progress)

        # --- Buttons ---
        button_layout = QtWidgets.QHBoxLayout()

        self.convert_btn = QtWidgets.QPushButton(self.strings["convert"])
        self.convert_btn.setMinimumHeight(40)
        font = self.convert_btn.font()
        font.setPointSize(11)
        font.setBold(True)
        self.convert_btn.setFont(font)
        self.convert_btn.clicked.connect(self.convert)

        self.map_btn = QtWidgets.QPushButton(
            self.strings.get("map_refresh", "Karte aktualisieren")
        )
        self.map_btn.setMinimumHeight(40)
        map_font = self.map_btn.font()
        map_font.setPointSize(10)
        self.map_btn.setFont(map_font)
        self.map_btn.clicked.connect(self.show_satellite_map)

        self.day_plan_btn = QtWidgets.QPushButton(
            self.strings.get("day_plan", "Tagesplan")
        )
        self.day_plan_btn.setMinimumHeight(40)
        day_plan_font = self.day_plan_btn.font()
        day_plan_font.setPointSize(10)
        self.day_plan_btn.setFont(day_plan_font)
        self.day_plan_btn.clicked.connect(self.generate_day_plan)

        self.reset_btn = QtWidgets.QPushButton(
            self.strings.get("reset", "Zurücksetzen")
        )
        self.reset_btn.setMinimumHeight(40)
        reset_font = self.reset_btn.font()
        reset_font.setPointSize(10)
        self.reset_btn.setFont(reset_font)
        self.reset_btn.clicked.connect(self.reset_to_defaults)

        self.convert_btn.setMinimumWidth(180)
        self.map_btn.setMinimumWidth(180)
        self.day_plan_btn.setMinimumWidth(180)
        self.reset_btn.setMinimumWidth(160)

        button_layout.addWidget(self.convert_btn, stretch=2)
        button_layout.addWidget(self.map_btn, stretch=1)
        button_layout.addWidget(self.day_plan_btn, stretch=1)
        button_layout.addWidget(self.reset_btn, stretch=1)
        button_layout.setContentsMargins(0, 5, 0, 5)

        input_layout.addLayout(button_layout)

        # --- Unteres Panel links: Output/Logs ---
        output_panel = QtWidgets.QWidget()
        output_panel.setMinimumHeight(140)
        output_layout = QtWidgets.QVBoxLayout(output_panel)
        output_layout.setContentsMargins(0, 0, 0, 0)

        self.output_label = QtWidgets.QLabel(self.strings["output"])
        self.output_label.setObjectName("outputLabel")
        output_layout.addWidget(self.output_label)

        self.log = QtWidgets.QPlainTextEdit()
        self.log.setReadOnly(True)
        self.log.setMinimumHeight(120)
        output_layout.addWidget(self.log)

        input_layout.addWidget(output_panel)

        input_panel.setMinimumWidth(520)
        main_splitter.addWidget(input_panel)

        # --- Mittleres Panel: Kartenansicht ---
        self.map_panel = QtWidgets.QWidget()
        self.map_panel.setMinimumHeight(260)
        map_layout = QtWidgets.QVBoxLayout(self.map_panel)
        map_layout.setContentsMargins(0, 0, 0, 0)

        self.map_view = None
        self.map_fallback_label = None
        self.map_bridge = None
        self.web_channel = None
        if WEBENGINE_AVAILABLE and QtWebEngineWidgets is not None:
            self.map_view = QtWebEngineWidgets.QWebEngineView(self.map_panel)
            if QtWebEngineCore is not None:
                map_settings = self.map_view.settings()
                map_settings.setAttribute(
                    QtWebEngineCore.QWebEngineSettings.WebAttribute.LocalContentCanAccessRemoteUrls,
                    True,
                )
                map_settings.setAttribute(
                    QtWebEngineCore.QWebEngineSettings.WebAttribute.LocalContentCanAccessFileUrls,
                    True,
                )
            self.map_bridge = MapBridge(self)
            self.web_channel = QtWebChannel.QWebChannel(self.map_view.page())
            self.web_channel.registerObject("bridge", self.map_bridge)
            self.map_view.page().setWebChannel(self.web_channel)
            map_layout.addWidget(self.map_view)
        else:
            self.map_fallback_label = QtWidgets.QLabel(
                self.strings.get(
                    "map_panel_fallback",
                    "Kartenpanel benötigt QtWebEngine. Browser-Fallback ist aktiv.",
                )
            )
            self.map_fallback_label.setWordWrap(True)
            self.map_fallback_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
            map_layout.addWidget(self.map_fallback_label)

        # Rechtes Panel: nur Karte (volle Höhe)
        right_panel = QtWidgets.QWidget()
        right_layout = QtWidgets.QVBoxLayout(right_panel)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.addWidget(self.map_panel)

        right_panel.setMinimumWidth(520)
        main_splitter.addWidget(right_panel)
        main_splitter.setStretchFactor(0, 2)
        main_splitter.setStretchFactor(1, 3)

        self.main_splitter = main_splitter
        main_layout.addWidget(self.main_splitter)

        self.main_splitter.setSizes([540, 900])

        self.status = self.statusBar()
        self.status.showMessage(self.strings["ready"])

        self._apply_theme()
        self._write_default_map()
        self._update_map_panel_visibility()

    def _create_menu_bar(self):
        menubar = self.menuBar()

        # File menu
        file_menu = menubar.addMenu(self.strings["file"])
        exit_action = file_menu.addAction(self.strings["exit"])
        exit_action.triggered.connect(self.close)

        # Settings menu
        settings_menu = menubar.addMenu(self.strings["settings"])

        # Theme submenu
        theme_submenu = settings_menu.addMenu(self.strings["theme"])
        self.theme_actions = {}
        for theme_name in THEMES.keys():
            action = theme_submenu.addAction(theme_name)
            action.setCheckable(True)
            action.setChecked(theme_name == self.theme)
            action.triggered.connect(lambda checked, t=theme_name: self._set_theme(t))
            self.theme_actions[theme_name] = action

        # Language submenu
        lang_submenu = settings_menu.addMenu(self.strings["language"])
        self.lang_actions = {}
        for lang_name in LANGUAGES.keys():
            action = lang_submenu.addAction(lang_name)
            action.setCheckable(True)
            action.setChecked(lang_name == self.language)
            action.triggered.connect(lambda checked, l=lang_name: self._set_language(l))
            self.lang_actions[lang_name] = action

        # Units submenu
        units_submenu = settings_menu.addMenu(self.strings["units"])
        self.units_actions = {}
        for unit_key in UNITS.keys():
            unit_label = UNITS[unit_key]["label"]
            action = units_submenu.addAction(unit_label)
            action.setCheckable(True)
            action.setChecked(unit_key == self.units)
            action.triggered.connect(lambda checked, u=unit_key: self._set_units(u))
            self.units_actions[unit_key] = action

        settings_menu.addSeparator()
        update_action = settings_menu.addAction("Nach Updates suchen")
        update_action.triggered.connect(self.check_for_updates)

        # Help menu
        help_menu = menubar.addMenu(self.strings["help"])

        # Documentation
        help_menu.addSeparator()
        doc_action = help_menu.addAction(
            "📖 " + self.strings.get("documentation", "Dokumentation")
        )
        doc_action.triggered.connect(self.open_documentation)

        # GitHub
        github_action = help_menu.addAction("GitHub Repository")
        github_action.triggered.connect(self.open_github)

        # About
        help_menu.addSeparator()
        about_action = help_menu.addAction(self.strings["about"])
        about_action.triggered.connect(self.show_about)

        # Easter Egg
        easter_action = help_menu.addAction("G-Mode aktivieren")
        easter_action.triggered.connect(self.open_easter_egg)

    def open_easter_egg(self):
        """Open the ultimate best help source 🎵"""
        webbrowser.open(
            "https://www.youtube.com/watch?v=xMHJGd3wwZk&list=RDxMHJGd3wwZk&start_radio=1"
        )

    def show_settings(self):
        dlg = SettingsDialog(self, self.theme, self.language, self.units, self.strings)
        if dlg.exec():
            new_theme, new_lang, new_units = dlg.get_settings()
            changed = False
            if new_theme != self.theme:
                self.theme = new_theme
                changed = True
                self._apply_theme()
            if new_lang != self.language:
                self.language = new_lang
                self.strings = LANGUAGES[self.language]
                changed = True
            if new_units != self.units:
                self.units = new_units
                changed = True
            if changed:
                self._update_ui_text()

    def _set_theme(self, theme_name):
        """Set theme and update UI"""
        if self.theme != theme_name:
            self.theme = theme_name
            self._apply_theme()
            # Update checkmarks
            for t, action in self.theme_actions.items():
                action.setChecked(t == theme_name)

    def _set_language(self, lang_name):
        """Set language and update UI"""
        if self.language != lang_name:
            self.language = lang_name
            self.strings = LANGUAGES[self.language]
            self._update_ui_text()
            # Update checkmarks
            for l, action in self.lang_actions.items():
                action.setChecked(l == lang_name)

    def _set_units(self, unit_key):
        """Set units and update UI"""
        if self.units != unit_key:
            metric_values = self._get_metric_values()
            self.units = unit_key
            self._apply_unit_ranges()
            self._set_display_values_from_metric(metric_values)
            self._update_ui_text()
            # Update checkmarks
            for u, action in self.units_actions.items():
                action.setChecked(u == unit_key)

    def _unit_factor(self, key: str) -> float:
        unit_config = UNITS.get(self.units, UNITS["Metric"])
        return float(unit_config[key][1])

    def _to_metric(self, value: float, key: str) -> float:
        factor = self._unit_factor(key)
        if factor == 0:
            return float(value)
        return float(value) / factor

    def _from_metric(self, value: float, key: str) -> float:
        factor = self._unit_factor(key)
        return float(value) * factor

    def _get_metric_values(self):
        return {
            "altitude": self._to_metric(self.alt_spin.value(), "altitude"),
            "safe_height": self._to_metric(self.safe_spin.value(), "safe_height"),
            "speed": self._to_metric(self.speed_spin.value(), "speed"),
        }

    def _apply_unit_ranges(self):
        alt_factor = self._unit_factor("altitude")
        safe_factor = self._unit_factor("safe_height")
        speed_factor = self._unit_factor("speed")

        alt_min, alt_max = BASE_LIMITS["altitude"]
        safe_min, safe_max = BASE_LIMITS["safe_height"]
        speed_min, speed_max = BASE_LIMITS["speed"]

        self.alt_slider.setRange(
            round(alt_min * alt_factor), round(alt_max * alt_factor)
        )
        self.alt_spin.setRange(round(alt_min * alt_factor), round(alt_max * alt_factor))

        self.safe_slider.setRange(
            round(safe_min * safe_factor), round(safe_max * safe_factor)
        )
        self.safe_spin.setRange(
            round(safe_min * safe_factor), round(safe_max * safe_factor)
        )

        speed_min_disp = max(1, round(speed_min * speed_factor))
        speed_max_disp = max(speed_min_disp, round(speed_max * speed_factor))
        self.speed_slider.setRange(speed_min_disp, speed_max_disp)
        self.speed_spin.setRange(speed_min_disp, speed_max_disp)

    def _set_display_values_from_metric(self, metric_values):
        alt_disp = round(self._from_metric(metric_values["altitude"], "altitude"))
        safe_disp = round(
            self._from_metric(metric_values["safe_height"], "safe_height")
        )
        speed_disp = round(self._from_metric(metric_values["speed"], "speed"))

        self.alt_slider.blockSignals(True)
        self.alt_spin.blockSignals(True)
        self.safe_slider.blockSignals(True)
        self.safe_spin.blockSignals(True)
        self.speed_slider.blockSignals(True)
        self.speed_spin.blockSignals(True)

        alt_disp = max(
            self.alt_slider.minimum(), min(self.alt_slider.maximum(), alt_disp)
        )
        self.alt_slider.setValue(alt_disp)
        self.alt_spin.setValue(alt_disp)

        safe_disp = max(safe_disp, alt_disp)
        safe_disp = max(
            self.safe_slider.minimum(), min(self.safe_slider.maximum(), safe_disp)
        )
        self.safe_slider.setValue(safe_disp)
        self.safe_spin.setValue(safe_disp)

        speed_disp = max(
            self.speed_slider.minimum(), min(self.speed_slider.maximum(), speed_disp)
        )
        self.speed_slider.setValue(speed_disp)
        self.speed_spin.setValue(speed_disp)

        self.alt_slider.blockSignals(False)
        self.alt_spin.blockSignals(False)
        self.safe_slider.blockSignals(False)
        self.safe_spin.blockSignals(False)
        self.speed_slider.blockSignals(False)
        self.speed_spin.blockSignals(False)

    def _apply_theme(self):
        """Apply theme stylesheet"""
        theme_colors = THEMES[self.theme]
        bg = theme_colors["bg"]
        fg = theme_colors["fg"]
        accent = theme_colors["accent"]
        button_bg = theme_colors["button_bg"]
        border = theme_colors["border"]
        hover_bg = theme_colors.get("hover_bg", button_bg)

        stylesheet = f"""
        QMainWindow, QWidget {{
            background-color: {bg};
            color: {fg};
        }}
        QWidget#inputPanel {{
            background-color: {bg};
            border: 1px solid {border};
            border-radius: 8px;
        }}
        QLineEdit, QPlainTextEdit, QSpinBox {{
            background-color: {bg};
            color: {fg};
            border: 1px solid {border};
            padding: 6px;
            border-radius: 4px;
            selection-background-color: {accent};
        }}
        QComboBox {{
            background-color: {bg};
            color: {fg};
            border: 1px solid {border};
            padding: 6px;
            border-radius: 4px;
        }}
        QComboBox::drop-down {{
            border: none;
        }}
        QComboBox QAbstractItemView {{
            background-color: {bg};
            color: {fg};
            selection-background-color: {accent};
            padding: 2px;
        }}
        QPushButton {{
            background-color: {button_bg};
            color: {fg};
            border: 1px solid {border};
            padding: 8px 14px;
            border-radius: 4px;
            font-weight: 500;
        }}
        QPushButton:hover {{
            background-color: {hover_bg};
            border: 1px solid {accent};
        }}
        QPushButton#convertBtn {{
            background-color: {accent};
            color: white;
            padding: 10px 18px;
            font-weight: bold;
            font-size: 11pt;
        }}
        QPushButton#convertBtn:hover {{
            background-color: {accent};
            opacity: 0.9;
        }}
        QGroupBox {{
            color: {fg};
            border: 1px solid {border};
            border-radius: 5px;
            margin-top: 8px;
            padding-top: 10px;
        }}
        QGroupBox::title {{
            subcontrol-origin: margin;
            subcontrol-position: top left;
            left: 10px;
            padding: 0px 3px;
        }}
        QCheckBox {{
            color: {fg};
            spacing: 6px;
        }}
        QCheckBox::indicator {{
            width: 18px;
            height: 18px;
        }}
        QCheckBox::indicator:unchecked {{
            background-color: {bg};
            border: 1px solid {border};
            border-radius: 3px;
        }}
        QCheckBox::indicator:checked {{
            background-color: {accent};
            border: 1px solid {accent};
            border-radius: 3px;
        }}
        QLabel {{
            color: {fg};
        }}
        QLabel#outputLabel {{
            font-weight: bold;
            color: {accent};
            padding: 5px;
        }}
        QProgressBar {{
            border: 1px solid {border};
            border-radius: 4px;
            background-color: {button_bg};
            text-align: center;
            color: {fg};
        }}
        QProgressBar::chunk {{
            background-color: {accent};
            border-radius: 2px;
        }}
        QSlider::groove:horizontal {{
            border: 1px solid {border};
            height: 6px;
            background: {button_bg};
            border-radius: 3px;
        }}
        QSlider::handle:horizontal {{
            background: {accent};
            border: 1px solid {accent};
            width: 14px;
            margin: -4px 0;
            border-radius: 7px;
        }}
        QSlider::sub-page:horizontal {{
            background: {accent};
            border-radius: 3px;
        }}
        QMenu {{
            background-color: {bg};
            color: {fg};
            border: 1px solid {border};
        }}
        QMenu::item:selected {{
            background-color: {accent};
            color: white;
        }}
        QMenuBar {{
            background-color: {button_bg};
            color: {fg};
            border-bottom: 1px solid {border};
        }}
        QMenuBar::item:selected {{
            background-color: {accent};
            color: white;
        }}
        QStatusBar {{
            background-color: {button_bg};
            color: {fg};
            border-top: 1px solid {border};
        }}
        """
        self.setStyleSheet(stylesheet)
        self.convert_btn.setObjectName("convertBtn")

    def _update_ui_text(self):
        """Update all UI text after language or units change"""
        self.setWindowTitle(self.strings["title"])

        # Get unit system
        unit_config = UNITS.get(self.units, UNITS["Metric"])
        alt_unit, alt_factor = unit_config["altitude"]
        safe_unit, safe_factor = unit_config["safe_height"]
        speed_unit, speed_factor = unit_config["speed"]

        # Update file input labels
        self.kmz_file_label.setText(self.strings["kmz_file"] + ":")
        self.output_dir_label.setText(self.strings["output_dir"] + ":")
        self.output_label.setText(self.strings["output"])

        # Update form labels with units
        self.alt_label.setText(self.strings["altitude"] + " (" + alt_unit + "):")
        self.overlap_label.setText(self.strings["overlap"] + ":")
        self.safe_height_label.setText(
            self.strings["safe_height"] + " (" + safe_unit + "):"
        )
        self.drone_label.setText(self.strings["drone"] + ":")
        self.action_label.setText(self.strings["action"] + ":")
        self.speed_label.setText(self.strings["speed"] + " (" + speed_unit + "):")
        self.margin_label.setText(self.strings["margin"] + ":")

        # Update spinbox suffixes
        self.alt_spin.setSuffix(" " + alt_unit)
        self.safe_spin.setSuffix(" " + safe_unit)
        self.speed_spin.setSuffix(" " + speed_unit)

        # Update optimize group
        self.optimize_group.setTitle(self.strings["optimize_group"])
        self.optimize_direction_check.setText(self.strings["optimize_dir"])
        self.elevation_optimize_check.setText(self.strings["optimize_elev"])

        # Update buttons
        self.convert_btn.setText(self.strings["convert"])
        self.map_btn.setText(self.strings.get("map_refresh", "Karte aktualisieren"))
        self.day_plan_btn.setText(self.strings.get("day_plan", "Tagesplan"))
        self.reset_btn.setText(self.strings.get("reset", "Zurücksetzen"))

        if self.map_fallback_label is not None:
            self.map_fallback_label.setText(
                self.strings.get(
                    "map_panel_fallback",
                    "Kartenpanel benötigt QtWebEngine. Browser-Fallback ist aktiv.",
                )
            )

        if hasattr(self, "survey_link_btn"):
            self.survey_link_btn.setToolTip(
                self.strings.get("link_survey_tip", "Survey123 öffnen")
            )
        if hasattr(self, "arcgis_link_btn"):
            self.arcgis_link_btn.setToolTip(
                self.strings.get("link_arcgis_tip", "ArcGIS Map öffnen")
            )
        if hasattr(self, "home_link_btn"):
            self.home_link_btn.setToolTip(
                self.strings.get("link_home_tip", "Homepage öffnen")
            )
        if hasattr(self, "toilet_btn"):
            self.toilet_btn.setToolTip(self.strings.get("toilet_tip", "Klopapierrolle"))

        # Recreate menu bar for language change
        menubar = self.menuBar()
        menubar.clear()
        self._create_menu_bar()

        # Update status bar
        self.status.showMessage(self.strings["ready"])

        # Refresh map texts in embedded map HTML (title/controls in white overlay)
        self._refresh_map_language_texts()

    def changeEvent(self, event):
        super().changeEvent(event)
        if event.type() == QtCore.QEvent.Type.WindowStateChange:
            self._update_map_panel_visibility()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self._update_map_panel_visibility()

    def show_about(self):
        QtWidgets.QMessageBox.information(
            self,
            self.strings["about"],
            "Kitzrettung – DJI Drohnen-Missionsplaner v1.0\n\n"
            "Ein professionelles Tool zur Erstellung von DJI-Missionen\n"
            "aus KML/KMZ-Gebietsdaten.\n\n"
            "Unterstützte Drohnen: M4T, M3T, M2EA\n\n"
            "© 2024–2026 | Lizenz: MIT\n\n"
            "Für vollständige Dokumentation siehe Help → Dokumentation",
        )

    def open_documentation(self):
        """Open README.md in browser or default viewer"""
        readme_path = Path(__file__).parent.parent / "README.md"
        if readme_path.exists():
            # Try to open in browser or default viewer
            try:
                if sys.platform == "win32":
                    subprocess.Popen(["notepad", str(readme_path)])
                else:
                    webbrowser.open(readme_path.as_uri())
            except Exception as e:
                QtWidgets.QMessageBox.warning(
                    self,
                    self.strings["error"],
                    f"Konnte Dokumentation nicht öffnen:\n{str(e)}",
                )
        else:
            QtWidgets.QMessageBox.information(
                self,
                self.strings.get("documentation", "Dokumentation"),
                "README.md nicht gefunden.\n\n"
                "Bitte besuche das GitHub Repository für die vollständige Dokumentation:\n"
                "https://github.com/messmersvenpriv/LittleOne",
            )

    def open_github(self):
        """Open GitHub repository in browser"""
        github_url = "https://github.com/messmersvenpriv/LittleOne"
        try:
            webbrowser.open(github_url)
        except Exception as e:
            QtWidgets.QMessageBox.warning(
                self,
                self.strings["error"],
                f"Konnte GitHub nicht öffnen:\n{str(e)}\n\n"
                f"Bitte besuche manuell:\n{github_url}",
            )

    def _parse_version(self, text: str):
        nums = [int(n) for n in re.findall(r"\d+", str(text))[:4]]
        while len(nums) < 4:
            nums.append(0)
        return tuple(nums)

    def _fetch_latest_release(self):
        api_url = f"https://api.github.com/repos/{GITHUB_REPO}/releases/latest"
        req = urllib.request.Request(
            api_url,
            headers={
                "Accept": "application/vnd.github+json",
                "User-Agent": "LittleOne-Updater",
            },
        )
        with urllib.request.urlopen(req, timeout=12) as resp:
            data = resp.read().decode("utf-8", errors="replace")
        return json.loads(data)

    def _pick_windows_asset(self, release_json):
        assets = release_json.get("assets") or []
        exe_assets = [
            a for a in assets if str(a.get("name", "")).lower().endswith(".exe")
        ]
        if not exe_assets:
            return None
        preferred = sorted(exe_assets, key=lambda x: len(str(x.get("name", ""))))
        return preferred[0]

    def check_for_updates(self):
        try:
            self.status.showMessage("Prüfe auf Updates ...")
            QtCore.QCoreApplication.processEvents()

            release = self._fetch_latest_release()
            latest_tag = str(release.get("tag_name") or "").strip()
            latest_ver = self._parse_version(latest_tag)
            current_ver = self._parse_version(APP_VERSION)

            if latest_ver <= current_ver:
                QtWidgets.QMessageBox.information(
                    self,
                    "Updates",
                    f"Du nutzt bereits die aktuelle Version ({APP_VERSION}).",
                )
                self.status.showMessage("Keine Updates verfügbar")
                return

            release_name = release.get("name") or latest_tag or "Neue Version"
            release_page = (
                release.get("html_url") or f"https://github.com/{GITHUB_REPO}/releases"
            )
            asset = self._pick_windows_asset(release)

            msg = (
                f"Update verfügbar: {release_name}\n"
                f"Aktuell: {APP_VERSION}\n"
                f"Neu: {latest_tag or 'unbekannt'}\n\n"
            )

            can_auto_install = bool(
                asset and getattr(sys, "frozen", False) and sys.platform == "win32"
            )
            if can_auto_install:
                msg += "Jetzt herunterladen und Update starten?"
            else:
                msg += "Download-Seite öffnen?"

            btn = QtWidgets.QMessageBox.question(
                self,
                "Update verfügbar",
                msg,
                QtWidgets.QMessageBox.StandardButton.Yes
                | QtWidgets.QMessageBox.StandardButton.No,
            )
            if btn != QtWidgets.QMessageBox.StandardButton.Yes:
                self.status.showMessage("Updateprüfung beendet")
                return

            if can_auto_install:
                if asset is None:
                    webbrowser.open(release_page)
                    self.status.showMessage("Release-Seite geöffnet")
                    return
                url = asset.get("browser_download_url")
                name = asset.get("name") or "LittleOne-Update.exe"
                if not url:
                    webbrowser.open(release_page)
                    self.status.showMessage("Release-Seite geöffnet")
                    return

                target = Path(tempfile.gettempdir()) / name
                self.status.showMessage("Lade Update herunter ...")
                QtCore.QCoreApplication.processEvents()
                urllib.request.urlretrieve(url, str(target))

                QtWidgets.QMessageBox.information(
                    self,
                    "Update",
                    "Update wurde geladen. Der Installer wird jetzt gestartet.",
                )
                subprocess.Popen([str(target)])
                QtWidgets.QApplication.quit()
                return

            webbrowser.open(release_page)
            self.status.showMessage("Release-Seite geöffnet")
        except urllib.error.URLError as ex:
            QtWidgets.QMessageBox.warning(
                self,
                "Updatefehler",
                f"Konnte Update-Informationen nicht laden:\n{ex}",
            )
            self.status.showMessage("Updateprüfung fehlgeschlagen")
        except Exception as ex:
            QtWidgets.QMessageBox.warning(
                self,
                "Updatefehler",
                f"Fehler bei Updateprüfung:\n{ex}",
            )
            self.status.showMessage("Updateprüfung fehlgeschlagen")

    # --- Logik: sichere Starthöhe folgt der Flughöhe nach oben ---
    def _sync_safe_with_alt(self, alt_value: int):
        if self.safe_spin.value() < alt_value:
            try:
                self.safe_spin.blockSignals(True)
                self.safe_slider.blockSignals(True)
                self.safe_spin.setValue(alt_value)
                self.safe_slider.setValue(alt_value)
            finally:
                self.safe_spin.blockSignals(False)
                self.safe_slider.blockSignals(False)

    def pick_kmz(self):
        dlg = QtWidgets.QFileDialog(self)
        dlg.setNameFilters(["KMZ (*.kmz)", "KML (*.kml)", "All Files (*.*)"])
        if dlg.exec():
            self.kmz_edit.setText(dlg.selectedFiles()[0])
            self.excluded_area_keys.clear()

    def pick_out(self):
        dir_ = QtWidgets.QFileDialog.getExistingDirectory(
            self, "Ausgabeordner wählen", str(Path.cwd())
        )
        if dir_:
            self.out_edit.setText(dir_)

    def logln(self, msg: str):
        self.log.appendPlainText(msg)
        self.log.verticalScrollBar().setValue(self.log.verticalScrollBar().maximum())

    def _validate_input_path(self) -> Path | None:
        kmz_path_str = self.kmz_edit.text().strip()
        if not kmz_path_str:
            QtWidgets.QMessageBox.warning(
                self,
                self.strings.get("error", "Fehler"),
                self.strings.get(
                    "select_kmz_empty", "Bitte wählen Sie eine KMZ/KML-Datei aus"
                ),
            )
            return None

        kmz_path = Path(kmz_path_str)
        if not kmz_path.exists():
            QtWidgets.QMessageBox.warning(
                self,
                self.strings.get("error", "Fehler"),
                self.strings.get(
                    "file_not_found",
                    f"Die Datei wurde nicht gefunden:\n\n{kmz_path}",
                ),
            )
            return None
        return kmz_path

    def _to_leaflet_rings(self, polygon):
        rings = []
        ext = [[float(lat), float(lon)] for lon, lat in polygon.exterior.coords]
        rings.append(ext)
        for ring in polygon.interiors:
            rings.append([[float(lat), float(lon)] for lon, lat in ring.coords])
        return rings

    def _make_area_key(self, applicant: str, label: str, rings) -> str:
        payload = {
            "applicant": str(applicant or ""),
            "label": str(label or ""),
            "rings": [
                [[round(float(pt[0]), 7), round(float(pt[1]), 7)] for pt in ring]
                for ring in rings
            ],
        }
        raw = json.dumps(payload, ensure_ascii=False, sort_keys=True)
        return hashlib.md5(raw.encode("utf-8", errors="ignore")).hexdigest()[:16]

    def _collect_geometry_entries(self, features, summaries):
        from shapely.geometry import Polygon, MultiPolygon

        entries = []
        for feat, summary in zip(features, summaries):
            geom = feat.geom
            if geom is None:
                continue

            applicant = " ".join(
                x
                for x in [summary.antragsteller_vorname, summary.antragsteller_name]
                if x
            ).strip()
            if not applicant:
                applicant = str(summary.antragsteller_name or feat.name or "Unbekannt")

            base_label = str(summary.schlag_flurstueck or feat.name or "Fläche")

            def _append(poly, label):
                rings = self._to_leaflet_rings(poly)
                entries.append(
                    {
                        "applicant": applicant,
                        "label": label,
                        "rings": rings,
                        "key": self._make_area_key(applicant, label, rings),
                        "geom": poly,
                        "summary": summary,
                        "feature": feat,
                    }
                )

            if isinstance(geom, Polygon):
                _append(geom, base_label)
            elif isinstance(geom, MultiPolygon):
                for idx, poly in enumerate(geom.geoms, start=1):
                    _append(poly, f"{base_label}-{idx}")

        for entry in entries:
            centroid = entry["geom"].centroid
            entry["center"] = [float(centroid.y), float(centroid.x)]
        return entries

    def _collect_map_items(self, features, summaries):
        entries = self._collect_geometry_entries(features, summaries)
        current_keys = {entry["key"] for entry in entries}
        self.excluded_area_keys.intersection_update(current_keys)
        return [
            {
                "applicant": entry["applicant"],
                "label": entry["label"],
                "rings": entry["rings"],
                "key": entry["key"],
                "excluded": entry["key"] in self.excluded_area_keys,
                "center": entry.get("center"),
            }
            for entry in entries
        ]

    def _haversine_m(self, lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        radius_m = 6371008.8
        phi1 = math.radians(float(lat1))
        phi2 = math.radians(float(lat2))
        d_phi = math.radians(float(lat2) - float(lat1))
        d_lambda = math.radians(float(lon2) - float(lon1))
        a = (
            math.sin(d_phi / 2.0) ** 2
            + math.cos(phi1) * math.cos(phi2) * math.sin(d_lambda / 2.0) ** 2
        )
        return (
            2.0
            * radius_m
            * math.atan2(
                math.sqrt(max(0.0, a)),
                math.sqrt(max(1e-12, 1.0 - a)),
            )
        )

    def _fetch_osrm_json(self, endpoint: str, query: dict | None = None):
        query = query or {}
        query_str = urllib.parse.urlencode(query)
        url = f"https://router.project-osrm.org{endpoint}"
        if query_str:
            url += f"?{query_str}"
        req = urllib.request.Request(
            url,
            headers={"User-Agent": "LittleOne-DayPlan/1.0"},
        )
        with urllib.request.urlopen(req, timeout=12) as resp:
            payload = resp.read().decode("utf-8", errors="replace")
        return json.loads(payload)

    def _build_drive_matrix(self, points_lonlat):
        n = len(points_lonlat)
        if n <= 1:
            return [[0.0]], [[0.0]], "single"

        try:
            coord_str = ";".join(f"{lon:.7f},{lat:.7f}" for lon, lat in points_lonlat)
            data = self._fetch_osrm_json(
                f"/table/v1/driving/{coord_str}",
                {"annotations": "duration,distance"},
            )
            durations = data.get("durations")
            distances = data.get("distances")
            if not durations or len(durations) != n:
                raise ValueError("Ungültige OSRM-Matrix")

            clean_durations = [[0.0 for _ in range(n)] for _ in range(n)]
            clean_distances = [[0.0 for _ in range(n)] for _ in range(n)]
            avg_speed_mps = 60.0 / 3.6
            for i in range(n):
                for j in range(n):
                    if i == j:
                        continue
                    fallback_d = self._haversine_m(
                        points_lonlat[i][1],
                        points_lonlat[i][0],
                        points_lonlat[j][1],
                        points_lonlat[j][0],
                    )
                    raw_d = None
                    raw_t = None
                    try:
                        raw_d = distances[i][j] if distances and distances[i] else None
                    except Exception:
                        raw_d = None
                    try:
                        raw_t = durations[i][j] if durations and durations[i] else None
                    except Exception:
                        raw_t = None

                    d_m = float(raw_d) if raw_d is not None else float(fallback_d)
                    if not math.isfinite(d_m) or d_m <= 0:
                        d_m = float(fallback_d)

                    t_s = (
                        float(raw_t)
                        if raw_t is not None
                        else (d_m / max(2.0, avg_speed_mps))
                    )
                    if not math.isfinite(t_s) or t_s <= 0:
                        t_s = d_m / max(2.0, avg_speed_mps)

                    clean_distances[i][j] = d_m
                    clean_durations[i][j] = t_s

            return clean_durations, clean_distances, "osrm"
        except Exception as ex:
            self.logln(f"ℹ Tagesplan-Fallback ohne OSRM-Matrix: {ex}")

        durations = [[0.0 for _ in range(n)] for _ in range(n)]
        distances = [[0.0 for _ in range(n)] for _ in range(n)]
        avg_speed_mps = 60.0 / 3.6
        for i in range(n):
            lon1, lat1 = points_lonlat[i]
            for j in range(n):
                if i == j:
                    continue
                lon2, lat2 = points_lonlat[j]
                d_m = self._haversine_m(lat1, lon1, lat2, lon2)
                distances[i][j] = d_m
                durations[i][j] = d_m / max(2.0, avg_speed_mps)
        return durations, distances, "geo"

    def _path_cost(self, order, matrix) -> float:
        if len(order) <= 1:
            return 0.0
        return float(
            sum(float(matrix[order[i]][order[i + 1]]) for i in range(len(order) - 1))
        )

    def _two_opt_open_path(self, order, matrix):
        if len(order) < 4:
            return list(order)
        best = list(order)
        improved = True
        while improved:
            improved = False
            best_cost = self._path_cost(best, matrix)
            for i in range(1, len(best) - 2):
                for j in range(i + 1, len(best) - 1):
                    candidate = (
                        best[:i] + list(reversed(best[i : j + 1])) + best[j + 1 :]
                    )
                    cand_cost = self._path_cost(candidate, matrix)
                    if cand_cost + 1e-6 < best_cost:
                        best = candidate
                        best_cost = cand_cost
                        improved = True
        return best

    def _optimize_visit_order(self, matrix):
        n = len(matrix)
        if n <= 1:
            return [0]

        best_order = None
        best_cost = float("inf")
        for start in range(n):
            unvisited = set(range(n))
            order = [start]
            unvisited.remove(start)
            while unvisited:
                prev = order[-1]
                nxt = min(unvisited, key=lambda idx: float(matrix[prev][idx]))
                order.append(nxt)
                unvisited.remove(nxt)
            order = self._two_opt_open_path(order, matrix)
            cost = self._path_cost(order, matrix)
            if cost < best_cost:
                best_cost = cost
                best_order = order

        return best_order or list(range(n))

    def _segment_route(self, start_lonlat, end_lonlat):
        start_lon, start_lat = start_lonlat
        end_lon, end_lat = end_lonlat
        try:
            coord_str = (
                f"{start_lon:.7f},{start_lat:.7f};" f"{end_lon:.7f},{end_lat:.7f}"
            )
            data = self._fetch_osrm_json(
                f"/route/v1/driving/{coord_str}",
                {
                    "overview": "full",
                    "geometries": "geojson",
                    "steps": "false",
                },
            )
            routes = data.get("routes") or []
            if routes:
                route = routes[0]
                geometry = route.get("geometry")
                coords = (
                    geometry.get("coordinates", [])
                    if isinstance(geometry, dict)
                    else []
                )
                line = []
                for coord in coords:
                    if isinstance(coord, (list, tuple)) and len(coord) >= 2:
                        line.append([float(coord[1]), float(coord[0])])
                if len(line) < 2:
                    line = [
                        [float(start_lat), float(start_lon)],
                        [float(end_lat), float(end_lon)],
                    ]
                return {
                    "line": line,
                    "duration_s": float(route.get("duration", 0.0)),
                    "distance_m": float(route.get("distance", 0.0)),
                    "source": "osrm",
                }
        except Exception:
            pass

        d_m = self._haversine_m(
            float(start_lat), float(start_lon), float(end_lat), float(end_lon)
        )
        dur_s = d_m / max(2.0, 60.0 / 3.6)
        return {
            "line": [
                [float(start_lat), float(start_lon)],
                [float(end_lat), float(end_lon)],
            ],
            "duration_s": float(dur_s),
            "distance_m": float(d_m),
            "source": "geo",
        }

    def _build_day_plan(self, entries):
        active_entries = [
            entry for entry in entries if entry["key"] not in self.excluded_area_keys
        ]
        if not active_entries:
            return None

        points_lonlat = [
            (float(entry["center"][1]), float(entry["center"][0]))
            for entry in active_entries
        ]
        durations, distances, matrix_source = self._build_drive_matrix(points_lonlat)
        order = self._optimize_visit_order(durations)

        ordered_entries = [active_entries[idx] for idx in order]
        sequence_by_key = {
            entry["key"]: idx + 1 for idx, entry in enumerate(ordered_entries)
        }

        segments = []
        total_distance_m = 0.0
        total_duration_s = 0.0
        for idx in range(len(order) - 1):
            src = ordered_entries[idx]
            dst = ordered_entries[idx + 1]
            src_pt = (float(src["center"][1]), float(src["center"][0]))
            dst_pt = (float(dst["center"][1]), float(dst["center"][0]))
            segment = self._segment_route(src_pt, dst_pt)
            total_distance_m += float(segment["distance_m"])
            total_duration_s += float(segment["duration_s"])
            segments.append(
                {
                    "from_key": src["key"],
                    "to_key": dst["key"],
                    "from_label": src["label"],
                    "to_label": dst["label"],
                    "duration_s": float(segment["duration_s"]),
                    "distance_m": float(segment["distance_m"]),
                    "line": segment["line"],
                    "source": segment["source"],
                }
            )

        return {
            "matrix_source": matrix_source,
            "sequence_by_key": sequence_by_key,
            "ordered_keys": [entry["key"] for entry in ordered_entries],
            "ordered_labels": [entry["label"] for entry in ordered_entries],
            "segments": segments,
            "total_distance_m": total_distance_m,
            "total_duration_s": total_duration_s,
            "matrix_distance_hint_m": float(self._path_cost(order, distances)),
        }

    def toggle_area_exclusion(self, area_key: str):
        if area_key in self.excluded_area_keys:
            self.excluded_area_keys.remove(area_key)
            self.logln(f"Fläche wieder aktiviert: {area_key}")
        else:
            self.excluded_area_keys.add(area_key)
            self.logln(f"Fläche ausgeschlossen: {area_key}")

    def _color_for_applicant(self, applicant: str) -> str:
        palette = [
            "#e41a1c",
            "#377eb8",
            "#4daf4a",
            "#984ea3",
            "#ff7f00",
            "#a65628",
            "#f781bf",
            "#999999",
            "#66c2a5",
            "#fc8d62",
            "#8da0cb",
            "#e78ac3",
            "#a6d854",
            "#ffd92f",
            "#e5c494",
            "#b3b3b3",
        ]
        digest = hashlib.md5(applicant.encode("utf-8", errors="ignore")).hexdigest()
        return palette[int(digest[:8], 16) % len(palette)]

    def _build_satellite_map_html(
        self,
        map_items,
        color_map,
        mapping_line_items=None,
        flight_stats=None,
        day_plan=None,
        default_center=None,
        default_zoom: int = 11,
    ):
        title = self.strings.get("map_title", "Satellitenkarte")
        map_items_json = json.dumps(map_items, ensure_ascii=False)
        color_map_json = json.dumps(color_map, ensure_ascii=False)
        line_items_json = json.dumps(mapping_line_items or [], ensure_ascii=False)
        flight_stats_json = json.dumps(flight_stats or {}, ensure_ascii=False)
        day_plan_json = json.dumps(day_plan or {}, ensure_ascii=False)
        title_json = json.dumps(title, ensure_ascii=False)
        remove_label = json.dumps(
            self.strings.get("map_remove_area", "Fläche entfernen"),
            ensure_ascii=False,
        )
        add_label = json.dumps(
            self.strings.get("map_readd_area", "Fläche wieder aufnehmen"),
            ensure_ascii=False,
        )
        opt_disabled_json = json.dumps(
            self.strings.get("map_opt_disabled", "Winkeloptimierung ist deaktiviert."),
            ensure_ascii=False,
        )
        stats_active_json = json.dumps(
            self.strings.get("map_stats_active_areas", "Flächen aktiv"),
            ensure_ascii=False,
        )
        stats_distance_json = json.dumps(
            self.strings.get("map_stats_distance", "Geschätzte Strecke"),
            ensure_ascii=False,
        )
        stats_time_json = json.dumps(
            self.strings.get("map_stats_time", "Geschätzte Flugzeit"),
            ensure_ascii=False,
        )
        stats_lines_json = json.dumps(
            self.strings.get("map_stats_lines", "Linien"),
            ensure_ascii=False,
        )
        stats_drone_json = json.dumps(
            self.strings.get("map_stats_drone", "Drohne"),
            ensure_ascii=False,
        )
        stats_altitude_json = json.dumps(
            self.strings.get("map_stats_altitude", "Höhe"),
            ensure_ascii=False,
        )
        stats_overlap_json = json.dumps(
            self.strings.get("map_stats_overlap", "Überlapp"),
            ensure_ascii=False,
        )
        stats_speed_json = json.dumps(
            self.strings.get("map_stats_speed", "Speed"),
            ensure_ascii=False,
        )
        leaflet_error_json = json.dumps(
            self.strings.get(
                "map_leaflet_error",
                "Leaflet konnte nicht geladen werden (Offline/Netzwerk).",
            ),
            ensure_ascii=False,
        )
        center = default_center or self.default_map_center
        center_json = json.dumps(center, ensure_ascii=False)
        return f"""<!doctype html>
<html lang=\"de\">
<head>
  <meta charset=\"utf-8\" />
  <meta name=\"viewport\" content=\"width=device-width,initial-scale=1\" />
  <title>{title}</title>
  <link rel=\"stylesheet\" href=\"https://unpkg.com/leaflet@1.9.4/dist/leaflet.css\" />
  <style>
    html, body, #map {{ height: 100%; margin: 0; padding: 0; }}
    #legend {{
      position: absolute;
      top: 12px;
      right: 12px;
      z-index: 1000;
      background: rgba(255, 255, 255, 0.95);
      padding: 10px 12px;
      border-radius: 6px;
      max-height: 70vh;
      overflow: auto;
      font-family: Arial, sans-serif;
      font-size: 12px;
      line-height: 1.4;
      box-shadow: 0 1px 8px rgba(0,0,0,0.2);
    }}
        #controls {{
            position: absolute;
            top: 12px;
            left: 12px;
            z-index: 1000;
            background: rgba(255, 255, 255, 0.95);
            padding: 10px 12px;
            border-radius: 6px;
            min-width: 230px;
            font-family: Arial, sans-serif;
            font-size: 12px;
            line-height: 1.4;
            box-shadow: 0 1px 8px rgba(0,0,0,0.2);
        }}
        #controls .row {{ margin-bottom: 6px; }}
        #controls .stats {{ color: #222; }}
        #controls .muted {{ color: #666; }}
    .legend-item {{ display: flex; align-items: center; margin-bottom: 4px; }}
    .swatch {{ width: 14px; height: 14px; border-radius: 2px; margin-right: 6px; border: 1px solid #444; }}
  </style>
</head>
<body>
  <div id=\"map\"></div>
    <div id="controls">
        <div class="row"><strong>{self.strings.get("map_controls_title", "Kartierungslinien")}</strong></div>
        <div class="row">
            <label>
                <input id="toggle-lines" type="checkbox" /> {self.strings.get("map_controls_toggle", "Linien anzeigen")}
            </label>
        </div>
        <div id="flight-stats" class="stats"></div>
    </div>
  <div id=\"legend\"></div>

    <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
    <script src=\"qrc:///qtwebchannel/qwebchannel.js\"></script>
    <script>
        if (typeof window.L === 'undefined') {{
            const s = document.createElement('script');
            s.src = 'https://cdn.jsdelivr.net/npm/leaflet@1.9.4/dist/leaflet.js';
            document.head.appendChild(s);
        }}
    </script>
  <script>
    const title = {title_json};
    const features = {map_items_json};
    const colors = {color_map_json};
        const lineItems = {line_items_json};
        const flightStatsSeed = {flight_stats_json};
        const dayPlan = {day_plan_json};
        const defaultCenter = {center_json};
        const defaultZoom = {int(default_zoom)};
        const removeLabel = {remove_label};
        const addLabel = {add_label};
        const optDisabledText = {opt_disabled_json};
        const statsActiveText = {stats_active_json};
        const statsDistanceText = {stats_distance_json};
        const statsTimeText = {stats_time_json};
        const statsLinesText = {stats_lines_json};
        const statsDroneText = {stats_drone_json};
        const statsAltitudeText = {stats_altitude_json};
        const statsOverlapText = {stats_overlap_json};
        const statsSpeedText = {stats_speed_json};
        const leafletErrorText = {leaflet_error_json};
        const excluded = new Set(features.filter(f => !!f.excluded).map(f => f.key));
        let bridge = null;
        const layersByKey = new Map();
        const featureByKey = new Map();
        const lineItemsByKey = new Map();
        for (const item of lineItems) {{
            lineItemsByKey.set(item.key, item);
        }}
        const daySequenceByKey = dayPlan.sequence_by_key || {{}};
        const daySegments = Array.isArray(dayPlan.segments) ? dayPlan.segments : [];

        if (window.qt && typeof QWebChannel !== 'undefined') {{
            new QWebChannel(qt.webChannelTransport, function(channel) {{
                bridge = channel.objects.bridge || null;
            }});
        }}

        function escapeHtml(text) {{
            return String(text)
                .replaceAll('&', '&amp;')
                .replaceAll('<', '&lt;')
                .replaceAll('>', '&gt;')
                .replaceAll('"', '&quot;')
                .replaceAll("'", '&#039;');
        }}

        function renderLeafletMap() {{
            if (typeof window.L === 'undefined') {{
                const mapNode = document.getElementById('map');
                if (mapNode) {{
                    mapNode.style.display = 'flex';
                    mapNode.style.alignItems = 'center';
                    mapNode.style.justifyContent = 'center';
                    mapNode.style.fontFamily = 'Arial, sans-serif';
                    mapNode.style.fontSize = '13px';
                    mapNode.textContent = leafletErrorText;
                }}
                return;
            }}

            const toggleLines = document.getElementById('toggle-lines');
            const statsNode = document.getElementById('flight-stats');
            const optimizationActive = !!flightStatsSeed.optimization_active;
            const hasLines = lineItems.length > 0;
            const defaultShowLines = optimizationActive && hasLines;
            let showLines = defaultShowLines;

            if (toggleLines) {{
                toggleLines.checked = defaultShowLines;
                toggleLines.disabled = !hasLines;
            }}

            function formatStats() {{
                if (!optimizationActive) {{
                    if (statsNode) statsNode.innerHTML = '<span class="muted">' + escapeHtml(optDisabledText) + '</span>';
                    return;
                }}

                let totalDistance = 0;
                let totalTime = 0;
                let totalLines = 0;
                let areas = 0;
                for (const item of lineItems) {{
                    if (excluded.has(item.key)) continue;
                    totalDistance += Number(item.distance_m || 0);
                    totalTime += Number(item.time_s || 0);
                    totalLines += Number(item.line_count || 0);
                    areas += 1;
                }}

                const minutes = totalTime / 60.0;
                const speed = Number(flightStatsSeed.speed_mps || 0);
                const overlap = Number(flightStatsSeed.overlap_percent || 0);
                const altitude = Number(flightStatsSeed.altitude_m || 0);
                const drone = String(flightStatsSeed.drone || '');

                if (statsNode) {{
                    statsNode.innerHTML =
                        '<div>' + escapeHtml(statsActiveText) + ': <b>' + areas + '</b></div>' +
                        '<div>' + escapeHtml(statsDistanceText) + ': <b>' + totalDistance.toFixed(1) + ' m</b></div>' +
                        '<div>' + escapeHtml(statsTimeText) + ': <b>' + minutes.toFixed(1) + ' min</b></div>' +
                        '<div>' + escapeHtml(statsLinesText) + ': <b>' + Math.round(totalLines) + '</b></div>' +
                        '<div class="muted">' +
                            escapeHtml(statsDroneText) + ' ' + escapeHtml(drone) +
                            ' · ' + escapeHtml(statsAltitudeText) + ' ' + altitude.toFixed(1) + ' m' +
                            ' · ' + escapeHtml(statsOverlapText) + ' ' + overlap.toFixed(0) + '%' +
                            ' · ' + escapeHtml(statsSpeedText) + ' ' + speed.toFixed(1) + ' m/s' +
                        '</div>';
                }}
            }}

            function setLayerStyle(layer, key, baseColor) {{
                if (excluded.has(key)) {{
                    layer.setStyle({{
                        color: '#888888',
                        fillColor: '#9e9e9e',
                        fillOpacity: 0.2,
                        weight: 2,
                        dashArray: '6,4'
                    }});
                }} else {{
                    layer.setStyle({{
                        color: baseColor,
                        fillColor: baseColor,
                        fillOpacity: 0.35,
                        weight: 2,
                        dashArray: null
                    }});
                }}
            }}

            function lineColorForKey(key) {{
                const feature = featureByKey.get(key);
                if (!feature) return '#ffffff';
                return colors[feature.applicant] || '#ffffff';
            }}

            const lineLayerGroup = L.layerGroup();
            const driveLayerGroup = L.layerGroup();
            const driveTextLayerGroup = L.layerGroup();

            function renderLineOverlay() {{
                lineLayerGroup.clearLayers();
                if (!showLines) {{
                    return;
                }}
                for (const item of lineItems) {{
                    if (excluded.has(item.key)) {{
                        continue;
                    }}
                    const col = lineColorForKey(item.key);
                    const lines = Array.isArray(item.lines) ? item.lines : [];
                    for (const line of lines) {{
                        if (!Array.isArray(line) || line.length < 2) continue;
                        L.polyline(line, {{
                            color: col,
                            weight: 2,
                            opacity: 0.9,
                            dashArray: '8,6'
                        }}).addTo(lineLayerGroup);
                    }}
                }}
            }}

            function popupHtml(feature) {{
                const isExcluded = excluded.has(feature.key);
                const actionLabel = isExcluded ? addLabel : removeLabel;
                const actionColor = isExcluded ? '#2e7d32' : '#b71c1c';
                return `
                    <b>${{escapeHtml(feature.label)}}</b><br>
                    ${{escapeHtml(feature.applicant)}}<br><br>
                    <button
                        type="button"
                        class="toggle-area-btn"
                        data-key="${{encodeURIComponent(feature.key)}}"
                        style="padding:6px 10px;border:1px solid #555;border-radius:4px;cursor:pointer;color:white;background:${{actionColor}};"
                    >
                        ${{escapeHtml(actionLabel)}}
                    </button>
                `;
            }}

            function formatMinutes(seconds) {{
                const minutes = Math.max(0, Number(seconds || 0)) / 60.0;
                return minutes.toFixed(1) + ' min';
            }}

            function midPoint(line) {{
                if (!Array.isArray(line) || line.length === 0) return null;
                return line[Math.floor(line.length / 2)] || null;
            }}

            function renderDayRoutes() {{
                driveLayerGroup.clearLayers();
                driveTextLayerGroup.clearLayers();
                if (!Array.isArray(daySegments) || daySegments.length === 0) return;
                for (const seg of daySegments) {{
                    if (excluded.has(seg.from_key) || excluded.has(seg.to_key)) continue;
                    const line = Array.isArray(seg.line) ? seg.line : [];
                    if (line.length < 2) continue;
                    L.polyline(line, {{
                        color: '#1565c0',
                        weight: 4,
                        opacity: 0.8,
                    }}).addTo(driveLayerGroup);

                    const mid = midPoint(line);
                    if (mid) {{
                        L.marker(mid, {{
                            interactive: false,
                            icon: L.divIcon({{
                                className: 'drive-time-label',
                                html: '<div style="background:rgba(21,101,192,0.92);color:#fff;padding:2px 6px;border-radius:10px;font:600 11px Arial;white-space:nowrap;">' + escapeHtml(formatMinutes(seg.duration_s)) + '</div>',
                            }}),
                        }}).addTo(driveTextLayerGroup);
                    }}
                }}
            }}

            window.toggleArea = function(encodedKey) {{
                const key = decodeURIComponent(encodedKey);
                const feature = featureByKey.get(key);
                const layer = layersByKey.get(key);
                if (!feature || !layer) {{
                    return;
                }}
                if (excluded.has(key)) {{
                    excluded.delete(key);
                }} else {{
                    excluded.add(key);
                }}
                setLayerStyle(layer, key, colors[feature.applicant] || '#ff0000');
                layer.setPopupContent(popupHtml(feature));
                renderLineOverlay();
                renderDayRoutes();
                formatStats();
                if (bridge && typeof bridge.toggleArea === 'function') {{
                    bridge.toggleArea(key);
                }}
            }};

            const map = L.map('map', {{ zoomControl: true }});
            L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{{z}}/{{y}}/{{x}}', {{
                attribution: 'Tiles © Esri'
            }}).addTo(map);
            lineLayerGroup.addTo(map);
            driveLayerGroup.addTo(map);
            driveTextLayerGroup.addTo(map);

            const group = L.featureGroup().addTo(map);
            for (const feature of features) {{
                const color = colors[feature.applicant] || '#ff0000';
                const poly = L.polygon(feature.rings, {{
                    color: color,
                    weight: 2,
                    fillColor: color,
                    fillOpacity: 0.35
                }});
                featureByKey.set(feature.key, feature);
                layersByKey.set(feature.key, poly);
                setLayerStyle(poly, feature.key, color);
                poly.bindPopup(popupHtml(feature));

                const seq = daySequenceByKey[feature.key];
                if (seq && Array.isArray(feature.center) && feature.center.length === 2) {{
                    L.marker(feature.center, {{
                        interactive: false,
                        icon: L.divIcon({{
                            className: 'day-seq-label',
                            html: '<div style="background:#111;color:#fff;border:2px solid #fff;width:24px;height:24px;line-height:20px;border-radius:12px;text-align:center;font:700 12px Arial;">' + String(seq) + '</div>'
                        }})
                    }}).addTo(group);
                }}

                poly.on('popupopen', function(e) {{
                    const root = e.popup && e.popup.getElement ? e.popup.getElement() : null;
                    if (!root) {{
                        return;
                    }}
                    const btn = root.querySelector('.toggle-area-btn');
                    if (!btn) {{
                        return;
                    }}
                    btn.onclick = function() {{
                        window.toggleArea(btn.dataset.key || '');
                    }};
                }});
                poly.addTo(group);
            }}

            if (group.getLayers().length > 0) {{
                map.fitBounds(group.getBounds().pad(0.08));
            }} else {{
            map.setView(defaultCenter, defaultZoom);
            }}

            const legend = document.getElementById('legend');
            legend.innerHTML = '';
            for (const [applicant, color] of Object.entries(colors).sort((a, b) => a[0].localeCompare(b[0], 'de'))) {{
                const row = document.createElement('div');
                row.className = 'legend-item';
                row.innerHTML = '<span class="swatch" style="background:' + color + '"></span>' + escapeHtml(applicant);
                legend.appendChild(row);
            }}

            if (toggleLines) {{
                toggleLines.onchange = function() {{
                    showLines = !!toggleLines.checked;
                    renderLineOverlay();
                }};
            }}

            renderLineOverlay();
            renderDayRoutes();
            formatStats();

            setTimeout(() => map.invalidateSize(true), 120);
            setTimeout(() => map.invalidateSize(true), 320);
            window.addEventListener('resize', () => map.invalidateSize(true));
        }}

        setTimeout(renderLeafletMap, 50);
  </script>
</body>
</html>
"""

    def _map_output_dir(self) -> Path:
        out_dir = Path(self.out_edit.text().strip() or (Path.cwd() / "out"))
        out_dir.mkdir(parents=True, exist_ok=True)
        return out_dir

    def _save_map_html(self, html: str) -> Path:
        html_path = self._map_output_dir() / "satellitenkarte.html"
        html_path.write_text(html, encoding="utf-8")
        return html_path

    def _render_map_from_payload(
        self,
        payload: dict,
        force_reload: bool = False,
        log_open: bool = False,
    ) -> Path:
        html = self._build_satellite_map_html(
            payload.get("map_items", []),
            payload.get("color_map", {}),
            mapping_line_items=payload.get("mapping_line_items", []),
            flight_stats=payload.get("flight_stats", {}),
            day_plan=payload.get("day_plan", {}),
            default_center=payload.get("default_center", self.default_map_center),
            default_zoom=int(payload.get("default_zoom", self.default_map_zoom)),
        )
        html_path = self._save_map_html(html)
        self._open_map_preview(
            html_path,
            fallback_to_browser=False,
            log_open=log_open,
            force_reload=force_reload,
        )
        return html_path

    def _refresh_map_language_texts(self):
        if self.map_view is None:
            return
        payload = self.last_map_payload or {
            "map_items": [],
            "color_map": {},
            "mapping_line_items": [],
            "flight_stats": {},
            "day_plan": {},
            "default_center": self.default_map_center,
            "default_zoom": self.default_map_zoom,
        }
        self.last_map_payload = payload
        self._render_map_from_payload(payload, force_reload=True, log_open=False)

    def _write_default_map(self):
        self.last_map_payload = {
            "map_items": [],
            "color_map": {},
            "mapping_line_items": [],
            "flight_stats": {},
            "day_plan": {},
            "default_center": self.default_map_center,
            "default_zoom": self.default_map_zoom,
        }
        self._render_map_from_payload(
            self.last_map_payload,
            force_reload=False,
            log_open=False,
        )

    def _update_map_panel_visibility(self):
        if self.map_view is None:
            return
        self.map_panel.setVisible(True)

        is_large = self.isMaximized() or (self.width() >= 1450 and self.height() >= 880)
        if is_large:
            self.main_splitter.setSizes([500, 1000])
        else:
            self.main_splitter.setSizes([540, 900])

        html_path = self._map_output_dir() / "satellitenkarte.html"
        if not html_path.exists():
            self._write_default_map()
            return
        if self.current_map_html_path is None:
            self._open_map_preview(
                html_path,
                fallback_to_browser=False,
                log_open=False,
            )

    def _open_map_preview(
        self,
        html_path: Path,
        fallback_to_browser: bool = True,
        log_open: bool = True,
        force_reload: bool = False,
    ):
        resolved_path = str(html_path.resolve())
        if self.map_view is not None:
            if (not force_reload) and self.current_map_html_path == resolved_path:
                return
            self.current_map_html_path = resolved_path
            self.map_view.setUrl(QtCore.QUrl.fromLocalFile(resolved_path))
            if log_open:
                self.logln(
                    f"{self.strings.get('map_opened', 'Satellitenkarte geöffnet')}: GUI"
                )
            return

        if fallback_to_browser:
            webbrowser.open(html_path.resolve().as_uri())
            self.logln(
                "QtWebEngine nicht verfügbar – Karte im Standardbrowser geöffnet."
            )

    def show_satellite_map(self):
        kmz_path = self._validate_input_path()
        if kmz_path is None:
            return

        ok, import_err = _ensure_engine_modules()
        if not ok:
            err_text = (
                f"{type(import_err).__name__}: {import_err}"
                if import_err
                else "Unbekannter Importfehler"
            )
            self.logln(f"Engine-Importfehler: {err_text}")
            QtWidgets.QMessageBox.critical(
                self,
                self.strings["import_error"],
                "LittleOne-Engine konnte nicht geladen werden.\n\n"
                f"Details: {err_text}\n\n"
                "Bitte venv/Startpfad prüfen.",
            )
            return

        kmz = kmz_reader
        if kmz is None:
            QtWidgets.QMessageBox.critical(
                self,
                self.strings["import_error"],
                "LittleOne-Engine ist nicht verfügbar.",
            )
            return

        try:
            self.progress.setVisible(True)
            self.progress.setMaximum(0)
            self.progress.setValue(0)
            self.map_btn.setEnabled(False)
            self.day_plan_btn.setEnabled(False)
            self.status.showMessage(self.strings.get("map_loading", "Lade Karte..."))
            self.logln(self.strings.get("map_loading", "Lade Karte..."))
            QtCore.QCoreApplication.processEvents()

            features = kmz.parse_kmz_to_area_features(str(kmz_path))
            summaries = kmz.summarize_features(features)
            entries = self._collect_geometry_entries(features, summaries)
            current_keys = {entry["key"] for entry in entries}
            self.excluded_area_keys.intersection_update(current_keys)

            map_items = [
                {
                    "applicant": entry["applicant"],
                    "label": entry["label"],
                    "rings": entry["rings"],
                    "key": entry["key"],
                    "excluded": entry["key"] in self.excluded_area_keys,
                    "center": entry.get("center"),
                }
                for entry in entries
            ]

            if not map_items:
                self.logln(
                    self.strings.get("map_no_polygons", "Keine Polygone gefunden.")
                )
                QtWidgets.QMessageBox.information(
                    self,
                    self.strings.get("map_title", "Satellitenkarte"),
                    self.strings.get("map_no_polygons", "Keine Polygone gefunden."),
                )
                self.status.showMessage(
                    self.strings.get("map_no_polygons", "Keine Polygone gefunden.")
                )
                return

            applicants = sorted({item["applicant"] for item in map_items})
            color_map = {
                applicant: self._color_for_applicant(applicant)
                for applicant in applicants
            }

            mapping_line_items = []
            flight_stats = {
                "optimization_active": False,
                "drone": self.drone_combo.currentText(),
                "altitude_m": 0.0,
                "overlap_percent": float(self.overlap_spin.value()),
                "speed_mps": 0.0,
            }

            metric_values = self._get_metric_values()
            flight_stats["altitude_m"] = float(metric_values["altitude"])
            flight_stats["speed_mps"] = float(metric_values["speed"])

            def _num(value, default=0.0):
                try:
                    return float(value)
                except Exception:
                    return float(default)

            optimizer = optimize_angle_mod
            optimize_active = self.optimize_direction_check.isChecked()
            if (
                optimize_active
                and optimizer is not None
                and hasattr(optimizer, "mapping_preview")
            ):
                flight_stats["optimization_active"] = True
                for entry in entries:
                    if entry["key"] in self.excluded_area_keys:
                        continue
                    preview = optimizer.mapping_preview(
                        entry["geom"],
                        altitude_m=float(metric_values["altitude"]),
                        side_overlap_percent=float(self.overlap_spin.value()),
                        speed_mps=float(metric_values["speed"]),
                        drone=self.drone_combo.currentText(),
                    )
                    mapping_line_items.append(
                        {
                            "key": entry["key"],
                            "direction_deg": _num(preview.get("direction_deg", 0.0)),
                            "distance_m": _num(preview.get("distance_m", 0.0)),
                            "time_s": _num(preview.get("time_s", 0.0)),
                            "line_count": _num(preview.get("line_count", 0.0)),
                            "lines": preview.get("lines_latlon", []),
                        }
                    )

                total_distance_m = sum(
                    float(item["distance_m"]) for item in mapping_line_items
                )
                total_time_min = (
                    sum(float(item["time_s"]) for item in mapping_line_items) / 60.0
                )
                self.logln(
                    "ℹ Kartenvorschau (optimiert): "
                    f"{total_distance_m:.1f} m, {total_time_min:.1f} min"
                )
            elif optimize_active and optimizer is not None:
                self.logln(
                    "ℹ Optimierung aktiv, aber Linien-Preview wird von diesem Optimizer noch nicht unterstützt."
                )

            self.last_map_payload = {
                "map_items": map_items,
                "color_map": color_map,
                "mapping_line_items": mapping_line_items,
                "flight_stats": flight_stats,
                "day_plan": {},
                "default_center": self.default_map_center,
                "default_zoom": self.default_map_zoom,
            }
            html_path = self._render_map_from_payload(
                self.last_map_payload,
                force_reload=True,
                log_open=True,
            )
            self.logln(
                f"{self.strings.get('map_saved', 'Karte gespeichert')}: {html_path}"
            )
            self.status.showMessage(
                self.strings.get("map_opened", "Satellitenkarte geöffnet")
            )
        except Exception as ex:
            tb = traceback.format_exc()
            self.logln("─" * 60)
            self.logln("❌ Kartenfehler:")
            self.logln(tb)
            self.status.showMessage(self.strings["error"])
            QtWidgets.QMessageBox.critical(self, self.strings["error"], str(ex))
        finally:
            self.progress.setVisible(False)
            self.progress.setMaximum(100)
            self.progress.setValue(0)
            self.map_btn.setEnabled(True)
            self.day_plan_btn.setEnabled(True)

    def _show_day_plan_window(self, entries, day_plan):
        dialog = QtWidgets.QDialog(self)
        dialog.setWindowTitle(self.strings.get("day_plan", "Tagesplan"))
        dialog.resize(700, 540)

        layout = QtWidgets.QVBoxLayout(dialog)
        header = QtWidgets.QLabel(
            f"<b>{self.strings.get('day_plan', 'Tagesplan')}</b><br>"
            f"Flächen: {len(day_plan.get('ordered_keys', []))}"
            f" · Strecke: {day_plan.get('total_distance_m', 0.0) / 1000.0:.2f} km"
            f" · Fahrzeit: {day_plan.get('total_duration_s', 0.0) / 60.0:.1f} min"
        )
        header.setWordWrap(True)
        layout.addWidget(header)

        detail_box = QtWidgets.QPlainTextEdit()
        detail_box.setReadOnly(True)

        by_key = {entry["key"]: entry for entry in entries}
        lines = []
        for idx, key in enumerate(day_plan.get("ordered_keys", []), start=1):
            entry = by_key.get(key)
            if entry is None:
                continue
            lines.append(f"{idx}. {entry['label']} ({entry['applicant']})")

        lines.append("")
        lines.append("Fahrtsegmente:")
        for idx, seg in enumerate(day_plan.get("segments", []), start=1):
            lines.append(
                f"{idx}. {seg.get('from_label')} -> {seg.get('to_label')}"
                f" | {float(seg.get('distance_m', 0.0)) / 1000.0:.2f} km"
                f" | {float(seg.get('duration_s', 0.0)) / 60.0:.1f} min"
            )

        source = str(day_plan.get("matrix_source", "geo")).upper()
        lines.append("")
        lines.append(f"Routing-Quelle: {source}")
        if source != "OSRM":
            lines.append(
                "Hinweis: Fallback mit Luftlinie + Durchschnittsgeschwindigkeit aktiv."
            )

        detail_box.setPlainText("\n".join(lines))
        layout.addWidget(detail_box, 1)

        close_btn = QtWidgets.QPushButton(self.strings.get("ok", "OK"))
        close_btn.clicked.connect(dialog.accept)
        row = QtWidgets.QHBoxLayout()
        row.addStretch(1)
        row.addWidget(close_btn)
        layout.addLayout(row)

        dialog.exec()

    def generate_day_plan(self):
        kmz_path = self._validate_input_path()
        if kmz_path is None:
            return

        ok, import_err = _ensure_engine_modules()
        if not ok:
            err_text = (
                f"{type(import_err).__name__}: {import_err}"
                if import_err
                else "Unbekannter Importfehler"
            )
            self.logln(f"Engine-Importfehler: {err_text}")
            QtWidgets.QMessageBox.critical(
                self,
                self.strings["import_error"],
                "LittleOne-Engine konnte nicht geladen werden.\n\n"
                f"Details: {err_text}\n\n"
                "Bitte venv/Startpfad prüfen.",
            )
            return

        kmz = kmz_reader
        if kmz is None:
            QtWidgets.QMessageBox.critical(
                self,
                self.strings["import_error"],
                "LittleOne-Engine ist nicht verfügbar.",
            )
            return

        try:
            self.progress.setVisible(True)
            self.progress.setMaximum(0)
            self.progress.setValue(0)
            self.day_plan_btn.setEnabled(False)
            self.map_btn.setEnabled(False)
            self.convert_btn.setEnabled(False)
            self.status.showMessage("Berechne Tagesplan ...")
            self.logln("Berechne Tagesplan ...")
            QtCore.QCoreApplication.processEvents()

            features = kmz.parse_kmz_to_area_features(str(kmz_path))
            summaries = kmz.summarize_features(features)
            entries = self._collect_geometry_entries(features, summaries)
            current_keys = {entry["key"] for entry in entries}
            self.excluded_area_keys.intersection_update(current_keys)

            day_plan = self._build_day_plan(entries)
            if not day_plan or not day_plan.get("ordered_keys"):
                QtWidgets.QMessageBox.information(
                    self,
                    self.strings.get("day_plan", "Tagesplan"),
                    "Keine aktiven Flächen für Tagesplan vorhanden.",
                )
                return

            sequence_by_key = day_plan.get("sequence_by_key", {})
            applicants = sorted({entry["applicant"] for entry in entries})
            color_map = {
                applicant: self._color_for_applicant(applicant)
                for applicant in applicants
            }
            map_items = [
                {
                    "applicant": entry["applicant"],
                    "label": (
                        f"{sequence_by_key[entry['key']]}. {entry['label']}"
                        if entry["key"] in sequence_by_key
                        else entry["label"]
                    ),
                    "rings": entry["rings"],
                    "key": entry["key"],
                    "excluded": entry["key"] in self.excluded_area_keys,
                    "center": entry.get("center"),
                }
                for entry in entries
            ]

            self.last_map_payload = {
                "map_items": map_items,
                "color_map": color_map,
                "mapping_line_items": [],
                "flight_stats": {"optimization_active": False},
                "day_plan": day_plan,
                "default_center": self.default_map_center,
                "default_zoom": self.default_map_zoom,
            }
            self._render_map_from_payload(
                self.last_map_payload,
                force_reload=True,
                log_open=True,
            )

            self.logln(
                "✓ Tagesplan: "
                f"{len(day_plan.get('ordered_keys', []))} Flächen, "
                f"{day_plan.get('total_distance_m', 0.0) / 1000.0:.2f} km, "
                f"{day_plan.get('total_duration_s', 0.0) / 60.0:.1f} min"
            )
            self.status.showMessage("Tagesplan erstellt")
            self._show_day_plan_window(entries, day_plan)
        except Exception as ex:
            tb = traceback.format_exc()
            self.logln("─" * 60)
            self.logln("❌ Tagesplan-Fehler:")
            self.logln(tb)
            self.status.showMessage(self.strings["error"])
            QtWidgets.QMessageBox.critical(self, self.strings["error"], str(ex))
        finally:
            self.progress.setVisible(False)
            self.progress.setMaximum(100)
            self.progress.setValue(0)
            self.day_plan_btn.setEnabled(True)
            self.map_btn.setEnabled(True)
            self.convert_btn.setEnabled(True)

    def convert(self):
        try:
            kmz_path = self._validate_input_path()
            if kmz_path is None:
                return

            out_dir = Path(self.out_edit.text())
            basename = "area"  # default fallback for polygon names

            ok, import_err = _ensure_engine_modules()
            if not ok:
                err_text = (
                    f"{type(import_err).__name__}: {import_err}"
                    if import_err
                    else "Unbekannter Importfehler"
                )
                self.logln(f"Engine-Importfehler: {err_text}")
                QtWidgets.QMessageBox.critical(
                    self,
                    self.strings["import_error"],
                    "LittleOne-Engine konnte nicht geladen werden.\n\n"
                    f"Details: {err_text}\n\n"
                    "Bitte venv/Startpfad prüfen.",
                )
                return

            kmz = kmz_reader
            writer = kml_writer
            rules = dji_rules
            optimizer = optimize_angle_mod
            if kmz is None or writer is None or rules is None:
                QtWidgets.QMessageBox.critical(
                    self,
                    self.strings["import_error"],
                    "LittleOne-Engine ist nicht verfügbar.",
                )
                return

            # Options sammeln (intern immer metrisch)
            metric_values = self._get_metric_values()
            options = {
                "flughöhe_m": float(metric_values["altitude"]),
                "seitlicher_überlapp_prozent": self.overlap_spin.value(),
                "sichere_starthöhe_m": float(metric_values["safe_height"]),
                "drohne": self.drone_combo.currentText(),
                "aktion_beenden": self.action_combo.currentText(),
                "geschwindigkeit_ms": float(metric_values["speed"]),
                "rand": self.margin_spin.value(),
                "winkel_optimierung_aktiv": self.optimize_direction_check.isChecked(),
                "elevation_optimize_enable": self.elevation_optimize_check.isChecked(),
            }

            # UI für Konvertierung vorbereiten
            self.progress.setVisible(True)
            self.progress.setValue(0)
            self.progress.setMaximum(0)  # Indeterminate mode
            self.convert_btn.setEnabled(False)
            self.map_btn.setEnabled(False)
            self.day_plan_btn.setEnabled(False)

            self.status.showMessage(self.strings["converting"])
            self.logln(f"Starte Konvertierung: {kmz_path}")
            self.logln("─" * 60)
            self.logln("Einstellungen:")
            for k, v in options.items():
                self.logln(f"  • {k}: {v}")
            self.logln("─" * 60)

            # Process events to show progress bar
            QtCore.QCoreApplication.processEvents()

            # Parse & extract
            self.logln("Parsing KMZ...")
            features = kmz.parse_kmz_to_area_features(str(kmz_path))
            self.logln(f"✓ {len(features)} Features geladen")
            QtCore.QCoreApplication.processEvents()

            summaries = kmz.summarize_features(features)

            entries = self._collect_geometry_entries(features, summaries)
            current_keys = {entry["key"] for entry in entries}
            self.excluded_area_keys.intersection_update(current_keys)

            polys = []
            names = []
            directions = []
            est_total_distance_m = 0.0
            est_total_time_s = 0.0

            def _clean(v: str) -> str:
                txt = (v or "").strip()
                replacements = {
                    "ä": "ae",
                    "ö": "oe",
                    "ü": "ue",
                    "Ä": "Ae",
                    "Ö": "Oe",
                    "Ü": "Ue",
                    "ß": "ss",
                }
                for src, dst in replacements.items():
                    txt = txt.replace(src, dst)
                txt = re.sub(r"\s+", "", txt)
                txt = re.sub(r"[^A-Za-z0-9.-]+", "-", txt)
                txt = txt.replace("_", "-")
                txt = re.sub(r"-+", "-", txt)
                return txt.strip("-.")

            def _fmt_short_date(d):
                if not d:
                    return "ohneDatum"
                mon = {
                    1: "Jan",
                    2: "Feb",
                    3: "Mar",
                    4: "Apr",
                    5: "Mai",
                    6: "Jun",
                    7: "Jul",
                    8: "Aug",
                    9: "Sep",
                    10: "Okt",
                    11: "Nov",
                    12: "Dez",
                }
                return f"{d.day:02d}{mon.get(d.month, 'Mon')}"

            self.logln("Extrahiere Polygone...")
            skipped = 0
            for entry in entries:
                if entry["key"] in self.excluded_area_keys:
                    skipped += 1
                    continue
                feat = entry["feature"]
                summary = entry["summary"]
                geom = entry["geom"]

                nachname = _clean(summary.antragsteller_name or "unbekannt")
                datum = _fmt_short_date(summary.datum_mahd)
                schlag = _clean(
                    entry["label"] or summary.schlag_flurstueck or feat.name or basename
                )

                base_file_name = f"{nachname}-{datum}-{schlag}"

                polys.append(geom)
                names.append(base_file_name)
                if self.optimize_direction_check.isChecked() and optimizer is not None:
                    if hasattr(optimizer, "best_mapping_direction_deg"):
                        result = optimizer.best_mapping_direction_deg(
                            geom,
                            altitude_m=float(metric_values["altitude"]),
                            side_overlap_percent=float(self.overlap_spin.value()),
                            speed_mps=float(metric_values["speed"]),
                            drone=self.drone_combo.currentText(),
                        )
                        direction_deg = (
                            int(round(float(result.get("direction_deg", 0.0)))) % 180
                        )
                        directions.append(direction_deg)
                        est_total_distance_m += float(result.get("distance_m", 0.0))
                        est_total_time_s += float(result.get("time_s", 0.0))
                    else:
                        directions.append(
                            int(round(float(optimizer.mrr_angle_deg(geom)))) % 180
                        )
                else:
                    directions.append(0)

            if skipped > 0:
                self.logln(
                    f"ℹ {skipped} Fläche(n) ausgeschlossen und nicht konvertiert"
                )

            if not polys:
                self.logln("❌ Keine Polygone gefunden.")
                self.status.showMessage("Keine Polygone.")
                self.progress.setVisible(False)
                self.convert_btn.setEnabled(True)
                self.day_plan_btn.setEnabled(True)
                return

            self.logln(f"✓ {len(polys)} Polygone extrahiert")
            if self.optimize_direction_check.isChecked() and est_total_distance_m > 0:
                est_total_time_min = est_total_time_s / 60.0
                self.logln(
                    "ℹ Schätzung optimierter Flugweg: "
                    f"{est_total_distance_m:.1f} m, {est_total_time_min:.1f} min"
                )
            QtCore.QCoreApplication.processEvents()

            # Normalize
            self.logln("Normalisiere Geometrien...")
            norm = [rules.normalize_polygon(p, add_z_if_missing=True) for p in polys]
            self.logln("✓ Geometrien normalisiert")
            QtCore.QCoreApplication.processEvents()

            out_dir.mkdir(parents=True, exist_ok=True)
            debug_kml_dir = out_dir / "debug_kml"

            # Generate KMZs
            self.logln(f"Schreibe {len(norm)} KMZ-Dateien...")
            written = writer.write_polygons_to_kmzs(
                norm,
                str(out_dir),
                basename,
                options=options,
                names=names,
                directions=directions,
                debug_kml_dir=str(debug_kml_dir),
            )

            self.progress.setMaximum(100)
            self.progress.setValue(100)

            self.logln("─" * 60)
            self.logln(f"✓ {written} KMZ-Dateien generiert")
            self.logln(f"Ausgabeordner: {out_dir}")
            self.logln(f"Debug-KMLs: {debug_kml_dir}")
            self.status.showMessage(self.strings["done"])

            QtWidgets.QMessageBox.information(
                self,
                self.strings["success"],
                f"✓ Erfolgreich: {written} KMZ-Dateien\n\n"
                f"Ausgabe:\n{out_dir}\n\n"
                f"Debug-KMLs:\n{debug_kml_dir}",
            )
        except Exception as ex:
            tb = traceback.format_exc()
            self.logln("─" * 60)
            self.logln(f"❌ FEHLER:")
            self.logln(tb)
            self.status.showMessage(self.strings["error"])
            QtWidgets.QMessageBox.critical(self, self.strings["error"], str(ex))
        finally:
            self.progress.setVisible(False)
            self.convert_btn.setEnabled(True)
            self.map_btn.setEnabled(True)
            self.day_plan_btn.setEnabled(True)

    def _detect_system_theme(self) -> str:
        """Detect system theme (Light or Dark)"""
        try:
            if sys.platform == "win32":
                import winreg

                try:
                    registry_path = (
                        r"Software\Microsoft\Windows\CurrentVersion\Themes\Personalize"
                    )
                    registry_key = winreg.OpenKey(
                        winreg.HKEY_CURRENT_USER, registry_path
                    )
                    value, _ = winreg.QueryValueEx(registry_key, "AppsUseLightTheme")
                    return "Light" if value == 1 else "Dark"
                except:
                    return "Light"  # Default fallback
            else:
                return "Light"  # Mac/Linux default
        except:
            return "Light"

    def reset_to_defaults(self):
        """Reset all controls to default values"""
        # Parameters (Defaultwerte sind intern metrisch)
        self._set_display_values_from_metric(BASE_DEFAULTS)

        self.overlap_slider.blockSignals(True)
        self.overlap_spin.blockSignals(True)
        self.overlap_slider.setValue(30)
        self.overlap_spin.setValue(30)
        self.overlap_slider.blockSignals(False)
        self.overlap_spin.blockSignals(False)

        self.margin_slider.blockSignals(True)
        self.margin_spin.blockSignals(True)
        self.margin_slider.setValue(0)
        self.margin_spin.setValue(0)
        self.margin_slider.blockSignals(False)
        self.margin_spin.blockSignals(False)

        # Comboboxes
        self.drone_combo.setCurrentText("M4T")
        self.action_combo.setCurrentText("Rückkehrfunktion")

        # Checkboxes
        self.optimize_direction_check.setChecked(True)
        self.elevation_optimize_check.setChecked(False)

        # File paths
        self.kmz_edit.clear()
        self.out_edit.setText(str(Path.cwd() / "out"))
        self.excluded_area_keys.clear()

        # Output
        self.output_label.clear()

        # Status
        self.status.showMessage("")

        self.logln(self.strings.get("reset", "Parameter zurückgesetzt"))


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    w = MainWindow()
    w.show()
    sys.exit(app.exec())
