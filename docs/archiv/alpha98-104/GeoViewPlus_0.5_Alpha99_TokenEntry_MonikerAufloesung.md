# GeoViewPlus 0.5 – Alpha99: TokenEntry- und Moniker-Auflösung

## Ergebnis

Alpha99 rekonstruiert für die bereitgestellte PC/GEOS-2.x-Datei token_da(2).000 die Verbindung vom DB-Map-Block über den Token-Map-DB-Eintrag bis zu den Monikerlisten und deren DB-Items. Alle Auswertungen erfolgen read-only.

Datei: 522.008 Bytes
SHA-256: 76f1fb554111623b0616d139f29976087f3a8cb9b8dc722a8e45c4c18ae9da73

## 1. DB-Map-Block

Der VM-Header nennt DB-Map-Blockhandle 0x00D4. Der Directory-Eintrag führt auf einen 16-Byte-Block. Die ersten sechs WORDs lauten:

00D4 3030 008C 000E 00F8 0000

Die sechs Felder stimmen mit DBMapBlock aus Include/Internal/dbaseInt.def überein: DBMB_vmemHandle=0x00D4, DBMB_handle=0x3030, DBMB_mapGroup=0x008C, DBMB_mapItem=0x000E, DBMB_ungrouped=0x00F8, DBMB_newUngrouped=0x0000. Die vier nachfolgenden Bytes des 16-Byte-VM-Blocks sind null; sie werden nicht den sechs WORD-Feldern zugeschrieben.

## 2. Token-Map-DB-Item

Die DB-Gruppe 0x008C hat User-ID 0xFF01. Das DB-Item bei Gruppenoffset 0x000E enthält DBItemBlockInfo-Offset 0x010E und LMem-Chunkhandle 0x0014. Die DBItemBlockInfo bei 0x010E verweist auf VM-Item-Block 0x00B0; RefCount=1. Der Block trägt User-ID 0xFF02 und ist 6.544 Bytes groß.

Im LMem-Block löst Chunkhandle 0x0014 auf Chunkoffset 0x0056 auf. Das LMem-Chunkgrößenfeld lautet 0x193A; nach Abzug des 2-Byte-Größenfeldes umfasst der Chunkinhalt 6.456 Bytes.

## 3. TokenEntry-Datensätze

Der Chunk enthält exakt 269 Datensätze zu je 24 Bytes. Der erste Datensatz besteht vollständig aus Nullen und ist der Dummy-Eintrag, den der Originalquellcode in Library/User/Token/token.asm beim Suchen überspringt. Damit bleiben 268 TokenEntry-Datensätze.

Der 24-Byte-Aufbau ergibt sich aus den Originaldefinitionen:
- GeodeToken (TokenChars + ManufacturerID): 6 Byte
- TokenDBItem (Gruppe + Item): 4 Byte
- TokenFlags: 2 Byte
- ReleaseNumber: 8 Byte
- ProtocolNumber: 4 Byte

Die ersten TokenChars lauten unter anderem DESK, FLDR, FILE, gAPP, gDAT, gDOS, TMPL, DLCH, PFHC und BOOK. Alle 268 TokenEntry-Datensätze verweisen auf Monikerlisten in Gruppe 0x0068. Die Release- und Protocol-Werte bleiben Rohdaten; sie werden nicht semantisch bewertet, weil die untersuchte AddTokenEntry-Routine diese Felder nicht initialisiert.

## 4. Monikerlisten

Die Gruppe 0x0068 trägt User-ID 0xFF01. Die DBItemBlockInfo am Offset 0x010E verweist auf VM-Item-Block 0x011C; RefCount=0x010C (268).

Alle 268 TokenEntry-Monikerlisten konnten aus dieser Gruppe aufgelöst werden. Die Listen bestehen aus 6-Byte-Einträgen: WORD VisMonikerListEntryType, WORD DB-Gruppe, WORD DB-Item.

Listenlängen:
| Einträge je Liste | Anzahl |
|---:|---:|
| 1 | 19 |
| 2 | 59 |
| 3 | 50 |
| 4 | 59 |
| 5 | 33 |
| 6 | 10 |
| 7 | 13 |
| 8 | 8 |
| 9 | 4 |
| 10 | 3 |
| 11 | 9 |
| 13 | 1 |

Insgesamt wurden 1.081 Moniker-Referenzen aufgelöst. Jede referenzierte DB-Gruppe und jedes Item ließ sich im VM-/DB-Verzeichnis auflösen; in diesem Durchlauf gab es keine fehlerhaften Referenzen.

## 5. Gegenprobe am Token DESK

DESK besitzt neun Monikerlisteneinträge. Alle neun Ziel-Items konnten geöffnet und ihre 5-Byte-VisMoniker-Köpfe gelesen werden:

| Listentyp | Zielgruppe | Zielitem | VisMoniker-Typ | Größe |
|---:|---:|---:|---:|---:|
| 0x23C6 | 0x0140 | 0x000E | 0x46 | 64 × 40 |
| 0x23C1 | 0x0188 | 0x000E | 0x41 | 64 × 40 |
| 0x13C6 | 0x01D0 | 0x000E | 0x46 | 48 × 30 |
| 0x13C1 | 0x0218 | 0x000E | 0x41 | 48 × 30 |
| 0x03C6 | 0x0260 | 0x000E | 0x46 | 32 × 20 |
| 0x03C1 | 0x02A8 | 0x000E | 0x41 | 32 × 20 |
| 0x03E1 | 0x02F0 | 0x000E | 0x61 | 48 × 14 |
| 0x04C1 | 0x0338 | 0x000E | 0x41 | 15 × 15 |
| 0x04E1 | 0x0380 | 0x000E | 0x61 | 15 × 10 |

Die VisMoniker-Kopfstruktur ist ein Byte VisMonikerType gefolgt von zwei WORDs für Breite und Höhe. Das GString-Bit 0x40 ist bei allen neun DESK-Varianten gesetzt. Die GString-Inhalte selbst werden in Alpha99 noch nicht gerendert.

## 6. Implementierung

Neu: geoviewplus_token_db_v2_database.py. Der Resolver liest DBMapBlock-Felder, löst DB-Gruppe/DB-Item über DBItemInfo und DBItemBlockInfo auf, prüft LMem-Chunkhandles und Chunkgrenzen, liest TokenEntry-Datensätze, Monikerlisteneinträge und VisMoniker-Köpfe. Er verändert keine Originaldatei.

Tests: tests/test_token_db_v2_database.py. Der Integrationstest läuft nur, wenn GEOVIEWPLUS_TOKEN_DB_SAMPLE auf die lokale Testdatei zeigt; die Binärdatei wird nicht veröffentlicht.

## 7. Nächster Schritt – Alpha100

1. GString-/Bitmap-Nutzdaten der neun DESK-Moniker untersuchen.
2. GString-Opcodefolgen und eingebettete Bitmap-Daten getrennt klassifizieren.
3. Decoder mit weiteren Tokens und unabhängigen Referenzdateien testen.
4. Erst nach erfolgreicher Bildrekonstruktion die Moniker-Galerie integrieren.

## Quellen

- FreeGEOS Include/Internal/dbaseInt.def: DBMapBlock, DBGroupHeader, DBItemInfo, DBItemBlockInfo.
- FreeGEOS Include/token.def: TokenEntry, TokenDBItem, MonikerGroupEntry.
- FreeGEOS Include/geode.def: GeodeToken, ReleaseNumber, ProtocolNumber.
- FreeGEOS Include/lmem.def: LMemBlockHeader und Chunkhandle.
- FreeGEOS Tools/goc/symbol.h: VisMonikerListEntryType, VisMonikerType, VisualMonikerListEntry und VisualMoniker.
- FreeGEOS Library/User/Token/token.asm: Dummy-TokenEntry, TokenEntry-Suche und DBMap-/Token-Map-Verwendung.
- FreeGEOS Technical Documentation, Database Library: https://bluewaysw.github.io/pcgeos/Concepts/cdb.html
