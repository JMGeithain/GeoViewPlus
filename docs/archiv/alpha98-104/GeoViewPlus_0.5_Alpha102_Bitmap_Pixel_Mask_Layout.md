# GeoViewPlus 0.5 – Alpha102: Bitmap-Pixel- und Maskenlayout

## Ziel

Alpha102 untersucht die Pixeldaten der in Alpha101 extrahierten neun DESK-Moniker. Es wird bewusst noch keine RGB-Palette fest eingebaut: Die drei 4-Bit-Bitmaps enthalten laut Header keine eigene Palette. PC/GEOS greift in diesem Fall auf die zur Laufzeit gelieferte System-Standardpalette zurück.

## Verifizierte PC/GEOS-Quelltextbefunde

Untersuchte Referenz ist der PC/GEOS-Quellstand `01c7a0172688aa72cc29898eb832dd5915d49cf7` im Repository `bluewaysw/pcgeos`.

1. `Include/graphics.def` definiert `BMT_MASK` als zusätzliche Maskenebene, `BMT_PALETTE` als Kennzeichen einer mitgelieferten Palette und `BMT_COMPLEX` als Kennzeichen für komplexe Bitmaps. Die einfache `Bitmap`-Struktur besteht aus Breite, Höhe, Kompressionsart und Typ. Die komplexe `CBitmap`-Struktur besitzt dagegen Offsets `CB_data` und `CB_palette`.
2. `Library/Trans/Graphics/Vector/EPS/Export/exportBitmap.asm`, Routine `CalcLineSize`, berechnet die Bilddaten pro Scanline und addiert bei gesetztem `BMT_MASK` die Maskenbytes hinzu.
3. `Library/Trans/Graphics/Vector/EPS/Export/exportBitmap.asm`, Routine `MaskOffPixels`, zeigt die Reihenfolge explizit: Der Zeiger beginnt auf der Maske (Kommentar `mask comes first`); nach `ceil(width/8)` Bytes beginnt die Pixeldatenebene. Die Maske wird für jede Scanline separat verarbeitet.
4. Dieselbe Routine startet das Maskenbit mit `0x80` und schiebt es nach rechts. Das höchstwertige Bit steht damit für das linke Pixel. Ein gesetztes Maskenbit lässt das Pixel unverändert; ein gelöschtes Bit wird als maskiertes Pixel behandelt.
5. `EmitColorScan` verarbeitet 4-Bit-Pixel zuerst aus dem hohen Nibble und anschließend aus dem niedrigen Nibble. Pixel 0 liegt somit im High-Nibble, Pixel 1 im Low-Nibble.
6. `SetupBitmapPalette` verwendet bei fehlender Bitmap-Palette `GPT_DEFAULT` über `GrGetPalette`. Die konkrete RGB-Farbzuordnung ist daher nicht in diesen einfachen Bitmapdaten enthalten und kann vom Laufzeit-System abhängen.

## Alpha102-Implementierung

Neue Datei: `geoviewplus_bitmap_raster.py`

- Unterstützt einfache PC/GEOS-Bitmaps mit 1-, 4- und 8-Bit-Indizes.
- Trennt die Daten scanlineweise in Maskenbytes und Bildbytes.
- Liest Maskenbits MSB-first.
- Liest 4-Bit-Pixel High-Nibble-first.
- Liefert Pixelindizes und optionale Sichtbarkeits-/Opacity-Masken als Zeilenarrays.
- Weist komplexe Bitmaps und unpassende Datenlängen zurück.
- Erfindet keine RGB-Farben und erzeugt deshalb noch keine farbtreue PNG-Vorschau.

## DESK-Befund

Die Alpha101-Auswertung enthält neun DESK-Varianten. Drei sind 4-Bit-Bitmaps mit Maske (`B_type=0x11`), sechs sind monochrome Bitmaps ohne Maske (`B_type=0x00`). Alle neun lassen sich mit dem Alpha102-Rasterdecoder in die erwartete Anzahl von Pixelzeilen zerlegen.

Für die drei 4-Bit-Varianten gilt: `BMT_PALETTE` und `BMT_COMPLEX` sind nicht gesetzt. Sie besitzen somit keine eingebettete Palette; die genaue Farbdarstellung erfordert die passende PC/GEOS-Systempalette. Alpha102 behauptet daher keine farbgetreue Darstellung.

## Tests

Mit privater Token-Datenbank `token_da(2).000` (nur lokal; nicht Bestandteil des Pakets):

```text
Ran 34 tests
OK
```

## Quellen

- [graphics.def](https://github.com/bluewaysw/pcgeos/blob/01c7a0172688aa72cc29898eb832dd5915d49cf7/Include/graphics.def)
- [graphicsRasterDraw.asm](https://github.com/bluewaysw/pcgeos/blob/01c7a0172688aa72cc29898eb832dd5915d49cf7/Library/Kernel/Graphics/graphicsRasterDraw.asm)
- [exportBitmap.asm](https://github.com/bluewaysw/pcgeos/blob/01c7a0172688aa72cc29898eb832dd5915d49cf7/Library/Trans/Graphics/Vector/EPS/Export/exportBitmap.asm)

## Abgrenzung

Diese Analyse bezieht sich ausschließlich auf PC/GEOS 2.x-Quelltext und die dazugehörige Token-Datenbank. Sie ist keine Aussage über GeoWorks 1.x.
