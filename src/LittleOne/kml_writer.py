from pathlib import Path
from typing import Iterable, Optional, Sequence
import time
import re
import zipfile
from shapely.geometry import Polygon


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

    count = 0
    for i, poly in enumerate(poly_list, start=1):
        if names and i - 1 < len(names) and names[i - 1]:
            file_stem = _sanitize_filename(names[i - 1])
        else:
            file_stem = _sanitize_filename(f"{base_name}-{i:03d}")
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

    count = 0
    for i, poly in enumerate(poly_list, start=1):
        if names and i - 1 < len(names) and names[i - 1]:
            file_stem = _sanitize_filename(names[i - 1])
        else:
            file_stem = _sanitize_filename(f"{base_name}-{i:03d}")

        item_options = dict(options or {})
        if directions and i - 1 < len(directions):
            item_options["direction"] = int(directions[i - 1])

        xml = polygon_to_wpml_kml(poly, options=item_options)

        kmz_file = out_path / f"{file_stem}.kmz"
        with zipfile.ZipFile(
            kmz_file, mode="w", compression=zipfile.ZIP_DEFLATED
        ) as zf:
            zf.writestr("wpmz/template.kml", xml)
            zf.writestr("doc.kml", xml)

        count += 1

    return count
