# GeoViewPlus 0.5 Alpha100 – GString-Bitmap-Extraktion

## Umfang

Alpha100 ergänzt einen konservativen, read-only Decoder für genau einen nachgewiesenen GString-Befehl: `GR_DRAW_BITMAP_CP` (Opcode `0x51`). Es wird noch kein allgemeiner GString-Interpreter und kein farbtreuer Icon-Renderer behauptet.

Die Implementierung in `geoviewplus_gstring_bitmap.py` prüft den Opcode, liest das nachfolgende WORD als Länge des eingebetteten Bitmap-Blocks, liest den sechs Byte langen Bitmap-Header, dekodiert `BMCompact=BMC_PACKBITS`, prüft die erwartete Größe einfacher unterstützter Bitmaps und verlangt als Abschluss genau `GR_END_GSTRING` (0). Die entpackten Bytes bleiben Rohdaten; Palette und Maskenpixel werden nicht interpretiert.

## Nachweis am DESK-Moniker

Untersucht wurde die erste Monikervariante des Tokens `DESK` in der privaten PC/GEOS-2.x-Token-Datenbank `token_da(2).000`. Die Binärdatei wird weder verändert noch in dieses Paket oder das öffentliche Repository übernommen.

| Feld | Verifizierter Wert |
|---|---:|
| Token | `DESK` |
| Moniker-DB-Gruppe / Item | `0x0140 / 0x000E` |
| VisMoniker-Typbyte | `0x46` |
| VisMoniker-Größe | 64 × 40 |
| GString-Opcode | `0x51` = `GR_DRAW_BITMAP_CP` |
| Bitmap-Block-Länge | 166 Bytes |
| Bitmap-Breite / Höhe | 64 × 40 |
| BMCompact | `1` = `BMC_PACKBITS` |
| Bitmap-Typ | `0x11` = Maskenbit gesetzt, Formatcode `1` (`BMF_4BIT`) |
| komprimierte Bitmapdaten nach 6-Byte-Header | 160 Bytes |
| entpackte Bitmapdaten | 1.600 Bytes |
| erwartete Größe | 1.600 Bytes |
| abschließender GString-Befehl | `0x00` = `GR_END_GSTRING` |

Die Größenprüfung: `(64 × 4 / 8 + 64 / 8) × 40 = (32 + 8) × 40 = 1.600 Bytes`. Die Daten werden als Rohdaten behandelt; Reihenfolge und Semantik der Masken-/Bilddaten sowie die 16-Farben-Palette werden noch nicht gerendert.

SHA-256 der entpackten 1.600 Rohbytes: `fc9ec119ecaf2efb86ccdd1a7474bd785feb23ba7ea7f5ea89b50425848830c0`.

## Quellenabgleich

- [CInclude/graphics.h](https://github.com/bluewaysw/pcgeos/blob/01c7a0172688aa72cc29898eb832dd5915d49cf7/CInclude/graphics.h): `GR_DRAW_BITMAP_CP=81` (`0x51`), `BMC_PACKBITS=1`, `BMF_4BIT=1`, `BMT_MASK=0x10), Bitmap-Header.
- [CInclude/gstring.h](https://github.com/bluewaysw/pcgeos/blob/01c7a0172688aa72cc29898eb832dd5915d49cf7/CInclude/gstring.h): `OpDrawBitmapAtCP` ist Opcode plus WORD-Größe; `GSDrawBitmapAtCP` bestätigt die Bytefolge.

Das PackBits-Verhalten wurde anhand der tatsächlichen Datenlänge und der erwarteten 1.600 Byte validiert. Der Decoder bricht bei abgeschnittenen Literal-/Wiederholungsfolgen, Größenüberschreitungen und unerwarteten Folgeelementen ab.

## Grenzen / nächste Schritte

- Keine Interpretation der 4-Bit-Farbwerte oder Maskenpixel.
- Keine Aussage zur Palette oder zum Nibble-/Scanline-Layout.
- Keine Dekodierung der übrigen acht DESK-Moniker; deren GString-Elemente werden erst nach separater Opcode-/Längenprüfung angefasst.
- Kein Eingriff in GeoWorks 1.x; dieser Schritt betrifft ausschließlich PC/GEOS 2.x.
