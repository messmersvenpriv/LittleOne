import typer
from pathlib import Path
from . import kmz_reader, kml_writer, dji_rules, optimize_angle

app = typer.Typer(help='KMZ → DJI-KML umwandeln')

@app.command()
def convert(kmz: Path, out: Path = Path('out'), name: str = 'area'):
    text = kmz_reader.extract_kml_string_from_kmz(str(kmz)) if kmz.suffix.lower()=='.kmz' else kmz.read_text(encoding='utf-8')
    polys = kmz_reader.polygons_from_kml(text)
    norm = [dji_rules.normalize_polygon(p, add_z_if_missing=True) for p in polys]
    out.mkdir(parents=True, exist_ok=True)
    kml_writer.write_polygons_to_kmls(norm, str(out), name)
    print(f'OK: {len(norm)} KMLs in {out}')

@app.command()
def angle(kml: Path, out: Path = Path('out')):
    from fastkml import kml as kmlmod
    from shapely.geometry import shape
    text = kml.read_text(encoding='utf-8')
    doc = kmlmod.KML(); doc.from_string(text.encode('utf-8'))
    polys=[]
    for f1 in doc.features():
        for f2 in getattr(f1, 'features', lambda: [])():
            for f3 in getattr(f2, 'features', lambda: [])():
                g = getattr(f3, 'geometry', None)
                if g:
                    shp = shape(g.__geo_interface__)
                    if shp.geom_type=='Polygon': polys.append(shp)
    if not polys: raise SystemExit('Keine Polygone')
    ang = optimize_angle.mrr_angle_deg(polys[0])
    out.mkdir(parents=True, exist_ok=True)
    (out/ f"{kml.stem}_angle.txt").write_text(f"{ang:.3f}", encoding='utf-8')
    print(f'Winkel: {ang:.3f}°')
