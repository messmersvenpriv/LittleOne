from pathlib import Path
import sys

sys.path.append(str(Path(__file__).resolve().parents[1] / "src"))
from LittleOne import kmz_reader

p = Path(r"C:\LittleOne\data\start\2299_files.kmz")
print("Datei:", p)
try:
    kml_text = kmz_reader.extract_kml_string_from_kmz(str(p))
    print("Länge KML:", len(kml_text))
    head = kml_text[:4000]
    print("\n---- KML Kopf (erste 4000 Zeichen) ----\n")
    print(head)
    print("\n---- Tag-Statistiken ----")
    import re

    print(
        "Placemark count:",
        len(re.findall(r"<placemark", kml_text, flags=re.IGNORECASE)),
    )
    print("Polygon count:", len(re.findall(r"<polygon", kml_text, flags=re.IGNORECASE)))
    print(
        "coordinates count:",
        len(re.findall(r"<coordinates", kml_text, flags=re.IGNORECASE)),
    )
except Exception as e:
    print("Fehler beim Lesen:", type(e), e)
    import traceback

    traceback.print_exc()
