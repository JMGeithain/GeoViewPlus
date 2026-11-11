# Untersuchung 176 – Kartierung der MZ-Relokationsstellen nach Segment

## Ziel und Methode

Untersuchung 175 hat die 276 DOS-MZ-Relokationen der im Ensemble enthaltenen `KERNEL.EXE` gezählt und nach dem Segmentfeld der Relokationseinträge gruppiert. Hier wird geprüft, wo die zu korrigierenden WORDs innerhalb des MZ-Ladebereichs liegen und welche lokalen Bytekontexte dort vorkommen.

Für einen MZ-Relokationseintrag mit Offset `o` und Segment `s` liegt das zu korrigierende WORD im Ladebereich bei:

`linearer Ladebereichsoffset = s × 16 + o`

Der tatsächliche Dateioffset ist zusätzlich um die MZ-Headergröße `0600h` erhöht. Es handelt sich um die **Position des Relokationsziels**, nicht um die Adresse des durch den Wert referenzierten Objekts.

## Untersuchte Datei

- Datei: `KERNEL.EXE` im Ordner `source/pm-backport/target-original/GWSVGA`
- Größe: 72.736 Byte
- SHA-256: `c2cc8952cdb01d0f459bf281ee3b78f8ce9464aba0b58c3758f8c73e24fb6eb5`
- MZ-Header: 96 Paragraphen = `0600h`
- MZ-Relokationen: 276

## 1. Verteilung der Relokationsstellen

Die 276 Einträge verteilen sich auf drei Segmentfelder:

| Segmentfeld des MZ-Eintrags | Anzahl | kleinster Offset | größter Offset |
|---:|---:|---:|---:|
| `0000h` | 61 | `0162h` | `D216h` |
| `0E34h` | 59 | `0004h` | `0FCBh` |
| `0F93h` | 156 | `0004h` | `1CCFh` |
| **Gesamt** | **276** | | |

Die Werte sind Segment:Offset-Positionen **innerhalb des MZ-Ladebereichs**, an denen das DOS-Ladeprogramm WORDs korrigiert. Sie beschreiben nicht die Anzahl oder Größe von drei eigenständigen Programmsegmenten.

## 2. Räumliche Verteilung

Die Relokationsstellen sind nicht gleichmäßig verteilt:

- Segmentfeld `0000h`: 61 Einträge über einen großen Offsetbereich von `0162h` bis `D216h`. Es gibt einzelne weit auseinanderliegende Stellen und kleine Häufungen, unter anderem im Bereich `8F00h` bis `9100h` (26 Einträge in diesen beiden 256-Byte-Fenstern zusammen).
- Segmentfeld `0E34h`: 59 Einträge. Davon liegen 7 in `0000h–00FFh`, 3 in `0500h–05FFh`, 13 in `0E00h–0EFFh` und 36 in `0F00h–0FFFh`. Die Häufung am oberen Ende des Offsetbereichs ist deutlich.
- Segmentfeld `0F93h`: 156 Einträge über `0004h` bis `1CCFh`. Sie verteilen sich über fast den gesamten Bereich; auffällige Häufungen liegen beispielsweise in `0800h–08FFh`, `0C00h–0CFFh` und `1700h–17FFh`.

Diese Verteilung beschreibt ausschließlich die Positionen der Relokations-WORDs. Eine semantische Segmentklassifikation als „Code“, „Daten“, „Heap“ oder „Exporttabelle“ folgt daraus allein nicht.

## 3. Bytekontexte an repräsentativen Stellen

Die lokalen Bytes zeigen, dass die Relokations-WORDs in unterschiedlichen Kontexten vorkommen:

### Segmentfeld `0000h`

- Offset `0162h`: Bytes `BA 34 0E 81 EA 00 00 03 D0...`; das Relokations-WORD folgt hier auf eine unmittelbare Register-/Operandsequenz.
- Offset `02B4h`: Kontext `... FE 9A 00 00 93 0F 2E 01...`.
- Offset `09BBh`: Kontext `... 55 06 1E BD 34 0E 8E DD...`.

### Segmentfeld `0E34h`

- Offset `0004h`: Anfangskontext `10 00 10 00 34 0E 00 00...`.
- Offset `001Eh`: Kontext `... E5 9D 00 00 E9 9D 00 00 ED 9D...`, eine Folge von WORD-artigen Werten.
- Offset `05BAh`: Kontext `... 4D 11 93 0F 9A BB 97 00 00 50...`.

### Segmentfeld `0F93h`

- Offset `0004h`: Kontext `FC 8C D8 BB 34 0E 8E DB...`.
- Offset `016Dh`: Kontext `... 00 9A 13 98 00 00 B4 09 CD 21...`; hier steht das Relokations-WORD unmittelbar in einem FAR-CALL-Operandkontext.
- Offset `0281h`: Kontext `... 00 9A 19 1F 00 00 73 08 9A 99...`, ebenfalls mit FAR-CALL-Opcode `9Ah` vor einem Relokations-WORD.

Die Beispiele belegen, dass Relokationen an unterschiedlichen Arten von Bytekontexten vorkommen. Sie reichen jedoch nicht aus, um den gesamten jeweiligen Segmentbereich pauschal als Code oder Daten zu klassifizieren.

## 4. Verhältnis zu den elf Treiber-FAR-CALL-Zielen

Die elf in Untersuchung 173 ermittelten Werte (`0000h`, `0002h`, `0005h`, `0006h`, `00AAh`, `00ABh`, `00C2h`, `00D0h`, `0126h`, `01C2h`, `01C4h`) sind gespeicherte Ziel-Offsets aus FAR-CALL-Operanden der Treiber. Die MZ-Tabelle der Kernel-Datei beschreibt hingegen, wo im Kernel-Ladebereich der DOS-Lader WORDs anpasst.

Daher sind die beiden Wertemengen nicht direkt vergleichbar. Insbesondere darf man die MZ-Segmentfelder `0000h`, `0E34h`, `0F93h` nicht als Zielsegmente der elf Treiber-Aufrufe interpretieren.

## 5. Ergebnis

**Gesichert:**

1. Die 276 MZ-Relokationen liegen an drei Gruppen von Segment:Offset-Positionen.
2. Die Gruppe `0F93h` ist mit 156 Einträgen die größte; `0000h` und `0E34h` enthalten 61 bzw. 59 Einträge.
3. Die Relokationsstellen im Segmentfeld `0E34h` häufen sich stark am Ende seines untersuchten Offsetbereichs.
4. Die Bytekontexte sind heterogen; mindestens einzelne Relokationsstellen liegen erkennbar in FAR-CALL-Operanden, andere in WORD-Folgen oder Instruktionskontexten.

**Nicht bewiesen:**

- dass die drei Segmentfelder drei logische Kernel-Komponenten bezeichnen;
- dass ein Segmentfeld einem Export-/API-Segment entspricht;
- dass sich die elf Treiber-Kernel-Ziel-Offsets aus der MZ-Relokationstabelle ablesen lassen.

## 6. Nächster Schritt

Untersuchung 177 sollte die MZ-Relokationen nach dem **gespeicherten WORD-Inhalt** und nach dem **lokalen Instruktionsmuster** gruppieren. Besonders die FAR-CALL-Kontexte können Hinweise auf interne Aufrufketten geben. Die Analyse muss weiterhin zwischen MZ-Relokationsstelle, gespeichertem Segmentwert und dem separaten GeoWorks-Relokationstyp unterscheiden.

---
*Read-only-Analyse. Keine Änderung an KERNEL.EXE, GEO-Dateien oder GeoViewPlus-Programmcode.*
