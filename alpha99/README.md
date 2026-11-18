# GeoViewPlus 0.5 – Alpha99

Alpha99 ergänzt die Alpha98-PC/GEOS-2.x-VM-Verzeichnisanalyse um die Auflösung der Datenbankstruktur bis zu TokenEntry-Datensätzen, Monikerlisten und VisMoniker-Köpfen.

## Neu in Alpha99

- DBMapBlock-Felder aus VM-DB-Map-Block 0x00D4 auslesen
- DB-Gruppe/DB-Item über DBItemInfo und DBItemBlockInfo auflösen
- LMem-Chunkhandles und Chunk-Grenzen validieren
- 24-Byte-TokenEntry-Datensätze lesen und Dummy-Eintrag überspringen
- 6-Byte-Monikerlisteneinträge lesen
- alle referenzierten DB-Items und VisMoniker-Köpfe verfolgen
- neue GUI-Ansicht Token/Moniker… mit Rohdatenexport
- Originaldateien bleiben unverändert und werden nicht ins öffentliche Repository übernommen

## Verifizierter lokaler Datensatz

token_da(2).000 – 522.008 Bytes, SHA-256 76f1fb554111623b0616d139f29976087f3a8cb9b8dc722a8e45c4c18ae9da73.

- 268 TokenEntry-Datensätze (plus ein 24-Byte-Dummy)
- 268 Monikerlisten
- 1.081 Moniker-Referenzen, alle erfolgreich aufgelöst
- DESK besitzt neun Monikervarianten von 64×40 bis 15×10 Pixel

## Dateien

- geoviewplus_token_db_v2_database.py – read-only DB-/Token-/Moniker-Resolver
- tests/test_token_db_v2_database.py – Struktur- und optionaler Integrationstest
- docs/GeoViewPlus_0.5_Alpha99_TokenEntry_MonikerAufloesung.md – vollständiger Untersuchungsbericht
- alpha99/GeoViewPlus_Alpha99_GUI_Integration.patch – GUI-Erweiterung für Alpha98

## Tests

16 Tests aus TokenDB-Erkennung, VM-Directory und Alpha99 bestanden. Der echte Datenbank-Integrationstest läuft, wenn GEOVIEWPLUS_TOKEN_DB_SAMPLE auf die lokale Datei token_da(2).000 zeigt.

## Noch offen – Alpha100

Die GString-/Bitmap-Nutzdaten der aufgelösten Moniker werden dekodiert und anschließend als echte Programm- und Dokument-Icons gerendert. Die bloße Referenzauflösung ist noch keine fertige Bilddekodierung.
