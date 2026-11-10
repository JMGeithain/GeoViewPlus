# Untersuchung 153 – LMEM-Handle- und Offset-Analyse der Ressourcen 5–10

**Projekt:** GeoViewPlus – Untersuchung echter PC/GEOS-Icons  
**Gegenstand:** `BOUNCE.GEO` und `BCOLTEST.GEO` aus Basebox-SVGA-Ensemble12(2).zip  
**Geltungsbereich:** Bytebefunde an den vorliegenden Dateien; keine Übertragung von PC/GEOS 2.x-/FreeGEOS-Strukturen auf GeoWorks 1.x.

## 1. Ziel

Die in Untersuchung 152 offen gebliebene Frage war, ob die zwei WORDs ab Ressourcenoffset `+20h` gewöhnliche LMem-Chunk-Handles sind und wie sich ihre Zieladressen erklären lassen. Dafür wurden die Ressourcen 5 bis 10 erneut direkt aus beiden GEO-Dateien gelesen.

## 2. Reproduzierbare Rohbefunde

In allen Ressourcen 5–10 beider Dateien stehen bei `+20h` dieselben zwei WORDs:

```text
Offset +20h: 26 00  2A 00
WORD-Werte:  0026h  002Ah
```

Die Ressourcen 5–10 sind zwischen `BOUNCE.GEO` und `BCOLTEST.GEO` byteidentisch. Ihre Größen betragen 160, 96, 256, 624, 144 und 224 Bytes.

Für jede dieser Ressourcen gilt:
- Offset `+26h` enthält die Bytes `2A 00`, also den WORD-Wert `002Ah`.
- Offset `+2Ah` beginnt der nachfolgende Datenbereich. Die dortigen ersten Bytes lauten je nach Ressource beispielsweise:
  - R5: `00 02 6A 00 61 30 ...`
  - R6: `00 02 35 00 61 40 ...`
  - R7: `00 02 CC 00 41 30 ...`
  - R8: `00 02 45 02 46 30 ...`
  - R9: `00 02 61 00 41 40 ...`
  - R10: `00 02 B1 00 46 40 ...`

Damit zeigt der Tabellenwert `0026h` auf das zweite Tabellen-WORD. Der Wert dieses WORDs ist `002Ah`, das auf den anschließenden Datenbereich zeigt.

## 3. Abgleich mit der LMem-Semantik

Die GeoWorks-Systemsoftwarebeschreibung von 10. November 1990 beschreibt LMem-Chunk-Handles als Offsets innerhalb des Blocks auf die Stelle, an der der tatsächliche Chunk-Offset gespeichert ist. Der gespeicherte Offset wird dereferenziert; der daraus resultierende Datenoffset ist nicht dauerhaft stabil. Diese Beschreibung ist in der Quelle im Abschnitt zu `LMemAlloc` und Chunk-Handles erläutert.

Quelle: *PC/GEOS System Software Overview*, Draft 10 November 1990, Abschnitte zu LMem und Chunk Handles, insbesondere die Erläuterung von Handle und tatsächlichem Offset.  
https://www.lyonlabs.org/commodore/onrequest/geos/PC-GEOS-System-Software-Overview.pdf

Der Befund `+26h → WORD 002Ah` ist mit genau einem solchen Dereferenzierungsschritt vereinbar: Ein Handle-artiger Wert `0026h` führt zu einem gespeicherten Offset `002Ah`.

Allerdings löst das die zweite Tabellenposition nicht. Wenn `002Ah` ebenfalls als Handle interpretiert wird, läge dessen gespeicherter WORD direkt bei `+2Ah` und hätte den Wert `0200h`. Dieser Wert liegt außerhalb der jeweiligen Ressourcengröße. Eine einfache Interpretation beider Tabellen-WORDs als zwei normale LMem-Chunk-Handles ist deshalb mit den vorliegenden Bytes nicht schlüssig.

## 4. Was daraus folgt – und was nicht

**Gesichert:**
1. Die WORD-Folge `0026h, 002Ah` ist in R5–R10 beider GEO-Dateien identisch.
2. `0026h` adressiert innerhalb der Ressource das zweite Tabellen-WORD.
3. Dieses zweite WORD enthält `002Ah`.
4. Bei `+2Ah` beginnt ein Datenbereich.
5. Eine naive Dereferenzierung beider Werte als zwei unabhängige LMem-Handles führt beim zweiten Wert zu `0200h`, also außerhalb der Ressource.

**Nicht gesichert:**
- Dass die Tabelle ab `+20h` tatsächlich die vollständige LMem-Handle-Tabelle ist.
- Dass `002Ah` ein zweites gültiges LMem-Handle ist.
- Dass der Datenbereich ab `+2Ah` bereits der Anfang eines vollständigen Monikers oder Icons ist.
- Die genaue Bedeutung der Felder im vorangestellten Bereich.

Die Beobachtung spricht für eine verkettete oder gestufte Offsetstruktur, beweist aber noch keine konkrete Datenstruktur. Insbesondere darf aus der Übereinstimmung eines einzelnen Dereferenzierungsschritts keine vollständige LMem-Interpretation abgeleitet werden.

## 5. Konsequenz für GeoViewPlus

Noch keine Änderung am Resolver und keine Änderung an der Heuristik. Die aktuelle Implementierung darf diese Werte nicht als bestätigte Chunk-Handles behandeln.

Der nächste notwendige Schritt ist, die Ressource als Ganzes gegen eine unabhängig identifizierte LMem-Heap-Grenze und die tatsächliche Chunk-Verwaltung zu prüfen. Dazu müssen insbesondere die 16-Byte-LMem-Block-Header-Angaben aus der GeoWorks-Dokumentation von den zusätzlichen Bytes vor dem Bereich ab `+20h` getrennt werden. Die bloße Lage der Tabelle bei `+20h` reicht dafür nicht.

## 6. Integrität und Änderungen

- Untersucht wurden nur lesende Bytezugriffe auf die beiden GEO-Dateien im ZIP-Archiv.
- Keine Originaldatei wurde verändert.
- Kein GeoViewPlus-Programmcode wurde geändert.
- Diese Untersuchung dokumentiert einen Bytebefund und eine eingeschränkte Interpretation, keinen abgeschlossenen LMEM-Parser.
