# GeoViewPlus 0.5 – Alpha103: VGA16-Palette und PNG-Rendering

## Ergebnis

Alpha103 ergänzt Alpha102 um die RGB-Farbzuordnung des PC/GEOS-2.x-VGA16-Treibers und rendert die neun in Alpha101 extrahierten DESK-Moniker als RGBA-PNG.

## Warum genau diese Palette?

Die bereitgestellte PC/GEOS-Ensemble-Installation enthält in `ensemble/geos.ini` den Eintrag `driver = vga16.geo`. Der PC/GEOS-Quellstand `01c7a0172688aa72cc29898eb832dd5915d49cf7` enthält `Driver/Video/VGAlike/VGA16/vga16Palette.asm`. Der Dateikopf beschreibt die Tabelle ausdrücklich als Standardpalette des VGA16-Treibers. Die ersten 16 RGB-Einträge sind die Farbwerte für die 4-Bit-Indizes 0 bis 15.

| Index | Farbe laut Quellkommentar | RGB |
|---:|---|---|
| 0 | black | (0, 0, 0) |
| 1 | dk blue | (0, 0, 170) |
| 2 | dk green | (0, 170, 0) |
| 3 | dk cyan | (0, 170, 170) |
| 4 | dk red | (170, 0, 0) |
| 5 | dk violet | (170, 0, 170) |
| 6 | brown | (170, 85, 0) |
| 7 | dk grey | (170, 170, 170) |
| 8 | lt grey | (85, 85, 85) |
| 9 | lt blue | (85, 85, 255) |
| 10 | lt green | (85, 255, 85) |
| 11 | lt cyan | (85, 255, 255) |
| 12 | lt red | (255, 85, 85) |
| 13 | lt violet | (255, 85, 255) |
| 14 | yellow | (255, 255, 85) |
| 15 | white | (255, 255, 255) |

Dies ist die VGA16-Palette. Sie wird nicht als universelle Palette für alle PC/GEOS-Videotreiber ausgegeben. Andere Treiber oder benutzerdefinierte Paletten können andere RGB-Werte liefern.

## Implementierung

Neue Module:

- `geoviewplus_palette.py`: 16 RGB-Einträge und sichere Indexabfrage.
- `geoviewplus_bitmap_png.py`: RGBA-Renderer für einfache 1-Bit- und 4-Bit-Bitmaps.
- `render_alpha103_desk.py`: reproduzierbarer Renderer für die neun Alpha101-DESK-Rohdateien.
- `test_geoviewplus_palette_png.py`: Tests für Palettenwerte, Nibble-Auswertung, Maske und Monochromdarstellung.

Die 4-Bit-Pixel werden mit der VGA16-Palette eingefärbt. Die sechs monochromen DESK-Varianten werden mit gesetztem Bit als schwarze Tinte und gelöschtem Bit als weißem Papier ausgegeben. Maskenbits mit Wert 1 behalten das Pixel; maskierte Pixel werden in der PNG transparent.

8-Bit-Bitmaps werden bewusst noch nicht gerendert, weil dafür eine passende 256-Farben-Palette benötigt wird.

## Beobachtung bei DESK-Variante 0

Die erste 64×40-Variante (Index 0, 4-Bit mit Maske) enthält in den extrahierten Maskenzeilen ausschließlich Nullbits. Nach der in Alpha102 anhand der GEOS-Routine `MaskOffPixels` bestätigten Maskenregel ist damit kein Pixel sichtbar; die erzeugte PNG ist vollständig transparent. Ob diese Variante im ursprünglichen Desktop-Kontext absichtlich leer ist oder ob ihr eine andere Rolle zukommt, ist ohne Vergleich in einer laufenden PC/GEOS-Umgebung nicht abschließend bestätigt.

## Testergebnis

Mit der privaten Token-Datenbank `token_da(2).000` als lokalem Testdatensatz:

`Ran 39 tests in 0.089s – OK`

Alle 39 Tests liefen erfolgreich, einschließlich der Integrationstests für die neun DESK-Moniker. Die private Token-Datenbank und die PC/GEOS-Installationsarchive sind nicht Bestandteil des Quellpakets.

## Quellen

- [VGA16-Standardpalette – vga16Palette.asm](https://github.com/bluewaysw/pcgeos/blob/01c7a0172688aa72cc29898eb832dd5915d49cf7/Driver/Video/VGAlike/VGA16/vga16Palette.asm)
- [PC/GEOS-Grafiktreiber-Schnittstelle – videoDr.def](https://github.com/bluewaysw/pcgeos/blob/01c7a0172688aa72cc29898eb832dd5915d49cf7/Include/Internal/videoDr.def)
- [Bitmap- und Maskenstrukturen – graphics.def](https://github.com/bluewaysw/pcgeos/blob/01c7a0172688aa72cc29898eb832dd5915d49cf7/Include/graphics.def)
- [Maskenverarbeitung – exportBitmap.asm](https://github.com/bluewaysw/pcgeos/blob/01c7a0172688aa72cc29898eb832dd5915d49cf7/Library/Trans/Graphics/Vector/EPS/Export/exportBitmap.asm)

## Abgrenzung

Diese Arbeit bezieht sich ausschließlich auf PC/GEOS 2.x und den VGA16-Treiber. Sie ist keine Aussage über GeoWorks 1.x.
