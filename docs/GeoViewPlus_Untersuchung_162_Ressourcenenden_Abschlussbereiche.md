# Untersuchung 162 – Ressourcenenden und mögliche Abschlussbereiche

**Projekt:** GeoViewPlus – Untersuchung echter PC/GEOS-Icons  
**Material:** `BOUNCE.GEO` und `BCOLTEST.GEO`, Ressourcen 5–10  
**Geltungsbereich:** Bytebefunde an den vorliegenden GeoWorks-/PC/GEOS-1.x-Dateien.

## 1. Ziel und Methode

Untersucht wurden die letzten Bytes der Ressourcen 5–10. Für jede Ressource wurden abschließende Nullfolgen und unmittelbar davorliegende `CC`-Folgen gezählt. Alle Offsets sind relativ zum Ressourcenanfang. Die sechs Ressourcen sind in beiden GEO-Dateien byteidentisch; die Endbereiche stimmen daher überein.

## 2. Größen und Endmuster

| Ressource | Größe | Bereich am Ende | Terminale Nullbytes |
|---:|---:|---|---:|
| R5 | 160 (`A0h`) | `+90h: 00 00 CC CC`, danach 12 Nullbytes | 12 |
| R6 | 96 (`60h`) | `+5Bh: 00 00 CC CC CC`, endet direkt mit CC-Triplett | 0 |
| R7 | 256 (`100h`) | `+F2h` bis `+FFh`: 14 Nullbytes | 14 |
| R8 | 624 (`270h`) | `+26Ch: 00 CC CC CC`, endet direkt mit CC-Triplett | 0 |
| R9 | 144 (`90h`) | `+87h: 00 00 CC CC CC 00 00 00 00` | 4 |
| R10 | 224 (`E0h`) | `+D8h: 00 CC CC CC 00 00 00 00` | 4 |

## 3. Einzelbefunde

### Ressource 5
Letzte 16 Bytes ab `+90h`:
```text
00 00 CC CC 00 00 00 00 00 00 00 00 00 00 00 00
```
Das CC-Paar liegt bei `+92h` und `+93h`; zwölf Nullbytes schließen die Ressource ab.

### Ressource 6
Letzte fünf Bytes ab `+5Bh`:
```text
00 00 CC CC CC
```
Das CC-Triplett liegt bei `+5Dh` bis `+5Fh` und endet genau am Ressourcenende.

### Ressource 7
Die letzten 14 Bytes beginnen bei `+F2h`:
```text
00 00 00 00 00 00 00 00 00 00 00 00 00 00
```

### Ressource 8
Letzte vier Bytes ab `+26Ch`:
```text
00 CC CC CC
```
Das CC-Triplett liegt bei `+26Dh` bis `+26Fh` und endet genau am Ressourcenende.

### Ressource 9
Letzte neun Bytes ab `+87h`:
```text
00 00 CC CC CC 00 00 00 00
```
Das CC-Triplett liegt bei `+89h` bis `+8Bh`; vier Nullbytes folgen bis zum Ende.

### Ressource 10
Letzte acht Bytes ab `+D8h`:
```text
00 CC CC CC 00 00 00 00
```
Das CC-Triplett liegt bei `+D9h` bis `+DBh`; vier Nullbytes folgen bis zum Ende.

## 4. Aussagekraft

**Gesichert:**
1. R5, R6, R8, R9 und R10 enden mit einer CC-Folge, auf die je nach Ressource null, vier oder zwölf Nullbytes folgen.
2. R7 endet mit 14 Nullbytes und enthält an dieser Endposition keine CC-Folge.
3. Die Endmuster und Offsets sind in beiden GEO-Dateien identisch.
4. Die Ressourcenenden sind nicht einheitlich aufgebaut.
5. Die Ressourcen 5–10 sind zwischen den beiden GEO-Dateien byteidentisch.

**Nicht gesichert:**
- Dass die Nullbytes Padding oder Ausrichtung darstellen.
- Dass `CC` ein Füllwert, eine Markierung oder ein Abschlussbyte ist.
- Dass die letzten Bytes außerhalb der eigentlichen Nutzdaten liegen.
- Dass alle Ressourcen mit denselben Regeln abgeschlossen werden.

Ein Bytewert allein erlaubt keine Unterscheidung zwischen Nutzdaten, reservierten Feldern, Füllbytes und Abschlussmarkierungen.

## 5. Konsequenz für GeoViewPlus

Noch keine Änderung am Parser. Die Ressourcenlänge bleibt die verbindliche äußere Grenze. Ein Parser darf nicht pauschal abschließende Nullbytes oder `CC`-Folgen abschneiden, solange ihre Bedeutung nicht geklärt ist.

Für die weitere Untersuchung sollten die Endbereiche mit den jeweiligen Ressourcenheaderfeldern und tatsächlichen Referenzzielen verglichen werden. Erst wenn kein Verweis in einen vermeintlichen Abschlussbereich zeigt und ein konsistentes Format erkennbar ist, kann eine Abgrenzung erwogen werden.

## 6. Integrität

- Ressourcen 5–10 in beiden GEO-Dateien ausschließlich lesend untersucht.
- Keine Originaldatei verändert.
- Kein GeoViewPlus-Programmcode geändert.
- Keine Icon-/Moniker-Zuordnung vorgenommen.