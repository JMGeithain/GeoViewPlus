# Untersuchung 150 – LMEM-Kopf- und Chunk-Tabellenvergleich der Ressourcen 3–10

**Projekt:** GeoViewPlus – GeoWorks / PC/GEOS 1.x  
**Datum:** 10.11.2026  
**Eingaben:** `BOUNCE.GEO` und `BCOLTEST.GEO` aus `Basebox-SVGA-Ensemble12(2).zip`  
**Arbeitsweise:** Read-only-Binäranalyse; keine Änderungen an GEO-Dateien oder Archiv.

## 1. Integritätsdaten

| Datei | Größe | SHA-256 |
|---|---:|---|
| `BOUNCE.GEO` | 3.572 | `698aa8a78568bccbea7b81709a9777e4bc34cdff0de03418f8f9f5789bf83393` |
| `BCOLTEST.GEO` | 4.000 | `3e5d7a9cdb0ed5d506e5b79056b3f274a04e97b9b07845fd1c8d4fe99295dcac` |

Das mitgelieferte Skript `source/pm-backport/native-binary/inspect_geodes.py` erkennt beide Dateien als GEOS-1.x-Geodes. Beide Parserläufe melden keine Validierungsfehler. Die Ressourcenbytes wurden separat anhand der vom Parser gelieferten Ressourcengrenzen gelesen.

## 2. LMEM-Kopf: rohe Felder

Die Ressourcen 3–10 tragen im Ressourcenanfang eine 32 Byte lange Struktur, auf die bereits in den vorigen Untersuchungen Bezug genommen wurde. Hier werden zunächst nur die Rohwerte an den untersuchten WORD-Positionen notiert; ihre vollständige semantische Bedeutung ist nicht aus dem Bytevergleich allein bewiesen.

Alle WORD-Werte sind Little-Endian.

### Ressourcen 3 und 4

| Datei / Ressource | +00 | +02 | +04 | +06 | +08 | +0A | +14 |
|---|---:|---:|---:|---:|---:|---:|---:|
| BOUNCE / 3 | 0003 | 0020 | E000 | 0002 | 0178 | 000E | 0180 |
| BCOLTEST / 3 | 0003 | 0020 | E000 | 0002 | 0184 | 000E | 0190 |
| BOUNCE / 4 | 0004 | 0020 | E000 | 0002 | 0144 | 0006 | 0150 |
| BCOLTEST / 4 | 0004 | 0020 | E000 | 0002 | 0150 | 0006 | 0150 |

### Ressourcen 5–10

| Ressource | +00 | +02 | +04 | +06 | +08 | +0A | +14 |
|---:|---:|---:|---:|---:|---:|---:|---:|
| 5 | 0005 | 0020 | C000 | 0002 | 0094 | 0002 | 00A0 |
| 6 | 0006 | 0020 | C000 | 0002 | 0060 | 0002 | 0060 |
| 7 | 0007 | 0020 | C000 | 0002 | 00F4 | 0002 | 0100 |
| 8 | 0008 | 0020 | C000 | 0002 | 0270 | 0002 | 0270 |
| 9 | 0009 | 0020 | C000 | 0002 | 008C | 0002 | 0090 |
| 10 | 000A | 0020 | C000 | 0002 | 00DC | 0002 | 00E0 |

Die Werte der Ressourcen 5–10 sind in beiden Dateien gleich, weil die vollständigen Ressourcenbytes dort identisch sind. Ressource 3 unterscheidet sich in `+08` und `+14`; Ressource 4 unterscheidet sich in `+08`, während `+14` gleich bleibt.

## 3. Tabellenbereich ab Ressourcenoffset +20

Der Tabellenbereich beginnt in allen acht untersuchten Ressourcen bei `+0x20`. Der Wert an `+0A` entspricht in den beobachteten Beispielen der Zahl der dort abgelegten WORD-Einträge:

- Ressource 3: 14 WORDs
- Ressource 4: 6 WORDs
- Ressourcen 5–10: jeweils 2 WORDs

### Ressourcen 5–10

In jeder dieser sechs Ressourcen lautet der Tabelleninhalt:

```text
Offset +20: 26 00 2A 00
```

Als Little-Endian-WORDs gelesen: `0x0026`, `0x002A`.

Die Bytes an diesen relativen Positionen müssen sorgfältig zugeordnet werden:

- bei `+0x26`: `00 02 ...`
- bei `+0x2A`: die jeweils abweichenden Nutzbytes

Der Abstand zwischen den beiden Zahlenwerten ist vier Byte. Das ist ein beobachteter Offset-Abstand, aber noch kein eigenständiger Beweis, dass es sich um zwei reguläre LMEM-Chunks handelt. Die genaue Bedeutung der Einträge und der Verwaltungsfelder bleibt Gegenstand weiterer Prüfung.

### Ressource 3

BOUNCE.GEO, Ressource 3, enthält ab `+0x20` diese 14 WORDs:

```text
003E FFFF 004E 0072 0082 008E 00B6
00C6 00CE 00F2 00FE 0122 012E 0000
```

BCOLTEST.GEO, Ressource 3, enthält:

```text
003E FFFF 004E 0072 008E 009A 00C2
00D2 00DA 00FE 010A 012E 013A 0000
```

Damit unterscheiden sich die Tabellen von Ressource 3 ab dem fünften WORD. Die Einträge sind Offsets bzw. Werte in einer Tabelle; ohne validierte LMEM-Definition werden sie hier nicht weiter als Chunk-Handles klassifiziert.

### Ressource 4

Beide Dateien haben in Ressource 4 ab `+0x20` dieselben sechs WORDs:

```text
002E 0036 00FE 012A 0136 0000
```

Der vollständige Inhalt der Ressource 4 ist dennoch nicht byteidentisch; Größe und Tabelleninhalt allein beschreiben nicht die gesamte Ressource.

## 4. Vollständige Identität der Ressourcen 5–10

Für jede Ressource wurden die vollständigen Bytebereiche gehasht und zusätzlich direkt verglichen. Die SHA-256-Werte stimmen dateiübergreifend exakt überein:

| Ressource | Größe | SHA-256 |
|---:|---:|---|
| 5 | 160 | `07111ffb4b1992ab18b6e25bb3b2f00089c07c1dcf90e881a1e88fd68c9bbb0e` |
| 6 | 96 | `d076dfa6975956e2060d7b41b19475582702f5b70811dcb45b4bad4d145a4454` |
| 7 | 256 | `2d9417547aa3a4bd2f110b920ee314367b1a839bdb469f7c8fd599a39f50f117` |
| 8 | 624 | `b0f61f6fc3892ff2458c087fabe54729cf24c0ce94c1b451fb7921e68847f31f` |
| 9 | 144 | `e2f44b6027fda5c6df1125ba63e99cf7f33e145cb84f49aa595ac359277db9da` |
| 10 | 224 | `b965fdcf40809877033a989a1697f0bc15c12777f85da317d707dd2bc1b9f29d` |

Dies bestätigt die vollständige Byteidentität der Ressourcen 5–10 zwischen diesen beiden konkreten Geodes.

## 5. Einordnung und Grenzen

**Gesichert:**
1. Beide Dateien werden als GEOS-1.x-Geodes erkannt.
2. Ressourcen 5–10 sind jeweils vollständig byteidentisch zwischen BOUNCE und BCOLTEST.
3. Ressource 3 ist in den beiden Dateien unterschiedlich; auch Ressource 4 ist trotz gleicher Länge nicht byteidentisch.
4. Der Tabellenbereich ab `+0x20` enthält bei Ressourcen 5–10 jeweils zwei WORD-Werte, bei Ressource 4 sechs und bei Ressource 3 vierzehn.
5. Die beobachteten Tabelleninhalte der Ressourcen 3 und 4 sind oben vollständig wiedergegeben.

**Nicht bewiesen:**
- dass jeder Tabellenwert ein LMEM-Chunk-Offset ist;
- dass die Daten ab `+0x26` bzw. `+0x2A` Moniker, Bitmaps oder Icons darstellen;
- die vollständige Semantik der Kopf-WORDs `+04`, `+06`, `+08`, `+0A` und `+14`;
- dass die Ressourcen 5–10 in allen GeoWorks-1.x-Geodes dieselbe Funktion haben.

## 6. Nächster Schritt

Die nächste Untersuchung soll eine unabhängige, versionsspezifische Definition des LMEM-Headers und der Chunk-Verwaltung für GeoWorks / PC/GEOS 1.x finden. Erst danach werden Tabellenwerte als Chunk-Offsets oder Handles interpretiert. Die 2.x-/FreeGEOS-Quellen im Archiv werden nicht als Beleg für 1.x verwendet.

## 7. Datenintegrität

Es wurden keine GEO-Dateien, kein ZIP-Archiv und keine Projektquellen verändert. Diese Untersuchung ist Dokumentation der Read-only-Befunde. Ein Programm- oder Dokument-Icon wurde nicht identifiziert.
