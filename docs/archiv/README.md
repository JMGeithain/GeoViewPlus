# Archiv: frühere Untersuchungsberichte

Diese Berichte stammen aus Zweigen, die nicht in `main` übernommen wurden. Sie sind hier
gesichert, damit der Forschungsweg nachvollziehbar bleibt. Der zugehörige Code ist durch
GeoViewPlus 0.5 bis 0.7 (`releases/0.7.0/geoscore.py`) vollständig überholt und wurde nicht übernommen.

## alpha98-104 (18./19.11.2026, nur GEOS 2.x)

Früherer Anlauf, die Token-Datenbank von GEOS 2.x/FreeGEOS zu lesen.

| Bericht | Thema | Heute gelöst in |
|---|---|---|
| Alpha98 | VM-Kopf und Blockverzeichnis von `TOKEN_DA.000` | `VMFile` |
| Alpha99 | TokenEntry und Auflösung der Moniker-Listen | `TokenDB` |
| Alpha100 | Bitmap aus dem GString | `parse_moniker` |
| Alpha101 | DESK-Moniker in allen Größen | `TokenEntry.monikers` |
| Alpha102 | Pixel- und Masken-Aufbau | `moniker_rgba` |
| Alpha103 | VGA16-Standardpalette und PNG-Ausgabe | `PALETTE16` (identische Werte) |

Alpha104 (Moniker-Typwort) hatte keinen eigenen Bericht; die Bedeutung der Bits steht heute in
`describe_entry_type`.

## untersuchungen-0.4.9-0.4.21 (10.11.2026, GeoWorks 1.x)

Kernel-Analyse von GeoWorks 1.x (`KERNEL.EXE`): MZ-Relokationen, FAR-Calls, Bootstrap,
Datensegment, Feldzugriffe, DOS-Treiberauswahl, Trampolin bei 257Eh, BX-Herkunft und
Statuswörter, Feldschreiber, Segmentkontext und DS-Kontrollfluss; dazu der Sicherungsindex
0.4.1–0.4.9. Für die Icons nicht mehr nötig, aber Grundlage für spätere GeoWorks-1-Projekte
(z. B. einen Token-Löscher).
