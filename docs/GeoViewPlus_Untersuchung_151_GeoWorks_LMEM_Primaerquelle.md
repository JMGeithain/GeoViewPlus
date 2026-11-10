# Untersuchung 151 – Zeitgenössische GeoWorks-Dokumentation zur Local Memory-Verwaltung

**Projekt:** GeoViewPlus – strikt GeoWorks / PC/GEOS 1.x  
**Datum:** 10.11.2026  
**Anlass:** Unabhängige Prüfung der bisherigen Interpretation der LMEM-Ressourcen in BOUNCE.GEO und BCOLTEST.GEO.

## 1. Neue Primärquelle

Gefunden wurde das Dokument:

**PC/GEOS System Software Overview**, Draft Version, 10 November 1990, © 1990 GeoWorks.

PDF:
https://www.lyonlabs.org/commodore/onrequest/geos/PC-GEOS-System-Software-Overview.pdf

Für diese Untersuchung ist das Dokument besonders relevant, weil es zeitgenössisch zur frühen PC/GEOS-Entwicklung ist und den Local Memory Manager ausdrücklich beschreibt. Es ist kein FreeGEOS-/PC/GEOS-2.x-Dokument.

Die relevanten Abschnitte stehen im PDF auf den gedruckten Seiten 38–40 (PDF-Seiten entsprechend dem Dokument prüfen).

## 2. Was GeoWorks über Local Memory beschreibt

Der Abschnitt „Using Blocks“ beschreibt folgende Abläufe:

1. Eine Anwendung legt zunächst einen Speicherblock an und sperrt ihn.
2. Mit `LMemInitHeap` wird an einem bestimmten Offset innerhalb dieses Blocks ein Local-Memory-Heap initialisiert.
3. Der Heap reicht vom angegebenen Offset bis zum Ende des Blocks.
4. Am Anfang des Blocks befindet sich die Struktur `LMemBlockHeader`.
5. Anschließend können Chunks im Local-Memory-Heap angelegt, vergrößert und freigegeben werden.
6. `LMemAlloc` liefert einen Chunk-Handle.
7. Dieser Chunk-Handle wird als Offset in den Block verwendet, an dem der tatsächliche Offset des Chunks gespeichert ist.
8. Der tatsächliche Chunk-Datenoffset ist nur bis zum nächsten Aufruf einer LMem-Routine als stabil anzusehen. Daher muss der Handle gespeichert werden, nicht der einmal dereferenzierte Offset.

Die Darstellung „Figure 8. A Local Memory Block“ nennt außerdem eine LMem-Handle-Tabelle mit 16 WORDs und einen `LMem Block Header` von 16 Bytes.

## 3. Korrektur der bisherigen GeoViewPlus-Terminologie

In den Untersuchungen 139–150 wurde der Bereich `+0x00 bis +0x1F` teilweise pauschal als „32-Byte-LMEM-Kopf“ bezeichnet.

Diese Bezeichnung ist nicht hinreichend belegt und wird hiermit zurückgenommen.

Die zeitgenössische GeoWorks-Dokumentation unterscheidet ausdrücklich:
- einen `LMemBlockHeader` von 16 Bytes;
- eine LMem-Handle-Tabelle mit 16 WORDs.

Daraus folgt **nicht automatisch**, dass die 32 Bytes in unseren GEO-Ressourcen genau diese beiden Bereiche in einer bestimmten Reihenfolge darstellen. Die schematische Abbildung muss zusammen mit dem tatsächlichen Ressourcenlayout interpretiert werden. Die exakten Feldpositionen, die Reihenfolge von Header und Handle-Tabelle und die Bedeutung der konkreten WORD-Werte in BOUNCE.GEO bleiben offen.

Die bisherigen Rohbyte-Befunde (Ressourcengrößen, Bytes und WORDs an den protokollierten Offsets) werden dadurch nicht ungültig. Korrigiert wird die semantische Bezeichnung des Bereichs.

## 4. Konsequenz für die bisherigen Offset-Hypothesen

Die bisherigen Tabellen ab Ressourcenoffset `+0x20` dürfen nicht ohne Weiteres als „Chunk-Tabelle“ bezeichnet werden.

Die zeitgenössische Dokumentation erklärt das grundlegende Handle-Prinzip: Ein Chunk-Handle verweist auf einen Speicherplatz, der den tatsächlichen Chunk-Offset enthält. Daraus folgt, dass ein Tabellen-WORD nicht zwangsläufig direkt der Offset des Chunk-Inhalts sein muss.

Für die Werte `0x0026` und `0x002A` aus Ressourcen 5–10 ist daher weiterhin offen, ob sie:
- Chunk-Handles,
- Einträge einer Handle-Tabelle,
- andere Verwaltungswerte,
- oder eine anders strukturierte Ressourcentabelle darstellen.

Die Abstände und Bytes wurden in früheren Untersuchungen protokolliert; eine semantische Klassifizierung wird hier ausdrücklich nicht vorgenommen.

## 5. Gesicherte und offene Aussagen

### Gesichert durch die GeoWorks-Quelle

- `LMemInitHeap` initialisiert einen Local-Memory-Heap in einem Speicherblock.
- Der Heap reicht vom Initialisierungsoffset bis zum Ende des Blocks.
- Die Struktur heißt `LMemBlockHeader` und wird mit 16 Bytes angegeben.
- Die Abbildung zeigt eine LMem-Handle-Tabelle mit 16 WORDs.
- Chunk-Handles sind von den tatsächlichen Chunk-Datenoffsets zu unterscheiden.
- Chunk-Datenoffsets können nach LMem-Aufrufen ungültig werden.

### Noch nicht geklärt

- Exakte Felddefinition und Feldreihenfolge des 16-Byte-Headers für die konkrete GeoWorks-1.x-Version.
- Exakte Lage und Größe der Handle-Tabelle im gespeicherten GEO-Ressourcenformat.
- Ob die Tabellen bei `+0x20` in BOUNCE.GEO tatsächlich Handle-Tabellen sind.
- Bedeutung der Kopfwerte `E000` und `C000`.
- Ob und wie die referenzierten Objekte Moniker oder Bitmapdaten enthalten.

## 6. Auswirkungen auf GeoViewPlus

Der spätere Resolver darf Chunk-Handles nicht wie direkte Datenoffsets behandeln. Er muss zunächst die Blockstruktur und Handle-Tabelle validieren und anschließend den im Handle-Eintrag gespeicherten tatsächlichen Chunk-Offset lesen.

Eine Implementierung wird erst begonnen, wenn die konkrete Layoutvariante für die untersuchten GeoWorks-1.x-Ressourcen durch weitere unabhängige Befunde abgesichert ist.

## 7. Nächster Schritt – Untersuchung 152

Als Nächstes wird die schematische GeoWorks-Abbildung mit den realen Ressourcen verglichen. Dabei werden insbesondere geprüft:

1. Wo im Ressourcenspeicher der 16-Byte-`LMemBlockHeader` liegen kann.
2. Ob ein 16-WORD-Handle-Tabellenbereich in den Ressourcen nachweisbar ist.
3. Ob die Werte an `+0x20` in Ressourcen 3–10 mit dieser Darstellung vereinbar sind.
4. Ob die tatsächlichen Chunk-Datenoffsets über die Handle-Einträge aufgelöst werden können.

Die Abbildung ist ein konzeptioneller Beleg für die damalige LMem-Architektur, aber kein Ersatz für die versionsgenaue Strukturdefinition.

## 8. Versionsgrenze und Datenintegrität

Die verwendete GeoWorks-Quelle stammt aus dem Jahr 1990 und beschreibt die damalige PC/GEOS-Architektur. FreeGEOS-/PC/GEOS-2.x-Dokumentation wurde nicht als Beleg für die hier untersuchten 1.x-Dateien verwendet.

Die GEO-Dateien und das ZIP-Archiv wurden nicht verändert. Es wurden keine Resolver- oder Programmcodeänderungen vorgenommen.
