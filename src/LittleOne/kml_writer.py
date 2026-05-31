from pathlib import Path
from typing import Iterable, Optional, Sequence
import time
import re
import zipfile
import math
from shapely.geometry import Polygon, MultiPolygon, LineString
from shapely.ops import unary_union, nearest_points

try:
    from .optimize_angle import mapping_preview
except Exception:
    from LittleOne.optimize_angle import mapping_preview


def _fmt_number(value: float) -> str:
    txt = f"{float(value):.12f}".rstrip("0").rstrip(".")
    return txt if txt else "0"


def _coordinates_text(poly: Polygon) -> str:
    coords = []
    for lon, lat, *_ in poly.exterior.coords:
        coords.append(f"{_fmt_number(lon)},{_fmt_number(lat)},0")
    return "\n                ".join(coords)


def _sanitize_filename(name: str) -> str:
    cleaned = (name or "").strip()
    replacements = {
        "ä": "ae",
        "ö": "oe",
        "ü": "ue",
        "Ä": "Ae",
        "Ö": "Oe",
        "Ü": "Ue",
        "ß": "ss",
    }
    for src, dst in replacements.items():
        cleaned = cleaned.replace(src, dst)

    cleaned = re.sub(r"\s+", "", cleaned)
    cleaned = re.sub(r"[^A-Za-z0-9.-]+", "-", cleaned)
    cleaned = cleaned.replace("_", "-")
    cleaned = re.sub(r"-+", "-", cleaned)
    cleaned = cleaned.strip("-.")
    return cleaned or "area"


def _build_output_stems(
    total_count: int,
    base_name: str,
    names: Optional[Sequence[str]] = None,
) -> list[str]:
    stems: list[str] = []
    counters: dict[str, int] = {}

    for i in range(total_count):
        if names and i < len(names) and names[i]:
            base_stem = _sanitize_filename(names[i])
        else:
            base_stem = _sanitize_filename(f"{base_name}-{i + 1:03d}")

        occurrence = counters.get(base_stem, 0) + 1
        counters[base_stem] = occurrence

        if occurrence == 1:
            stems.append(base_stem)
        else:
            stems.append(f"{base_stem}-{occurrence}")

    return stems


def _drone_profile(drone: str) -> dict:
    key = (drone or "").strip().upper()
    if key == "M4T":
        return {
            "drone_enum": 99,
            "payload_enum": 89,
            "gimbal_pitch": -90,
            "include_wayline_avoid": True,
            "include_quick_ortho": True,
        }
    if key == "M3T":
        return {
            "drone_enum": 77,
            "payload_enum": 67,
            "gimbal_pitch": -45,
            "include_wayline_avoid": False,
            "include_quick_ortho": False,
        }
    return {
        "drone_enum": 60,
        "payload_enum": 56,
        "gimbal_pitch": -45,
        "include_wayline_avoid": False,
        "include_quick_ortho": False,
    }


def _map_finish_action(action_ui: str) -> str:
    mapping = {
        "Routenmodus verlassen": "noAction",
        "Rückkehrfunktion": "goHome",
        "Landen": "autoLand",
        "Zur Startposition zurückkehren und schweben": "gotoFirstWaypoint",
    }
    return mapping.get(action_ui, "goHome")


def polygon_to_wpml_kml(polygon: Polygon, options: Optional[dict] = None) -> str:
    opts = options or {}
    profile = _drone_profile(str(opts.get("drohne", "M4T")))

    flughoehe = float(opts.get("flughöhe_m", 60))
    sichere_starthoehe = float(opts.get("sichere_starthöhe_m", max(20, flughoehe)))
    speed = float(opts.get("geschwindigkeit_ms", 8))
    overlap_w = int(opts.get("seitlicher_überlapp_prozent", 30))
    margin = int(opts.get("rand", 0))
    direction = int(opts.get("direction", 0))
    elevation_optimize_enable = (
        1 if bool(opts.get("elevation_optimize_enable", True)) else 0
    )
    finish_action = _map_finish_action(
        str(opts.get("aktion_beenden", "Rückkehrfunktion"))
    )

    now_ms = int(time.time() * 1000)
    coords = _coordinates_text(polygon)

    wayline_avoid = ""
    if profile["include_wayline_avoid"]:
        wayline_avoid = (
            "\n      <wpml:waylineAvoidLimitAreaMode>1</wpml:waylineAvoidLimitAreaMode>"
        )

    quick_ortho = ""
    if profile["include_quick_ortho"]:
        quick_ortho = (
            "\n        <wpml:quickOrthoMappingEnable>0</wpml:quickOrthoMappingEnable>"
        )

    return f"""<?xml version="1.0" encoding="UTF-8"?>
<kml xmlns="http://www.opengis.net/kml/2.2" xmlns:wpml="http://www.dji.com/wpmz/1.0.6">
    <Document>
        <wpml:createTime>{now_ms}</wpml:createTime>
        <wpml:updateTime>{now_ms}</wpml:updateTime>
        <wpml:missionConfig>
            <wpml:flyToWaylineMode>safely</wpml:flyToWaylineMode>
            <wpml:finishAction>{finish_action}</wpml:finishAction>
            <wpml:exitOnRCLost>executeLostAction</wpml:exitOnRCLost>
            <wpml:executeRCLostAction>goBack</wpml:executeRCLostAction>
            <wpml:takeOffSecurityHeight>{_fmt_number(sichere_starthoehe)}</wpml:takeOffSecurityHeight>
            <wpml:globalTransitionalSpeed>15</wpml:globalTransitionalSpeed>
            <wpml:droneInfo>
                <wpml:droneEnumValue>{profile["drone_enum"]}</wpml:droneEnumValue>
                <wpml:droneSubEnumValue>0</wpml:droneSubEnumValue>
            </wpml:droneInfo>{wayline_avoid}
            <wpml:payloadInfo>
                <wpml:payloadEnumValue>{profile["payload_enum"]}</wpml:payloadEnumValue>
                <wpml:payloadSubEnumValue>2</wpml:payloadSubEnumValue>
                <wpml:payloadPositionIndex>0</wpml:payloadPositionIndex>
            </wpml:payloadInfo>
        </wpml:missionConfig>
        <Folder>
            <wpml:templateType>mapping2d</wpml:templateType>
            <wpml:templateId>0</wpml:templateId>
            <wpml:waylineCoordinateSysParam>
                <wpml:coordinateMode>WGS84</wpml:coordinateMode>
                <wpml:heightMode>relativeToStartPoint</wpml:heightMode>
                <wpml:globalShootHeight>{_fmt_number(flughoehe)}</wpml:globalShootHeight>
            </wpml:waylineCoordinateSysParam>
            <wpml:autoFlightSpeed>{_fmt_number(speed)}</wpml:autoFlightSpeed>
            <Placemark>
                <wpml:caliFlightEnable>0</wpml:caliFlightEnable>
                <wpml:elevationOptimizeEnable>{elevation_optimize_enable}</wpml:elevationOptimizeEnable>
                <wpml:smartObliqueEnable>0</wpml:smartObliqueEnable>{quick_ortho}
                <wpml:facadeWaylineEnable>0</wpml:facadeWaylineEnable>
                <wpml:isLookAtSceneSet>0</wpml:isLookAtSceneSet>
                <wpml:smartObliqueGimbalPitch>{profile["gimbal_pitch"]}</wpml:smartObliqueGimbalPitch>
                <wpml:shootType>time</wpml:shootType>
                <wpml:direction>{direction}</wpml:direction>
                <wpml:margin>{margin}</wpml:margin>
                <wpml:efficiencyFlightModeEnable>0</wpml:efficiencyFlightModeEnable>
                <wpml:overlap>
                    <wpml:orthoLidarOverlapH>80</wpml:orthoLidarOverlapH>
                    <wpml:orthoLidarOverlapW>{overlap_w}</wpml:orthoLidarOverlapW>
                    <wpml:orthoCameraOverlapH>80</wpml:orthoCameraOverlapH>
                    <wpml:orthoCameraOverlapW>{overlap_w}</wpml:orthoCameraOverlapW>
                </wpml:overlap>
                <Polygon>
                    <outerBoundaryIs>
                        <LinearRing>
                            <coordinates>
                                {coords}
                            </coordinates>
                        </LinearRing>
                    </outerBoundaryIs>
                </Polygon>
                <wpml:ellipsoidHeight>{_fmt_number(flughoehe)}</wpml:ellipsoidHeight>
                <wpml:height>{_fmt_number(flughoehe)}</wpml:height>
            </Placemark>
            <wpml:payloadParam>
                <wpml:payloadPositionIndex>0</wpml:payloadPositionIndex>
                <wpml:dewarpingEnable>0</wpml:dewarpingEnable>
                <wpml:returnMode>singleReturnFirst</wpml:returnMode>
                <wpml:samplingRate>240000</wpml:samplingRate>
                <wpml:scanningMode>nonRepetitive</wpml:scanningMode>
                <wpml:modelColoringEnable>0</wpml:modelColoringEnable>
                <wpml:imageFormat>ir</wpml:imageFormat>
            </wpml:payloadParam>
        </Folder>
    </Document>
</kml>
"""


def _haversine_m(lon1: float, lat1: float, lon2: float, lat2: float) -> float:
    r = 6371000.0
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = (
        math.sin(dphi / 2.0) ** 2
        + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2.0) ** 2
    )
    return 2.0 * r * math.atan2(math.sqrt(a), math.sqrt(max(1e-12, 1.0 - a)))


def _heading_deg(lon1: float, lat1: float, lon2: float, lat2: float) -> float:
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    dlambda = math.radians(lon2 - lon1)
    x = math.sin(dlambda) * math.cos(phi2)
    y = math.cos(phi1) * math.sin(phi2) - math.sin(phi1) * math.cos(phi2) * math.cos(
        dlambda
    )
    brng = math.degrees(math.atan2(x, y))
    return (brng + 360.0) % 360.0


def polygon_to_waylines_wpml(polygon: Polygon, options: Optional[dict] = None) -> str:
    opts = options or {}
    profile = _drone_profile(str(opts.get("drohne", "M4T")))

    flughoehe = float(opts.get("flughöhe_m", 60))
    sichere_starthoehe = float(opts.get("sichere_starthöhe_m", max(20, flughoehe)))
    speed = max(0.1, float(opts.get("geschwindigkeit_ms", 8)))
    overlap_w = float(opts.get("seitlicher_überlapp_prozent", 30))
    direction = float(opts.get("direction", 0))
    drone = str(opts.get("drohne", "M4T"))
    finish_action = _map_finish_action(
        str(opts.get("aktion_beenden", "Rückkehrfunktion"))
    )

    preview = mapping_preview(
        polygon,
        altitude_m=flughoehe,
        side_overlap_percent=overlap_w,
        speed_mps=speed,
        drone=drone,
        direction_deg=direction,
    )
    line_segments = list(preview.get("lines_latlon") or [])

    coords = []
    for line_index, segment in enumerate(line_segments):
        if not segment or len(segment) < 2:
            continue
        points = [(float(lon), float(lat)) for lat, lon in segment]
        if line_index % 2 == 1:
            points.reverse()
        if coords and points and coords[-1] == points[0]:
            coords.extend(points[1:])
        else:
            coords.extend(points)

    if len(coords) < 2:
        fallback = [
            (float(lon), float(lat)) for lon, lat, *_ in polygon.exterior.coords
        ]
        if len(fallback) >= 2 and fallback[0] == fallback[-1]:
            fallback = fallback[:-1]
        coords = fallback

    if len(coords) < 2:
        raise ValueError("Polygon requires at least two coordinates for wayline")

    total_distance = 0.0
    for i in range(len(coords) - 1):
        total_distance += _haversine_m(
            coords[i][0], coords[i][1], coords[i + 1][0], coords[i + 1][1]
        )
    total_duration = total_distance / speed

    wayline_avoid = ""
    if profile["include_wayline_avoid"]:
        wayline_avoid = (
            "\n      <wpml:waylineAvoidLimitAreaMode>1</wpml:waylineAvoidLimitAreaMode>"
        )

    placemarks = []
    for idx, (lon, lat) in enumerate(coords):
        if idx < len(coords) - 1:
            next_lon, next_lat = coords[idx + 1]
        else:
            next_lon, next_lat = coords[idx]
        heading = _heading_deg(lon, lat, next_lon, next_lat)
        placemarks.append(
            f"""      <Placemark>
                <Point>
                    <coordinates>{_fmt_number(lon)},{_fmt_number(lat)}</coordinates>
                </Point>
                <wpml:index>{idx}</wpml:index>
                <wpml:executeHeight>{_fmt_number(flughoehe)}</wpml:executeHeight>
                <wpml:waypointSpeed>{_fmt_number(speed)}</wpml:waypointSpeed>
                <wpml:waypointHeadingParam>
                    <wpml:waypointHeadingMode>followWayline</wpml:waypointHeadingMode>
                    <wpml:waypointHeadingAngle>{_fmt_number(heading)}</wpml:waypointHeadingAngle>
                    <wpml:waypointPoiPoint>0.000000,0.000000,0.000000</wpml:waypointPoiPoint>
                    <wpml:waypointHeadingAngleEnable>0</wpml:waypointHeadingAngleEnable>
                    <wpml:waypointHeadingPathMode>followBadArc</wpml:waypointHeadingPathMode>
                    <wpml:waypointHeadingPoiIndex>0</wpml:waypointHeadingPoiIndex>
                </wpml:waypointHeadingParam>
                <wpml:waypointTurnParam>
                    <wpml:waypointTurnMode>coordinateTurn</wpml:waypointTurnMode>
                    <wpml:waypointTurnDampingDist>0</wpml:waypointTurnDampingDist>
                </wpml:waypointTurnParam>
                <wpml:useStraightLine>1</wpml:useStraightLine>
                <wpml:waypointGimbalHeadingParam>
                    <wpml:waypointGimbalPitchAngle>0</wpml:waypointGimbalPitchAngle>
                    <wpml:waypointGimbalYawAngle>0</wpml:waypointGimbalYawAngle>
                </wpml:waypointGimbalHeadingParam>
                <wpml:isRisky>0</wpml:isRisky>
                <wpml:waypointWorkType>0</wpml:waypointWorkType>
            </Placemark>"""
        )
    placemarks_xml = "\n".join(placemarks)

    return f"""<?xml version="1.0" encoding="UTF-8"?>
<kml xmlns="http://www.opengis.net/kml/2.2" xmlns:wpml="http://www.dji.com/wpmz/1.0.6">
    <Document>
        <wpml:missionConfig>
            <wpml:flyToWaylineMode>safely</wpml:flyToWaylineMode>
            <wpml:finishAction>{finish_action}</wpml:finishAction>
            <wpml:exitOnRCLost>executeLostAction</wpml:exitOnRCLost>
            <wpml:executeRCLostAction>goBack</wpml:executeRCLostAction>
            <wpml:takeOffSecurityHeight>{_fmt_number(sichere_starthoehe)}</wpml:takeOffSecurityHeight>
            <wpml:globalTransitionalSpeed>15</wpml:globalTransitionalSpeed>
            <wpml:droneInfo>
                <wpml:droneEnumValue>{profile["drone_enum"]}</wpml:droneEnumValue>
                <wpml:droneSubEnumValue>0</wpml:droneSubEnumValue>
            </wpml:droneInfo>{wayline_avoid}
            <wpml:payloadInfo>
                <wpml:payloadEnumValue>{profile["payload_enum"]}</wpml:payloadEnumValue>
                <wpml:payloadSubEnumValue>2</wpml:payloadSubEnumValue>
                <wpml:payloadPositionIndex>0</wpml:payloadPositionIndex>
            </wpml:payloadInfo>
        </wpml:missionConfig>
        <Folder>
            <wpml:templateId>0</wpml:templateId>
            <wpml:executeHeightMode>relativeToStartPoint</wpml:executeHeightMode>
            <wpml:waylineId>0</wpml:waylineId>
            <wpml:distance>{_fmt_number(total_distance)}</wpml:distance>
            <wpml:duration>{_fmt_number(total_duration)}</wpml:duration>
            <wpml:autoFlightSpeed>{_fmt_number(speed)}</wpml:autoFlightSpeed>
{placemarks_xml}
        </Folder>
    </Document>
</kml>
"""


def polygons_to_waylines_wpml(
    polygons: Sequence[Polygon],
    options: Optional[dict] = None,
    directions: Optional[Sequence[int]] = None,
) -> str:
    poly_list = list(polygons)
    if not poly_list:
        raise ValueError("polygons must not be empty")

    opts = options or {}
    profile = _drone_profile(str(opts.get("drohne", "M4T")))

    flughoehe = float(opts.get("flughöhe_m", 60))
    sichere_starthoehe = float(opts.get("sichere_starthöhe_m", max(20, flughoehe)))
    speed = max(0.1, float(opts.get("geschwindigkeit_ms", 8)))
    overlap_w = float(opts.get("seitlicher_überlapp_prozent", 30))
    drone = str(opts.get("drohne", "M4T"))
    finish_action = _map_finish_action(
        str(opts.get("aktion_beenden", "Rückkehrfunktion"))
    )

    global_coords = []
    for i, polygon in enumerate(poly_list):
        direction = float(opts.get("direction", 0))
        if directions and i < len(directions):
            direction = float(directions[i])

        preview = mapping_preview(
            polygon,
            altitude_m=flughoehe,
            side_overlap_percent=overlap_w,
            speed_mps=speed,
            drone=drone,
            direction_deg=direction,
        )
        line_segments = list(preview.get("lines_latlon") or [])

        coords = []
        for line_index, segment in enumerate(line_segments):
            if not segment or len(segment) < 2:
                continue
            points = [(float(lon), float(lat)) for lat, lon in segment]
            if line_index % 2 == 1:
                points.reverse()
            if coords and points and coords[-1] == points[0]:
                coords.extend(points[1:])
            else:
                coords.extend(points)

        if len(coords) < 2:
            fallback = [
                (float(lon), float(lat)) for lon, lat, *_ in polygon.exterior.coords
            ]
            if len(fallback) >= 2 and fallback[0] == fallback[-1]:
                fallback = fallback[:-1]
            coords = fallback

        if len(coords) < 2:
            raise ValueError("Polygon requires at least two coordinates for wayline")

        if global_coords and coords and global_coords[-1] == coords[0]:
            global_coords.extend(coords[1:])
        else:
            global_coords.extend(coords)

    if len(global_coords) < 2:
        raise ValueError("polygons require at least two coordinates for wayline")

    total_distance = 0.0
    for i in range(len(global_coords) - 1):
        total_distance += _haversine_m(
            global_coords[i][0],
            global_coords[i][1],
            global_coords[i + 1][0],
            global_coords[i + 1][1],
        )
    total_duration = total_distance / speed

    wayline_avoid = ""
    if profile["include_wayline_avoid"]:
        wayline_avoid = (
            "\n      <wpml:waylineAvoidLimitAreaMode>1</wpml:waylineAvoidLimitAreaMode>"
        )

    placemarks = []
    for idx, (lon, lat) in enumerate(global_coords):
        if idx < len(global_coords) - 1:
            next_lon, next_lat = global_coords[idx + 1]
        else:
            next_lon, next_lat = global_coords[idx]
        heading = _heading_deg(lon, lat, next_lon, next_lat)
        placemarks.append(
            f"""      <Placemark>
                <Point>
                    <coordinates>{_fmt_number(lon)},{_fmt_number(lat)}</coordinates>
                </Point>
                <wpml:index>{idx}</wpml:index>
                <wpml:executeHeight>{_fmt_number(flughoehe)}</wpml:executeHeight>
                <wpml:waypointSpeed>{_fmt_number(speed)}</wpml:waypointSpeed>
                <wpml:waypointHeadingParam>
                    <wpml:waypointHeadingMode>followWayline</wpml:waypointHeadingMode>
                    <wpml:waypointHeadingAngle>{_fmt_number(heading)}</wpml:waypointHeadingAngle>
                    <wpml:waypointPoiPoint>0.000000,0.000000,0.000000</wpml:waypointPoiPoint>
                    <wpml:waypointHeadingAngleEnable>0</wpml:waypointHeadingAngleEnable>
                    <wpml:waypointHeadingPathMode>followBadArc</wpml:waypointHeadingPathMode>
                    <wpml:waypointHeadingPoiIndex>0</wpml:waypointHeadingPoiIndex>
                </wpml:waypointHeadingParam>
                <wpml:waypointTurnParam>
                    <wpml:waypointTurnMode>coordinateTurn</wpml:waypointTurnMode>
                    <wpml:waypointTurnDampingDist>0</wpml:waypointTurnDampingDist>
                </wpml:waypointTurnParam>
                <wpml:useStraightLine>1</wpml:useStraightLine>
                <wpml:waypointGimbalHeadingParam>
                    <wpml:waypointGimbalPitchAngle>0</wpml:waypointGimbalPitchAngle>
                    <wpml:waypointGimbalYawAngle>0</wpml:waypointGimbalYawAngle>
                </wpml:waypointGimbalHeadingParam>
                <wpml:isRisky>0</wpml:isRisky>
                <wpml:waypointWorkType>0</wpml:waypointWorkType>
            </Placemark>"""
        )
    placemarks_xml = "\n".join(placemarks)

    return f"""<?xml version="1.0" encoding="UTF-8"?>
<kml xmlns="http://www.opengis.net/kml/2.2" xmlns:wpml="http://www.dji.com/wpmz/1.0.6">
    <Document>
        <wpml:missionConfig>
            <wpml:flyToWaylineMode>safely</wpml:flyToWaylineMode>
            <wpml:finishAction>{finish_action}</wpml:finishAction>
            <wpml:exitOnRCLost>executeLostAction</wpml:exitOnRCLost>
            <wpml:executeRCLostAction>goBack</wpml:executeRCLostAction>
            <wpml:takeOffSecurityHeight>{_fmt_number(sichere_starthoehe)}</wpml:takeOffSecurityHeight>
            <wpml:globalTransitionalSpeed>15</wpml:globalTransitionalSpeed>
            <wpml:droneInfo>
                <wpml:droneEnumValue>{profile["drone_enum"]}</wpml:droneEnumValue>
                <wpml:droneSubEnumValue>0</wpml:droneSubEnumValue>
            </wpml:droneInfo>{wayline_avoid}
            <wpml:payloadInfo>
                <wpml:payloadEnumValue>{profile["payload_enum"]}</wpml:payloadEnumValue>
                <wpml:payloadSubEnumValue>2</wpml:payloadSubEnumValue>
                <wpml:payloadPositionIndex>0</wpml:payloadPositionIndex>
            </wpml:payloadInfo>
        </wpml:missionConfig>
        <Folder>
            <wpml:templateId>0</wpml:templateId>
            <wpml:executeHeightMode>relativeToStartPoint</wpml:executeHeightMode>
            <wpml:waylineId>0</wpml:waylineId>
            <wpml:distance>{_fmt_number(total_distance)}</wpml:distance>
            <wpml:duration>{_fmt_number(total_duration)}</wpml:duration>
            <wpml:autoFlightSpeed>{_fmt_number(speed)}</wpml:autoFlightSpeed>
{placemarks_xml}
        </Folder>
    </Document>
</kml>
"""


def polygons_to_wpml_kml(
    polygons: Sequence[Polygon],
    options: Optional[dict] = None,
    directions: Optional[Sequence[int]] = None,
) -> str:
    poly_list = list(polygons)
    if not poly_list:
        raise ValueError("polygons must not be empty")

    opts = options or {}
    profile = _drone_profile(str(opts.get("drohne", "M4T")))

    flughoehe = float(opts.get("flughöhe_m", 60))
    sichere_starthoehe = float(opts.get("sichere_starthöhe_m", max(20, flughoehe)))
    speed = float(opts.get("geschwindigkeit_ms", 8))
    overlap_w = int(opts.get("seitlicher_überlapp_prozent", 30))
    margin = int(opts.get("rand", 0))
    elevation_optimize_enable = (
        1 if bool(opts.get("elevation_optimize_enable", True)) else 0
    )
    finish_action = _map_finish_action(
        str(opts.get("aktion_beenden", "Rückkehrfunktion"))
    )

    now_ms = int(time.time() * 1000)

    wayline_avoid = ""
    if profile["include_wayline_avoid"]:
        wayline_avoid = (
            "\n      <wpml:waylineAvoidLimitAreaMode>1</wpml:waylineAvoidLimitAreaMode>"
        )

    quick_ortho = ""
    if profile["include_quick_ortho"]:
        quick_ortho = (
            "\n        <wpml:quickOrthoMappingEnable>0</wpml:quickOrthoMappingEnable>"
        )

    placemarks = []
    for i, poly in enumerate(poly_list):
        direction = int(opts.get("direction", 0))
        if directions and i < len(directions):
            direction = int(directions[i])
        coords = _coordinates_text(poly)
        placemarks.append(
            f"""            <Placemark>
                <wpml:caliFlightEnable>0</wpml:caliFlightEnable>
                <wpml:elevationOptimizeEnable>{elevation_optimize_enable}</wpml:elevationOptimizeEnable>
                <wpml:smartObliqueEnable>0</wpml:smartObliqueEnable>{quick_ortho}
                <wpml:facadeWaylineEnable>0</wpml:facadeWaylineEnable>
                <wpml:isLookAtSceneSet>0</wpml:isLookAtSceneSet>
                <wpml:smartObliqueGimbalPitch>{profile["gimbal_pitch"]}</wpml:smartObliqueGimbalPitch>
                <wpml:shootType>time</wpml:shootType>
                <wpml:direction>{direction}</wpml:direction>
                <wpml:margin>{margin}</wpml:margin>
                <wpml:efficiencyFlightModeEnable>0</wpml:efficiencyFlightModeEnable>
                <wpml:overlap>
                    <wpml:orthoLidarOverlapH>80</wpml:orthoLidarOverlapH>
                    <wpml:orthoLidarOverlapW>{overlap_w}</wpml:orthoLidarOverlapW>
                    <wpml:orthoCameraOverlapH>80</wpml:orthoCameraOverlapH>
                    <wpml:orthoCameraOverlapW>{overlap_w}</wpml:orthoCameraOverlapW>
                </wpml:overlap>
                <Polygon>
                    <outerBoundaryIs>
                        <LinearRing>
                            <coordinates>
                                {coords}
                            </coordinates>
                        </LinearRing>
                    </outerBoundaryIs>
                </Polygon>
                <wpml:ellipsoidHeight>{_fmt_number(flughoehe)}</wpml:ellipsoidHeight>
                <wpml:height>{_fmt_number(flughoehe)}</wpml:height>
            </Placemark>"""
        )

    placemarks_xml = "\n".join(placemarks)
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<kml xmlns="http://www.opengis.net/kml/2.2" xmlns:wpml="http://www.dji.com/wpmz/1.0.6">
    <Document>
        <wpml:createTime>{now_ms}</wpml:createTime>
        <wpml:updateTime>{now_ms}</wpml:updateTime>
        <wpml:missionConfig>
            <wpml:flyToWaylineMode>safely</wpml:flyToWaylineMode>
            <wpml:finishAction>{finish_action}</wpml:finishAction>
            <wpml:exitOnRCLost>executeLostAction</wpml:exitOnRCLost>
            <wpml:executeRCLostAction>goBack</wpml:executeRCLostAction>
            <wpml:takeOffSecurityHeight>{_fmt_number(sichere_starthoehe)}</wpml:takeOffSecurityHeight>
            <wpml:globalTransitionalSpeed>15</wpml:globalTransitionalSpeed>
            <wpml:droneInfo>
                <wpml:droneEnumValue>{profile["drone_enum"]}</wpml:droneEnumValue>
                <wpml:droneSubEnumValue>0</wpml:droneSubEnumValue>
            </wpml:droneInfo>{wayline_avoid}
            <wpml:payloadInfo>
                <wpml:payloadEnumValue>{profile["payload_enum"]}</wpml:payloadEnumValue>
                <wpml:payloadSubEnumValue>2</wpml:payloadSubEnumValue>
                <wpml:payloadPositionIndex>0</wpml:payloadPositionIndex>
            </wpml:payloadInfo>
        </wpml:missionConfig>
        <Folder>
            <wpml:templateType>mapping2d</wpml:templateType>
            <wpml:templateId>0</wpml:templateId>
            <wpml:waylineCoordinateSysParam>
                <wpml:coordinateMode>WGS84</wpml:coordinateMode>
                <wpml:heightMode>relativeToStartPoint</wpml:heightMode>
                <wpml:globalShootHeight>{_fmt_number(flughoehe)}</wpml:globalShootHeight>
            </wpml:waylineCoordinateSysParam>
            <wpml:autoFlightSpeed>{_fmt_number(speed)}</wpml:autoFlightSpeed>
{placemarks_xml}
            <wpml:payloadParam>
                <wpml:payloadPositionIndex>0</wpml:payloadPositionIndex>
                <wpml:dewarpingEnable>0</wpml:dewarpingEnable>
                <wpml:returnMode>singleReturnFirst</wpml:returnMode>
                <wpml:samplingRate>240000</wpml:samplingRate>
                <wpml:scanningMode>nonRepetitive</wpml:scanningMode>
                <wpml:modelColoringEnable>0</wpml:modelColoringEnable>
                <wpml:imageFormat>ir</wpml:imageFormat>
            </wpml:payloadParam>
        </Folder>
    </Document>
</kml>
"""


def write_polygons_to_kmls(
    polys: Iterable[Polygon],
    out_dir: str,
    base_name: str,
    options: Optional[dict] = None,
    names: Optional[Sequence[str]] = None,
    directions: Optional[Sequence[int]] = None,
) -> int:
    poly_list = list(polys)
    Path(out_dir).mkdir(parents=True, exist_ok=True)
    file_stems = _build_output_stems(len(poly_list), base_name, names)

    count = 0
    for i, poly in enumerate(poly_list, start=1):
        file_stem = file_stems[i - 1]
        out_file = Path(out_dir) / f"{file_stem}.kml"
        item_options = dict(options or {})
        if directions and i - 1 < len(directions):
            item_options["direction"] = int(directions[i - 1])
        xml = polygon_to_wpml_kml(poly, options=item_options)
        out_file.write_text(xml, encoding="utf-8")
        count += 1
    return count


def write_to_kmls(polys: Iterable[Polygon], out_dir: str, base_name: str):
    Path(out_dir).mkdir(parents=True, exist_ok=True)
    write_polygons_to_kmls(polys, out_dir, base_name)


def write_polygons_to_kmzs(
    polys: Iterable[Polygon],
    out_dir: str,
    base_name: str,
    options: Optional[dict] = None,
    names: Optional[Sequence[str]] = None,
    directions: Optional[Sequence[int]] = None,
    debug_kml_dir: Optional[str] = None,
) -> int:
    poly_list = list(polys)
    out_path = Path(out_dir)
    out_path.mkdir(parents=True, exist_ok=True)
    file_stems = _build_output_stems(len(poly_list), base_name, names)

    count = 0
    for i, poly in enumerate(poly_list, start=1):
        file_stem = file_stems[i - 1]

        item_options = dict(options or {})
        if directions and i - 1 < len(directions):
            item_options["direction"] = int(directions[i - 1])

        xml = polygon_to_wpml_kml(poly, options=item_options)
        waylines_xml = polygon_to_waylines_wpml(poly, options=item_options)

        kmz_file = out_path / f"{file_stem}.kmz"
        with zipfile.ZipFile(
            kmz_file, mode="w", compression=zipfile.ZIP_DEFLATED
        ) as zf:
            zf.writestr("wpmz/template.kml", xml)
            zf.writestr("wpmz/waylines.wpml", waylines_xml)
            zf.writestr("doc.kml", xml)

        count += 1

    return count


def write_polygon_group_to_kmz(
    polygons: Sequence[Polygon],
    out_dir: str,
    file_stem: str,
    options: Optional[dict] = None,
    directions: Optional[Sequence[int]] = None,
    display_mode: str = "hull",
) -> Path:
    poly_list = list(polygons)
    if not poly_list:
        raise ValueError("polygons must not be empty")

    mode = str(display_mode or "hull").strip().lower()
    merged_geom = unary_union(poly_list)
    template_polygons: list[Polygon]
    template_directions: list[int] = list(int(d) for d in (directions or []))

    if mode == "bridge":
        components = list(merged_geom.geoms) if isinstance(merged_geom, MultiPolygon) else [merged_geom]
        components = [g for g in components if isinstance(g, Polygon) and not g.is_empty]

        if len(components) <= 1:
            display_geom = components[0] if components else merged_geom
            if isinstance(display_geom, Polygon):
                template_polygons = [display_geom]
            elif isinstance(display_geom, MultiPolygon):
                template_polygons = [max(display_geom.geoms, key=lambda g: g.area)]
            else:
                template_polygons = poly_list
        else:
            minx, miny, maxx, maxy = merged_geom.bounds
            span = max(maxx - minx, maxy - miny)

            # Thin but robust bridge width in degree-space.
            base_width = max(0.000003, min(0.00002, span * 0.00035))

            merged_parts = [components[0]]
            remaining = components[1:]
            connector_polys: list[Polygon] = []

            while remaining:
                best_idx = None
                best_dist = float("inf")
                best_pair = None
                for idx, candidate in enumerate(remaining):
                    for joined in merged_parts:
                        p1, p2 = nearest_points(joined, candidate)
                        dist = p1.distance(p2)
                        if dist < best_dist:
                            best_dist = dist
                            best_idx = idx
                            best_pair = (p1, p2)

                if best_idx is None or best_pair is None:
                    merged_parts.extend(remaining)
                    break

                chosen = remaining.pop(best_idx)
                merged_parts.append(chosen)
                p1, p2 = best_pair
                strip_geom = LineString([(float(p1.x), float(p1.y)), (float(p2.x), float(p2.y))]).buffer(
                    base_width / 2.0,
                    cap_style=2,
                    join_style=2,
                )
                if isinstance(strip_geom, Polygon) and not strip_geom.is_empty:
                    connector_polys.append(strip_geom)
                elif isinstance(strip_geom, MultiPolygon):
                    connector_polys.extend(
                        [g for g in strip_geom.geoms if isinstance(g, Polygon) and not g.is_empty]
                    )

            # Build ONE connected polygon so Pilot 2 shows one area object with preserved contours.
            build_geoms = list(components) + connector_polys
            display_geom = unary_union(build_geoms)

            # If still not connected, gradually increase strip width (still narrow).
            if isinstance(display_geom, MultiPolygon):
                grow_factors = (1.8, 2.6, 3.6)
                for factor in grow_factors:
                    widened = []
                    width = base_width * factor
                    for strip in connector_polys:
                        widened_geom = strip.buffer(width / 2.0, cap_style=2, join_style=2)
                        if isinstance(widened_geom, Polygon) and not widened_geom.is_empty:
                            widened.append(widened_geom)
                        elif isinstance(widened_geom, MultiPolygon):
                            widened.extend(
                                [g for g in widened_geom.geoms if isinstance(g, Polygon) and not g.is_empty]
                            )
                    display_geom = unary_union(list(components) + widened)
                    if isinstance(display_geom, Polygon):
                        break

            if isinstance(display_geom, Polygon):
                template_polygons = [display_geom]
            elif isinstance(display_geom, MultiPolygon):
                # Fallback: choose largest connected part instead of huge hull.
                template_polygons = [max(display_geom.geoms, key=lambda g: g.area)]
            else:
                template_polygons = [merged_geom.convex_hull]
    else:
        # Default: single hull display area for robust Pilot 2 rendering.
        display_geom = merged_geom.convex_hull
        if isinstance(display_geom, Polygon):
            display_polygon = display_geom
        elif isinstance(display_geom, MultiPolygon):
            display_polygon = display_geom.convex_hull
        else:
            display_polygon = display_geom.convex_hull
        template_polygons = [display_polygon]
        template_directions = [int(template_directions[0])] if template_directions else []

    if not template_polygons:
        raise ValueError("Could not create display geometry for group")
    template_polygons = [
        p for p in template_polygons if isinstance(p, Polygon) and not p.is_empty
    ]
    if not template_polygons:
        raise ValueError("Could not create valid template polygons for group")

    out_path = Path(out_dir)
    out_path.mkdir(parents=True, exist_ok=True)
    safe_stem = _sanitize_filename(file_stem)

    template_options = dict(options or {})
    template_xml = polygons_to_wpml_kml(
        template_polygons,
        options=template_options,
        directions=template_directions,
    )
    waylines_xml = polygons_to_waylines_wpml(
        poly_list,
        options=options,
        directions=directions,
    )

    kmz_file = out_path / f"{safe_stem}.kmz"
    with zipfile.ZipFile(kmz_file, mode="w", compression=zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("wpmz/template.kml", template_xml)
        zf.writestr("wpmz/waylines.wpml", waylines_xml)
        zf.writestr("doc.kml", template_xml)

    return kmz_file
