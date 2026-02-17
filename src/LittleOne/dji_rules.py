from shapely.geometry import Polygon
from shapely.geometry.polygon import orient

def ensure_closed_ring(poly: Polygon) -> Polygon:
    ext = list(poly.exterior.coords)
    if ext[0] != ext[-1]:
        ext.append(ext[0])
    return Polygon(ext, [list(r.coords) for r in poly.interiors])

def add_z_to_coords(poly: Polygon, z_value: float = 0.0) -> Polygon:
    def addz(coords): return [(x, y, z_value) for x, y in coords]
    ext = addz(poly.exterior.coords)
    holes = [addz(r.coords) for r in poly.interiors]
    return Polygon(ext, holes)

def normalize_polygon(poly, add_z_if_missing=True) -> Polygon:
    p = ensure_closed_ring(poly)
    p = orient(p, sign=1.0)
    if add_z_if_missing:
        try:
            _ = p.exterior.coords[0][2]
        except IndexError:
            p = add_z_to_coords(p, 0.0)
    return p
