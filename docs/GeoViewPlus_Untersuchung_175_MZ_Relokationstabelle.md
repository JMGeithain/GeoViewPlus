# Untersuchung 175 – Die 276 DOS-MZ-Relokationen der KERNEL.EXE

## Ziel

Nach der Formatprüfung in Untersuchung 174 wird die MZ-Relokationstabelle der im SVGA-Ensemble enthaltenen `KERNEL.EXE` getrennt ausgewertet. Ziel ist, ihre tatsächliche Struktur zu dokumentieren und zu prüfen, ob sie eine direkte Zuordnung der elf FAR-CALL-Zielwerte aus den Treibern ermöglicht.

## Untersuchte Datei

`Basebox-SVGA-Ensemble12/source/pm-backport/target-original/GWSVGA/KERNEL.EXE`

- Dateigröße: 72.736 Byte
- SHA-256: `c2cc8952cdb01d0f459bf281ee3b78f8ce9464aba0b58c3758f8c73e24fb6eb5`
- MZ-Relokationstabelle: Dateioffset `003Ch`
- Anzahl der MZ-Relokationseinträge (`e_crlc`): 276
- MZ-Headergröße: 96 Paragraphen = 1.536 Byte = `0600h`

Die MZ-Relokationstabelle besteht aus 276 Datensätzen zu je vier Byte. Jeder Datensatz enthält ein WORD-Offset und ein WORD-Segment. Der vom MZ-Lader zu korrigierende WORD-Wert liegt im Ladebereich bei:

`Dateioffset = MZ-Headergröße + Segment × 16 + Offset`

## 1. Verteilung der 276 Einträge

Die 276 Einträge verteilen sich nach dem Segmentfeld des Relokationsdatensatzes auf drei Gruppen:

| Segmentfeld | Anzahl | Offsetbereich innerhalb des Segments |
|---:|---:|---:|
| `0F93h` | 156 | `0004h–1CCFh` |
| `0E34h` | 59 | `0004h–0FCBh` |
| `0000h` | 61 | `0162h–D216h` |
| **Gesamt** | **276** | |

Die Zählung erfolgt unmittelbar aus den 276 Vier-Byte-Datensätzen ab Dateioffset `003Ch`. Die Offsetbereiche sind jeweils Minimum und Maximum des ersten WORDs innerhalb der Gruppe.

## 2. WORD-Werte an den Relokationsstellen

Vor der DOS-Laderelokation enthalten die WORDs an den 276 berechneten Zielstellen folgende Werte:

| gespeicherter WORD-Wert | Anzahl |
|---:|---:|
| `0000h` | 222 |
| `0E34h` | 47 |
| `0F93h` | 5 |
| `0DEBh` | 1 |
| `0F53h` | 1 |
| **Gesamt** | **276** |

Diese Werte sind die im Dateiabzug gespeicherten Inhalte der zu korrigierenden WORDs. Sie dürfen nicht mit den Segmentfeldern der Relokationseinträge verwechselt werden. Der MZ-Lader addiert beim Laden die tatsächliche Ladeparagraphenbasis zu diesen Werten.

## 3. Abgrenzung zur GeoWorks-Relokation

Die beiden Tabellen sind technisch und semantisch getrennt:

| Eigenschaft | MZ-Relokation in KERNEL.EXE | GeoWorks-Relokation in SVGA-Treiber |
|---|---|---|
| Zweck | DOS-Lader passt Segmentwerte beim Laden an | GeoWorks-Lader verarbeitet geode-/ressourcenbezogene Referenzen |
| Eintragsgröße | 4 Byte | 4 Byte |
| Struktur | Offset-WORD + Segment-WORD | Info-Byte + Extra-Byte + Ziel-WORD |
| Anzahl hier | 276 | 72 in Ressource 1 jedes untersuchten Treibers |
| Aussage über Kernel-API-Namen | keine | FAR-CALL-Operand ist bei Typ `00h` belegt, Funktionsname noch offen |

Die bloße Tatsache, dass beide Tabellen vier Byte pro Eintrag verwenden, macht sie nicht kompatibel oder austauschbar.

## 4. Suche nach lesbaren Export- und Funktionsnamen

Die lesbaren ASCII-Zeichenfolgen des MZ-Ladebereichs wurden extrahiert und nach auffälligen Begriffen durchsucht. Dabei fanden sich unter anderem:

- `kernel.exe`
- `System error: `
- `Cannot open geos.str`
- `geos.str`
- `geos.ini`
- `GEOS_ACT.IVE`
- die zusammenhängende Zeichenfolge `Heap$File$Drive$Disk$Geode$Thread$Timer$Object$Scrub thread$File System$Kernel Library$Fonts$Graphics$Window$Memory Video$Localization$Font ID$Font Size$EMS$XMS$Extended Memory$Keyboard$Font$User Interface$Initializing $ module$ driver$.`

Diese Zeichenfolge enthält interne Systembegriffe und Komponentennamen, aber keine erkennbare Tabelle, die die elf FAR-CALL-Ziel-Offsets aus Untersuchung 173 mit symbolischen Funktionsnamen verbindet.

Eine reine ASCII-Suche kann komprimierte, tokenisierte oder binär codierte Namensdaten nicht ausschließen. Das Ergebnis lautet daher präzise: **In den untersuchten lesbaren Zeichenfolgen wurde keine belastbare Kernel-Export-/Funktionsnamensliste gefunden.**

## 5. Ergebnis

**Gesichert:**

1. Die MZ-Relokationstabelle enthält exakt 276 Einträge.
2. Die Einträge verteilen sich auf die Segmentfelder `0F93h` (156), `0E34h` (59) und `0000h` (61).
3. Die gespeicherten WORD-Werte an den Zielstellen verteilen sich auf `0000h` (222), `0E34h` (47), `0F93h` (5), `0DEBh` (1) und `0F53h` (1).
4. Die lesbaren Zeichenfolgen liefern keine belastbare Namenszuordnung für die elf Treiber-FAR-CALL-Zielwerte.

**Nicht bewiesen:**

- dass die drei MZ-Segmentgruppen den drei GeoWorks-Treiberschnittstellen oder bestimmten Kernel-Komponenten entsprechen;
- dass die Zeichenfolge mit Systembegriffen eine Exporttabelle darstellt;
- dass sich die elf Kernel-Ziel-Offsets unmittelbar aus den MZ-Relokationen ableiten lassen.

## 6. Nächster Schritt

Untersuchung 176 sollte die drei MZ-Segmentgruppen anhand der tatsächlichen Code- und Datenbereiche kartieren und prüfen, ob die Segmentgrenzen mit erkennbaren Programmabschnitten übereinstimmen. Parallel dazu muss die GeoWorks-1.x-Lader-/Kernel-Schnittstelle anhand von 1.x-Unterlagen oder einem nachweislich passenden Kernel-Symbolbestand untersucht werden. PC/GEOS 2.x und FreeGEOS bleiben ausdrücklich Vergleichsmaterial, keine Beweisquelle für GeoWorks 1.x.

---
*Read-only-Analyse. Die KERNEL.EXE und die GEO-Dateien im ZIP wurden nicht verändert. Keine Änderung am GeoViewPlus-Programmcode.*
