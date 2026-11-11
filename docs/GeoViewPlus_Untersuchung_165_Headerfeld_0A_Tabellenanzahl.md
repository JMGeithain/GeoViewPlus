# Untersuchung 165 – Headerfeld +0Ah und Anzahl der Tabelleneinträge

**Projekt:** GeoViewPlus – Untersuchung echter PC/GEOS-Icons  
**Material:** `BOUNCE.GEO` und `BCOLTEST.GEO`, Ressourcen 3–10  
**Geltungsbereich:** Direkte Bytebefunde an den vorliegenden GeoWorks-/PC/GEOS-1.x-Dateien.  
**Methode:** Vergleich der 16 WORD-Felder im 32-Byte-Ressourcenpräfix mit den zuvor aus dem Bereich ab Ressourcenoffset `+20h` gelesenen Tabellen.

## 1. Fragestellung

Untersuchung 163 und 164 behandelten die Felder `+08h` und `+14h`. Nun wird geprüft, ob das WORD bei `+0Ah` mit der Anzahl der WORD-Slots in den bekannten Tabellen übereinstimmt.

Die Ressourcen 3–10 besitzen in beiden untersuchten GEO-Dateien denselben Grundaufbau: Der Tabellenbereich beginnt bei Ressourcenoffset `+20h`. Die Tabellenwerte wurden zuvor als Little-Endian-WORDs erfasst.

## 2. Headervergleich

Die ersten 16 WORDs (Offsets `+00h` bis `+1Eh`) zeigen für Ressourcen 3–10 folgende Werte:

| Feld | R3 | R4 | R5–R10 | Beobachtung |
|---|---|---|---|---|
| +00h | Ressourcennummer 3 | 4 | jeweilige Nummer 5–10 | stimmt mit Ressourcenindex überein |
| +02h | `0020h` | `0020h` | `0020h` | Tabellenbereich beginnt bei +20h |
| +04h | `E000h` | `E000h` | `C000h` | zwei Wertgruppen; Bedeutung offen |
| +06h | `0002h` | `0002h` | `0002h` | in allen Fällen konstant |
| +08h | variabel | variabel | variabel | Kandidat für logische Grenze aus Untersuchung 163/164 |
| +0Ah | `000Eh` | `0006h` | `0002h` | stimmt mit Anzahl der Tabellen-WORDs überein |
| +0Ch bis +12h | jeweils null | jeweils null | jeweils null | alle untersuchten Felder null |
| +14h | Ressourcengröße | Ressourcengröße | Ressourcengröße | stimmt exakt mit tatsächlicher Größe überein |
| +16h bis +1Eh | jeweils null | jeweils null | jeweils null | alle untersuchten Felder null |

Die Werte gelten für beide Dateien. R5–R10 sind zwischen BOUNCE.GEO und BCOLTEST.GEO in diesen Ressourcen byteidentisch.

## 3. Abgleich von +0Ah mit den Tabellen

### Ressource 3

Das Headerfeld `+0Ah` enthält `000Eh` (dezimal 14).

Die zuvor aus der Tabelle gelesenen WORD-Werte umfassen jeweils 14 Slots:

- BOUNCE R3: `003Eh, FFFFh, 004Eh, 0072h, 0082h, 008Eh, 00B6h, 00C6h, 00CEh, 00F2h, 00FEh, 0122h, 012Eh, 0000h`.
- BCOLTEST R3: `003Eh, FFFFh, 004Eh, 0072h, 008Eh, 009Ah, 00C2h, 00D2h, 00DAh, 00FEh, 010Ah, 012Eh, 013Ah, 0000h`.

Die Anzahl 14 stimmt exakt mit `+0Ah = 000Eh` überein. Dabei werden auch der Sentinel `FFFFh` und der abschließende Nullwert als physische Tabellen-Slots mitgezählt. Die Untersuchung behauptet nicht, dass jeder Slot ein gültiges Datenziel enthält.

### Ressource 4

Das Headerfeld `+0Ah` enthält `0006h` (dezimal 6).

Die zuvor erfasste Tabelle umfasst sechs WORD-Slots:

`002Eh, 0036h, 00FEh, 012Ah, 0136h, 0000h`.

Auch hier stimmt die Slotanzahl exakt mit dem Headerwert überein.

### Ressourcen 5–10

Das Headerfeld `+0Ah` enthält in jeder dieser Ressourcen `0002h`. Die bekannte Tabelle umfasst jeweils zwei WORD-Werte:

`0026h, 002Ah`.

Damit stimmt die Slotanzahl in allen sechs Ressourcen mit dem Headerfeld überein.

## 4. Bedeutung der weiteren Headerfelder – nur Beobachtung

- `+02h = 0020h`: Der Wert entspricht dem Offset, an dem die bekannten Tabellen beginnen. Das ist eine direkte numerische Übereinstimmung. Ob das Feld formal einen Tabellenoffset, eine Headergröße oder eine andere Größe bezeichnet, ist noch nicht durch eine zeitgenössische 1.x-Strukturbeschreibung bestätigt.
- `+04h`: Ressourcen 3 und 4 enthalten `E000h`, Ressourcen 5–10 dagegen `C000h`. Die Bedeutung dieser unterschiedlichen Werte ist offen. Sie dürfen vorerst nicht als konkrete Flags interpretiert werden.
- `+06h = 0002h`: Der Wert ist über alle Ressourcen 3–10 konstant. Seine Bedeutung ist nicht bestimmt.
- `+0Ch` bis `+12h` sowie `+16h` bis `+1Eh`: In den untersuchten Headern stehen hier Nullwerte. Daraus allein lässt sich keine Feldfunktion ableiten.

## 5. Ergebnis und Sicherheitsgrad

**Direkt belegt:**
1. Ressourcen 3–10 beginnen ihren bekannten Tabellenbereich bei Offset `+20h`.
2. `+02h` enthält in allen Ressourcen 3–10 den Wert `0020h`.
3. `+0Ah` entspricht in allen acht Ressourcenvorkommen von BOUNCE.GEO und BCOLTEST.GEO exakt der Anzahl der physischen WORD-Slots der jeweils bekannten Tabelle.
4. Die Übereinstimmung gilt auch für Tabellen mit Sentinel- und Null-Slots, die bei der Zählung mitgezählt werden.
5. `+04h` unterscheidet die Gruppe R3/R4 (`E000h`) von R5–R10 (`C000h`); die übrigen genannten Headerwerte sind in der jeweiligen Gruppe gleich.

**Starke Arbeitshypothese:** Das Feld `+0Ah` speichert die Anzahl der WORD-Slots der nachfolgenden Tabelle. Die vollständige Übereinstimmung über Ressourcen mit 14, 6 und 2 Einträgen ist ein starker Hinweis. Für eine endgültige Festlegung sollte noch mindestens eine weitere unabhängige GeoWorks-1.x-Datei bzw. Ressourcenklasse geprüft werden.

**Nicht bewiesen:** Die formalen Feldnamen und die Bedeutung von `+04h`, `+06h` und `+02h` in der originalen GeoWorks-1.x-Implementierung.

## 6. Konsequenz für GeoViewPlus

Noch keine Programmänderung. Der künftige Parser kann das Feld intern als Kandidaten `header_word_0A_candidate_table_word_count` protokollieren. Es darf noch nicht als universelles Ressourcenformat für alle GeoWorks-1.x-Ressourcen fest verdrahtet werden.

Der nächste Test sollte eine weitere unabhängige 1.x-GEO-Datei mit vergleichbarem Ressourcentyp heranziehen und prüfen, ob `+0Ah` auch dort mit der tatsächlichen Tabellen-Slotzahl übereinstimmt. Zusätzlich sollte die Bedeutung von `+04h` anhand weiterer Ressourcen mit kontrolliert unterschiedlichem Aufbau untersucht werden.

## 7. Integrität und Versionsgrenze

- Beide GEO-Dateien ausschließlich lesend untersucht.
- Keine Originaldatei verändert.
- Kein GeoViewPlus-Programmcode geändert.
- Keine Icon- oder Moniker-Zuordnung vorgenommen.
- Keine PC/GEOS-2.x-Struktur als Beleg für GeoWorks 1.x verwendet.
