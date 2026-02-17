
import typer
from pathlib import Path
from . import kmz_reader, kml_writer, optimize_angle, dji_rules

app = typer.Typer(help="KMZ → (DJI-kompatible) KMLs konvertieren und optimieren.")

@app.command()
def convert(
    kmz: Path = typer.Argument(..., exists=True, readable=True),
    out: Path = typer.Option(Path("out"), "--out", "-o"),
    base_name: str = typer.Option("area", "--name", "-n"),
    add_z: bool = typer.Option(True, help="Z=0 ergänzen, falls fehlt"),
):
    """
    Liest ein KMZ (ArcGIS-Export), extrahiert Polygone und schreibt einzelne KMLs.
    """
    kml_text = kmz_reader.extract_kml_string_from_kmz(str(kmz))
    polys = kmz_reader.polygons_from_kml(kml_text)
    if not polys:
        typer.secho("Keine Polygone gefunden.", fg=typer.colors.RED, err=True)
        raise typer.Exit(2)

    # DJI-Validierung/Normalisierung
    norm = [dji_rules.normalize_polygon(p, add_z_if_missing=add_z) for p in polys]
    out.mkdir(parents=True, exist_ok=True)
    kml_writer.write_polygons_to_kmls(norm, str(out), base_name)
    typer.secho(f"Erfolgreich: {len(norm)} KMLs in {out}", fg=typer.colors.GREEN)

@app.command()
def optimize(
    kml_file: Path = typer.Argument(..., exists=True, readable=True),
    out: Path = typer.Option(Path("out"), "--out", "-o"),
    mode: str = typer.Option("mrr", help="'mrr' oder Grad (0-179)"),
):
    """
    Ermittelt/übernimmt optimalen Grid-Winkel (nur Analyse; z. B. für Dateiname).
    """
    from fastkml import kml as kmlmod
    from shapely.geometry import shape, Polygon

    text = kml_file.read_text(encoding="utf-8")
    doc = kmlmod.KML(); doc.from_string(text.encode("utf-8"))
    polys = []
    for f1 in doc.features():
        for f2 in getattr(f1, "features", lambda: [])():
            for f3 in getattr(f2, "features", lambda: [])():
                g = getattr(f3, "geometry", None)
                if g:
                    shp = shape(g.__geo_interface__)
                    if shp.geom_type == "Polygon": polys.append(shp)

    if not polys:
        typer.secho("Keine Polygone im KML.", fg=typer.colors.RED, err=True); raise typer.Exit(2)

    ang = optimize_angle.mrr_angle_deg(polys[0]) if mode == "mrr" else float(mode)
    out.mkdir(parents=True, exist_ok=True)
    out_file = out / f"{kml_file.stem}_angle_{int(round(ang))}.txt"
    out_file.write_text(f"{ang:.3f}", encoding="utf-8")
    typer.secho(f"Winkel={ang:.3f}° → {out_file.name}", fg=typer.colors.GREEN)

if __name__ == "__main__":
    app()
