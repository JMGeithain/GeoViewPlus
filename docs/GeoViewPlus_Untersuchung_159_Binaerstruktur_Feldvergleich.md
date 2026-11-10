# Untersuchung 159 – Feldvergleich der wiederkehrenden binären Struktur in Ressource 3

**Projekt:** GeoViewPlus – Untersuchung echter PC/GEOS-Icons  
**Material:** `BOUNCE.GEO` und `BCOLTEST.GEO` aus Basebox-SVGA-Ensemble12(2).zip  
**Geltungsbereich:** Ausschließlich die vorliegenden GeoWorks-/PC/GEOS-1.x-Dateien.

## 1. Ausgangspunkt

Untersuchung 158 identifizierte dieselbe 16-Byte-Folge an unterschiedlichen ressourcenrelativen Positionen:
- BOUNCE.GEO, Ressource 3, `+0082h`
- BCOLTEST.GEO, Ressource 3, `+008Eh`

Die Verschiebung entspricht dem Unterschied der vorangehenden Textlängen. Die Ressourcen wurden erneut direkt aus dem ZIP gelesen. Die Größen und SHA-256-Prüfsummen entsprechen den zuvor dokumentierten Werten.

## 2. Wiederkehrende Folge

An beiden Positionen stehen dieselben Bytes:

```text
41 40 08 00 07 00 02 00 CC CC 26 00
```

Die Folge lässt sich rein deskriptiv in sechs Little-Endian-WORDs gruppieren:

| Relative Position | Bytes | WORD |
|---:|---|---:|
| +00 | 41 40 | 4041h |
| +02 | 08 00 | 0008h |
| +04 | 07 00 | 0007h |
| +06 | 02 00 | 0002h |
| +08 | CC CC | CCCCh |
| +0A | 26 00 | 0026h |

Diese Gruppierung ist nur eine Byte-/WORD-Darstellung. Sie beweist nicht, dass die Felder im Programm tatsächlich als sechs WORDs gelesen werden.

## 3. Folgende Struktur ab +0Ch

Zwölf Bytes nach dem Anfang der Folge beginnt in beiden Dateien die nächste wiederkehrende Folge:

```text
00 30 53 00 00 00 08 00 00 00 00 00
```

Positionen:
- BOUNCE R3: `+008Eh`
- BCOLTEST R3: `+009Ah`

Auch diese Folge lässt sich deskriptiv als sechs WORDs schreiben:

```text
3000h 0053h 0000h 0008h 0000h 0000h
```

Unmittelbar danach folgt in beiden Ressourcen:

```text
38 00 00 40 30 00 00 40 2C 00 00 00
```

Diese 12-Byte-Folge liegt:
- BOUNCE R3 bei `+009Ah`
- BCOLTEST R3 bei `+00A6h`

Die Bytes sind positionsverschoben, aber im jeweiligen logischen Ablauf gleich.

## 4. Vergleich der folgenden Bytes

Der zusammenhängende Bereich um die beiden Folgen zeigt in beiden Dateien dasselbe Muster:

BOUNCE R3 ab `+0082h`:
```text
41 40 08 00 07 00 02 00 CC CC 26 00
00 30 53 00 00 00 08 00 00 00 00 00
38 00 00 40 30 00 00 40 2C 00 00 00
2E 00 00 C0 28 00 00 00 00 10 00 0C
```

BCOLTEST R3 ab `+008Eh`:
```text
41 40 08 00 07 00 02 00 CC CC 26 00
00 30 53 00 00 00 08 00 00 00 00 00
38 00 00 40 30 00 00 40 2C 00 00 00
34 00 00 40 00 00 00 00 32 00 00 00
```

Die ersten 36 Bytes (drei 12-Byte-Gruppen) sind identisch. Danach unterscheiden sich die Bytes. Der Vergleich belegt somit einen identischen gemeinsamen Teil und einen nachfolgenden variablen Bereich.

## 5. Beobachtung zu den 12-Byte-Gruppen

Die drei identischen Gruppen haben Längen von jeweils zwölf Bytes und folgen direkt aufeinander. Das ist ein wiederkehrendes Strukturmuster. Es ist jedoch nicht ausreichend, um sie als C-Strukturen, Objektdatensätze, Moniker-Einträge oder LMem-Chunks zu bezeichnen.

Auch die Werte `4041h`, `0008h`, `0007h`, `0002h`, `CCCCh`, `0026h`, `3000h`, `0053h` und `0008h` bleiben zunächst unbenannte Felder. Eine Größen- oder Typinterpretation wäre ohne Code- oder Dokumentationsbeleg spekulativ.

## 6. Ergebnis

**Gesichert:**
1. Die Folge `41 40 08 00 07 00 02 00 CC CC 26 00` ist in BOUNCE R3 bei `+82h` und BCOLTEST R3 bei `+8Eh` identisch.
2. Zwölf Bytes danach folgt in beiden Dateien `00 30 53 00 00 00 08 00 00 00 00 00`.
3. Weitere zwölf Bytes danach folgt `38 00 00 40 30 00 00 40 2C 00 00 00`.
4. Die ersten 36 Bytes dieses binären Bereichs sind identisch; danach unterscheiden sich die Inhalte.
5. Die Positionen sind relativ zum Ressourcenanfang angegeben und berücksichtigen den unterschiedlichen Titeltext.

**Nicht gesichert:**
- Die Feldbedeutung der WORDs.
- Ob die 12-Byte-Gruppierung eine tatsächliche Datensatzgrenze darstellt.
- Ob die Folge eine Objektbeschreibung, Grafik-/Moniker-Metadaten, einen Ressourcenverweis oder eine andere Struktur enthält.
- Ob irgendeines der WORDs ein LMem-Handle oder ein direkter Offset ist.

## 7. Konsequenz für GeoViewPlus

Noch keine Codeänderung. Die 12-Byte-Gruppierung kann als Untersuchungsraster dienen, darf aber nicht als bestätigtes Datensatzformat implementiert werden. Als nächster Schritt sollte die Folge mit weiteren Instanzen in denselben Ressourcen sowie mit den zugehörigen Programm-/Objektdefinitionen abgeglichen werden.

## 8. Integrität

- GEO-Dateien ausschließlich lesend aus dem ZIP-Archiv gelesen.
- Keine Originaldatei verändert.
- Kein GeoViewPlus-Programmcode geändert.
- Keine Icon-/Moniker-Klassifizierung vorgenommen.
