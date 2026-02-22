#!/usr/bin/env python3
import sys
from pathlib import Path
import traceback

sys.path.append(str(Path(__file__).resolve().parents[1] / "src"))

from LittleOne import kmz_reader

root = Path(__file__).resolve().parents[1]
search = list(root.rglob("*.kmz")) + list(root.rglob("*.kml"))

if not search:
    print("Keine .kmz/.kml Dateien gefunden unter", root)
    raise SystemExit(1)

for p in sorted(search):
    print(f"---\nDatei: {p}\n---")
    try:
        if p.suffix.lower() == ".kmz":
            summaries = kmz_reader.parse_kmz_to_area_summaries(str(p))
            print(f"Erfolgreich: {len(summaries)} Summaries")
        else:
            text = p.read_text(encoding="utf-8")
            polys = kmz_reader.polygons_from_kml(text)
            print(f"Erfolgreich: {len(polys)} Polygone (aus KML)")
    except Exception as ex:
        print("Fehler beim Parsen:")
        print(type(ex), ex)
        traceback.print_exc()

print("Fertig")
