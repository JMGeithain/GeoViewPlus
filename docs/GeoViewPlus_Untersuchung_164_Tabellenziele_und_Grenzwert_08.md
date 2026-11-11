# Untersuchung 164 – Tabellenziele im Verhältnis zum Grenzwert +08h

**Projekt:** GeoViewPlus – Untersuchung echter PC/GEOS-Icons  
**Material:** `BOUNCE.GEO` und `BCOLTEST.GEO`, Ressourcen 3–10  
**Geltungsbereich:** Direkte Bytebefunde an den vorliegenden GeoWorks-/PC/GEOS-1.x-Dateien.  
**Methode:** Ausschließlich lesender Vergleich der bereits ermittelten Tabellenziele mit den WORD-Werten bei Ressourcenoffset `+08h` und `+14h`.

## 1. Fragestellung

Untersuchung 163 zeigte, dass das WORD bei `+14h` in allen Ressourcen 3–10 exakt der unabhängig ermittelten Ressourcengröße entspricht. Das WORD bei `+08h` liegt entweder am Ressourcenende oder davor. Nun wird geprüft, ob die bislang bekannten Ziele der Tabellen in Ressourcen 3–10 in den Bereich ab `+08h` hineinreichen.

Wichtig: Geprüft werden die bereits identifizierten Tabellenziele. Das ist keine Behauptung, dass sämtliche denkbaren impliziten Referenzen oder Laufzeitzeiger in den Ressourcen bekannt wären.

## 2. Ressourcen 3 und 4

Die zuvor aus den Tabellen gelesenen WORD-Ziele (Little Endian) lauten:

### Ressource 3

- BOUNCE.GEO: `003Eh, FFFFh, 004Eh, 0072h, 0082h, 008Eh, 00B6h, 00C6h, 00CEh, 00F2h, 00FEh, 0122h, 012Eh, 0000h`.
- BCOLTEST.GEO: `003Eh, FFFFh, 004Eh, 0072h, 008Eh, 009Ah, 00C2h, 00D2h, 00DAh, 00FEh, 010Ah, 012Eh, 013Ah, 0000h`.

Der Eintrag `FFFFh` ist ein Sentinel und kein innerhalb der Ressource liegender Offset. Der Nullwert wird hier als Tabellenwert dokumentiert, nicht als Nachweis eines gültigen Datenziels.

Der größte positive, von null verschiedene Offset beträgt:
- BOUNCE R3: `012Eh`, gegenüber `+08h = 0178h`.
- BCOLTEST R3: `013Ah`, gegenüber `+08h = 0184h`.

Damit liegen sämtliche hier aufgelisteten positiven Tabellenziele unterhalb des jeweiligen `+08h)-Werts.

### Ressource 4

Die zuvor ermittelten Ziele lauten für beide Dateien:
`002Eh, 0036h, 00FEh, 012Ah, 0136h, 0000h`.

Der größte positive Offset ist `0136h).
- BOUNCE R4: `+08h = 0144h`.
- BCOLTEST R4: `+08h = 0150h`.

Auch diese positiven Tabellenziele liegen unterhalb des jeweiligen `+08h)-Werts.

## 3. Ressourcen 5–10

Für die zuvor untersuchten Tabellen in R5–R10 wurden die Werte `0026h` und `002Ah` festgestellt. Beide liegen jeweils deutlich unterhalb der zugehörigen `+08h)-Grenze:

| Ressource | +08h | bekannte Tabellenwerte | Vergleich |
|---:|---:|---:|---|
| R5 | `0094h` | `0026h, 002Ah` | beide kleiner |
| R6 | `0060h` | `0026h, 002Ah` | beide kleiner |
| R7 | `00F4h` | `0026h, 002Ah` | beide kleiner |
| R8 | `0270h` | `0026h, 002Ah` | beide kleiner |
| R9 | `008Ch` | `0026h, 002Ah` | beide kleiner |
| R10 | `00DCh` | `0026h, 002Ah` | beide kleiner |

Diese Aussage bezieht sich auf die identifizierte Tabelle und deren Werte. Sie beweist nicht, dass es in diesen Ressourcen keine weiteren Referenzmechanismen gibt.

## 4. Exakte Bytes ab +08h bis +14h

Die Suffixbereiche wurden erneut direkt aus den beiden GEO-Dateien gelesen. In allen Fällen, in denen `+08h` kleiner als die Ressourcengröße ist, bestehen die Bytes ab diesem Offset bis zum Ressourcenende ausschließlich aus Nullbytes:

| Datei / Ressource | +08h | Ressourcengröße (+14h) | Suffixlänge | Bytes ab +08h |
|---|---:|---:|---:|---|
| BOUNCE R3 | `0178h` | `0180h` | 8 | 8 × `00` |
| BCOLTEST R3 | `0184h` | `0190h` | 12 | 12 × `00` |
| BOUNCE R4 | `0144h` | `0150h` | 12 | 12 × `00` |
| BCOLTEST R4 | `0150h` | `0150h` | 0 | leer |
| R5 (beide Dateien) | `0094h` | `00A0h` | 12 | 12 × `00` |
| R6 (beide Dateien) | `0060h` | `0060h` | 0 | leer |
| R7 (beide Dateien) | `00F4h` | `0100h` | 12 | 12 × `00` |
| R8 (beide Dateien) | `0270h` | `0270h` | 0 | leer |
| R9 (beide Dateien) | `008Ch` | `0090h` | 4 | 4 × `00` |
| R10 (beide Dateien) | `00DCh` | `00E0h` | 4 | 4 × `00` |

Bei R5–R10 sind die Ressourcen in beiden Dateien byteidentisch; die Werte wurden für beide Vorkommen gegengeprüft.

## 5. Ergebnis

**Direkt belegt:**
1. Kein positiver Offset aus den hier bekannten Tabellen in Ressourcen 3 und 4 erreicht den jeweiligen `+08h)-Grenzwert.
2. Die bekannten Tabellenwerte `0026h` und `002Ah` in Ressourcen 5–10 liegen ebenfalls jeweils unter `+08h`.
3. In allen Ressourcen 3–10 ist der Bereich ab `+08h` bis zur durch `+14h` bestätigten Ressourcengröße entweder leer oder besteht ausschließlich aus Nullbytes.
4. Die Tabellenziele, die in dieser Untersuchung berücksichtigt wurden, zeigen somit nicht in den Suffixbereich ab `+08h`.

**Noch nicht bewiesen:**
- Dass `+08h` formal das Ende aller gültigen Nutzdaten bezeichnet.
- Dass alle Nullbytes nach `+08h` semantisch Padding sind.
- Dass keine nicht-tabellarischen oder zur Laufzeit erzeugten Referenzen in diesen Bereich zeigen.
- Dass die Felder `+08h` und `+14h` in jeder GeoWorks-1.x-Ressourcenklasse dieselbe Semantik besitzen.

Die Befunde stärken die Arbeitshypothese aus Untersuchung 163, reichen aber noch nicht für eine endgültige Benennung von `+08h`.

## 6. Konsequenz für GeoViewPlus

Keine Änderung am Parser und keine Änderung am Programmcode. Für eine spätere Implementierung kann `+08h` weiterhin als neutraler Kandidat-Grenzwert protokolliert werden. Ein Abschneiden der Ressource an dieser Stelle ist noch nicht freigegeben: Zuerst müssen weitere Ressourcentypen und mögliche nicht-tabellarische Referenzen geprüft werden.

## 7. Integrität und Versionsgrenze

- `BOUNCE.GEO` und `BCOLTEST.GEO` ausschließlich lesend untersucht.
- Keine Originaldatei verändert.
- Kein GeoViewPlus-Programmcode geändert.
- Keine Icon- oder Moniker-Zuordnung vorgenommen.
- Keine PC/GEOS-2.x-Struktur als Beleg für GeoWorks 1.x verwendet.
