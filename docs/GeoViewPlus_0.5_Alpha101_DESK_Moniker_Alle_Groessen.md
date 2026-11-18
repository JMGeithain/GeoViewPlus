# GeoViewPlus 0.5 Alpha101 – alle neun DESK-Moniker dekodiert

Alpha101 dekodiert alle neun Varianten des Tokens `DESK` in der untersuchten privaten PC/GEOS-2.x-Token-Datenbank. Es kommen zwei Befehle vor: `0x51=GR_DRAW_BITMAP_CP` und `0x4D=GR_FILL_BITMAP_CP`. Beide Strukturen sind Opcode-Byte, WORD-Blockgröße, Bitmap-Header und Bitmapdaten; danach folgt in allen Fällen `GR_END_GSTRING` (0).

| Index | VisMoniker-Typ | Größe | Befehl | Blockbytes | Komprimierung | Bitmaptyp | Rohbytes |
|---:|---:|---:|---|---:|---|---:|---:|
| 0 | 0x46 | 64×40 | DRAW_BITMAP_CP | 166 | PackBits | 0x11 (4 Bit + Maske) | 1600 |
| 1 | 0x41 | 64×40 | FILL_BITMAP_CP | 86 | PackBits | 0x00 (Mono) | 320 |
| 2 | 0x46 | 48×30 | DRAW_BITMAP_CP | 620 | PackBits | 0x11 (4 Bit + Maske) | 900 |
| 3 | 0x41 | 48×30 | FILL_BITMAP_CP | 186 | unkomprimiert | 0x00 (Mono) | 180 |
| 4 | 0x46 | 32×20 | DRAW_BITMAP_CP | 348 | PackBits | 0x11 (4 Bit + Maske) | 400 |
| 5 | 0x41 | 32×20 | FILL_BITMAP_CP | 86 | unkomprimiert | 0x00 (Mono) | 80 |
| 6 | 0x61 | 48×14 | FILL_BITMAP_CP | 90 | unkomprimiert | 0x00 (Mono) | 84 |
| 7 | 0x41 | 15×15 | FILL_BITMAP_CP | 36 | unkomprimiert | 0x00 (Mono) | 30 |
| 8 | 0x61 | 15×10 | FILL_BITMAP_CP | 26 | unkomprimiert | 0x00 (Mono) | 20 |

Die drei DRAW-Varianten sind 4-Bit-Bitmaps mit Maske und PackBits-Komprimierung. Die sechs FILL-Varianten sind monochrom; davon ist eine PackBits-komprimiert und fünf sind unkomprimiert. Die Größen stimmen mit den erwarteten einfachen Bitmap-Rohgrößen überein.

**Grenze:** Die Rohbytes sind extrahiert und längenkonsistent. Alpha101 interpretiert noch keine Paletteneinträge, Maskenpolarität oder Pixelreihenfolge und erzeugt daher noch keine farbtreue Icon-Vorschau. Die privaten Quelldaten wurden nicht in das Repository aufgenommen.

Quellen:
- [CInclude/graphics.h](https://github.com/bluewaysw/pcgeos/blob/01c7a0172688aa72cc29898eb832dd5915d49cf7/CInclude/graphics.h) – Opcode- und Bitmap-Konstanten.
- [CInclude/gstring.h](https://github.com/bluewaysw/pcgeos/blob/01c7a0172688aa72cc29898eb832dd5915d49cf7/CInclude/gstring.h) – OpFillBitmapAtCP und OpDrawBitmapAtCP, jeweils Opcode plus WORD-Größe.
- [Include/gstring.def](https://github.com/bluewaysw/pcgeos/blob/01c7a0172688aa72cc29898eb832dd5915d49cf7/Include/gstring.def) – Zuordnung der Befehle zum Bitmap-Parser.
