from __future__ import annotations
import csv, json
from pathlib import Path
from PIL import Image, ImageDraw
from geoviewplus_gstring_bitmap import BitmapHeader
from geoviewplus_bitmap_png import render_bitmap_rgba

ROOT = Path(__file__).resolve().parent
RAW = ROOT / "output" / "Alpha101_DESK"
OUT = ROOT / "output" / "Alpha103_DESK_PNG"
OUT.mkdir(parents=True, exist_ok=True)
rows = list(csv.DictReader((ROOT / "output" / "Alpha101_DESK_inventory.csv").open(
    encoding="utf-8", newline=""
)))
manifest = []
for row in rows:
    idx, width, height = int(row["index"]), int(row["width"]), int(row["height"])
    header = BitmapHeader(width, height, int(row["compact"]), int(row["bitmap_type"], 16))
    raw = (RAW / row["file"]).read_bytes()
    image = render_bitmap_rgba(header, raw)
    path = OUT / f"DESK_{idx:02d}_{width}x{height}.png"
    image.save(path)
    manifest.append({
        "index": idx, "width": width, "height": height,
        "format": header.format_code, "mask": header.has_mask,
        "png": str(path.relative_to(ROOT)),
    })

cards = []
for item in manifest:
    src = Image.open(ROOT / item["png"]).convert("RGBA")
    scale = max(3, min(8, 160 // max(src.size)))
    src = src.resize((src.width * scale, src.height * scale), Image.Resampling.NEAREST)
    card = Image.new("RGBA", (220, 170), (238, 238, 238, 255))
    draw = ImageDraw.Draw(card)
    for y in range(0, 150, 10):
        for x in range(0, 220, 10):
            if (x // 10 + y // 10) % 2:
                draw.rectangle((x, y, x + 9, y + 9), fill=(210, 210, 210, 255))
    card.alpha_composite(src, ((220 - src.width) // 2, (145 - src.height) // 2))
    ImageDraw.Draw(card).text(
        (8, 150),
        f'DESK {item["index"]:02d}  {item["width"]}x{item["height"]}  '
        f'{"4-bit" if item["format"] == 1 else "mono"}',
        fill=(0, 0, 0, 255),
    )
    cards.append(card)

sheet = Image.new("RGBA", (660, 510), (250, 250, 250, 255))
for i, card in enumerate(cards):
    sheet.alpha_composite(card, ((i % 3) * 220, (i // 3) * 170))
sheet.convert("RGB").save(OUT / "DESK_Alle_9_Vorschau.png")
(OUT / "manifest.json").write_text(
    json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8"
)
print(f"Rendered {len(manifest)} DESK PNG files")
