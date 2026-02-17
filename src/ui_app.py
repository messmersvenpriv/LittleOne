from PySide6 import QtWidgets, QtGui
from pathlib import Path
import sys, traceback

try:
    from LittleOne import kmz_reader, kml_writer, dji_rules
except Exception:
    kmz_reader = kml_writer = dji_rules = None


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Kitzrettung – KMZ/KML Tool")
        self.resize(960, 600)
        ico_path = Path(__file__).parent.parent / "assets" / "app.ico"
        if ico_path.exists():
            self.setWindowIcon(QtGui.QIcon(str(ico_path)))
        central = QtWidgets.QWidget(self)
        self.setCentralWidget(central)
        self.kmz_edit = QtWidgets.QLineEdit()
        self.kmz_btn = QtWidgets.QPushButton("…")
        self.kmz_btn.clicked.connect(self.pick_kmz)
        self.out_edit = QtWidgets.QLineEdit(str(Path.cwd() / "out"))
        self.out_btn = QtWidgets.QPushButton("…")
        self.out_btn.clicked.connect(self.pick_out)
        self.base_edit = QtWidgets.QLineEdit("area")
        self.convert_btn = QtWidgets.QPushButton("Konvertieren (KMZ → KMLs)")
        self.convert_btn.clicked.connect(self.convert)
        self.log = QtWidgets.QPlainTextEdit()
        self.log.setReadOnly(True)
        form = QtWidgets.QFormLayout()
        row_kmz = QtWidgets.QHBoxLayout()
        row_kmz.addWidget(self.kmz_edit)
        row_kmz.addWidget(self.kmz_btn)
        row_out = QtWidgets.QHBoxLayout()
        row_out.addWidget(self.out_edit)
        row_out.addWidget(self.out_btn)
        form.addRow("KMZ/KML-Datei", row_kmz)
        form.addRow("Ausgabeordner", row_out)
        form.addRow("Basisname", self.base_edit)
        layout = QtWidgets.QVBoxLayout(central)
        layout.addLayout(form)
        layout.addWidget(self.convert_btn)
        layout.addWidget(self.log, 1)
        self.status = self.statusBar()
        self.status.showMessage("Bereit.")

    def pick_kmz(self):
        dlg = QtWidgets.QFileDialog(self)
        dlg.setNameFilters(["KMZ (*.kmz)", "KML (*.kml)", "Alle Dateien (*.*)"])
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

    def convert(self):
        try:
            kmz_path = Path(self.kmz_edit.text())
            out_dir = Path(self.out_edit.text())
            basename = self.base_edit.text().strip() or "area"
            if not kmz_path.exists():
                QtWidgets.QMessageBox.warning(
                    self, "Hinweis", "Bitte KMZ oder KML auswählen."
                )
                return
            if kmz_reader is None:
                QtWidgets.QMessageBox.critical(
                    self,
                    "Fehlende Engine",
                    "Paket 'kitzkmz' fehlt. Bitte Abhängigkeiten im venv installieren.",
                )
                return
            self.status.showMessage("Konvertiere …")
            self.logln(f"Starte Konvertierung: {kmz_path}")
            if kmz_path.suffix.lower() == ".kmz":
                kml_text = kmz_reader.extract_kml_string_from_kmz(str(kmz_path))
            else:
                kml_text = kmz_path.read_text(encoding="utf-8")
            from shapely.geometry import shape
            from fastkml import kml as kmlmod

            doc = kmlmod.KML()
            doc.from_string(kml_text.encode("utf-8"))
            polys = []
            for f1 in doc.features():
                for f2 in getattr(f1, "features", lambda: [])():
                    for f3 in getattr(f2, "features", lambda: [])():
                        g = getattr(f3, "geometry", None)
                        if g:
                            shp = shape(g.__geo_interface__)
                            if shp.geom_type == "Polygon":
                                polys.append(shp)
            if not polys:
                self.logln("Keine Polygone gefunden.")
                self.status.showMessage("Keine Polygone.")
                return
            norm = [
                dji_rules.normalize_polygon(p, add_z_if_missing=True) for p in polys
            ]
            out_dir.mkdir(parents=True, exist_ok=True)
            kml_writer.write_polygons_to_kmls(norm, str(out_dir), basename)
            self.logln(f"OK: {len(norm)} KML-Dateien in {out_dir}")
            self.status.showMessage("Fertig.")
            QtWidgets.QMessageBox.information(
                self, "OK", f"Erfolgreich: {len(norm)} KML-Dateien in\n{out_dir}"
            )
        except Exception as ex:
            import traceback

            tb = traceback.format_exc()
            self.logln(tb)
            self.status.showMessage("Fehler.")
            QtWidgets.QMessageBox.critical(self, "Fehler", str(ex))


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    w = MainWindow()
    w.show()
    sys.exit(app.exec())
