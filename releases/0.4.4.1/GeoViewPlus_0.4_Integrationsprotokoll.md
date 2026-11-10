# GeoViewPlus 0.4 – Integrationsprotokoll

## Zusammenführung
- Programmgrundlage: `GeoViewPlus_0.4_Zeichensatz_Test.py` aus dem Nutzerpaket 0.4.
- Integrierter Programmname: `GeoViewPlus.py`.
- Ressourcenfix: `geoworks_motif_icon.ico` und der zugehörige PyInstaller-Parameter `--add-data` aus dem Nutzerpaket 0.3.2.
- Beibehalten: Token-Vorschaubilder WP00/WDAT und Untersuchung 122.
- Buildskript: Python-Erkennung über `py -3` oder `python`; PyInstaller wird geprüft und nur nach Rückfrage installiert.

## Wichtige Abgrenzung
Das ZIP 0.4 enthielt eine vollständige 970-Zeilen-Anwendung sowie einen Regressionstest, aber nicht die benötigten externen Testdateien `GEOWORKS.zip` und `GEODEXGC.GEO`. Die neue Regressionstestdatei prüft deshalb nur die im Paket vorhandenen Funktionen und Ressourcen und ist ohne externe GeoWorks-Daten ausführbar.

## Nicht behauptet
- Python auf dem Windows-Rechner des Nutzers wurde nicht direkt ausgelesen.
- Es wurde hier keine Windows-EXE erstellt oder gestartet.
- Das korrekte Fenster-Icon in der fertigen EXE ist erst nach dem lokalen Windows-Test bestätigt.
