from shapely.geometry import Polygon
import math

def _dist(a, b): return math.hypot(b[0]-a[0], b[1]-a[1])

def mrr_angle_deg(poly: Polygon) -> float:
    mrr = poly.minimum_rotated_rectangle
    coords = list(mrr.exterior.coords)[:4]
    a0, a1, a2, a3 = coords
    if _dist(a0, a1) >= _dist(a1, a2):
        dx, dy = a1[0]-a0[0], a1[1]-a0[1]
    else:
        dx, dy = a2[0]-a1[0], a2[1]-a1[1]
    ang = math.degrees(math.atan2(dy, dx))
    if ang < 0: ang += 180.0
    return ang
