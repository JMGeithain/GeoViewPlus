# Untersuchung 177 – MZ-Relokationswerte und Instruktionskontexte

## Anlass und wichtige Korrektur

Untersuchung 176 hat beispielhaft FAR-CALL-Kontexte an MZ-Relokationsstellen erwähnt. Die erneute programmgesteuerte Prüfung der tatsächlichen `KERNEL.EXE` ergibt jedoch:

**Keine der 276 MZ-Relokationsstellen hat unmittelbar vor dem Relokations-WORD das Byte `9Ah`.** Damit ist an keiner dieser Stellen der 8086-Opcode `CALL FAR ptr16:16` durch dieses einfache unmittelbare Bytekriterium belegt. Die entsprechenden FAR-CALL-Beispiele aus Untersuchung 176 sind zurückzunehmen und nicht als gesicherter Befund zu verwenden.

Die 44 FAR-CALL-Operanden aus Untersuchung 173 betreffen dagegen die GeoWorks-Relokationen in Ressource 1 der fünf SVGA-Treiber. Sie sind eine andere Datei und eine andere Relokationsebene. Die beiden Ergebnisse dürfen nicht vermischt werden.

## Untersuchte Datei

- `Basebox-SVGA-Ensemble12/source/pm-backport/target-original/GWSVGA/KERNEL.EXE`
- Größe: 72.736 Byte
- SHA-256: `c2cc8952cdb01d0f459bf281ee3b78f8ce9464aba0b58c3758f8c73e24fb6eb5`
- MZ-Headergröße: 96 Paragraphen = `0600h`
- Relokationstabelle: Dateioffset `003Ch`
- Anzahl MZ-Relokationen: 276

Die Relokationsstelle im Ladebereich wird für jeden MZ-Eintrag aus `Segment × 16 + Offset` berechnet; der Dateioffset ergibt sich durch Addition der MZ-Headergröße.

## 1. Häufigkeit der gespeicherten WORD-Werte

Die 276 WORD-Inhalte an den MZ-Relokationsstellen verteilen sich so:

| gespeicherter WORD-Wert | Anzahl |
|---:|---:|
| `0000h` | 222 |
| `0E34h` | 47 |
| `0F93h` | 5 |
| `0DEBh` | 1 |
| `0F53h` | 1 |
| **Gesamt** | **276** |

Diese Werte sind die Inhalte, auf die der DOS-MZ-Lader die Ladeparagraphenbasis addiert. Sie sind nicht die Segmentfelder der Relokationseinträge und auch keine symbolischen Funktionsnummern.

## 2. Kreuztabelle: Segmentfeld und gespeicherter WORD-Wert

| Segmentfeld | gespeicherter Wert | Anzahl |
|---:|---:|---:|
| `0000h` | `0000h` | 29 |
| `0000h` | `0E34h` | 29 |
| `0000h` | `0F93h` | 2 |
| `0000h` | `0DEBh` | 1 |
| `0E34h` | `0000h` | 57 |
| `0E34h` | `0E34h` | 1 |
| `0E34h` | `0F93h` | 1 |
| `0F93h` | `0000h` | 136 |
| `0F93h` | `0E34h` | 17 |
| `0F93h` | `0F93h` | 2 |
| `0F93h` | `0F53h` | 1 |
| **Summe** | | **276** |

Die Kreuztabelle zeigt, dass die gespeicherten WORD-Werte nicht einfach mit dem Segmentfeld identisch sind. Besonders häufig ist der Wert `0000h`, vor allem in der Gruppe mit Segmentfeld `0F93h`.

## 3. Eindeutig erkennbare MOV-immediate-Kontexte

An 50 Relokationsstellen steht unmittelbar vor dem Relokations-WORD ein Opcode aus `B8h–BFh`. Auf dem 8086 codiert diese Gruppe `MOV r16, imm16`: Das auf den Opcode folgende WORD ist ein unmittelbarer 16-Bit-Wert.

| Opcode | Instruktion | Anzahl |
|---:|---|---:|
| `B8h` | `MOV AX, imm16` | 24 |
| `B9h` | `MOV CX, imm16` | 5 |
| `BAh` | `MOV DX, imm16` | 3 |
| `BBh` | `MOV BX, imm16` | 4 |
| `BDh` | `MOV BP, imm16` | 6 |
| `BEh` | `MOV SI, imm16` | 4 |
| `BFh` | `MOV DI, imm16` | 4 |
| **Summe** | | **50** |

In dieser Gruppe fehlt `BCh` (`MOV SP, imm16`). Die Relokations-WORDs sind hier also unmittelbare Operanden der MOV-Instruktionen. Daraus lässt sich die jeweilige spätere Bedeutung des geladenen Wertes noch nicht bestimmen.

## 4. Prüfung auf FAR-CALL-Opcode

Für alle 276 Relokationsstellen wurde das Byte unmittelbar vor dem Relokations-WORD geprüft:

- Treffer für `9Ah`: **0**
- Relokationsstellen insgesamt: **276**

Das widerlegt nicht, dass die Kernel-Datei an anderen Stellen FAR-CALL-Instruktionen enthält. Es besagt ausschließlich, dass keine der 276 hier untersuchten MZ-Relokationsstellen direkt auf das erste Operandbyte einer unmittelbar vorausgehenden `9Ah`-Instruktion folgt.

## 5. Bedeutung und Grenzen

**Gesichert:**

1. Die gespeicherten WORD-Werte haben die oben dokumentierte Häufigkeitsverteilung.
2. Segmentfeld und gespeicherter WORD-Wert sind unterschiedliche Felder mit unterschiedlichen Verteilungen.
3. 50 Relokationsstellen liegen unmittelbar hinter einem Opcode der `MOV r16, imm16`-Familie.
4. Keine der 276 MZ-Relokationsstellen ist durch das unmittelbare Präfix `9Ah` als FAR-CALL-Operand ausgewiesen.

**Nicht gesichert:**

- die semantische Rolle der mit MOV geladenen Werte;
- die Namen oder Funktionen der referenzierten Segmente;
- eine Zuordnung zu den elf Kernel-Ziel-Offsets der SVGA-Treiber;
- eine allgemeine Code-/Datenklassifikation allein anhand dieser Relokationspositionen.

## 6. Nächster Schritt

Untersuchung 178 sollte die 50 MOV-immediate-Stellen einzeln mit etwas größerem Bytekontext dokumentieren und prüfen, ob sich wiederkehrende Codeabläufe oder konstante Segmentwerte erkennen lassen. Anschließend können die übrigen 226 Relokationsstellen nach klaren 8086-Operandmustern klassifiziert werden. Ein vollständiger Disassembler-/Kontrollflussnachweis wäre einer bloßen Suche nach einzelnen Opcode-Bytes vorzuziehen.

---
*Read-only-Analyse. Die KERNEL.EXE und die GEO-Dateien im Archiv wurden nicht verändert. Keine Änderung am GeoViewPlus-Programmcode.*
