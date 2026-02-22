from pathlib import Path
import sys

sys.path.append(str(Path(__file__).resolve().parents[1] / "src"))
from LittleOne import kmz_reader

p = Path(r"C:\LittleOne\data\start\2299_files.kmz")
text = kmz_reader.extract_kml_string_from_kmz(str(p))
text = kmz_reader._sanitize_kml_text(text)
idx = 746
start = max(0, idx - 40)
end = idx + 40
snippet = text[start:end]
print("Context index range:", start, end)
print(repr(snippet))
print("\nChars and ordinals:")
for i, ch in enumerate(snippet):
    print(start + i, ch, ord(ch))
