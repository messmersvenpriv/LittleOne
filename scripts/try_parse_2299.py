from pathlib import Path
import sys

sys.path.append(str(Path(__file__).resolve().parents[1] / "src"))
from LittleOne import kmz_reader

p = Path(r"C:\LittleOne\data\start\2299_files.kmz")
print("Datei:", p)

try:
    feats = kmz_reader.parse_kmz_to_area_features(str(p))
    print("parse_kmz_to_area_features ->", len(feats))
except Exception as e:
    print("parse_kmz_to_area_features raised:", type(e), e)

try:
    kml_text = kmz_reader.extract_kml_string_from_kmz(str(p))
    polys = kmz_reader.polygons_from_kml(kml_text)
    print("polygons_from_kml ->", len(polys))
except Exception as e:
    print("polygons_from_kml raised:", type(e), e)

try:
    kml_text = kmz_reader.extract_kml_string_from_kmz(str(p))
    fallback = kmz_reader._parse_kml_text_fallback(kml_text)
    print("_parse_kml_text_fallback ->", len(fallback))
except Exception as e:
    print("_parse_kml_text_fallback raised:", type(e), e)

print("Done")
