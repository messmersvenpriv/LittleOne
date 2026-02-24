from PySide6 import QtWidgets, QtGui, QtCore

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
import subprocess
import webbrowser

ENGINE_IMPORT_ERROR = None
optimize_angle_mod = None
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
        "title": "Kitzrettung – DJI Drohnen-Missionsplaner",
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
        "settings_title": "Einstellungen",
        "theme": "Design",
        "language": "Sprache",
        "units": "Einheiten",
        "ok": "OK",
        "cancel": "Abbrechen",
    },
    "English": {
        "title": "Kitzrettung – DJI Drone Mission Planner",
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
        "settings_title": "Settings",
        "theme": "Theme",
        "language": "Language",
        "units": "Units",
        "ok": "OK",
        "cancel": "Cancel",
    },
    "Français": {
        "title": "Kitzrettung – Planificateur de Missions DJI",
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
        "settings_title": "Paramètres",
        "theme": "Thème",
        "language": "Langue",
        "units": "Unités",
        "ok": "OK",
        "cancel": "Annuler",
    },
    "Suomi": {
        "title": "Kitzrettung – DJI Drone Mission Planner",
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
        "drone": "Droni",
        "action": "Lopetustoiminto",
        "speed": "Nopeus",
        "speed_unit": "m/s",
        "margin": "Marginaali",
        "optimize_group": "Optimoinnit",
        "optimize_dir": "Kulman optimointi",
        "optimize_elev": "Korkeuden optimointi",
        "convert": "Muunna",
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


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.default_map_center = [48.77, 8.23]  # Landkreis Rastatt
        self.default_map_zoom = 11
        self.theme = self._detect_system_theme()
        self.language = "Deutsch"
        self.units = "Metric"
        self.strings = LANGUAGES[self.language]

        self.setWindowTitle(self.strings["title"])
        self.resize(1200, 800)

        ico_path = Path(__file__).parent.parent / "assets" / "app.ico"
        if ico_path.exists():
            self.setWindowIcon(QtGui.QIcon(str(ico_path)))

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
        input_layout = QtWidgets.QVBoxLayout(input_panel)

        # Formular
        form = QtWidgets.QFormLayout()
        form.setSpacing(8)
        form.setContentsMargins(10, 10, 10, 10)
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
        self.optimize_direction_check.setChecked(False)
        opt_layout.addWidget(self.optimize_direction_check)

        self.elevation_optimize_check = QtWidgets.QCheckBox(
            self.strings["optimize_elev"]
        )
        self.elevation_optimize_check.setChecked(True)
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
        self.reset_btn.setMinimumWidth(160)

        button_layout.addWidget(self.convert_btn, stretch=2)
        button_layout.addWidget(self.map_btn, stretch=1)
        button_layout.addWidget(self.reset_btn, stretch=1)
        button_layout.setContentsMargins(0, 5, 0, 5)

        input_layout.addLayout(button_layout)

        # Add stretch to push content to top
        input_layout.addStretch()

        input_panel.setMinimumWidth(520)
        main_splitter.addWidget(input_panel)

        # --- Mittleres Panel: Kartenansicht ---
        self.map_panel = QtWidgets.QWidget()
        self.map_panel.setMinimumHeight(260)
        map_layout = QtWidgets.QVBoxLayout(self.map_panel)
        map_layout.setContentsMargins(0, 0, 0, 0)

        self.map_view = None
        self.map_fallback_label = None
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

        # Rechtes Panel: Karte oben, Ausgabe unten
        right_panel = QtWidgets.QWidget()
        right_layout = QtWidgets.QVBoxLayout(right_panel)
        right_layout.setContentsMargins(0, 0, 0, 0)

        right_splitter = QtWidgets.QSplitter(QtCore.Qt.Orientation.Vertical)
        right_splitter.addWidget(self.map_panel)

        # --- Unteres Panel: Output/Logs ---
        output_panel = QtWidgets.QWidget()
        output_panel.setMinimumHeight(95)
        output_layout = QtWidgets.QVBoxLayout(output_panel)
        output_layout.setContentsMargins(0, 0, 0, 0)

        self.output_label = QtWidgets.QLabel(self.strings["output"])
        self.output_label.setObjectName("outputLabel")
        output_layout.addWidget(self.output_label)

        self.log = QtWidgets.QPlainTextEdit()
        self.log.setReadOnly(True)
        self.log.setMaximumHeight(160)
        output_layout.addWidget(self.log)

        right_splitter.addWidget(output_panel)
        right_splitter.setStretchFactor(0, 5)
        right_splitter.setStretchFactor(1, 1)

        right_layout.addWidget(right_splitter)

        right_panel.setMinimumWidth(520)
        main_splitter.addWidget(right_panel)
        main_splitter.setStretchFactor(0, 2)
        main_splitter.setStretchFactor(1, 3)

        self.main_splitter = main_splitter
        self.right_splitter = right_splitter
        main_layout.addWidget(self.main_splitter)

        self.main_splitter.setSizes([540, 900])
        self.right_splitter.setSizes([560, 120])

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

        # Help menu
        help_menu = menubar.addMenu(self.strings["help"])

        # Documentation
        help_menu.addSeparator()
        doc_action = help_menu.addAction(
            "📖 " + self.strings.get("documentation", "Dokumentation")
        )
        doc_action.triggered.connect(self.open_documentation)

        # GitHub
        github_action = help_menu.addAction("🔗 GitHub Repository")
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
        webbrowser.open("https://www.youtube.com/watch?v=2qBlE2-WL60&t=3s")

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
        self.reset_btn.setText(self.strings.get("reset", "Zurücksetzen"))

        if self.map_fallback_label is not None:
            self.map_fallback_label.setText(
                self.strings.get(
                    "map_panel_fallback",
                    "Kartenpanel benötigt QtWebEngine. Browser-Fallback ist aktiv.",
                )
            )

        # Recreate menu bar for language change
        menubar = self.menuBar()
        menubar.clear()
        self._create_menu_bar()

        # Update status bar
        self.status.showMessage(self.strings["ready"])

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

    def _collect_map_items(self, features, summaries):
        from shapely.geometry import Polygon, MultiPolygon

        items = []
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

            label = str(summary.schlag_flurstueck or feat.name or "Fläche")

            if isinstance(geom, Polygon):
                items.append(
                    {
                        "applicant": applicant,
                        "label": label,
                        "rings": self._to_leaflet_rings(geom),
                    }
                )
            elif isinstance(geom, MultiPolygon):
                for idx, poly in enumerate(geom.geoms, start=1):
                    items.append(
                        {
                            "applicant": applicant,
                            "label": f"{label}-{idx}",
                            "rings": self._to_leaflet_rings(poly),
                        }
                    )
        return items

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
        default_center=None,
        default_zoom: int = 11,
    ):
        title = self.strings.get("map_title", "Satellitenkarte")
        map_items_json = json.dumps(map_items, ensure_ascii=False)
        color_map_json = json.dumps(color_map, ensure_ascii=False)
        title_json = json.dumps(title, ensure_ascii=False)
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
    .legend-item {{ display: flex; align-items: center; margin-bottom: 4px; }}
    .swatch {{ width: 14px; height: 14px; border-radius: 2px; margin-right: 6px; border: 1px solid #444; }}
  </style>
</head>
<body>
  <div id=\"map\"></div>
  <div id=\"legend\"></div>

    <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
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
        const defaultCenter = {center_json};
        const defaultZoom = {int(default_zoom)};

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
                    mapNode.textContent = 'Leaflet konnte nicht geladen werden (Offline/Netzwerk).';
                }}
                return;
            }}

            const map = L.map('map', {{ zoomControl: true }});
            L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{{z}}/{{y}}/{{x}}', {{
                attribution: 'Tiles © Esri'
            }}).addTo(map);

            const group = L.featureGroup().addTo(map);
            for (const feature of features) {{
                const color = colors[feature.applicant] || '#ff0000';
                const poly = L.polygon(feature.rings, {{
                    color: color,
                    weight: 2,
                    fillColor: color,
                    fillOpacity: 0.35
                }});
                poly.bindPopup(
                    '<b>' + escapeHtml(feature.label) + '</b><br>' +
                    escapeHtml(feature.applicant)
                );
                poly.addTo(group);
            }}

            if (group.getLayers().length > 0) {{
                map.fitBounds(group.getBounds().pad(0.08));
            }} else {{
            map.setView(defaultCenter, defaultZoom);
            }}

            const legend = document.getElementById('legend');
            legend.innerHTML = '<strong>' + escapeHtml(title) + '</strong><hr style="margin:6px 0;">';
            for (const [applicant, color] of Object.entries(colors).sort((a, b) => a[0].localeCompare(b[0], 'de'))) {{
                const row = document.createElement('div');
                row.className = 'legend-item';
                row.innerHTML = '<span class="swatch" style="background:' + color + '"></span>' + escapeHtml(applicant);
                legend.appendChild(row);
            }}

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

    def _write_default_map(self):
        html = self._build_satellite_map_html(
            [],
            {},
            default_center=self.default_map_center,
            default_zoom=self.default_map_zoom,
        )
        html_path = self._save_map_html(html)
        self._open_map_preview(html_path, fallback_to_browser=False, log_open=False)

    def _update_map_panel_visibility(self):
        if self.map_view is None:
            return
        self.map_panel.setVisible(True)

        is_large = self.isMaximized() or (self.width() >= 1450 and self.height() >= 880)
        if is_large:
            self.main_splitter.setSizes([500, 1000])
            self.right_splitter.setSizes([700, 110])
        else:
            self.main_splitter.setSizes([540, 900])
            self.right_splitter.setSizes([560, 120])

        html_path = self._map_output_dir() / "satellitenkarte.html"
        if not html_path.exists():
            self._write_default_map()
            return
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
    ):
        if self.map_view is not None:
            self.map_view.setUrl(QtCore.QUrl.fromLocalFile(str(html_path.resolve())))
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
            self.status.showMessage(self.strings.get("map_loading", "Lade Karte..."))
            self.logln(self.strings.get("map_loading", "Lade Karte..."))
            QtCore.QCoreApplication.processEvents()

            features = kmz.parse_kmz_to_area_features(str(kmz_path))
            summaries = kmz.summarize_features(features)
            map_items = self._collect_map_items(features, summaries)

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

            html = self._build_satellite_map_html(
                map_items,
                color_map,
                default_center=self.default_map_center,
                default_zoom=self.default_map_zoom,
            )
            html_path = self._save_map_html(html)

            self._open_map_preview(html_path)
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

            from shapely.geometry import Polygon, MultiPolygon

            polys = []
            names = []
            directions = []

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
            for feat, summary in zip(features, summaries):
                geom = feat.geom
                if geom is None:
                    continue

                nachname = _clean(summary.antragsteller_name or "unbekannt")
                datum = _fmt_short_date(summary.datum_mahd)
                schlag = _clean(summary.schlag_flurstueck or feat.name or basename)

                base_file_name = f"{nachname}-{datum}-{schlag}"

                if isinstance(geom, Polygon):
                    polys.append(geom)
                    names.append(base_file_name)
                    if (
                        self.optimize_direction_check.isChecked()
                        and optimizer is not None
                    ):
                        directions.append(
                            int(round(float(optimizer.mrr_angle_deg(geom)))) % 180
                        )
                    else:
                        directions.append(0)
                elif isinstance(geom, MultiPolygon):
                    for idx, poly in enumerate(geom.geoms, start=1):
                        polys.append(poly)
                        names.append(f"{base_file_name}-{idx}")
                        if (
                            self.optimize_direction_check.isChecked()
                            and optimizer is not None
                        ):
                            directions.append(
                                int(round(float(optimizer.mrr_angle_deg(poly)))) % 180
                            )
                        else:
                            directions.append(0)

            if not polys:
                self.logln("❌ Keine Polygone gefunden.")
                self.status.showMessage("Keine Polygone.")
                self.progress.setVisible(False)
                self.convert_btn.setEnabled(True)
                return

            self.logln(f"✓ {len(polys)} Polygone extrahiert")
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
        self.optimize_direction_check.setChecked(False)
        self.elevation_optimize_check.setChecked(True)

        # File paths
        self.kmz_edit.clear()
        self.out_edit.setText(str(Path.cwd() / "out"))

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
