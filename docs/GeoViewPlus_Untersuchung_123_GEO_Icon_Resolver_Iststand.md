# GeoViewPlus – Untersuchung 123: Ist-Stand der GEO-Icon-Ermittlung und nächste Ressourcenanalyse

**Datum:** 10. November 2026  
**Zielgeneration:** ausschließlich GeoWorks / PC/GEOS 1.x für die neue Ressourcenanalyse

## 1. Geprüfte Quelltextbasis

Geprüft wurde der Quelltext `GeoViewPlus.py` aus dem bereitgestellten Gesamtpaket `GeoViewPlus_0.4.4.1_JME_Logo_Layoutfix.zip`. Diese Untersuchung beschreibt diesen konkreten Paketstand; sie behauptet nicht, dass damit alle späteren lokalen Entwicklungsstände erfasst sind.

## 2. Tatsächlicher Ablauf in `load_file()`

Der aktuelle Code liest beim Öffnen zunächst nur:

```python
data = file_data[:4096]  # header + icon parsing
```

Danach wird `parse_geos_header(data)` aufgerufen. Für `TOKEN.DB` wird anschließend der vollständige Dateiinhalt an `scan_token_db_monikers(file_data)` übergeben. Das ist der Grund, weshalb die Galerie die Moniker-Fundstellen der gesamten Token-Datenbank finden kann.

Bei normalen GEO-Dateien wird das links angezeigte Bild jedoch nicht aus der GEO-Datei extrahiert. Der Code ruft stattdessen auf:

```python
self.icon_image = get_token_icon_image(token)
```

Diese Funktion liest aus dem statischen Python-Dictionary `TOKEN_ICONS` (unter anderem WP00, WDAT, DP00, GEOS und Fallback). Das ist eine Token-Vorschau aus eingebetteten PNG-Daten, keine nachgewiesene Extraktion der tatsächlichen Moniker-Ressource aus der gerade geöffneten GEO-Datei.

## 3. Was der vorhandene Moniker-Scanner leistet – und was nicht

`scan_token_db_monikers()` durchsucht den übergebenen Bytebereich nach strukturellen Kandidaten. Es prüft Moniker-Typ, Maße, GString-Opcode `0x1A`, Bitmap-Header, Kompression und die exakt erwartete PackBits-Ausgabelänge.

Der Scanner stellt derzeit ausdrücklich keine Verbindung her zwischen:
- Token-Chunk bzw. Token-Namen,
- VM-Datei-Ressource,
- Chunk-Referenz,
- Moniker-Objekt,
- Rolle als Programm- oder Dokument-Icon.

Die Galerie kennzeichnet diese Einschränkung bereits. Ein Kandidat mit passender Größe oder Farbtiefe darf deshalb nicht als das tatsächlich verwendete Programm-Icon ausgegeben werden.

## 4. Zentrale Lücke

Die fehlende Stufe ist kein weiterer Pixel-Decoder, sondern ein **GeoWorks-1.x-VM-/Ressourcen-Resolver**. Er muss die auf der Festplatte gespeicherten VM-Dateistrukturen und ihre Referenzen auswerten, statt beliebige Bytefolgen global zu scannen.

Die belastbare Beweiskette soll lauten:

1. GeoWorks-1.x-Dateisignatur und Header aus der vollständigen Datei lesen.
2. VM-Dateikennung und VM-Struktur erkennen.
3. VM-Header, Block-/Resource-Directory und zugehörige Tabellen nach dem tatsächlichen 1.x-Layout dekodieren.
4. Resource-/Chunk-Referenzen mit ihren Datei-Offsets und Größen nachvollziehen.
5. Token- und Moniker-Referenz innerhalb der passenden Ressource verfolgen.
6. Zielobjekt als Moniker/GString/Bitmap strukturell validieren.
7. Programm-Icon und Dokument-Icon nur anhand der referenzierenden Objekt-/Token-Rolle unterscheiden.
8. Originaldaten unverändert dekodieren und mit Quellhash, Ressourcen-ID, Chunk-ID, Token und Bytebereich dokumentieren.

Jeder Schritt benötigt mindestens einen konkreten Offset- und Referenznachweis aus einer echten GeoWorks-1.x-Datei. Unbekannte Felder bleiben zunächst unbenannt, bis ihre Funktion belegt ist.

## 5. Konkrete Befunde am 0.4.4.1-Quelltext

| Bereich | Ist-Zustand |
|---|---|
| Header-Parsing | `parse_geos_header()` erhält beim normalen Öffnen nur die ersten 4096 Bytes |
| TOKEN.DB | Spezialerkennung über Dateiname/Signatur und VM-Marker; danach Scan der gesamten Datei |
| Moniker-Fundstellen | Strukturell validierter Byte-Scan |
| Token-Zuordnung | Keine VM-/Chunk-Referenzauflösung |
| GEO-Programm-Icon | Statische Token-Tabelle / Fallback |
| Dokument-Icon | Keine belastbare automatische Zuordnung |
| Cache | Kein nachgewiesener Ressourcen-/Dokument-Icon-Cache |

## 6. Nächster Arbeitsschritt

Als nächstes wird eine konkrete GeoWorks-1.x-Datei (vorzugsweise `GEODEXGC.GEO` und/oder die passende `TOKEN.DB`) als Referenzfall verwendet. Die Datei wird bytegenau untersucht, um zuerst den VM-Header und die Resource-/Chunk-Directory-Struktur zu lokalisieren und zu validieren. Erst danach werden einzelne Token-Referenzen verfolgt.

Die erforderlichen Originaldateien müssen aus dem Nutzerarchiv `GEOWORKS.zip` entnommen werden. Der hier untersuchte Programm-ZIP enthält diese GeoWorks-Originaldateien nicht.

## 7. Strikte Abgrenzung

- Keine Übernahme von PC/GEOS 2.x-/FreeGEOS-Strukturen als Beleg für GeoWorks 1.x.
- Keine Änderungen an Originaldateien.
- Keine Icon-Zuordnung allein aufgrund von Ähnlichkeit, Bildgröße oder Farbtiefe.
- Keine Behauptung einer echten GEO-Icon-Extraktion, solange die Ressourcenreferenz nicht nachgewiesen ist.
