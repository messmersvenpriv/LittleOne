#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
import os
import sys
from pathlib import Path
from typing import Any
from urllib.parse import urlencode
from urllib.request import Request, urlopen


def _http_json(
    url: str, params: dict[str, Any], method: str = "POST"
) -> dict[str, Any]:
    payload = urlencode(params).encode("utf-8")
    req = Request(url=url, data=payload if method == "POST" else None, method=method)
    if method == "GET":
        req = Request(url=f"{url}?{urlencode(params)}", method="GET")

    with urlopen(req, timeout=60) as response:
        charset = response.headers.get_content_charset() or "utf-8"
        raw = response.read().decode(charset, errors="replace")

    try:
        data = json.loads(raw)
    except json.JSONDecodeError as ex:
        raise RuntimeError(f"Ungültige JSON-Antwort von {url}: {ex}") from ex

    if "error" in data:
        err = data["error"]
        code = err.get("code", "?")
        msg = err.get("message", "Unbekannter Fehler")
        details = "; ".join(err.get("details", []) or [])
        detail_text = f" ({details})" if details else ""
        raise RuntimeError(f"ArcGIS-Fehler {code}: {msg}{detail_text}")

    return data


def _normalize_layer_url(service_url: str, layer_id: int) -> str:
    url = service_url.strip().rstrip("/")
    lower = url.lower()

    if "/featureserver/" in lower:
        return url

    if lower.endswith("/featureserver"):
        return f"{url}/{layer_id}"

    raise ValueError(
        "Ungültige URL. Erwartet wird .../FeatureServer oder .../FeatureServer/<layerId>."
    )


def _fetch_layer_info(layer_url: str, token: str) -> dict[str, Any]:
    return _http_json(layer_url, {"f": "json", "token": token}, method="GET")


def _fetch_all_features(
    layer_url: str,
    token: str,
    chunk_size: int,
    with_geometry: bool,
) -> tuple[list[dict[str, Any]], str]:
    ids_info = _http_json(
        f"{layer_url}/query",
        {
            "f": "json",
            "where": "1=1",
            "returnIdsOnly": "true",
            "token": token,
        },
    )

    object_ids = sorted(ids_info.get("objectIds") or [])
    oid_field = ids_info.get("objectIdFieldName") or "OBJECTID"

    if not object_ids:
        return [], oid_field

    all_features: list[dict[str, Any]] = []
    total = len(object_ids)

    for start in range(0, total, chunk_size):
        part = object_ids[start : start + chunk_size]
        id_list = ",".join(str(v) for v in part)
        where = f"{oid_field} IN ({id_list})"

        data = _http_json(
            f"{layer_url}/query",
            {
                "f": "json",
                "where": where,
                "outFields": "*",
                "returnGeometry": str(with_geometry).lower(),
                "token": token,
            },
        )

        features = data.get("features") or []
        all_features.extend(features)

        done = min(start + chunk_size, total)
        print(f"Geladen: {done}/{total}")

    return all_features, oid_field


def _extract_rows(
    features: list[dict[str, Any]],
    field_names: list[str],
    with_geometry: bool,
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []

    for feat in features:
        attrs = feat.get("attributes") or {}
        row = {name: attrs.get(name) for name in field_names}

        if with_geometry:
            geom = feat.get("geometry") or {}
            if "x" in geom and "y" in geom:
                row["X"] = geom.get("x")
                row["Y"] = geom.get("y")
            else:
                row["GEOMETRY_JSON"] = json.dumps(geom, ensure_ascii=False)

        rows.append(row)

    return rows


def _write_csv(rows: list[dict[str, Any]], out_path: Path) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)

    columns: list[str] = []
    for row in rows:
        for key in row.keys():
            if key not in columns:
                columns.append(key)

    with out_path.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=columns)
        writer.writeheader()
        writer.writerows(rows)


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Exportiert einen ArcGIS Feature Layer per REST in CSV. "
            "Ohne Jahresfilter: alle vorhandenen Jahre werden automatisch mit exportiert."
        )
    )
    parser.add_argument(
        "--service-url",
        required=True,
        help="URL wie .../FeatureServer oder .../FeatureServer/<layerId>",
    )
    parser.add_argument(
        "--layer-id",
        type=int,
        default=0,
        help="Nur relevant, wenn service-url auf .../FeatureServer endet (Default: 0)",
    )
    parser.add_argument(
        "--token",
        default=os.getenv("ARCGIS_TOKEN"),
        help="ArcGIS Token; alternativ Umgebungsvariable ARCGIS_TOKEN verwenden",
    )
    parser.add_argument(
        "--chunk-size",
        type=int,
        default=500,
        help="Anzahl OBJECTIDs pro Query (Default: 500)",
    )
    parser.add_argument(
        "--no-geometry",
        action="store_true",
        help="Geometrie nicht exportieren",
    )
    parser.add_argument(
        "--out",
        default="data/arcgis_exports/Rehkitz_Fundort.csv",
        help="Ausgabepfad für CSV",
    )
    return parser


def main() -> int:
    parser = build_arg_parser()
    args = parser.parse_args()

    if not args.token:
        print(
            "Fehler: Kein Token vorhanden. Nutze --token oder setze ARCGIS_TOKEN.",
            file=sys.stderr,
        )
        return 2

    try:
        layer_url = _normalize_layer_url(args.service_url, args.layer_id)
        with_geometry = not args.no_geometry

        info = _fetch_layer_info(layer_url, args.token)
        layer_name = info.get("name") or "Unbekannt"
        field_names = [
            f.get("name") for f in (info.get("fields") or []) if f.get("name")
        ]

        print(f"Layer: {layer_name}")
        print(f"URL:   {layer_url}")

        features, oid_field = _fetch_all_features(
            layer_url=layer_url,
            token=args.token,
            chunk_size=max(1, args.chunk_size),
            with_geometry=with_geometry,
        )

        if not features:
            print("Keine Features gefunden.")
            return 0

        rows = _extract_rows(features, field_names, with_geometry=with_geometry)

        out_path = Path(args.out)
        _write_csv(rows, out_path)

        print(f"OBJECTID-Feld: {oid_field}")
        print(f"Features:      {len(features)}")
        print(f"CSV:           {out_path}")
        return 0
    except Exception as ex:
        print(f"Fehler: {ex}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
