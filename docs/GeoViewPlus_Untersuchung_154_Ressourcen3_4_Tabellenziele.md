# Untersuchung 154 – Tabellenziele in den Ressourcen 3 und 4

**Projekt:** GeoViewPlus – Untersuchung echter PC/GEOS-Icons  
**Dateien:** `BOUNCE.GEO` und `BCOLTEST.GEO` aus Basebox-SVGA-Ensemble12(2).zip  
**Geltungsbereich:** Bytebefunde an den vorliegenden GEOS-1.x-Dateien. Keine Übertragung von PC/GEOS 2.x-/FreeGEOS-Strukturen.

## 1. Fragestellung

Die Untersuchung verfolgt die Einträge der WORD-Tabelle ab Ressourcenoffset `+20h` in Ressource 3 und 4. Ziel ist festzustellen, welche Inhalte an den angegebenen Offsets tatsächlich liegen. Die Tabellenwerte werden zunächst nur als Offsets behandelt; ihre semantische Bedeutung ist nicht vorausgesetzt.

## 2. Ressource 3

In beiden GEO-Dateien enthält Ressource 3 eine Tabelle mit 14 WORD-Einträgen ab `+20h`.

BOUNCE.GEO:
```text
003E FFFF 004E 0072 0082 008E 00B6
00C6 00CE 00F2 00FE 0122 012E 0000
```

BCOLTEST.GEO:
```text
003E FFFF 004E 0072 008E 009A 00C2
00D2 00DA 00FE 010A 012E 013A 0000
```

An mehreren Zielpositionen liegen klar erkennbare Textdatensätze. Beispiele:

| Datei | Zieloffset | Bytes ab Zieloffset | Erkennbarer Text |
|---|---:|---|---|
| BOUNCE | 0072h | `01 00 00 00 00 FF 42 6F 75 6E 63 65 00` | Bounce |
| BOUNCE | 00B6h | `01 00 00 00 00 FF 53 74 61 74 75 73 3A 00` | Status: |
| BOUNCE | 00F2h | `01 00 00 00 00 FF 4F 6E 00` | On |
| BOUNCE | 0122h | `01 00 00 00 00 FF 4F 66 66 00` | Off |
| BCOLTEST | 0072h | Text beginnt nach `01 00 00 00 00 FF` | RGB565 colour proof |
| BCOLTEST | 00C2h | Text beginnt nach `01 00 00 00 00 FF` | Status: |
| BCOLTEST | 00FEh | Text beginnt nach `01 00 00 00 00 FF` | On |
| BCOLTEST | 012Eh | Text beginnt nach `01 00 00 00 00 FF` | Off |

Damit ist direkt belegt, dass zumindest einige Tabellenziele auf Datensätze mit einem wiederkehrenden sechs Byte langen Präfix und anschließendem nullterminiertem Text zeigen.

Andere Ziele führen in binäre Bereiche, beispielsweise `003E`, `004E`, `0082`, `008E` und `00CE` in BOUNCE. Diese enthalten keine unmittelbar lesbaren Textanfänge und werden hier nicht ohne weitere Strukturkenntnis als Icons, Moniker oder LMem-Chunks klassifiziert.

Der Eintrag `FFFFh` ist ein Sonderwert und kein gültiger Offset innerhalb der Ressource. Der abschließende Eintrag `0000h` zeigt auf den Ressourcenanfang, also auf den dortigen Ressourcen-/Heap-Präfix. Ob dies ein Null-/Sentinel-Eintrag oder eine gültige Sonderreferenz ist, bleibt offen.

## 3. Ressource 4

Ressource 4 enthält in beiden Dateien sechs WORD-Einträge:

```text
002E 0036 00FE 012A 0136 0000
```

Die Ziele zeigen auf unterschiedliche Arten von Daten:
- `002Eh` und `0036h` liegen in einem binären Bereich mit wiederkehrenden WORD-/BYTE-Feldern.
- `00FEh` liegt in einem längeren binären Bereich, der sich nicht allein aus den Bytes als Moniker identifizieren lässt.
- `012Ah` liegt unmittelbar vor einem wiederkehrenden Textdatensatz-Präfix.
- `0136h` zeigt direkt auf den Textdatensatz.

Text bei `0136h`:
- BOUNCE.GEO: `Bounce`
- BCOLTEST.GEO: `RGB565 colour proof`

Die unterschiedlichen Textinhalte bei gleichbleibender Tabellenstruktur sprechen für eine wiederverwendete Ressourcenstruktur mit programmspezifischen Daten.

## 4. Strukturbeobachtung

Die Tabellenziele sind heterogen:
1. Einige zeigen auf Textdatensätze mit Präfix `01 00 00 00 00 FF`.
2. Andere zeigen auf binäre Datenbereiche.
3. Ein Tabellenwert ist `FFFFh`.
4. Ein abschließender Tabellenwert ist `0000h` und zeigt damit auf den Ressourcenanfang.

Diese Heterogenität ist mit der Annahme unvereinbar, dass alle Tabellenwerte ohne weitere Regeln gleichartige, direkt lesbare Moniker-Datenstarts darstellen. Sie beweist aber auch nicht, dass es sich um LMem-Handles handelt.

## 5. Abgrenzung zur LMem-Interpretation

Die GeoWorks-Systemsoftwarebeschreibung von 10. November 1990 erläutert LMem-Chunk-Handles als Offsets auf WORD-Speicherstellen, an denen der tatsächliche Chunk-Offset abgelegt ist. Die hier beobachteten Zielbereiche beginnen teils mit `01 00`, teils mit ganz anderen Bytefolgen. Ohne die Lage und Struktur der tatsächlichen LMem-Heap- und Handle-Tabelle ist daraus keine sichere Handle-Dereferenzierung ableitbar.

Primärquelle: *PC/GEOS System Software Overview*, Draft 10 November 1990:  
https://www.lyonlabs.org/commodore/onrequest/geos/PC-GEOS-System-Software-Overview.pdf

## 6. Ergebnis

**Gesichert:** Die Tabellen ab `+20h` in Ressource 3 und 4 enthalten Offsets, die auf unterschiedliche interne Datensatzbereiche zeigen. Mehrere Ziele enthalten klar erkennbare, wiederkehrend aufgebaute Textdatensätze. Ressource 4 weist dieselbe Tabellenstruktur in beiden GEO-Dateien auf, während sich der zugehörige Textinhalt unterscheidet.

**Nicht gesichert:** Die genaue Bedeutung der Tabelle, die Semantik der sechs Präfixbytes, die Zuordnung der binären Zielbereiche und die Frage, ob diese Tabelle direkt oder indirekt über LMem-Handles ausgewertet wird.

## 7. Konsequenz

Keine Änderung am GeoViewPlus-Code. Keine Extraktion oder Klassifizierung dieser Datensätze als Icons. Der nächste Schritt ist eine feldweise Gegenüberstellung der Textdatensätze und ihrer binären Nachbarbereiche, um wiederkehrende Datensatzgrenzen und mögliche interne Referenzfelder zu bestimmen.

Originaldateien wurden ausschließlich lesend untersucht und nicht verändert.
