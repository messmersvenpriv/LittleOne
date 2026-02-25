import math
from typing import Dict, List, Optional, Sequence, Tuple

from shapely import affinity
from shapely.geometry import GeometryCollection, LineString, MultiLineString, Polygon


EARTH_RADIUS_M = 6371008.8


def _dist(a, b):
    return math.hypot(b[0] - a[0], b[1] - a[1])


def _normalize_heading_deg(angle: float) -> float:
    value = float(angle) % 180.0
    if value < 0:
        value += 180.0
    return value


def _drone_ir_hfov_deg(drone: str) -> float:
    key = (drone or "").strip().upper()
    if key == "M4T":
        # DJI Matrice 4T Wärmebildkamera: diagonales Sichtfeld ca. 45°
        return 45.0
    if key == "M3T":
        # DJI Mavic 3T Wärmebildkamera: diagonales Sichtfeld ca. 61°
        return 61.0
    if key == "M2EA":
        # DJI M2EA Wärmebildkamera: häufig mit ~57° angegeben.
        return 57.0
    return 57.0


def _ground_swath_width_m(altitude_m: float, ir_hfov_deg: float) -> float:
    altitude = max(0.1, float(altitude_m))
    hfov = max(1.0, min(179.0, float(ir_hfov_deg)))
    return 2.0 * altitude * math.tan(math.radians(hfov / 2.0))


def _line_spacing_m(swath_width_m: float, side_overlap_percent: float) -> float:
    overlap = max(0.0, min(95.0, float(side_overlap_percent)))
    spacing = float(swath_width_m) * (1.0 - overlap / 100.0)
    return max(0.5, spacing)


def _project_to_local_metric(poly: Polygon) -> Polygon:
    lon0 = float(poly.centroid.x)
    lat0 = float(poly.centroid.y)
    lat0_rad = math.radians(lat0)

    def _xy(coord: Sequence[float]) -> Tuple[float, float]:
        lon = float(coord[0])
        lat = float(coord[1])
        x = EARTH_RADIUS_M * math.radians(lon - lon0) * math.cos(lat0_rad)
        y = EARTH_RADIUS_M * math.radians(lat - lat0)
        return x, y

    ext = [_xy(c) for c in poly.exterior.coords]
    holes = [[_xy(c) for c in ring.coords] for ring in poly.interiors]
    local = Polygon(ext, holes)
    if not local.is_valid:
        local = local.buffer(0)
    return local


def _project_to_local_metric_with_ref(
    poly: Polygon,
) -> Tuple[Polygon, Dict[str, float]]:
    lon0 = float(poly.centroid.x)
    lat0 = float(poly.centroid.y)
    lat0_rad = math.radians(lat0)

    ref = {
        "lon0": lon0,
        "lat0": lat0,
        "lat0_rad": lat0_rad,
        "cos_lat0": max(1e-9, math.cos(lat0_rad)),
    }

    def _xy(coord: Sequence[float]) -> Tuple[float, float]:
        lon = float(coord[0])
        lat = float(coord[1])
        x = EARTH_RADIUS_M * math.radians(lon - ref["lon0"]) * ref["cos_lat0"]
        y = EARTH_RADIUS_M * math.radians(lat - ref["lat0"])
        return x, y

    ext = [_xy(c) for c in poly.exterior.coords]
    holes = [[_xy(c) for c in ring.coords] for ring in poly.interiors]
    local = Polygon(ext, holes)
    if not local.is_valid:
        local = local.buffer(0)
    return local, ref


def _local_to_lonlat(x: float, y: float, ref: Dict[str, float]) -> Tuple[float, float]:
    lon = ref["lon0"] + math.degrees(x / (EARTH_RADIUS_M * ref["cos_lat0"]))
    lat = ref["lat0"] + math.degrees(y / EARTH_RADIUS_M)
    return lon, lat


def _segment_length_on_line(geom) -> float:
    if geom.is_empty:
        return 0.0
    if isinstance(geom, LineString):
        return float(geom.length)
    if isinstance(geom, MultiLineString):
        return float(sum(g.length for g in geom.geoms))
    if isinstance(geom, GeometryCollection):
        return float(sum(_segment_length_on_line(g) for g in geom.geoms))
    return 0.0


def _extract_line_strings(geom) -> List[LineString]:
    if geom.is_empty:
        return []
    if isinstance(geom, LineString):
        if geom.length > 0:
            return [geom]
        return []
    if isinstance(geom, MultiLineString):
        return [g for g in geom.geoms if g.length > 0]
    if isinstance(geom, GeometryCollection):
        lines: List[LineString] = []
        for g in geom.geoms:
            lines.extend(_extract_line_strings(g))
        return lines
    return []


def _line_positions(
    y_min: float,
    y_max: float,
    swath_width_m: float,
    line_spacing_m: float,
) -> List[float]:
    width = max(0.0, y_max - y_min)
    if width <= 0:
        return [0.5 * (y_min + y_max)]

    if width <= swath_width_m:
        return [0.5 * (y_min + y_max)]

    n_lines = int(math.ceil((width - swath_width_m) / line_spacing_m)) + 1
    n_lines = max(1, n_lines)

    covered = swath_width_m + (n_lines - 1) * line_spacing_m
    slack = max(0.0, covered - width)
    first_center = y_min - (slack / 2.0) + (swath_width_m / 2.0)

    return [first_center + i * line_spacing_m for i in range(n_lines)]


def _estimate_path_length_for_heading(
    local_poly: Polygon,
    heading_deg_north_cw: float,
    swath_width_m: float,
    line_spacing_m: float,
) -> Dict[str, float]:
    heading = _normalize_heading_deg(heading_deg_north_cw)

    # Shapely-Rotation: 0° liegt auf +X (Ost), CCW positiv.
    # Heading ist hier 0°=Nord, im Uhrzeigersinn.
    # Für Ausrichtung der Fluglinien auf X'-Achse:
    math_ccw = 90.0 - heading
    rotated = affinity.rotate(
        local_poly, -math_ccw, origin="centroid", use_radians=False
    )

    minx, miny, maxx, maxy = rotated.bounds
    line_ys = _line_positions(miny, maxy, swath_width_m, line_spacing_m)

    if not line_ys:
        return {"distance_m": 0.0, "line_count": 0.0}

    span = (maxx - minx) + 20.0
    x0 = minx - 10.0
    x1 = x0 + span

    survey_len = 0.0
    for y in line_ys:
        line = LineString([(x0, y), (x1, y)])
        inter = rotated.intersection(line)
        survey_len += _segment_length_on_line(inter)

    transit_len = max(0, len(line_ys) - 1) * line_spacing_m
    total_len = survey_len + transit_len
    return {"distance_m": total_len, "line_count": float(len(line_ys))}


def _survey_lines_for_heading(
    local_poly: Polygon,
    heading_deg_north_cw: float,
    swath_width_m: float,
    line_spacing_m: float,
) -> Tuple[List[LineString], Dict[str, float]]:
    heading = _normalize_heading_deg(heading_deg_north_cw)
    math_ccw = 90.0 - heading
    centroid = local_poly.centroid
    rotated = affinity.rotate(
        local_poly, -math_ccw, origin="centroid", use_radians=False
    )

    minx, miny, maxx, maxy = rotated.bounds
    line_ys = _line_positions(miny, maxy, swath_width_m, line_spacing_m)
    if not line_ys:
        return [], {"distance_m": 0.0, "line_count": 0.0}

    span = (maxx - minx) + 20.0
    x0 = minx - 10.0
    x1 = x0 + span

    rotated_segments: List[LineString] = []
    survey_len = 0.0
    for y in line_ys:
        line = LineString([(x0, y), (x1, y)])
        inter = rotated.intersection(line)
        pieces = _extract_line_strings(inter)
        for seg in pieces:
            survey_len += float(seg.length)
            rotated_segments.append(seg)

    local_segments = [
        affinity.rotate(seg, math_ccw, origin=centroid, use_radians=False)
        for seg in rotated_segments
    ]

    transit_len = max(0, len(line_ys) - 1) * line_spacing_m
    total_len = survey_len + transit_len
    return local_segments, {"distance_m": total_len, "line_count": float(len(line_ys))}


def mrr_angle_deg(poly: Polygon) -> float:
    mrr = poly.minimum_rotated_rectangle
    coords = list(mrr.exterior.coords)[:4]
    a0, a1, a2, _ = coords
    if _dist(a0, a1) >= _dist(a1, a2):
        dx, dy = a1[0] - a0[0], a1[1] - a0[1]
    else:
        dx, dy = a2[0] - a1[0], a2[1] - a1[1]

    # Umrechnung auf Heading-Konvention: 0°=Nord, 90°=Ost.
    math_ccw = math.degrees(math.atan2(dy, dx))
    heading = 90.0 - math_ccw
    return _normalize_heading_deg(heading)


def best_mapping_direction_deg(
    poly: Polygon,
    altitude_m: float,
    side_overlap_percent: float,
    speed_mps: float,
    drone: str = "M4T",
    angle_step_deg: float = 1.0,
) -> Dict[str, float]:
    local_poly = _project_to_local_metric(poly)

    ir_hfov_deg = _drone_ir_hfov_deg(drone)
    swath_width = _ground_swath_width_m(altitude_m, ir_hfov_deg)
    spacing = _line_spacing_m(swath_width, side_overlap_percent)

    step = max(0.5, float(angle_step_deg))
    best = {
        "direction_deg": float(mrr_angle_deg(poly)),
        "distance_m": float("inf"),
        "time_s": float("inf"),
        "line_count": 0.0,
        "line_spacing_m": spacing,
        "swath_width_m": swath_width,
        "ir_hfov_deg": ir_hfov_deg,
    }

    speed = max(0.1, float(speed_mps))
    angle = 0.0
    while angle < 180.0:
        est = _estimate_path_length_for_heading(local_poly, angle, swath_width, spacing)
        dist = float(est["distance_m"])
        if dist < best["distance_m"]:
            best["direction_deg"] = float(angle)
            best["distance_m"] = dist
            best["time_s"] = dist / speed
            best["line_count"] = float(est["line_count"])
        angle += step

    if not math.isfinite(best["distance_m"]):
        best["direction_deg"] = float(mrr_angle_deg(poly))
        best["distance_m"] = 0.0
        best["time_s"] = 0.0

    return best


def mapping_preview(
    poly: Polygon,
    altitude_m: float,
    side_overlap_percent: float,
    speed_mps: float,
    drone: str = "M4T",
    angle_step_deg: float = 1.0,
    direction_deg: Optional[float] = None,
) -> Dict[str, object]:
    local_poly, ref = _project_to_local_metric_with_ref(poly)

    ir_hfov_deg = _drone_ir_hfov_deg(drone)
    swath_width = _ground_swath_width_m(altitude_m, ir_hfov_deg)
    spacing = _line_spacing_m(swath_width, side_overlap_percent)
    speed = max(0.1, float(speed_mps))

    if direction_deg is None:
        best = best_mapping_direction_deg(
            poly,
            altitude_m=altitude_m,
            side_overlap_percent=side_overlap_percent,
            speed_mps=speed,
            drone=drone,
            angle_step_deg=angle_step_deg,
        )
        chosen_direction = float(best["direction_deg"])
    else:
        chosen_direction = _normalize_heading_deg(float(direction_deg))

    lines_local, est = _survey_lines_for_heading(
        local_poly,
        chosen_direction,
        swath_width,
        spacing,
    )

    lines_latlon: List[List[List[float]]] = []
    for seg in lines_local:
        pts: List[List[float]] = []
        for x, y in seg.coords:
            lon, lat = _local_to_lonlat(float(x), float(y), ref)
            pts.append([lat, lon])
        if len(pts) >= 2:
            lines_latlon.append(pts)

    distance_m = float(est.get("distance_m", 0.0))
    time_s = distance_m / speed
    return {
        "direction_deg": chosen_direction,
        "distance_m": distance_m,
        "time_s": time_s,
        "line_count": float(est.get("line_count", 0.0)),
        "line_spacing_m": spacing,
        "swath_width_m": swath_width,
        "ir_hfov_deg": ir_hfov_deg,
        "lines_latlon": lines_latlon,
    }
