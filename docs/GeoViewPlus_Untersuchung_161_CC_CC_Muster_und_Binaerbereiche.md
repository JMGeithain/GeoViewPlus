# Untersuchung 161 – CC-CC-Muster und binäre Bereiche in allen Ressourcen

**Projekt:** GeoViewPlus – Untersuchung echter PC/GEOS-Icons  
**Material:** `BOUNCE.GEO` und `BCOLTEST.GEO` aus Basebox-SVGA-Ensemble12(2).zip  
**Geltungsbereich:** Direkte, ressourcenbegrenzte Byteanalyse der vorliegenden GeoWorks-/PC/GEOS-1.x-Dateien.

## 1. Ziel und Methode

Untersuchung 160 zeigte, dass drei exakte 12-Byte-Folgen nur in Ressource 3 vorkommen. Untersuchung 161 prüft nun das auffällige Bytepaar `CC CC` in allen elf Ressourcen beider Dateien und betrachtet jeweils den lokalen Bytekontext.

Die Suche wurde innerhalb jeder einzelnen Ressource durchgeführt. Ein Treffer wurde nicht über Ressourcengrenzen hinweg gebildet. Bei überlappenden Paaren, etwa `CC CC CC`, werden die Startpositionen der einzelnen Zweibyte-Treffer ausgewiesen.

## 2. Ergebnisübersicht

Die folgenden ressourcenrelativen Startpositionen enthalten `CC CC`:

| Ressource | BOUNCE.GEO | BCOLTEST.GEO |
|---:|---|---|
| 0 | keine | keine |
| 1 | keine | keine |
| 2 | keine | keine |
| 3 | 008Ah, 00B2h, 00CAh, 00EDh, 00EEh, 011Dh, 011Eh, 0175h, 0176h | 0096h, 00BEh, 00D6h, 00F9h, 00FAh, 0129h, 012Ah, 0181h, 0182h |
| 4 | 0132h | 0132h |
| 5 | 0092h | 0092h |
| 6 | 005Dh, 005Eh | 005Dh, 005Eh |
| 7 | keine | keine |
| 8 | 026Dh, 026Eh | 026Dh, 026Eh |
| 9 | 0089h, 008Ah | 0089h, 008Ah |
| 10 | 00D9h, 00DAh | 00D9h, 00DAh |

Die Ressourcen 5–10 sind in beiden Dateien byteidentisch; deshalb stimmen ihre Trefferpositionen überein. Auch Ressource 4 zeigt das Paar an derselben Position.

## 3. Lokale Kontexte

### Ressource 3

In BOUNCE R3 bei `+008Ah`:

```text
08 00 07 00 02 00 CC CC 26 00 00 30 53 00 00 00
```

In BCOLTEST R3 bei `+0096h` steht dieselbe Folge. Das ist die bereits in Untersuchung 159 untersuchte Struktur.

Weitere R3-Treffer stehen in anderen Kontexten, zum Beispiel BOUNCE bei `+00B2h`:

```text
00 00 00 10 00 0C CC CC 10 00 01 00 00 00 00 FF
```

und BOUNCE bei `+00CAh`:

```text
06 00 20 40 04 00 CC CC 21 00 00 30 52 00 00 00
```

Diese Kontexte unterscheiden sich vom ersten Beispiel. Das Bytepaar `CC CC` ist daher nicht auf die eine 12-Byte-Folge aus Untersuchung 159 beschränkt.

### Ressource 4

Beide Dateien enthalten bei R4+`0132h`:

```text
03 10 00 00 00 00 CC CC 0F 00 01 00 00 00 00 FF
```

Das Paar liegt unmittelbar vor dem Längen-WORD des bekannten Textdatensatzes. In BCOLTEST steht an derselben Stelle anstelle von `0F 00` der Wert `1C 00`.

### Ressourcen 5, 6, 8, 9 und 10

Die Treffer liegen überwiegend nahe am Ende der jeweiligen Ressource. Beispiele:

R5+`0092h`:
```text
00 15 55 FE 00 00 CC CC 00 00 00 00 00 00 00 00
```

R6+`005Dh`:
```text
00 F9 00 F9 00 00 CC CC CC
```

R8+`026Dh`:
```text
DD FB 00 E9 DD 00 CC CC CC
```

R9+`0089h`:
```text
00 F9 00 F9 00 00 CC CC CC 00 00 00 00
```

R10+`00D9h`:
```text
DD F9 00 E1 DD 00 CC CC CC 00 00 00 00
```

Bei den Dreierfolgen `CC CC CC` entstehen zwei überlappende Zweibyte-Treffer. Das erklärt die jeweils zwei Startpositionen in der Übersicht.

## 4. Interpretation mit klarer Grenze

**Gesichert:**
1. Das Bytepaar `CC CC` kommt nicht nur in Ressource 3 vor, sondern auch in Ressourcen 4, 5, 6, 8, 9 und 10.
2. Die lokalen Kontexte sind unterschiedlich.
3. In Ressourcen 6, 8, 9 und 10 steht das Paar als Teil einer Dreierfolge `CC CC CC` nahe am Ressourcenende.
4. In Ressource 4 liegt `CC CC` direkt vor dem Längen-WORD des bekannten Textdatensatzes.
5. In Ressource 3 liegt es an mehreren Stellen innerhalb der binären Folge- und Textnachbarbereiche.

**Nicht gesichert:**
- Dass `CC` eine allgemeine Padding-, Füll- oder Ungültigbyte-Konvention in GeoWorks 1.x ist.
- Dass `CC CC` eine Feldmarkierung, ein Sentinel, ein uninitialisierter Wert oder ein bestimmter Datentyp ist.
- Dass alle Vorkommen dieselbe semantische Funktion haben.
- Dass die Ressourcen 6, 8, 9 und 10 Grafiken oder Moniker enthalten, nur weil die Bytes am Ende wiederholt auftreten.

Das Bytepaar kann daher als Suchmerkmal dienen, aber nicht als Typkennung.

## 5. Abgleich mit den drei 12-Byte-Folgen aus Untersuchung 159

Die drei exakten 12-Byte-Folgen aus Untersuchung 159 wurden in dieser Runde nicht neu semantisch interpretiert. Die exakte Suche aus Untersuchung 160 bleibt gültig: Die drei vollständigen Folgen sind nur in Ressource 3 gefunden worden. Das häufigere Auftreten von `CC CC` in anderen Ressourcen bedeutet nicht, dass dort dieselbe 12-Byte-Struktur vorliegt.

## 6. Konsequenz für GeoViewPlus

Keine Codeänderung. Ein Parser darf `CC CC` nicht als alleinige Signatur eines Datensatztyps verwenden. Bei späteren Strukturtests muss das Bytepaar zusammen mit Feldposition, Ressourcengrenze und Nachbarbytes betrachtet werden.

Nächster sinnvoller Schritt: Die übrigen Ressourcen 5–10 unabhängig von `CC CC` auf Endbereiche, Nullfolgen, Längenfelder und wiederkehrende Blockmuster untersuchen. Dabei ist zwischen Nutzdaten und möglichem Abschluss-/Ausrichtungsbereich zu unterscheiden, ohne eine Bedeutung vorwegzunehmen.

## 7. Integrität

- Beide GEO-Dateien ausschließlich lesend untersucht.
- Treffer ressourcenrelativ und innerhalb der Ressourcengrenzen ermittelt.
- Keine Originaldatei verändert.
- Kein GeoViewPlus-Programmcode geändert.
- Keine Icon-/Moniker-Zuordnung vorgenommen.
