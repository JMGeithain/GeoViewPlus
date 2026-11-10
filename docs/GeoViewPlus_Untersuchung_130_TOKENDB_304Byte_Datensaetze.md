# GeoViewPlus – Untersuchung 130: Struktur der 304-Byte-Datensätze in TOKEN.DB

## Ziel und Datenbasis

Untersucht wurden die 81 Directory-Einträge aus `GEOWORKS/SYSTEM/TOKEN.DB`, die in Untersuchung 129 der User-ID `0x2222` und der Blockgröße `0x0130` zugeordnet wurden.

- Dateigröße: 952.688 Bytes
- SHA-256: `c7fa3d51c9bdce14b988d20fd8ed57ac7da9837803090ac858990613ec53ae35`
- Directory-Basis: Dateioffset `0xCF400`; Einträge ab `0xCF420`, jeweils 12 Bytes
- Anzahl untersuchter Datensätze: 81
- Größe jedes Datensatzes: `0x0130` = 304 Bytes
- Die Analyse erfolgte lesend. Die ZIP-Datei und die enthaltene Original-TOKEN.DB wurden nicht verändert.

## 1. Konstante Felder

Die folgenden WORD-Werte sind in allen 81 Datensätzen identisch:

| Datensatz-Offset | Wert | Beobachtung |
|---:|---:|---|
| `+0x04` | `0x0000` | in allen 81 Datensätzen konstant |
| `+0x0C` | `0x012C` | in allen 81 Datensätzen konstant; dezimal 300 |
| `+0x0E` | `0x010E` | in allen 81 Datensätzen konstant; dezimal 270 |
| `+0x10` | `0x0014` | in allen 81 Datensätzen konstant; dezimal 20 |
| `+0x106` | `0x010A` | in allen 81 Datensätzen konstant |
| `+0x10A` | `0x0000` | in allen 81 Datensätzen konstant |

**Hinweis:** Der Bereich ab `+0x10` ist kein einheitlicher einfacher Zähler. Die bytegenaue Stichprobe zeigt mehrere Abschnitte: zunächst fortlaufende gerade Werte mit wiederkehrendem `0x010E`, danach weitere Werte mit `0x0114` sowie anschließend eine Folge gerader Werte mit dazwischenliegenden Null-WORDs. Die Grenzen dieser Teilbereiche variieren zwischen Datensätzen. Eine semantische Tabellenbezeichnung wird daraus noch nicht abgeleitet.

## 2. Felder mit wenigen Varianten

| Offset | Häufige Werte | Verteilung |
|---:|---|---|
| `+0x06` | `0x0114` / `0x010E` | 77 / 4 Datensätze |
| `+0x0A` | `0x011A` / `0x0114` | 77 / 4 Datensätze |
| `+0x08` | mehrere Werte | 36 unterschiedliche Werte |

Die vier Ausnahmen bei `+0x06` und `+0x0A` sind Directory-Indizes 9, 313, 335 und 357. Bei ihnen sind die beiden häufigen Werte vertauscht:

- 77 Datensätze: `+0x06 = 0x0114`, `+0x0A = 0x011A`
- 4 Datensätze: `+0x06 = 0x010E`, `+0x0A = 0x0114`

Das ist ein reproduzierbares Muster. Ob es Varianten eines Datensatztyps oder eine andere Unterklasse kennzeichnet, ist noch nicht bewiesen.

## 3. Variable Anfangsfelder

Das erste WORD (`+0x00`) ist bei allen 81 Datensätzen verschieden. Das zweite WORD (`+0x02`) besitzt 77 unterschiedliche Werte; einzelne Werte kommen zweimal vor. Das WORD bei `+0x08` besitzt 36 unterschiedliche Werte.

Beispielhafte Datensatzanfänge:

| Directory-Index | Dateioffset | erste 16 Bytes |
|---:|---:|---|
| 4 | `0x2480` | `50 00 E0 21 00 00 14 01 5A 00 1A 01 2C 01 0E 01` |
| 9 | `0x0250` | `8C 00 20 26 00 00 0E 01 12 00 14 01 2C 01 0E 01` |
| 14 | `0x45680` | `C8 00 B0 39 00 00 14 01 62 00 1A 01 2C 01 0E 01` |
| 17 | `0x3A60` | `EC 00 A0 38 00 00 14 01 6A 00 1A 01 2C 01 0E 01` |
| 18 | `0x2D10` | `F8 00 F0 38 00 00 14 01 6A 00 1A 01 2C 01 0E 01` |

## 4. Regelmäßiger Bereich im Datensatzinneren

Ab `+0x10` ist ein wiederkehrender strukturierter WORD-Bereich sichtbar. In den untersuchten Beispielen erscheinen zunächst gerade Werte (`0x0014`, `0x0016`, `0x0018` usw.) mit dem wiederkehrenden Zwischenwert `0x010E`. In einem anschließenden Abschnitt tritt `0x0114` als weiterer wiederkehrender Wert auf. Später folgen gerade Werte mit Null-WORDs dazwischen. Die Übergänge und die Länge der Abschnitte unterscheiden sich zwischen Datensätzen.

Beispiel für Directory-Index 4 bei Dateioffset `0x2480`: ab `+0x10` beginnt `0014 010E 0016 010E ...`; danach folgen `002C 010E 002E 010E 0030 0114`, anschließend weitere Werte und später Paare wie `005E 0000`, `0062 0000` usw. Das belegt einen strukturierten Unterbereich, aber nicht dessen Bedeutung. Er könnte beispielsweise eine Offset-/Indexstruktur enthalten; diese Deutung ist ausdrücklich noch unbestätigt.

## 5. Vier abweichende Datensätze

Die vier oben genannten Datensätze unterscheiden sich bereits in den Feldern `+0x06` und `+0x0A`. Sie sollten bei einer späteren Rekonstruktion nicht stillschweigend in das 77er-Hauptmuster eingegliedert werden.

| Directory-Index | Dateioffset | erstes WORD | `+0x06` | `+0x0A` |
|---:|---:|---:|---:|---:|
| 9 | `0x0250` | `0x008C` | `0x010E` | `0x0114` |
| 313 | `0x86860` | `0x0ECC` | `0x010E` | `0x0114` |
| 335 | `0x783E0` | `0x0FD4` | `0x010E` | `0x0114` |
| 357 | `0x8B2D0` | `0x10DC` | `0x010E` | `0x0114` |

## 6. Was damit noch nicht bewiesen ist

- Die 304-Byte-Blöcke sind nicht als Icons identifiziert.
- Die User-ID `0x2222` ist weiterhin nicht semantisch entschlüsselt.
- Das erste WORD ist nicht automatisch ein Token-Handle oder Moniker-Handle.
- Die regelmäßigen Werte im inneren Bereich sind nicht automatisch Dateioffsets.
- Es besteht weiterhin keine nachgewiesene Referenzkette von `GEODEXGC.GEO` zu einem dieser Datensätze und weiter zu einem Icon-Moniker.

## 7. Nächster Untersuchungsschritt

Untersuchung 131 sollte die vier Ausnahmen mit den 77 Hauptdatensätzen byteweise vergleichen und den inneren Bereich ab `+0x10` vollständig als Byte-/WORD-Tabelle darstellen. Parallel werden die ersten WORD-Werte gegen die übrigen Directory-Einträge und deren Dateioffsets geprüft. Erst eine eindeutige Referenz oder ein reproduzierbarer Parser erlaubt eine belastbare Typzuweisung.

## Prüfbarkeit

Alle Zahlen und Bytefolgen beziehen sich auf die oben durch SHA-256 identifizierte Datei `GEOWORKS/SYSTEM/TOKEN.DB` aus `GEOWORKS.zip`. Die Directory-Einträge wurden anhand der in Untersuchung 129 dokumentierten 12-Byte-Struktur ausgewertet. Unbekannte Felder bleiben ausdrücklich unbenannt.
