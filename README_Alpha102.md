# GeoViewPlus 0.5 – Alpha102

Alpha102 ergänzt den Alpha101-DESK-Moniker-Decoder um eine verifizierte Aufteilung der einfachen PC/GEOS-Bitmapdaten in Masken- und Bilddaten sowie die Expansion von 1-/4-/8-Bit-Pixelindizes.

**Wichtig:** Noch keine farbtreue PNG-Vorschau. Die drei DESK-4-Bit-Bitmaps besitzen keine eingebettete Palette; PC/GEOS verwendet dafür GPT_DEFAULT. Die tatsächliche Systempalette muss separat aus der passenden Laufzeitumgebung ermittelt werden.

Details: [Alpha102-Dokumentation](docs/GeoViewPlus_0.5_Alpha102_Bitmap_Pixel_Mask_Layout.md)

Neue Dateien:
- geoviewplus_bitmap_raster.py
- test_geoviewplus_bitmap_raster.py

Validierung: 34 Tests bestanden, einschließlich aller neun DESK-Varianten aus der privaten Testdatenbank. Die private Token-Datenbank ist nicht Bestandteil des Pakets.
