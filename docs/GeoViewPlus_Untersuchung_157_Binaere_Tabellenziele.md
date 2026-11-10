# Untersuchung 157 – Binäre Tabellenziele in Ressourcen 3 und 4

**Projekt:** GeoViewPlus – Untersuchung echter PC/GEOS-Icons  
**Material:** `BOUNCE.GEO` und `BCOLTEST.GEO` aus Basebox-SVGA-Ensemble12(2).zip  
**Geltungsbereich:** Bytebefunde der vorliegenden GeoWorks-/PC/GEOS-1.x-Dateien.

## 1. Ziel

Nach dem Nachweis des Längen-WORDs bei bekannten Textdatensätzen werden die übrigen Tabellenziele in Ressourcen 3 und 4 betrachtet. Gesucht sind wiederkehrende Muster, die eine vorsichtige Trennung von Textdatensätzen und anderen binären Daten erlauben.

## 2. Referenz: bestätigtes Textdatensatzmuster

Für die untersuchten Textdatensätze gilt:

```text
WORD Gesamtlänge
01 00 00 00 00 FF
ASCII-Text
00
```

Die Länge umfasst das Längen-WORD, das sechs Byte lange Präfix, die Textbytes und den Nullterminator. Dieses Muster wurde für die in Untersuchung 156 aufgeführten zehn Fälle geprüft.

## 3. Ressource 3 – Nicht-Textziele

Die Tabellen in Ressource 3 unterscheiden sich in einzelnen Offsets zwischen BOUNCE und BCOLTEST. Gemeinsam ist ihnen unter anderem:
- `003Eh`
- `FFFFh` als Sonderwert
- `004Eh`
- `0072h`
- weitere Ziele vor den Textdatensätzen und zwischen den Textdatensätzen
- `0000h` als letzter Tabelleneintrag

Die Bytes ab `003Eh` beginnen in beiden Dateien mit:

BOUNCE und BCOLTEST:
```text
00 02 03 02 02 07 02 02 07 02 07 02 07 00
23 00 00 30 ...
```

Ab `004Eh` unterscheiden sich die folgenden Bytes bereits zwischen den Dateien. BOUNCE enthält dort unter anderem `2A 00 00 40`, BCOLTEST `38 00 00 40`. Das ist ein Hinweis auf variable binäre Inhalte, aber noch keine identifizierte Feldbedeutung.

Einige Tabellenziele zeigen nicht auf den Anfang des bekannten Textdatensatzmusters. Beispielsweise beginnt BOUNCE R3 bei `0082h` mit `41 40 08 00 07 00 02 00...`; BCOLTEST R3 hat an `008Eh` einen vergleichbaren binären Bereich. Diese Ziele sind daher nicht als Textdatensatzstarts zu klassifizieren.

## 4. Ressource 3 – Textdatensätze und ihre Längen

Die direkt im Ressourceninhalt erkannten Textanfänge sind:

| Datei | Offset | Text | Längen-WORD |
|---|---:|---|---:|
| BOUNCE | 0072h | Bounce | 000Fh |
| BOUNCE | 00B6h | Status: | 0010h |
| BOUNCE | 00F2h | On | 000Bh |
| BOUNCE | 0122h | Off | 000Ch |
| BCOLTEST | 0072h | RGB565 colour proof | 001Ch |
| BCOLTEST | 00C2h | Status: | 0010h |
| BCOLTEST | 00FEh | On | 000Bh |
| BCOLTEST | 012Eh | Off | 000Ch |

Jeder Eintrag erfüllt das in Abschnitt 2 beschriebene Längenmuster. Andere Tabellenziele in der Nähe zeigen dagegen auf binäre Folgefelder oder in deren Mitte.

## 5. Ressource 4 – Binärziele

Die Tabelle lautet in beiden Dateien:

```text
002E 0036 00FE 012A 0136 0000
```

Die Ziele `002Eh` und `0036h` beginnen mit binären Daten. Beispielsweise:

```text
R4 +002E:
00 03 02 02 02 00 C8 00 00 30 47 00 ...
```

Das Ziel `00FEh` liegt in einem längeren binären Bereich. Dort sind wiederkehrende Werte und Muster sichtbar, aber aus den Bytes allein kann kein belastbarer Typname abgeleitet werden.

Der Eintrag `012Ah` zeigt auf einen zwölf Byte langen Vorspann, der direkt vor dem bekannten Textdatensatz beginnt. Bei `0136h` beginnt der Textdatensatz selbst. Die zwölf Bytes bei `012Ah` lauten:

BOUNCE:
```text
24 00 03 10 00 00 00 00 CC CC 0F 00
```

BCOLTEST:
```text
24 00 03 10 00 00 00 00 CC CC 1C 00
```

Die letzten beiden Bytes dieses Vorspanns sind das bereits nachgewiesene Längen-WORD. Die ersten zehn Bytes sind weiterhin nicht semantisch entschlüsselt.

## 6. Ergebnis

**Gesichert:**
1. Das bekannte Textdatensatzformat lässt sich in Ressourcen 3 und 4 wiedererkennen.
2. Die übrigen Tabellenziele zeigen teilweise auf binäre Datenbereiche und nicht auf Textdatensatzanfänge.
3. Ressource 3 enthält unterschiedliche binäre Bytes in BOUNCE und BCOLTEST, obwohl Teile des Tabellen- und Ressourcenaufbaus vergleichbar sind.
4. In Ressource 4 liegen `002Eh`, `0036h` und `00FEh` in binären Bereichen; `012Ah` zeigt auf den Vorspann des Textdatensatzes, `0136h` auf dessen Anfang.

**Nicht gesichert:**
- Ob die binären Bereiche Objektbeschreibungen, Moniker, Grafiken, LMem-Chunks oder andere Ressourcenstrukturen enthalten.
- Die Feldbedeutung der Bytes an `003Eh`, `004Eh`, `002Eh`, `0036h` und `00FEh`.
- Ob die Tabellenwerte direkte Offsets oder über eine weitere Ebene zu interpretierende Referenzen sind.

## 7. Konsequenz für GeoViewPlus

Noch keine Implementierung. Ein künftiger Parser darf nur das verifizierte Textdatensatzmuster als solches klassifizieren. Alle anderen Ziele müssen bis zu einer eigenständigen Strukturidentifikation als unbekannte binäre Bereiche erhalten bleiben.

Die nächste Untersuchung sollte die wiederkehrenden binären Muster in Ressource 3 und 4 über beide Dateien hinweg vergleichen, ohne sie vorzeitig als Icons oder Moniker zu benennen.

## 8. Integrität

- Beide GEO-Dateien nur lesend aus dem ZIP-Archiv gelesen.
- Keine Originaldatei verändert.
- Kein GeoViewPlus-Programmcode geändert.
- Keine Icon-Extraktion oder Moniker-Zuordnung vorgenommen.
