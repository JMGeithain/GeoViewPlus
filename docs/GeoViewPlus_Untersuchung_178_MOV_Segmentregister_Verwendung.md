# Untersuchung 178 – Die 50 MOV-immediate-Relokationsstellen im Kontext

## Ziel

Untersuchung 177 fand 50 MZ-Relokationsstellen, an denen unmittelbar vor dem Relokations-WORD ein Opcode aus `B8h–BFh` steht. Diese Untersuchung betrachtet die folgenden Bytes, um zu prüfen, ob die geladenen WORD-Werte als Segmentwerte verwendet werden.

## Untersuchte Datei

- `Basebox-SVGA-Ensemble12/source/pm-backport/target-original/GWSVGA/KERNEL.EXE`
- Größe: 72.736 Byte
- SHA-256: `c2cc8952cdb01d0f459bf281ee3b78f8ce9464aba0b58c3758f8c73e24fb6eb5`
- MZ-Headergröße: `0600h`
- 276 MZ-Relokationen

Alle Offsets in den Tabellen sind Segment:Offset-Werte des MZ-Relokationseintrags. Die Datei-Offsets sind davon zu unterscheiden.

## 1. Inhalt der 50 MOV-immediate-Operanden

Die 50 Operanden verteilen sich auf drei gespeicherte Werte:

| Operandwert | Anzahl |
|---:|---:|
| `0E34h` | 44 |
| `0000h` | 5 |
| `0F93h` | 1 |
| **Summe** | **50** |

Die 44 Operanden mit Wert `0E34h` sind besonders auffällig. In 40 Fällen folgt unmittelbar auf die MOV-Instruktion ein Opcode `8Eh` (`MOV Sreg,r/m16`). Das unmittelbar geladene Segmentwort wird also direkt in ein Segmentregister übertragen.

## 2. Direkte Segmentregister-Ladevorgänge mit Wert 0E34h

Die 40 unmittelbaren Folgeinstruktionen teilen sich so auf:

| Zielsegmentregister | Anzahl | Byteform nach dem unmittelbaren Wert |
|---|---:|---|
| DS | 34 | `8E /r`, ModR/M-Regfeld = 3 |
| ES | 6 | `8E /r`, ModR/M-Regfeld = 0 |
| **Summe** | **40** | |

Beispiele:

- `B8 34 0E 8E D8` = `MOV AX,0E34h`; `MOV DS,AX`
- `BD 34 0E 8E DD` = `MOV BP,0E34h`; `MOV DS,BP`
- `BF 34 0E 8E C7` = `MOV DI,0E34h`; `MOV ES,DI`
- `BA 34 0E 8E C2` = `MOV DX,0E34h`; `MOV ES,DX`

Damit ist für diese 40 Stellen nicht nur eine zufällige Zahlenhäufung nachgewiesen: Der Wert `0E34h` wird unmittelbar als Segmentwert in DS oder ES geladen.

### Vollständige Liste der 40 direkten Stellen

| MZ-Relokationsposition | Register-MOV | Folgebefehl |
|---|---|---|
| `0000:09BB` | `MOV BP,0E34h` | `MOV DS,BP` |
| `0000:1845` | `MOV AX,0E34h` | `MOV DS,AX` |
| `0000:1F1F` | `MOV BX,0E34h` | `MOV DS,BX` |
| `0000:1F7B` | `MOV AX,0E34h` | `MOV DS,AX` |
| `0000:1FA8` | `MOV AX,0E34h` | `MOV DS,AX` |
| `0000:226D` | `MOV BP,0E34h` | `MOV DS,BP` |
| `0000:22B1` | `MOV AX,0E34h` | `MOV DS,AX` |
| `0000:3CC7` | `MOV AX,0E34h` | `MOV DS,AX` |
| `0000:3CF6` | `MOV AX,0E34h` | `MOV DS,AX` |
| `0000:4131` | `MOV AX,0E34h` | `MOV DS,AX` |
| `0000:41B5` | `MOV AX,0E34h` | `MOV DS,AX` |
| `0000:56F6` | `MOV BX,0E34h` | `MOV DS,BX` |
| `0000:594B` | `MOV AX,0E34h` | `MOV DS,AX` |
| `0000:6F9C` | `MOV AX,0E34h` | `MOV DS,AX` |
| `0000:6FE1` | `MOV AX,0E34h` | `MOV DS,AX` |
| `0000:7173` | `MOV AX,0E34h` | `MOV DS,AX` |
| `0000:71EC` | `MOV AX,0E34h` | `MOV DS,AX` |
| `0000:75DD` | `MOV SI,0E34h` | `MOV DS,SI` |
| `0000:78D2` | `MOV AX,0E34h` | `MOV DS,AX` |
| `0000:98D7` | `MOV AX,0E34h` | `MOV ES,AX` |
| `0000:9ACA` | `MOV AX,0E34h` | `MOV DS,AX` |
| `0000:9E60` | `MOV AX,0E34h` | `MOV DS,AX` |
| `0000:A0A1` | `MOV AX,0E34h` | `MOV DS,AX` |
| `0000:AD16` | `MOV BP,0E34h` | `MOV DS,BP` |
| `0F93:0004` | `MOV BX,0E34h` | `MOV DS,BX` |
| `0F93:0163` | `MOV DI,0E34h` | `MOV ES,DI` |
| `0F93:0197` | `MOV DX,0E34h` | `MOV ES,DX` |
| `0F93:01C9` | `MOV AX,0E34h` | `MOV DS,AX` |
| `0F93:0450` | `MOV DI,0E34h` | `MOV ES,DI` |
| `0F93:048A` | `MOV BP,0E34h` | `MOV ES,BP` |
| `0F93:06D6` | `MOV CX,0E34h` | `MOV DS,CX` |
| `0F93:07CE` | `MOV AX,0E34h` | `MOV DS,AX` |
| `0F93:0846` | `MOV CX,0E34h` | `MOV DS,CX` |
| `0F93:08E6` | `MOV DI,0E34h` | `MOV DS,DI` |
| `0F93:1073` | `MOV SI,0E34h` | `MOV DS,SI` |
| `0F93:1161` | `MOV AX,0E34h` | `MOV DS,AX` |
| `0F93:1251` | `MOV BX,0E34h` | `MOV DS,BX` |
| `0F93:1826` | `MOV AX,0E34h` | `MOV DS,AX` |
| `0F93:1AF5` | `MOV SI,0E34h` | `MOV ES,SI` |
| `0F93:1B79` | `MOV AX,0E34h` | `MOV DS,AX` |

## 3. Vier weitere MOV-Stellen mit Operand 0E34h

Die übrigen vier der 44 `0E34h`-Operanden haben keine unmittelbar folgende Segmentregister-Übertragung. Drei zeigen aber einen späteren Segmentregister-Kontext:

- `0000:0162`: `MOV DX,0E34h`; danach folgen arithmetische Operationen auf DX und anschließend `MOV SS,DX` (`8E D2`). Der Segmentwert wird also nicht unverändert unmittelbar übernommen, sondern DX wird zuvor verändert.
- `0000:D216`: `MOV BP,0E34h`; danach `MOV DI,118Ah`; anschließend `MOV DS,BP` (`8E DD`). Das Segmentladen erfolgt mit einem Zwischenschritt.
- `0F93:08BD`: `MOV DI,0E34h`; danach `PUSH DS` und `MOV DS,DI` (`8E DF`). Auch hier folgt die Segmentübertragung verzögert.
- `0000:44BE`: `MOV BP,0E34h`; unmittelbar danach `RET`. In diesem lokalen Ausschnitt ist keine Segmentübertragung belegt; mögliche Verwendung durch den Aufrufer bleibt offen.

Diese drei verzögerten Fälle plus die 40 unmittelbaren Fälle ergeben 43 Stellen, bei denen die lokale Bytefolge eine Verwendung des Werts `0E34h` als Segmentwert nahelegt bzw. direkt belegt. Der Fall `0000:44BE` bleibt unklassifiziert.

## 4. Der einzelne Operandwert 0F93h

Bei `0F93:002E` lautet die Bytefolge:

`B9 93 0F 8E D9`

Das ist:

- `MOV CX,0F93h`
- `MOV DS,CX`

Auch der Wert `0F93h` wird somit direkt in DS geladen. Er entspricht zugleich einem der Segmentfelder, die in der MZ-Relokationstabelle vorkommen. Das ist ein konkreter Zusammenhang im MZ-Programm, aber noch kein Beleg für eine symbolische Segmentbezeichnung.

## 5. Die fünf Null-Operanden

Fünf der 50 MOV-immediate-Relokationen enthalten den gespeicherten Wert `0000h`. Die Folgebytes zeigen nicht in allen Fällen eine direkte Segmentregister-Übertragung. Sie sind deshalb getrennt zu behandeln; ein Nullwert kann ein initialisierter Offset, Zähler, Zeigerbestandteil oder anderer Operand sein. Ohne vollständigen Kontrollfluss und Datenfluss darf er nicht als „Nullsegment“ interpretiert werden.

## 6. Ergebnis

**Gesichert:**

1. Von 50 MOV-immediate-Relokationen enthalten 44 den Wert `0E34h`, fünf `0000h` und eine `0F93h`.
2. 40 der 44 `0E34h`-Werte werden unmittelbar nach dem MOV in DS (34-mal) oder ES (6-mal) übertragen.
3. Drei weitere `0E34h`-Fälle zeigen eine verzögerte Segmentregister-Übertragung in DS bzw. SS.
4. Der einzelne Wert `0F93h` wird unmittelbar in DS übertragen.
5. Ein `0E34h`-Fall bleibt lokal unklassifiziert.

**Nicht bewiesen:**

- welche symbolischen Namen den Segmenten `0E34h` und `0F93h` entsprechen;
- ob `0E34h` ein einzelnes logisches Modul oder ein gemeinsamer Daten-/Codebereich ist;
- welche Funktion jede einzelne MOV-Stelle erfüllt.

## 7. Nächster Schritt

Untersuchung 179 sollte die unmittelbaren DS-/ES-Ladevorgänge nach den nachfolgenden Zugriffen gruppieren. Insbesondere ist zu prüfen, ob die folgenden Instruktionen wiederkehrend auf feste Offsets wie `[98h]`, `[10h]`, `[44h]` oder andere Datenstrukturen zugreifen. Damit könnte die Rolle des Segments `0E34h` näher eingegrenzt werden, ohne eine unbelegte symbolische Benennung vorzunehmen.

---
*Read-only-Analyse. Keine Änderung an KERNEL.EXE, GEO-Dateien oder GeoViewPlus-Programmcode.*
