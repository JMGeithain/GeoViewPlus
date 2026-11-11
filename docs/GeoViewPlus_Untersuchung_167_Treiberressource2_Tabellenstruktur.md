# Untersuchung 167 – Tabellenstruktur in Treiber-Ressource 2

**Projekt:** GeoViewPlus – Untersuchung echter PC/GEOS-Icons  
**Material:** `BB120_64.GEO`, `BB72_64.GEO`, `BB96_64.GEO`, `S16_1280.GEO`, `V16_0720.GEO`  
**Geltungsbereich:** Direkte Bytebefunde an den fünf GeoWorks-/PC/GEOS-1.x-Treiberdateien aus dem vorliegenden Archiv.  
**Methode:** Ressource 2 jeweils anhand der Geode-Ressourcentabelle abgegrenzt und ausschließlich lesend untersucht.

## 1. Ressourcengrenzen und Header

Alle fünf Dateien besitzen drei Ressourcen. Ressource 2 ist jeweils 1.776 Bytes (`06F0h`) groß. Der Beginn der Ressource liegt dateiabhängig an folgenden Dateioffsets:

| Datei | Dateioffset R2 | Größe R2 |
|---|---:|---:|
| BB120_64.GEO | 33230 | 1776 |
| BB72_64.GEO | 33230 | 1776 |
| BB96_64.GEO | 33230 | 1776 |
| S16_1280.GEO | 26974 | 1776 |
| V16_0720.GEO | 33182 | 1776 |

Der 32-Byte-Header von Ressource 2 ist in allen fünf Dateien gleich, mit Ausnahme des WORD-Feldes bei `+16h`:

| Offset | BB120 | BB72 | BB96 | S16 | V16 |
|---|---:|---:|---:|---:|---:|
| +00h | 0002 | 0002 | 0002 | 0002 | 0002 |
| +02h | 0020 | 0020 | 0020 | 0020 | 0020 |
| +04h | 0000 | 0000 | 0000 | 0000 | 0000 |
| +06h | 0000 | 0000 | 0000 | 0000 | 0000 |
| +08h | 06F0 | 06F0 | 06F0 | 06F0 | 06F0 |
| +0Ah | 0024 | 0024 | 0024 | 0024 | 0024 |
| +0Ch | 0000 | 0000 | 0000 | 0000 | 0000 |
| +0Eh | 0000 | 0000 | 0000 | 0000 | 0000 |
| +10h | 0001 | 0001 | 0001 | 0001 | 0001 |
| +12h | 0016 | 0016 | 0016 | 0016 | 0016 |
| +14h | 0000 | 0000 | 0000 | 0000 | 0000 |
| +16h | 0066 | 0062 | 0064 | 0046 | 003C |
| +18h bis +1Eh | 0000 | 0000 | 0000 | 0000 | 0000 |

Alle Werte sind Little-Endian-WORDs.

## 2. Das Feld +0Ah und die Tabelle ab +20h

Das WORD bei `+0Ah` ist `0024h` (= 36) in allen fünf Dateien.

Ab Ressourcenoffset `+20h` liegen genau 36 aufeinanderfolgende WORD-Werte. Die Tabelle belegt damit 72 Bytes und reicht von `+20h` bis einschließlich `+67h`; der nächste Byteoffset ist `+68h`.

Die 36 Tabellenwerte sind in allen fünf Dateien identisch:

```text
006A 009A 00CA 00FA 012A 015A 018A 01BA
01EA 021A 024A 027A 02AA 02DA 030A 033A
036A 039A 03CA 03FA 042A 045A 048A 04BA
04EA 051A 054A 057A 05AA 05DA 060A 063A
066A 069A 06B6 06D2
```

Damit ist die Übereinstimmung von `+0Ah = 36` mit 36 physischen WORD-Slots direkt bestätigt. Es handelt sich hier aber nicht um dieselbe kleine Tabellenstruktur wie in den Ressourcen 3–10 von BOUNCE/BCOLTEST.

## 3. Tabellenziele führen in lesbare Textdatensätze

Alle 36 Werte sind gerade, innerhalb der 1.776-Byte-Ressource liegende Offsets. An jedem Ziel beginnt ein lesbarer Textdatensatz. Unmittelbar vor jedem Ziel steht ein WORD-Feld, das in diesen Dateien typischerweise Werte von `002Eh`, `002Fh` oder `0030h` enthält. Die Datensätze enthalten unter anderem Bezeichnungen wie:

- `VESA Compatible SuperVGA: 640x480 64K-color`
- `VESA Compatible SuperVGA: 800x600 64K-color`
- `VESA Compatible SuperVGA: 1024x768 64K-color`
- `VESA Compatible SuperVGA: 1280x1024 64K-color`
- `VESA Compatible SuperVGA: 1920x1080 64K-color`
- `Basebox: 72 DPI 64K-color`
- `Basebox: 96 DPI 64K-color`
- `Basebox: 120 DPI 64K-color`

Die Tabelle ist daher nachweislich eine Offsetliste zu Textbereichen bzw. Textdatensätzen. Die exakte Semantik der einzelnen Texte und die Interpretation des vorangestellten WORD-Feldes sind damit noch nicht vollständig geklärt. Die Textdaten enthalten auch Nullbytes und `CC`-Bytes; diese dürfen nicht ungeprüft als Teil des sichtbaren Textes ausgegeben werden.

## 4. Regelmäßigkeit der Offsetwerte

Die ersten 34 Tabellenziele steigen in Schritten von `0030h` an. Die letzten beiden Ziele sind `06B6h` und `06D2h`; die letzten Abstände betragen jeweils `001Ch`.

Das ist ein direkter Befund der Offsetliste. Er passt zu einer Folge regelmäßig angeordneter Textbereiche mit kürzeren Schlussdatensätzen. Daraus wird noch keine allgemeine Datensatzstruktur für andere Ressourcentypen abgeleitet.

## 5. Feld +16h – veränderlicher Wert innerhalb der Tabelle

Das WORD bei `+16h` unterscheidet sich je Datei:

| Datei | WORD +16h | Tabellenindex (Offset in Tabelle) |
|---|---:|---:|
| BB120_64.GEO | 0066h | 35 |
| BB72_64.GEO | 0062h | 33 |
| BB96_64.GEO | 0064h | 34 |
| S16_1280.GEO | 0046h | 19 |
| V16_0720.GEO | 003Ch | 14 |

Die Werte liegen jeweils innerhalb des Tabellenbereichs `+20h..+67h` und zeigen auf die Position eines WORD-Slots in der Offsetliste. Die Indexrechnung ist `(Wert - 0020h) / 2`.

**Nicht bewiesen ist**, ob `+16h` einen letzten aktiven Eintrag, eine Auswahl-/Grenzposition oder etwas anderes bezeichnet. Insbesondere darf der Wert nicht ohne weitere Untersuchung als Anzahl interpretiert werden: Die Werte sind Byteoffsets innerhalb der Ressource, keine direkten Eintragszahlen.

## 6. Schlussfolgerungen

**Gesichert:**
1. Alle fünf Treiber besitzen in Ressource 2 eine 1.776 Byte große Struktur mit gleichem 32-Byte-Header bis auf `+16h`.
2. `+0Ah = 0024h` entspricht exakt 36 WORD-Einträgen ab `+20h`.
3. Alle 36 WORDs sind in allen fünf Dateien identisch.
4. Die Tabellenwerte zeigen auf lesbare Textdatensätze in Ressource 2.
5. Die Werte bei `+16h` unterscheiden sich je Treiber, liegen aber jeweils auf einem WORD-Slot innerhalb der 36-Einträge-Tabelle.

**Noch offen:**
- Die formale Bedeutung der Felder `+00h`, `+10h`, `+12h` und `+16h`.
- Die genaue Struktur und Bedeutung des WORD-Feldes unmittelbar vor jedem Textziel.
- Ob die 36 Einträge vollständig die auswählbaren Modi beschreiben oder zusätzliche Auswahl-/Statusdaten enthalten.
- Ob diese Struktur außerhalb dieser Treiberfamilie wiederkehrt.

## 7. Konsequenz für GeoViewPlus

Diese Ressource ist eine gute Gegenprobe für die Klassifizierung: Eine 36-WORD-Offsetliste führt zu Textdatensätzen. Sie ist keine nachgewiesene Icon- oder Moniker-Tabelle. GeoViewPlus darf diese Ressource daher nicht als Iconquelle klassifizieren, nur weil sie eine Offsetliste und viele Textdaten enthält.

Keine Codeänderung. Die Befunde werden ausschließlich dokumentiert.

## 8. Integrität und Versionsgrenze

- Fünf GEO-Dateien ausschließlich lesend untersucht.
- Keine Originaldatei verändert.
- Kein GeoViewPlus-Programmcode geändert.
- Keine Icon-/Moniker-Zuordnung vorgenommen.
- Keine PC/GEOS-2.x-Struktur als Beleg für GeoWorks 1.x verwendet.
