# GeoViewPlus 0.5 – Untersuchung 231
## Alpha46: GeoWorks-1.x-Geode-Ressourcen, Code-Segmente und R11-Referenzen

**Prüfdatum:** 14.11.2026  
**Primärarchiv:** vom Benutzer bereitgestelltes `GEOWORKS.zip`  
**Untersuchte Dateien:** `GEOWORKS/WORLD/WRITE.GEO`, `GEOWORKS/WORLD/PROGRAMM.E/WRITE.GEO`

**Vorgänger:** Alpha45 / Untersuchung 230  
**Geltungsbereich:** ausschließlich GeoWorks / PC/GEOS 1.x. PC/GEOS-2.x-Strukturen werden nicht als Parsergrundlage verwendet.

## 1. Ziel und Methode

Alpha45 hatte 66 Bytefolgen `BE <ChunkHandle>` in der vollständigen Datei gefunden und linear disassembliert. Alpha46 rekonstruiert den Version-1-Geode-Kopf und die Ressourcentabelle, trennt die Ressourcen voneinander und disassembliert nur Segmente mit gesetztem HAF_CODE-Flag.

Als Formatvergleich wurde GeoDump von Marcus Gröber verwendet. Seine Dokumentation beschreibt Geodes als Folge aus zusätzlichem Programmheader, Bibliotheksliste, Exportliste, Ressourcentabelle und Ressourcen einschließlich Fixup-Tabellen. Sie erläutert auch den Kontrollflussansatz des symbolischen Disassemblers und die Pointer-/Jumplist-Strukturen.

Quellen:
- GeoDump-Dokumentation: https://www.mgroeber.de/geodump-documentation.html
- geos.h: https://github.com/bluewaysw/pcgeos/blob/master/Tools/geodump/geos.h
- geodump.c: https://github.com/bluewaysw/pcgeos/blob/master/Tools/geodump/geodump.c
- geodis.c: https://github.com/bluewaysw/pcgeos/blob/master/Tools/geodump/geodis.c

Die GeoDump-Referenz enthält Version-1- und Version-2-Pfade. Alpha46 verwendet ausschließlich den Version-1-Pfad: Magic 0x53CF45C7 und den zusätzlichen Geode-Kopf bei Dateioffset 0x00C0. Die Version-2-Headerstruktur wurde nicht angewendet.

## 2. Integrität und Geode-Kopf

- ZIP-Einträge: 2.951; CRC-Prüfung erfolgreich.
- Größe je WRITE.GEO: 73.110 Byte.
- Magic: 0x53CF45C7.
- Geode-Kopf Version 1: 0x00C0.
- Typ: 1 (Application).
- Permanenter Name: write.app.
- Bibliotheken: ui, spool, spell.
- Exporte: 16, alle in Segment 1.
- Ressourcensegmente: 36.

Die beiden WRITE.GEO-Dateien besitzen unterschiedliche vollständige SHA-256-Werte, aber identische Ressourcentabellen und Segmentbeschreibungen.

SHA-256:
- WRITE.GEO: 0d2958b810948603d15e412a61598623b9a4ccb73cfeb9fbe08d50ee718a6fd0
- PROGRAMM.E/WRITE.GEO: 3f1e606684ed6beae7d9ae26d23ad7430762ed6253fef596d1362ebdecba5e3f

## 3. Ressourcentabelle

Die Tabelle beginnt bei 0x018A und endet bei 0x02F2.

| Tabellenbereich | Dateioffset | Breite |
|---|---:|---:|
| Segmentlängen | 0x018A | 2 Byte × 36 |
| Segmentpositionen | 0x01D2 | 4 Byte × 36 |
| Fixup-Längen | 0x0262 | 2 Byte × 36 |
| Segmentflags | 0x02AA | 2 Byte × 36 |

Die Segmentpositionen sind 32-Bit-Dateioffsets. Die Fixup-Tabelle beginnt bei Segmentposition plus auf 16 Byte aufgerundeter Segmentlänge. Alle Fixup-Längen sind Vielfache von vier. Alle Segment-/Fixup-Bereiche liegen innerhalb der Datei und überlappen sich nicht.

### Code-Ressourcen

Sieben Ressourcen – Segmente 2 bis 8 – tragen das HAF_CODE-Flag. Der Rohwert ihrer Segmentflags ist 0x0A72 (READ_ONLY und CODE im hohen Byte).

| Segment | Dateioffset | Länge | Fixup-Bytes | MOV-SI-Kandidaten |
|---:|---:|---:|---:|---:|
| 2 | 0x012AE | 0x19F0 | 0x04D0 | 7 |
| 3 | 0x0316E | 0x1A20 | 0x0328 | 29 |
| 4 | 0x04EB6 | 0x1480 | 0x03BC | 16 |
| 5 | 0x066F2 | 0x10A0 | 0x0238 | 5 |
| 6 | 0x079CA | 0x03C0 | 0x0098 | 0 |
| 7 | 0x07E22 | 0x0900 | 0x0068 | 0 |
| 8 | 0x0878A | 0x0D70 | 0x01F4 | 9 |

## 4. Die 66 MOV-SI-Kandidaten in ihren Code-Ressourcen

Jede Code-Ressource wurde separat ab ihrem eigenen Offset 0 mit GNU objdump 2.44 (i8086, Intel-Syntax) disassembliert. Alle 66 Kandidaten werden erneut als MOV SI mit dem erwarteten ChunkHandle erkannt:

- Segment 2: 7
- Segment 3: 29
- Segment 4: 16
- Segment 5: 5
- Segment 8: 9
- Gesamt: 66 von 66.

### Kontrollfluss direkt nach MOV SI

Die erste Call-/Jump-Instruktion innerhalb der nächsten vier Instruktionen:

| Klasse | Anzahl |
|---|---:|
| Far Call | 28 |
| Near Call | 22 |
| Far Jump | 6 |
| Near Jump | 3 |
| Kein Call/Jump | 7 |
| Gesamt | 66 |

Bei den 28 Far Calls liegt jeweils ein Fixup vom Roh-Typ 0x0000 am Offset-Operanden. GeoDumps Decoder ordnet Typ 0x00 einer GEOS-Routine-Referenz zu. Die Roh-Ordinale 0x00A9 und 0x01E6 sind noch nicht mit Funktionsnamen aufgelöst.

Bei den sechs Far Jumps liegen Roh-Fixups der Typen 0x0001 und 0x0002 an den beiden Pointer-Wörtern. Diese Werte werden hier nicht weiter semantisch benannt.

Alle 25 Near-Call-/Near-Jump-Ziele wurden als Instruktionsanfänge im jeweiligen Ressourcensweep gefunden.

## 5. 351 Programmsegment-Verweise aus Segment 1

In der Fixup-Tabelle von Segment 1 wurden 351 Einträge mit Roh-Typ 0x0022 gefunden. GeoDumps Decoder bezeichnet diesen Typ als Fixup für Programmsegmente.

Für jeden Eintrag wurde das Segment-WORD am Fixup-Offset gelesen. Das unmittelbar davorliegende WORD wurde als Offset-Komponente ausgewertet. Diese Offset-zuerst-/Segment-zuletzt-Anordnung entspricht GeoDumps Beschreibung von Far-Pointer-Jumplisten.

Alle 351 Ziele liegen innerhalb der jeweiligen Zielsegmentgrenzen:

| Zielsegment | Verweise |
|---:|---:|
| 1 | 3 |
| 2 | 55 |
| 3 | 111 |
| 4 | 90 |
| 5 | 41 |
| 6 | 6 |
| 7 | 14 |
| 8 | 31 |
| Gesamt | 351 |

348 Verweise zeigen auf Code-Ressourcen 2 bis 8. Davon liegen 344 Ziele an Instruktionsanfängen des ressourcenlokalen linearen Sweeps.

Die sieben übrigen Ziele:
- Segment 1: 0x0448 (zweimal) und 0x08B7.
- Segment 3: 0x0815 und 0x09B6.
- Segment 8: 0x02BF und 0x0378.

Das sind sehr gute Einsprungpunkt-Kandidaten, aber noch kein rekursiv bestätigter Kontrollflussgraph.

## 6. R11-Gegenprüfung

R11 ist Segment 11:

- Dateioffset 0x09B22.
- Segmentlänge 0x0670.
- Flags 0x087A; LMem-Flag gesetzt.

LMem-Kopf:
- Segmentnummer 0x000B.
- Handle-Tabellenoffset 0x0010.
- LMem-Typ 0x0000.
- Blockgrößenfeld 0x066C.
- 20 Handles.

Die Einträge 11 bis 19 verweisen weiterhin auf die neun Datenanfänge 0x03E2 bis 0x0602. Die Alpha42-Zuordnung der ChunkHandles 0x0026 bis 0x0036 ist damit erneut bestätigt.

## 7. KERNEL.EXE und offene Ordinalnamen

Das Archiv enthält GEOWORKS/KERNEL.EXE (72.736 Byte). Die Datei beginnt mit MZ und wurde deshalb nicht mit dem GEO-Geode-Parser gelesen.

Die Kernel-Ordinalwerte 0x00A9 und 0x01E6 sind noch nicht mit Funktionsnamen verknüpft. Dafür wird eine passende GeoWorks-1.x-Kernel-Symbol-/Exportquelle oder eine kontrollierte Analyse des tatsächlich verwendeten Kernels benötigt.

SHA-256 KERNEL.EXE: c2cc8952cdb01d0f459bf281ee3b78f8ce9464aba0b58c3758f8c73e24fb6eb5

## 8. Gesichert und offen

Gesichert:
1. Version-1-Geode-Kopf bei 0x00C0.
2. 36 Segmente; sieben Code-Ressourcen.
3. Alle 66 Kandidaten liegen in Code-Ressourcen und werden dort als erwartetes MOV SI erkannt.
4. 351 Programmsegment-Fixups in Segment 1.
5. 348 Verweise auf Code-Ressourcen; 344 Ziele an Instruktionsanfängen im linearen Ressourcensweep.
6. R11 bleibt als LMem-Segment mit 20 Handles konsistent.

Offen:
- rekursiver Kontrollfluss und echte Einsprungpunkte;
- die Namen der Kernel-Ordinale 0x00A9 und 0x01E6;
- die semantische Zuordnung der neun Grafik-Chunks als Cursor, Icon, Moniker, Maske oder andere Ressource.

## 9. Alpha47

1. Die 351 Programmsegment-Verweise als Einsprungpunkt-Kandidaten verwenden.
2. Kontrollfluss rekursiv verfolgen.
3. Die 66 MOV-SI-Stellen mit erreichbaren Codeblöcken verknüpfen.
4. Kernel-Ordinale 0x00A9 und 0x01E6 mit einer GeoWorks-1.x-Quelle abgleichen.
5. Erst danach die Grafikoperationen der neun R11-Chunks benennen.

## 10. Reproduzierbarkeit

Voraussetzungen: Python 3.10+, GNU objdump mit i8086-Unterstützung und GEOWORKS.zip.

```bash
python geoviewplus_alpha46_geode_resource_map.py GEOWORKS.zip --out output
GEOWORKS_ZIP=GEOWORKS.zip python -m unittest -v test_alpha46.py
```

**38 von 38 Tests bestanden.** Alpha46 ist statische Analyse: keine GEO-Datei verändert, keine GUI-Änderung, kein EXE-Build.
