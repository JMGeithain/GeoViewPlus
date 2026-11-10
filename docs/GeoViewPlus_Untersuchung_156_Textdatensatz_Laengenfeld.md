# Untersuchung 156 – Längenfeld der Textdatensätze in Ressourcen 3 und 4

**Projekt:** GeoViewPlus – Untersuchung echter PC/GEOS-Icons  
**Material:** `BOUNCE.GEO` und `BCOLTEST.GEO` aus Basebox-SVGA-Ensemble12(2).zip  
**Geltungsbereich:** Direkte Bytebefunde an den vorliegenden GeoWorks-/PC/GEOS-1.x-Dateien.

## 1. Fragestellung

Untersuchung 155 hatte ein WORD unmittelbar vor dem wiederkehrenden Textpräfix `01 00 00 00 00 FF` festgestellt. In Ressource 4 lag es bei `+134h`, also direkt vor dem Präfix bei `+136h`. Die Werte waren `000Fh` in BOUNCE und `001Ch` in BCOLTEST. Zu prüfen war, ob dieses WORD die Länge des Textdatensatzes angibt.

## 2. Prüfmethode

Für jeden erkannten Textdatensatz wurden gezählt:
- 2 Bytes für das Längen-WORD,
- 6 Bytes für das wiederkehrende Präfix `01 00 00 00 00 FF`,
- die Textbytes,
- 1 Byte für den abschließenden Nullterminator.

Die Summe wurde mit dem unmittelbar vor dem Präfix gespeicherten WORD verglichen.

## 3. Ergebnisse

| Datei / Ressource | Text | Textbytes ohne Nullbyte | WORD vor Präfix | Berechnete Gesamtlänge |
|---|---|---:|---:|---:|
| BOUNCE / R3 | Bounce | 6 | 000Fh = 15 | 2 + 6 + 6 + 1 = 15 |
| BOUNCE / R3 | Status: | 7 | 0010h = 16 | 2 + 6 + 7 + 1 = 16 |
| BOUNCE / R3 | On | 2 | 000Bh = 11 | 2 + 6 + 2 + 1 = 11 |
| BOUNCE / R3 | Off | 3 | 000Ch = 12 | 2 + 6 + 3 + 1 = 12 |
| BCOLTEST / R3 | RGB565 colour proof | 19 | 001Ch = 28 | 2 + 6 + 19 + 1 = 28 |
| BCOLTEST / R3 | Status: | 7 | 0010h = 16 | 2 + 6 + 7 + 1 = 16 |
| BCOLTEST / R3 | On | 2 | 000Bh = 11 | 2 + 6 + 2 + 1 = 11 |
| BCOLTEST / R3 | Off | 3 | 000Ch = 12 | 2 + 6 + 3 + 1 = 12 |
| BOUNCE / R4 | Bounce | 6 | 000Fh = 15 | 2 + 6 + 6 + 1 = 15 |
| BCOLTEST / R4 | RGB565 colour proof | 19 | 001Ch = 28 | 2 + 6 + 19 + 1 = 28 |

Alle zehn geprüften Fälle stimmen exakt überein.

## 4. Rohdatenbeispiel aus Ressource 4

BOUNCE, Ressource 4, ab Offset `+12Ah`:

```text
24 00 03 10 00 00 00 00 CC CC
0F 00
01 00 00 00 00 FF
42 6F 75 6E 63 65 00
```

Das Längen-WORD `000Fh` steht unmittelbar vor dem sechs Byte langen Präfix. Die Länge ab dem Längen-WORD bis einschließlich Nullterminator beträgt genau 15 Bytes.

BCOLTEST, gleicher Bereich:

```text
24 00 03 10 00 00 00 00 CC CC
1C 00
01 00 00 00 00 FF
52 47 42 35 36 35 20 63 6F 6C 6F 75 72 20 70 72 6F 6F 66 00
```

Das WORD `001Ch` entspricht genau 28 Bytes: 2 + 6 + 19 + 1.

## 5. Ergebnis und Status

**Gesichert:** Das WORD unmittelbar vor dem Präfix gibt bei allen zehn untersuchten Textdatensätzen die Gesamtlänge des Datensatzes an, gerechnet ab dem Längen-WORD selbst und einschließlich des abschließenden Nullbytes.

Formel:

```text
record_length = 2 + 6 + text_byte_length + 1
```

Oder allgemeiner: Die gespeicherte Länge ist die Anzahl der Bytes vom Längen-WORD bis zum Ende des nullterminierten Textdatensatzes.

**Noch nicht gesichert:** Die Bedeutung der sechs Präfixbytes selbst, die Semantik der zehn Bytes vor dem Längen-WORD in Ressource 4 und die Funktion der weiteren binären Felder. Ebenso ist nicht bewiesen, dass alle anderen Tabellenziele dieselbe Datensatzart adressieren.

## 6. Konsequenz für GeoViewPlus

Dieser Befund erlaubt einen sicheren, eng begrenzten Parserbaustein: Wenn ein Textdatensatz dieses bekannten Präfixmusters erkannt wurde, kann das vorangehende WORD als Datensatzlänge geprüft werden. Die Prüfung sollte die Ressourcengrenze beachten und den Nullterminator innerhalb der angegebenen Länge verlangen.

Noch keine Änderung am Programmcode. Zunächst weitere Datensatztypen und Grenzfälle untersuchen.

## 7. Integrität

- GEO-Dateien ausschließlich lesend aus dem ZIP-Archiv untersucht.
- Keine Originaldatei verändert.
- Kein GeoViewPlus-Programmcode geändert.
- Keine Moniker-/Icon-Klassifizierung vorgenommen.
