# Untersuchung 155 – Textdatensatz-Präfixe und überlappende Tabellenziele

**Projekt:** GeoViewPlus – Untersuchung echter PC/GEOS-Icons  
**Material:** `BOUNCE.GEO` und `BCOLTEST.GEO` aus Basebox-SVGA-Ensemble12(2).zip  
**Geltungsbereich:** Bytebefunde an den vorliegenden GeoWorks-/PC/GEOS-1.x-Dateien. Keine Ableitung aus PC/GEOS 2.x oder FreeGEOS.

## 1. Anlass und Korrektur

Die Untersuchung 154 beschrieb Tabellenziele in den Ressourcen 3 und 4. Beim erneuten vollständigen Auslesen der Ressourcen ist eine Präzisierung nötig: Nicht jeder Tabellenwert markiert zwingend den Anfang eines eigenständigen Datensatzes. Einige Ziele liegen innerhalb eines bereits begonnenen zusammenhängenden Datenbereichs. Die Tabelle muss daher als Sammlung von Offsets mit möglicherweise überlappenden Zielbereichen behandelt werden.

## 2. Wiederkehrendes Textpräfix in Ressource 3

An den Textanfängen der Ressource 3 steht in beiden Dateien ein sechs Byte langes Präfix:

```text
01 00 00 00 00 FF
```

Direkt danach folgt nullterminierter ASCII-Text.

Beispiele aus den tatsächlichen Ressource-Bytes:

**BOUNCE.GEO, Ressource 3, Offset 0072h**
```text
01 00 00 00 00 FF 42 6F 75 6E 63 65 00
                  B  o  u  n  c  e  00
```

**BOUNCE.GEO, Ressource 3, Offset 00B6h**
```text
01 00 00 00 00 FF 53 74 61 74 75 73 3A 00
                  S  t  a  t  u  s  :  00
```

**BCOLTEST.GEO, Ressource 3, Offset 0072h**
```text
01 00 00 00 00 FF 52 47 42 35 36 35 20 63 6F 6C 6F 75 72 20 70 72 6F 6F 66 00
                  R  G  B  5  6  5     c  o  l  o  u  r     p  r  o  o  f  00
```

Weitere Textanfänge:
- BOUNCE: `00F2h` = `On`, `0122h` = `Off`.
- BCOLTEST: `00FEh` = `On`, `012Eh` = `Off`.

Der Befund belegt das wiederkehrende Bytepräfix und die nachfolgende Textdarstellung. Er belegt nicht, ob das Präfix eine Typkennung, ein String-Attribut, ein Objektfeld oder etwas anderes ist.

## 3. Überlappende Ziele in Ressource 3

Die Tabelle in BOUNCE Ressource 3 enthält unter anderem `0072h` und `0082h`. Der erste Offset zeigt auf den Anfang des Textdatensatzes `Bounce`. Der zweite Offset liegt bereits zehn Bytes später, innerhalb des Bereichs, der bei `0072h` beginnt beziehungsweise unmittelbar in dessen anschließenden Daten übergeht.

Die Bytes ab `0072h` lauten:

```text
01 00 00 00 00 FF 42 6F 75 6E 63 65 00 CC 0A 00
41 40 08 00 07 00 02 00 CC CC 26 00 00 30 53 00
...
```

Damit ist `0082h` kein zweiter Textanfang mit dem gleichen Präfix. Es liegt im nachfolgenden Datenbereich. Gleiches Prinzip ist in BCOLTEST zu beachten: Die Einträge `0072h` und `008Eh` liegen in benachbarten beziehungsweise übergehenden Bereichen, nicht alle Ziele sind gleichartige Textdatensatzstarts.

Folgerung: Ein Parser darf nicht einfach für jeden Tabellenoffset die sechs Präfixbytes erwarten. Er muss zunächst die jeweilige Zielposition und ihre Beziehung zu anderen Tabellenzielen untersuchen.

## 4. Ressource 4: Textbeginn und vorgelagerter Bereich

Ressource 4 enthält in beiden GEO-Dateien dieselbe WORD-Tabelle:

```text
002E 0036 00FE 012A 0136 0000
```

Bei `0136h` beginnt jeweils ein Textdatensatz mit dem bekannten Präfix:
- BOUNCE: `01 00 00 00 00 FF 42 6F 75 6E 63 65 00`
- BCOLTEST: `01 00 00 00 00 FF 52 47 42 35 36 35 20 63 6F 6C 6F 75 72 20 70 72 6F 6F 66 00`

Der Tabellenwert `012Ah` liegt sechs WORDs beziehungsweise zwölf Bytes vor `0136h`. Der Bereich ab `012Ah` enthält vor dem Textbeginn zusätzliche Bytes:

BOUNCE:
```text
24 00 03 10 00 00 00 00 CC CC 0F 00
01 00 00 00 00 FF 42 6F 75 6E 63 65 00
```

BCOLTEST:
```text
24 00 03 10 00 00 00 00 CC CC 1C 00
01 00 00 00 00 FF 52 47 42 35 36 35 20 63 6F 6C 6F 75 72 20 70 72 6F 6F 66 00
```

Die zwölf Bytes vor dem Text unterscheiden sich an einer Stelle (BOUNCE: `0F 00`; BCOLTEST: `1C 00`). Das ist ein konkreter programmspezifischer Unterschied. Ob dieses WORD die Textlänge, eine Größe, einen Typwert oder etwas anderes darstellt, ist noch offen. Es darf vorerst nicht als Längenfeld benannt werden.

## 5. Was wir daraus ableiten dürfen

**Gesichert:**
1. An mehreren Textanfängen in Ressource 3 und Ressource 4 steht das Präfix `01 00 00 00 00 FF`.
2. Direkt danach folgt nullterminierter ASCII-Text.
3. Die Tabellenwerte können auf Textanfänge, auf binäre Nachbarbereiche oder mitten in einen zusammenhängenden Datenbereich zeigen.
4. In Ressource 4 liegt der Tabellenwert `012Ah` genau zwölf Bytes vor dem Textanfang `0136h`.
5. Das WORD bei `012Ah + 0Ah` unterscheidet sich zwischen den Dateien: `000Fh` bei BOUNCE und `001Ch` bei BCOLTEST.

**Nicht gesichert:**
- Die Semantik des sechs Byte langen Textpräfixes.
- Die Bedeutung der zwölf Bytes vor dem Text in Ressource 4.
- Ob die unterschiedlichen Tabellenziele Objekte, Teilobjekte, Stringfelder, Moniker oder LMem-Chunks adressieren.
- Ob ein Tabellenwert eine Handle-Speicherstelle oder einen direkten Datenoffset bezeichnet.

## 6. Konsequenz für den Parser

Keine Änderung am GeoViewPlus-Code. Die Untersuchung zeigt, dass ein vorschneller Parser, der jedes Tabellenziel als Datensatzanfang behandelt, falsch klassifizieren könnte.

Vor einer Implementierung müssen die Ressourcendaten in Intervallen und Feldgrenzen modelliert werden. Für Ressource 4 ist insbesondere der zwölf Byte lange Bereich vor dem Textanfang `0136h` gemeinsam mit dem Textdatensatz zu untersuchen.

## 7. Integrität

- GEO-Dateien ausschließlich lesend untersucht.
- Keine Originaldatei verändert.
- Kein Programmcode geändert.
- Keine Icon-/Moniker-Klassifizierung vorgenommen.
