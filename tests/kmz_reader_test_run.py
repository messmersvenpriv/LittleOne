#!/usr/bin/env python3
"""Runnable test helper for parse_kmz_to_area_summaries.

Usage:
    python tests/kmz_reader_test_run.py [path/to/file.kmz]

If no path is given, uses the example KMZ in data/start/.
"""
import sys
from pathlib import Path

# add src to path
sys.path.append(str(Path(__file__).resolve().parents[1] / "src"))

from LittleOne.kmz_reader import parse_kmz_to_area_summaries


def main() -> int:
    if len(sys.argv) >= 2:
        kmz_file = sys.argv[1]
    else:
        kmz_file = str(
            Path(__file__).resolve().parents[1]
            / "data"
            / "start"
            / "S123_e6d87e0a84674ec19e836aa14c1a259d_KML (10).kmz"
        )

    print("Using:", kmz_file)
    summaries = parse_kmz_to_area_summaries(kmz_file)

    print(f"{len(summaries)} Flächen (Summaries)")
    if not summaries:
        print("Keine Summaries gefunden.")
        return 1

    for s in summaries[:50]:
        print(
            f"Placemark-ID: {s.placemark_id} | Datum: {s.datum_mahd} | Vorname: {s.antragsteller_vorname} | Name: {s.antragsteller_name} | Telefon: {s.antragsteller_telefon}"
        )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
