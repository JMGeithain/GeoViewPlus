# GeoViewPlus

Windows-Werkzeug zur Untersuchung von PC/GEOS-Dateien – mit besonderem Schwerpunkt auf GeoWorks / PC/GEOS 1.x.

## Aktueller Arbeitsstand

**Dokumentierter Anwendungstand: 0.4.4.1 (10.11.2026)**

Der Hilfe-Dialog wurde im Windows-Programm vom Projektverantwortlichen visuell geprüft. Das JME-Spirallogo wird kompakt angezeigt; die Textumbrüche funktionieren; der Dialog nennt das 25. Geithainer PC/GEOS-Treffen 2026 in Syhra sowie die Projektleitung Johannes Möller und die KI-Unterstützung ChatGPT (OpenAI) und Grok (xAI).

Die Copyright-Zeile lautet: **Möllerjaner © 2026 Johannes Möller**.

Details und Abnahmeprotokoll: [GeoViewPlus 0.4.4.1 – Windows-Abnahme und Fortschritt](docs/GeoViewPlus_0.4.4.1_Windows-Abnahme.md).

Technischer Ist-Stand der GEO-Icon-Ermittlung: [Untersuchung 123 – GEO-Icon-Resolver](docs/GeoViewPlus_Untersuchung_123_GEO_Icon_Resolver_Iststand.md).

Fortsetzung der TOKEN.DB-Analyse: [Untersuchung 129 – Blockgruppen 0x2222 und 0x3333](docs/GeoViewPlus_Untersuchung_129_TOKENDB_Blockgruppen.md) und [Untersuchung 130 – 304-Byte-Datensätze](docs/GeoViewPlus_Untersuchung_130_TOKENDB_304Byte_Datensaetze.md). [Untersuchung 131 – Ausnahmen im 304-Byte-Datensatzfeld](docs/GeoViewPlus_Untersuchung_131_TOKENDB_Ausnahmen.md) und [Untersuchung 132 – WORD-Feldanalyse der 304-Byte-Datensätze](docs/GeoViewPlus_Untersuchung_132_TOKENDB_WORD_Feldanalyse.md) und [Untersuchung 133 – Handlevergleich der 304-Byte-Datensätze](docs/GeoViewPlus_Untersuchung_133_TOKENDB_Handlevergleich.md). [Untersuchung 134 – Vergleich der TOKEN.DB-Zielblöcke](docs/GeoViewPlus_Untersuchung_134_TOKENDB_Zielblockvergleich.md).


Fortsetzung der GEO-Ressourcenanalyse: [Untersuchung 149 – Relokationen und Ressourcenvergleich in BOUNCE.GEO und BCOLTEST.GEO](docs/GeoViewPlus_Untersuchung_149_Relokationen_Ressourcenvergleich.md).

Fortsetzung der GEO-Ressourcenanalyse: [Untersuchung 150 – LMEM-Kopf- und Chunk-Tabellenvergleich](docs/GeoViewPlus_Untersuchung_150_LMEM_Kopf_Chunk_Tabellenvergleich.md).

Fortsetzung der GEO-Ressourcenanalyse: [Untersuchung 151 – zeitgenössische GeoWorks-Quelle zur LMEM-Verwaltung](docs/GeoViewPlus_Untersuchung_151_GeoWorks_LMEM_Primaerquelle.md).

Fortsetzung der GEO-Ressourcenanalyse: [Untersuchung 152 – LMEM-Abgleich und Handle-Dereferenzierung](docs/GeoViewPlus_Untersuchung_152_LMEM_Abgleich_Handle_Dereferenzierung.md).

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

Fortsetzung der GEO-Ressourcenanalyse: [Untersuchung 153 – LMEM-Handle- und Offset-Analyse der Ressourcen 5–10](docs/GeoViewPlus_Untersuchung_153_LMEM_Handle_Offset_Analyse.md).

Fortsetzung der GEO-Ressourcenanalyse: [Untersuchung 154 – Tabellenziele in den Ressourcen 3 und 4](docs/GeoViewPlus_Untersuchung_154_Ressourcen3_4_Tabellenziele.md).

Fortsetzung der GEO-Ressourcenanalyse: [Untersuchung 155 – Textdatensatz-Präfixe und überlappende Tabellenziele](docs/GeoViewPlus_Untersuchung_155_Textdatensatz_Praefixe_und_ueberlappende_Ziele.md).

Fortsetzung der GEO-Ressourcenanalyse: [Untersuchung 156 – Längenfeld der Textdatensätze in Ressourcen 3 und 4](docs/GeoViewPlus_Untersuchung_156_Textdatensatz_Laengenfeld.md).

Fortsetzung der GEO-Ressourcenanalyse: [Untersuchung 157 – Binäre Tabellenziele in Ressourcen 3 und 4](docs/GeoViewPlus_Untersuchung_157_Binaere_Tabellenziele.md).

Fortsetzung der GEO-Ressourcenanalyse: [Untersuchung 158 – Bytevergleich binärer Bereiche in BOUNCE.GEO und BCOLTEST.GEO](docs/GeoViewPlus_Untersuchung_158_Binaerbereiche_BOUNCE_BCOLTEST_Vergleich.md).

Fortsetzung der GEO-Ressourcenanalyse: [Untersuchung 159 – Feldvergleich der wiederkehrenden binären Struktur in Ressource 3](docs/GeoViewPlus_Untersuchung_159_Binaerstruktur_Feldvergleich.md).

Fortsetzung der GEO-Ressourcenanalyse: [Untersuchung 160 – Suche der 12-Byte-Muster in weiteren GEO-Ressourcen](docs/GeoViewPlus_Untersuchung_160_Suche_12Byte_Muster_in_weiteren_Ressourcen.md).

Fortsetzung der GEO-Ressourcenanalyse: [Untersuchung 161 – CC-CC-Muster und binäre Bereiche in allen Ressourcen](docs/GeoViewPlus_Untersuchung_161_CC_CC_Muster_und_Binaerbereiche.md).

Fortsetzung der GEO-Ressourcenanalyse: [Untersuchung 162 – Ressourcenenden und mögliche Abschlussbereiche](docs/GeoViewPlus_Untersuchung_162_Ressourcenenden_Abschlussbereiche.md).

Fortsetzung der GEO-Ressourcenanalyse: [Untersuchung 163 – Abgleich der Ressourcenlänge mit den Headerfeldern +08h und +14h](docs/GeoViewPlus_Untersuchung_163_Ressourcenlaenge_Headerfeld_08_14.md).

Fortsetzung der GEO-Ressourcenanalyse: [Untersuchung 164 – Tabellenziele im Verhältnis zum Grenzwert +08h](docs/GeoViewPlus_Untersuchung_164_Tabellenziele_und_Grenzwert_08.md).

Fortsetzung der GEO-Ressourcenanalyse: [Untersuchung 165 – Headerfeld +0Ah und Anzahl der Tabelleneinträge](docs/GeoViewPlus_Untersuchung_165_Headerfeld_0A_Tabellenanzahl.md).

Fortsetzung der GEO-Ressourcenanalyse: [Untersuchung 166 – Headerkontrolle an weiteren GeoWorks-1.x-Dateien](docs/GeoViewPlus_Untersuchung_166_Externe_GEO_Kontrolle.md).

Fortsetzung der GEO-Ressourcenanalyse: [Untersuchung 167 – Tabellenstruktur in Treiber-Ressource 2](docs/GeoViewPlus_Untersuchung_167_Treiberressource2_Tabellenstruktur.md).

Fortsetzung der GEO-Ressourcenanalyse: [Untersuchung 168 – Textlängenfelder und Abschlussbytes in Treiber-Ressource 2](docs/GeoViewPlus_Untersuchung_168_Textlaengen_und_Abschlussbytes.md).

Fortsetzung der GEO-Ressourcenanalyse: [Untersuchung 169 – Vergleich von Treiber-Ressource 1 mit Ressource 2](docs/GeoViewPlus_Untersuchung_169_Treiberressource1_Vergleich.md).

Fortsetzung der GEO-Ressourcenanalyse: [Untersuchung 170 – Relokationseinträge in Treiber-Ressource 1](docs/GeoViewPlus_Untersuchung_170_Treiberressource1_Relokationen.md).

Fortsetzung der GEO-Ressourcenanalyse: [Untersuchung 171 – Bytekontext der Relokationsziele in Treiber-Ressource 1](docs/GeoViewPlus_Untersuchung_171_Relokationsziele_Kontext.md).

Fortsetzung der GEO-Ressourcenanalyse: [Untersuchung 173 – Gruppierung der FAR-CALL-Ziele in den SVGA-Treibern](docs/GeoViewPlus_Untersuchung_173_FAR_CALL_Zielgruppen.md).

Fortsetzung der Kernel-Analyse: [Untersuchung 174 – Aufbau und Grenzen der vorliegenden KERNEL.EXE](docs/GeoViewPlus_Untersuchung_174_KERNEL_EXE_MZ_Analyse.md).

Fortsetzung der Kernel-Analyse: [Untersuchung 175 – Die 276 DOS-MZ-Relokationen der KERNEL.EXE](docs/GeoViewPlus_Untersuchung_175_MZ_Relokationstabelle.md).

Fortsetzung der Kernel-Analyse: [Untersuchung 176 – Kartierung der MZ-Relokationsstellen nach Segment](docs/GeoViewPlus_Untersuchung_176_MZ_Segmentkartierung.md).

Fortsetzung der Kernel-Analyse: [Untersuchung 177 – MZ-Relokationswerte und Instruktionskontexte](docs/GeoViewPlus_Untersuchung_177_MZ_Relokationswerte_Opcodekontexte.md).

Fortsetzung der Kernel-Analyse: [Untersuchung 178 – Die 50 MOV-immediate-Relokationsstellen im Kontext](docs/GeoViewPlus_Untersuchung_178_MOV_Segmentregister_Verwendung.md).

Fortsetzung der Kernel-Analyse: [Untersuchung 179 – Datenzugriffe nach Laden des Segments 0E34h](docs/GeoViewPlus_Untersuchung_179_Datenzugriffe_Segment_0E34.md).


Fortsetzung der Kernel-Analyse: [Untersuchung 180 – Datenfelder 0040h–0046h und 0FE2h–0FFEh](docs/GeoViewPlus_Untersuchung_180_Kernel_Datenfelder_0040_0FFE.md).


Fortsetzung der Kernel-Analyse: [Untersuchung 182 – INT-8-Einsprungpunkt und CS-relative Adressierung](docs/GeoViewPlus_Untersuchung_182_INT8_CS_Einsprungpunkt.md).
