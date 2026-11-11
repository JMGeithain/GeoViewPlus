# Untersuchung 168 – Textlängenfelder und Abschlussbytes in Treiber-Ressource 2

**Projekt:** GeoViewPlus – Untersuchung echter PC/GEOS-Icons  
**Material:** `BB120_64.GEO`, `BB72_64.GEO`, `BB96_64.GEO`, `S16_1280.GEO`, `V16_0720.GEO`  
**Geltungsbereich:** Direkte Bytebefunde an fünf GeoWorks-/PC/GEOS-1.x-Treiberdateien.  
**Untersuchter Bereich:** Ressource 2, 36 WORD-Offsets ab `+20h`, Textdatensätze an den jeweiligen Zielen.

## 1. Fragestellung

Untersuchung 167 zeigte, dass die 36 Tabellenwerte auf Textdatensätze verweisen. Nun wird das WORD unmittelbar vor jedem Textziel geprüft. Zusätzlich werden Datensatzende, Nullterminierung und Bytes bis zum nächsten Datensatz untersucht.

## 2. Längenfeld vor jedem Textziel

Für jeden der 36 Einträge gilt in allen fünf Dateien:

- Tabellenwert = Offset des ersten Textbytes.
- Zwei Bytes vor diesem Ziel steht ein WORD-Längenfeld.
- Der Text endet mit einem Nullbyte.
- Der Längenwert entspricht exakt: **2 Bytes Längenfeld + Textbytes + 1 Nullbyte**.

Formel:

`Datensatzlänge = 2 + Textlänge + 1`

Beispiele aus BB120_64.GEO:

| Text | Textbytes | WORD davor | Dezimal | Rechnung |
|---|---:|---:|---:|---|
| `VESA Compatible SuperVGA: 640x480 64K-color` | 43 | `002Eh` | 46 | 2 + 43 + 1 |
| `VESA Compatible SuperVGA: 1024x600 64K-color` | 44 | `002Fh` | 47 | 2 + 44 + 1 |
| `VESA Compatible SuperVGA: 1280x1024 64K-color` | 45 | `0030h` | 48 | 2 + 45 + 1 |
| `Basebox: 72 DPI 64K-color` | 25 | `001Ch` | 28 | 2 + 25 + 1 |
| `Basebox: 120 DPI 64K-color` | 26 | `001Dh` | 29 | 2 + 26 + 1 |

Die Formel wurde für alle 36 Einträge geprüft. Es gibt in dieser geprüften Tabelle keine Abweichung. Die Tabellen-Offsets und die Längenfelder sind in allen fünf Treibern gleich.

## 3. Abstand und Bytes zwischen Datensätzen

Die ersten 34 VESA-Datensätze liegen regelmäßig im Abstand `0030h`. Die drei Basebox-Datensätze liegen anschließend in kürzeren Abständen von jeweils `001Ch`.

Die Bytes zwischen dem Ende eines Datensatzes und dem Längen-WORD des nächsten Datensatzes sind nicht einheitlich:

- Bei den ersten neun Datensätzen liegen nach dem Nullterminator zwei Bytes `2E 00`.
- Beim zehnten bis neunzehnten sowie bei weiteren Datensätzen gibt es je nach Länge ein oder kein zusätzliches Byte `00`.
- Bei den abschließenden Datensätzen kann der nächste Datensatz direkt anschließen.
- Nach dem letzten Datensatz folgt am Ressourcenende noch `CC)-Füll-/Abschlussmaterial.

Die Zwischenbytes sind damit nicht Teil des durch das Längenfeld beschriebenen Textdatensatzes. Ihre genaue Funktion (Ausrichtung, Füllung oder eine andere interne Konvention) ist noch nicht bewiesen. Insbesondere wird `CC` nicht pauschal als Padding-Regel klassifiziert.

## 4. Feld +16h im Zusammenhang mit der Offsettabelle

Das WORD bei Ressourcenoffset `+16h` zeigt in jeder der fünf Dateien auf einen WORD-Slot innerhalb der 36-Einträge-Tabelle. Der Tabellenbeginn ist `+20h`; die Position wird mit `(Wert - 0020h) / 2` bestimmt.

Die so ermittelte Position entspricht jeweils einem sinnvollen, dateispezifischen Eintrag:

| Datei | WORD +16h | Tabellenindex (0-basiert) | Text am Eintrag |
|---|---:|---:|---|
| BB120_64.GEO | `0066h` | 35 | `Basebox: 120 DPI 64K-color` |
| BB72_64.GEO | `0062h` | 33 | `Basebox: 72 DPI 64K-color` |
| BB96_64.GEO | `0064h` | 34 | `Basebox: 96 DPI 64K-color` |
| S16_1280.GEO | `0046h` | 19 | `VESA Compatible SuperVGA: 1280x1024 64K-color` |
| V16_0720.GEO | `003Ch` | 14 | `VESA Compatible SuperVGA: 1280x720 64K-color` |

**Beobachtung:** In jeder Datei entspricht der Eintrag, auf den `+16h` zeigt, der jeweiligen Treiber-/Build-spezifischen Zielauflösung bzw. DPI-Angabe.

**Arbeitshypothese:** `+16h` könnte eine aktuelle, bevorzugte oder voreingestellte Auswahl innerhalb der Modustabelle referenzieren. Diese Interpretation ist plausibel, aber ohne Laufzeitbeobachtung oder zeitgenössische Dokumentation nicht endgültig bewiesen.

Wichtig: `+16h` ist kein einfacher Zähler. Der Wert ist ein Byteoffset in der Ressource, der auf einen Tabellen-Slot zeigt.

## 5. Gesicherte Ergebnisse

1. Alle 36 Tabellenziele verweisen auf Textdatensätze.
2. Vor jedem Textziel steht ein WORD-Längenfeld.
3. Für alle 36 Datensätze gilt exakt `2 + Textlänge + 1`.
4. Der Nullterminator ist Bestandteil der durch das Längenfeld gezählten Datensatzlänge.
5. Die Zwischenbytes bis zum nächsten Datensatz liegen außerhalb dieses Längenbereichs.
6. `+16h` zeigt in jeder Datei auf einen Eintrag der 36-WORD-Tabelle.
7. Der ausgewählte Eintrag entspricht jeweils der im Dateinamen bzw. Build erkennbaren Zielauflösung oder DPI-Angabe.

## 6. Noch nicht bewiesen

- Die formale Bezeichnung und vollständige Semantik des Längen-WORDs.
- Ob die Zwischenbytes Alignment, Padding oder eine andere interne Funktion haben.
- Ob `+16h` die beim Start ausgewählte Auflösung, einen Standardmodus oder einen anderen Zustand bezeichnet.
- Ob dieselbe Textdatensatzform in anderen Ressourcentypen oder anderen GeoWorks-1.x-Treibern verwendet wird.
- Ob die 36 Einträge eine vollständige Modusliste darstellen oder ob außerhalb der Tabelle zusätzliche Modusinformationen existieren.

## 7. Konsequenz für GeoViewPlus

Diese Ressourcenklasse lässt sich jetzt deutlich sicherer als Tabelle mit Textdatensatz-Zielen beschreiben. Sie ist keine Icon-/Moniker-Ressource.

Für einen späteren Parser kann ein eigener, vorläufiger Datensatzleser verwendet werden, der:
1. den Tabellenoffset liest,
2. das WORD zwei Bytes vor dem Ziel als Datensatzlänge prüft,
3. die Textbytes bis zum Nullbyte validiert,
4. die Längenformel kontrolliert,
5. die nachfolgenden Zwischenbytes separat belässt.

Keine Implementierung wurde in dieser Untersuchung vorgenommen. Die Ressource wird nicht verändert.

## 8. Integrität und Versionsgrenze

- Fünf GEO-Dateien ausschließlich lesend untersucht.
- Keine Originaldatei verändert.
- Kein GeoViewPlus-Programmcode geändert.
- Keine Icon-/Moniker-Zuordnung vorgenommen.
- Keine PC/GEOS-2.x-Struktur als Beleg für GeoWorks 1.x verwendet.
