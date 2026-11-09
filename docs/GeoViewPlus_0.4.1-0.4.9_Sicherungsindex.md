# GeoView Plus – Sicherungsstand Zeichensatzuntersuchung 0.4.1–0.4.9

Stand: 9. November 2026  
Projekt: PC/GEOS 1.x / deutsche GeoWorks-1.2-Installation  
Archivzweig: `backup/geo-0.4.9-investigation`

## Gesicherte lokale Gesamtsicherung

Das vollständige Arbeitsarchiv mit Testprogramm, Regressionstest und den Untersuchungsberichten wurde zusätzlich in der ChatGPT-Dateibibliothek abgelegt:

`/GeoViewPlus/Sicherungen/GeoViewPlus_0.4.1-0.4.9_Gesamtsicherung.zip`

Das ZIP enthält:
- separate Testversion `GeoViewPlus_0.4.1_Zeichensatz_Test.py`
- Regressionstest `GeoViewPlus_0.4.1_Zeichensatz_Regressionstest.py`
- Testpaket `GeoViewPlus_0.4.1_Zeichensatz_Testpaket.zip`
- Untersuchungsberichte 0.4.2 bis 0.4.9, einschließlich des zusätzlichen MZ-Relokationsberichts
- README und SHA-256-Manifest

## Inhaltliche Übersicht

| Bericht | Thema |
|---|---|
| 0.4.2 | Ungeklärte Zeichen 0xCE, 0xCF, 0xD0, 0xD1 |
| 0.4.3 | Fontprüfung |
| 0.4.4 | Localization-Einträge in GEOS.INI |
| 0.4.5 | LOCAL.GEO und quotes-Schlüssel |
| 0.4.6 | LOCAL.GEO-Codepfad |
| 0.4.7 | Kernel-Aufrufe und Tabellenzugriff |
| 0.4.8 | Korrektur der MZ-Headerauswertung |
| 0.4.9 | Kernel-Ladebild und MZ-Einstiegspunkt |
| 0.4.9 Zusatz | MZ-Relokationstabellen |

## Regressionstest

Die lokale Ausführung von `GeoViewPlus_0.4.1_Zeichensatz_Regressionstest.py` ergab:

- 5 Tests bestanden
- 0 fehlgeschlagen

Geprüft wurden die deutschen Sonderzeichen, das 36-Byte-Namensfeld, Archivbeispiele, `GEODEXGC.GEO` und das unveränderte CP850-Verhalten für GEOS 2.x.

## Gesicherte Grenzen

- Die Zuordnungen für `0xCE`, `0xCF`, `0xD0` und `0xD1` sind weiterhin ungeklärt.
- Der Localization-Schlüssel `quotes` ist belegt; sein konkreter Einfluss auf Dateinamendarstellung ist nicht nachgewiesen.
- Die Kernel-Aufrufoperanden in `LOCAL.GEO` sind nachgewiesen, ihre symbolische Bedeutung bleibt offen.
- Die MZ-Analyse wurde in 0.4.8 korrigiert und in 0.4.9 weitergeführt.
- Keine GeoWorks-Originaldatei wurde verändert.
- Die Testversion ist kein Release und nicht als endgültig freigegeben.

## Dateien im Repository

Dieser Commit ergänzt die Sicherungsübersicht und den neuesten MZ-Relokationsbericht. Die vollständige, unveränderte Sammlung der Arbeitsdateien liegt im oben genannten ZIP-Backup. Der ursprüngliche Hauptzweig `main` bleibt unverändert; die Sicherung befindet sich in diesem Archivzweig.
