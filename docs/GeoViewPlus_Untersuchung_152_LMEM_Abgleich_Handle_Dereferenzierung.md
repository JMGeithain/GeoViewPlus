# Untersuchung 152 – Abgleich der GeoWorks-LMem-Abbildung mit BOUNCE.GEO

**Projekt:** GeoViewPlus – GeoWorks / PC/GEOS 1.x  
**Datum:** 10.11.2026  
**Primärquelle:** *PC/GEOS System Software Overview*, Draft 10 November 1990, S. 38–40  
**Binärdateien:** `BOUNCE.GEO` und `BCOLTEST.GEO` aus `Basebox-SVGA-Ensemble12(2).zip`

## 1. Ziel

Die Untersuchung vergleicht die schematische Darstellung des Local Memory Blocks aus der zeitgenössischen GeoWorks-Dokumentation mit den tatsächlich gespeicherten Ressourcen 3–10. Ziel ist ausdrücklich nicht, eine nicht belegte Struktur passend zu machen, sondern Widersprüche zu erkennen.

## 2. Aussagen der Primärquelle

Die GeoWorks-Dokumentation beschreibt:
- `LMemInitHeap` initialisiert einen lokalen Heap an einem angegebenen Offset innerhalb eines zuvor angelegten und gesperrten Blocks.
- Der Heap reicht vom Initialisierungsoffset bis zum Ende des Blocks.
- Am Anfang des Blocks liegt eine Struktur `LMemBlockHeader`.
- Figure 8 bezeichnet den Header mit 16 Bytes und die LMem-Handle-Tabelle mit 16 WORDs.
- `LMemAlloc` gibt einen Chunk-Handle zurück.
- Der Chunk-Handle wird als Offset in den Block verwendet, an dem der tatsächliche Chunk-Datenoffset gespeichert ist.
- Der Chunk-Handle ist somit nicht einfach der Datenoffset selbst.
- Die Dokumentation beschreibt außerdem, dass der tatsächliche Datenoffset nach LMem-Aufrufen nicht dauerhaft stabil sein muss.

Quelle: https://www.lyonlabs.org/commodore/onrequest/geos/PC-GEOS-System-Software-Overview.pdf  
Fundstellen: gedruckte Seiten 38–40; PDF-Textauszug insbesondere Seiten-/Zeilenbereich um 7382–7415 (Header und Figure 8), 7431–7508 (Chunk-Handle-Prinzip) und 7537–7615 (Object Descriptor).

## 3. Tatsächliche ersten 48 Bytes der BOUNCE-Ressourcen

Alle Werte sind Rohbytes relativ zum Anfang der jeweiligen Ressource. Die Zeilen sind jeweils 16 Bytes lang.

### Ressource 3, 384 Bytes

```text
+00  03 00 20 00 00 E0 02 00 78 01 0E 00 00 00 00 00
+10  00 00 00 00 80 01 00 00 00 00 00 00 00 00 00 00
+20  3E 00 FF FF 4E 00 72 00 82 00 8E 00 B6 00 C6 00
```

### Ressource 4, 336 Bytes

```text
+00  04 00 20 00 00 E0 02 00 44 01 06 00 00 00 00 00
+10  00 00 00 00 50 01 00 00 00 00 00 00 00 00 00 00
+20  2E 00 36 00 FE 00 2A 01 36 01 00 00 08 00 00 03
```

### Ressource 5, 160 Bytes

```text
+00  05 00 20 00 00 C0 02 00 94 00 02 00 00 00 00 00
+10  00 00 00 00 A0 00 00 00 00 00 00 00 00 00 00 00
+20  26 00 2A 00 04 00 00 02 6A 00 61 30 00 0E 00 1A
```

### Ressourcen 6–10

Die ersten 48 Bytes haben dieselbe allgemeine Anordnung. Insbesondere steht bei allen Ressourcen 5–10 bei `+0x20` die Folge `26 00 2A 00`. Die vollständigen Rohdaten und Prüfsummen der Ressourcen 5–10 wurden bereits in Untersuchung 150 dokumentiert.

## 4. Wichtiger Gegencheck: Handle-Dereferenzierung

Die Primärquelle erklärt das Handle-Prinzip mit einer Dereferenzierung: Der Chunk-Handle dient als Offset auf ein WORD, das den tatsächlichen Chunk-Datenoffset enthält. In der Beispielbeschreibung wird dies als `mov di, ds:[si]` dargestellt.

Wir prüfen deshalb rein hypothetisch, was geschähe, wenn die beiden WORD-Werte `0x0026` und `0x002A` aus Ressourcen 5–10 solche Chunk-Handles wären.

Bei Ressource 5:
- Handle-Kandidat `0x0026`: WORD an Ressourcenoffset `0x26` ist `0x0200` (512).
- Handle-Kandidat `0x002A`: WORD an Ressourcenoffset `0x2A` ist `0x3061` (Little-Endian aus Bytes `61 30`).

Die Ressource ist jedoch nur 160 Bytes groß. Beide dereferenzierten Werte liegen außerhalb der Ressource.

Bei Ressource 6:
- WORD an `0x26` ist ebenfalls `0x0200` (512).
- WORD an `0x2A` ist `0x4061` (Little-Endian aus Bytes `61 40`).
- Die Ressource ist nur 96 Bytes groß.

Auch hier liegen beide Werte außerhalb der Ressource.

Daher gilt: **Unter der Annahme, dass der Anfang der Ressource zugleich der Anfang des LMem-Blocks ist und die Tabellen-WORDs direkt Chunk-Handles dieses Blocks sind, passen die Werte nicht zum in der GeoWorks-Dokumentation beschriebenen Handle-Dereferenzierungsmodell.**

Diese Annahmen sind nicht abschließend bewiesen. Ein abweichender Heap-Startoffset oder eine andere Bedeutung der Tabelle könnte den Vergleich verändern. Der Befund reicht jedoch aus, um die bisherige Vermutung „0x0026 und 0x002A sind Chunk-Handles“ nicht weiter als Arbeitshypothese zu bevorzugen.

## 5. Was sich daraus ableiten lässt

**Gesichert:**
1. GeoWorks beschreibt einen 16-Byte-LMem-Header und eine Handle-Tabelle mit 16 WORDs in Figure 8.
2. GeoWorks unterscheidet ausdrücklich Chunk-Handle und tatsächlichen Chunk-Datenoffset.
3. Die BOUNCE-Ressourcen zeigen ab `+0x20` Tabellenwerte, deren Bedeutung noch nicht geklärt ist.
4. Die einfache Interpretation der Werte `0x0026` und `0x002A` als Chunk-Handles, relativ zum Ressourcenanfang, führt in kleinen Ressourcen zu Offsets außerhalb der Ressourcengrenzen.

**Nicht bewiesen:**
- dass der Heap bei Offset 0 der GEO-Ressource beginnt;
- dass die Struktur ab Offset 0 in diesen Ressourcen unmittelbar der im Dokument gezeigte LMem-Block ist;
- dass die WORD-Tabelle ab `+0x20` überhaupt die LMem-Handle-Tabelle ist;
- die Bedeutung der Kopfwerte `E000` und `C000`;
- dass die Ressourcen 5–10 Icons oder Moniker enthalten.

## 6. Korrektur der Arbeitsrichtung

Die Werte `0x0026` und `0x002A` werden ab jetzt neutral als **Tabellenwerte / Offset-Kandidaten** bezeichnet. Die Bezeichnung „Chunk-Handle“ wird erst verwendet, wenn ein gültiger Dereferenzierungspfad nachgewiesen ist.

Die frühere pauschale Bezeichnung des gesamten Bereichs `+0x00 bis +0x1F` als 32-Byte-LMem-Header bleibt zurückgenommen. Die Quelle nennt einen 16-Byte-Header, aber der konkrete Aufbau der GEO-Ressourcen muss separat bestimmt werden.

## 7. Nächster Schritt – Untersuchung 153

Als nächstes ist der Heap-Startoffset zu bestimmen. Dazu müssen wir:
1. Die LMem-Initialisierung bzw. das gespeicherte Layout der Objektressourcen für diese 1.x-Geodes genauer bestimmen.
2. Die 16-Byte-Headerfelder anhand einer versionsspezifischen Definition identifizieren.
3. Den möglichen Anfang der Handle-Tabelle lokalisieren.
4. Prüfen, ob sich Handles durch Dereferenzierung auf innerhalb der Ressource liegende Datenbereiche auflösen lassen.
5. Erst dann Chunk- oder Moniker-Typen untersuchen.

## 8. Datenintegrität

Beide GEO-Dateien und das ZIP-Archiv wurden ausschließlich gelesen. Keine Quellcodedatei und keine Originalressource wurde verändert. GeoViewPlus erhielt keine Resolver-Codeänderung.
