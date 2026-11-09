# GeoView Plus – Sicherungsstand Zeichensatzuntersuchung 0.4.1–0.4.13

Stand: 9. November 2026  
Projekt: PC/GEOS 1.x / deutsche GeoWorks-1.2-Installation  
Archivzweig: `backup/geo-0.4.9-investigation`

## Lokale Gesamtsicherung

Die ZIP-Datei `GeoViewPlus_0.4.1-0.4.13_Gesamtsicherung.zip` wurde als Download in diesem Chat bereitgestellt. Sie enthält die Testversion 0.4.1, Regressionstest, Testpaket und die Berichte 0.4.2–0.4.13. Die ZIP-Datei ist eine lokale Chat-Ausgabe und wurde nicht als ZIP-Datei in das GitHub-Repository hochgeladen.

## Untersuchungsübersicht

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
| 0.4.10 | MZ-relokierter Kernel-Far-Call |
| 0.4.11 | Kernel-Bootstrap, Segmentkopie und dynamischer zweiter Far-Call |
| 0.4.12 | Kernel-Datensegment 0E34h/0E35h und gespeicherte Segmentwerte |
| 0.4.13 | Zugriffe auf Kernel-Datenfelder im kopierten Segment |

## Regressionstest

Die im vorherigen Arbeitsstand dokumentierte lokale Ausführung von `GeoViewPlus_0.4.1_Zeichensatz_Regressionstest.py` ergab 5 bestandene Tests und 0 fehlgeschlagene Tests. Für Untersuchung 0.4.13 wurde kein neuer Regressionstest ausgeführt, da sie ausschließlich die statische Kernel-Analyse betrifft.

## Gesicherte Grenzen

- Die Zuordnungen für `0xCE`, `0xCF`, `0xD0` und `0xD1` sind weiterhin ungeklärt.
- Der Localization-Schlüssel `quotes` ist belegt; sein konkreter Einfluss auf Dateinamendarstellung ist nicht nachgewiesen.
- Die `LOCAL.GEO`-Aufrufoperanden sind nachgewiesen; ihre symbolische Bedeutung bleibt offen.
- Der MZ-Einstiegspunkt `0000:02B1` ist verifiziert.
- Der erste MZ-Far-Call führt in einen internen Bootstrap-Code, der `0x1CE0` Bytes in ein berechnetes Segment kopiert. Der Segmentoperand des zweiten Far-Calls wird anschließend dynamisch angepasst.
- `0E34h`/`0E35h` ist ein vom Bootstrap-Code verwendeter Datenbereich; die vollständige Datenstruktur ist offen.
- Die Felder `DS:0044h` und `DS:0046h` haben weitere nachgewiesene Zugriffe. `DS:0040h` und `DS:0042h` werden im Bootstrap mit `SS` und `SP` belegt; spätere Leser dieser Felder sind im untersuchten Kopierbereich nicht belegt.
- `DS:05BAh` wird zunächst mit `CS` beschrieben und später als Segmentwort eines Far-Pointers überschrieben.
- Keine GeoWorks-Originaldatei wurde verändert; die Testversion ist kein Release.

## GitHub-Sicherungsstand

Im Branch `backup/geo-0.4.9-investigation` liegen der Index sowie die Berichte 0.4.9 (MZ-Relokationen) und 0.4.10 bis 0.4.13. Die übrigen Dateien des ZIP-Archivs sind noch nicht vollständig als separate Dateien im Repository abgelegt. Der Branch `main` wurde durch diese Sicherungsarbeiten nicht verändert.
