import zipfile
from typing import List, Dict, Any, Optional, Union, Iterable, Tuple
from dataclasses import dataclass
from html import unescape
from pathlib import Path
import xml.etree.ElementTree as ET
from datetime import datetime, date
import re
from shapely.geometry import shape, Polygon, MultiPolygon, LinearRing

kml = None


def _get_fastkml_module():
    global kml
    if kml is not None:
        return kml
    try:
        from fastkml import kml as kml_module

        kml = kml_module
        return kml
    except Exception:
        return None


@dataclass
class AreaFeature:
    """Rohe Fläche aus dem KML/KMZ mit Properties und Geometrie."""

    id: Optional[str]
    name: Optional[str]
    props: Dict[str, Any]
    geom: Optional[Union[Polygon, MultiPolygon]]
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
    # ElementTree ist bei embedded HTML oft zu strikt. Versuche ET, sonst Fallback per Regex.
    try:
        root = ET.fromstring(html_text)
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
    except ET.ParseError:
        # Tolerante Regex-Variante: suche <table>...</table> und <tr><td>k</td><td>v</td></tr>
        tbl_match = re.search(
            r"<table[\s\S]*?>[\s\S]*?</table>", html_text, flags=re.IGNORECASE
        )
        if not tbl_match:
            return {}
        table_html = tbl_match.group(0)
        props = {}
        for tr in re.findall(
            r"<tr[\s\S]*?>[\s\S]*?</tr>", table_html, flags=re.IGNORECASE
        ):
            tds = re.findall(r"<td[\s\S]*?>([\s\S]*?)</td>", tr, flags=re.IGNORECASE)
            if len(tds) >= 2:
                key = re.sub(r"<[^>]+>", "", tds[0]).strip()
                val = re.sub(r"<[^>]+>", "", tds[1]).strip()
                if key:
                    props[key] = _normalize_value(val)
        return props


def _iter_placemarks(obj) -> Iterable[Any]:
    try:
        feats = list(obj.features())
    except Exception:
        feats = []
    for f in feats:
        if f.__class__.__name__.lower() == "placemark":
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


def extract_all_kml_strings_from_kmz(kmz_path: str) -> List[Tuple[str, str]]:
    """Extrahiere alle .kml Dateien aus einem .kmz (Zip) und liefere Liste (name, text)."""
    texts: List[Tuple[str, str]] = []
    try:
        with zipfile.ZipFile(kmz_path, "r") as z:
            for info in z.infolist():
                if info.filename.lower().endswith(".kml"):
                    try:
                        data = z.read(info.filename)
                        try:
                            txt = data.decode("utf-8")
                        except Exception:
                            txt = data.decode("utf-8", "replace")
                        texts.append((info.filename, txt))
                    except Exception:
                        continue
    except Exception:
        return []
    return texts


def extract_kml_string_from_kmz(kmz_path: str) -> str:
    """Liefert den besten KML-Text aus einem KMZ.

    Bevorzugt `doc.kml`, sonst die erste gefundene .kml-Datei.
    """
    texts = extract_all_kml_strings_from_kmz(kmz_path)
    if not texts:
        return ""

    for name, txt in texts:
        if Path(name).name.lower() == "doc.kml":
            return txt
    return texts[0][1]


def _sanitize_kml_text(text: str) -> str:
    """Entferne problematische Steuerzeichen und sorge für einen String.

    Diese Funktion ist defensiv: sie decodiert Bytes, entfernt NULL/control
    chars und ersetzt sie durch sichere Äquivalente.
    """
    if text is None:
        return ""
    if not isinstance(text, str):
        try:
            text = text.decode("utf-8")
        except Exception:
            try:
                text = text.decode("latin-1")
            except Exception:
                text = str(text)
    # entferne C0-Steuerzeichen außer Tab, LF, CR
    text = re.sub(r"[\x00-\x08\x0B\x0C\x0E-\x1F]", "", text)
    return text


def parse_kmz_to_area_features(kmz_path: str) -> List[AreaFeature]:
    """
    Vollständige Features extrahieren (wie zuvor).
    """
    # Unterstütze KMZ mit mehreren KML-Dateien: sammle alle KML-Texte
    kml_texts: List[Tuple[str, str]] = []
    if kmz_path.lower().endswith(".kmz"):
        kml_texts = extract_all_kml_strings_from_kmz(kmz_path)
    else:
        # Treat as plain KML file path
        kml_texts = [(kmz_path, Path(kmz_path).read_text(encoding="utf-8"))]

    features: List[AreaFeature] = []
    for name, kml_text in kml_texts:
        # sanitize and parse each KML text
        kml_text = _sanitize_kml_text(kml_text)
        kml_module = _get_fastkml_module()
        parsed_fastkml = False
        if kml_module is not None:
            try:
                kdoc = kml_module.KML()
                kdoc.from_string(kml_text)
                for pm in _iter_placemarks(kdoc):
                    geom = _as_polygon_or_multipolygon(pm.geometry)
                    desc = getattr(pm, "description", None) or ""
                    props = _parse_description_table(desc)
                    # Zusätzlich ExtendedData / SchemaData auslesen (SimpleData / Data)
                    pm_element = getattr(pm, "_element", None)
                    if pm_element is not None:
                        for node in pm_element.iter():
                            if not isinstance(node.tag, str):
                                continue
                            tag_local = node.tag.split("}")[-1].lower()
                            if tag_local == "simpledata":
                                name = node.get("name") or node.get("id")
                                val = (node.text or "").strip()
                                if name and name not in props:
                                    props[name] = _normalize_value(val)
                            elif tag_local == "data":
                                name = node.get("name")
                                # find <value>
                                val = ""
                                for ch in node:
                                    if (
                                        isinstance(ch.tag, str)
                                        and ch.tag.split("}")[-1].lower() == "value"
                                    ):
                                        val = (ch.text or "").strip()
                                        break
                                if name and name not in props:
                                    props[name] = _normalize_value(val)
                    pm_id = getattr(pm, "id", None)
                    pm_name = getattr(pm, "name", None)
                    style_url = (
                        getattr(pm, "styleUrl", None)
                        if hasattr(pm, "styleUrl")
                        else getattr(pm, "style_url", None)
                    )
                    features.append(
                        AreaFeature(
                            id=pm_id,
                            name=pm_name,
                            props=props,
                            geom=geom,
                            style_url=style_url,
                        )
                    )
                parsed_fastkml = True
            except Exception:
                parsed_fastkml = False

        if not parsed_fastkml:
            features.extend(_parse_kml_text_fallback(kml_text))

    # Ergänze Ergebnisse durch einen ElementTree/Regex-Fallback (einige Placemarks werden
    # von fastkml unter Umständen nicht korrekt geliefert). Wir mergen nach Placemark-ID
    # (falls vorhanden) und füllen fehlende Geometrien auf.
    # Ergänze zusätzlich Features aus einem Fallback-Scan (falls vorhanden)
    try:
        # fallback über alle Texte (falls mehrere KMLs)
        fallback_feats: List[AreaFeature] = []
        for _, kml_text in kml_texts:
            try:
                fallback_feats.extend(_parse_kml_text_fallback(kml_text))
            except Exception:
                continue
    except Exception:
        fallback_feats = []

    existing_ids = {f.id for f in features if f.id}
    # Merge: falls fallback Feature neue ID hat, oder existing has no geom but fallback has, update
    for fb in fallback_feats:
        if fb.id and fb.id in existing_ids:
            # update existing feature if it lacks geometry
            for ex in features:
                if ex.id == fb.id:
                    if (
                        ex.geom is None or getattr(ex.geom, "is_empty", False)
                    ) and fb.geom is not None:
                        ex.geom = fb.geom
                    # merge props: keep existing keys, extend missing
                    for k, v in fb.props.items():
                        if k not in ex.props:
                            ex.props[k] = v
                    break
        else:
            features.append(fb)
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
    Bevorzuge 'Antragsteller_Handy' (Mobil), sonst 'Antragsteller_Telefon'.
    Normalisiere grob (Spaces entfernen). Keine strenge Validierung.
    """
    # prefer mobile fields first
    tel = _get_prop(
        props,
        [
            "antragsteller_handy",
            "handy",
            "mobil",
        ],
    )
    if not tel:
        tel = _get_prop(
            props,
            [
                "antragsteller_telefon",
                "telefon",  # mögliche Kurzform
            ],
        )
    # Akzeptiere auch numerische Werte (kommen durch _normalize_value vor)
    if isinstance(tel, (int, float)):
        return str(int(tel))
    if isinstance(tel, str):
        t = tel.strip()
        # Ersetze NBSP etc., entferne überflüssige Leerzeichen
        t = t.replace("\u00a0", " ")
        t = re.sub(r"\s+", "", t)
        # Normalisiere gängige Trennzeichen: erhalte +, (), -, / ; entferne andere Zeichen
        t = re.sub(r"[^0-9\+\-\/()]+", "", t)
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
    # sanitize before attempting to parse with ElementTree
    kml_text = _sanitize_kml_text(kml_text)
    try:
        root = ET.fromstring(kml_text)
    except ET.ParseError:
        # versuche Strip BOM/whitespace
        try:
            root = ET.fromstring(kml_text.strip())
        except ET.ParseError:
            # letzter Fallback: extrahiere Placemark-Snippets per Regex und parse diese einzeln
            feats = []
            placemarks = re.findall(
                r"(<Placemark[\s\S]*?</Placemark>)", kml_text, flags=re.IGNORECASE
            )
            for pm_snip in placemarks:
                try:
                    pm_elem = ET.fromstring(pm_snip)
                except ET.ParseError:
                    # überspringe defekte Placemark
                    continue

                pm_id = pm_elem.get("id")
                name = None
                desc = ""
                style_url = None
                for c in pm_elem:
                    if isinstance(c.tag, str):
                        t = c.tag.split("}")[-1].lower()
                        if t == "name":
                            name = (c.text or "").strip()
                        elif t == "description":
                            desc = c.text or ""
                        elif t == "styleurl":
                            style_url = (c.text or "").strip()

                props = _parse_description_table(desc)
                geom_polys = []
                for node in pm_elem.iter():
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

                # Kombiniere mehrere Polygone zu einem MultiPolygon, falls nötig
                geom_final = None
                if len(geom_polys) == 1:
                    geom_final = geom_polys[0]
                elif len(geom_polys) > 1:
                    try:
                        geom_final = MultiPolygon(geom_polys)
                    except Exception:
                        geom_final = None

                feats.append(
                    AreaFeature(
                        id=pm_id,
                        name=name,
                        props=props,
                        geom=geom_final,
                        style_url=style_url,
                    )
                )

            return feats

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
        # Ergänze ExtendedData / SchemaData falls vorhanden
        for node in pm.iter():
            if not isinstance(node.tag, str):
                continue
            tag_local = node.tag.split("}")[-1].lower()
            if tag_local == "simpledata":
                name = node.get("name") or node.get("id")
                val = (node.text or "").strip()
                if name and name not in props:
                    props[name] = _normalize_value(val)
            elif tag_local == "data":
                name = node.get("name")
                val = ""
                for ch in node:
                    if (
                        isinstance(ch.tag, str)
                        and ch.tag.split("}")[-1].lower() == "value"
                    ):
                        val = (ch.text or "").strip()
                        break
                if name and name not in props:
                    props[name] = _normalize_value(val)

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

        # Kombiniere mehrere Polygone zu einem MultiPolygon, falls nötig;
        # lege ein einzelnes AreaFeature pro Placemark an (geom kann None sein).
        geom_final = None
        if len(geom_polys) == 1:
            geom_final = geom_polys[0]
        elif len(geom_polys) > 1:
            try:
                geom_final = MultiPolygon(geom_polys)
            except Exception:
                geom_final = None

        feats.append(
            AreaFeature(
                id=pm_id, name=name, props=props, geom=geom_final, style_url=style_url
            )
        )

    return feats


def polygons_from_kml(kml_text: str) -> List[Polygon]:
    """Gibt eine Liste von Shapely-Polygone aus einem KML-Text zurück (sowohl fastkml- als auch Fallback-Parsing)."""
    polys: List[Polygon] = []
    # sanitize before parsing
    kml_text = _sanitize_kml_text(kml_text)
    kml_module = _get_fastkml_module()
    if kml_module is not None:
        try:
            kdoc = kml_module.KML()
            kdoc.from_string(kml_text)
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
        key_nachname = [
            "antragsteller_nachname",
            "nachname",
            "lastname",
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
        # Falls nur ein Name-Feld vorhanden ist, kann es "Vorname Nachname" oder
        # "Nachname, Vorname" enthalten. Versuche eine robuste Aufteilung.
        if isinstance(full_name, str) and full_name.strip():
            nm = full_name.strip()
            # Komma-getrennt ("Nachname, Vorname")
            if "," in nm:
                parts = [p.strip() for p in nm.split(",") if p.strip()]
                if len(parts) >= 2:
                    vorname = parts[1]
                    nachname = parts[0]
                else:
                    vorname, nachname = _split_name(nm)
            else:
                vorname, nachname = _split_name(nm)
        else:
            vorname, nachname = _split_name(None)

        # Heuristik: Wenn das einzelne Namensfeld nur einen Token enthielt und
        # es ein separates 'nachname' Feld in props gibt, dann ist es
        # wahrscheinlich so, dass das einzelne Feld der Vorname ist und das
        # separate Feld der Nachname. Korrigiere das.
        if (
            isinstance(full_name, str)
            and full_name.strip()
            and vorname is None
            and isinstance(nachname, str)
            and len(nachname.split()) == 1
        ):
            alt_n = _get_prop(props, key_nachname)
            if alt_n and isinstance(alt_n, str) and alt_n.strip():
                # Nutze das Einzel-Feld als Vorname und das separate Nachname-Feld
                vorname = full_name.strip()
                nachname = alt_n.strip()

        telefon = _best_phone(props)

        # Wenn nur 'Antragsteller_Telefon' vorhanden ist, kopiere es in 'Antragsteller_Handy'
        # damit ältere Datenformate Handynummern unter dem Handy-Feld erhalten.
        tel_raw = (
            _get_prop(props, ["antragsteller_telefon", "telefon"])
            if isinstance(props, dict)
            else None
        )
        mobile_raw = (
            _get_prop(props, ["antragsteller_handy", "handy", "mobil"])
            if isinstance(props, dict)
            else None
        )
        if not mobile_raw and tel_raw:
            # setze fallback key so that later lookups find it
            try:
                props["Antragsteller_Handy"] = tel_raw
            except Exception:
                pass
            # recompute telefon value
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

        koords = _extract_rings_lonlat(feat.geom) if feat.geom is not None else []

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
