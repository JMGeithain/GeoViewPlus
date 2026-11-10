# Untersuchung 149 – Relokationen und Ressourcenverweise in BOUNCE.GEO und BCOLTEST.GEO

**Projekt:** GeoViewPlus – strikt GeoWorks / PC/GEOS 1.x  
**Datum:** 10.11.2026  
**Untersuchungsbasis:** `Basebox-SVGA-Ensemble12(2).zip`  
**Ziel:** Prüfen, ob die in Untersuchung 148 festgestellte Byteidentität der Ressourcen 5–10 durch die GEOS-Relokationstabellen als Ressourcenverknüpfung erklärt wird.

## 1. Eingabedateien und Integrität

| Datei | Größe | SHA-256 |
|---|---:|---|
| `BOUNCE.GEO` | 3.572 Byte | `698aa8a78568bccbea7b81709a9777e4bc34cdff0de03418f8f9f5789bf83393` |
| `BCOLTEST.GEO` | 4.000 Byte | `3e5d7a9cdb0ed5d506e5b79056b3f274a04e97b9b07845fd1c8d4fe99295dcac` |

Beide Dateien wurden ausschließlich gelesen. Das ZIP-Archiv und die darin enthaltenen GEO-Dateien wurden nicht verändert.

## 2. Parser und Prüfgrenzen

Verwendet wurde das im Archiv enthaltene Skript `source/pm-backport/native-binary/inspect_geodes.py`. Es erkennt für beide Dateien das Format GEOS 1.x, liest Ressourcen-, Import- und Exporttabellen sowie die Relokationstabellen und meldet für beide Dateien keine Validierungsfehler.

Die Untersuchung stützt sich auf die vom Parser gelesenen Tabellen und einen separaten Bytevergleich der jeweiligen Ressourcendaten. Die Interpretation der Relokationseinträge wird auf die tatsächlich dekodierten Felder beschränkt. Daraus werden keine Aussagen über nicht untersuchte LMEM- oder Moniker-Innenstrukturen abgeleitet.

## 3. Ressourcenvergleich

| Ressource | BOUNCE.GEO | BCOLTEST.GEO | Bytevergleich |
|---:|---:|---:|---|
| 0 | 0 Byte | 0 Byte | identisch (leer) |
| 1 | 240 Byte | 768 Byte | unterschiedlich |
| 2 | 512 Byte | 432 Byte | unterschiedlich |
| 3 | 384 Byte | 400 Byte | unterschiedlich |
| 4 | 336 Byte | 336 Byte | unterschiedlich |
| 5 | 160 Byte | 160 Byte | vollständig identisch |
| 6 | 96 Byte | 96 Byte | vollständig identisch |
| 7 | 256 Byte | 256 Byte | vollständig identisch |
| 8 | 624 Byte | 624 Byte | vollständig identisch |
| 9 | 144 Byte | 144 Byte | vollständig identisch |
| 10 | 224 Byte | 224 Byte | vollständig identisch |

Für Ressourcen 5–10 wurden jeweils die vollständigen Ressourcendaten zwischen den durch die Ressourcentabellen angegebenen Startpositionen und Größen verglichen. Alle sechs Vergleiche ergaben Gleichheit. Für Ressourcen 3 und 4 ergab der Bytevergleich trotz gleicher Größe von Ressource 4 keine Gleichheit.

### SHA-256 der einzelnen Ressourcen 5–10

| Ressource | SHA-256 (beide Dateien identisch) |
|---:|---|
| 5 | `07111ffb4b1992ab` (Präfix) |
| 6 | `d076dfa6975956e2` (Präfix) |
| 7 | `2d9417547aa3a4bd` (Präfix) |
| 8 | `b0f61f6fc3892ff2` (Präfix) |
| 9 | `e2f44b6027fda5c6` (Präfix) |
| 10 | `b965fdcf40809877` (Präfix) |

Die Tabelle zeigt bewusst nur die ersten 16 Hex-Zeichen der jeweiligen Ressourcendigest-Werte; die Gleichheit wurde zusätzlich durch direkten Bytevergleich geprüft.

## 4. Relokationen der Ressourcen 3–10

Der Parser meldet für jede Ressource 3 bis 10 genau einen Relokationseintrag. Die dekodierten Felder sind in beiden Dateien gleich:

- `info = 0x23`
- `source = resource`
- `type = HANDLE`
- `extra = 0`
- `target_resource_offset = 0`

Das WORD am Zieloffset 0 enthält jeweils die Nummer der Ressource selbst:

| Ressource | WORD bei Ressourcenoffset 0 |
|---:|---:|
| 3 | `0003` |
| 4 | `0004` |
| 5 | `0005` |
| 6 | `0006` |
| 7 | `0007` |
| 8 | `0008` |
| 9 | `0009` |
| 10 | `000A` |

Die Relokation ist somit als Ressourcen-HANDLE-Relokation am Anfang der jeweiligen Ressource erkennbar. Sie belegt **keine** direkte Querverbindung von Ressource 3 oder 4 zu Ressourcen 5–10. Die identischen Inhalte der Ressourcen 5–10 sind ein Befund des Bytevergleichs, nicht das Ergebnis einer aus diesen Relokationen abgeleiteten Referenzkette.

## 5. Ressourcentabellen und Positionen

Die vom Parser gelesenen Ressourcenpositionen und Größen lauten:

### BOUNCE.GEO

| Ressource | Dateioffset | Größe | Relokationsbytes | Flags |
|---:|---:|---:|---:|---:|
| 3 | 1316 | 384 | 4 | `0x145A` |
| 4 | 1704 | 336 | 4 | `0x145A` |
| 5 | 2044 | 160 | 4 | `0x1C7A` |
| 6 | 2208 | 96 | 4 | `0x1C7A` |
| 7 | 2308 | 256 | 4 | `0x1C7A` |
| 8 | 2568 | 624 | 4 | `0x1C7A` |
| 9 | 3196 | 144 | 4 | `0x1C7A` |
| 10 | 3344 | 224 | 4 | `0x1C7A` |

### BCOLTEST.GEO

| Ressource | Dateioffset | Größe | Relokationsbytes | Flags |
|---:|---:|---:|---:|---:|
| 3 | 1728 | 400 | 4 | `0x145A` |
| 4 | 2132 | 336 | 4 | `0x145A` |
| 5 | 2472 | 160 | 4 | `0x1C7A` |
| 6 | 2636 | 96 | 4 | `0x1C7A` |
| 7 | 2736 | 256 | 4 | `0x1C7A` |
| 8 | 2996 | 624 | 4 | `0x1C7A` |
| 9 | 3624 | 144 | 4 | `0x1C7A` |
| 10 | 3772 | 224 | 4 | `0x1C7A` |

Die Flags werden hier als Rohwerte wiedergegeben. Ihre semantische Auswertung ist nicht Gegenstand dieser Untersuchung.

## 6. Gesicherte Ergebnisse

1. Beide Dateien werden vom mitgelieferten Parser als GEOS-1.x-Geodes erkannt.
2. Beide Parserläufe melden keine Validierungsfehler.
3. Die vollständigen Ressourcen 5–10 sind zwischen den beiden Dateien byteidentisch.
4. Ressourcen 3 und 4 sind nicht byteidentisch; Ressource 4 ist trotz gleicher Größe unterschiedlich.
5. Ressourcen 3–10 besitzen jeweils einen Relokationseintrag `resource/HANDLE` an Ressourcenoffset 0.
6. Das dort gespeicherte unrelokierte WORD entspricht jeweils der eigenen Ressourcennummer.
7. Diese Relokationseinträge weisen keine Querverbindungen zwischen den Ressourcen nach.

## 7. Offene Fragen

- Warum werden dieselben Ressourceninhalte 5–10 in beiden Anwendungen verwendet?
- Welche konkreten LMEM-Objekte und Chunk-Typen enthalten diese Ressourcen?
- Welche Referenzmechanismen innerhalb der LMEM-/Objektstrukturen verbinden UI-Objekte mit Monikern oder Grafikdaten?
- Lassen sich die identischen Ressourcen auch in weiteren unabhängigen GeoWorks-1.x-Geodes finden?

## 8. Konsequenz für GeoViewPlus

Noch keinen Icon-Resolver aus den hier untersuchten Relokationen ableiten. Die Ergebnisse liefern eine gute Vergleichsbasis für wiederverwendete Ressourcen, aber keine semantische Zuordnung zu Programm-Icons, Dokument-Icons oder Monikern. Die nächste Untersuchung muss die LMEM-Strukturen und deren interne Referenzen unabhängig auflösen.

**Versionsgrenze:** Diese Untersuchung verwendet ausschließlich zwei GEOS-1.x-Dateien und deren 1.x-Parserpfad. PC/GEOS 2.x / FreeGEOS wird nicht als Beleg herangezogen.
