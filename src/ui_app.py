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
import csv
import hashlib
import math
import base64
from datetime import datetime
import subprocess
import webbrowser
import urllib.request
import urllib.error
import urllib.parse
import tempfile
import socket
import uuid

ENGINE_IMPORT_ERROR = None
optimize_angle_mod = None
APP_VERSION = "0.0.0"
GITHUB_REPO = "messmersvenpriv/LittleOne"
TOILET_PAPER_URL = "https://www.hygi.de/category/toilettenpapier?msclkid=fdd7cb679dff18c16f86a2f869da95cd"

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
        "title": "LittleOne - Datenkonvertierungssoftware der Kitzrettung Rastatt Baden-Baden",
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
        "convert": "Konvertieren und Exportieren",
        "convert_upload": "Konvertieren und Hochladen",
        "upload_select_drone": "Zieldrohne auswählen",
        "upload_no_mapping": "Keine FlightHub-Gerätezuordnung für den gewählten Drohnentyp gefunden.",
        "upload_missing_config": "FlightHub-Konfiguration fehlt oder ist ungültig:\n{path}",
        "upload_invalid_config": "FlightHub-Konfiguration ist unvollständig:\n{details}",
        "upload_devices_api_failed": "Geräteliste konnte nicht live geladen werden. Es wird das lokale Mapping verwendet.",
        "upload_missing_mission_id": "Upload-Antwort enthält keine mission_id (Datei: {file}).",
        "upload_started": "Konvertierung und Upload gestartet ...",
        "upload_done": "Upload abgeschlossen",
        "upload_failed": "Upload fehlgeschlagen",
        "upload_select_prompt": "Bitte Zielgerät für Typ {drone} auswählen:",
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
        "map_set_start_area": "Als Startfläche festlegen",
        "map_start_area_selected": "Startfläche ausgewählt",
        "map_set_new_start_area": "Diese Fläche als neuen Startpunkt festlegen",
        "map_browser_fallback_opened": "QtWebEngine nicht verfügbar – Karte im Standardbrowser geöffnet.",
        "map_opened_gui_suffix": "GUI",
        "map_start_set_log": "Startfläche gesetzt: {key}",
        "map_area_reenabled_log": "Fläche wieder aktiviert: {key}",
        "map_area_excluded_log": "Fläche ausgeschlossen: {key}",
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
        "offline_notice_title": "Offline-Hinweis",
        "offline_notice_message": "Keine Internetverbindung erkannt.\n\nDie Konvertierung von KMZ/KML funktioniert weiterhin.\nKartenansicht und Tagesplan-Routing sind offline eingeschränkt und nutzen ggf. Fallbacks.",
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
        "save_defaults_action": "Aktuelle Werte als Standard speichern",
        "save_defaults_status": "Standardeinstellungen gespeichert",
        "save_defaults_ok": "Standardeinstellungen wurden gespeichert:",
        "save_defaults_error": "Standardeinstellungen konnten nicht gespeichert werden:",
        "update_check_action": "Nach Updates suchen",
        "help_github": "GitHub Repository",
        "help_easter": "G-Mode aktivieren",
        "about_text": "Kitzrettung – DJI Drohnen-Missionsplaner v1.0\n\nEin professionelles Tool zur Erstellung von DJI-Missionen\naus KML/KMZ-Gebietsdaten.\n\nUnterstützte Drohnen: M4T, M3T, M2EA\n\n© 2024–2026 | Lizenz: MIT\n\nFür vollständige Dokumentation siehe Help → Dokumentation",
        "doc_open_error": "Konnte Dokumentation nicht öffnen:",
        "doc_not_found": "README.md nicht gefunden.\n\nBitte besuche das GitHub Repository für die vollständige Dokumentation:\nhttps://github.com/messmersvenpriv/LittleOne",
        "github_open_error": "Konnte GitHub nicht öffnen:\n{error}\n\nBitte besuche manuell:\n{url}",
        "offline_log": "ℹ Kein Internet erkannt – Konvertierung bleibt verfügbar.",
        "action_end_route": "Routenmodus verlassen",
        "action_end_rth": "Rückkehrfunktion",
        "action_end_land": "Landen",
        "action_end_first_wp": "Zur Startposition zurückkehren und schweben",
        "update_checking": "Prüfe auf Updates ...",
        "updates_title": "Updates",
        "updates_up_to_date": "Du nutzt bereits die aktuelle Version ({version}).",
        "update_none_status": "Keine Updates verfügbar",
        "update_available_title": "Update verfügbar",
        "update_available_msg": "Update verfügbar: {release_name}\nAktuell: {current}\nNeu: {latest}\n\n",
        "update_prompt_install": "Jetzt Installer herunterladen und Update starten?\n(Bevorzugt wird Setup.exe aus dem Release)",
        "update_prompt_open": "Download-Seite öffnen?",
        "update_check_done": "Updateprüfung beendet",
        "release_page_opened": "Release-Seite geöffnet",
        "update_downloading": "Lade Update herunter ...",
        "update_downloaded": "Update wurde geladen. Der Installer wird jetzt gestartet.\n\nBitte Rückfragen der Windows-Sicherheit bestätigen.",
        "update_no_release": "Es wurde kein veröffentlichter GitHub-Release gefunden (HTTP 404).\nBitte veröffentliche einen Release (nicht nur Tag) oder prüfe die Repository-Sichtbarkeit.",
        "update_no_release_status": "Kein veröffentlichter Release gefunden",
        "update_error_title": "Updatefehler",
        "update_error_http": "Konnte Update-Informationen nicht laden (HTTP {code}):\n{reason}",
        "update_error_status": "Updateprüfung fehlgeschlagen",
        "update_error_ssl_hint": "\n\nHinweis: In VPN/Proxy-Netzen kann SSL-Inspection aktiv sein. Bitte Firmen-Zertifikate prüfen oder kurz ohne VPN testen.",
        "update_error_generic": "Fehler bei Updateprüfung:\n{error}",
        "pick_output_dir": "Ausgabeordner wählen",
        "map_error_log": "❌ Kartenfehler:",
        "day_plan_start_info": "Bitte zuerst eine Startfläche in der Karte auswählen\noder hier den Startpunkt (Wohnort) eingeben.",
        "day_plan_start_placeholder": "Startpunkt (Wohnort), z. B. Musterstraße 1, 76437 Rastatt",
        "day_plan_start_hint": "Leer lassen, wenn Sie die Startfläche direkt in der Karte festlegen möchten.",
        "day_plan_options_title_suffix": "Optionen",
        "day_plan_options_info": "Bitte auswählen, was für den Tagesplan berechnet werden soll.",
        "day_plan_opt_drive": "Fahrtzeiten und Wege berechnen",
        "day_plan_opt_total": "Gesamtdauer berechnen (Flugzeit-Faktor + Kitzzeiten)",
        "day_plan_options_hint": "Kitzdaten werden aus data/Locations/Rehkitz_Fundort.csv gelesen. Mehrere Einträge je Jahr innerhalb einer Fläche werden summiert.",
        "day_plan_start_auto": "Automatisch",
        "day_plan_start_home_prefix": "Wohnort",
        "day_plan_start_area": "Startfläche aus Karte",
        "day_plan_header_areas": "Flächen",
        "day_plan_header_distance": "Strecke",
        "day_plan_header_drive_time": "Fahrzeit",
        "day_plan_header_flight_time": "Flugzeit",
        "day_plan_header_total": "Tageseinsatz",
        "day_plan_header_start": "Start",
        "day_plan_segments": "Fahrtsegmente:",
        "day_plan_timeline_drive": "Zeitablauf (Fahrt + Flug):",
        "day_plan_timeline_flight": "Zeitablauf (Flug):",
        "day_plan_step_drive": "Fahrt",
        "day_plan_step_flight": "Flug",
        "day_plan_area_processing": "Bearbeitungszeit je Fläche:",
        "day_plan_label_factor": "Faktor",
        "day_plan_label_flight_adjusted": "Flug bereinigt",
        "day_plan_label_avg_kitz": "Ø Kitze",
        "day_plan_label_kitz_time": "+Kitzzeit",
        "day_plan_label_years": "Jahre",
        "day_plan_total_work": "Tageseinsatz gesamt",
        "day_plan_total_kitz": "davon Kitzzeiten",
        "day_plan_routing_source": "Routing-Quelle",
        "day_plan_routing_fallback": "Hinweis: Fallback mit Luftlinie + Durchschnittsgeschwindigkeit aktiv.",
        "day_plan_calc_status": "Berechne Tagesplan ...",
        "day_plan_calc_log": "Berechne Tagesplan ...",
        "day_plan_need_start": "Bitte entweder eine Startfläche in der Karte auswählen oder einen Wohnort eingeben.",
        "day_plan_home_set": "Startpunkt (Wohnort) gesetzt: {home}",
        "day_plan_home_error": "Wohnort konnte nicht ermittelt werden:\n{error}",
        "day_plan_csv_missing": "⚠ Kitz-CSV nicht gefunden: {path}",
        "day_plan_csv_loaded": "Kitz-CSV geladen: {path} ({years} Jahre)",
        "day_plan_no_active_areas": "Keine aktiven Flächen für Tagesplan vorhanden.",
        "day_plan_created_log": "✓ Tagesplan: {areas} Flächen, {distance_km:.2f} km, {drive_min:.1f} min Fahrt, {flight_min:.1f} min Flug, {total_min:.1f} min Gesamt",
        "day_plan_created_status": "Tagesplan erstellt",
        "day_plan_error_log": "❌ Tagesplan-Fehler:",
        "geocode_not_found": "Adresse nicht gefunden",
        "convert_start_log": "Starte Konvertierung: {path}",
        "convert_settings_log": "Einstellungen:",
        "convert_parsing_log": "Parsing KMZ...",
        "convert_features_loaded": "✓ {count} Features geladen",
        "convert_extract_polygons": "Extrahiere Polygone...",
        "convert_excluded": "ℹ {count} Fläche(n) ausgeschlossen und nicht konvertiert",
        "convert_no_polygons_log": "❌ Keine Polygone gefunden.",
        "convert_no_polygons_status": "Keine Polygone.",
        "convert_polygons_extracted": "✓ {count} Polygone extrahiert",
        "convert_estimate": "ℹ Schätzung optimierter Flugweg: {distance_m:.1f} m, {minutes:.1f} min",
        "convert_normalizing": "Normalisiere Geometrien...",
        "convert_normalized": "✓ Geometrien normalisiert",
        "convert_writing": "Schreibe {count} KMZ-Dateien...",
        "convert_generated": "✓ {count} KMZ-Dateien generiert",
        "convert_combined": "Zusätzliche Sammel-KMZ: {name}",
        "convert_output_folder": "Ausgabeordner: {path}",
        "convert_debug_kml": "Debug-KMLs: {path}",
        "convert_success_text": "✓ Erfolgreich: {count} KMZ-Dateien\n\nAusgabe:\n{out_dir}\n\nDebug-KMLs:\n{debug_dir}",
        "convert_combined_suffix": "\n\nZusätzliche Sammel-KMZ:\n{name}",
        "convert_error_log": "❌ FEHLER:",
        "engine_unknown_import_error": "Unbekannter Importfehler",
        "engine_import_log": "Engine-Importfehler: {error}",
        "engine_load_failed": "LittleOne-Engine konnte nicht geladen werden.\n\nDetails: {details}\n\nBitte venv/Startpfad prüfen.",
        "engine_unavailable": "LittleOne-Engine ist nicht verfügbar.",
        "ok": "OK",
        "cancel": "Abbrechen",
    },
    "English": {
        "title": "LittleOne - Datenkonvertierungssoftware der Kitzrettung Rastatt Baden-Baden",
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
        "convert": "Convert and Export",
        "convert_upload": "Convert and Upload",
        "upload_select_drone": "Select target drone",
        "upload_no_mapping": "No FlightHub device mapping found for the selected drone type.",
        "upload_missing_config": "FlightHub configuration is missing or invalid:\n{path}",
        "upload_invalid_config": "FlightHub configuration is incomplete:\n{details}",
        "upload_devices_api_failed": "Could not load live device list. Falling back to local mapping.",
        "upload_missing_mission_id": "Upload response has no mission_id (file: {file}).",
        "upload_started": "Conversion and upload started ...",
        "upload_done": "Upload completed",
        "upload_failed": "Upload failed",
        "upload_select_prompt": "Select target device for type {drone}:",
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
        "map_set_start_area": "Set as start area",
        "map_start_area_selected": "Start area selected",
        "map_set_new_start_area": "Set this area as new start point",
        "map_browser_fallback_opened": "QtWebEngine not available – map opened in default browser.",
        "map_opened_gui_suffix": "GUI",
        "map_start_set_log": "Start area set: {key}",
        "map_area_reenabled_log": "Area re-enabled: {key}",
        "map_area_excluded_log": "Area excluded: {key}",
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
        "offline_notice_title": "Offline notice",
        "offline_notice_message": "No internet connection detected.\n\nKMZ/KML conversion still works.\nMap view and day-plan routing are limited offline and may use fallbacks.",
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
        "save_defaults_action": "Save current values as defaults",
        "save_defaults_status": "Default settings saved",
        "save_defaults_ok": "Default settings were saved:",
        "save_defaults_error": "Default settings could not be saved:",
        "update_check_action": "Check for updates",
        "help_github": "GitHub repository",
        "help_easter": "Enable G-Mode",
        "about_text": "Kitzrettung – DJI Drone Mission Planner v1.0\n\nA professional tool for creating DJI missions\nfrom KML/KMZ area data.\n\nSupported drones: M4T, M3T, M2EA\n\n© 2024–2026 | License: MIT\n\nSee Help → Documentation for full documentation",
        "doc_open_error": "Could not open documentation:",
        "doc_not_found": "README.md not found.\n\nPlease visit the GitHub repository for full documentation:\nhttps://github.com/messmersvenpriv/LittleOne",
        "github_open_error": "Could not open GitHub:\n{error}\n\nPlease open manually:\n{url}",
        "offline_log": "ℹ No internet detected – conversion remains available.",
        "action_end_route": "Exit route mode",
        "action_end_rth": "Return to home",
        "action_end_land": "Land",
        "action_end_first_wp": "Return to start position and hover",
        "update_checking": "Checking for updates ...",
        "updates_title": "Updates",
        "updates_up_to_date": "You are already using the latest version ({version}).",
        "update_none_status": "No updates available",
        "update_available_title": "Update available",
        "update_available_msg": "Update available: {release_name}\nCurrent: {current}\nNew: {latest}\n\n",
        "update_prompt_install": "Download installer now and start update?\n(Setup.exe from release is preferred)",
        "update_prompt_open": "Open download page?",
        "update_check_done": "Update check finished",
        "release_page_opened": "Release page opened",
        "update_downloading": "Downloading update ...",
        "update_downloaded": "The update was downloaded. The installer will now start.\n\nPlease confirm Windows security prompts.",
        "update_no_release": "No published GitHub release found (HTTP 404).\nPlease publish a release (not only a tag) or check repository visibility.",
        "update_no_release_status": "No published release found",
        "update_error_title": "Update error",
        "update_error_http": "Could not load update information (HTTP {code}):\n{reason}",
        "update_error_status": "Update check failed",
        "update_error_ssl_hint": "\n\nHint: SSL inspection may be active in VPN/proxy networks. Please check corporate certificates or test briefly without VPN.",
        "update_error_generic": "Error during update check:\n{error}",
        "pick_output_dir": "Select output folder",
        "map_error_log": "❌ Map error:",
        "day_plan_start_info": "Please first select a start area on the map\nor enter the start point (home address) here.",
        "day_plan_start_placeholder": "Start point (home address), e.g. Sample Street 1, 76437 Rastatt",
        "day_plan_start_hint": "Leave empty if you want to set the start area directly on the map.",
        "day_plan_options_title_suffix": "Options",
        "day_plan_options_info": "Please choose what should be calculated for the day plan.",
        "day_plan_opt_drive": "Calculate driving times and routes",
        "day_plan_opt_total": "Calculate total duration (flight factor + fawn times)",
        "day_plan_options_hint": "Fawn data is read from data/Locations/Rehkitz_Fundort.csv. Multiple entries per year inside one area are summed.",
        "day_plan_start_auto": "Automatic",
        "day_plan_start_home_prefix": "Home",
        "day_plan_start_area": "Start area from map",
        "day_plan_header_areas": "Areas",
        "day_plan_header_distance": "Distance",
        "day_plan_header_drive_time": "Drive time",
        "day_plan_header_flight_time": "Flight time",
        "day_plan_header_total": "Day mission",
        "day_plan_header_start": "Start",
        "day_plan_segments": "Drive segments:",
        "day_plan_timeline_drive": "Timeline (Drive + Flight):",
        "day_plan_timeline_flight": "Timeline (Flight):",
        "day_plan_step_drive": "Drive",
        "day_plan_step_flight": "Flight",
        "day_plan_area_processing": "Processing time per area:",
        "day_plan_label_factor": "Factor",
        "day_plan_label_flight_adjusted": "Adjusted flight",
        "day_plan_label_avg_kitz": "Avg fawns",
        "day_plan_label_kitz_time": "+Fawn time",
        "day_plan_label_years": "Years",
        "day_plan_total_work": "Total day mission",
        "day_plan_total_kitz": "of which fawn times",
        "day_plan_routing_source": "Routing source",
        "day_plan_routing_fallback": "Note: fallback with straight-line distance + average speed is active.",
        "day_plan_calc_status": "Calculating day plan ...",
        "day_plan_calc_log": "Calculating day plan ...",
        "day_plan_need_start": "Please either select a start area on the map or enter a home address.",
        "day_plan_home_set": "Start point (home) set: {home}",
        "day_plan_home_error": "Could not resolve home address:\n{error}",
        "day_plan_csv_missing": "⚠ Fawn CSV not found: {path}",
        "day_plan_csv_loaded": "Fawn CSV loaded: {path} ({years} years)",
        "day_plan_no_active_areas": "No active areas available for day plan.",
        "day_plan_created_log": "✓ Day plan: {areas} areas, {distance_km:.2f} km, {drive_min:.1f} min drive, {flight_min:.1f} min flight, {total_min:.1f} min total",
        "day_plan_created_status": "Day plan created",
        "day_plan_error_log": "❌ Day plan error:",
        "geocode_not_found": "Address not found",
        "convert_start_log": "Starting conversion: {path}",
        "convert_settings_log": "Settings:",
        "convert_parsing_log": "Parsing KMZ...",
        "convert_features_loaded": "✓ {count} features loaded",
        "convert_extract_polygons": "Extracting polygons...",
        "convert_excluded": "ℹ {count} area(s) excluded and not converted",
        "convert_no_polygons_log": "❌ No polygons found.",
        "convert_no_polygons_status": "No polygons.",
        "convert_polygons_extracted": "✓ {count} polygons extracted",
        "convert_estimate": "ℹ Estimated optimized flight path: {distance_m:.1f} m, {minutes:.1f} min",
        "convert_normalizing": "Normalizing geometries...",
        "convert_normalized": "✓ Geometries normalized",
        "convert_writing": "Writing {count} KMZ files...",
        "convert_generated": "✓ {count} KMZ files generated",
        "convert_combined": "Additional combined KMZ: {name}",
        "convert_output_folder": "Output folder: {path}",
        "convert_debug_kml": "Debug KMLs: {path}",
        "convert_success_text": "✓ Success: {count} KMZ files\n\nOutput:\n{out_dir}\n\nDebug KMLs:\n{debug_dir}",
        "convert_combined_suffix": "\n\nAdditional combined KMZ:\n{name}",
        "convert_error_log": "❌ ERROR:",
        "engine_unknown_import_error": "Unknown import error",
        "engine_import_log": "Engine import error: {error}",
        "engine_load_failed": "LittleOne engine could not be loaded.\n\nDetails: {details}\n\nPlease check venv/start path.",
        "engine_unavailable": "LittleOne engine is not available.",
        "ok": "OK",
        "cancel": "Cancel",
    },
    "Français": {
        "title": "LittleOne - Datenkonvertierungssoftware der Kitzrettung Rastatt Baden-Baden",
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
        "offline_notice_title": "Avis hors ligne",
        "offline_notice_message": "Aucune connexion Internet détectée.\n\nLa conversion KMZ/KML continue de fonctionner.\nLa carte et le routage du plan du jour sont limités hors ligne et peuvent utiliser des alternatives.",
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
        "title": "LittleOne - Datenkonvertierungssoftware der Kitzrettung Rastatt Baden-Baden",
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
        "offline_notice_title": "Offline-ilmoitus",
        "offline_notice_message": "Internet-yhteyttä ei havaittu.\n\nKMZ/KML-muunnos toimii silti.\nKarttanäkymä ja päiväsuunnitelman reititys ovat offline-tilassa rajoitettuja ja voivat käyttää vararatkaisuja.",
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

FORM_DEFAULTS = {
    "overlap": 30,
    "margin": 0,
    "drone": "M4T",
    "action": "Rückkehrfunktion",
    "optimize_direction": True,
    "optimize_elevation": False,
    "output_dir": "",
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


class FlightHubSyncClient:
    def __init__(self, config: dict):
        self.config = config or {}
        self.base_url = str(self.config.get("base_url") or "").strip().rstrip("/")
        self.timeout = int(self.config.get("timeout_seconds", 30))

    def _configured_project_uuid(self) -> str:
        value = str(self.config.get("project_uuid") or "").strip()
        if value:
            return value
        auth = self.config.get("auth") if isinstance(self.config, dict) else {}
        auth = auth if isinstance(auth, dict) else {}
        return str(auth.get("project_uuid") or "").strip()

    def _base_auth_headers(self) -> dict:
        auth = self.config.get("auth") if isinstance(self.config, dict) else {}
        auth = auth if isinstance(auth, dict) else {}

        headers = {}
        static_token = str(auth.get("access_token") or "").strip()
        if static_token:
            header_name = str(auth.get("header_name") or "Authorization").strip()
            if header_name.lower() == "authorization":
                token_prefix = str(auth.get("token_prefix") or "Bearer").strip()
                headers["Authorization"] = (
                    f"{token_prefix} {static_token}" if token_prefix else static_token
                )
            else:
                headers[header_name] = static_token

            # FlightHub2 OpenAPI expects X-User-Token.
            # Keep x-auth-token compatibility for gateway/UI APIs.
            headers.setdefault("X-User-Token", static_token)
            headers.setdefault("x-auth-token", static_token)

        project_uuid = self._configured_project_uuid()
        if project_uuid:
            headers["X-Project-Uuid"] = project_uuid
        return headers

    def _build_url(self, path_or_url: str) -> str:
        raw = str(path_or_url or "").strip()
        if not raw:
            raise ValueError("FlightHub endpoint is missing")
        if raw.startswith("http://") or raw.startswith("https://"):
            return raw
        if not self.base_url:
            raise ValueError("FlightHub base_url is missing")
        if not raw.startswith("/"):
            raw = "/" + raw
        return self.base_url + raw

    def _request_json(
        self,
        method: str,
        path_or_url: str,
        payload: dict | None = None,
        extra_headers: dict | None = None,
    ) -> dict:
        url = self._build_url(path_or_url)
        headers = {
            "User-Agent": "LittleOne-FlightHub/1.0",
            "Accept": "application/json",
            "X-Request-Id": str(uuid.uuid4()),
        }
        headers.update(self._base_auth_headers())
        if extra_headers:
            headers.update({str(k): str(v) for k, v in extra_headers.items()})

        body = None
        if payload is not None:
            body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
            headers["Content-Type"] = "application/json"

        req = urllib.request.Request(url, data=body, headers=headers, method=method)
        try:
            with urllib.request.urlopen(req, timeout=self.timeout) as resp:
                text = resp.read().decode("utf-8", errors="replace")
        except urllib.error.HTTPError as ex:
            err_text = ex.read().decode("utf-8", errors="replace") if ex.fp else ""
            err_payload = {}
            if err_text.strip():
                try:
                    parsed = json.loads(err_text)
                    if isinstance(parsed, dict):
                        err_payload = parsed
                    else:
                        err_payload = {"data": parsed}
                except Exception:
                    err_payload = {"raw": err_text}

            detail = (
                err_payload.get("message") if isinstance(err_payload, dict) else None
            )
            detail = str(detail or err_payload or ex.reason)
            raise RuntimeError(f"HTTP {ex.code} {ex.reason}: {detail}") from ex
        if not text.strip():
            return {}
        try:
            parsed = json.loads(text)
            return parsed if isinstance(parsed, dict) else {"data": parsed}
        except Exception:
            return {"raw": text}

    def _auth_headers(self) -> dict:
        auth = self.config.get("auth") if isinstance(self.config, dict) else {}
        auth = auth if isinstance(auth, dict) else {}

        static_token = str(auth.get("access_token") or "").strip()
        if static_token:
            return self._base_auth_headers()

        token_url = str(auth.get("token_url") or "").strip()
        client_id = str(auth.get("client_id") or "").strip()
        client_secret = str(auth.get("client_secret") or "").strip()
        if not (token_url and client_id and client_secret):
            return {}

        payload = {
            "grant_type": "client_credentials",
            "client_id": client_id,
            "client_secret": client_secret,
        }
        token_data = self._request_json("POST", token_url, payload=payload)
        token = str(token_data.get("access_token") or "").strip()
        if not token:
            raise RuntimeError("FlightHub token request returned no access_token")
        oauth_headers = self._base_auth_headers()
        token_prefix = str(auth.get("token_prefix") or "Bearer").strip()
        oauth_headers["Authorization"] = (
            f"{token_prefix} {token}" if token_prefix else token
        )
        return oauth_headers

    def validate_config(self) -> list[str]:
        issues = []
        if not self.base_url:
            issues.append("base_url fehlt")

        endpoints = (
            self.config.get("endpoints") if isinstance(self.config, dict) else {}
        )
        endpoints = endpoints if isinstance(endpoints, dict) else {}
        upload_endpoint = str(endpoints.get("upload") or "").strip()
        if not upload_endpoint:
            issues.append("endpoints.upload fehlt")

        auth = self.config.get("auth") if isinstance(self.config, dict) else {}
        auth = auth if isinstance(auth, dict) else {}
        has_access_token = bool(str(auth.get("access_token") or "").strip())
        has_oauth = all(
            bool(str(auth.get(key) or "").strip())
            for key in ("token_url", "client_id", "client_secret")
        )
        if not (has_access_token or has_oauth):
            issues.append(
                "Credentials fehlen (auth.access_token ODER auth.token_url + client_id + client_secret)"
            )
        return issues

    def _normalize_devices(self, raw) -> list[dict]:
        def _map_model_name(value: str) -> str:
            text = str(value or "").strip().upper().replace(" ", "")
            if "MATRICE4T" in text or text in {"M4T", "M4TD"}:
                return "M4T"
            if "MATRICE3T" in text or text in {"M3T", "M3TD"}:
                return "M3T"
            if "MATRICE30T" in text or text in {"M30T", "M2EA"}:
                return "M2EA"
            return str(value or "").strip()

        out = []

        # FlightHub2 OpenAPI shape: data.list[].drone / data.list[].gateway
        if isinstance(raw, dict):
            data = raw.get("data") if isinstance(raw.get("data"), dict) else {}
            list_items = data.get("list") if isinstance(data, dict) else []
            if isinstance(list_items, list):
                for item in list_items:
                    if not isinstance(item, dict):
                        continue
                    for node_key in ("drone", "gateway"):
                        node = item.get(node_key)
                        if not isinstance(node, dict):
                            continue
                        dev_id = str(node.get("sn") or "").strip()
                        model_raw = ""
                        device_model = node.get("device_model")
                        if isinstance(device_model, dict):
                            model_raw = str(device_model.get("name") or "").strip()
                        model = _map_model_name(model_raw)
                        if not dev_id or not model:
                            continue
                        out.append(
                            {
                                "id": dev_id,
                                "name": str(node.get("callsign") or dev_id),
                                "model": model,
                                "workspace_id": self._configured_project_uuid(),
                                "enabled": True,
                            }
                        )
                if out:
                    return out

        if isinstance(raw, dict):
            candidates = (
                raw.get("devices")
                or raw.get("items")
                or raw.get("results")
                or raw.get("data")
                or []
            )
        elif isinstance(raw, list):
            candidates = raw
        else:
            candidates = []

        for item in candidates:
            if not isinstance(item, dict):
                continue
            dev_id = str(
                item.get("id") or item.get("device_id") or item.get("deviceId") or ""
            ).strip()
            model = str(
                item.get("model")
                or item.get("drone_type")
                or item.get("droneType")
                or ""
            ).strip()
            model = _map_model_name(model)
            if not dev_id or not model:
                continue
            out.append(
                {
                    "id": dev_id,
                    "name": str(item.get("name") or item.get("label") or dev_id),
                    "model": model,
                    "workspace_id": str(
                        item.get("workspace_id") or item.get("workspaceId") or ""
                    ),
                    "enabled": bool(item.get("enabled", True)),
                }
            )
        return out

    def list_devices(self, drone_type: str | None = None) -> list[dict]:
        endpoints = (
            self.config.get("endpoints") if isinstance(self.config, dict) else {}
        )
        endpoints = endpoints if isinstance(endpoints, dict) else {}
        devices_endpoint = str(endpoints.get("devices") or "").strip()
        if not devices_endpoint:
            return []

        query = ""
        drone_val = str(drone_type or "").strip()
        if drone_val and "/openapi/" not in devices_endpoint:
            query = urllib.parse.urlencode({"model": drone_val})

        path_or_url = devices_endpoint
        if query:
            separator = "&" if "?" in devices_endpoint else "?"
            path_or_url = f"{devices_endpoint}{separator}{query}"

        data = self._request_json(
            "GET",
            path_or_url,
            payload=None,
            extra_headers=self._auth_headers(),
        )
        return self._normalize_devices(data)

    def upload_mission_file(
        self,
        file_path: Path,
        target_device: dict,
        drone_type: str,
    ) -> dict:
        endpoints = (
            self.config.get("endpoints") if isinstance(self.config, dict) else {}
        )
        endpoints = endpoints if isinstance(endpoints, dict) else {}
        upload_endpoint = str(endpoints.get("upload") or "").strip()
        if not upload_endpoint:
            raise RuntimeError("FlightHub upload endpoint is not configured")

        # DJI FlightHub2 OpenAPI flow:
        # 1) GET /openapi/v0.1/project/sts-token
        # 2) Upload KMZ to OSS with STS credentials -> object_key
        # 3) POST /openapi/v0.1/wayline/finish-upload with {name, object_key}
        if "/openapi/v0.1/wayline/finish-upload" in upload_endpoint:
            sts_endpoint = str(
                endpoints.get("sts") or "/openapi/v0.1/project/sts-token"
            )
            sts_resp = self._request_json(
                "GET",
                sts_endpoint,
                payload=None,
                extra_headers=self._auth_headers(),
            )

            data = sts_resp.get("data") if isinstance(sts_resp, dict) else {}
            data = data if isinstance(data, dict) else {}
            endpoint = str(data.get("endpoint") or "").strip()
            provider = str(data.get("provider") or "").strip().lower()
            sts_region = str(data.get("region") or "").strip()
            bucket_name = str(data.get("bucket") or "").strip()
            prefix = str(data.get("object_key_prefix") or "").strip().strip("/")
            creds_raw = data.get("credentials")
            creds = creds_raw if isinstance(creds_raw, dict) else {}
            access_key_id = str(creds.get("access_key_id") or "").strip()
            access_key_secret = str(creds.get("access_key_secret") or "").strip()
            security_token = str(creds.get("security_token") or "").strip()

            missing = []
            if not endpoint:
                missing.append("data.endpoint")
            if not bucket_name:
                missing.append("data.bucket")
            if not prefix:
                missing.append("data.object_key_prefix")
            if not access_key_id:
                missing.append("data.credentials.access_key_id")
            if not access_key_secret:
                missing.append("data.credentials.access_key_secret")
            if not security_token:
                missing.append("data.credentials.security_token")
            if missing:
                raise RuntimeError("STS-Antwort unvollständig: " + ", ".join(missing))

            oss_region = sts_region
            host = ""
            if (not oss_region) or (provider == "ali" and "-" not in oss_region):
                try:
                    host = urllib.parse.urlparse(endpoint).netloc
                except Exception:
                    host = ""
                if "oss-" in host:
                    seg = host.split("oss-", 1)[1]
                    seg = seg.split(".", 1)[0]
                    if seg:
                        oss_region = seg
            elif not host:
                try:
                    host = urllib.parse.urlparse(endpoint).netloc
                except Exception:
                    host = ""

            auth_cfg = self.config.get("auth") if isinstance(self.config, dict) else {}
            auth_cfg = auth_cfg if isinstance(auth_cfg, dict) else {}
            allow_v1_fallback = bool(auth_cfg.get("allow_legacy_fallback", False))

            stem = str(file_path.stem or "mission").strip()
            stem = re.sub(r"[^A-Za-z0-9-]+", "-", stem)
            stem = re.sub(r"-+", "-", stem).strip("-") or "mission"
            safe_filename = f"{stem}.kmz"
            object_key = f"{prefix}/{uuid.uuid4()}/{safe_filename}".strip("/")
            upload_job = {
                "provider": provider,
                "endpoint": endpoint,
                "bucket": bucket_name,
                "access_key_id": access_key_id,
                "access_key_secret": access_key_secret,
                "security_token": security_token,
                "object_key": object_key,
                "file_path": str(file_path),
                "timeout": int(self.timeout),
                "auth_version": "v4",
                "oss_region": oss_region,
                "allow_v1_fallback": allow_v1_fallback,
            }
            upload_script = (
                "import json,sys\n"
                "payload=json.loads(sys.stdin.read())\n"
                "provider=str(payload.get('provider') or '').lower()\n"
                "endpoint=str(payload.get('endpoint') or '')\n"
                "if provider=='aws' or 'amazonaws.com' in endpoint:\n"
                "    import boto3\n"
                "    from botocore.config import Config\n"
                "    client=boto3.client(\n"
                "        's3',\n"
                "        endpoint_url=endpoint,\n"
                "        region_name=(payload.get('oss_region') or None),\n"
                "        aws_access_key_id=payload['access_key_id'],\n"
                "        aws_secret_access_key=payload['access_key_secret'],\n"
                "        aws_session_token=payload['security_token'],\n"
                "        config=Config(signature_version='s3v4', s3={'addressing_style': 'path'})\n"
                "    )\n"
                "    with open(payload['file_path'],'rb') as fh:\n"
                "        client.put_object(Bucket=payload['bucket'], Key=payload['object_key'], Body=fh, ContentType='application/vnd.google-earth.kmz')\n"
                "    print('OK:aws-s3v4')\n"
                "    sys.exit(0)\n"
                "import oss2\n"
                "preferred=str(payload.get('auth_version') or 'v4')\n"
                "allow_v1=bool(payload.get('allow_v1_fallback', False))\n"
                "versions=[preferred]\n"
                "if 'v2' not in versions:\n"
                "    versions.append('v2')\n"
                "if allow_v1 and 'v1' not in versions:\n"
                "    versions.append('v1')\n"
                "errors=[]\n"
                "for ver in versions:\n"
                "    try:\n"
                "        if ver=='v4':\n"
                "            provider2=oss2.credentials.StaticCredentialsProvider(payload['access_key_id'],payload['access_key_secret'],payload['security_token'])\n"
                "            auth=oss2.ProviderAuthV4(provider2)\n"
                "        else:\n"
                "            auth=oss2.StsAuth(payload['access_key_id'],payload['access_key_secret'],payload['security_token'],auth_version=ver)\n"
                "        bucket=oss2.Bucket(auth,payload['endpoint'],payload['bucket'],connect_timeout=int(payload.get('timeout',30)),region=(payload.get('oss_region') or None))\n"
                "        bucket.put_object_from_file(payload['object_key'],payload['file_path'],headers={'Content-Type':'application/vnd.google-earth.kmz'})\n"
                "        print('OK:'+ver)\n"
                "        sys.exit(0)\n"
                "    except Exception as ex:\n"
                "        errors.append(f'[{ver}] {type(ex).__name__}: {ex}')\n"
                "raise RuntimeError(' ; '.join(errors) if errors else 'unknown oss upload error')\n"
                "print('OK')\n"
            )
            proc = subprocess.run(
                [sys.executable, "-c", upload_script],
                input=json.dumps(upload_job, ensure_ascii=False),
                capture_output=True,
                text=True,
                timeout=max(120, int(self.timeout) * 4),
            )
            if proc.returncode != 0:
                detail = (proc.stderr or proc.stdout or "unknown error").strip()
                raise RuntimeError(
                    "OSS upload failed: "
                    f"provider={provider or '-'}, endpoint={endpoint}, region={oss_region or '-'} | "
                    + detail
                )

            payload = {
                "name": stem,
                "object_key": object_key,
            }
            return self._request_json(
                "POST",
                upload_endpoint,
                payload=payload,
                extra_headers=self._auth_headers(),
            )

        raw_bytes = file_path.read_bytes()
        encoded = base64.b64encode(raw_bytes).decode("ascii")

        payload = {
            "filename": file_path.name,
            "mime_type": "application/vnd.google-earth.kmz",
            "content_base64": encoded,
            "drone_type": str(drone_type or ""),
            "target": {
                "id": str(target_device.get("id") or ""),
                "name": str(target_device.get("name") or ""),
                "model": str(target_device.get("model") or ""),
                "workspace_id": str(target_device.get("workspace_id") or ""),
            },
        }

        return self._request_json(
            "POST",
            upload_endpoint,
            payload=payload,
            extra_headers=self._auth_headers(),
        )

    def assign_mission(
        self,
        mission_id: str,
        target_device: dict,
        task_name: str | None = None,
        flight_options: dict | None = None,
    ) -> dict:
        endpoints = (
            self.config.get("endpoints") if isinstance(self.config, dict) else {}
        )
        endpoints = endpoints if isinstance(endpoints, dict) else {}
        assign_endpoint = str(endpoints.get("assign") or "").strip()
        if not assign_endpoint:
            return {"skipped": True, "reason": "assign endpoint not configured"}

        if "/openapi/v0.1/flight-task" in assign_endpoint:
            opts = flight_options if isinstance(flight_options, dict) else {}
            action_value = str(opts.get("action") or "Rückkehrfunktion")
            out_of_control = (
                "return_home" if action_value == "Rückkehrfunktion" else "continue_task"
            )
            rth_alt = int(round(float(opts.get("safe_height_m", 60.0))))

            cfg_defaults = (
                self.config.get("task_defaults")
                if isinstance(self.config, dict)
                else {}
            )
            cfg_defaults = cfg_defaults if isinstance(cfg_defaults, dict) else {}

            payload = {
                "name": str(task_name or f"task-{mission_id[:8]}"),
                "wayline_uuid": str(mission_id or ""),
                "sn": str(target_device.get("id") or ""),
                "rth_altitude": rth_alt,
                "rth_mode": str(cfg_defaults.get("rth_mode") or "preset"),
                "wayline_precision_type": str(
                    cfg_defaults.get("wayline_precision_type") or "gps"
                ),
                "out_of_control_action_in_flight": out_of_control,
                "resumable_status": str(
                    cfg_defaults.get("resumable_status") or "manual"
                ),
                "task_type": str(cfg_defaults.get("task_type") or "immediate"),
                "time_zone": str(cfg_defaults.get("time_zone") or "Europe/Berlin"),
            }

            landing_dock_sn = str(
                cfg_defaults.get("landing_dock_sn")
                or target_device.get("landing_dock_sn")
                or ""
            ).strip()
            if landing_dock_sn:
                payload["landing_dock_sn"] = landing_dock_sn

            return self._request_json(
                "POST",
                assign_endpoint,
                payload=payload,
                extra_headers=self._auth_headers(),
            )

        payload = {
            "mission_id": str(mission_id or ""),
            "target_id": str(target_device.get("id") or ""),
            "workspace_id": str(target_device.get("workspace_id") or ""),
        }
        return self._request_json(
            "POST",
            assign_endpoint,
            payload=payload,
            extra_headers=self._auth_headers(),
        )


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

    @QtCore.Slot(str)
    def setStartArea(self, area_key: str):
        self.window.set_start_area(area_key)


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
        webbrowser.open(TOILET_PAPER_URL)

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
        self.selected_start_area_key = None
        self._startup_offline_hint_shown = False
        self.current_map_html_path = None
        self.last_map_payload = None
        self.theme = self._detect_system_theme()
        self.language = "Deutsch"
        self.units = "Metric"
        self.user_defaults = {}
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
        self.input_panel = input_panel
        input_panel.setObjectName("inputPanel")
        input_layout = QtWidgets.QVBoxLayout(input_panel)

        # Formular
        form = QtWidgets.QFormLayout()
        form.setSpacing(8)
        form.setContentsMargins(10, 10, 10, 10)

        links_row = QtWidgets.QHBoxLayout()
        links_row.setContentsMargins(10, 4, 10, 2)
        links_row.setSpacing(8)
        links_row.addStretch(1)

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
        self._populate_action_combo(FORM_DEFAULTS["action"])
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
        button_layout = QtWidgets.QVBoxLayout()
        self.action_button_layout = button_layout
        button_layout.setSpacing(8)

        self.convert_btn = QtWidgets.QPushButton(self.strings["convert"])
        self.convert_btn.clicked.connect(self.convert)

        self.convert_upload_btn = QtWidgets.QPushButton(
            self._txt("convert_upload", "Konvertieren und Hochladen")
        )
        self.convert_upload_btn.clicked.connect(self.convert_and_upload)

        self.map_btn = QtWidgets.QPushButton(
            self.strings.get("map_refresh", "Karte aktualisieren")
        )
        self.map_btn.clicked.connect(self.show_satellite_map)

        self.day_plan_btn = QtWidgets.QPushButton(
            self.strings.get("day_plan", "Tagesplan")
        )
        self.day_plan_btn.clicked.connect(self.generate_day_plan)

        self.reset_btn = QtWidgets.QPushButton(
            self.strings.get("reset", "Zurücksetzen")
        )
        self.reset_btn.clicked.connect(self.reset_to_defaults)

        action_btn_font = self.convert_btn.font()
        action_btn_font.setPointSize(10)
        self.top_action_buttons = [
            self.map_btn,
            self.day_plan_btn,
            self.reset_btn,
        ]
        self.bottom_action_buttons = [
            self.convert_btn,
            self.convert_upload_btn,
        ]
        self.action_buttons = self.top_action_buttons + self.bottom_action_buttons
        for btn in self.action_buttons:
            btn.setFont(action_btn_font)
            btn.setFixedHeight(40)
            btn.setSizePolicy(
                QtWidgets.QSizePolicy.Policy.Minimum,
                QtWidgets.QSizePolicy.Policy.Fixed,
            )

        top_row_layout = QtWidgets.QHBoxLayout()
        self.top_action_button_layout = top_row_layout
        top_row_layout.setSpacing(10)
        top_row_layout.addStretch(1)
        for btn in self.top_action_buttons:
            top_row_layout.addWidget(btn)
        top_row_layout.addStretch(1)

        bottom_row_layout = QtWidgets.QHBoxLayout()
        self.bottom_action_button_layout = bottom_row_layout
        bottom_row_layout.setSpacing(10)
        bottom_row_layout.addStretch(1)
        for btn in self.bottom_action_buttons:
            bottom_row_layout.addWidget(btn)
        bottom_row_layout.addStretch(1)

        button_layout.addLayout(top_row_layout)
        button_layout.addLayout(bottom_row_layout)
        button_layout.setContentsMargins(0, 5, 0, 5)

        input_layout.addLayout(button_layout)

        # --- Unteres Panel links: Output/Logs ---
        output_panel = QtWidgets.QWidget()
        output_panel.setMinimumHeight(96)
        output_layout = QtWidgets.QVBoxLayout(output_panel)
        output_layout.setContentsMargins(0, 0, 0, 0)

        self.output_label = QtWidgets.QLabel(self.strings["output"])
        self.output_label.setObjectName("outputLabel")
        output_layout.addWidget(self.output_label)

        self.log = QtWidgets.QPlainTextEdit()
        self.log.setReadOnly(True)
        self.log.setMinimumHeight(80)
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
        self.main_splitter.splitterMoved.connect(
            lambda _pos, _index: self._update_action_buttons_layout()
        )
        main_layout.addWidget(self.main_splitter)

        self.main_splitter.setSizes([540, 900])

        self.status = self.statusBar()
        self.status.showMessage(self.strings["ready"])

        self._load_user_defaults()
        self._apply_theme()
        self._write_default_map()
        self._update_map_panel_visibility()
        self._update_action_buttons_layout()
        QtCore.QTimer.singleShot(900, self._show_startup_connectivity_hint)

    def _user_defaults_path(self) -> Path:
        app_cfg = QtCore.QStandardPaths.writableLocation(
            QtCore.QStandardPaths.StandardLocation.AppConfigLocation
        )
        if app_cfg:
            cfg_dir = Path(app_cfg)
        else:
            cfg_dir = Path.home() / ".littleone"
        cfg_dir.mkdir(parents=True, exist_ok=True)
        return cfg_dir / "user_defaults.json"

    def _clamp_int(self, value, lower: int, upper: int) -> int:
        try:
            number = int(round(float(value)))
        except Exception:
            number = lower
        return max(lower, min(upper, number))

    def _default_output_dir(self) -> str:
        downloads = QtCore.QStandardPaths.writableLocation(
            QtCore.QStandardPaths.StandardLocation.DownloadLocation
        )
        if downloads:
            return str(Path(downloads))
        return str(Path.home() / "Downloads")

    def _remember_output_dir(self, output_dir: str):
        out_dir = str(output_dir or "").strip()
        if not out_dir:
            return

        defaults_payload = (
            self.user_defaults if isinstance(self.user_defaults, dict) else {}
        )
        defaults_raw = defaults_payload.get("defaults")
        defaults_obj: dict[str, object] = (
            {str(k): v for k, v in defaults_raw.items()}
            if isinstance(defaults_raw, dict)
            else {}
        )
        defaults_obj["output_dir"] = out_dir

        payload = {
            "theme": self.theme,
            "language": self.language,
            "units": self.units,
            "last_output_dir": out_dir,
            "defaults": defaults_obj,
        }

        self.user_defaults = payload
        try:
            path = self._user_defaults_path()
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(
                json.dumps(payload, ensure_ascii=False, indent=2),
                encoding="utf-8",
            )
        except Exception:
            pass

    def _txt(self, key: str, fallback: str = "") -> str:
        value = self.strings.get(key)
        if value is not None:
            return str(value)
        english = LANGUAGES.get("English", {})
        if key in english:
            return str(english.get(key))
        return str(fallback)

    def _end_action_items(self):
        return [
            (
                "Routenmodus verlassen",
                self._txt("action_end_route", "Routenmodus verlassen"),
            ),
            ("Rückkehrfunktion", self._txt("action_end_rth", "Rückkehrfunktion")),
            ("Landen", self._txt("action_end_land", "Landen")),
            (
                "Zur Startposition zurückkehren und schweben",
                self._txt(
                    "action_end_first_wp",
                    "Zur Startposition zurückkehren und schweben",
                ),
            ),
        ]

    def _populate_action_combo(self, preferred_canonical: str | None = None):
        previous = preferred_canonical
        if previous is None and hasattr(self, "action_combo"):
            previous = str(self.action_combo.currentData() or "").strip() or None

        self.action_combo.blockSignals(True)
        self.action_combo.clear()
        for canonical, label in self._end_action_items():
            self.action_combo.addItem(label, canonical)

        target = previous or FORM_DEFAULTS["action"]
        idx = self.action_combo.findData(target)
        if idx < 0:
            idx = self.action_combo.findData(FORM_DEFAULTS["action"])
        if idx < 0:
            idx = 0
        self.action_combo.setCurrentIndex(idx)
        self.action_combo.blockSignals(False)

    def _current_form_defaults(self) -> dict:
        metric_values = self._get_metric_values()
        return {
            "altitude": float(metric_values.get("altitude", BASE_DEFAULTS["altitude"])),
            "safe_height": float(
                metric_values.get("safe_height", BASE_DEFAULTS["safe_height"])
            ),
            "speed": float(metric_values.get("speed", BASE_DEFAULTS["speed"])),
            "overlap": int(self.overlap_spin.value()),
            "margin": int(self.margin_spin.value()),
            "drone": str(self.drone_combo.currentText()),
            "action": str(
                self.action_combo.currentData()
                or self.action_combo.currentText()
                or FORM_DEFAULTS["action"]
            ),
            "optimize_direction": bool(self.optimize_direction_check.isChecked()),
            "optimize_elevation": bool(self.elevation_optimize_check.isChecked()),
            "output_dir": str(self.out_edit.text()).strip()
            or self._default_output_dir(),
        }

    def _apply_form_defaults(self, defaults: dict | None = None):
        defaults = defaults or {}

        metric_values = {
            "altitude": float(defaults.get("altitude", BASE_DEFAULTS["altitude"])),
            "safe_height": float(
                defaults.get("safe_height", BASE_DEFAULTS["safe_height"])
            ),
            "speed": float(defaults.get("speed", BASE_DEFAULTS["speed"])),
        }
        self._set_display_values_from_metric(metric_values)

        overlap = self._clamp_int(
            defaults.get("overlap", FORM_DEFAULTS["overlap"]),
            self.overlap_slider.minimum(),
            self.overlap_slider.maximum(),
        )
        self.overlap_slider.blockSignals(True)
        self.overlap_spin.blockSignals(True)
        self.overlap_slider.setValue(overlap)
        self.overlap_spin.setValue(overlap)
        self.overlap_slider.blockSignals(False)
        self.overlap_spin.blockSignals(False)

        margin = self._clamp_int(
            defaults.get("margin", FORM_DEFAULTS["margin"]),
            self.margin_slider.minimum(),
            self.margin_slider.maximum(),
        )
        self.margin_slider.blockSignals(True)
        self.margin_spin.blockSignals(True)
        self.margin_slider.setValue(margin)
        self.margin_spin.setValue(margin)
        self.margin_slider.blockSignals(False)
        self.margin_spin.blockSignals(False)

        drone = str(defaults.get("drone", FORM_DEFAULTS["drone"]))
        drone_idx = self.drone_combo.findText(drone)
        if drone_idx >= 0:
            self.drone_combo.setCurrentIndex(drone_idx)

        action = str(defaults.get("action", FORM_DEFAULTS["action"]))
        action_idx = self.action_combo.findData(action)
        if action_idx < 0:
            action_idx = self.action_combo.findText(action)
        if action_idx >= 0:
            self.action_combo.setCurrentIndex(action_idx)

        self.optimize_direction_check.setChecked(
            bool(
                defaults.get("optimize_direction", FORM_DEFAULTS["optimize_direction"])
            )
        )
        self.elevation_optimize_check.setChecked(
            bool(
                defaults.get("optimize_elevation", FORM_DEFAULTS["optimize_elevation"])
            )
        )

        out_dir = (
            str(defaults.get("output_dir", "")).strip() or self._default_output_dir()
        )
        self.out_edit.setText(out_dir)

        self.kmz_edit.clear()
        self.excluded_area_keys.clear()
        self.selected_start_area_key = None

    def _load_user_defaults(self):
        path = self._user_defaults_path()
        data = {}
        if path.exists():
            try:
                data = json.loads(path.read_text(encoding="utf-8"))
                if not isinstance(data, dict):
                    data = {}
            except Exception:
                data = {}

        theme = data.get("theme")
        if isinstance(theme, str) and theme in THEMES:
            self.theme = theme

        language = data.get("language")
        if isinstance(language, str) and language in LANGUAGES:
            self.language = language
            self.strings = LANGUAGES[self.language]

        units = data.get("units")
        if isinstance(units, str) and units in UNITS:
            self.units = units

        self._apply_unit_ranges()

        defaults_raw = data.get("defaults")
        form_defaults: dict[str, object] = (
            {str(k): v for k, v in defaults_raw.items()}
            if isinstance(defaults_raw, dict)
            else {}
        )
        last_output_dir = str(data.get("last_output_dir") or "").strip()
        if last_output_dir:
            form_defaults["output_dir"] = last_output_dir
        self._apply_form_defaults(form_defaults)

        merged_defaults = {**FORM_DEFAULTS, **BASE_DEFAULTS}
        if isinstance(form_defaults, dict):
            merged_defaults.update(form_defaults)

        self.user_defaults = {
            "theme": self.theme,
            "language": self.language,
            "units": self.units,
            "last_output_dir": str(
                merged_defaults.get("output_dir") or self._default_output_dir()
            ),
            "defaults": merged_defaults,
        }
        self._update_ui_text()

    def save_current_as_defaults(self):
        path = self._user_defaults_path()
        payload = {
            "theme": self.theme,
            "language": self.language,
            "units": self.units,
            "last_output_dir": str(self.out_edit.text()).strip()
            or self._default_output_dir(),
            "defaults": self._current_form_defaults(),
        }

        try:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(
                json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8"
            )
            self.user_defaults = payload
            self.status.showMessage(self._txt("save_defaults_status"), 4000)
            QtWidgets.QMessageBox.information(
                self,
                self._txt("success", "Success"),
                f"{self._txt('save_defaults_ok')}\n{path}",
            )
        except Exception as ex:
            QtWidgets.QMessageBox.critical(
                self,
                self._txt("error", "Error"),
                f"{self._txt('save_defaults_error')}\n{ex}",
            )

    def _has_network_access(self) -> bool:
        check_urls = [
            "https://router.project-osrm.org/",
            "https://unpkg.com/leaflet@1.9.4/dist/leaflet.js",
        ]
        for url in check_urls:
            try:
                req = urllib.request.Request(
                    url,
                    headers={"User-Agent": "LittleOne-NetCheck/1.0"},
                )
                with urllib.request.urlopen(req, timeout=2.5) as resp:
                    if int(getattr(resp, "status", 200)) < 500:
                        return True
            except Exception:
                continue

        try:
            socket.getaddrinfo("github.com", 443)
            return True
        except Exception:
            return False

    def _show_startup_connectivity_hint(self):
        if self._startup_offline_hint_shown:
            return
        if self._has_network_access():
            return

        self._startup_offline_hint_shown = True
        self.logln(self._txt("offline_log"))
        QtWidgets.QMessageBox.information(
            self,
            self.strings.get("offline_notice_title", "Offline-Hinweis"),
            self.strings.get(
                "offline_notice_message",
                "Keine Internetverbindung erkannt.\n\nDie Konvertierung von KMZ/KML funktioniert weiterhin.\nKartenansicht und Tagesplan-Routing sind offline eingeschränkt.",
            ),
        )

    def _update_action_buttons_layout(self):
        if not hasattr(self, "action_buttons") or not self.action_buttons:
            return
        panel_width = (
            self.input_panel.width() if hasattr(self, "input_panel") else self.width()
        )
        available_width = max(0, panel_width - 16)

        def _apply_row(buttons, row_layout):
            button_count = len(buttons)
            if button_count <= 0:
                return

            large_button_width = 140
            min_button_width = 72
            max_button_width = 220

            content_widths = []
            desired_widths = []
            for btn in buttons:
                text_width = btn.fontMetrics().horizontalAdvance(btn.text())
                content_width = max(
                    min_button_width, min(max_button_width, text_width + 36)
                )
                content_widths.append(content_width)
                desired_widths.append(max(large_button_width, content_width))

            spacing_value = 10
            min_total = sum(content_widths) + spacing_value * (button_count - 1)
            for candidate_spacing in (10, 8, 6, 4):
                candidate_total = sum(content_widths) + candidate_spacing * (
                    button_count - 1
                )
                if candidate_total <= available_width:
                    spacing_value = candidate_spacing
                    min_total = candidate_total
                    break

            desired_total = sum(desired_widths) + spacing_value * (button_count - 1)

            if desired_total <= available_width:
                target_widths = desired_widths
            elif min_total <= available_width:
                extra_width = available_width - min_total
                demands = [
                    max(0, desired_widths[i] - content_widths[i])
                    for i in range(button_count)
                ]
                demand_total = sum(demands)

                if demand_total <= 0:
                    target_widths = content_widths
                else:
                    additions = [
                        int(extra_width * demand / demand_total) for demand in demands
                    ]
                    remainder = extra_width - sum(additions)
                    for i in range(remainder):
                        additions[i % button_count] += 1
                    target_widths = [
                        content_widths[i] + additions[i] for i in range(button_count)
                    ]
            else:
                width_per_button = max(
                    min_button_width,
                    (available_width - spacing_value * (button_count - 1))
                    // button_count,
                )
                target_widths = [width_per_button for _ in buttons]

            if row_layout is not None:
                row_layout.setSpacing(spacing_value)

            for i, btn in enumerate(buttons):
                btn.setFixedWidth(target_widths[i])

        _apply_row(
            getattr(self, "top_action_buttons", []),
            getattr(self, "top_action_button_layout", None),
        )
        _apply_row(
            getattr(self, "bottom_action_buttons", []),
            getattr(self, "bottom_action_button_layout", None),
        )

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
        save_defaults_action = settings_menu.addAction(
            self._txt("save_defaults_action")
        )
        save_defaults_action.triggered.connect(self.save_current_as_defaults)

        settings_menu.addSeparator()
        update_action = settings_menu.addAction(self._txt("update_check_action"))
        update_action.triggered.connect(self.check_for_updates)

        # Help menu
        help_menu = menubar.addMenu(self.strings["help"])

        # Documentation
        help_menu.addSeparator()
        doc_action = help_menu.addAction(
            self.strings.get("documentation", "Dokumentation")
        )
        doc_action.triggered.connect(self.open_documentation)

        # GitHub
        github_action = help_menu.addAction(self._txt("help_github"))
        github_action.triggered.connect(self.open_github)

        # About
        help_menu.addSeparator()
        about_action = help_menu.addAction(self.strings["about"])
        about_action.triggered.connect(self.show_about)

        # Easter Egg
        easter_action = help_menu.addAction(self._txt("help_easter"))
        easter_action.triggered.connect(self.open_easter_egg)

    def open_easter_egg(self):
        """Open the ultimate best help source"""
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
            padding: 8px 14px;
            font-weight: 600;
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
        current_action = str(self.action_combo.currentData() or "").strip() or None
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
        self._populate_action_combo(current_action)

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
        self.convert_upload_btn.setText(
            self._txt("convert_upload", "Konvertieren und Hochladen")
        )
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

        self._update_action_buttons_layout()

        # Refresh map texts in embedded map HTML (title/controls in white overlay)
        self._refresh_map_language_texts()

    def changeEvent(self, event):
        super().changeEvent(event)
        if event.type() == QtCore.QEvent.Type.WindowStateChange:
            self._update_map_panel_visibility()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self._update_map_panel_visibility()
        self._update_action_buttons_layout()

    def show_about(self):
        QtWidgets.QMessageBox.information(
            self,
            self.strings["about"],
            self._txt("about_text"),
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
                    f"{self._txt('doc_open_error')}\n{str(e)}",
                )
        else:
            QtWidgets.QMessageBox.information(
                self,
                self.strings.get("documentation", "Dokumentation"),
                self._txt("doc_not_found"),
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
                self._txt("github_open_error").format(error=str(e), url=github_url),
            )

    def _parse_version(self, text: str):
        nums = [int(n) for n in re.findall(r"\d+", str(text))[:4]]
        while len(nums) < 4:
            nums.append(0)
        return tuple(nums)

    def _is_ssl_cert_error(self, ex: Exception) -> bool:
        text = str(ex).lower()
        if (
            "certificate_verify_failed" in text
            or "unable to get local issuer certificate" in text
        ):
            return True

        reason = getattr(ex, "reason", None)
        if reason:
            rtext = str(reason).lower()
            if (
                "certificate_verify_failed" in rtext
                or "unable to get local issuer certificate" in rtext
            ):
                return True

        return False

    def _fetch_latest_release_via_powershell(self):
        api_url = f"https://api.github.com/repos/{GITHUB_REPO}/releases/latest"
        safe_url = api_url.replace("'", "''")
        script = (
            "$ErrorActionPreference='Stop';"
            "$ProgressPreference='SilentlyContinue';"
            "[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12;"
            "$headers=@{Accept='application/vnd.github+json';'User-Agent'='LittleOne-Updater'};"
            "$resp=Invoke-WebRequest -Uri '"
            + safe_url
            + "' -Headers $headers -Method Get -UseBasicParsing -TimeoutSec 20;"
            "$content=[string]$resp.Content;"
            "if ([string]::IsNullOrWhiteSpace($content)) { throw 'GitHub API returned empty response content.' };"
            "[Console]::Out.Write($content)"
        )

        proc = subprocess.run(
            [
                "powershell",
                "-NoProfile",
                "-ExecutionPolicy",
                "Bypass",
                "-Command",
                script,
            ],
            capture_output=True,
            text=True,
            timeout=30,
        )

        if proc.returncode != 0:
            stderr = (proc.stderr or "").strip()
            stdout = (proc.stdout or "").strip()
            raise RuntimeError(stderr or stdout or "PowerShell release request failed")

        payload = (proc.stdout or "").strip()
        if not payload:
            raise RuntimeError("PowerShell release request returned empty response")

        try:
            return json.loads(payload)
        except json.JSONDecodeError as ex:
            head = payload[:280]
            raise RuntimeError(
                f"PowerShell release response is not valid JSON: {ex}. Response head: {head}"
            )

    def _download_with_powershell(self, url: str, target: Path):
        safe_url = str(url).replace("'", "''")
        safe_target = str(target).replace("'", "''")
        script = (
            "$ErrorActionPreference='Stop';"
            "$ProgressPreference='SilentlyContinue';"
            "[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12;"
            "Invoke-WebRequest -Uri '"
            + safe_url
            + "' -OutFile '"
            + safe_target
            + "' -UseBasicParsing -TimeoutSec 300"
        )

        proc = subprocess.run(
            [
                "powershell",
                "-NoProfile",
                "-ExecutionPolicy",
                "Bypass",
                "-Command",
                script,
            ],
            capture_output=True,
            text=True,
            timeout=330,
        )

        if proc.returncode != 0:
            stderr = (proc.stderr or "").strip()
            stdout = (proc.stdout or "").strip()
            raise RuntimeError(stderr or stdout or "PowerShell download failed")

        if not target.exists() or target.stat().st_size == 0:
            raise RuntimeError("Downloaded update file is missing or empty")

    def _fetch_latest_release(self):
        api_url = f"https://api.github.com/repos/{GITHUB_REPO}/releases/latest"
        req = urllib.request.Request(
            api_url,
            headers={
                "Accept": "application/vnd.github+json",
                "User-Agent": "LittleOne-Updater",
            },
        )
        try:
            with urllib.request.urlopen(req, timeout=12) as resp:
                data = resp.read().decode("utf-8", errors="replace")
            return json.loads(data)
        except urllib.error.URLError as ex:
            if sys.platform == "win32" and self._is_ssl_cert_error(ex):
                return self._fetch_latest_release_via_powershell()
            raise

    def _pick_windows_asset(self, release_json):
        assets = release_json.get("assets") or []
        exe_assets = [
            a for a in assets if str(a.get("name", "")).lower().endswith(".exe")
        ]
        if not exe_assets:
            return None

        def _rank(asset):
            name = str(asset.get("name", "")).lower()
            if "setup" in name:
                return 0
            if "install" in name:
                return 1
            if "littleone" in name:
                return 2
            return 3

        preferred = sorted(
            exe_assets,
            key=lambda x: (_rank(x), len(str(x.get("name", "")))),
        )
        return preferred[0]

    def check_for_updates(self):
        try:
            self.status.showMessage(self._txt("update_checking"))
            QtCore.QCoreApplication.processEvents()

            release = self._fetch_latest_release()
            latest_tag = str(release.get("tag_name") or "").strip()
            latest_ver = self._parse_version(latest_tag)
            current_ver = self._parse_version(APP_VERSION)

            if latest_ver <= current_ver:
                QtWidgets.QMessageBox.information(
                    self,
                    self._txt("updates_title"),
                    self._txt("updates_up_to_date").format(version=APP_VERSION),
                )
                self.status.showMessage(self._txt("update_none_status"))
                return

            release_name = release.get("name") or latest_tag or "Neue Version"
            release_page = (
                release.get("html_url") or f"https://github.com/{GITHUB_REPO}/releases"
            )
            asset = self._pick_windows_asset(release)

            msg = self._txt("update_available_msg").format(
                release_name=release_name,
                current=APP_VERSION,
                latest=(latest_tag or "unknown"),
            )

            can_auto_install = bool(
                asset and getattr(sys, "frozen", False) and sys.platform == "win32"
            )
            if can_auto_install:
                msg += self._txt("update_prompt_install")
            else:
                msg += self._txt("update_prompt_open")

            btn = QtWidgets.QMessageBox.question(
                self,
                self._txt("update_available_title"),
                msg,
                QtWidgets.QMessageBox.StandardButton.Yes
                | QtWidgets.QMessageBox.StandardButton.No,
            )
            if btn != QtWidgets.QMessageBox.StandardButton.Yes:
                self.status.showMessage(self._txt("update_check_done"))
                return

            if can_auto_install:
                if asset is None:
                    webbrowser.open(release_page)
                    self.status.showMessage(self._txt("release_page_opened"))
                    return
                url = asset.get("browser_download_url")
                name = asset.get("name") or "LittleOne-Setup.exe"
                if not url:
                    webbrowser.open(release_page)
                    self.status.showMessage(self._txt("release_page_opened"))
                    return

                target = Path(tempfile.gettempdir()) / name
                self.status.showMessage(self._txt("update_downloading"))
                QtCore.QCoreApplication.processEvents()
                try:
                    urllib.request.urlretrieve(url, str(target))
                except urllib.error.URLError as ex:
                    if sys.platform == "win32" and self._is_ssl_cert_error(ex):
                        self._download_with_powershell(url, target)
                    else:
                        raise

                QtWidgets.QMessageBox.information(
                    self,
                    self._txt("update_available_title"),
                    self._txt("update_downloaded"),
                )
                subprocess.Popen([str(target)])
                QtWidgets.QApplication.quit()
                return

            webbrowser.open(release_page)
            self.status.showMessage(self._txt("release_page_opened"))
        except urllib.error.HTTPError as ex:
            if ex.code == 404:
                QtWidgets.QMessageBox.information(
                    self,
                    self._txt("updates_title"),
                    self._txt("update_no_release"),
                )
                self.status.showMessage(self._txt("update_no_release_status"))
            else:
                QtWidgets.QMessageBox.warning(
                    self,
                    self._txt("update_error_title"),
                    self._txt("update_error_http").format(
                        code=ex.code, reason=ex.reason
                    ),
                )
                self.status.showMessage(self._txt("update_error_status"))
        except urllib.error.URLError as ex:
            extra = ""
            if self._is_ssl_cert_error(ex):
                extra = self._txt("update_error_ssl_hint")
            QtWidgets.QMessageBox.warning(
                self,
                self._txt("update_error_title"),
                f"{self._txt('update_error_http').format(code='-', reason=ex)}{extra}",
            )
            self.status.showMessage(self._txt("update_error_status"))
        except Exception as ex:
            QtWidgets.QMessageBox.warning(
                self,
                self._txt("update_error_title"),
                self._txt("update_error_generic").format(error=ex),
            )
            self.status.showMessage(self._txt("update_error_status"))

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
            self.selected_start_area_key = None

    def pick_out(self):
        dir_ = QtWidgets.QFileDialog.getExistingDirectory(
            self,
            self._txt("pick_output_dir", "Select output folder"),
            str(Path(self.out_edit.text().strip() or self._default_output_dir())),
        )
        if dir_:
            self.out_edit.setText(dir_)
            self._remember_output_dir(dir_)

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

    def _optimize_visit_order(self, matrix, fixed_start: int | None = None):
        n = len(matrix)
        if n <= 1:
            return [0]

        best_order = None
        best_cost = float("inf")
        starts = (
            [int(fixed_start)]
            if fixed_start is not None and 0 <= int(fixed_start) < n
            else list(range(n))
        )
        for start in starts:
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

    def _geocode_address(self, address: str):
        query = (address or "").strip()
        if not query:
            raise ValueError("Leere Adresse")

        params = urllib.parse.urlencode(
            {
                "q": query,
                "format": "json",
                "limit": "1",
                "addressdetails": "0",
            }
        )
        req = urllib.request.Request(
            f"https://nominatim.openstreetmap.org/search?{params}",
            headers={"User-Agent": "LittleOne-DayPlan/1.0"},
        )
        with urllib.request.urlopen(req, timeout=14) as resp:
            payload = resp.read().decode("utf-8", errors="replace")
        data = json.loads(payload)
        if not isinstance(data, list) or not data:
            raise ValueError(self._txt("geocode_not_found", "Address not found"))

        hit = data[0]
        lat = float(hit.get("lat"))
        lon = float(hit.get("lon"))
        name = str(hit.get("display_name") or query).strip()
        return (lon, lat), name

    def _ask_day_plan_start(self):
        dialog = QtWidgets.QDialog(self)
        dialog.setWindowTitle(self.strings.get("day_plan", "Tagesplan"))
        dialog.resize(560, 210)

        layout = QtWidgets.QVBoxLayout(dialog)
        label = QtWidgets.QLabel(self._txt("day_plan_start_info"))
        label.setWordWrap(True)
        layout.addWidget(label)

        edit = QtWidgets.QLineEdit()
        edit.setPlaceholderText(self._txt("day_plan_start_placeholder"))
        layout.addWidget(edit)

        hint = QtWidgets.QLabel(self._txt("day_plan_start_hint"))
        hint.setWordWrap(True)
        hint.setStyleSheet("color: #666;")
        layout.addWidget(hint)

        buttons = QtWidgets.QDialogButtonBox(
            QtWidgets.QDialogButtonBox.StandardButton.Ok
            | QtWidgets.QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)
        layout.addWidget(buttons)

        if dialog.exec() != int(QtWidgets.QDialog.DialogCode.Accepted):
            return {"cancelled": True, "address": ""}

        return {"cancelled": False, "address": edit.text().strip()}

    def _ask_day_plan_options(self):
        dialog = QtWidgets.QDialog(self)
        dialog.setWindowTitle(
            self.strings.get("day_plan", "Tagesplan")
            + " – "
            + self._txt("day_plan_options_title_suffix", "Options")
        )
        dialog.resize(540, 280)

        layout = QtWidgets.QVBoxLayout(dialog)
        info = QtWidgets.QLabel(self._txt("day_plan_options_info"))
        info.setWordWrap(True)
        layout.addWidget(info)

        drive_check = QtWidgets.QCheckBox(self._txt("day_plan_opt_drive"))
        drive_check.setChecked(True)
        layout.addWidget(drive_check)

        total_check = QtWidgets.QCheckBox(self._txt("day_plan_opt_total"))
        total_check.setChecked(True)
        layout.addWidget(total_check)

        hint = QtWidgets.QLabel(self._txt("day_plan_options_hint"))
        hint.setWordWrap(True)
        hint.setStyleSheet("color: #666;")
        layout.addWidget(hint)

        buttons = QtWidgets.QDialogButtonBox(
            QtWidgets.QDialogButtonBox.StandardButton.Ok
            | QtWidgets.QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)
        layout.addWidget(buttons)

        if dialog.exec() != int(QtWidgets.QDialog.DialogCode.Accepted):
            return {"cancelled": True}

        return {
            "cancelled": False,
            "include_drive": bool(drive_check.isChecked()),
            "include_total_duration": bool(total_check.isChecked()),
            "include_kitz_time": True,
        }

    def _fundort_csv_path(self) -> Path:
        return (
            Path(__file__).resolve().parents[1]
            / "data"
            / "Locations"
            / "Rehkitz_Fundort.csv"
        )

    def _parse_year_value(self, row: dict) -> int | None:
        year_raw = str(row.get("Jahr") or "").strip()
        if year_raw:
            m = re.search(r"\d{4}", year_raw)
            if m:
                try:
                    return int(m.group(0))
                except Exception:
                    pass

        date_raw = str(row.get("Funddatum") or "").strip()
        if not date_raw:
            return None

        formats = [
            "%m/%d/%Y %I:%M:%S %p",
            "%m/%d/%Y %I:%M %p",
            "%m/%d/%Y",
            "%Y-%m-%d %H:%M:%S",
            "%Y-%m-%d",
            "%d.%m.%Y %H:%M:%S",
            "%d.%m.%Y %H:%M",
            "%d.%m.%Y",
        ]
        for fmt in formats:
            try:
                return int(datetime.strptime(date_raw, fmt).year)
            except Exception:
                continue

        m = re.search(r"\b(20\d{2})\b", date_raw)
        if m:
            return int(m.group(1))
        return None

    def _to_float(self, value, default=0.0) -> float:
        try:
            return float(value)
        except Exception:
            return float(default)

    def _to_int(self, value, default=0) -> int:
        try:
            return int(float(value))
        except Exception:
            return int(default)

    def _polygon_area_ha(self, geom) -> float:
        from shapely.geometry import Polygon, MultiPolygon

        def ring_area_m2(coords, lat0_rad: float) -> float:
            if not coords:
                return 0.0
            radius = 6371008.8
            pts = []
            for lon, lat in coords:
                x = radius * math.radians(float(lon)) * math.cos(lat0_rad)
                y = radius * math.radians(float(lat))
                pts.append((x, y))
            if pts[0] != pts[-1]:
                pts.append(pts[0])

            area2 = 0.0
            for i in range(len(pts) - 1):
                x1, y1 = pts[i]
                x2, y2 = pts[i + 1]
                area2 += (x1 * y2) - (x2 * y1)
            return abs(area2) * 0.5

        def poly_area_m2(poly: Polygon) -> float:
            c = poly.centroid
            lat0_rad = math.radians(float(c.y))
            outer = ring_area_m2(list(poly.exterior.coords), lat0_rad)
            holes = sum(
                ring_area_m2(list(r.coords), lat0_rad) for r in list(poly.interiors)
            )
            return max(0.0, outer - holes)

        if geom is None:
            return 0.0
        if isinstance(geom, Polygon):
            return poly_area_m2(geom) / 10000.0
        if isinstance(geom, MultiPolygon):
            return sum(poly_area_m2(p) for p in geom.geoms) / 10000.0
        return 0.0

    def _work_time_factors_for_area(self, area_ha: float) -> tuple[float, float]:
        area = float(area_ha)
        if area < 1.0:
            return 2.0, 5.0
        if area < 5.0:
            return 1.5, 7.0
        return 1.2, 10.0

    def _kitz_time_minutes_for_area(self, area_ha: float, avg_kitz: float) -> float:
        avg = max(0.0, float(avg_kitz))
        if avg <= 0.0:
            return 0.0

        _, first_kitz_min = self._work_time_factors_for_area(area_ha)
        add_per_extra = 2.0 if float(area_ha) < 5.0 else 5.0
        extra_kitz = max(0.0, avg - 1.0)
        return float(first_kitz_min) + (extra_kitz * add_per_extra)

    def _load_kitz_points(self, csv_path: Path):
        points = []
        years = set()

        if not csv_path.exists():
            return points, []

        with csv_path.open("r", encoding="utf-8-sig", newline="") as f:
            reader = csv.DictReader(f)
            for row in reader:
                lon = self._to_float(row.get("x"), default=float("nan"))
                lat = self._to_float(row.get("y"), default=float("nan"))
                if not (math.isfinite(lon) and math.isfinite(lat)):
                    continue

                year = self._parse_year_value(row)
                if year is None:
                    continue

                count = self._to_int(row.get("Anzahl Kitze am Fundort"), default=0)
                if count < 0:
                    count = 0

                points.append(
                    {
                        "lon": float(lon),
                        "lat": float(lat),
                        "year": int(year),
                        "count": int(count),
                    }
                )
                years.add(int(year))

        return points, sorted(years)

    def _kitz_stats_by_entry(self, entries, csv_path: Path):
        from shapely.geometry import Point

        points, years = self._load_kitz_points(csv_path)
        out = {
            "years": years,
            "csv_path": str(csv_path),
            "csv_exists": bool(csv_path.exists()),
            "by_key": {},
        }

        for entry in entries:
            key = str(entry.get("key"))
            geom = entry.get("geom")
            area_ha = self._polygon_area_ha(geom)
            yearly = {int(y): 0 for y in years}
            point_hits = 0

            if geom is not None:
                for item in points:
                    pt = Point(float(item["lon"]), float(item["lat"]))
                    if geom.covers(pt):
                        y = int(item["year"])
                        yearly[y] = int(yearly.get(y, 0)) + int(item["count"])
                        point_hits += 1

            positive_values = [v for v in yearly.values() if v > 0]
            avg_kitz = (
                float(sum(positive_values)) / float(len(positive_values))
                if positive_values
                else 0.0
            )

            out["by_key"][key] = {
                "area_ha": float(area_ha),
                "yearly": yearly,
                "avg_kitz": float(avg_kitz),
                "point_hits": int(point_hits),
            }

        return out

    def _compute_area_time_estimates(
        self,
        entries,
        flight_by_key: dict,
        kitz_stats: dict | None,
        include_kitz_time: bool,
    ):
        kitz_by_key = (kitz_stats or {}).get("by_key", {})
        years = (kitz_stats or {}).get("years", [])

        area_estimates = {}
        total_adjusted_flight_time_s = 0.0
        total_kitz_time_s = 0.0
        total_area_time_s = 0.0

        for entry in entries:
            key = entry["key"]
            f_time_s = float(flight_by_key.get(key, {}).get("time_s", 0.0))
            kitz_row = kitz_by_key.get(key, {})
            area_ha = float(
                kitz_row.get("area_ha", self._polygon_area_ha(entry.get("geom")))
            )
            yearly = dict(kitz_row.get("yearly") or {})
            avg_kitz = float(kitz_row.get("avg_kitz", 0.0))
            points_in_poly = int(kitz_row.get("point_hits", 0))

            multiplier, min_per_kitz = self._work_time_factors_for_area(area_ha)
            adjusted_flight_s = f_time_s * float(multiplier)
            add_per_extra_kitz = 2.0 if float(area_ha) < 5.0 else 5.0
            kitz_minutes_total = self._kitz_time_minutes_for_area(area_ha, avg_kitz)
            kitz_time_s = float(kitz_minutes_total) * 60.0 if include_kitz_time else 0.0
            area_total_s = adjusted_flight_s + kitz_time_s

            total_adjusted_flight_time_s += adjusted_flight_s
            total_kitz_time_s += kitz_time_s
            total_area_time_s += area_total_s

            area_estimates[key] = {
                "area_ha": float(area_ha),
                "flight_multiplier": float(multiplier),
                "kitz_minutes_per_item": float(min_per_kitz),
                "kitz_extra_minutes_per_item": float(add_per_extra_kitz),
                "kitz_minutes_total": float(kitz_minutes_total),
                "yearly": yearly,
                "years": [int(y) for y in years],
                "avg_kitz": float(avg_kitz),
                "points_in_polygon": int(points_in_poly),
                "flight_time_s": float(f_time_s),
                "adjusted_flight_time_s": float(adjusted_flight_s),
                "kitz_time_s": float(kitz_time_s),
                "area_total_time_s": float(area_total_s),
            }

        return {
            "area_estimates_by_key": area_estimates,
            "kitz_years": [int(y) for y in years],
            "total_adjusted_flight_time_s": float(total_adjusted_flight_time_s),
            "total_kitz_time_s": float(total_kitz_time_s),
            "total_area_time_s": float(total_area_time_s),
        }

    def _estimate_flight_times(self, active_entries):
        optimizer = optimize_angle_mod
        if optimizer is None or not hasattr(optimizer, "mapping_preview"):
            return {}

        def _num(value, default=0.0):
            try:
                return float(value)
            except Exception:
                return float(default)

        metric_values = self._get_metric_values()
        result = {}
        for entry in active_entries:
            try:
                preview = optimizer.mapping_preview(
                    entry["geom"],
                    altitude_m=float(metric_values["altitude"]),
                    side_overlap_percent=float(self.overlap_spin.value()),
                    speed_mps=float(metric_values["speed"]),
                    drone=self.drone_combo.currentText(),
                )
                result[entry["key"]] = {
                    "time_s": _num(preview.get("time_s", 0.0)),
                    "distance_m": _num(preview.get("distance_m", 0.0)),
                    "line_count": _num(preview.get("line_count", 0.0)),
                }
            except Exception:
                result[entry["key"]] = {
                    "time_s": 0.0,
                    "distance_m": 0.0,
                    "line_count": 0.0,
                }
        return result

    def _build_day_plan(
        self,
        entries,
        start_area_key: str | None = None,
        start_home_lonlat=None,
        start_home_label: str | None = None,
        include_drive: bool = True,
        include_total_duration: bool = True,
        include_kitz_time: bool = True,
        kitz_stats: dict | None = None,
    ):
        active_entries = [
            entry for entry in entries if entry["key"] not in self.excluded_area_keys
        ]
        if not active_entries:
            return None

        matrix_source = "none"
        distances = [[0.0 for _ in active_entries] for _ in active_entries]
        index_by_key = {entry["key"]: idx for idx, entry in enumerate(active_entries)}

        if include_drive:
            points_lonlat = [
                (float(entry["center"][1]), float(entry["center"][0]))
                for entry in active_entries
            ]
            durations, distances, matrix_source = self._build_drive_matrix(
                points_lonlat
            )
            fixed_start = (
                index_by_key.get(start_area_key)
                if start_area_key in index_by_key
                else None
            )
            order = self._optimize_visit_order(durations, fixed_start=fixed_start)
        else:
            order = list(range(len(active_entries)))
            if start_area_key in index_by_key:
                first_idx = index_by_key[start_area_key]
                order = [first_idx] + [idx for idx in order if idx != first_idx]

        ordered_entries = [active_entries[idx] for idx in order]
        sequence_by_key = {
            entry["key"]: idx + 1 for idx, entry in enumerate(ordered_entries)
        }

        flight_by_key = self._estimate_flight_times(active_entries)
        total_flight_time_s = sum(
            float(flight_by_key.get(entry["key"], {}).get("time_s", 0.0))
            for entry in ordered_entries
        )
        total_flight_distance_m = sum(
            float(flight_by_key.get(entry["key"], {}).get("distance_m", 0.0))
            for entry in ordered_entries
        )

        segments = []
        total_distance_m = 0.0
        total_duration_s = 0.0

        home_start_segment = None
        if include_drive and start_home_lonlat is not None and ordered_entries:
            first = ordered_entries[0]
            first_pt = (float(first["center"][1]), float(first["center"][0]))
            home_start_segment = self._segment_route(start_home_lonlat, first_pt)
            total_distance_m += float(home_start_segment["distance_m"])
            total_duration_s += float(home_start_segment["duration_s"])
            segments.append(
                {
                    "from_key": "__home__",
                    "to_key": first["key"],
                    "from_label": str(
                        start_home_label
                        or self._txt("day_plan_start_home_prefix", "Home")
                    ),
                    "to_label": first["label"],
                    "duration_s": float(home_start_segment["duration_s"]),
                    "distance_m": float(home_start_segment["distance_m"]),
                    "line": home_start_segment["line"],
                    "source": home_start_segment["source"],
                }
            )

        if include_drive:
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

        area_payload = self._compute_area_time_estimates(
            entries=ordered_entries,
            flight_by_key=flight_by_key,
            kitz_stats=kitz_stats,
            include_kitz_time=include_kitz_time,
        )
        area_estimates = area_payload.get("area_estimates_by_key", {}) or {}
        total_adjusted_flight_time_s = float(
            area_payload.get("total_adjusted_flight_time_s", 0.0)
        )
        total_kitz_time_s = float(area_payload.get("total_kitz_time_s", 0.0))
        total_area_time_s = float(area_payload.get("total_area_time_s", 0.0))
        years = [int(y) for y in (area_payload.get("kitz_years") or [])]

        total_work_time_s = total_area_time_s + (
            total_duration_s if include_drive else 0.0
        )

        return {
            "matrix_source": matrix_source,
            "options": {
                "include_drive": bool(include_drive),
                "include_total_duration": bool(include_total_duration),
                "include_kitz_time": bool(include_kitz_time),
            },
            "sequence_by_key": sequence_by_key,
            "ordered_keys": [entry["key"] for entry in ordered_entries],
            "ordered_labels": [entry["label"] for entry in ordered_entries],
            "segments": segments,
            "total_distance_m": total_distance_m,
            "total_duration_s": total_duration_s,
            "total_flight_time_s": float(total_flight_time_s),
            "total_adjusted_flight_time_s": float(total_adjusted_flight_time_s),
            "total_kitz_time_s": float(total_kitz_time_s),
            "total_area_time_s": float(total_area_time_s),
            "total_work_time_s": float(total_work_time_s),
            "total_flight_distance_m": float(total_flight_distance_m),
            "flight_by_key": flight_by_key,
            "area_estimates_by_key": area_estimates,
            "kitz_years": [int(y) for y in years],
            "start_area_key": (
                start_area_key if start_area_key in index_by_key else None
            ),
            "start_home_label": (
                str(start_home_label or "") if start_home_lonlat else ""
            ),
            "start_home_lonlat": (
                [float(start_home_lonlat[0]), float(start_home_lonlat[1])]
                if start_home_lonlat
                else None
            ),
            "matrix_distance_hint_m": float(self._path_cost(order, distances)),
        }

    def set_start_area(self, area_key: str):
        area_key = str(area_key or "").strip()
        if not area_key:
            return
        self.selected_start_area_key = area_key
        self.logln(self._txt("map_start_set_log").format(key=area_key))

    def toggle_area_exclusion(self, area_key: str):
        if area_key in self.excluded_area_keys:
            self.excluded_area_keys.remove(area_key)
            self.logln(self._txt("map_area_reenabled_log").format(key=area_key))
        else:
            self.excluded_area_keys.add(area_key)
            if self.selected_start_area_key == area_key:
                self.selected_start_area_key = None
            self.logln(self._txt("map_area_excluded_log").format(key=area_key))

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
        selected_start_area_key: str | None = None,
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
            self._txt("map_remove_area", "Remove area"),
            ensure_ascii=False,
        )
        add_label = json.dumps(
            self._txt("map_readd_area", "Include area again"),
            ensure_ascii=False,
        )
        start_label = json.dumps(
            self._txt("map_set_start_area", "Set as start area"),
            ensure_ascii=False,
        )
        start_selected_label = json.dumps(
            self._txt("map_start_area_selected", "Start area selected"),
            ensure_ascii=False,
        )
        start_replace_label = json.dumps(
            self._txt("map_set_new_start_area", "Set this area as new start point"),
            ensure_ascii=False,
        )
        start_key_json = json.dumps(selected_start_area_key, ensure_ascii=False)
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
        const setStartLabel = {start_label};
        const selectedStartLabel = {start_selected_label};
        const setNewStartLabel = {start_replace_label};
        let selectedStartKey = {start_key_json};
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
                const isStart = selectedStartKey && selectedStartKey === feature.key;
                const hasOtherStart = !!selectedStartKey && !isStart;
                const startButtonLabel = isStart
                    ? selectedStartLabel
                    : (hasOtherStart ? setNewStartLabel : setStartLabel);
                const startButtonColor = isStart ? '#455a64' : '#1565c0';
                let infoBlocks = [];
                if (feature.kitz_show && feature.kitz_yearly && typeof feature.kitz_yearly === 'object') {{
                    const years = Object.keys(feature.kitz_yearly)
                        .map(x => Number(x))
                        .filter(x => Number.isFinite(x))
                        .sort((a, b) => a - b);
                    const rows = [];
                    for (const year of years) {{
                        const val = Number(feature.kitz_yearly[String(year)] ?? feature.kitz_yearly[year] ?? 0);
                        rows.push(String(year) + ': ' + String(Math.max(0, Math.round(val))) + ' Kitze');
                    }}
                    const avg = Number(feature.kitz_avg || 0);
                    const areaHa = Number(feature.area_ha || 0);
                    if (rows.length > 0) {{
                        infoBlocks.push('<b>Kitzfunde im Polygon</b><br>' + rows.map(escapeHtml).join('<br>') +
                            '<br>Ø Kitze: ' + escapeHtml(avg.toFixed(2)) +
                            '<br>Fläche: ' + escapeHtml(areaHa.toFixed(2)) + ' ha');
                    }}
                }}

                if (feature.time_show) {{
                    const flightMin = Number(feature.flight_time_min || 0);
                    const factor = Number(feature.flight_factor || 1);
                    const adjFlightMin = Number(feature.adjusted_flight_min || 0);
                    const kitzMin = Number(feature.kitz_time_min || 0);
                    const kitzBaseMin = Number(feature.kitz_minutes_per_item || 0);
                    const kitzExtraMin = Number(feature.kitz_extra_minutes_per_item || 0);
                    const kitzTotalCalcMin = Number(feature.kitz_minutes_total || 0);
                    const totalMin = Number(feature.processing_total_min || 0);
                    const avgKitz = Number(feature.kitz_avg || 0);
                    infoBlocks.push(
                        '<b>Zeitabschätzung Fläche</b><br>' +
                        'Flugzeit: ' + escapeHtml(flightMin.toFixed(1)) + ' min<br>' +
                        'Faktor: ' + escapeHtml(factor.toFixed(1)) +
                        ' → Flug bereinigt: ' + escapeHtml(adjFlightMin.toFixed(1)) + ' min<br>' +
                        'Kitzzeit: 1. Kitz ' + escapeHtml(kitzBaseMin.toFixed(1)) + ' min' +
                        ' + ab 2. Kitz ' + escapeHtml(kitzExtraMin.toFixed(1)) + ' min' +
                        ' (Ø ' + escapeHtml(avgKitz.toFixed(2)) + ' Kitze)' +
                        ' = ' + escapeHtml((kitzTotalCalcMin || kitzMin).toFixed(1)) + ' min<br>' +
                        '<b>Bearbeitung gesamt: ' + escapeHtml(totalMin.toFixed(1)) + ' min</b>'
                    );
                }}

                const extraInfo = infoBlocks.length > 0 ? '<br><br>' + infoBlocks.join('<br><br>') : '';

                return `
                    <b>${{escapeHtml(feature.label)}}</b><br>
                    ${{escapeHtml(feature.applicant)}}${{extraInfo}}<br><br>
                    <button
                        type="button"
                        class="toggle-area-btn"
                        data-key="${{encodeURIComponent(feature.key)}}"
                        style="padding:6px 10px;border:1px solid #555;border-radius:4px;cursor:pointer;color:white;background:${{actionColor}};"
                    >
                        ${{escapeHtml(actionLabel)}}
                    </button>
                    <button
                        type="button"
                        class="set-start-btn"
                        data-key="${{encodeURIComponent(feature.key)}}"
                        style="margin-left:8px;padding:6px 10px;border:1px solid #555;border-radius:4px;cursor:pointer;color:white;background:${{startButtonColor}};"
                    >
                        ${{escapeHtml(startButtonLabel)}}
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

            window.setStartArea = function(encodedKey) {{
                const key = decodeURIComponent(encodedKey);
                if (!featureByKey.has(key)) return;
                selectedStartKey = key;

                for (const [k, lyr] of layersByKey.entries()) {{
                    const feat = featureByKey.get(k);
                    if (!feat) continue;
                    lyr.setPopupContent(popupHtml(feat));
                }}

                if (bridge && typeof bridge.setStartArea === 'function') {{
                    bridge.setStartArea(key);
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
                    if (btn) {{
                        btn.onclick = function() {{
                            window.toggleArea(btn.dataset.key || '');
                        }};
                    }}
                    const startBtn = root.querySelector('.set-start-btn');
                    if (startBtn) {{
                        startBtn.onclick = function() {{
                            window.setStartArea(startBtn.dataset.key || '');
                        }};
                    }}
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
            selected_start_area_key=payload.get(
                "selected_start_area_key", self.selected_start_area_key
            ),
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
            "selected_start_area_key": self.selected_start_area_key,
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
            "selected_start_area_key": self.selected_start_area_key,
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
                    f"{self.strings.get('map_opened', 'Satellitenkarte geöffnet')}: {self._txt('map_opened_gui_suffix', 'GUI')}"
                )
            return

        if fallback_to_browser:
            webbrowser.open(html_path.resolve().as_uri())
            self.logln(self._txt("map_browser_fallback_opened"))

    def show_satellite_map(self):
        kmz_path = self._validate_input_path()
        if kmz_path is None:
            return

        ok, import_err = _ensure_engine_modules()
        if not ok:
            err_text = (
                f"{type(import_err).__name__}: {import_err}"
                if import_err
                else self._txt("engine_unknown_import_error")
            )
            self.logln(self._txt("engine_import_log").format(error=err_text))
            QtWidgets.QMessageBox.critical(
                self,
                self.strings["import_error"],
                self._txt("engine_load_failed").format(details=err_text),
            )
            return

        kmz = kmz_reader
        if kmz is None:
            QtWidgets.QMessageBox.critical(
                self,
                self.strings["import_error"],
                self._txt("engine_unavailable"),
            )
            return

        try:
            self.progress.setVisible(True)
            self.progress.setMaximum(0)
            self.progress.setValue(0)
            self.map_btn.setEnabled(False)
            self.day_plan_btn.setEnabled(False)
            self.convert_upload_btn.setEnabled(False)
            self.status.showMessage(self.strings.get("map_loading", "Lade Karte..."))
            self.logln(self.strings.get("map_loading", "Lade Karte..."))
            QtCore.QCoreApplication.processEvents()

            features = kmz.parse_kmz_to_area_features(str(kmz_path))
            summaries = kmz.summarize_features(features)
            entries = self._collect_geometry_entries(features, summaries)
            current_keys = {entry["key"] for entry in entries}
            self.excluded_area_keys.intersection_update(current_keys)
            if self.selected_start_area_key not in current_keys:
                self.selected_start_area_key = None

            csv_path = self._fundort_csv_path()
            kitz_stats = self._kitz_stats_by_entry(entries, csv_path)
            flight_by_key = self._estimate_flight_times(entries)
            area_payload = self._compute_area_time_estimates(
                entries=entries,
                flight_by_key=flight_by_key,
                kitz_stats=kitz_stats,
                include_kitz_time=True,
            )
            area_estimates_by_key = area_payload.get("area_estimates_by_key", {}) or {}

            map_items = [
                {
                    "applicant": entry["applicant"],
                    "label": entry["label"],
                    "rings": entry["rings"],
                    "key": entry["key"],
                    "excluded": entry["key"] in self.excluded_area_keys,
                    "center": entry.get("center"),
                    "kitz_show": True,
                    "kitz_yearly": (
                        area_estimates_by_key.get(entry["key"], {}).get("yearly", {})
                    ),
                    "kitz_avg": (
                        area_estimates_by_key.get(entry["key"], {}).get("avg_kitz", 0.0)
                    ),
                    "area_ha": (
                        area_estimates_by_key.get(entry["key"], {}).get("area_ha", 0.0)
                    ),
                    "time_show": True,
                    "flight_time_min": (
                        float(
                            area_estimates_by_key.get(entry["key"], {}).get(
                                "flight_time_s", 0.0
                            )
                        )
                        / 60.0
                    ),
                    "flight_factor": (
                        area_estimates_by_key.get(entry["key"], {}).get(
                            "flight_multiplier", 1.0
                        )
                    ),
                    "adjusted_flight_min": (
                        float(
                            area_estimates_by_key.get(entry["key"], {}).get(
                                "adjusted_flight_time_s", 0.0
                            )
                        )
                        / 60.0
                    ),
                    "kitz_minutes_per_item": (
                        area_estimates_by_key.get(entry["key"], {}).get(
                            "kitz_minutes_per_item", 0.0
                        )
                    ),
                    "kitz_extra_minutes_per_item": (
                        area_estimates_by_key.get(entry["key"], {}).get(
                            "kitz_extra_minutes_per_item", 0.0
                        )
                    ),
                    "kitz_minutes_total": (
                        area_estimates_by_key.get(entry["key"], {}).get(
                            "kitz_minutes_total", 0.0
                        )
                    ),
                    "kitz_time_min": (
                        float(
                            area_estimates_by_key.get(entry["key"], {}).get(
                                "kitz_time_s", 0.0
                            )
                        )
                        / 60.0
                    ),
                    "processing_total_min": (
                        float(
                            area_estimates_by_key.get(entry["key"], {}).get(
                                "area_total_time_s", 0.0
                            )
                        )
                        / 60.0
                    ),
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
                "selected_start_area_key": self.selected_start_area_key,
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
            self.logln(self._txt("map_error_log"))
            self.logln(tb)
            self.status.showMessage(self.strings["error"])
            QtWidgets.QMessageBox.critical(self, self.strings["error"], str(ex))
        finally:
            self.progress.setVisible(False)
            self.progress.setMaximum(100)
            self.progress.setValue(0)
            self.map_btn.setEnabled(True)
            self.day_plan_btn.setEnabled(True)
            self.convert_upload_btn.setEnabled(True)

    def _show_day_plan_window(self, entries, day_plan):
        dialog = QtWidgets.QDialog(self)
        dialog.setWindowTitle(self.strings.get("day_plan", "Tagesplan"))
        dialog.resize(700, 540)

        layout = QtWidgets.QVBoxLayout(dialog)
        start_home = str(day_plan.get("start_home_label") or "").strip()
        start_area_key = str(day_plan.get("start_area_key") or "").strip()
        start_desc = self._txt("day_plan_start_auto", "Automatic")
        if start_home:
            start_desc = (
                f"{self._txt('day_plan_start_home_prefix', 'Home')}: {start_home}"
            )
        elif start_area_key:
            start_desc = self._txt("day_plan_start_area", "Start area from map")

        opts = day_plan.get("options", {}) or {}
        include_drive = bool(opts.get("include_drive", True))
        include_kitz_time = bool(opts.get("include_kitz_time", True))

        header_parts = [
            f"{self._txt('day_plan_header_areas', 'Areas')}: {len(day_plan.get('ordered_keys', []))}",
            f"{self._txt('day_plan_header_flight_time', 'Flight time')}: {day_plan.get('total_flight_time_s', 0.0) / 60.0:.1f} min",
        ]
        if include_drive:
            header_parts.insert(
                1,
                f"{self._txt('day_plan_header_distance', 'Distance')}: {day_plan.get('total_distance_m', 0.0) / 1000.0:.2f} km",
            )
            header_parts.insert(
                2,
                f"{self._txt('day_plan_header_drive_time', 'Drive time')}: {day_plan.get('total_duration_s', 0.0) / 60.0:.1f} min",
            )
        header_parts.append(
            f"{self._txt('day_plan_header_total', 'Day mission')}: {day_plan.get('total_work_time_s', 0.0) / 60.0:.1f} min"
        )

        header = QtWidgets.QLabel(
            f"<b>{self.strings.get('day_plan', 'Tagesplan')}</b><br>"
            f"{' · '.join(header_parts)}"
            f"<br>{self._txt('day_plan_header_start', 'Start')}: {start_desc}"
        )
        header.setWordWrap(True)
        layout.addWidget(header)

        detail_box = QtWidgets.QPlainTextEdit()
        detail_box.setReadOnly(True)

        by_key = {entry["key"]: entry for entry in entries}
        flight_by_key = day_plan.get("flight_by_key", {}) or {}
        area_estimates = day_plan.get("area_estimates_by_key", {}) or {}
        lines = []
        for idx, key in enumerate(day_plan.get("ordered_keys", []), start=1):
            entry = by_key.get(key)
            if entry is None:
                continue
            lines.append(f"{idx}. {entry['label']} ({entry['applicant']})")

        if include_drive:
            lines.append("")
            lines.append(self._txt("day_plan_segments", "Drive segments:"))
            for idx, seg in enumerate(day_plan.get("segments", []), start=1):
                lines.append(
                    f"{idx}. {seg.get('from_label')} -> {seg.get('to_label')}"
                    f" | {float(seg.get('distance_m', 0.0)) / 1000.0:.2f} km"
                    f" | {float(seg.get('duration_s', 0.0)) / 60.0:.1f} min"
                )

        lines.append("")
        lines.append(
            self._txt("day_plan_timeline_drive", "Timeline (Drive + Flight):")
            if include_drive
            else self._txt("day_plan_timeline_flight", "Timeline (Flight):")
        )
        timeline_no = 1
        ordered_keys = day_plan.get("ordered_keys", [])
        segments = list(day_plan.get("segments", []) or [])
        area_segments = [
            seg
            for seg in segments
            if str(seg.get("to_key") or "") != ""
            and str(seg.get("to_key") or "") != "__home__"
        ]
        seg_idx = 0

        for pos, key in enumerate(ordered_keys, start=1):
            if (
                include_drive
                and seg_idx < len(area_segments)
                and str(area_segments[seg_idx].get("to_key")) == str(key)
            ):
                seg = area_segments[seg_idx]
                lines.append(
                    f"{timeline_no}. {self._txt('day_plan_step_drive', 'Drive')}: {seg.get('from_label')} -> {seg.get('to_label')}"
                    f" | {float(seg.get('duration_s', 0.0)) / 60.0:.1f} min"
                )
                timeline_no += 1
                seg_idx += 1

            entry = by_key.get(key)
            if entry is None:
                continue
            f_time_s = float(flight_by_key.get(key, {}).get("time_s", 0.0))
            f_dist_m = float(flight_by_key.get(key, {}).get("distance_m", 0.0))
            lines.append(
                f"{timeline_no}. {self._txt('day_plan_step_flight', 'Flight')}: {entry['label']}"
                f" | {f_dist_m / 1000.0:.2f} km"
                f" | {f_time_s / 60.0:.1f} min"
            )
            timeline_no += 1

            if include_drive and pos < len(ordered_keys):
                next_key = ordered_keys[pos]
                if (
                    seg_idx < len(area_segments)
                    and str(area_segments[seg_idx].get("from_key")) == str(key)
                    and str(area_segments[seg_idx].get("to_key")) == str(next_key)
                ):
                    seg = area_segments[seg_idx]
                    lines.append(
                        f"{timeline_no}. {self._txt('day_plan_step_drive', 'Drive')}: {seg.get('from_label')} -> {seg.get('to_label')}"
                        f" | {float(seg.get('duration_s', 0.0)) / 60.0:.1f} min"
                    )
                    timeline_no += 1
                    seg_idx += 1

        lines.append("")
        lines.append(self._txt("day_plan_area_processing", "Processing time per area:"))
        for idx, key in enumerate(ordered_keys, start=1):
            entry = by_key.get(key)
            estimate = area_estimates.get(key, {})
            if entry is None or not estimate:
                continue

            base = (
                f"{idx}. {entry['label']} | {float(estimate.get('area_ha', 0.0)):.2f} ha"
                f" | {self._txt('day_plan_label_factor', 'Factor')} {float(estimate.get('flight_multiplier', 1.0)):.1f}"
                f" | {self._txt('day_plan_label_flight_adjusted', 'Adjusted flight')} {float(estimate.get('adjusted_flight_time_s', 0.0)) / 60.0:.1f} min"
            )

            if include_kitz_time:
                years = [int(y) for y in (estimate.get("years") or [])]
                yearly = estimate.get("yearly") or {}
                year_bits = [f"{y}: {int(yearly.get(y, 0))}" for y in years]
                extra = (
                    f" | {self._txt('day_plan_label_avg_kitz', 'Avg fawns')} {float(estimate.get('avg_kitz', 0.0)):.2f}"
                    f" | {self._txt('day_plan_label_kitz_time', '+Fawn time')} {float(estimate.get('kitz_time_s', 0.0)) / 60.0:.1f} min"
                )
                if year_bits:
                    extra += (
                        " | "
                        + self._txt("day_plan_label_years", "Years")
                        + " "
                        + ", ".join(year_bits)
                    )
                lines.append(base + extra)
            else:
                lines.append(base)

        lines.append("")
        lines.append(
            f"{self._txt('day_plan_total_work', 'Total day mission')}: {float(day_plan.get('total_work_time_s', 0.0)) / 60.0:.1f} min"
        )
        if include_kitz_time:
            lines.append(
                f"  {self._txt('day_plan_total_kitz', 'of which fawn times')}: {float(day_plan.get('total_kitz_time_s', 0.0)) / 60.0:.1f} min"
            )

        source = str(day_plan.get("matrix_source", "geo")).upper()
        lines.append("")
        lines.append(
            f"{self._txt('day_plan_routing_source', 'Routing source')}: {source}"
        )
        if include_drive and source != "OSRM":
            lines.append(self._txt("day_plan_routing_fallback"))

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
                else self._txt("engine_unknown_import_error")
            )
            self.logln(self._txt("engine_import_log").format(error=err_text))
            QtWidgets.QMessageBox.critical(
                self,
                self.strings["import_error"],
                self._txt("engine_load_failed").format(details=err_text),
            )
            return

        kmz = kmz_reader
        if kmz is None:
            QtWidgets.QMessageBox.critical(
                self,
                self.strings["import_error"],
                self._txt("engine_unavailable"),
            )
            return

        try:
            self.progress.setVisible(True)
            self.progress.setMaximum(0)
            self.progress.setValue(0)
            self.day_plan_btn.setEnabled(False)
            self.map_btn.setEnabled(False)
            self.convert_btn.setEnabled(False)
            self.convert_upload_btn.setEnabled(False)
            self.status.showMessage(self._txt("day_plan_calc_status"))
            self.logln(self._txt("day_plan_calc_log"))
            QtCore.QCoreApplication.processEvents()

            features = kmz.parse_kmz_to_area_features(str(kmz_path))
            summaries = kmz.summarize_features(features)
            entries = self._collect_geometry_entries(features, summaries)
            current_keys = {entry["key"] for entry in entries}
            self.excluded_area_keys.intersection_update(current_keys)
            if self.selected_start_area_key not in current_keys:
                self.selected_start_area_key = None

            start_area_key = self.selected_start_area_key
            start_home_lonlat = None
            start_home_label = None
            plan_options = self._ask_day_plan_options()
            if plan_options.get("cancelled"):
                return

            if not start_area_key:
                start_choice = self._ask_day_plan_start()
                if start_choice.get("cancelled"):
                    return

                address = str(start_choice.get("address") or "").strip()
                if not address:
                    QtWidgets.QMessageBox.information(
                        self,
                        self.strings.get("day_plan", "Tagesplan"),
                        self._txt("day_plan_need_start"),
                    )
                    return

                try:
                    start_home_lonlat, start_home_label = self._geocode_address(address)
                    self.logln(
                        self._txt("day_plan_home_set").format(home=start_home_label)
                    )
                except Exception as ex:
                    QtWidgets.QMessageBox.warning(
                        self,
                        self.strings.get("error", "Fehler"),
                        self._txt("day_plan_home_error").format(error=ex),
                    )
                    return

            include_drive = bool(plan_options.get("include_drive", True))
            include_total_duration = bool(
                plan_options.get("include_total_duration", True)
            )
            include_kitz_time = bool(plan_options.get("include_kitz_time", True))

            csv_path = self._fundort_csv_path()
            kitz_stats = self._kitz_stats_by_entry(entries, csv_path)
            if not kitz_stats.get("csv_exists"):
                self.logln(self._txt("day_plan_csv_missing").format(path=csv_path))
            else:
                self.logln(
                    self._txt("day_plan_csv_loaded").format(
                        path=csv_path, years=len(kitz_stats.get("years", []))
                    )
                )

            day_plan = self._build_day_plan(
                entries,
                start_area_key=start_area_key,
                start_home_lonlat=start_home_lonlat,
                start_home_label=start_home_label,
                include_drive=include_drive,
                include_total_duration=include_total_duration,
                include_kitz_time=include_kitz_time,
                kitz_stats=kitz_stats,
            )
            if not day_plan or not day_plan.get("ordered_keys"):
                QtWidgets.QMessageBox.information(
                    self,
                    self.strings.get("day_plan", "Tagesplan"),
                    self._txt("day_plan_no_active_areas"),
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
                    "kitz_show": bool(include_kitz_time),
                    "kitz_yearly": (
                        (day_plan.get("area_estimates_by_key", {}) or {})
                        .get(entry["key"], {})
                        .get("yearly", {})
                    ),
                    "kitz_avg": (
                        (day_plan.get("area_estimates_by_key", {}) or {})
                        .get(entry["key"], {})
                        .get("avg_kitz", 0.0)
                    ),
                    "area_ha": (
                        (day_plan.get("area_estimates_by_key", {}) or {})
                        .get(entry["key"], {})
                        .get("area_ha", 0.0)
                    ),
                    "time_show": True,
                    "flight_time_min": (
                        float(
                            (day_plan.get("area_estimates_by_key", {}) or {})
                            .get(entry["key"], {})
                            .get("flight_time_s", 0.0)
                        )
                        / 60.0
                    ),
                    "flight_factor": (
                        (day_plan.get("area_estimates_by_key", {}) or {})
                        .get(entry["key"], {})
                        .get("flight_multiplier", 1.0)
                    ),
                    "adjusted_flight_min": (
                        float(
                            (day_plan.get("area_estimates_by_key", {}) or {})
                            .get(entry["key"], {})
                            .get("adjusted_flight_time_s", 0.0)
                        )
                        / 60.0
                    ),
                    "kitz_minutes_per_item": (
                        (day_plan.get("area_estimates_by_key", {}) or {})
                        .get(entry["key"], {})
                        .get("kitz_minutes_per_item", 0.0)
                    ),
                    "kitz_extra_minutes_per_item": (
                        (day_plan.get("area_estimates_by_key", {}) or {})
                        .get(entry["key"], {})
                        .get("kitz_extra_minutes_per_item", 0.0)
                    ),
                    "kitz_minutes_total": (
                        (day_plan.get("area_estimates_by_key", {}) or {})
                        .get(entry["key"], {})
                        .get("kitz_minutes_total", 0.0)
                    ),
                    "kitz_time_min": (
                        float(
                            (day_plan.get("area_estimates_by_key", {}) or {})
                            .get(entry["key"], {})
                            .get("kitz_time_s", 0.0)
                        )
                        / 60.0
                    ),
                    "processing_total_min": (
                        float(
                            (day_plan.get("area_estimates_by_key", {}) or {})
                            .get(entry["key"], {})
                            .get("area_total_time_s", 0.0)
                        )
                        / 60.0
                    ),
                }
                for entry in entries
            ]

            self.last_map_payload = {
                "map_items": map_items,
                "color_map": color_map,
                "mapping_line_items": [],
                "flight_stats": {"optimization_active": False},
                "day_plan": day_plan,
                "selected_start_area_key": self.selected_start_area_key,
                "default_center": self.default_map_center,
                "default_zoom": self.default_map_zoom,
            }
            self._render_map_from_payload(
                self.last_map_payload,
                force_reload=True,
                log_open=True,
            )

            self.logln(
                self._txt("day_plan_created_log").format(
                    areas=len(day_plan.get("ordered_keys", [])),
                    distance_km=day_plan.get("total_distance_m", 0.0) / 1000.0,
                    drive_min=day_plan.get("total_duration_s", 0.0) / 60.0,
                    flight_min=day_plan.get("total_flight_time_s", 0.0) / 60.0,
                    total_min=day_plan.get("total_work_time_s", 0.0) / 60.0,
                )
            )
            self.status.showMessage(self._txt("day_plan_created_status"))
            self._show_day_plan_window(entries, day_plan)
        except Exception as ex:
            tb = traceback.format_exc()
            self.logln("─" * 60)
            self.logln(self._txt("day_plan_error_log"))
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
            self.convert_upload_btn.setEnabled(True)

    def _flighthub_config_path(self) -> Path:
        return Path(__file__).resolve().parents[1] / "config" / "flighthub2.json"

    def _load_flighthub_config(self) -> tuple[dict | None, Path]:
        cfg_path = self._flighthub_config_path()
        if not cfg_path.exists():
            cfg_path.parent.mkdir(parents=True, exist_ok=True)
            template = {
                "base_url": "https://your-flighthub-bridge.example.com",
                "timeout_seconds": 30,
                "mode": "bridge-json-base64",
                "auth": {
                    "access_token": "",
                    "token_url": "",
                    "client_id": "",
                    "client_secret": "",
                },
                "endpoints": {
                    "devices": "/api/flighthub/devices",
                    "upload": "/api/flighthub/missions/upload",
                    "assign": "/api/flighthub/missions/assign",
                },
                "devices": [
                    {
                        "id": "DEVICE-ID-1",
                        "name": "M4T-Team-1",
                        "model": "M4T",
                        "workspace_id": "",
                        "enabled": True,
                    }
                ],
            }
            cfg_path.write_text(
                json.dumps(template, ensure_ascii=False, indent=2), encoding="utf-8"
            )
            return None, cfg_path

        try:
            loaded = json.loads(cfg_path.read_text(encoding="utf-8"))
            if not isinstance(loaded, dict):
                return None, cfg_path
            return loaded, cfg_path
        except Exception:
            return None, cfg_path

    def _devices_for_drone_type(self, config: dict, drone_type: str) -> list[dict]:
        devices = config.get("devices") if isinstance(config, dict) else []
        if not isinstance(devices, list):
            return []

        target = str(drone_type or "").strip().upper()
        out = []
        for item in devices:
            if not isinstance(item, dict):
                continue
            if item.get("enabled", True) is False:
                continue
            model = str(item.get("model") or "").strip().upper()
            if model != target:
                continue
            out.append(item)
        return out

    def _select_upload_device(
        self, drone_type: str, devices: list[dict]
    ) -> dict | None:
        if not devices:
            return None
        labels = []
        by_label = {}
        for dev in devices:
            label = f"{dev.get('name', 'Unnamed')} ({dev.get('id', '-')})"
            labels.append(label)
            by_label[label] = dev

        selected, ok = QtWidgets.QInputDialog.getItem(
            self,
            self._txt("upload_select_drone", "Zieldrohne auswählen"),
            self._txt(
                "upload_select_prompt",
                "Bitte Zielgerät für Typ {drone} auswählen:",
            ).format(drone=drone_type),
            labels,
            0,
            False,
        )
        if not ok:
            return None
        return by_label.get(str(selected))

    def _sanitize_output_name(self, name: str) -> str:
        cleaned = (name or "").strip()
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
            cleaned = cleaned.replace(src, dst)
        cleaned = re.sub(r"\s+", "", cleaned)
        cleaned = re.sub(r"[^A-Za-z0-9.-]+", "-", cleaned)
        cleaned = cleaned.replace("_", "-")
        cleaned = re.sub(r"-+", "-", cleaned)
        cleaned = cleaned.strip("-.")
        return cleaned or "area"

    def _run_conversion(
        self,
        show_success_dialog: bool = True,
        output_dir: Path | None = None,
        persist_output_dir: bool = True,
        log_output_dir: bool = True,
    ) -> dict | None:
        kmz_path = self._validate_input_path()
        if kmz_path is None:
            return None

        out_dir = (
            Path(output_dir) if output_dir is not None else Path(self.out_edit.text())
        )
        basename = "area"

        if persist_output_dir:
            self._remember_output_dir(str(out_dir))

        ok, import_err = _ensure_engine_modules()
        if not ok:
            err_text = (
                f"{type(import_err).__name__}: {import_err}"
                if import_err
                else self._txt("engine_unknown_import_error")
            )
            self.logln(self._txt("engine_import_log").format(error=err_text))
            QtWidgets.QMessageBox.critical(
                self,
                self.strings["import_error"],
                self._txt("engine_load_failed").format(details=err_text),
            )
            return None

        kmz = kmz_reader
        writer = kml_writer
        rules = dji_rules
        optimizer = optimize_angle_mod
        if kmz is None or writer is None or rules is None:
            QtWidgets.QMessageBox.critical(
                self,
                self.strings["import_error"],
                self._txt("engine_unavailable"),
            )
            return None

        metric_values = self._get_metric_values()
        options = {
            "flughöhe_m": float(metric_values["altitude"]),
            "seitlicher_überlapp_prozent": self.overlap_spin.value(),
            "sichere_starthöhe_m": float(metric_values["safe_height"]),
            "drohne": self.drone_combo.currentText(),
            "aktion_beenden": str(
                self.action_combo.currentData() or self.action_combo.currentText()
            ),
            "geschwindigkeit_ms": float(metric_values["speed"]),
            "rand": self.margin_spin.value(),
            "winkel_optimierung_aktiv": self.optimize_direction_check.isChecked(),
            "elevation_optimize_enable": self.elevation_optimize_check.isChecked(),
        }

        self.progress.setVisible(True)
        self.progress.setValue(0)
        self.progress.setMaximum(0)
        self.convert_btn.setEnabled(False)
        self.convert_upload_btn.setEnabled(False)
        self.map_btn.setEnabled(False)
        self.day_plan_btn.setEnabled(False)

        try:
            self.status.showMessage(self.strings["converting"])
            self.logln(self._txt("convert_start_log").format(path=kmz_path))
            self.logln("─" * 60)
            self.logln(self._txt("convert_settings_log"))
            for key, value in options.items():
                self.logln(f"  • {key}: {value}")
            self.logln("─" * 60)

            QtCore.QCoreApplication.processEvents()

            self.logln(self._txt("convert_parsing_log"))
            features = kmz.parse_kmz_to_area_features(str(kmz_path))
            self.logln(self._txt("convert_features_loaded").format(count=len(features)))
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

            def _clean(value: str) -> str:
                return self._sanitize_output_name(value)

            def _fmt_short_date(day_value):
                if not day_value:
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
                return f"{day_value.day:02d}{mon.get(day_value.month, 'Mon')}"

            self.logln(self._txt("convert_extract_polygons"))
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
                self.logln(self._txt("convert_excluded").format(count=skipped))

            if not polys:
                self.logln(self._txt("convert_no_polygons_log"))
                self.status.showMessage(self._txt("convert_no_polygons_status"))
                return None

            self.logln(self._txt("convert_polygons_extracted").format(count=len(polys)))
            if self.optimize_direction_check.isChecked() and est_total_distance_m > 0:
                est_total_time_min = est_total_time_s / 60.0
                self.logln(
                    self._txt("convert_estimate").format(
                        distance_m=est_total_distance_m,
                        minutes=est_total_time_min,
                    )
                )
            QtCore.QCoreApplication.processEvents()

            self.logln(self._txt("convert_normalizing"))
            norm = [rules.normalize_polygon(p, add_z_if_missing=True) for p in polys]
            self.logln(self._txt("convert_normalized"))
            QtCore.QCoreApplication.processEvents()

            out_dir.mkdir(parents=True, exist_ok=True)

            self.logln(self._txt("convert_writing").format(count=len(norm)))
            written = writer.write_polygons_to_kmzs(
                norm,
                str(out_dir),
                basename,
                options=options,
                names=names,
                directions=directions,
            )

            self.progress.setMaximum(100)
            self.progress.setValue(100)

            written_files = []
            for idx in range(written):
                if idx < len(names):
                    stem = self._sanitize_output_name(names[idx])
                else:
                    stem = self._sanitize_output_name(f"{basename}-{idx + 1:03d}")
                written_files.append(out_dir / f"{stem}.kmz")

            self.logln("─" * 60)
            self.logln(self._txt("convert_generated").format(count=written))
            if log_output_dir:
                self.logln(self._txt("convert_output_folder").format(path=out_dir))
            self.status.showMessage(self.strings["done"])

            if show_success_dialog:
                success_text = (
                    f"✓ {self._txt('success', 'Success')}: {written} KMZ-Dateien\n\n"
                    f"{self._txt('output_folder', 'Output folder')}:\n{out_dir}"
                )
                QtWidgets.QMessageBox.information(
                    self,
                    self.strings["success"],
                    success_text,
                )

            return {
                "written": int(written),
                "out_dir": out_dir,
                "files": [p for p in written_files if p.exists()],
            }
        finally:
            self.progress.setVisible(False)
            self.convert_btn.setEnabled(True)
            self.convert_upload_btn.setEnabled(True)
            self.map_btn.setEnabled(True)
            self.day_plan_btn.setEnabled(True)

    def convert(self):
        try:
            self._run_conversion(show_success_dialog=True)
        except Exception as ex:
            tb = traceback.format_exc()
            self.logln("─" * 60)
            self.logln(self._txt("convert_error_log"))
            self.logln(tb)
            self.status.showMessage(self.strings["error"])
            QtWidgets.QMessageBox.critical(self, self.strings["error"], str(ex))

    def convert_and_upload(self):
        try:
            config, cfg_path = self._load_flighthub_config()
            if not config:
                QtWidgets.QMessageBox.warning(
                    self,
                    self._txt("upload_failed", "Upload fehlgeschlagen"),
                    self._txt(
                        "upload_missing_config",
                        "FlightHub-Konfiguration fehlt oder ist ungültig:\n{path}",
                    ).format(path=cfg_path),
                )
                return

            client = FlightHubSyncClient(config)
            issues = client.validate_config()
            if issues:
                QtWidgets.QMessageBox.warning(
                    self,
                    self._txt("upload_failed", "Upload fehlgeschlagen"),
                    self._txt(
                        "upload_invalid_config",
                        "FlightHub-Konfiguration ist unvollständig:\n{details}",
                    ).format(details="\n- " + "\n- ".join(issues)),
                )
                return

            drone_type = str(self.drone_combo.currentText()).strip()
            devices = []
            try:
                devices = client.list_devices(drone_type)
            except Exception as ex:
                self.logln(f"ℹ {self._txt('upload_devices_api_failed')}: {ex}")

            if not devices:
                devices = self._devices_for_drone_type(config, drone_type)

            if not devices:
                QtWidgets.QMessageBox.information(
                    self,
                    self._txt("upload_select_drone", "Zieldrohne auswählen"),
                    self._txt(
                        "upload_no_mapping",
                        "Keine FlightHub-Gerätezuordnung für den gewählten Drohnentyp gefunden.",
                    ),
                )
                return

            target_device = self._select_upload_device(drone_type, devices)
            if not target_device:
                return

            self.logln(
                self._txt("upload_started", "Konvertierung und Upload gestartet ...")
            )
            metric_values = self._get_metric_values()
            assign_options = {
                "safe_height_m": float(metric_values.get("safe_height", 60.0)),
                "action": str(
                    self.action_combo.currentData() or self.action_combo.currentText()
                ),
            }

            with tempfile.TemporaryDirectory(prefix="littleone-upload-") as tmp_dir:
                conversion = self._run_conversion(
                    show_success_dialog=False,
                    output_dir=Path(tmp_dir),
                    persist_output_dir=False,
                    log_output_dir=False,
                )
                if not conversion:
                    return

                files = list(conversion.get("files") or [])
                if not files:
                    raise RuntimeError("No generated KMZ files found for upload")

                uploaded_count = 0
                for file_path in files:
                    upload_resp = client.upload_mission_file(
                        file_path, target_device, drone_type
                    )
                    mission_id = str(
                        upload_resp.get("mission_id")
                        or upload_resp.get("missionId")
                        or upload_resp.get("id")
                        or (upload_resp.get("data") or {}).get("uuid")
                        or upload_resp.get("uuid")
                        or ""
                    ).strip()
                    if mission_id:
                        assign_resp = client.assign_mission(
                            mission_id,
                            target_device,
                            task_name=Path(file_path).stem,
                            flight_options=assign_options,
                        )
                        self.logln(
                            f"✓ Upload {file_path.name}: mission_id={mission_id}, assign={assign_resp}"
                        )
                    else:
                        warn_msg = self._txt(
                            "upload_missing_mission_id",
                            "Upload-Antwort enthält keine mission_id (Datei: {file}).",
                        ).format(file=file_path.name)
                        self.logln(f"⚠ {warn_msg} Response={upload_resp}")
                    uploaded_count += 1

            self.status.showMessage(self._txt("upload_done", "Upload abgeschlossen"))
            QtWidgets.QMessageBox.information(
                self,
                self._txt("success", "Erfolgreich"),
                f"{self._txt('upload_done', 'Upload abgeschlossen')}\n\n"
                f"Dateien: {uploaded_count}\n"
                f"Ziel: {target_device.get('name', '-')}",
            )
        except Exception as ex:
            self.status.showMessage(self._txt("upload_failed", "Upload fehlgeschlagen"))
            self.logln(f"❌ Upload-Fehler: {ex}")
            QtWidgets.QMessageBox.critical(
                self,
                self._txt("upload_failed", "Upload fehlgeschlagen"),
                str(ex),
            )

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
        defaults = (
            self.user_defaults.get("defaults", {})
            if isinstance(self.user_defaults, dict)
            else {}
        )
        self._apply_form_defaults(defaults)

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
