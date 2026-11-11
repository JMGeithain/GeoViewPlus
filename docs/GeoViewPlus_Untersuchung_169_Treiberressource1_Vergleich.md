# Untersuchung 169 – Vergleich von Treiber-Ressource 1 mit der Texttabellen-Ressource 2

**Projekt:** GeoViewPlus – Untersuchung echter PC/GEOS-Icons  
**Material:** `BB120_64.GEO`, `BB72_64.GEO`, `BB96_64.GEO`, `S16_1280.GEO`, `V16_0720.GEO`  
**Geltungsbereich:** Direkte Byte- und Geode-Tabellenbefunde an fünf GeoWorks-/PC/GEOS-1.x-Treibern.  
**Ziel:** Prüfen, ob die in Ressource 2 nachgewiesene 36-WORD-Offsetliste mit Textdatensätzen auch in Ressource 1 oder in dessen Anfangsbereich vorkommt.

## 1. Ressourcentabelle

Alle fünf Dateien besitzen drei Ressourcen. Die relevanten Metadaten:

| Datei | R1-Größe | R1-Relokationsbytes | R1-Flags | R2-Größe | R2-Relokationsbytes | R2-Flags |
|---|---:|---:|---:|---:|---:|---:|
| BB120_64.GEO | 32622 | 288 | 0080h | 1776 | 4 | 097Ah |
| BB72_64.GEO | 32622 | 288 | 0080h | 1776 | 4 | 097Ah |
| BB96_64.GEO | 32622 | 288 | 0080h | 1776 | 4 | 097Ah |
| V16_0720.GEO | 32576 | 288 | 0080h | 1776 | 4 | 097Ah |
| S16_1280.GEO | 26368 | 288 | 0080h | 1776 | 4 | 097Ah |

Die Ressourcengrößen und Relokationslängen stammen aus den Geode-Ressourcentabellen. Die Ressource 1 besitzt in allen fünf Dateien 288 Relokationsbytes, also 72 Vier-Byte-Relokationseinträge. Ressource 2 besitzt jeweils vier Relokationsbytes, also einen Eintrag.

Die Flags werden hier nur als Rohwerte dokumentiert. Die Untersuchung leitet daraus keine zusätzliche semantische Bezeichnung ab.

## 2. Ressource 1 beginnt nicht mit der Text-Offsetliste

Der Anfang von Ressource 1 besteht in allen fünf Dateien aus 64 Nullbytes. Der erste nichtnull Bytewert liegt bei Ressourcenoffset `+40h`.

Ab dort folgen binäre Werte, keine 36-WORD-Folge der in Ressource 2 ermittelten Offsets. Die genaue Interpretation dieser Binärbereiche ist nicht Gegenstand dieser Untersuchung.

Eine gezielte Suche nach den ersten fünf WORD-Werten der Ressource-2-Tabelle (`006A 009A 00CA 00FA 012A`) als zusammenhängende Little-Endian-Sequenz ergab in Ressource 1 jeder der fünf Dateien keinen Treffer.

Das schließt nicht aus, dass Ressource 1 andere Tabellen oder indirekte Referenzen enthält. Es belegt nur, dass die bekannte Offsetfolge nicht als identische zusammenhängende Bytefolge in Ressource 1 vorliegt.

## 3. Unterschiede zwischen den fünf Ressource-1-Inhalten

Die Ressource 1 ist nicht in allen fünf Treibern byteidentisch:

- BB120_64, BB72_64 und BB96_64 besitzen jeweils 32.622 Bytes. Zwischen BB120_64 und BB72_64 sowie zwischen BB120_64 und BB96_64 unterscheiden sich im direkten Bytevergleich jeweils vier Positionen.
- V16_0720 besitzt 32.576 Bytes und unterscheidet sich in Größe und Inhalt von BB120_64.
- S16_1280 besitzt 26.368 Bytes. Im gemeinsamen Längenbereich unterscheiden sich gegenüber BB120_64 nur acht Bytepositionen; die Ressource ist jedoch um 6.254 Bytes kürzer.

Diese Bytevergleiche sind keine semantische Dekodierung. Sie zeigen lediglich, dass die Treiber eine weitgehend gemeinsame Ressource 1 besitzen, die an wenigen bzw. je nach Treiberfamilie umfangreicheren Stellen variiert.

## 4. Gegenüberstellung mit Ressource 2

Ressource 2 ist in allen fünf Dateien exakt 1.776 Bytes groß. Ihre 36-WORD-Offsetliste, die Textdatensatz-Längenfelder und die Textziele wurden in Untersuchungen 167 und 168 rekonstruiert.

Ressource 1 unterscheidet sich deutlich:
- Sie ist wesentlich größer.
- Sie besitzt 72 Relokationseinträge statt eines.
- Die bekannte 36-WORD-Offsetfolge aus Ressource 2 wurde in ihr nicht als zusammenhängende Sequenz gefunden.
- Ihr Anfang zeigt ab +40h binäre Daten statt der nachgewiesenen Textdatensatz-Ziele.

Das ist mit einer anderen Ressourcenfunktion vereinbar. Eine vollständige Funktionsbestimmung von Ressource 1 ist damit nicht erreicht.

## 5. Gesicherte Ergebnisse

1. Ressource 1 ist in allen fünf Treibern deutlich größer als Ressource 2.
2. Ressource 1 besitzt in allen fünf Dateien 288 Relokationsbytes (72 Vier-Byte-Einträge).
3. Ressource 2 besitzt jeweils vier Relokationsbytes (einen Eintrag).
4. Die bekannte 36-WORD-Offsetfolge aus Ressource 2 kommt in Ressource 1 nicht als identische zusammenhängende Folge vor.
5. Die Ressource-1-Inhalte der fünf Treiber sind nicht vollständig identisch; drei Basebox-Varianten sind bis auf vier Bytepositionen identisch, S16_1280 weicht an acht Positionen im gemeinsamen Bereich ab und ist deutlich kürzer, V16_0720 ist ebenfalls kürzer und unterscheidet sich umfangreicher.

## 6. Noch offen

- Ob Ressource 1 überwiegend Code, Daten oder eine Mischung enthält.
- Welche konkreten Strukturen durch ihre 72 Relokationseinträge adressiert werden.
- Ob in Ressource 1 andere Tabellen mit indirekten oder anders kodierten Referenzen liegen.
- Welche semantische Rolle Ressource 2 und Ressource 1 im Treiber-Laufzeitmodell genau haben.
- Ob eine dieser Ressourcen Icon-/Moniker-Daten enthält. Dafür liegt hier kein positiver Nachweis vor.

## 7. Konsequenz für GeoViewPlus

Die bekannte 36er-Offset-/Textdatensatzstruktur darf nicht auf Ressource 1 übertragen werden. Die Ressourcentyp-Klassifizierung muss auf mehreren Merkmalen beruhen, unter anderem Größe, Relokationsumfang, Headerwerte und validierte interne Strukturen.

Keine Codeänderung. Keine Icon- oder Moniker-Zuordnung. Ressource 1 bleibt ein eigener, noch nicht vollständig dekodierter Untersuchungsgegenstand.

## 8. Integrität und Versionsgrenze

- Fünf GEO-Dateien ausschließlich lesend untersucht.
- Keine Originaldatei verändert.
- Kein GeoViewPlus-Programmcode geändert.
- Keine PC/GEOS-2.x-Struktur als Beleg für GeoWorks 1.x verwendet.
