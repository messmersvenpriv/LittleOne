from fastkml import kml
import zipfile
from typing import List, Dict, Any, Optional, Union, Iterable, Tuple
from dataclasses import dataclass
from shapely.geometry import shape, Polygon, MultiPolygon, LinearRing
from html import unescape
import xml.etree.ElementTree as ET
from datetime import datetime, date
import re


def extract_kml_string_from_kmz(kmz_path: str) -> str:
    """
    Liest die erste KML-Datei aus einem KMZ-Archiv und gibt sie als UTF-8-String zurück.
    """
    with zipfile.ZipFile(kmz_path, "r") as zf:
        kml_name = next(n for n in zf.namelist() if n.lower().endswith(".kml"))
        return zf.read(kml_name).decode("utf-8")


# ==========================
# Datenmodell (vollständig)
# ==========================


@dataclass
class AreaFeature:
    id: Optional[str]
    name: Optional[str]
    props: Dict[str, Any]
    geom: Union[Polygon, MultiPolygon]
    style_url: Optional[str] = None

    def centroid_lonlat(self) -> Optional[tuple]:
        if self.geom is None:
            return None
        c = self.geom.centroid
        return (float(c.x), float(c.y))


# ==========================
# Datenmodell
# ==========================


@dataclass
class AreaSummary:
    """
    Aufbereitete Kerndaten je Fläche.
    - placemark_id:   ID aus dem KML (zur Nachverfolgbarkeit)
    - datum_mahd:     nur Datum (datetime.date) oder None
    - schlag_flurstueck: Originaltext (falls vorhanden)
    - antragsteller_vorname: extrahiert aus 'Antragsteller_Name' wenn möglich
    - antragsteller_name:    Nachname / Rest
    - antragsteller_telefon: bevorzugt 'Antragsteller_Telefon', sonst 'Antragsteller_Handy'
    - bekanntgabe_kitzrettung: bool oder None (falls unklar)
    - koordinaten:  Liste von Ringen; jeder Ring ist Liste[Tuple[lon, lat]]
                    [ [ (lon,lat), (lon,lat), ... ], [ ... (inner rings optional) ... ] ]
      (typischerweise 1 Ring = äußere Grenze, aber wir unterstützen mehrere)
    """

    placemark_id: Optional[str]
    datum_mahd: Optional[date]
    schlag_flurstueck: Optional[str]
    antragsteller_vorname: Optional[str]
    antragsteller_name: Optional[str]
    antragsteller_telefon: Optional[str]
    bekanntgabe_kitzrettung: Optional[bool]
    koordinaten: List[List[Tuple[float, float]]]


# ==========================
# Parser-Hilfsfunktionen
# ==========================


def _try_parse_number(s: str) -> Any:
    s_stripped = s.strip().replace(" ", "")
    try:
        if re.fullmatch(r"-?\d+", s_stripped):
            return int(s_stripped)
        return float(s_stripped)
    except ValueError:
        return s


def _try_parse_bool_or_null(s: str) -> Any:
    v = s.strip().lower()
    if v in ("null", ""):
        return None
    if v in ("ja", "yes", "true", "wahr"):
        return True
    if v in ("nein", "no", "false", "falsch"):
        return False
    return s


def _try_parse_datetime(s: str) -> Any:
    s_clean = s.strip()
    formats = [
        "%m/%d/%Y %I:%M:%S.%f %p",
        "%m/%d/%Y %I:%M:%S %p",
        "%m/%d/%Y %I:%M %p",
        "%m/%d/%Y",
        "%Y-%m-%d %H:%M:%S",
        "%Y-%m-%d",
        "%d.%m.%Y",  # falls mal deutsch formatiert
        "%d.%m.%Y %H:%M:%S",  # deutsch mit Zeit
        "%d.%m.%Y %H:%M",  # deutsch mit Zeit
    ]
    for fmt in formats:
        try:
            return datetime.strptime(s_clean, fmt)
        except ValueError:
            continue
    return s


def _normalize_value(s: str) -> Any:
    s_unescaped = unescape(s).strip()
    v = _try_parse_bool_or_null(s_unescaped)
    if isinstance(v, str):
        dt = _try_parse_datetime(v)
        if not isinstance(dt, str):
            return dt
        num = _try_parse_number(v)
        return num
    return v


def _parse_description_table(description_html: str) -> Dict[str, Any]:
    if not description_html:
        return {}
    html_text = unescape(description_html).strip()
    try:
        root = ET.fromstring(html_text)
    except ET.ParseError:
        start = html_text.lower().find("<table")
        end = html_text.lower().rfind("</table>")
        if start != -1 and end != -1:
            snippet = html_text[start : end + 8]
            root = ET.fromstring(snippet)
        else:
            return {}
    table = None
    if root.tag.lower() == "table":
        table = root
    else:
        for elem in root.iter():
            if isinstance(elem.tag, str) and elem.tag.lower() == "table":
                table = elem
                break
    if table is None:
        return {}
    props: Dict[str, Any] = {}
    for tr in table.findall(".//tr"):
        tds = tr.findall("td")
        if len(tds) == 2:
            key = "".join(tds[0].itertext()).strip()
            val = "".join(tds[1].itertext()).strip()
            if key:
                props[key] = _normalize_value(val)
    return props


def _iter_placemarks(obj) -> Iterable[kml.Placemark]:
    try:
        feats = list(obj.features())
    except Exception:
        feats = []
    for f in feats:
        if isinstance(f, kml.Placemark):
            yield f
        try:
            yield from _iter_placemarks(f)
        except Exception:
            continue


def _as_polygon_or_multipolygon(geom) -> Optional[Union[Polygon, MultiPolygon]]:
    if geom is None:
        return None
    try:
        if hasattr(geom, "geom_type"):
            gtype = geom.geom_type
            if gtype in ("Polygon", "MultiPolygon"):
                return geom
            if gtype == "GeometryCollection":
                polys = []
                for g in geom.geoms:
                    if g.geom_type == "Polygon":
                        polys.append(g)
                    elif g.geom_type == "MultiPolygon":
                        polys.extend(list(g.geoms))
                if not polys:
                    return None
                if len(polys) == 1:
                    return polys[0]
                return MultiPolygon(polys)
            return None
        else:
            shp = shape(geom)
            return _as_polygon_or_multipolygon(shp)
    except Exception:
        return None


# ==========================
# Hauptfunktionen
# ==========================


def parse_kmz_to_area_features(kmz_path: str) -> List[AreaFeature]:
    """
    Vollständige Features extrahieren (wie zuvor).
    """
    kml_text = extract_kml_string_from_kmz(kmz_path)
    kdoc = kml.KML()
    kdoc.from_string(kml_text.encode("utf-8"))

    features: List[AreaFeature] = []
    for pm in _iter_placemarks(kdoc):
        geom = _as_polygon_or_multipolygon(pm.geometry)
        if geom is None:
            continue
        desc = getattr(pm, "description", None) or ""
        props = _parse_description_table(desc)
        pm_id = getattr(pm, "id", None)
        pm_name = getattr(pm, "name", None)
        style_url = (
            getattr(pm, "styleUrl", None)
            if hasattr(pm, "styleUrl")
            else getattr(pm, "style_url", None)
        )

        features.append(
            AreaFeature(
                id=pm_id, name=pm_name, props=props, geom=geom, style_url=style_url
            )
        )

    # Fallback: falls fastkml keine Placemarks/Polygone geliefert hat (z.B. wegen Namespace-Varianten),
    # versuchen wir, das KML per ElementTree zu parsen und Polygone direkt auszulesen.
    if not features:
        try:
            features = _parse_kml_text_fallback(kml_text)
        except Exception:
            # Falls auch das fehlschlägt, behalten wir die leere Liste bei
            pass
    return features


# --------- Mapping  ---------


def _norm_key(key: str) -> str:
    """
    Vereinheitlicht Property-Schlüssel auf eine einfache Form:
    - lower-case
    - Umlaute ersetzt
    - nur alnum + underscore behalten
    - mehrfach-Varianten wie 'Schlag_Flurstueck', 'Schlag_Flurstück', 'Schlag/Flurstück' werden leichter gefunden
    """
    s = key.lower()
    # Umlaute
    s = s.replace("ä", "ae").replace("ö", "oe").replace("ü", "ue").replace("ß", "ss")
    # Trenner vereinheitlichen
    s = s.replace("/", "_").replace(" ", "_")
    # nur alnum + underscore
    s = re.sub(r"[^a-z0-9_]+", "", s)
    return s


def _get_prop(props: Dict[str, Any], candidates: List[str]) -> Optional[Any]:
    """
    Holt den ersten passenden Wert aus props, wobei keys normalisiert verglichen werden.
    candidates: Liste von erwarteten Varianten (bereits normalisierte Formen!)
    """
    # baue Map normalisiert -> original key
    norm_map: Dict[str, str] = {_norm_key(k): k for k in props.keys()}
    for cand in candidates:
        if cand in norm_map:
            return props[norm_map[cand]]
    # Soft-contains (für unerwartete leichte Abweichungen)
    for nk, ok in norm_map.items():
        for cand in candidates:
            if cand in nk:
                return props[ok]
    return None


def _to_date_only(value: Any) -> Optional[date]:
    """
    Nimmt Strings oder datetime und gibt nur date (ohne Zeit) zurück.
    Uhrzeit ist irrelevant.
    """
    if value is None:
        return None
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value
    if isinstance(value, str):
        dt = _try_parse_datetime(value)
        if isinstance(dt, datetime):
            return dt.date()
        if isinstance(dt, str):
            # weitere reine Datumsversuche
            for fmt in ("%m/%d/%Y", "%Y-%m-%d", "%d.%m.%Y"):
                try:
                    return datetime.strptime(value.strip(), fmt).date()
                except ValueError:
                    continue
            return None
        # falls _try_parse_datetime schon ein date geliefert hätte (tun wir oben nicht)
    return None


def _split_name(fullname: Optional[str]) -> Tuple[Optional[str], Optional[str]]:
    """
    Einfache Heuristik: Vorname = erstes Token, Nachname = rest (zusammengefügt).
    Falls nur ein Token vorhanden -> Vorname=None, Nachname=Original (oder umgekehrt?).
    Hier: Wir interpretieren letztes Wort als Nachname (häufiger korrekt, z.B. 'Karl Heinz Krebs').
    """
    if not fullname:
        return (None, None)
    # Trim doppelte Leerzeichen
    parts = [p for p in re.split(r"\s+", fullname.strip()) if p]
    if len(parts) == 1:
        # nur ein Teil -> wir behalten ihn als Nachname
        return (None, parts[0])
    # Vorname (alles außer letztes?) oder nur erstes? Du wolltest explizit Vorname, wenn es den gibt.
    # Wir nehmen das erste als Vorname, das letzte als Nachname, Mittelstücke kleben an den Vornamen.
    if len(parts) >= 2:
        vorname = " ".join(parts[:-1])
        nachname = parts[-1]
        return (vorname, nachname)
    return (None, " ".join(parts))


def _best_phone(props: Dict[str, Any]) -> Optional[str]:
    """
    Bevorzuge 'Antragsteller_Telefon', sonst 'Antragsteller_Handy'.
    Normalisiere grob (Spaces entfernen). Keine strenge Validierung.
    """
    tel = _get_prop(
        props,
        [
            "antragsteller_telefon",
            "telefon",  # mögliche Kurzform
        ],
    )
    if not tel:
        tel = _get_prop(
            props,
            [
                "antragsteller_handy",
                "handy",
                "mobil",
            ],
        )
    if isinstance(tel, str):
        t = tel.strip()
        # einfache Normalisierung: Leerzeichen raus
        t = re.sub(r"\s+", "", t)
        return t if t else None
    return None


def _extract_rings_lonlat(
    geom: Union[Polygon, MultiPolygon],
) -> List[List[Tuple[float, float]]]:
    """
    Liefert eine Liste von Ringen (Außen + ggf. Innenringe) in (lon, lat).
    KML-Koord. sind (lon,lat[,alt]).
    """

    def ring_to_lonlat(r: LinearRing) -> List[Tuple[float, float]]:
        # r.coords liefert (x,y[,z]) -> x=lon, y=lat
        return [(float(x), float(y)) for x, y, *_ in r.coords]

    rings: List[List[Tuple[float, float]]] = []
    if isinstance(geom, Polygon):
        rings.append(ring_to_lonlat(geom.exterior))
        for ir in geom.interiors:
            rings.append(ring_to_lonlat(ir))
        return rings

    if isinstance(geom, MultiPolygon):
        for poly in geom.geoms:
            rings.append(ring_to_lonlat(poly.exterior))
            for ir in poly.interiors:
                rings.append(ring_to_lonlat(ir))
        return rings

    return rings


def _parse_kml_text_fallback(kml_text: str) -> List[AreaFeature]:
    """
    Robuster Fallback-Parser: nutzt ElementTree, um Placemark-Polygone auszulesen
    falls fastkml aufgrund von Namespace-Varianten keine Features liefert.
    """
    feats: List[AreaFeature] = []
    try:
        root = ET.fromstring(kml_text)
    except ET.ParseError:
        # versuche Strip BOM/whitespace
        root = ET.fromstring(kml_text.strip())

    # Suche alle Placemark-Elemente (Namespace-unabhängig)
    for pm in root.iter():
        if not isinstance(pm.tag, str):
            continue
        tag_local = pm.tag.split("}")[-1].lower()
        if tag_local != "placemark":
            continue

        # id-Attribut
        pm_id = pm.get("id")

        # name
        name = None
        for c in pm:
            if isinstance(c.tag, str) and c.tag.split("}")[-1].lower() == "name":
                name = (c.text or "").strip()
                break

        # description (HTML-Table erwartet)
        desc = ""
        for c in pm:
            if isinstance(c.tag, str) and c.tag.split("}")[-1].lower() == "description":
                desc = c.text or ""
                break

        # styleUrl
        style_url = None
        for c in pm:
            if isinstance(c.tag, str) and c.tag.split("}")[-1].lower() == "styleurl":
                style_url = (c.text or "").strip()
                break

        props = _parse_description_table(desc)

        # Suche Polygon/LinearRing/coordinates unterhalb des Placemark
        geom_polys = []
        for node in pm.iter():
            if not isinstance(node.tag, str):
                continue
            if node.tag.split("}")[-1].lower() == "coordinates":
                coords_text = (node.text or "").strip()
                if not coords_text:
                    continue
                pts = []
                for part in re.split(r"\s+", coords_text.strip()):
                    if not part:
                        continue
                    comps = part.split(",")
                    if len(comps) >= 2:
                        try:
                            lon = float(comps[0])
                            lat = float(comps[1])
                            pts.append((lon, lat))
                        except ValueError:
                            continue
                if len(pts) >= 3:
                    try:
                        poly = Polygon(pts)
                        if poly.is_valid and not poly.is_empty:
                            geom_polys.append(poly)
                    except Exception:
                        continue

        # Für jeden Polygon ein Feature anlegen (falls mehrere Ringe vorhanden sind, nehmen wir das erste als äußere Grenze)
        for g in geom_polys:
            feats.append(
                AreaFeature(
                    id=pm_id, name=name, props=props, geom=g, style_url=style_url
                )
            )

    return feats


def polygons_from_kml(kml_text: str) -> List[Polygon]:
    """Gibt eine Liste von Shapely-Polygone aus einem KML-Text zurück (sowohl fastkml- als auch Fallback-Parsing)."""
    polys: List[Polygon] = []
    try:
        kdoc = kml.KML()
        kdoc.from_string(kml_text.encode("utf-8"))
        for pm in _iter_placemarks(kdoc):
            geom = _as_polygon_or_multipolygon(pm.geometry)
            if geom is None:
                continue
            if isinstance(geom, Polygon):
                polys.append(geom)
            elif isinstance(geom, MultiPolygon):
                for p in geom.geoms:
                    polys.append(p)
    except Exception:
        polys = []

    if not polys:
        # Fallback
        feats = _parse_kml_text_fallback(kml_text)
        for f in feats:
            if isinstance(f.geom, Polygon):
                polys.append(f.geom)
            elif isinstance(f.geom, MultiPolygon):
                for p in f.geom.geoms:
                    polys.append(p)

    return polys


def summarize_features(features: List[AreaFeature]) -> List[AreaSummary]:
    """
    Transformiert vollständige Features in deine gewünschte AreaSummary-Struktur.
    """
    summaries: List[AreaSummary] = []

    for feat in features:
        props = feat.props

        # Kandidatenlisten (normalisierte Schlüssel!)
        key_datum_mahd = [
            "datum_mahd",
            "geplantes_datum_mahd",  # falls mal nur dieses vorhanden ist
            "datum",  # Fallback
        ]
        key_schlag = [
            "schlag_flurstueck",
            "schlagflurstueck",
            "schlag_flurstuecke",
            "schlagflurstuecke",
            "schlag",
            "flurstueck",
            "flurstuecke",
        ]
        key_name = [
            "antragsteller_name",  # im Beispiel
            "name",  # Fallback (unspezifisch; wird nur genutzt, wenn oben fehlt)
        ]
        key_bekanntgabe = [
            "bekanntgabe_kitzrettung",
            "bekanntgabekitzrettung",
            "kitzrettung_bekanntgabe",
        ]

        datum_raw = _get_prop(props, key_datum_mahd)
        datum_only = _to_date_only(datum_raw)

        schlag = _get_prop(props, key_schlag)
        if isinstance(schlag, (int, float)):
            schlag = str(schlag)

        full_name = _get_prop(props, key_name)
        # In deinen Beispielen ist 'Antragsteller_Name' oft nur Vorname ('Bernd', 'Hartmut', 'Otto').
        # Wir splitten trotzdem nach Heuristik:
        vorname, nachname = _split_name(
            full_name if isinstance(full_name, str) else None
        )

        telefon = _best_phone(props)

        bekanntgabe_val = _get_prop(props, key_bekanntgabe)
        if isinstance(bekanntgabe_val, str):
            b = bekanntgabe_val.strip().lower()
            if b in ("ja", "yes", "true", "wahr"):
                bekanntgabe_bool = True
            elif b in ("nein", "no", "false", "falsch"):
                bekanntgabe_bool = False
            else:
                bekanntgabe_bool = None
        elif isinstance(bekanntgabe_val, bool):
            bekanntgabe_bool = bekanntgabe_val
        else:
            bekanntgabe_bool = None

        koords = _extract_rings_lonlat(feat.geom)

        summaries.append(
            AreaSummary(
                placemark_id=feat.id,
                datum_mahd=datum_only,
                schlag_flurstueck=(
                    schlag if isinstance(schlag, str) and schlag else None
                ),
                antragsteller_vorname=vorname,
                antragsteller_name=nachname,
                antragsteller_telefon=telefon,
                bekanntgabe_kitzrettung=bekanntgabe_bool,
                koordinaten=koords,
            )
        )

    return summaries


# ==========================
# Bequeme Ein-Funktion-Pipeline
# ==========================


def parse_kmz_to_area_summaries(kmz_path: str) -> List[AreaSummary]:
    """
    Direkt von KMZ → deine AreaSummary-Objekte.
    """
    feats = parse_kmz_to_area_features(kmz_path)
    return summarize_features(feats)
