# Untersuchung 160 – Suche der 12-Byte-Muster in weiteren GEO-Ressourcen

**Projekt:** GeoViewPlus – Untersuchung echter PC/GEOS-Icons  
**Material:** alle elf Ressourcen in `BOUNCE.GEO` und `BCOLTEST.GEO` aus Basebox-SVGA-Ensemble12(2).zip  
**Geltungsbereich:** Exakte Byte-Suche in den vorliegenden GeoWorks-/PC/GEOS-1.x-Dateien.

## 1. Fragestellung und Methode

Untersuchung 159 hatte drei aufeinanderfolgende 12-Byte-Folgen in Ressource 3 identifiziert. Hier wurde geprüft, ob dieselben drei exakten Folgen auch in anderen Ressourcen derselben beiden GEO-Dateien vorkommen.

Gesucht wurden die folgenden 12-Byte-Sequenzen:

1. `41 40 08 00 07 00 02 00 CC CC 26 00`
2. `00 30 53 00 00 00 08 00 00 00 00 00`
3. `38 00 00 40 30 00 00 40 2C 00 00 00`

Die Suche erfolgte ressourcenweise innerhalb der Grenzen der jeweiligen Ressource. Die Bytes außerhalb einer Ressource wurden nicht als Teil einer Ressource gewertet.

## 2. Ressourceninventar

Es wurden jeweils elf Ressourceneinträge untersucht. Die Größen lauten:

| Ressource | BOUNCE.GEO | BCOLTEST.GEO |
|---:|---:|---:|
| 0 | 0 | 0 |
| 1 | 240 | 768 |
| 2 | 512 | 432 |
| 3 | 384 | 400 |
| 4 | 336 | 336 |
| 5 | 160 | 160 |
| 6 | 96 | 96 |
| 7 | 256 | 256 |
| 8 | 624 | 624 |
| 9 | 144 | 144 |
| 10 | 224 | 224 |

## 3. Suchergebnis

Alle drei exakten 12-Byte-Folgen wurden ausschließlich in Ressource 3 gefunden.

| Folge | BOUNCE R3 | BCOLTEST R3 |
|---|---:|---:|
| Folge 1 | +0082h | +008Eh |
| Folge 2 | +008Eh | +009Ah |
| Folge 3 | +009Ah | +00A6h |

In den Ressourcen 0–2 und 4–10 wurde keine dieser drei exakten 12-Byte-Folgen gefunden.

Die Positionen der Folgen verschieben sich zwischen den Dateien um zwölf Bytes. Das entspricht dem bereits dokumentierten Unterschied zwischen den Titeltexten `Bounce` und `RGB565 colour proof`.

## 4. Aussagekraft

**Gesichert:**
1. Die drei exakten Bytefolgen bilden in Ressource 3 beider Dateien einen zusammenhängenden 36-Byte-Bereich.
2. Die drei Folgen wurden bei der exakten Suche in keiner anderen Ressource der beiden Dateien gefunden.
3. Die Verschiebung der Fundstellen zwischen BOUNCE und BCOLTEST beträgt jeweils zwölf Bytes.
4. Die Ressourcengrößen wurden bei der Suche berücksichtigt.

**Nicht gesichert:**
- Dass die 12-Byte-Gruppierung ein allgemeines GeoWorks-Datensatzformat ist.
- Dass die Struktur ausschließlich in Ressource 3 oder nur in diesen beiden Programmen vorkommt.
- Dass die Bytes Objekt-, Grafik-, Moniker- oder LMem-Strukturen darstellen.
- Dass ähnliche, aber nicht byteidentische Sequenzen in anderen Ressourcen dieselbe Bedeutung haben.

Eine exakte Suche kann nur identische Bytefolgen finden. Sie schließt strukturell ähnliche oder feldweise abweichende Datensätze nicht aus.

## 5. Konsequenz für GeoViewPlus

Die 12-Byte-Folge ist bislang ein spezifischer Befund der Ressource 3 dieser beiden Dateien. Sie darf nicht als allgemeines Ressourcenformat implementiert werden.

Der nächste Schritt sollte die übrigen Ressourcen unabhängig nach ähnlichen Feldmustern und plausiblen Datensatzgrenzen untersuchen. Dabei sind variable Werte zu normalisieren oder feldweise zu vergleichen, statt nur identische Bytes zu suchen.

## 6. Integrität

- ZIP-Mitglieder und GEO-Ressourcen ausschließlich lesend verarbeitet.
- Keine Originaldatei verändert.
- Kein GeoViewPlus-Programmcode geändert.
- Keine Icon- oder Moniker-Zuordnung vorgenommen.
