# GeoView Plus – Untersuchung 0.4.11
## Kernel-Bootstrap: Segmentkopie und dynamische Anpassung des zweiten Far-Calls

**Gegenstand:** PC/GEOS 1.x, `KERNEL.EXE` und `KERNEL.OLD` aus `GEOWORKS.zip`. Originaldateien unverändert.

### 1. MZ-Einstiegscode

Am Ladebildoffset `0x02B1` steht:

```asm
02B1  9A 00 00 93 0F   call far 0F93:0000
02B6  2E 01 06 C8 02   add word cs:[02C8h],ax
02BB  B0 04            mov al,04h
02BD  BB 02 00         mov bx,0002h
02C0  33 C9            xor cx,cx
02C2  E8 E2 FE         call ...
02C5  9A C7 01 93 0F   call far 0F93:01C7
```

Im `KERNEL.OLD` stehen `0F90h` statt `0F93h`. Die MZ-Relokationstabelle enthält Einträge für die Segmentwörter bei `0x02B4` und `0x02C8`.

### 2. Maschinenwirkung des ersten Aufrufs

Der Code bei `KERNEL.EXE`-Dateioffset `0xFF30` (Segment `0F93:0000`) sichert `SS` und `SP` in einem Datenbereich, berechnet ein Zielsegment in `ES`, setzt `DS=0F93h`, `SI=DI=0` und führt `REP MOVSW` mit `CX=0x0E70` Wörtern aus. Damit kopiert er `0x1CE0` Bytes aus dem Segment `0F93h` in das berechnete Zielsegment. Anschließend liefert er `AX = ES - 0F93h` zurück und kehrt mit `RETF` zurück.

### 3. Dynamische Anpassung des zweiten Far-Calls

Direkt danach addiert der MZ-Einstiegscode `AX` zum Wort `CS:[02C8h]`. An `0x02C8` liegt das Segmentwort des zweiten Far Calls `0F93:01C7`. Der zweite Aufruf wird damit auf das gerade kopierte Segment umgestellt; der Offset `01C7h` bleibt bestehen.

Der gleiche Ablauf ist im Originalkernel vorhanden, mit Ausgangssegment `0F90h` und Stack-Segmentwert `0E35h` statt `0E34h`.

### 4. Code am zweiten Ziel

`0F93:01C7` beginnt mit `push ds`, lädt `DS=0E34h`, speichert einen Wert bei `DS:0044h`, speichert `CS` bei `DS:05BAh` und ruft mehrere interne Routinen auf (`0134h`, `03DBh`, `02E8h`, `08F0h`, `18FCh`). Die symbolischen Namen und die vollständige Initialisierungssemantik sind noch offen.

### 5. Gesicherte Schlussfolgerungen

- Der erste Far Call ist ein Bootstrap-/Kopierschritt und keine bereits identifizierte Kernel-API.
- Der Code kopiert `0x1CE0` Bytes in ein berechnetes Segment.
- Der Rückgabewert stellt das Segmentwort des zweiten Far Calls dynamisch auf das kopierte Segment um.
- Die Unterschiede `0F93h`/`0F90h` und `0E34h`/`0E35h` sind versionsabhängige Startwerte.
- Daraus folgt noch keine Identifikation der `LOCAL.GEO`-Aufrufe `0000:0093` und `0000:0006`.

### 6. Nächster Schritt

Den kopierten Block mit dem übrigen Kernel-Ladebild vergleichen, den Datenbereich `DS=0E34h`/`0E35h` kartieren und die internen Routinen am zweiten Einstieg weiter verfolgen.

**Auswirkung auf GeoView Plus:** Keine Codeänderung und keine neue Zeichenzuordnung. `0xCE`, `0xCF`, `0xD0` und `0xD1` bleiben ungeklärt.