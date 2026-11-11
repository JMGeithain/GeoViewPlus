# Untersuchung 163 – Abgleich der Ressourcenlänge mit den Headerfeldern +08h und +14h

**Projekt:** GeoViewPlus – Untersuchung echter PC/GEOS-Icons  
**Material:** `BOUNCE.GEO` und `BCOLTEST.GEO`, Ressourcen 3–10  
**Geltungsbereich:** Direkte Bytebefunde an den vorliegenden GeoWorks-/PC/GEOS-1.x-Dateien.

## 1. Fragestellung

Untersuchung 162 erfasste unterschiedliche Endmuster der Ressourcen 5–10. Nun werden die WORD-Felder bei Ressourcenoffset `+08h` und `+14h` mit der tatsächlichen Ressourcengröße verglichen.

Alle Werte sind Little-Endian-WORDs. Die tatsächliche Ressourcengröße stammt aus der zuvor geprüften Ressourcentabelle. Die Bytes wurden erneut direkt aus beiden GEO-Dateien gelesen.

## 2. Ergebnisse für Ressourcen 5–10

| Ressource | Tatsächliche Größe | WORD +08h | WORD +14h | Größe minus +08h |
|---:|---:|---:|---:|---:|
| R5 | 160 (`00A0h`) | `0094h` (148) | `00A0h` (160) | 12 |
| R6 | 96 (`0060h`) | `0060h` (96) | `0060h` (96) | 0 |
| R7 | 256 (`0100h`) | `00F4h` (244) | `0100h` (256) | 12 |
| R8 | 624 (`0270h`) | `0270h` (624) | `0270h` (624) | 0 |
| R9 | 144 (`0090h`) | `008Ch` (140) | `0090h` (144) | 4 |
| R10 | 224 (`00E0h`) | `00DCh` (220) | `00E0h` (224) | 4 |

Das Feld `+14h` stimmt in allen sechs Fällen exakt mit der tatsächlichen Ressourcengröße überein.

Das Feld `+08h` liegt entweder am Ressourcenende oder davor. Die Differenz entspricht bei R5, R7, R9 und R10 der Länge des abschließenden Bereichs, der nach `+08h` liegt. Bei R6 und R8 ist `+08h` gleich der Ressourcengröße.

## 3. Abgleich mit den tatsächlichen Endbytes

### R5

`+08h = 0094h`. Ab Offset `+94h` folgen genau zwölf Nullbytes bis zum Ressourcenende `+A0h`. Unmittelbar davor liegt `CC CC` bei `+92h` und `+93h`.

### R6

`+08h = 0060h`, identisch mit der Ressourcengröße. Die letzten drei Bytes (`+5Dh` bis `+5Fh`) sind `CC CC CC`. Es gibt keinen nachfolgenden Bereich.

### R7 – Präzisierung zu Untersuchung 162

`+08h = 00F4h`. Von `+F2h` bis `+FFh` liegen 14 Nullbytes. Davon liegen die ersten zwei Nullbytes bei `+F2h` und `+F3h` noch vor dem durch `+08h` markierten Grenzwert. Ab `+F4h` verbleiben genau zwölf Nullbytes bis `+100h`.

Untersuchung 162 beschrieb korrekt 14 Nullbytes am physischen Ressourcenende, unterschied aber noch nicht zwischen den zwei Nullbytes vor und den zwölf Nullbytes ab dem Kandidaten-Grenzwert `+08h`. Diese Trennung ist hiermit ergänzt.

### R8

`+08h = 0270h`, identisch mit der Ressourcengröße. Die letzten drei Bytes (`+26Dh` bis `+26Fh`) sind `CC CC CC`.

### R9

`+08h = 008Ch`. Ab `+8Ch` folgen genau vier Nullbytes bis zum Ressourcenende `+90h`. Davor liegt `CC CC CC` bei `+89h` bis `+8Bh`.

### R10

`+08h = 00DCh`. Ab `+DCh` folgen genau vier Nullbytes bis zum Ressourcenende `+E0h`. Davor liegt `CC CC CC` bei `+D9h` bis `+DBh`.

## 4. Zusätzlicher Kontrollvergleich: Ressourcen 3 und 4

Auch die größeren Ressourcen 3 und 4 zeigen dieselbe Beziehung zwischen `+08h`, `+14h` und Ressourcengröße:

| Datei / Ressource | Größe | WORD +08h | WORD +14h | Differenz |
|---|---:|---:|---:|---:|
| BOUNCE R3 | 384 (`0180h`) | `0178h` | `0180h` | 8 |
| BCOLTEST R3 | 400 (`0190h`) | `0184h` | `0190h` | 12 |
| BOUNCE R4 | 336 (`0150h`) | `0144h` | `0150h` | 12 |
| BCOLTEST R4 | 336 (`0150h`) | `0150h` | `0150h` | 0 |

Das stärkt den Befund, dass `+14h` die Gesamtgröße der Ressource wiedergibt und `+08h` eine zweite, nicht größere Grenz- oder Längenangabe enthält. Die Unterschiede sind nicht auf Ressourcen 5–10 beschränkt.

## 5. Interpretation – bewusst begrenzt

**Gesichert:**
1. Bei allen untersuchten Ressourcen 3–10 entspricht das WORD bei `+14h` exakt der tatsächlichen Ressourcengröße.
2. Das WORD bei `+08h` ist in keinem dieser Fälle größer als die Ressourcengröße.
3. Bei R5, R7, R9 und R10 liegt `+08h` vor dem physischen Ressourcenende; die Differenz entspricht genau dem nachfolgenden Bereich.
4. Bei R6, R8 und BCOLTEST R4 liegt `+08h` genau am Ressourcenende.
5. Bei R7 liegen zwei der 14 abschließenden Nullbytes vor dem `+08h`-Grenzwert und zwölf danach.

**Plausible, aber noch nicht bewiesene Deutung:** `+14h` könnte die vollständige Ressourcenlänge und `+08h` das Ende eines logisch belegten Bereichs oder eine Nutzdatenlänge darstellen. Die Übereinstimmung mit den beobachteten Endbereichen ist stark, reicht allein aber nicht aus, um die Feldnamen oder ihre exakte Semantik festzulegen.

**Nicht gesichert:**
- Dass alle Bytes nach `+08h` Padding sind.
- Dass `+08h` ein Dateioffset statt einer Länge oder eines Grenzwerts ist.
- Dass `CC`-Folgen generell außerhalb der Nutzdaten liegen.
- Dass die beiden Felder in jeder beliebigen GeoWorks-1.x-Ressourcenklasse dieselbe Bedeutung haben.

## 6. Konsequenz für GeoViewPlus

Keine Codeänderung. Für den späteren Parser ist `+14h` ein sehr starker Kandidat für die Ressourcengesamtlänge, da er in allen hier untersuchten Ressourcen exakt mit der unabhängig ermittelten Größe übereinstimmt. `+08h` ist als zweiter Längen-/Grenzwert zu erfassen, aber bis zur Bestätigung nur neutral zu benennen, etwa `header_word_08`.

Der Parser darf die Bytes nach `+08h` noch nicht abschneiden. Zunächst muss geprüft werden, ob Tabellenziele oder andere Referenzen in diesen Bereich zeigen und ob weitere Ressourcentypen dieselbe Beziehung aufweisen.

## 7. Integrität

- Beide GEO-Dateien ausschließlich lesend untersucht.
- Keine Originaldatei verändert.
- Kein GeoViewPlus-Programmcode geändert.
- Keine Icon-/Moniker-Zuordnung vorgenommen.