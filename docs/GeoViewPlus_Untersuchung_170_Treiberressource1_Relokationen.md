# Untersuchung 170 – Relokationseinträge in Treiber-Ressource 1

**Projekt:** GeoViewPlus – Untersuchung echter PC/GEOS-Icons  
**Material:** `BB120_64.GEO`, `BB72_64.GEO`, `BB96_64.GEO`, `S16_1280.GEO`, `V16_0720.GEO`  
**Geltungsbereich:** Direkte Tabellen- und Bytebefunde an fünf GeoWorks-/PC/GEOS-1.x-Treibern.  
**Methode:** Die Relokationstabellen wurden anhand der Geode-Ressourcentabelle lokalisiert und die 72 Vier-Byte-Einträge jeweils roh sowie feldweise verglichen.

## 1. Lage der Relokationstabellen

Ressource 1 beginnt in allen fünf Dateien bei Dateioffset 318. Ihre Größe variiert nach Treiber. Die Relokationsdaten beginnen nach der auf 16 Bytes aufgerundeten Ressourcengröße.

| Datei | R1-Größe | auf 16 Bytes gerundet | Relokationstabelle ab Dateioffset | Bytes | Einträge |
|---|---:|---:|---:|---:|---:|
| BB120_64.GEO | 32622 | 32624 | 32942 | 288 | 72 |
| BB72_64.GEO | 32622 | 32624 | 32942 | 288 | 72 |
| BB96_64.GEO | 32622 | 32624 | 32942 | 288 | 72 |
| V16_0720.GEO | 32576 | 32576 | 32894 | 288 | 72 |
| S16_1280.GEO | 26368 | 26368 | 26686 | 288 | 72 |

Jeder Eintrag ist vier Bytes lang. Die 288 Bytes ergeben daher exakt 72 Einträge.

## 2. Byteidentität aller fünf Relokationstabellen

Alle 72 Einträge wurden in jeder Datei in derselben Reihenfolge ausgelesen. Der Vergleich der dekodierten Vier-Byte-Datensätze ergibt in allen fünf Dateien dieselbe Sequenz.

SHA-256 der normalisierten Folge aus jeweils `info`, `extra`, `target` und dem am Ziel gespeicherten WORD:

`1904f692cddc94395edff3e4a643f2b8c1423321fb485331922878e2c9b71f7f`

Dieser Digest ist für alle fünf Dateien identisch. Die Relokationsfolgen sind damit nicht nur gleich lang, sondern in allen 72 Einträgen identisch.

Das ist besonders bemerkenswert, weil die Ressource 1 selbst je nach Treiber eine andere Größe besitzt und ihr Inhalt an einigen Stellen variiert.

## 3. Rohdekodierung der info-Bytes

Die 72 Einträge verteilen sich auf drei beobachtete `info`-Werte:

| info | oberes Nibble | unteres Nibble | Anzahl |
|---:|---:|---:|---:|
| `00h` | 0 | 0 | 44 |
| `22h` | 2 | 2 | 24 |
| `23h` | 2 | 3 | 4 |

Das mitgelieferte Inventarisierungsskript bezeichnet diese Kombinationen als:
- `00h`: source kernel / type FAR_PTR
- `22h`: source resource / type SEGMENT
- `23h`: source resource / type HANDLE

Hier werden diese Bezeichnungen als Dekodierung des vorhandenen Skripts wiedergegeben. Die Untersuchung behauptet nicht, damit bereits alle semantischen Einzelheiten des GeoWorks-1.x-Relokationsformats unabhängig bewiesen zu haben. Die Rohwerte und Häufigkeiten sind der unmittelbare Befund.

Alle Einträge haben `extra = 0`.

## 4. Ziele der 24 Einträge mit info = 22h

Die 24 Zielpositionen innerhalb der Ressource lauten:

```text
0042 00BA 00C2 00C6 00CA 00CE 00E6 0126
012A 012E 0136 013A 013E 0142 0146 014A
014E 04CF 154B 1574 15E7 1603 1B71 58AE
```

Das WORD an jedem dieser Zieloffsets ist `0001h`.

Die Zielpositionen sind nicht gleichmäßig verteilt: 17 Ziele liegen im frühen Ressourcenbereich bis `014Eh`; die übrigen sieben sind über spätere Bereiche verteilt. Aus der Verteilung allein lässt sich noch keine konkrete Datenstruktur benennen.

## 5. Ziele der vier Einträge mit info = 23h

Die vier Zielpositionen lauten:

```text
0048 14B9 150C 159C
```

Das WORD an jedem dieser Zieloffsets ist `0002h`.

Der erste Zieloffset `0048h` liegt unmittelbar neben dem frühen Zielbereich der `22h)-Einträge. Die drei übrigen Ziele liegen in der Nähe weiterer späterer Ziele aus der `22h)-Gruppe. Das ist eine räumliche Beobachtung, noch kein Beweis einer gemeinsamen Objekt- oder Chunk-Struktur.

## 6. Ziele der 44 Einträge mit info = 00h

Die 44 Zielpositionen lauten:

```text
0364 037E 03A2 03C5 03DC 03F7 0418 0433
0449 0472 06BF 0851 089B 09E8 0E43 0E51
0E63 0F36 0F4B 0FE7 1015 11BF 11CA 1209
150F 1535 1546 159F 15C5 15D6 2002 2022
49BA 4B3F 4CA6 4CC2 4DE3 52AA 54EE 5520
61C2 61F5 61FC 624A
```

Die am Ziel gespeicherten WORD-Werte sind unterschiedlich. In der vorliegenden Folge kommen unter anderem `00AAh`, `00ABh`, `01C2h`, `01C4h`, `0005h`, `0006h`, `0000h` und `0002h` vor.

Die Zielpositionen verteilen sich auf mehrere größere Bereiche der Ressource. Die Relokationsart und die dort gespeicherten WORDs reichen allein nicht aus, um daraus Funktionsnamen oder Datenstrukturen abzuleiten.

## 7. Was die identischen Relokationen aussagen

**Gesichert:**
1. Jede der fünf Treiber-Ressourcen 1 besitzt 72 Relokationseinträge.
2. Alle 72 Einträge sind über alle fünf Treiber hinweg in gleicher Reihenfolge identisch.
3. Es gibt 44 Einträge mit `info=00h`, 24 mit `info=22h` und vier mit `info=23h`.
4. Die 24 `22h)-Ziele enthalten am Ziel jeweils `0001h`; die vier `23h)-Ziele jeweils `0002h`.
5. Die 44 `00h)-Ziele enthalten unterschiedliche WORD-Werte.
6. Die Ressourcengröße kann sich ändern, ohne dass sich die 72 Relokationseinträge ändern.

**Nicht bewiesen:**
- Dass die Relokationsziele Programm-Icons, Dokument-Icons oder Moniker bezeichnen.
- Dass alle Zielbereiche Chunk-Handles oder LMEM-Blöcke sind.
- Dass die vier `23h)-Einträge eine zusammenhängende Objektgruppe bilden.
- Dass aus den WORD-Werten an den Zielen unmittelbar Ressourcennummern, Objekt-IDs oder Typkennungen ablesbar sind.
- Dass die Relokationstabelle den gesamten internen Referenzbestand der Ressource beschreibt.

## 8. Konsequenz für GeoViewPlus

Die 72 Relokationen sind ein stabiler struktureller Fingerabdruck dieser Treiber-Ressource 1. Sie eignen sich für die spätere Klassifizierung und für einen Vergleich mit weiteren Treiberversionen.

Eine Icon-Zuordnung oder LMEM-Interpretation wird daraus ausdrücklich nicht abgeleitet. Der nächste sinnvolle Schritt ist die Untersuchung der Bytebereiche unmittelbar um die 28 Ressourcenziele (`22h` und `23h`) und der 44 weiteren Zielstellen. Dabei ist zu prüfen, ob wiederkehrende Feldmuster, Handle-/Chunk-Tabellen oder Text-/Moniker-ähnliche Daten nachweisbar sind.

Keine Programmcodeänderung.

## 9. Integrität und Versionsgrenze

- Alle fünf GEO-Dateien ausschließlich lesend untersucht.
- Keine Originaldatei verändert.
- Kein GeoViewPlus-Programmcode geändert.
- Keine Icon-/Moniker-Zuordnung vorgenommen.
- Keine PC/GEOS-2.x-Struktur als Beleg für GeoWorks 1.x verwendet.
