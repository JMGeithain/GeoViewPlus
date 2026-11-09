# GeoView Plus – Sicherungsstand Zeichensatzuntersuchung 0.4.1–0.4.10

Stand: 9. November 2026  
Projekt: PC/GEOS 1.x / deutsche GeoWorks-1.2-Installation  
Archivzweig: `backup/geo-0.4.9-investigation`

## Lokale Gesamtsicherung

Das vollständige Arbeitsarchiv mit Testprogramm, Regressionstest und den Untersuchungsberichten 0.4.2–0.4.9 wurde als ZIP-Datei für diesen Chat erstellt und bereitgestellt. Es wurde **nicht** in eine dauerhafte ChatGPT-Bibliothek hochgeladen. Download: `GeoViewPlus_0.4.1-0.4.9_Gesamtsicherung.zip`.

Das ZIP enthält:
- separate Testversion `GeoViewPlus_0.4.1_Zeichensatz_Test.py`
- Regressionstest `GeoViewPlus_0.4.1_Zeichensatz_Regressionstest.py`
- Testpaket `GeoViewPlus_0.4.1_Zeichensatz_Testpaket.zip`
- Untersuchungsberichte 0.4.2 bis 0.4.9 und ein SHA-256-Manifest

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
| 0.4.10 | Auflösung des ersten Kernel-Far-Calls über MZ-Relokation |

## Regressionstest

Die lokale Ausführung von `GeoViewPlus_0.4.1_Zeichensatz_Regressionstest.py` ergab 5 bestandene Tests und 0 fehlgeschlagene Tests. Geprüft wurden deutsche Sonderzeichen, das 36-Byte-Namensfeld, Archivbeispiele, `GEODEXGC.GEO` und das unveränderte CP850-Verhalten für GEOS 2.x.

## Gesicherte Grenzen

- Die Zuordnungen für `0xCE`, `0xCF`, `0xD0` und `0xD1` sind weiterhin ungeklärt.
- Der Localization-Schlüssel `quotes` ist belegt; sein konkreter Einfluss auf Dateinamendarstellung ist nicht nachgewiesen.
- Die `LOCAL.GEO`-Aufrufoperanden sind nachgewiesen; ihre symbolische Bedeutung bleibt offen.
- Der MZ-Einstiegspunkt `0000:02B1` ist verifiziert. Der erste Far-Call ist durch den Relokationseintrag als interner Kernel-Segmentaufruf belegt.
- Keine GeoWorks-Originaldatei wurde verändert.
- Die Testversion ist kein Release und nicht endgültig freigegeben.

## GitHub-Sicherungsstand

Im Branch `backup/geo-0.4.9-investigation` liegen die Sicherungsübersicht, der Bericht `GeoViewPlus_Untersuchung_0.4.9_Kernel_MZ_Relokationen.md` und der neue Bericht `GeoViewPlus_Untersuchung_0.4.10_Kernel_FarCall.md`. Die übrigen Einzeldateien des ZIP-Archivs sind noch nicht vollständig als separate Dateien im Repository abgelegt. Der Branch `main` wurde nicht verändert.
