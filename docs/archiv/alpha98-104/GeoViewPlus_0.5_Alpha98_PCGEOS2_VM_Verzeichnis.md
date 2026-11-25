# GeoViewPlus 0.5 – Alpha98: PC/GEOS-2.x-VM-Verzeichnis

## Ergebnis

Alpha98 ergänzt einen read-only Parser für das VM-Verzeichnis der PC/GEOS-2.x-Token-Datenbank. Die bestehende GeoWorks-1.x-Erkennung bleibt getrennt.

**Noch nicht dekodiert:** DB-Gruppen und -Items, Token-Einträge, Moniker-Listen sowie App-/Dokument-Icons. User-IDs werden ausschließlich numerisch angezeigt.

## Formatgrundlage

Eine GEOS-Datei besitzt einen 256-Byte-Dateikopf. Bei VM-Dateien beginnt bei 0x100 ein 24-Byte-VM-Kopf:
- +0: VM-Kennung 0xADEB
- +2: Directory-Größe
- +4: 32-Bit-Directory-Zeiger relativ zum Byte nach dem 256-Byte-Dateikopf

Der Directory-Block beginnt mit der Kennung 0x00FB und einem 32-Byte-Kopf. Danach folgen 12-Byte-Einträge:
- +0 Memory-Handle (WORD)
- +2 Flags (WORD)
- +4 User-ID (WORD)
- +6 Blockgröße (WORD)
- +8 Dateiposition (DWORD, relativ zum GEOS-Dateikopf)

Der VMBlockHandle eines Eintrags ist sein Byteoffset im Directory-Block: 0x20 + Index * 12. Er ist nicht mit dem Memory-Handle-Feld gleichzusetzen.

## Reproduzierter Anwender-Datensatz

Die Datei token_da(2).000 wurde lokal untersucht und nicht in das öffentliche Repository kopiert.

- Größe: 522.008 Bytes
- SHA-256: 76f1fb554111623b0616d139f29976087f3a8cb9b8dc722a8e45c4c18ae9da73
- Directory-Dateioffset: 0x537B8
- Directory-Größe: 0x0D4C (3.404 Bytes)
- Directory-Einträge: 281
- Belegte Blöcke: 113
- Freie Blöcke: 1
- Freie Handles: 167
- Belegte Blöcke laut Header: 113
- Geladene Blöcke laut Header: 43
- VM-Map-Block-Handle: 0x0044
- DB-Map-Block-Handle: 0x00D4

User-ID-Verteilung der belegten Einträge:

| User-ID | Anzahl |
|---|---:|
| 0x0000 | 1 |
| 0x8000 | 1 |
| 0xFF00 | 1 |
| 0xFF01 | 30 |
| 0xFF02 | 80 |

Diese User-IDs erhalten noch keine semantische Bezeichnung. Der VM-Map-Block 0x0044 ist 128 Bytes groß; der DB-Map-Block 0x00D4 ist 16 Bytes groß. Beide können mit vm_block_data() bounds-geprüft gelesen werden.

## GUI

Die Alpha98-GUI-Änderung ergänzt einen Button „VM-Blöcke…“ und eine Tabelle mit Index, VM-Handle, Memory-Handle, User-ID, Flags, Größe und Dateioffset. Unbekannte Strukturen werden nicht als Icons ausgegeben.

## Tests

Die fünf Tests in test_token_db_v2_vm_directory.py arbeiten mit einer synthetischen VM-Datei und prüfen Directory-Layout, Handle-Berechnung, User-ID-Ausgabe sowie die Zurückweisung ungültiger Header und Zeiger.

## Nächster Schritt: Alpha99

1. DB-Map-Block und VM-Map-Block getrennt untersuchen.
2. DB-Gruppenblöcke und Item-Blöcke unterscheiden.
3. Group-/Item-Referenzen nachweisen.
4. GeodeToken (vier Token-Zeichen plus Manufacturer-ID), TokenEntry und Moniker-DB-Items verbinden.
5. Erst nach gesicherter Referenzkette die Moniker-Bitmaps dekodieren.

## Quellen

- Marcus Gröber, Exchanging Data with GEOS Devices: https://www.mgroeber.de/exchanging-data-with-geos-devices.html
- FreeGEOS SDK, 19 Database Library: https://bluewaysw.github.io/pcgeos/Concepts/cdb.html
- FreeGEOS SDK, 6 Applications and Geodes, Abschnitt 6.2 Creating Icons: https://bluewaysw.github.io/pcgeos/Concepts/cappl.html
- FreeGEOS Token API: https://bluewaysw.github.io/pcgeos/Routines/rroutq_t.html
