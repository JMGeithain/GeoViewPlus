# GeoViewPlus 0.5 – Untersuchung 230
## Alpha45: Instruktionskontext-Audit der 66 MOV-SI-Kandidaten

**Prüfdatum:** 14.11.2026  
**Prüfgrundlage:** vom Benutzer bereitgestelltes `GEOWORKS.zip`  
**Dateien:** `GEOWORKS/WORLD/WRITE.GEO` und `GEOWORKS/WORLD/PROGRAMM.E/WRITE.GEO`  
**Vorgänger:** Alpha44 / Untersuchung 229  
**Geltungsbereich:** GeoWorks / PC/GEOS 1.x.

## 1. Ziel

Alpha44 fand 66 Bytefolgen `BE <imm16>` pro GeoWrite-Variante. Auf dem 8086 ist `BE iw` der Opcode für `MOV SI,imm16`. Alpha45 prüft diese Fundstellen mit GNU objdump im 8086-Modus und vergleicht die linearen Disassemblierungs-Kontexte beider Dateien.

**Methodische Grenze:** GNU objdump wurde linear ab Dateioffset 0 über die vollständige GEO-Datei ausgeführt. Eine GEO-Datei enthält Header, Tabellen, Code und Ressourcen. Der lineare Sweep ersetzt deshalb keine Rekonstruktion der Code-Ressourcen, gültigen Einsprungpunkte und Kontrollflussgrenzen. Die Resultate sind Instruktionskontext-Hinweise, kein abschließender Nachweis, dass jede Stelle ausführbarer Code ist.

## 2. Eingabeintegrität

| Merkmal | Ergebnis |
|---|---:|
| ZIP-Einträge | 2.951 |
| ZIP-CRC-Prüfung | erfolgreich |
| Größe je WRITE.GEO | 73.110 Byte |
| R11-Dateioffset | `0x9B22` |
| R11-Größe | `0x066C` |
| R11 zwischen Varianten | byteidentisch |
| Kandidaten je Variante | 66 |
| Kandidatenpositionen zwischen Varianten | identisch |

SHA-256:
- WRITE.GEO: `0d2958b810948603d15e412a61598623b9a4ccb73cfeb9fbe08d50ee718a6fd0`
- PROGRAMM.E/WRITE.GEO: `3f1e606684ed6beae7d9ae26d23ad7430762ed6253fef596d1362ebdecba5e3f`

## 3. Lineare 8086-Dekodierung

GNU objdump 2.44 wurde mit `-D -b binary -m i8086 -Mintel` auf beide Dateien angewendet.

| Prüfschritt | WRITE.GEO | PROGRAMM.E/WRITE.GEO |
|---|---:|---:|
| Bytekandidaten | 66 | 66 |
| Kandidaten an Instruktionszeile des linearen Sweeps | 66 | 66 |
| Dekodierung als MOV SI mit passendem Immediate | 66 | 66 |
| gleiche Dekodierung an allen Positionen | 66 | 66 |

Verteilung:
| ChunkHandle-Kandidat | Treffer |
|---:|---:|
| `0x0026` | 3 |
| `0x0028` | 8 |
| `0x002A` | 6 |
| `0x002C` | 4 |
| `0x002E` | 5 |
| `0x0030` | 12 |
| `0x0032` | 10 |
| `0x0034` | 15 |
| `0x0036` | 3 |
| **Summe** | **66** |

Alle Kandidaten liegen außerhalb der R11-Ressource `0x9B22–0xA18D`.

## 4. Folgekontexte

Innerhalb der nächsten vier linearen Instruktionen:

| Kontextklasse | Anzahl |
|---|---:|
| Near-Call | 26 |
| Far-Call `0000:01E6` | 15 |
| Far-Call `0000:00A9` | 13 |
| Jump | 5 |
| Kein Call/Jump | 7 |
| **Summe** | **66** |

Die Routineziele erhalten hier keine semantische Benennung.

Beispiele:

```asm
0131E: BE 2E 00       mov si,0x2e
01321: B8 55 08       mov ax,0x855
01324: BF 80 00       mov di,0x80
01327: 9A A9 00 00 00 call 0x0:0xa9
0132C: 5E             pop si
0132D: 5D             pop bp
0132E: C3             ret
```

```asm
02506: BE 32 00       mov si,0x32
02509: B8 01 60       mov ax,0x6001
0250C: BF 80 00       mov di,0x80
0250F: 9A A9 00 00 00 call 0x0:0xa9
02514: BE 28 00       mov si,0x28
```

```asm
036D8: BE 2C 00       mov si,0x2c
036DB: E8 20 FC       call 0x32fe
036DE: 49             dec cx
036DF: 81 C9 00 04    or cx,0x400
```

Die vollständigen 66 Kontexte stehen in `analysis/alpha45/GEO_alpha45_instruction_contexts.csv`.

## 5. Ergebnis und Grenzen

**Direkt geprüft:** Alle 66 Bytekandidaten werden in beiden Varianten im linearen Sweep als MOV SI mit dem erwarteten Immediate dekodiert; die Dekodierungen stimmen an allen Fundstellen überein.

**Noch offen:** echte Codegrenzen, Ressourcentyp, gültige Einsprungpunkte, Kontrollfluss, tatsächliche Handle-Dereferenzierung und die Semantik der neun Grafik-Chunks. Im GeoViewPlus-Resolver darf noch keine automatische Icon-/Cursor-Zuordnung aus diesen Befunden entstehen.

## 6. Alpha46

1. GeoWorks-1.x-Geode-/Ressourcengrenzen rekonstruieren.
2. Code-Ressourcen von Daten- und Grafikressourcen trennen.
3. Gültige Einsprungpunkte bestimmen.
4. Kontrollfluss und Call-Ziele auflösen.
5. Die 66 Stellen als bestätigte Code-Referenz, Datenfund oder unklar klassifizieren.
6. Prüfen, ob SI tatsächlich in die R11-Handle-Tabelle aufgelöst wird.

## 7. Reproduzierbarkeit

```bash
python geoviewplus_alpha45_disassembly_audit.py GEOWORKS.zip --out output
GEOWORKS_ZIP=GEOWORKS.zip python -m unittest -v test_alpha45.py
```

Voraussetzungen: Python 3.10+ und GNU objdump mit 8086-Unterstützung. **15 von 15 Tests bestanden.** Keine GUI-Änderung, kein EXE-Build.
