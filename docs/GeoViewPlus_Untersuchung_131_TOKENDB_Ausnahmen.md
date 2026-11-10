# GeoViewPlus – Untersuchung 131: Vier Ausnahmen im 304-Byte-Datensatzfeld

## Datenbasis

Untersucht wurden erneut die 81 Datensätze aus `GEOWORKS/SYSTEM/TOKEN.DB`, die Untersuchung 129 als `userID = 0x2222` und Größe `0x0130` identifiziert hat.

- Dateigröße: 952.688 Bytes
- SHA-256: `c7fa3d51c9bdce14b988d20fd8ed57ac7da9837803090ac858990613ec53ae35`
- Datensatzlänge: 304 Bytes (`0x0130`)
- Anzahl: 81
- Vier auffällige Directory-Indizes: 9, 313, 335 und 357
- Analyse ausschließlich lesend; Original-ZIP und Original-TOKEN.DB wurden nicht verändert.

## 1. Korrektur und Präzisierung der Gruppen

Die vier Datensätze unterscheiden sich in `+0x06` und `+0x0A` vom häufigsten Muster. Drei davon (Indizes 313, 335 und 357) zeigen jedoch weiterhin dieselbe regelmäßige Folge aus geraden Werten und `0x010E`, die auch bei der Hauptgruppe vorkommt. Index 9 ist deutlich anders aufgebaut.

Das bedeutet: Die vier Datensätze sind nicht alle gleichartige Ausnahmen. Drei zeigen eine erkennbare Tabellenvariante; einer besitzt eine abweichende Folge.

## 2. Die drei Tabellenvarianten (Indizes 313, 335, 357)

Bei allen drei Datensätzen beginnt der Bereich ab `+0x10` mit einer alternierenden Folge:

`0014 010E 0016 010E 0018 010E 001A 010E ...`

Die Folge setzt sich in den untersuchten Bytes fort. Die Werte links steigen in Zweierschritten; `0x010E` steht jeweils als Zwischenwert. Das Muster ist eine direkte Bytebeobachtung und kein Beweis für die Bedeutung als Offsettabelle.

Abweichungen:
- Index 313 (`Dateioffset 0x86860`): die Alternation ist in den ersten 64 Bytes bis `+0x3E` vollständig sichtbar.
- Index 335 (`Dateioffset 0x783E0`): derselbe sichtbare Aufbau.
- Index 357 (`Dateioffset 0x8B2D0`): zunächst dasselbe Muster, ab `+0x26` folgt jedoch eine Folge gerader Werte mit Null-WORDs dazwischen (`002A 0000 002E 0000 ...`). Die Tabelle ist damit an dieser Stelle anders fortgesetzt oder endet/ändert dort ihre Form.

## 3. Der abweichende Datensatz mit Index 9

Index 9 liegt bei Dateioffset `0x0250`. Seine ersten 16 Bytes lauten:

`8C 00 20 26 00 00 0E 01 12 00 14 01 2C 01 0E 01`

Ab `+0x10` stehen die geraden Werte nicht in der regelmäßigen Alternation mit `0x010E`. Stattdessen sind die Werte an ungeraden WORD-Positionen überwiegend variabel, beispielsweise:

| Offset | WORD-Wert |
|---:|---:|
| `+0x10` | `0x0014` |
| `+0x12` | `0x0016` |
| `+0x14` | `0xA31F` |
| `+0x16` | `0x001A` |
| `+0x18` | `0x1E89` |
| `+0x1A` | `0x001E` |
| `+0x1C` | `0xF626` |
| `+0x1E` | `0x0022` |
| `+0x20` | `0x1000` |
| `+0x22` | `0x0026` |

Diese Folge unterscheidet sich deutlich von den anderen drei Datensätzen. Die großen WORD-Werte könnten Daten oder Verweise darstellen; ohne Kenntnis der Struktur und ohne erfolgreiche Zielauflösung darf man sie nicht als Dateioffsets interpretieren.

## 4. Was lässt sich aus den vier Datensätzen ableiten?

Gesichert sind folgende Beobachtungen:

1. Drei Datensätze (313, 335, 357) teilen den regelmäßigen Aufbau ab `+0x10` zumindest teilweise.
2. Der Datensatz 357 wechselt innerhalb des betrachteten Bereichs von `WORD / 0x010E` zu `WORD / 0x0000`.
3. Datensatz 9 besitzt ab `+0x10` eine andere Folge, in der zahlreiche WORD-Werte nicht dem Muster der übrigen Datensätze entsprechen.
4. Die äußeren konstanten Felder `+0x04 = 0`, `+0x0C = 0x012C` und `+0x0E = 0x010E` bleiben bei allen vier erhalten.

Nicht gesichert ist:
- ob die alternierenden Werte Offsets, Längen, Indizes oder Tabellenmarken sind;
- ob die drei ähnlichen Datensätze eine andere Unterklasse desselben Typs bilden;
- ob Index 9 ein anderer Untertyp oder ein anders belegter Datensatz ist;
- ob eines dieser Felder auf einen Icon-Moniker verweist.

## 5. Nächster Schritt

Untersuchung 132 sollte die WORD-Werte im Bereich `+0x10` bis `+0x12E` aller 81 Datensätze spaltenweise klassifizieren. Insbesondere ist zu prüfen, ob Werte wie `0x010E`, `0x0114` und die geraden Zahlen als wiederkehrende Marker, Grenzwerte oder relative Positionsangaben funktionieren. Zusätzlich sollen die variablen ersten WORDs und zweiten WORDs mit tatsächlichen Directory-Handles und Datei-Offsets abgeglichen werden. Eine Referenz gilt erst dann als erkannt, wenn sie auf einen gültigen, inhaltlich passenden Zielblock zeigt.

## Prüfbarkeit

Die Untersuchung basiert auf der SHA-256-identifizierten `GEOWORKS/SYSTEM/TOKEN.DB` aus `GEOWORKS.zip`. Die hier wiedergegebenen Bytes stammen direkt aus den Datensatzbereichen an den oben genannten Dateioffsets. Die Datei wurde nicht verändert.
