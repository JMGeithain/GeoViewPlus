# GeoViewPlus 0.4 – Gesamtpaket

## Inhalt
- `GeoViewPlus.py`: vollständige Anwendung aus dem 0.4-Zeichensatz-Testbuild.
- `geoworks_motif_icon.ico`: Fenster-/EXE-Icon aus dem 0.3.2-Ressourcenfix.
- `make_exe.bat`: erkennt auf diesem Windows-Rechner Python 3 über `py -3` oder `python`.
- `GeoViewPlus_Regressionstest.py`: lokale Tests der Zeichensatzkorrektur und der Icon-Datei.
- `icons/`: vorhandene Token-Vorschaubilder WP00 und WDAT.
- `docs/`: Untersuchungsnotiz zum ICO-Fix und zu leeren Monikern.

## 1. Regressionstest
Im entpackten Verzeichnis eine Eingabeaufforderung öffnen und ausführen:

```bat
py -3 GeoViewPlus_Regressionstest.py
```

Falls `py` nicht verfügbar ist:

```bat
python GeoViewPlus_Regressionstest.py
```

Der Test benötigt keine zusätzlichen GeoWorks-Dateien.

## 2. EXE erstellen
`make_exe.bat` doppelklicken. Die Batchdatei:
1. sucht den vorhandenen Python-3-Interpreter (`py -3`, danach `python`);
2. prüft Tkinter;
3. prüft PyInstaller;
4. fragt bei fehlendem PyInstaller, ob es in genau dieser Python-Umgebung installiert werden soll;
5. baut `dist\GeoViewPlus.exe`.

Eine Internetverbindung ist nur erforderlich, wenn PyInstaller erst installiert werden muss.

## 3. Wichtige Hinweise
- Die Batchdatei kann nur Python-Installationen erkennen, die über den Python Launcher oder `PATH` erreichbar sind. Eine beliebige lokale Installation außerhalb davon muss gegebenenfalls über `PATH` eingebunden werden.
- Ich kann die Python-Installation auf Ihrem Windows-Rechner von hier aus nicht direkt durchsuchen. Die Suche erfolgt deshalb beim Start der Batchdatei auf Ihrem Rechner.
- Die EXE wurde in dieser Arbeitsumgebung nicht unter Windows gebaut oder gestartet. Der erfolgreiche Windows-Build und das Fenster-Icon müssen auf Ihrem Rechner geprüft werden.
- Die Zeichensatz-Zuordnung in 0.4 ist empirisch anhand der beigefügten Testfälle; sie ist keine vollständige veröffentlichte Spezifikation des GeoWorks-1.x-Zeichensatzes.
- Es wurden keine GeoWorks-Originaldateien verändert oder in dieses Paket aufgenommen.


## Nachtrag 0.4.1
Die GeoWorks-1.x-Dateityp-Anzeige wurde korrigiert: Ein gültiger 1.x-Header mit
Typkennung 0 wird nicht mehr als „Unknown / Non-GEOS“ bezeichnet. Siehe
`docs/GeoViewPlus_0.4.1_Klassifizierung.md`.


## Nachtrag 0.4.2
Der Öffnen-Dialog zeigt jetzt auch Dateien mit der Erweiterung `.db` an,
insbesondere `TOKEN.DB`.


## Nachtrag 0.4.3
Autorenangaben im Quelltext und Hilfe-Dialog aktualisiert:
Projektleitung und Weiterentwicklung: Johannes Möller;
KI-Unterstützung: ChatGPT (OpenAI) und Grok (xAI).


## Nachtrag 0.4.4
Das JME-Spirallogo wird im Hilfe-Dialog angezeigt. Außerdem enthält der Dialog
den Hinweis: „Entwickelt zum 25. Geithainer PC/GEOS-Treffen 2026 in Syhra.“
`make_exe.bat` bindet die PNG-Datei in den PyInstaller-Build ein.
