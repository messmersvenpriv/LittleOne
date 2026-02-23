from shapely.geometry import Polygon


def _xyz_tuple(coord, add_z_if_missing: bool):
    if len(coord) >= 3:
        return (float(coord[0]), float(coord[1]), float(coord[2]))
    if add_z_if_missing:
        return (float(coord[0]), float(coord[1]), 0.0)
    return (float(coord[0]), float(coord[1]))


def normalize_polygon(polygon: Polygon, add_z_if_missing: bool = True) -> Polygon:
    ext = [_xyz_tuple(c, add_z_if_missing) for c in polygon.exterior.coords]
    if ext and ext[0] != ext[-1]:
        ext.append(ext[0])

    holes = []
    for ring in polygon.interiors:
        pts = [_xyz_tuple(c, add_z_if_missing) for c in ring.coords]
        if pts and pts[0] != pts[-1]:
            pts.append(pts[0])
        holes.append(pts)

    return Polygon(ext, holes)
