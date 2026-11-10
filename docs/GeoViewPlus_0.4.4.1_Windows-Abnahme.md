# GeoViewPlus 0.4.4.1 – Windows-Abnahme und Fortschritt

**Stand:** 10. November 2026  
**Projektleitung und Weiterentwicklung:** Johannes Möller  
**KI-Unterstützung:** ChatGPT (OpenAI) und Grok (xAI)

## Windows-Sichtprüfung

Der Projektverantwortliche hat die mit Version 0.4.4.1 erzeugte Anwendung unter Windows geöffnet und einen Screenshot des Dialogs „Über GeoViewPlus“ bereitgestellt. Sichtbar bestätigt sind:

- kompaktes Fenster ohne übermäßige Breite
- JME-Spirallogo links neben dem Text, verkleinert auf maximal 104 × 104 Pixel
- korrekte mehrzeilige Darstellung mit echten Zeilenumbrüchen
- kein sichtbares \n mehr im Dialog
- Veranstaltungshinweis: „Entwickelt zum 25. Geithainer PC/GEOS-Treffen 2026 in Syhra.“
- Projektleitung: Johannes Möller
- KI-Unterstützung: ChatGPT (OpenAI) und Grok (xAI)
- Copyright-Zeile: „Möllerjaner © 2026 Johannes Möller“

**Abnahme:** Die Layoutkorrektur ist durch die Windows-Sichtprüfung des Nutzers bestätigt.

## Änderungen der Versionen 0.4.1 bis 0.4.4.1

- **0.4.1:** Drittanbieter-Klassifizierung und zugehörige Dokumentation.
- **0.4.2:** Öffnen-Dialog berücksichtigt `*.DB`, damit `TOKEN.DB` auswählbar ist.
- **0.4.3:** Autorenangaben nennen Johannes Möller als Projektleitung/Weiterentwicklung sowie ChatGPT und Grok als KI-Unterstützung; Rainer Bettstellers historische Original-Idee bleibt gewürdigt.
- **0.4.4:** JME-Spirallogo im Hilfe-Dialog und Hinweis auf das 25. Geithainer PC/GEOS-Treffen 2026 in Syhra; Logo wird als PyInstaller-Ressource eingebunden.
- **0.4.4.1:** Logo auf 104 × 104 Pixel verkleinert, Textumbruch bei 510 Pixeln und echte Zeilenumbrüche; Copyright-Zeile angepasst.

## Paketbestand

Das Gesamtpaket enthält die Anwendung `GeoViewPlus.py`, Regressionstests, `make_exe.bat`, JME-Logo, Anwendungs-ICO, Icon-Ressourcen und die begleitenden Untersuchungsberichte. Das Buildskript verwendet die vorhandene Python-Installation und bindet das Logo für PyInstaller ein.

Der Nutzer hat zuvor den EXE-Bau mit Python 3.15.0, Tkinter, Pillow und PyInstaller 6.22.3 erfolgreich ausgeführt. Die Darstellung des Hilfe-Dialogs wurde anschließend im fertigen Windows-Programm visuell bestätigt.

## Regressionstests

Für den Paketstand 0.4.4.1 wurden im Modell-Arbeitscontainer Syntaxprüfung und Regressionstests ausgeführt: **10 Tests bestanden**. Diese automatisierten Tests ergänzen, ersetzen aber nicht die Windows-Sichtprüfung.

## Weiter offene technische Aufgaben

Die UI-Abnahme ist kein Nachweis für die noch offene semantische Icon-Zuordnung. Weiterhin erforderlich:

1. VM-Ressourcen- und Chunk-Referenzen in GeoWorks-1.x-GEO-Dateien rekonstruieren.
2. Den Verweis vom Icon-Token auf die tatsächlichen Moniker-Ressourcen nachweisen.
3. Programm-Icon und Dokument-Icon anhand der Referenzketten unterscheiden.
4. Echtes Programm-Icon aus der geöffneten GEO-Datei extrahieren.
5. Dokument-Icons anhand Anwendung/Dokumenttyp zuordnen und einen nachvollziehbaren Cache aufbauen.

Strukturell validierte Moniker-Fundstellen sind nicht automatisch semantisch zugeordnete Icons. Größe oder Farbtiefe allein sind kein ausreichender Beweis.

## Versionsgrenze und Datenintegrität

Die neue Ressourcenanalyse und Icon-Engine bleiben strikt bei GeoWorks / PC/GEOS 1.x. Vorhandene GEOS-2.x-Kompatibilität im Programm ist getrennt zu behandeln. Originale GeoWorks-Dateien und `TOKEN.DB` bleiben unverändert und werden nicht ohne gesonderte Freigabe öffentlich ins Repository übernommen.

## Synchronisationshinweis

Das Repository-README war bei der Prüfung noch auf Version 0.3. Die Anwendung `GeoViewPlus.py` war nicht im Repository-Root vorhanden. Diese Änderung aktualisiert daher zunächst die Projektübersicht und dieses Abnahme-Dossier. Sie ist **keine vollständige Synchronisation des ausführbaren Quellcode-/Ressourcenpakets**. Das vollständige Paket bleibt als separates ZIP-Gesamtpaket dokumentiert.
