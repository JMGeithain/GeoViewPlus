# GeoViewPlus – Untersuchung 129: Vergleich der TOKEN.DB-Blockgruppen 0x2222 und 0x3333

## Ziel und Datenbasis

Untersucht wurden die 92 Directory-Einträge mit `userID = 0x2222` und die 178 Einträge mit `userID = 0x3333` in `GEOWORKS/SYSTEM/TOKEN.DB` aus `GEOWORKS.zip`.

- Dateigröße: 952,688 Bytes
- SHA-256: `c7fa3d51c9bdce14b988d20fd8ed57ac7da9837803090ac858990613ec53ae35`
- VM-Directory beginnt bei Dateioffset `0xCF400`.
- 358 Directory-Einträge zu je 12 Bytes ab `0xCF420`.
- Rohdaten wurden ausschließlich lesend aus dem ZIP analysiert; Originaldatei wurde nicht verändert.

## Directory-Eintragsformat

Die 12-Byte-Einträge sind in dieser Reihenfolge zu lesen:

| Relativer Offset | Feld |
|---:|---|
| +0 | Memory-Handle (WORD) |
| +2 | Flags (WORD) |
| +4 | User-ID (WORD) |
| +6 | Blockgröße (WORD) |
| +8 | Dateioffset (DWORD) |

Die Einträge sind fortlaufend im Directory abgelegt. Die frühere Bezeichnung der Directory-Position als „Handle“ war nicht ausreichend belegt. Dieser Bericht verwendet deshalb Directory-Index und Directory-Dateioffset und vermeidet daraus abgeleitete Handle-Nummern.

## Verteilung und Flags

| User-ID | Anzahl | Flags |
|---|---:|---|
| `0x2222` | 92 | alle `0x00FF` |
| `0x3333` | 178 | alle `0x01FF` |

Größenverteilung der 0x2222-Gruppe:
- `0x0010`: 1 Eintrag
- `0x0130`: 81 Einträge (304 Bytes)
- `0x0230`: 3 Einträge
- `0x0530`: 2 Einträge
- `0x0630`: 2 Einträge
- `0x0830`: 1 Eintrag
- `0x0930`: 2 Einträge

Damit ergeben sich 92 Einträge. Die 0x3333-Gruppe hat eine deutlich breitere Größenverteilung; die Größen reichen in den untersuchten Einträgen bis `0xDE20` (56.864 Bytes).

## Strukturbeobachtungen 0x2222

Viele Blöcke mit 304 Bytes beginnen mit wiederkehrenden Folgen aus WORD-Werten, z. B.:

`2C 00 20 26 00 00 14 01 4C 01 1A 01 2C 02 0E 01 ...`

Weitere Beispiele:
- `50 00 E0 21 00 00 14 01 5A 00 1A 01 2C 01 0E 01 ...`
- `8C 00 20 26 00 00 0E 01 12 00 14 01 2C 01 0E 01 ...`

Das sind wiederkehrende strukturierte Daten und keine erkennbaren Bitmap-Pixelströme an den Blockanfängen. Eine semantische Benennung als Token-Tabelle, Moniker-Tabelle oder Icon-Verzeichnis ist anhand dieser Bytes allein noch nicht zulässig.

Die 81 gleich großen 0x0130-Blöcke sind ein starker Hinweis auf einen einheitlichen Datensatztyp. Die wiederkehrenden WORD-Sequenzen sollten nach Feldern und Verweisen gruppiert werden.

## Strukturbeobachtungen 0x3333

Die 178 Blöcke unterscheiden sich durch größere und variablere Größen. Beispiele:
- Directory-Index 2, Größe `0x2100`, Offset `0x0380`: beginnt `C0 31 14 00 00 00 00 00 ...`
- Directory-Index 5, Größe `0x1F30`, Offset `0x5540`: beginnt `02 77 77 78 FE FE 0A F7 ...`
- Directory-Index 8, Größe `0xDE20`, Offset `0xAB50`: beginnt mit einer Folge kleiner Offsets (`00 00 E6 00 00 00 EA 00 ...`).

Wiederkehrende Startmuster sind vorhanden, z. B. `F9 00 E1 DD` (5 Vorkommen) und `F9 00 F9 00` (4 Vorkommen). Die Muster allein erlauben keine sichere Typzuweisung. Die sehr unterschiedlichen Größen sprechen dafür, dass 0x3333 eine andere Blockklasse als 0x2222 markiert; die konkrete Bedeutung bleibt offen.

## Sonderfall des 16-Byte-Blocks bei Dateioffset 0x00E0

Der Directory-Eintrag mit `userID = 0x2222`, Größe `0x0010` und Dateioffset `0x00E0` enthält:

`68 00 50 26 00 80 00 00 00 00 00 00 0E 00 00 00`

Beobachtbar sind erstes WORD `0x0068`, zweites WORD `0x2650`, drittes WORD `0x8000` und am Offset +12 das WORD `0x000E`. Die Bedeutung der Felder ist nicht nachgewiesen. `0x0068` wird nicht als sicherer Ressourcen- oder Moniker-Handle bezeichnet.

## Konsequenz für den Icon-Resolver

1. Die Gruppen `0x2222` und `0x3333` sind anhand ihrer User-ID und Flags klar unterscheidbar.
2. Die 0x2222-Blöcke enthalten häufig gleich große, strukturierte Daten mit wiederkehrenden WORD-Folgen.
3. Die 0x3333-Blöcke sind größer und variabler; ihre Inhalte haben andere Startmuster.
4. Es wurde noch keine belastbare Referenzkette von `GEODEXGC.GEO` zu einem Icon-Moniker nachgewiesen.
5. Es ist daher noch nicht gerechtfertigt, diese Gruppen als Icon-Ressourcen zu extrahieren oder in GeoViewPlus als solche zu labeln.

## Nächster Schritt – Untersuchung 130

- Die 81 Blöcke der Größe `0x0130` aus Gruppe 0x2222 bytegenau vergleichen.
- WORD-Felder an identischen Offsets statistisch gruppieren.
- Prüfen, ob erste WORDs mit anderen Directory-Metadaten oder internen Tabellenwerten korrelieren.
- Für 0x3333 die großen Blöcke getrennt nach Größenfamilien analysieren und Offsettabellen untersuchen.
- Erst danach gezielt nach Verweisen aus dem GEODEXGC.GEO-VM-Verzeichnis suchen.

## Prüfbarkeit

Alle genannten Werte stammen aus der oben durch SHA-256 identifizierten `TOKEN.DB`. Die Blockgrößen und Dateioffsets stammen direkt aus den 12-Byte-Directory-Einträgen. Unbekannte Felder werden ausdrücklich als unbekannt geführt.
