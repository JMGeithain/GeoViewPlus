# Untersuchung 158 – Bytevergleich binärer Bereiche in BOUNCE.GEO und BCOLTEST.GEO

**Projekt:** GeoViewPlus – Untersuchung echter PC/GEOS-Icons  
**Material:** `BOUNCE.GEO` und `BCOLTEST.GEO` aus Basebox-SVGA-Ensemble12(2).zip  
**Geltungsbereich:** Ausschließlich die vorliegenden GeoWorks-/PC/GEOS-1.x-Dateien.

## 1. Methode und Ressourcengrenzen

Die Ressourcen 3 und 4 wurden aus den beiden GEO-Dateien anhand der zuvor ermittelten Ressourcentabelle isoliert und relativ zum jeweiligen Ressourcenanfang verglichen.

| Datei | Ressource 3 | Größe | Ressource 4 | Größe |
|---|---:|---:|---:|---:|
| BOUNCE.GEO | Datei-Offset 1316 | 384 | Datei-Offset 1704 | 336 |
| BCOLTEST.GEO | Datei-Offset 1728 | 400 | Datei-Offset 2132 | 336 |

Alle folgenden Offsets sind **ressourcenrelative Offsets**, nicht Dateioffsets.

## 2. Ressource 3 – gemeinsamer binärer Anfang

Der Bereich ab `+003Eh` ist in beiden Ressourcen byteidentisch:

```text
00 02 03 02 02 07 02 02 07 02 07 02 07 00
23 00 00 30 58 00 00 00 08 00 00 00 00 00
23 00 04 10 ...
```

Der erste festgestellte Unterschied in diesem Bereich liegt bei `+005Eh`: BOUNCE enthält dort `2Ah`, BCOLTEST `38h`. Der umgebende Feldkontext lautet:

BOUNCE ab `+004Eh`:
```text
00 30 58 00 00 00 08 00 00 00 00 00 23 00 04 10
2A 00 00 40 26 00 00 00 28 00 00 C0 22 00 80 00
```

BCOLTEST ab `+004Eh`:
```text
00 30 58 00 00 00 08 00 00 00 00 00 23 00 04 10
38 00 00 40 26 00 00 00 28 00 00 C0 22 00 80 00
```

Gesichert ist hier nur die Byteabweichung `2Ah` gegenüber `38h`. Ob es sich um Breite, Kennung, Größe oder einen anderen Wert handelt, ist ohne Formatnachweis offen.

## 3. Ressource 3 – Textlänge verändert nachfolgende Offsets

Der Textdatensatz in BOUNCE beginnt bei `+0072h` mit `Bounce`. In BCOLTEST beginnt an `+0072h` der längere Text `RGB565 colour proof`.

Dadurch liegen nachfolgende binäre Inhalte nicht mehr an denselben Offsets:
- BOUNCE-Tabelle enthält unter anderem `0082h` und `008Eh`.
- BCOLTEST-Tabelle enthält stattdessen `008Eh` und `009Ah`.

Das ist wichtig: Ein positionsgleicher Vergleich von `+0082h` in beiden Dateien vergleicht nicht denselben logischen Datensatz. In BCOLTEST liegt `+0082h` noch innerhalb des längeren Textes `RGB565 colour proof`; in BOUNCE liegt `+0082h` bereits in einem binären Nachfolgebereich.

Beispiel BOUNCE R3 ab `+0082h`:
```text
41 40 08 00 07 00 02 00 CC CC 26 00 00 30 53 00
00 00 08 00 00 00 00 00 38 00 00 40 ...
```

BCOLTEST R3 ab `+008Eh`:
```text
41 40 08 00 07 00 02 00 CC CC 26 00 00 30 53 00
00 00 08 00 00 00 00 00 38 00 00 40 ...
```

Diese beiden Bereiche beginnen mit derselben Bytefolge. Der Vergleich ist ein stärkerer Hinweis auf dieselbe logische binäre Struktur, weil die jeweiligen Tabellenoffsets den längeren Text in BCOLTEST berücksichtigen.

## 4. Ressource 4 – weitgehend gleiche Binärstruktur

Ressource 4 ist in beiden Dateien 336 Bytes groß. Die ersten 10 Bytes sind identisch; die Tabelle ab `+20h` ist ebenfalls identisch:

```text
002E 0036 00FE 012A 0136 0000
```

Die binären Bereiche ab `+002Eh`, `+0036h` und `+00FEh` sind über weite Strecken byteidentisch. Ein klarer Unterschied liegt im Text-/Namensbereich bei `+0054h` bis `+0057h`:
- BOUNCE enthält ASCII-Anteile `42 4F 4E 43` (Beginn von `BONC...` im Rohbereich).
- BCOLTEST enthält `52 47 42 35` (Beginn von `RGB5...`).

Der Textdatensatz ab `+0136h` unterscheidet sich erwartungsgemäß:
- BOUNCE: Präfix und Text `Bounce`.
- BCOLTEST: Präfix und Text `RGB565 colour proof`.

Das Längen-WORD vor dem Präfix ist entsprechend `000Fh` beziehungsweise `001Ch`. Diese Längenwerte wurden in Untersuchung 156 anhand des Datensatzformats geprüft.

## 5. Korrektur zur positionsgleichen Interpretation

Die Ressource 3 kann wegen unterschiedlicher Textlängen nicht allein anhand identischer relativer Offsets verglichen werden. Der passende Vergleich muss die Tabellenziele beziehungsweise den logischen Inhalt berücksichtigen. Insbesondere darf `R3+0082h` in BOUNCE nicht mit `R3+0082h` in BCOLTEST als gleichartiger Datenbereich verglichen werden.

In Ressource 4 ist die relative Lage stabiler; dort bleiben die Tabellenwerte und die Ressourcengröße gleich.

## 6. Ergebnis

**Gesichert:**
1. Der binäre Bereich ab R3+`003Eh` ist zunächst weitgehend identisch; ein konkreter Unterschied tritt bei R3+`005Eh` auf (`2Ah` gegenüber `38h`).
2. Der längere Titeltext in BCOLTEST verschiebt die nachfolgenden logischen Datenpositionen gegenüber BOUNCE.
3. Die Tabellenwerte in R3 passen zu diesen unterschiedlichen Textlängen.
4. R3+`0082h` in BOUNCE und R3+`008Eh` in BCOLTEST beginnen mit derselben 16-Byte-Folge `41 40 08 00 07 00 02 00 CC CC 26 00 00 30 53 00`.
5. R4 ist 336 Bytes groß und hat in beiden Dateien dieselbe Tabelle und weitgehend dieselben binären Bereiche; die programmspezifischen Text-/Namensdaten unterscheiden sich.

**Nicht gesichert:**
- Die Semantik der Felder `2Ah` und `38h`.
- Ob die binären Bereiche Objekte, Moniker, Grafiken oder andere Strukturen enthalten.
- Die Bedeutung der Bytes `41 40 08 00 07 00 02 00 CC CC 26 00`.
- Ob und wie diese Daten mit LMem-Chunk-Handles verknüpft sind.

## 7. Konsequenz für GeoViewPlus

Keine Codeänderung. Ein künftiger Vergleichs- oder Parserbaustein muss variable Textlängen und dadurch verschobene Offsets berücksichtigen. Die Ressourcen dürfen nicht ausschließlich positionsgleich verglichen werden; die Tabellenwerte und die erkannten Datensatzgrenzen sind als zusätzliche Strukturinformationen einzubeziehen.

## 8. Integrität

- Originaldateien aus dem ZIP-Archiv nur lesend verarbeitet.
- Keine Originaldatei verändert.
- Kein GeoViewPlus-Programmcode geändert.
- Keine binären Bereiche als Icons oder Moniker klassifiziert.
