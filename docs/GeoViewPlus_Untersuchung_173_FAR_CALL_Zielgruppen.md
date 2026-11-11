# Untersuchung 173 – Gruppierung der FAR-CALL-Ziele in den SVGA-Treibern

## Fragestellung

Untersuchung 172 hat die 44 Relokationen vom Typ `00h` in Ressource 1 der fünf SVGA-Treiber als Operanden von 8086-`CALL FAR` identifiziert. Diese Untersuchung trennt nun die **44 Aufrufstellen** von den **tatsächlich verwendeten Ziel-Offsets** und prüft, ob die unmittelbaren Codekontexte zwischen den fünf Treibern übereinstimmen.

## Untersuchte Dateien

Aus `Basebox-SVGA-Ensemble12(2).zip`:

- `BB120_64.GEO`
- `BB72_64.GEO`
- `BB96_64.GEO`
- `S16_1280.GEO`
- `V16_0720.GEO`

Alle fünf Dateien besitzen Ressource 1 ab Dateioffset `013Eh`. Die Relokationstabelle von Ressource 1 enthält 72 Einträge; die 44 Einträge mit `info=00h` wurden ausgewertet. Die Originaldateien wurden nicht verändert.

## 1. 44 Aufrufstellen und 11 unterschiedliche Ziel-Offsets

Die 44 Relokationseinträge bezeichnen 44 unterschiedliche Stellen innerhalb von Ressource 1. An jeder Stelle steht unmittelbar davor der Opcode `9Ah` (8086 `CALL FAR ptr16:16`). Das Operandformat ist:

```
9A  <Offset-WORD, little endian>  <Segment-WORD, little endian>
```

In allen 44 Fällen ist das Segment-WORD im gespeicherten GEO-Abbild `0000h`. Das Offset-WORD ergibt elf unterschiedliche Werte:

| Ziel-Offset | Aufrufstellen |
|---:|---:|
| `01C2h` | 9 |
| `00AAh` | 7 |
| `00ABh` | 7 |
| `0006h` | 7 |
| `0005h` | 4 |
| `00C2h` | 2 |
| `0126h` | 2 |
| `0000h` | 2 |
| `0002h` | 2 |
| `00D0h` | 1 |
| `01C4h` | 1 |
| **Summe** | **44** |

Die Werte sind Ziel-Offsets im durch die Relokation referenzierten Kernel-Segmentkontext. Sie sind keine Dateioffsets in der GEO-Datei. Eine Zuordnung zu symbolischen Kernel-Funktionsnamen ist mit den hier nachgewiesenen Bytes nicht möglich.

## 2. Exakte Aufrufstellen

Die Relokationsziele (Offset innerhalb von Ressource 1) und die gespeicherten FAR-Ziele lauten:

| Aufrufstelle R1 | FAR-Ziel |
|---:|---:|
| `0364h` | `0000:00AA` |
| `037Eh` | `0000:00AA` |
| `03A2h` | `0000:00AB` |
| `03C5h` | `0000:00AB` |
| `03DCh` | `0000:00AA` |
| `03F7h` | `0000:00AB` |
| `0418h` | `0000:00AA` |
| `0433h` | `0000:00AA` |
| `0449h` | `0000:00AB` |
| `0472h` | `0000:00AB` |
| `06BFh` | `0000:01C2` |
| `0851h` | `0000:01C2` |
| `089Bh` | `0000:00C2` |
| `09E8h` | `0000:01C2` |
| `0E43h` | `0000:00AB` |
| `0E51h` | `0000:00D0` |
| `0E63h` | `0000:00AA` |
| `0F36h` | `0000:0126` |
| `0F4Bh` | `0000:0126` |
| `0FE7h` | `0000:01C2` |
| `1015h` | `0000:01C4` |
| `11BFh` | `0000:0006` |
| `11CAh` | `0000:0005` |
| `1209h` | `0000:0006` |
| `150Fh` | `0000:0005` |
| `1535h` | `0000:0006` |
| `1546h` | `0000:0006` |
| `159Fh` | `0000:0005` |
| `15C5h` | `0000:0006` |
| `15D6h` | `0000:0006` |
| `2002h` | `0000:01C2` |
| `2022h` | `0000:00C2` |
| `49BAh` | `0000:01C2` |
| `4B3Fh` | `0000:01C2` |
| `4CA6h` | `0000:0000` |
| `4CC2h` | `0000:0002` |
| `4DE3h` | `0000:01C2` |
| `52AAh` | `0000:01C2` |
| `54EEh` | `0000:00AB` |
| `5520h` | `0000:00AA` |
| `61C2h` | `0000:0000` |
| `61F5h` | `0000:0005` |
| `61FCh` | `0000:0006` |
| `624Ah` | `0000:0002` |

## 3. Vergleich der fünf Treiber

An allen 44 Aufrufstellen wurden die Bytes vor dem Operand und die vier Operandbytes verglichen. Die Bytefenster von 1, 3, 5 und 8 Bytes vor dem Relokationsziel bis einschließlich der vier Operandbytes sind in allen fünf Dateien identisch.

Damit gilt: Nicht nur die Relokationseinträge, sondern auch die lokalen Maschineninstruktions-Kontexte aller 44 FAR-Aufrufe stimmen in den fünf untersuchten Treibern überein. Die Unterschiede der Treiber liegen in anderen Bereichen von Ressource 1 und ändern diese Aufrufstellen nicht.

## 4. Was daraus folgt – und was nicht

**Gesichert:**

- 44 FAR-CALL-Aufrufstellen.
- 11 unterschiedliche gespeicherte Ziel-Offsets.
- Alle gespeicherten Segment-WORDs dieser Aufrufe sind `0000h`.
- Die untersuchten lokalen Codefenster sind über alle fünf GEO-Dateien identisch.

**Nicht gesichert:**

- Die Namen der aufgerufenen Kernel-Funktionen.
- Ob zwei unterschiedliche Offsets semantisch verschiedene API-Funktionen oder unterschiedliche Eintrittspunkte in gemeinsame Routinen sind.
- Die Bedeutung der vier Relokationen vom Typ `23h` und der 24 Relokationen vom Typ `22h`.

Die in demselben Archiv enthaltene Datei `KERNEL.EXE` (72.736 Bytes; eingebettete Copyright-Zeichenfolge „Copyright GeoWorks 1991“) ist ein konkreter Kandidat für eine spätere Kernel-Binäranalyse. Allein aus der Copyright-Zeichenfolge und den FAR-Ziel-Offsets lässt sich jedoch keine Funktionsnamenszuordnung ableiten. Die im Archiv enthaltene moderne `pcgeos-master`-Quelle ist kein Beleg für die Symbolbelegung eines GeoWorks-1.x-Kernels und wird deshalb nicht zur Benennung dieser Ziele herangezogen.

## 5. Nächster sinnvoller Untersuchungsschritt

Als Untersuchung 174 sollte die konkrete `KERNEL.EXE` aus dem gleichen Ensemble-/Treiberpaket unabhängig auf ausführbare Segmentstruktur, Tabellen und mögliche Symbol-/Namensreste untersucht werden. Erst wenn sich eine belastbare Zuordnung zwischen Kernel-Segment und den Offsets `0000h`, `0002h`, `0005h`, `0006h`, `00AAh`, `00ABh`, `00C2h`, `00D0h`, `0126h`, `01C2h` und `01C4h` ergibt, dürfen Funktionsnamen eingetragen werden.

---
*Read-only-Binäranalyse. Keine Änderung an den Original-GEO-Dateien und keine Änderung am GeoViewPlus-Programmcode.*
