# GeoViewPlus

Windows-Werkzeug zur Untersuchung von PC/GEOS-Dateien – von GeoWorks 1.* bis FreeGEOS.

## Aktueller Entwicklungsstand

**Version 0.3 – Farbmoniker-Testbuild**

Der 0.3-Teststand ergänzt die Vorschau von 4-Bit-Farbmonikern um eine aus GeoWorks 1.x `WORLD/DUMP.GEO` rekonstruierte 16-Farben-RGB-Palette. Die Nibble-Reihenfolge (hohes Nibble zuerst) ist im dortigen `mapPixels`-Ausgabepfad dokumentiert.

Wichtige Einschränkung: Es ist noch nicht abschließend nachgewiesen, dass jeder Farbmoniker-Untertyp in `TOKEN.DB` dieselbe Palette verwendet. Version 0.3 ist deshalb als Testbuild gekennzeichnet.

## Build unter Windows

Voraussetzungen: Python 3.15, Pillow und PyInstaller.

Im entpackten Projektordner `make_exe.bat` ausführen. Die EXE wird unter `dist/GeoViewPlus.exe` erzeugt.

## Projektstruktur

- `GeoViewPlus.py` – Anwendung
- `GeoViewPlus_0.3_Regressionstest.py` – Regressionstests
- `make_exe.bat` – EXE-Build
- `icons/` – Anwendungsressourcen
- `docs/` – Untersuchungsdokumentation

## Daten und Integrität

Originale GeoWorks-Dateien und `TOKEN.DB` werden nicht verändert und aus Urheberrechts- und Reproduzierbarkeitsgründen nicht mit diesem Repository ausgeliefert. Tests verwenden eine lokal bereitgestellte `TOKEN.DB`.

## Untersuchung 121

Siehe [GeoWorks 1.x: 4-Bit-Farbmoniker, RGB-Zuordnung und Nibble-Reihenfolge](docs/GeoViewPlus_Untersuchung_121_Farbpalette_4Bit.md).
