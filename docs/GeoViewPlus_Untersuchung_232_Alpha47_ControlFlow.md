# GeoViewPlus 0.5 – Untersuchung 232
## Alpha47: Rekursive Kontrollfluss- und Erreichbarkeitsanalyse in GeoWrite

**Prüfdatum:** 14.11.2026  
**Primärarchiv:** GEOWORKS.zip  
**Untersuchte Geodes:** GEOWORKS/WORLD/WRITE.GEO und GEOWORKS/WORLD/PROGRAMM.E/WRITE.GEO  
**Vorgänger:** Alpha46 / Untersuchung 231  
**Geltungsbereich:** GeoWorks / PC/GEOS 1.x.

## 1. Ziel

Alpha46 rekonstruierte die Ressourcentabelle und fand 351 Programmsegment-Verweise aus Segment 1 sowie 20 Programm-Far-Pointer-Fixups in Code-Ressourcen. Alpha47 verwendet diese Referenzen und die 16 Export-Einträge als Startpunkte für eine rekursive Verfolgung von Basic Blocks.

## 2. Formatreferenz

GeoDumps Fixup-Auswertung unterscheidet unter anderem:
- Typ 0x22: Programmsegment-Fixup; Segment-WORD am Fixup-Offset. Die zugehörige Offset-Komponente liegt in den Segment-1-Pointerlisten unmittelbar davor.
- Typ 0x24: Programm-Far-Pointer; GeoDump liest am Fixup-Offset zuerst das Segment-WORD und danach das Offset-WORD.

Quellen:
- GeoDump-Dokumentation: https://www.mgroeber.de/geodump-documentation.html
- geodis.c: https://github.com/bluewaysw/pcgeos/blob/master/Tools/geodump/geodis.c
- geodump.c: https://github.com/bluewaysw/pcgeos/blob/master/Tools/geodump/geodump.c

Die Referenzimplementierung enthält Version-1- und Version-2-Pfade. Alpha47 benutzt weiterhin ausschließlich die in Alpha46 validierte GeoWorks-1.x-Ressourcenabbildung und deren Fixup-Daten.

## 3. Startpunkte

| Quelle | Rohverweise | Eindeutige Ziele |
|---|---:|---:|
| Segment 1, Typ 0x0022 | 351 | 321 Code-Ziele |
| Typ 0x0024 Far-Pointer | 20 | 7 Code-Ziele |
| Export-Tabelle | 16 | 16 Exportadressen |
| Vereinigte Startmenge | – | 343 |

Die 351 Typ-0x22-Verweise wurden in Alpha46 geprüft: 348 zeigen auf Code-Ressourcen, 344 davon liegen an Instruktionsanfängen des ressourcenlokalen Linearsweeps. Alle 20 Typ-0x24-Pointer zeigen auf Instruktionsanfänge in Code-Ressourcen.

## 4. Kontrollflussmodell

GNU objdump wird jeweils mit der Startadresse eines bekannten Einsprungpunktes auf die betreffende Ressource angesetzt. Verfolgt werden Near Calls, Near Jumps, bedingte Sprünge, Loop-Befehle, Rückkehrbefehle sowie auflösbare Far Calls/Jumps mit Programmsegment-Fixup. Indirekte Sprünge und nicht aufgelöste Fixup-Formen werden nicht spekulativ verfolgt.

## 5. Ergebnis

| Kennzahl | Ergebnis |
|---|---:|
| Eindeutige Startadressen | 343 |
| Basic-Block-Starts verarbeitet | 1.206 |
| Dekodierte Instruktionsadressen | 11.246 |
| Kontrollflusskanten | 2.374 |
| Überlappende/abweichende Dekodierungen | 21 |
| Nicht dekodierbare Seed-/Branch-Adressen | 0 |
| MOV-SI-Kandidaten insgesamt | 66 |
| Im aktuellen Graphen erreicht | 48 |
| Im aktuellen Graphen nicht erreicht | 18 |

### Erreichbarkeit nach Code-Ressource

| Segment | Kandidaten | Erreicht | Nicht erreicht |
|---:|---:|---:|---:|
| 2 | 7 | 5 | 2 |
| 3 | 29 | 13 | 16 |
| 4 | 16 | 16 | 0 |
| 5 | 5 | 5 | 0 |
| 8 | 9 | 9 | 0 |
| Gesamt | 66 | 48 | 18 |

Alle 18 nicht erreichten Kandidaten liegen in Segment 2 oder 3. Die vollständigen Dateioffsets und Handles stehen in GEO_alpha47_candidate_reachability.csv und im JSON-Bericht.

## 6. Einordnung der 18 nicht erreichten Kandidaten

**Nicht erreicht bedeutet nicht nachgewiesen unerreichbar.** Mögliche Ursachen sind indirekte Dispatch-/Callback-Tabellen, Objektressourcen und Handle-Verweise vom Typ 0x0023, weitere Fixup-Formen oder überlappende Code-/Datenbereiche.

Die 21 überlappenden Dekodierungen zeigen, dass verschiedene Einsprungpunkte teilweise unterschiedliche Instruktionsgrenzen erzeugen. Diese Fälle werden separat dokumentiert.

## 7. Bedeutung für R11

48 der 66 Stellen, an denen ein R11-ChunkHandle in SI geladen wird, liegen im aktuellen rekursiv erreichten Code. Das ist ein stärkerer Befund als die Byte-Suche aus Alpha45.

Noch nicht nachgewiesen ist, welche Kernel-Funktionen die Ordinale 0x00A9 und 0x01E6 ausführen und ob die neun R11-Chunks Cursor, Icons, Moniker, Masken oder andere Grafikelemente sind. Eine automatische Icon-Klassifikation ist deshalb noch nicht freigegeben.

## 8. Alpha48

1. Die 18 nicht erreichten Stellen auf Referenzen in Objektressourcen und Typ-0x23-Handle-Fixups prüfen.
2. Indirekte Dispatch- und Callback-Tabellen identifizieren.
3. Die 21 überlappenden Dekodierungen gegen Fixup-Grenzen und Objektmethoden abgleichen.
4. Kernel-Ordinale 0x00A9 und 0x01E6 gegen eine passende GeoWorks-1.x-Kernelquelle prüfen.
5. Erst danach die Grafiksemantik der neun R11-Chunks festlegen.

## 9. Reproduzierbarkeit

Voraussetzungen: Python 3.10+, GNU objdump mit i8086-Unterstützung und GEOWORKS.zip.

```bash
python geoviewplus_alpha47_control_flow.py GEOWORKS.zip --out output
GEOWORKS_ZIP=GEOWORKS.zip python -m unittest -v test_alpha47.py
```

**20 von 20 Tests bestanden.** Statische Analyse; keine GEO-Datei verändert, keine GUI-Änderung, kein EXE-Build.
