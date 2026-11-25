# GeoView Plus – Untersuchung 0.4.10
## Auflösung des ersten Kernel-Far-Calls über die MZ-Relokation

**Gegenstand:** PC/GEOS 1.x, `GEOWORKS/KERNEL.EXE` und `GEOWORKS/KERNEL.OLD` aus `GEOWORKS.zip`.
**Methode:** MZ-Header und Relokationstabelle bytegenau ausgewertet; Segmentziele in das Dateiladebild umgesetzt. Originaldateien unverändert.

### 1. Neuer entscheidender Befund

Der MZ-Einstiegscode beginnt bei beiden Dateien am Dateioffset `0x08B1` (Ladebildoffset `0x02B1`) und enthält einen Far Call:

- `KERNEL.EXE`: `9A 00 00 93 0F` → `CALL FAR 0F93:0000`
- `KERNEL.OLD`: `9A 00 00 90 0F` → `CALL FAR 0F90:0000`

Die Segmentwörter liegen im Ladebild an Offset `0x02B4`. In beiden MZ-Relokationstabellen existiert ein Eintrag für `0000:02B4`. Damit ist belegt, dass das Segmentwort beim Laden als MZ-relokierbare Segmentadresse behandelt wird.

### 2. Zieladresse im Dateibild

Der MZ-Header ist `0x600` Bytes lang. Die Dateiabbildung eines Segmentoffsets `S:O` lautet:

`Dateioffset = 0x600 + S * 16 + O`

Daraus ergibt sich:

| Kernel | Segmentziel | Dateioffset des Segments |
|---|---:|---:|
| `KERNEL.EXE` | `0F93:0000` | `0xFF30` |
| `KERNEL.OLD` | `0F90:0000` | `0xFF00` |

Die Anfangsbytes sind in beiden Versionen strukturell gleich. Die Stack-Segment-Konstante unterscheidet sich (`0E34h` gegenüber `0E35h`).

### 3. Zweiter Aufruf innerhalb desselben Segments

- `KERNEL.EXE`: `CALL FAR 0F93:01C7` → Dateioffset `0x100F7`
- `KERNEL.OLD`: `CALL FAR 0F90:01C7` → Dateioffset `0x100C7`

Die Zielbytes beginnen in beiden Dateien mit `1E B8 ...`; versionsabhängige Datenwerte unterscheiden sich. Die vollständige Semantik der Routinen ist noch nicht symbolisch bestimmt.

### 4. Gesicherte Ergebnisse

1. MZ-Einstiegspunkt: `0000:02B1`.
2. Der erste Far Call führt in ein internes, MZ-relokiertes Kernel-Segment.
3. Zielsegment im `KERNEL.EXE`: `0F93h`; im `KERNEL.OLD`: `0F90h`.
4. Der zweite Far Call zielt auf Offset `01C7h` desselben Segments.
5. Die Zielbytes sind im Dateiladebild lokalisiert und können separat disassembliert werden.

### 5. Offene Punkte

- Symbolische Namen/API-Bedeutung der Routinen bei `S:0000` und `S:01C7`.
- Auflösung der `LOCAL.GEO`-Aufrufe `0000:0093` und `0000:0006` im GEOS-Segment-/Dispatchermodell.
- Zusammenhang zwischen `LOCAL.GEO`-`quotes` und langer Dateinamencodierung.
- Unicode-Zuordnungen für `0xCE`, `0xCF`, `0xD0`, `0xD1`.

### 6. Nächster Schritt

Routinen ab `0F93:0000` und `0F93:01C7` mit korrekter 16-Bit-Segmentbasis disassemblieren, interne Aufrufe und Speicherzugriffe verfolgen und mit dem Originalkernel vergleichen. LOCAL.GEO-Aufrufe bis zum Nachweis ihres Segmentmodells separat behandeln.

**Status:** Der erste MZ-Far-Call ist durch den Relokationseintrag als interner Kernel-Segmentaufruf nachgewiesen. Keine Änderung am GeoView-Plus-Decoder oder an der Zeichentabelle.