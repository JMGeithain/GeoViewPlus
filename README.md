# GeoViewPlus

Windows-Werkzeug zur Untersuchung von PC/GEOS-Dateien – mit besonderem Schwerpunkt auf GeoWorks / PC/GEOS 1.x.

## Aktueller Arbeitsstand

**Dokumentierter Anwendungstand: 0.4.4.1 (10.11.2026)**

Der Hilfe-Dialog wurde im Windows-Programm vom Projektverantwortlichen visuell geprüft. Das JME-Spirallogo wird kompakt angezeigt; die Textumbrüche funktionieren; der Dialog nennt das 25. Geithainer PC/GEOS-Treffen 2026 in Syhra sowie die Projektleitung Johannes Möller und die KI-Unterstützung ChatGPT (OpenAI) und Grok (xAI).

Die Copyright-Zeile lautet: **Möllerjaner © 2026 Johannes Möller**.

Details und Abnahmeprotokoll: [GeoViewPlus 0.4.4.1 – Windows-Abnahme und Fortschritt](docs/GeoViewPlus_0.4.4.1_Windows-Abnahme.md).

Technischer Ist-Stand der GEO-Icon-Ermittlung: [Untersuchung 123 – GEO-Icon-Resolver](docs/GeoViewPlus_Untersuchung_123_GEO_Icon_Resolver_Iststand.md).

Fortsetzung der TOKEN.DB-Analyse: [Untersuchung 129 – Blockgruppen 0x2222 und 0x3333](docs/GeoViewPlus_Untersuchung_129_TOKENDB_Blockgruppen.md) und [Untersuchung 130 – 304-Byte-Datensätze](docs/GeoViewPlus_Untersuchung_130_TOKENDB_304Byte_Datensaetze.md). [Untersuchung 131 – Ausnahmen im 304-Byte-Datensatzfeld](docs/GeoViewPlus_Untersuchung_131_TOKENDB_Ausnahmen.md) und [Untersuchung 132 – WORD-Feldanalyse der 304-Byte-Datensätze](docs/GeoViewPlus_Untersuchung_132_TOKENDB_WORD_Feldanalyse.md).

## Versionsschritte

- **0.4.1:** Drittanbieter-Klassifizierung.
- **0.4.2:** Dateiauswahl um `*.DB` erweitert, damit `TOKEN.DB` direkt geöffnet werden kann.
- **0.4.3:** Projektverantwortung und KI-Unterstützung im Hilfe-Dialog ausgewiesen.
- **0.4.4:** JME-Spirallogo und Hinweis auf das 25. Geithainer PC/GEOS-Treffen 2026 in Syhra.
- **0.4.4.1:** Hilfe-Dialog kompakter; Logo 104 × 104 Pixel, Textumbruch und echte Zeilenumbrüche korrigiert.

## Technische nächste Schritte

Die weitere Kernarbeit ist die Rekonstruktion der GeoWorks-1.x-VM-Ressourcenreferenzen. Erst nach Nachweis der Referenzketten werden echtes Programm-Icon und Dokument-Icon semantisch zugeordnet und die Extraktion bzw. der Dokument-Icon-Cache implementiert.

Strukturell gefundene Moniker-Kandidaten sind nicht automatisch die verwendeten Programm- oder Dokument-Icons.

## Build unter Windows

Das separate Gesamtpaket enthält `make_exe.bat`, das die vorhandene Python-Installation sowie Tkinter, Pillow und PyInstaller prüft und den EXE-Bau startet. Der Nutzer hat einen erfolgreichen Build mit Python 3.15.0 und PyInstaller 6.22.3 gemeldet.

## Datenintegrität und Versionsgrenze

Die neue Ressourcenanalyse bleibt strikt bei GeoWorks / PC/GEOS 1.x. GEOS-2.x-Kompatibilität im bestehenden Programm wird als getrennter Zweig behandelt. Originaldateien und `TOKEN.DB` werden nicht verändert und nicht ohne gesonderte Freigabe in das öffentliche Repository übernommen.

## Repository-Synchronisation

Dieses Repository enthält derzeit Projektübersicht und Dokumentation sowie ältere Build-Historie. Die Anwendung `GeoViewPlus.py` und die vollständigen Laufzeitressourcen des getesteten 0.4.4.1-Gesamtpakets sind mit diesem Commit **noch nicht vollständig in das Repository gespiegelt**. Die Dokumentationsaktualisierung darf nicht mit einer vollständigen Quellcodeveröffentlichung verwechselt werden.
