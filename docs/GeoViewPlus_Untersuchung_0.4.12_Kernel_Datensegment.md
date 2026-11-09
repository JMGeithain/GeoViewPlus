# GeoView Plus – Untersuchung 0.4.12
## Kernel-Datensegment 0E34h/0E35h und gespeicherte Segmentwerte

**Gegenstand:** PC/GEOS 1.x, `KERNEL.EXE` und `KERNEL.OLD` aus `GEOWORKS.zip`. Originaldateien unverändert.

### 1. Segmentabbildung

Mit MZ-Headergröße `0x600` gilt: `Dateioffset = 0x600 + Segment * 16 + Offset`.

- Gepatchter Kernel: Segment `0E34h` beginnt bei Dateioffset `0xE940`.
- Originalkernel: Segment `0E35h` beginnt bei Dateioffset `0xE950`.

### 2. Relevante Zugriffe

Der Code bei `0F93:0000` setzt `DS=0E34h`, speichert `SS` nach `DS:0040h`, `SP` nach `DS:0042h` und setzt `DS:0046h` auf null. Der Code bei `0F93:01C7` setzt erneut `DS=0E34h`, speichert den zuvor aktiven DS-Wert bei `DS:0044h` und speichert `CS` bei `DS:05BAh`. Im `KERNEL.OLD` sind die entsprechenden Segmente `0E35h` und `0F90h`.

### 3. Rohdatenbefund

Im statischen Dateibild sind die Felder `DS:0040h`, `DS:0042h` und `DS:0044h` zunächst null; `DS:0046h` ist null. `DS:05BAh` enthält initial `0F93h` im gepatchten Kernel und `0F90h` im Originalkernel. Die Routine überschreibt dieses Feld zur Laufzeit mit dem aktuellen `CS` des kopierten Segments.

### 4. Gesicherte Schlussfolgerungen

- `0E34h`/`0E35h` ist ein vom Bootstrap-Code direkt verwendeter Datenbereich.
- `SS`, `SP` und der zuvor aktive `DS` werden dort abgelegt.
- `DS:05BAh` enthält im Dateiabbild den ursprünglichen Bootstrap-Segmentwert und wird zur Laufzeit mit dem aktuellen `CS` aktualisiert.
- Das passt zum nachgewiesenen Kopiervorgang in ein dynamisch berechnetes Segment.

### 5. Grenzen und nächster Schritt

Die vollständige Datenstruktur und die symbolischen Bedeutungen weiterer Felder bleiben offen. Dies identifiziert nicht die `LOCAL.GEO`-Aufrufe `0000:0093`/`0000:0006` und liefert keine neue Zeichenzuordnung für `0xCE`, `0xCF`, `0xD0`, `0xD1`. Als Nächstes werden alle Zugriffe auf `DS:0040h`, `0042h`, `0044h`, `0046h` und `05BAh` im kopierten Segment verfolgt.

**Auswirkung auf GeoView Plus:** Keine Codeänderung und keine neue Zeichenzuordnung.