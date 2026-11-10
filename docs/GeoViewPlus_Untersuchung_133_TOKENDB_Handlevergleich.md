# GeoViewPlus – Untersuchung 133: Abgleich der 304-Byte-Datensätze mit VM-Directory-Handles

**Datum:** 10.11.2026  
**Datenbasis:** `GEOWORKS/SYSTEM/TOKEN.DB` aus `GEOWORKS.zip`  
**Dateigröße:** 952.688 Bytes  
**SHA-256:** `c7fa3d51c9bdce14b988d20fd8ed57ac7da9837803090ac858990613ec53ae35`

## 1. Fragestellung

Untersuchung 132 hat in 81 Datensätzen der Größe `0x0130` wiederkehrende WORD-Felder beschrieben. In Untersuchung 133 wird geprüft, ob WORD-Werte dieser Datensätze exakt mit den im VM-Directory eingetragenen Handles anderer Blöcke übereinstimmen.

Dies ist ein reiner Bytevergleich. Ein Zahlenwert, der einem Directory-Handle entspricht, ist zunächst nur ein Handle-Kandidat. Erst eine konsistente Struktur und eine nachvollziehbare Zielblock-Auswertung würden eine tatsächliche Referenz belegen.

## 2. Directory-Layout und Auswahl

Das Directory beginnt bei Dateioffset `0x0CF400`; die Einträge beginnen bei `0x0CF420` und sind jeweils 12 Bytes lang. Der hier verwendete Eintragsaufbau lautet:

| Relative Position | Länge | Feld |
|---|---:|---|
| `+0x00` | 2 | Handle |
| `+0x02` | 2 | Flags |
| `+0x04` | 2 | User-ID |
| `+0x06` | 2 | Blockgröße |
| `+0x08` | 4 | Dateiposition |

Die Auswahlbedingung lautet User-ID `0x2222` und Größe `0x0130`. Sie ergibt 81 Datensätze. Die Directory-Indexnummer ist der nullbasierte Eintragsindex ab `0x0CF420`.

Die Datenbasis wurde erneut anhand der Dateigröße und SHA-256 geprüft. Andere `TOKEN.DB`-Varianten wurden nicht einbezogen.

## 3. Suchmethode

Für jeden der 81 Datensätze wurden alle 16-Bit-Werte an geraden Offsets von `+0x00` bis `+0x12E` als Little-Endian-WORD gelesen. Anschließend wurde geprüft, ob der Wert exakt einem nichtleeren Handle eines belegten Directory-Eintrags entspricht.

Es wurden keine Werte umgerechnet, keine Bytefolgen als Handles geraten und keine Zieladressen aus den Treffern konstruiert.

## 4. Ergebnis

In **14 von 81** untersuchten Datensätzen fand sich mindestens ein WORD, das exakt einem belegten Directory-Handle entspricht. Es wurden **19 Trefferpositionen** in diesen Datensätzen festgestellt. Die Treffer liegen nicht ausschließlich im zuvor betrachteten Bereich ab `+0x10`, sondern unter anderem bei `+0x02`, `+0x98`, `+0xA8`, `+0xC4`, `+0xC8`, `+0xD8`, `+0xE4` und `+0xEC`.

| Datensatzindex | Feldoffset | WORD-Wert | Zielindex | Ziel-UID | Zielgröße | Ziel-Dateiposition |
|---:|---:|---:|---:|---:|---:|---:|
| 14 | `+0xE4` | `0x3450` | 51 | `0x3333` | `0x0440` | `0x012790` |
| 33 | `+0x02` | `0x3BE0` | 12 | `0x3333` | `0x1F00` | `0x067E80` |
| 33 | `+0x98` | `0x3B90` | 182 | `0x2222` | `0x0630` | `0x083880` |
| 33 | `+0xE4` | `0x3CA0` | 4 | `0x2222` | `0x0130` | `0x002480` |
| 95 | `+0x02` | `0x3B60` | 306 | `0x3333` | `0x1A90` | `0x0AF3F0` |
| 95 | `+0xE4` | `0x3BA0` | 300 | `0x3333` | `0x0930` | `0x0AA5F0` |
| 97 | `+0xC4` | `0x3CE0` | 21 | `0x3333` | `0x0560` | `0x0062B0` |
| 102 | `+0x02` | `0x3E50` | 128 | `0x3333` | `0x2090` | `0x08FB20` |
| 110 | `+0xC8` | `0x3C20` | 73 | `0x3333` | `0x20F0` | `0x027200` |
| 130 | `+0x02` | `0x3C40` | 179 | `0x2222` | `0x0130` | `0x025EF0` |
| 136 | `+0xA8` | `0x3C20` | 73 | `0x3333` | `0x20F0` | `0x027200` |
| 163 | `+0xE4` | `0x3D00` | 32 | `0x3333` | `0x1CD0` | `0x00E180` |
| 259 | `+0x02` | `0x3CA0` | 4 | `0x2222` | `0x0130` | `0x002480` |
| 279 | `+0x02` | `0x3C80` | 62 | `0x2222` | `0x0130` | `0x00D780` |
| 279 | `+0xD8` | `0x3E50` | 128 | `0x3333` | `0x2090` | `0x08FB20` |
| 279 | `+0xEC` | `0x33D0` | 275 | `0x2222` | `0x0130` | `0x077EB0` |
| 287 | `+0x02` | `0x3E50` | 128 | `0x3333` | `0x2090` | `0x08FB20` |
| 313 | `+0x02` | `0x3B10` | 333 | `0x3333` | `0x0420` | `0x0AAF20` |
| 357 | `+0x02` | `0x3B90` | 182 | `0x2222` | `0x0630` | `0x083880` |

## 5. Auffälligkeit der Trefferpositionen

Der häufigste frühe Treffer liegt bei `+0x02`. Weitere Treffer konzentrieren sich auf spätere Offsets, besonders `+0xE4`. Das ist ein Hinweis darauf, dass einzelne WORD-Felder in den 304-Byte-Blöcken möglicherweise Handle-Werte enthalten.

Gleichzeitig ist das Muster nicht universell: 67 der 81 Datensätze enthalten bei diesem vollständigen exakten Vergleich keinen WORD-Treffer auf einen belegten Directory-Handle. Daraus folgt, dass man nicht pauschal jedes WORD-Feld als Handle interpretieren darf.

Die Wiederholung derselben Zielhandles ist bemerkenswert:
- `0x3E50` entspricht dem Directory-Eintrag Index 128 und erscheint in mehreren Datensätzen.
- `0x3B90` entspricht dem Eintrag Index 182.
- `0x3CA0` entspricht dem Eintrag Index 4.

Diese Übereinstimmungen sind reproduzierbar, beweisen aber für sich allein noch nicht, dass die betreffenden Felder zur Laufzeit als VM-Handles dereferenziert werden.

## 6. Grenzen und offene Fragen

1. Die Bedeutung der Feldpositionen ist noch nicht geklärt.
2. Die 67 Datensätze ohne Treffer können andere Referenzformen, lokale Indizes oder überhaupt keine Handle-Referenzen enthalten.
3. Es ist noch nicht bewiesen, dass die Treffer auf semantisch zusammengehörige Daten zeigen.
4. Ein passender Directory-Handle ist nicht mit einem Bild-/Moniker-Handle gleichzusetzen.
5. Es wurde keine Änderung an GeoViewPlus vorgenommen.

## 7. Nächster Prüfschritt

Als nächstes sollten die vollständigen Zielblöcke der wiederholt getroffenen Handles `0x3E50`, `0x3B90` und `0x3CA0` sowie die übrigen Trefferblöcke byteweise gegenübergestellt werden. Dabei ist insbesondere zu prüfen, ob ihre Blockanfänge, internen Header und Datenlängen zu einem gemeinsamen Typ passen und ob Rückverweise oder weitere Handle-Bezüge bestehen.

## 8. Reproduzierbarkeit

Die Untersuchung verwendet ausschließlich `GEOWORKS/SYSTEM/TOKEN.DB` aus dem bezeichneten ZIP-Archiv. Die 81 Datensätze wurden anhand der Directory-Felder User-ID `0x2222` und Größe `0x0130` ausgewählt. Der Vergleich erfolgte über exakte 16-Bit-Little-Endian-Werte mit den nichtleeren Handles der belegten Directory-Einträge. Die Originaldateien blieben unverändert.
