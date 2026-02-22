from fastkml import kml
from pygeoif import geometry as pgi
from pathlib import Path
from typing import Iterable
from shapely.geometry import Polygon


def write_to_kmls(polys: Iterable[Polygon], out_dir: str, base_name: str):
    Path(out_dir).mkdir(parents=True, exist_ok=True)
    for i, p in enumerate(polys, start=1):
        xml = polygon_to_kml(p, "{base_name}_{i:03d}")
        out_file = Path(out_dir) / f"{base_name}_{i:03d}.kml"
        out_file.write_text(xml, encoding="utf-8")
