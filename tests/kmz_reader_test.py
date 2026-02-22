# tests/kmz_reader_testpy.py

import sys
from pathlib import Path

# src zum Modul-Suchpfad hinzufügen
sys.path.append(str(Path(__file__).resolve().parents[1] / "src"))

from LittleOne.kmz_reader import parse_kmz_to_area_summaries


if __name__ == "__main__":
    kmz_file = (
        r"C:\LittleOne\data\start\S123_e6d87e0a84674ec19e836aa14c1a259d_KML (10).kmz"
    )
    summaries = parse_kmz_to_area_summaries(kmz_file)

    print(f"{len(summaries)} Flächen (Summaries)")
    for s in summaries:
        print("Placemark-ID:", s.placemark_id)
        print("Datum_Mahd:", s.datum_mahd)  # datetime.date oder None
        print("Schlag/Flurstücke:", s.schlag_flurstueck)
        print("Antragsteller Vorname:", s.antragsteller_vorname)
        print("Antragsteller Name:", s.antragsteller_name)
        print("Telefon:", s.antragsteller_telefon)
        print("Bekanntgabe Kitzrettung:", s.bekanntgabe_kitzrettung)
        # Erste 3 Eckpunkte des ersten Rings als Beispiel:
        if s.koordinaten:
            print("Erste 3 Eckpunkte:", s.koordinaten[0][:3])
        print("---")
