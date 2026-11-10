# GeoView Plus – Untersuchung 0.4.20
## Segmentkontext der vermeintlichen Feldschreiber 0609h und 0613h

**Geltungsbereich:** ausschließlich PC/GEOS 1.x / deutsche GeoWorks-1.2-Kerneldateien.  
**Quellen:** `GEOWORKS.zip`, darin `GEOWORKS/KERNEL.EXE` (72.736 Bytes) und `GEOWORKS/KERNEL.OLD` (72.688 Bytes).  
**Methode:** MZ-Ladebild ab Dateioffset `0600h` extrahiert und mit `objdump -D -b binary -m i8086 -Mintel` statisch disassembliert. Alle genannten Adressen sind Ladebildoffsets; Dateioffset = `0600h + Ladebildoffset`. Keine Laufzeittests, keine Änderungen an Originaldateien.

## 1. Korrektur zu Untersuchung 0.4.19

Der dortige Befund, `10BD5h` schreibe das Kernel-Datenfeld `DS:[0613h]`, ist **nicht haltbar**. Im Codepfad steht unmittelbar davor:

```asm
10BC4  push cs
10BC5  pop  ds
...
10BD5  mov  [0613h], bx
```

Damit ist DS an dieser Stelle ausdrücklich gleich CS. Der Schreibzugriff geht also nach `CS:0613h`, nicht in das Kernel-Datensegment `0E34h:0613h`. Der Befund ist aus der Liste der nachgewiesenen Kernel-Datensegment-Schreibstellen zu streichen.

## 2. Vergleich mit KERNEL.OLD: gleicher Segmentkontext

Im entsprechenden älteren Codepfad findet sich:

```asm
10B94  push cs
10B95  pop  ds
10BA5  mov  [0609h], bx
```

Auch hier ist DS zuvor auf CS gesetzt. Der Schreibzugriff bei `10BA5h` ist daher `CS:0609h`, nicht `0E35h:0609h`.

Der Vergleich zeigt eine strukturelle Verwandtschaft des DOS-Treiber-Setup-Pfades, aber keine direkte Schreibbestätigung für das Kernel-Datenfeld `DS:[0609h]`.

## 3. Aufrufkontext des neueren Pfades

Der neuere Pfad wird unter anderem bei `110E1h` mit einem Far-Call auf `0000:10BCh` aufgerufen. Innerhalb des Pfades wird bei `10B83h` das Segment `0E34h` zunächst nach DS geladen. Vor dem eigentlichen Tabellen-/Treiber-Aufruf bei `10BC6h` wird DS dann ausdrücklich durch CS ersetzt. Das erklärt, warum die anschließende absolute Speicherstelle `0613h` nicht dem zuvor verwendeten Kernel-Datensegment zugeordnet werden darf.

## 4. Feld 060Fh bei FFFAh – noch nicht abschließend zugeordnet

Die Bytes bei `FFFAh` disassemblieren als `mov [060Fh],bx`. Der umgebende Bereich enthält davor und danach tatsächlich ausführbaren Code; zugleich liegen in der Nähe eingebettete Dateinamensstrings. Die Instruktion ist deshalb nicht allein aufgrund des linearen Disassemblats als Kernel-Datenfeldschreiber klassifiziert.

Der konkrete DS-Wert am Eintritt in diesen Pfad und über die Aufrufe `0189h`, `01E4h`, `017Bh` sowie den Fehlerpfad `0000:0399` ist noch nicht vollständig nachgewiesen. Bis diese Register-/Segmentherkunft geklärt ist, bleibt `FFFAh` ein **möglicher**, aber nicht bestätigter Schreiber von `0E34h:060Fh`.

## 5. Gesicherte und offene Aussagen

| Adresse | Instruktion | Segmentaussage | Status |
|---|---|---|---|
| `10BD5h` in KERNEL.EXE | `mov [0613h],bx` | DS = CS | Kein Kernel-Datensegment-Schreiber |
| `10BA5h` in KERNEL.OLD | `mov [0609h],bx` | DS = CS | Kein Kernel-Datensegment-Schreiber |
| `FFFAh` in KERNEL.EXE | `mov [060Fh],bx` | DS beim Schreiben noch nicht bewiesen | Offen |
| `2590h–259Bh` in KERNEL.EXE | liest `060Fh`, `0609h`, `0611h`, `0613h` | Statusroutine liest nach Segmentauflösung aus Kernel-Datensegment | Lesebefund bleibt bestehen |
| `259Ah–25A5h` in KERNEL.OLD | liest `0605h`, `05FFh`, `0607h`, `0609h` | Statusroutine der alten Kernelversion | Lesebefund bleibt bestehen |

## 6. Konsequenz für die weitere Analyse

Die Feldliste aus 0.4.19 darf nicht als Liste bestätigter Schreiber verwendet werden. Insbesondere sind `10BD5h` und `10BA5h` wegen `DS=CS` keine Schreiber der jeweiligen Kernel-Datensegmentfelder. Als nächster Schritt ist der Eintrittspfad der Routine um `FFFAh` zu verfolgen und DS über sämtliche Pfade bis zur Instruktion zu protokollieren. Erst danach lässt sich entscheiden, ob `060Fh` im Kernel-Datensegment tatsächlich beschrieben wird.

**Integrität:** Die Originaldateien aus `GEOWORKS.zip` wurden nur gelesen und für die Disassemblierung temporär extrahiert. Keine Binärdatei wurde gepatcht.
