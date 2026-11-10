# GeoViewPlus – Untersuchung 132: WORD-Feldanalyse der 304-Byte-Datensätze

**Datum:** 10.11.2026  
**Datenbasis:** `GEOWORKS/SYSTEM/TOKEN.DB` aus `GEOWORKS.zip`  
**Umfang:** 81 Directory-Einträge mit User-ID `0x2222` und Blockgröße `0x0130` (304 Bytes)

## 1. Datenintegrität und reproduzierbare Auswahl

Die Datei wurde direkt aus dem ZIP-Archiv gelesen; das Archiv und die enthaltene Datei wurden nicht verändert.

- Dateigröße: **952.688 Bytes**
- SHA-256: `c7fa3d51c9bdce14b988d20fd8ed57ac7da9837803090ac858990613ec53ae35`
- VM-Directory-Block: Dateioffset `0x0CF400`
- Directory-Einträge beginnen bei `0x0CF420`
- Directory-Eintragsgröße: 12 Bytes
- Auswahlbedingung: drittes WORD (User-ID) `0x2222`, viertes WORD (Blockgröße) `0x0130`
- Ergebnis: **81 Datensätze**

Wichtig zur Feldinterpretation des Directory-Eintrags: Die 12 Bytes wurden als sechs WORDs gelesen. Die hier verwendeten Felder sind WORD 0 = Speicherhandle, WORD 1 = Flags, WORD 2 = User-ID, WORD 3 = Größe; die letzten vier Bytes bilden die Dateiposition. Das erste WORD ist also nicht die User-ID und auch nicht der Beginn des Datensatzinhalts.

## 2. Verteilung und Aufbau ab Datensatzoffset +0x10

Alle 81 Datensätze wurden in Little-Endian-WORDs zerlegt. Der Bereich `+0x10` bis `+0x12E` umfasst 144 WORDs.

Konstant bzw. nahezu konstant sind unter anderem:

| Offset | Beobachtung in 81 Datensätzen |
|---|---|
| `+0x10` | `0x0014` in 81/81 |
| `+0x106` | `0x010A` in 81/81 |
| `+0x10A` | `0x0000` in 81/81 |
| `+0x11A` | `0x0120` in 81/81 |
| `+0x120` | `0x0126` in 81/81 |
| `+0x126` | `0x0000` in 81/81 |

Ab `+0x10` zeigt sich in vielen Datensätzen zunächst ein wiederkehrendes WORD-Muster: an geraden Positionen `+0x10, +0x14, +0x18, ...` stehen aufsteigende Werte (`0x0014`, `0x0016`, `0x0018`, ...); an den dazwischenliegenden Positionen steht häufig `0x010E`. Dieses Muster ist jedoch nicht in allen Datensätzen gleich lang und wird danach unterschiedlich fortgesetzt.

## 3. Markerhäufigkeiten und Übergänge

Die Marker `0x010E` und `0x0114` treten in den WORD-Spalten mit 4-Byte-Abstand (also jeweils in der zweiten Position eines mutmaßlichen Paares) häufig auf. Ihre Anzahl und Endposition variieren deutlich zwischen den Datensätzen.

Die Zählung zeigt:

- `0x010E` kommt in vielen Datensätzen als früher Marker vor, endet aber je Datensatz an unterschiedlichen Offsets.
- `0x0114` tritt häufig anschließend auf; bei vier Datensätzen fehlt dieser Marker in dem untersuchten regelmäßigen Bereich vollständig.
- Die Markerfolge ist nicht durch eine einheitliche feste Länge begrenzt.
- Ab etwa `+0x110` ändert sich das statistische Bild deutlich: die Werte sind dort stark variabel und enthalten unter anderem kleine Zahlen, Nullwerte, ASCII-artige WORDs und weitere binär wirkende Werte.

Die Häufigkeitsanalyse der 81 Datensätze ergibt für einzelne WORD-Positionen:

| Offset | Häufigste Werte (Anzahl) |
|---|---|
| `+0x12` | `0x010E` (80), `0x0016` (1) |
| `+0x14` | `0x0016` (80), `0xA31F` (1) |
| `+0x16` | `0x010E` (79), `0x001A` (1), `0x0052` (1) |
| `+0x18` | `0x0018` (80), `0x1E89` (1) |
| `+0x1A` | `0x010E` (79), `0x001E` (1), `0x0062` (1) |
| `+0x1C` | `0x001A` (80), `0xF626` (1) |
| `+0x1E` | `0x010E` (80), `0x0022` (1) |
| `+0x20` | `0x001C` (80), `0x1000` (1) |
| `+0x22` | `0x010E` (80), `0x0026` (1) |
| `+0x106` | `0x010A` (81) |
| `+0x10A` | `0x0000` (81) |
| `+0x114` | `0x010E` (77), `0x011A` (4) |
| `+0x11A` | `0x0120` (81) |
| `+0x120` | `0x0126` (81) |

## 4. Auffällige Datensätze

Die bereits in Untersuchung 131 erkannten Ausnahmen bleiben auch in der Gesamtfeldanalyse sichtbar:

- **Directory-Index 9**, Datei-Offset `0x000250`: Das frühe Paarmuster ist bereits ab `+0x10` unterbrochen. Die folgenden WORDs enthalten unter anderem `0xA31F`, `0x1E89`, `0xF626` und `0x1000`. Dies ist kein bloß kurzer Datensatz des sonst üblichen Musters.
- **Directory-Index 313**, Datei-Offset `0x086860`: Das regelmäßige Muster ist zunächst vorhanden; später weicht der Marker bei `+0x12` von `0x010E` auf `0x001A` ab.
- **Directory-Index 335**, Datei-Offset `0x0783E0`: Das regelmäßige Anfangsmuster ist länger vorhanden; ab dem späteren Bereich tritt ebenfalls eine abweichende Marker-/Nullstruktur auf.
- **Directory-Index 357**, Datei-Offset `0x08B2D0`: Das Anfangsmuster bricht deutlich früher ab; anschließend folgen unter anderem `0x002A` und Null-WORDs.

Zusätzlich gibt es zahlreiche Datensätze, in denen das `0x010E`-Muster unterschiedlich lang ist und danach `0x0114` oder andere Werte folgen. Die Unterschiede sind daher nicht auf die vier zuvor isolierten Ausnahmen beschränkt.

## 5. Abgrenzung: Was ist damit bewiesen – und was nicht?

**Bewiesen durch die Byteanalyse:**

1. Es existieren exakt 81 Directory-Einträge mit User-ID `0x2222` und Blockgröße `0x0130` in dieser konkreten `SYSTEM/TOKEN.DB`.
2. Die Datensätze besitzen wiederkehrende WORD-Konstanten und eine variable, teilweise markerartige Struktur.
3. Die frühe Sequenz aus aufsteigenden WORDs und `0x010E` ist ein häufiges, aber nicht universelles Muster.
4. Spätere Bereiche enthalten andere, stark variable WORD-Folgen.

**Nicht bewiesen:**

1. Dass die aufsteigenden WORDs Offsets, Koordinaten, Zeichenindizes oder Moniker-Referenzen sind.
2. Dass `0x010E` oder `0x0114` eine bestimmte Typ-, Längen- oder Terminatorbedeutung besitzen.
3. Dass die Datensätze unmittelbar Icons oder Icon-Bilddaten enthalten.
4. Dass Werte innerhalb der Datensätze gültige Dateioffsets oder VM-Handles sind.

Die Werte wurden deshalb nicht als Zeiger interpretiert und es wurde keine Zieladresse daraus abgeleitet.

## 6. Konsequenz für GeoViewPlus

Noch keine Änderung am Programmcode. Der nächste belastbare Schritt ist, die Bedeutung der Felder über unabhängige Referenzketten zu bestimmen: insbesondere über VM-Block-/Handle-Bezüge, die auf dieselbe Datenstruktur zeigen, und über bekannte Icon-/Moniker-Ressourcen aus einer nachweislich zugehörigen GeoWorks-1.x-Datei. Erst wenn eine solche Referenzkette durchgängig nachvollziehbar ist, darf ein Feld als Icon-Referenz implementiert werden.

## 7. Reproduzierbarkeit

Die Analyse basiert ausschließlich auf der oben bezeichneten `SYSTEM/TOKEN.DB` aus dem hochgeladenen `GEOWORKS.zip`. Andere `TOKEN.DB`-Varianten (einschließlich `SYSTEM/TOKENDB.ALT/TOKEN.DB` und `BUCH/TOKEN.DB`) wurden nicht in diese Zählung eingemischt. Die Originaldateien blieben unverändert.
