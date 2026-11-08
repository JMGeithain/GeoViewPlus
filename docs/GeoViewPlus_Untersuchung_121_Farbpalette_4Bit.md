# GeoViewPlus – Untersuchung 121
## GeoWorks 1.x: 4-Bit-Farbmoniker, RGB-Zuordnung und Nibble-Reihenfolge

**Quelle:** bereitgestelltes `GEOWORKS.zip`, deutsche GeoWorks-1.x-Installation.  
**Untersuchte Dateien:** `GEOWORKS/WORLD/DUMP.GEO`, `GEOWORKS/WORLD/COLOR.GEO`, `GEOWORKS/COLOR1.INI`, `GEOWORKS/SYSTEM/EGA.GEO`, `GEOWORKS/SYSTEM/VGA.GEO`, `GEOWORKS/KERNEL.OLD`.

## 1. Befund in DUMP.GEO

In `DUMP.GEO` sind PostScript-Prozeduren zur Ausgabe von Bitmapdaten enthalten. Die Datei definiert drei 16 Einträge lange Tabellen: `redMap`, `greenMap` und `blueMap`.

Die Prozedur `mapPixels` extrahiert aus jedem Byte zuerst das hohe Nibble (`-4 bitshift`) und danach das niedrige Nibble (`15 and`). Beide Nibbles werden über die drei Farbtabellen in Rot-, Grün- und Blaukomponenten umgesetzt.

**Belegt:** Im untersuchten 4-Bit-Pixelausgabepfad wird das hohe Nibble zuerst verarbeitet. Ein Decoder, der die Nibbles vertauscht, vertauscht benachbarte Pixel.

## 2. 16-Farben-Tabelle

Die Tabellenwerte (Komponenten 0–15) und die rechnerisch auf 8 Bit skalierten RGB-Werte:

| Index | R | G | B | RGB |
|---:|---:|---:|---:|---|
| 0 | 0 | 0 | 0 | (0, 0, 0) |
| 1 | 0 | 0 | 10 | (0, 0, 170) |
| 2 | 0 | 10 | 0 | (0, 170, 0) |
| 3 | 0 | 10 | 10 | (0, 170, 170) |
| 4 | 10 | 0 | 0 | (170, 0, 0) |
| 5 | 10 | 0 | 10 | (170, 0, 170) |
| 6 | 10 | 5 | 0 | (170, 85, 0) |
| 7 | 10 | 10 | 10 | (170, 170, 170) |
| 8 | 5 | 5 | 5 | (85, 85, 85) |
| 9 | 5 | 5 | 15 | (85, 85, 255) |
| 10 | 5 | 15 | 5 | (85, 255, 85) |
| 11 | 5 | 15 | 15 | (85, 255, 255) |
| 12 | 15 | 5 | 5 | (255, 85, 85) |
| 13 | 15 | 5 | 15 | (255, 85, 255) |
| 14 | 15 | 15 | 5 | (255, 255, 85) |
| 15 | 15 | 15 | 15 | (255, 255, 255) |

Die 8-Bit-Werte entstehen durch Multiplikation der 4-Bit-Komponenten mit 17. Das ist eine Darstellungsumrechnung für GeoViewPlus, kein zusätzlicher Wert aus der Datei.

## 3. COLOR1.INI

`COLOR1.INI` ist 384 Bytes groß; SHA-256: `5bd34a3217210c470e3b145ee76abf85d634c3a7a0b385b4dcf53920fd2c0fa7`.

Die Bytes lassen sich als 128 RGB-Tripel lesen. Die ersten 64 Tripel bilden einen 4×4×4-RGB-Würfel mit Komponentenwerten 0, 21, 42 und 63; die folgenden 64 Tripel sind Null. Das passt zu einer 64-Farben-Auswahl-/Farbkonfiguration, beweist aber nicht, dass diese Werte die 4-Bit-Moniker in `TOKEN.DB` indizieren.

**Korrektur:** Die Datei ist nicht als sechs 64-Byte-Blöcke mit 16 RGBA-Einträgen zu interpretieren. Die beobachtete Struktur ist 128 RGB-Tripel. Die genaue Rolle der Nullhälfte bleibt offen.

## 4. Konsequenz für GeoViewPlus 0.3

Die bisherige Graustufenumrechnung für den untersuchten 4-Bit-Farbmoniker-Pfad wurde durch eine RGB-Palettenzuordnung ersetzt. Die High-/Low-Nibble-Reihenfolge bleibt: High zuerst, Low danach. Die Transparenzmaske und der PackBits-/RLE-Decoder wurden nicht verändert.

Der Teststand wurde mit der vorhandenen `TOKEN.DB` geprüft: 1.493 Moniker wurden erkannt; alle 4-Bit-Farbmoniker-Vorschauen ließen sich ohne Render-Ausnahme erzeugen. Zusätzlich wurden Regressionstests für Palette und Nibble-Reihenfolge ergänzt.

## 5. Noch nicht abschließend bewiesen

- Dass jeder als Farbe klassifizierte Moniker-Untertyp dieselbe 16-Farben-Palette nutzt.
- Ob einzelne Moniker eine eigene Palette oder abweichende Farbtabelle enthalten.
- Ob EGA- und VGA-Treiber in allen Modi dieselbe Palette verwenden.
- Die genaue Bedeutung der 64 Null-Tripel in `COLOR1.INI`.
- Die genaue Zuordnung von Farb- und Maskenebenen in jedem Bitmap-Untertyp.

## 6. Nächste Schritte

1. Farbmoniker in GeoViewPlus 0.3 visuell gegen die Originaldarstellung prüfen.
2. Unterschiedliche Farbmoniker-Untertypen getrennt vergleichen.
3. Erst bei bestätigter Zuordnung die Palette als endgültige Standardbehandlung freigeben.

**Integrität:** Die untersuchten GeoWorks-Originaldateien wurden nur gelesen. `TOKEN.DB`, `KERNEL.OLD`, EGA/VGA-Treiber und Decoder wurden nicht verändert.
