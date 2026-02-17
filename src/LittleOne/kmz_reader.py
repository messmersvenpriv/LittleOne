from fastkml import kml
import zipfile
from typing import List
from shapely.geometry import shape, Polygon, MultiPolygon

def extract_kml_string_from_kmz(kmz_path: str) -> str:
    with zipfile.ZipFile(kmz_path, 'r') as zf:
        kml_name = next(n for n in zf.namelist() if n.lower().endswith('.kml'))
        return zf.read(kml_name).decode('utf-8')

def polygons_from_kml(kml_text: str) -> List[Polygon]:
    doc = kml.KML()
    doc.from_string(kml_text.encode('utf-8'))
    polys: List[Polygon] = []
    for f1 in doc.features():
        for f2 in getattr(f1, 'features', lambda: [])():
            for f3 in getattr(f2, 'features', lambda: [])():
                geom = getattr(f3, 'geometry', None)
                if not geom:
                    continue
                shp = shape(geom.__geo_interface__)
                if isinstance(shp, Polygon):
                    polys.append(shp)
                elif isinstance(shp, MultiPolygon):
                    polys.extend([p for p in shp.geoms])
    return polys
