# GeoViewPlus – Untersuchung 122: leere S/W-Moniker und Fenster-ICO

Datum: 08.11.2026

## 1. Moniker bei TOKEN.DB-Offset 0x0036DA

Der Datensatz wurde anhand der aktuellen TOKEN.DB erneut geprüft.

- Moniker-Typ: `0x41` (S/W)
- Abmessungen: 64 × 40 Pixel
- Bitmap-Länge: `0x0056` (86 Bytes)
- Bitmap-Typ: `0x00`
- erwartete dekomprimierte Länge: 8 Bytes/Zeile × 40 Zeilen = 320 Bytes
- tatsächliche dekomprimierte Länge: 320 Bytes
- alle dekomprimierten Bytes sind `0x00`
- SHA-256: `7b6436b0c98f62380866d9432c2af0ee08ce16a171bda6951aecd95ee1307d61`

Der PackBits-Decoder liefert exakt die erwartete Länge und verbraucht den gesamten komprimierten Datenstrom. Ein Decoderfehler ist für diesen Datensatz daher nicht erkennbar. Die aktuelle S/W-Vorschau interpretiert Nullbits als weiße Pixel und zeichnet sie deckend; daraus entsteht das weiße Rechteck.

## 2. Häufigkeit

Im aktuellen Scan der bereitgestellten TOKEN.DB wurden 426 S/W-Moniker-Kandidaten untersucht. Bei 44 davon bestehen die vollständig dekomprimierten Bitmapdaten ausschließlich aus Nullbytes. Diese Kandidaten sind nach dem derzeitigen Decoder also tatsächlich bildinhaltlich leer (alle Bits 0). Das sagt noch nicht, ob sie im ursprünglichen GEOS-Kontext als bewusst leere Platzhalter, Hintergrundflächen oder anderweitig verwendete Moniker gedacht sind.

Die übrigen Moniker werden durch diesen Befund nicht verändert.

## 3. Fenster-ICO: Ursache und Korrektur

Die Anwendung verwendete `sys._MEIPASS/geoworks_motif_icon.ico` als Laufzeitpfad. Der bisherige PyInstaller-Aufruf setzte zwar `--icon` (Icon-Ressource der EXE), nahm die ICO-Datei aber nicht zusätzlich als Datendatei in das One-File-Bundle auf. Dadurch konnte `iconbitmap()` die Datei zur Laufzeit nicht finden; der Fehler wurde durch den vorhandenen TclError-Handler still abgefangen.

Die Build-Batchdatei ergänzt deshalb:

`--add-data "%~dp0geoworks_motif_icon.ico;."`

Damit wird die ICO-Datei in das temporäre One-File-Verzeichnis extrahiert, wo der vorhandene `_MEIPASS`-Pfad sie findet. Der EXE-Ressourcenparameter `--icon` bleibt zusätzlich bestehen.

## 4. Noch zu testen

1. `make_exe.bat` aus dem entpackten Verzeichnis ausführen.
2. Die neu erzeugte `dist\GeoViewPlus.exe` starten.
3. Prüfen, ob das Fenster links oben das GeoWorks-Motif-Icon zeigt.
4. Moniker bei `0x0036DA` und weitere Kandidaten aus der Nullbyte-Liste prüfen.

Die ICO-Korrektur ist eine begründete Build-Fix-Hypothese, aber erst durch den Test der neu gebauten EXE bestätigt.
