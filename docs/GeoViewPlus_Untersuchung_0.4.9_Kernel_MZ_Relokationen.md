# GeoView Plus – Untersuchung 0.4.9
## MZ-Einstiegspunkt und Relokationstabellen der beiden Kerneldateien

**Gegenstand:** PC/GEOS 1.x, `GEOWORKS/KERNEL.EXE` und `GEOWORKS/KERNEL.OLD` aus dem vorhandenen `GEOWORKS.zip`.  
**Methode:** MZ-Header und Relokationseinträge direkt aus den Originalbytes gelesen. Keine Datei verändert.

### 1. Verifizierte Einstiegspunkte

Beide Dateien haben:
- `e_cparhdr = 0x0060`, also 96 Paragraphen bzw. 0x600 Byte MZ-Header
- `e_cs = 0x0000`
- `e_ip = 0x02B1`

Der im MZ-Header angegebene Startpunkt ist damit in beiden Dateien relativ zum geladenen MZ-Modul `0000:02B1`. Der entsprechende Dateioffset liegt bei `0x600 + 0x2B1 = 0x8B1`.

Das ist der DOS-MZ-Einstiegspunkt. Daraus folgt noch nicht, dass die im `LOCAL.GEO` verwendeten Segment:Offset-Adressen `0000:0093` oder `0000:0006` auf diesen MZ-Einstiegspunkt oder auf direkte Kernel-API-Funktionen zeigen.

### 2. Stackwerte

| MZ-Feld | KERNEL.EXE | KERNEL.OLD |
|---|---:|---:|
| `e_ss` | `0x0E34` | `0x0E35` |
| `e_sp` | `0x15F0` | `0x15B0` |

Die initialen Stackwerte unterscheiden sich. Das ist ein weiterer Beleg dafür, dass die Dateien nicht einfach byteidentische Kernelvarianten sind.

### 3. Relokationstabellen

| Merkmal | KERNEL.EXE | KERNEL.OLD |
|---|---:|---:|
| Relokationseinträge (`e_crlc`) | 276 | 273 |
| Relokationstabellen-Offset (`e_lfarlc`) | `0x003C` | `0x003C` |
| Erste Einträge | `0000:0162`, `0000:0166`, `0000:02B4`, `0000:02C8` | identisch |
| Letzter Eintrag | `0F93:1CC6` | `0F90:1CC6` |

Die Relokationseinträge sind MZ-Paare aus Offset und Segment. Beim Laden addiert der DOS-Loader die Ladebasis zu den an diesen Positionen gespeicherten Segmentwerten.

Beim Vergleich der vollständigen Eintragslisten:
- 5 Einträge stimmen als identische Offset-/Segmentpaare überein.
- 271 Einträge kommen nur in `KERNEL.EXE` vor.
- 268 Einträge kommen nur in `KERNEL.OLD` vor.

Die Reihenfolge und die Werte der Einträge unterscheiden sich also deutlich. Das ist mit einer bloßen kleinen Änderung am Dateiende nicht vereinbar; die geladenen Kernelbilder unterscheiden sich wesentlich.

### 4. Was daraus folgt – und was nicht

**Gesichert:**
- Beide Kernel haben denselben MZ-Einstiegspunkt `0000:02B1`.
- Beide haben denselben MZ-Headerumfang von 0x600 Byte.
- Stackinitialisierung und Relokationstabellen unterscheiden sich.
- Die Kerneldateien sind nicht identisch.

**Nicht gesichert:**
- Die semantische Bedeutung der `LOCAL.GEO`-Aufrufe `0000:0093` und `0000:0006`.
- Dass diese Adressen direkt als MZ-Moduloffsets interpretiert werden dürfen.
- Dass die Quote-Werte aus `GEOS.INI` zur Dateinamendecodierung verwendet werden.

### 5. Konsequenz für die weitere Analyse

Die MZ-Analyse allein reicht nicht aus, um die GEOS-interne Segmentverwaltung oder die Kernel-API zu rekonstruieren. Der nächste Schritt muss die GEOS-spezifische Lade- und Segmentinitialisierung am DOS-MZ-Einstiegspunkt `0000:02B1` untersuchen.

Erst wenn klar ist, wie GEOS den Kernel nach dem DOS-Start umorganisiert und welche Segmente danach gültig sind, können die Far-Call-Ziele aus `LOCAL.GEO` korrekt aufgelöst werden.

### 6. Status der Zeichensatzuntersuchung

Es erfolgt weiterhin keine Änderung an der Zeichentabelle von GeoView Plus. Die Bytes `0xCE`, `0xCF`, `0xD0` und `0xD1` bleiben ungeklärt. Die `quotes`-Konfiguration bleibt ein separater Lokalisierungsbefund, bis ein tatsächlicher Datenfluss zu Dateinamen nachgewiesen ist.
