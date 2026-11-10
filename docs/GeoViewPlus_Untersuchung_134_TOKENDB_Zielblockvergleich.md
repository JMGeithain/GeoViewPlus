# GeoViewPlus – Untersuchung 134: Bytevergleich der drei Zielblöcke

**Datum:** 10.11.2026  
**Datenbasis:** `GEOWORKS/SYSTEM/TOKEN.DB` aus `GEOWORKS.zip`  
**SHA-256:** `c7fa3d51c9bdce14b988d20fd8ed57ac7da9837803090ac858990613ec53ae35`

## 1. Ziel

Untersuchung 133 fand in 304-Byte-Datensätzen WORD-Werte, die exakt als Handles im VM-Directory vorkommen. Drei wiederholt gefundene Handles wurden ausgewählt: `0x3CA0`, `0x3B90` und `0x3E50`. In dieser Untersuchung werden ihre Directory-Einträge und tatsächlichen Blockanfänge verglichen.

## 2. Verifizierte Directory-Einträge

Das Directory beginnt bei `0x0CF400`; die Einträge beginnen bei `0x0CF420` und sind 12 Bytes lang. Die drei Handles wurden durch exakte Suche in den Directory-Einträgen gefunden.

| Handle | Index (0-basiert) | Flags | User-ID | Größe | Dateiposition |
|---|---:|---:|---:|---:|---:|
| `0x3CA0` | 4 | `0x00FF` | `0x2222` | `0x0130` (304) | `0x002480` |
| `0x3B90` | 182 | `0x00FF` | `0x2222` | `0x0630` (1.584) | `0x083880` |
| `0x3E50` | 128 | `0x01FF` | `0x3333` | `0x2090` (8.336) | `0x08FB20` |

Die Angaben zu User-ID, Größe und Position stammen jeweils aus demselben Directory-Eintrag wie das Handle. Die drei Zielpositionen liegen innerhalb der unveränderten Datei.

## 3. Blockanfänge im Vergleich

### Handle 0x3CA0

Erste 96 Bytes:

```
50 00 E0 21 00 00 14 01 5A 00 1A 01 2C 01 0E 01
14 00 0E 01 16 00 0E 01 18 00 0E 01 1A 00 0E 01
1C 00 0E 01 1E 00 0E 01 20 00 0E 01 22 00 0E 01
24 00 0E 01 26 00 0E 01 28 00 0E 01 2A 00 0E 01
2C 00 0E 01 2E 00 0E 01 30 00 14 01 14 00 14 01
16 00 14 01 18 00 14 01 1A 00 5E 00 00 00 62 00
```

Dieser Block ist selbst einer der 81 Datensätze mit User-ID `0x2222` und Größe `0x0130`. Sein Anfang zeigt das bereits bekannte Muster mit aufsteigenden WORDs und den Markern `0x010E` bzw. später `0x0114`.

### Handle 0x3B90

Erste 96 Bytes:

```
A8 08 C0 37 00 00 14 01 50 05 1A 01 2C 06 0E 01
14 00 0E 01 16 00 0E 01 18 00 0E 01 1A 00 0E 01
1C 00 0E 01 1E 00 0E 01 20 00 0E 01 22 00 0E 01
24 00 0E 01 26 00 0E 01 28 00 0E 01 2A 00 0E 01
2C 00 0E 01 2E 00 0E 01 30 00 0E 01 32 00 0E 01
34 00 0E 01 36 00 0E 01 38 00 0E 01 3A 00 0E 01
```

Auch dieser Block gehört zur User-ID-Gruppe `0x2222`. Sein Anfang besitzt eine sehr ähnliche Sequenz wie die 304-Byte-Datensätze, die Folge läuft hier aber über einen wesentlich größeren Block weiter. Seine Größe beträgt exakt `0x0630`, also 1.584 Bytes.

### Handle 0x3E50

Erste 96 Bytes:

```
F0 42 14 00 00 00 00 00 84 20 10 01 86 1F 00 01
20 06 0E 01 36 02 52 02 6E 02 8A 02 A6 02 C2 02
DE 02 FA 02 16 03 32 03 4E 03 6A 03 86 03 A2 03
BE 03 DA 03 F6 03 12 04 2E 04 4A 04 66 04 82 04
9E 04 BA 04 D6 04 F2 04 0E 05 2A 05 46 05 62 05
7E 05 9A 05 B6 05 D2 05 EE 05 0A 06 26 06 42 06
```

Dieser Block gehört zur anderen User-ID-Gruppe `0x3333` und ist mit 8.336 Bytes deutlich größer. Sein Anfang unterscheidet sich sichtbar von den beiden `0x2222`-Blöcken: Nach wenigen WORDs folgt eine lange Folge aufsteigender, nicht durch `0x010E` unterbrochener Werte.

## 4. Direkter Vergleich der internen Handle-Werte

Die drei ausgewählten Handle-Werte `0x3CA0`, `0x3B90` und `0x3E50` wurden innerhalb jedes der drei Zielblöcke als Little-Endian-WORDs an geraden Offsets gesucht. In keinem der drei Blöcke trat einer dieser drei Werte als vollständiges WORD auf.

Das schließt andere Referenzarten oder Referenzen in anderen Blöcken nicht aus. Es zeigt lediglich, dass sich in diesen drei Blöcken keine unmittelbare gegenseitige Selbst-/Querverweisung mit genau diesen drei Handle-Werten nachweisen ließ.

## 5. Bewertung

**Gesichert:**

1. Alle drei Handles sind reale Einträge des VM-Directory.
2. `0x3CA0` und `0x3B90` gehören zur User-ID `0x2222`.
3. Beide `0x2222`-Blöcke beginnen mit einer strukturell ähnlichen Folge, die auch in den 304-Byte-Datensätzen vorkommt.
4. `0x3B90` ist größer als ein einzelner 304-Byte-Datensatz, besitzt aber denselben erkennbaren Anfangstyp.
5. `0x3E50` gehört zur User-ID `0x3333` und besitzt einen sichtbar anderen Anfangsaufbau.

**Noch nicht gesichert:**

- Ob die `0x2222`-Struktur ein Array, eine Tabelle, ein Verzeichnis oder eine andere Datenstruktur darstellt.
- Ob die WORD-Sequenz in `0x3B90` mehrere Datensätze enthält oder eine zusammenhängende Struktur mit variabler Länge ist.
- Ob ein Verweis aus einem 304-Byte-Block zur Laufzeit tatsächlich auf einen dieser Blöcke zeigt.
- Ob einer dieser Blöcke Icons oder Moniker-Daten enthält.

Eine Handle-Übereinstimmung ist ein starker Prüfansatz, aber noch kein semantischer Beweis.

## 6. Nächster Schritt

Als Nächstes sollte der gesamte Block `0x3B90` mit den 304-Byte-Datensätzen verglichen werden: wiederkehrende Präfixe, mögliche Datensatzgrenzen, interne Längenfelder und Übergänge. Parallel sollte der `0x3333`-Block `0x3E50` separat klassifiziert werden, ohne die beiden User-ID-Gruppen zu vermischen.

## 7. Datenintegrität

Analysiert wurde ausschließlich `GEOWORKS/SYSTEM/TOKEN.DB` aus dem genannten ZIP-Archiv. Die Datei hat 952.688 Bytes und den oben angegebenen SHA-256. Originaldateien und GeoViewPlus-Programmcode wurden nicht verändert.
