# GeoViewPlus 0.5 – Alpha103

Alpha103 ergänzt die Alpha102-Bitmap-Rasterdaten um die RGB-Farbzuordnung des PC/GEOS-2.x-VGA16-Treibers und rendert die neun extrahierten DESK-Moniker als RGBA-PNG.

- VGA16-Palette direkt aus `vga16Palette.asm`
- Transparente Maskenbereiche
- 1-Bit-Moniker in Schwarz/Weiß
- 8-Bit-Bitmaps bleiben bis zur Ermittlung einer passenden 256-Farben-Palette bewusst ausgeschlossen
- Private Token-Datenbank und Installationsarchive sind nicht im Paket enthalten

Dokumentation: `docs/GeoViewPlus_0.5_Alpha103_VGA16_Palette_und_PNG_Rendering.md`

Tests mit privater Testdatenbank: 39/39 bestanden.

Vorschau: `output/Alpha103_DESK_PNG/DESK_Alle_9_Vorschau.png`
