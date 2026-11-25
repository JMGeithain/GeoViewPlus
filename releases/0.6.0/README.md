# GeoViewPlus 0.6.0

Windows-Programm, das GEOS-Dateien von GeoWorks 1.x, GEOS 2.x (Ensemble, NewDeal, Breadbox)
und FreeGEOS anzeigt: Langnamen, Kopfdaten und Icons.
Vorbild: GeoView von Rainer Bettsteller (RABE-Soft, 2000).

## Dateien

| Datei | Inhalt |
|---|---|
| `GeoViewPlus.py` | Windows-Oberfläche (Tkinter) |
| `geoscore.py` | Lese-Logik: Dateiköpfe, VM-Dateien, Token-Datenbank, Icons in Apps |
| `test_geoscore.py` | Regressionstest mit einer echten Installation |
| `make_exe.bat` | baut `dist\GeoViewPlus.exe` (Python, Pillow, PyInstaller) |
| `report.py` | erzeugt eine HTML-Übersicht (Hilfswerkzeug) |

## Woher die Icons kommen

1. **Apps:** aus der App selbst (Icon-Liste im Bereich des Application-Objekts).
2. **Dokumente:** aus der App, die das Dokument erzeugt hat (Ersteller-Token im Dokumentkopf).
   Die App meldet ihre Dokument-Tokens in den Daten des Dokument-Controllers.
3. Sonst aus der Token-Datenbank (`SYSTEM\TOKEN.DB` bzw. `PRIVDATA\TOKEN_DA.000`).
4. Zuletzt ein Standard-Icon (gAPP, gDAT, FILE, FLDR).

## Suche (Extras → Suchen, Strg+F)

Durchsucht die ganze Installation oder den aktuellen Ordner mit Unterordnern nach
GEOS-Langname/DOS-Name (Teilwort), Token, Ersteller-Token, Hersteller-ID (passt auf Token
oder Ersteller) und Art (Programme, Dokumente, Daten). Es werden nur die Dateiköpfe gelesen;
die Suche läuft im Hintergrund. Doppelklick auf einen Treffer zeigt die Datei im Hauptfenster.
Beispiele: alle GeoWrite-Dokumente (Ersteller `WP00`), alle eigenen Programme (Hersteller-ID `16506`).

## Details zu Apps und Dokumenten

* **Apps:** interner Name (z. B. `write.app`), Eigenschaften (Prozess, Anwendung, Bibliothek …),
  Anzahl Ressourcen und Exporte, benutzte Bibliotheken mit Protokollnummer, angelegte Dokumentarten.
  Knopf „Dokumente dieser App suchen“.
* **Dokumente:** „Erzeugt von“ mit der App aus der Installation, Knopf „→ Zur App“ und
  „Ähnliche Dokumente suchen“.

## Ordner (nur GEOS 2.x / FreeGEOS)

GeoWorks 1.x kennt keine langen Ordnernamen. Ab GEOS 2.x liegen in Ordnern zwei Verwaltungsdateien:

* `@DIRNAME.000` – GEOS-Dateikopf mit Langname und Token des Ordners (eigenes Ordner-Icon,
  z. B. `nMYC` für „Computer“). Danach folgen die **Verknüpfungen** des Ordners: je ein Satz
  mit Signatur `LN00`, Langname, Typ, Token, Ersteller, Attributen und dem Ziel
  (Standardpfad wie WORLD/DOCUMENT/SYSAPPL plus Pfad aus GEOS-Langnamen, oder ein Laufwerk wie `A:\.`).
  GeoViewPlus zeigt die Verknüpfungen als eigene Einträge; ein Doppelklick öffnet das Ziel.
* `@DIRECTO.000` – VM-Datei von GeoManager (DirInfo, Protokoll 4): Fenstergröße und -position
  in Prozent des Bildschirms, Ansicht, Sortierung, angezeigte Dateitypen und die Positionen frei
  verschobener Symbole. Die Positionen hängen an einer FileID (Hash `id = id*33 + Zeichen` über
  den DOS-Pfad im Emulator); GeoViewPlus ordnet sie den Dateien zu, indem es den unbekannten
  Ordnerpfad-Anteil aus den Einträgen zurückrechnet. *An echten Dateien mit verschobenen Symbolen
  noch nicht geprüft.*

## Formate (geprüft an GeoWorks 1.28 und FreeGEOS 2.81)

* Dateikopf 1.x: Signatur `C7 45 CF 53`, Kopf 0xC8 Bytes; Typ +04h, Release +08h, Protokoll +10h,
  Token +14h, Ersteller +1Ah, Langname +20h, Notizen +44h, Copyright +A8h.
* Dateikopf 2.x: Signatur `C7 45 C1 53`, Kopf 0x100 Bytes; Langname +04h, Typ +28h, Release +2Ch,
  Protokoll +34h, Token +38h, Ersteller +3Eh, Notizen +44h, Copyright +A8h, Erstellt +C8h.
* VM-Dateien: VM-Dateikopf direkt nach dem GEOS-Kopf (Signatur `ADEB`). Bei 2.x zählen alle
  Dateipositionen erst nach dem 256-Byte-Kopf.
* Token-Datenbank: DB-Map → Token-Tabelle → Moniker-Liste (6-Byte-Einträge Typ/Gruppe/Item) → Moniker.
  1.x-Einträge sind 26 Bytes groß und liegen mit noch ungeklärten Lücken; sie werden mit einer
  bis zum Bitmap prüfenden Suche gelesen.
* Moniker: Typ-Byte, Breite, Höhe, GString mit Bitmap (mono, 16 oder 256 Farben, optional Maske,
  PackBits); 256-Farben-Icons als „komplexe“ Bitmaps mit eigener Palette.

## Start

    python GeoViewPlus.py [Ordner oder Datei]

## Test

    python test_geoscore.py "%APPDATA%\freeGEOS\GEOWORKS" "%APPDATA%\freeGEOS\FreeGEOS.281"

Möllerjaner © 2026 Johannes Möller
