from pathlib import Path
import zipfile

p = Path(r"C:\LittleOne\data\start\2299_files.kmz")
with zipfile.ZipFile(p, "r") as zf:
    kml_name = next(n for n in zf.namelist() if n.lower().endswith(".kml"))
    data = zf.read(kml_name)
print("Bytes length:", len(data))
idx = 746
start = max(0, idx - 40)
end = idx + 40
snippet = data[start:end]
print("Context bytes range:", start, end)
print(snippet[:200])
print("\nByte values:")
for i, b in enumerate(snippet):
    print(start + i, b, chr(b) if 32 <= b < 127 else ".")
