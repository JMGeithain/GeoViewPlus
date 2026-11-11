# Untersuchung 171 – Bytekontext der 72 Relokationsziele in Treiber-Ressource 1

**Projekt:** GeoViewPlus – Untersuchung echter PC/GEOS-Icons  
**Material:** `BB120_64.GEO`, `BB72_64.GEO`, `BB96_64.GEO`, `S16_1280.GEO`, `V16_0720.GEO`  
**Geltungsbereich:** GeoWorks-/PC/GEOS-1.x-Treiber; direkte Bytebefunde an Ressource 1.  
**Ausgangspunkt:** Die 72 Relokationseinträge sind in allen fünf Dateien identisch (Untersuchung 170). Hier wird der Bytekontext ihrer Zielstellen geprüft.

## 1. Wiederholbarkeit über fünf Treiber

Die 72 Relokationen besitzen in allen fünf Dateien dieselbe Reihenfolge, dieselben `info`-Werte, dieselben Zieloffsets und dieselben unrelokierten WORD-Werte. Daher wurde die Kontextanalyse zunächst an BB120_64.GEO durchgeführt und anschließend stichprobenartig bzw. über die Zielbytes mit den vier anderen Dateien abgeglichen.

Die Zieloffsets liegen innerhalb Ressource 1. Die Kontextfenster werden als Ressourcenoffsets angegeben, nicht als Dateioffsets.

## 2. Gruppe info = 00h: 44 unmittelbare FAR-CALL-Operanden

**Alle 44 Ziele dieser Gruppe haben unmittelbar vor dem Zielbyte den Opcode `9Ah`.**

Beim 8086 ist `9A` der Opcode für einen unmittelbaren FAR CALL mit vier Byte Operand: zuerst Offset-WORD, danach Segment-WORD. Die Relokationszielposition liegt hier genau auf dem ersten Byte des Offset-WORDs.

Beispiel Ressource 1, Ziel `+0364h`:

```text
... 9A AA 00 00 00 ...
       ^^^^^^^^
       4-Byte-FAR-CALL-Operand
```

Die Relokation bei `+0364h` beginnt auf `AA 00`; die zwei folgenden Bytes sind `00 00`. Dasselbe Muster – Ziel direkt nach `9A`, vier Byte Operand – gilt für alle 44 Einträge mit `info=00h`.

Häufige unrelokierte Offset-WORDs in dieser Gruppe sind:
- `01C2h` (mehrfach)
- `00AAh` und `00ABh`
- `0005h` und `0006h`
- daneben einzelne Werte wie `0126h`, `01C4h`, `00C2h`, `00D0h` und `0000h`.

**Belegter Schluss:** Diese 44 Relokationsstellen sind unmittelbar in 8086-FAR-CALL-Operanden eingebettet. Die Relokation betrifft den Offsetteil des vier Byte langen Operanden. Welche konkrete Kernelroutine sich hinter jedem Offset verbirgt, ist ohne passende Kernel-Symbol-/Protokollzuordnung nicht identifiziert.

## 3. Gruppe info = 22h: 24 Segment-WORD-Ziele

Für alle 24 Einträge gilt:
- Das WORD am Relokationsziel ist `0001h`.
- Zwei Bytes vor dem Ziel liegt ein weiteres WORD, das je nach Stelle variiert.
- Die Relokationsstelle liegt damit an der zweiten WORD-Position eines vier Byte umfassenden Bereichs.

Beispiel Ziel `+00BAh`:

```text
... 20 7B 01 00 ...
    ^^^^^ ^^^^^
    WORD  WORD
    davor Ziel
```

Das passt zur im Inventarisierungsskript verwendeten Dekodierung `source=resource, type=SEGMENT`: Der Ziel-WORD ist die zweite Hälfte eines möglichen 16:16-Fernzeigers, während das davorliegende WORD der Offsetteil wäre.

**Einschränkung:** Die Byteanordnung allein beweist nicht, dass jeder dieser 24 Vier-Byte-Bereiche zur Laufzeit als vollständiger FAR-Pointer dereferenziert wird. Sie belegt aber die konsistente Lage des Relokations-WORDs und den einheitlichen unrelokierten Wert `0001h`.

## 4. Gruppe info = 23h: vier HANDLE-Ziele

Die vier Zielpositionen und Werte:

| Relokationsindex | Zieloffset | WORD am Ziel |
|---:|---:|---:|
| 1 | `0048h` | `0002h` |
| 43 | `14B9h` | `0001h` |
| 44 | `150Ch` | `0002h` |
| 50 | `159Ch` | `0002h` |

Diese vier Stellen zeigen kein einheitliches unmittelbares Bytepräfix wie die Gruppe `00h`. Insbesondere liegt nicht bei allen vier Zielen derselbe Opcode direkt davor. Zwei Ziele (`150Ch` und `159Ch`) liegen in sehr ähnlichem Codekontext; die anderen beiden liegen in anderen Kontexten.

Die vom Parser gelieferte Dekodierung lautet `source=resource, type=HANDLE`. Das ist ein Relokations-Typbefund, aber die konkrete Bedeutung des Handles und die jeweilige umgebende Datenstruktur sind noch nicht identifiziert.

## 5. Zielgruppen und räumliche Verteilung

Die 24 `22h)-Ziele konzentrieren sich zum Teil im frühen Bereich `+0042h..+014Eh`; weitere Ziele liegen bei `+04CFh`, `+154Bh`, `+1574h`, `+15E7h`, `+1603h`, `+1B71h` und `+58AEh`.

Die vier `23h)-Ziele liegen bei `+0048h`, `+14B9h`, `+150Ch` und `+159Ch`.

Die 44 `00h)-Ziele verteilen sich über den Ressourcenkörper. Sie sind durch das gemeinsame FAR-CALL-Muster verbunden, nicht durch räumliche Nähe.

## 6. Was wir nun sicher unterscheiden können

| Gruppe | Anzahl | unmittelbarer Kontext | sicherer Befund |
|---|---:|---|---|
| `info=00h` | 44 | Ziel folgt jeweils direkt auf `9Ah` | FAR-CALL-Operand, Ziel auf Offset-WORD |
| `info=22h` | 24 | Ziel-WORD hat davor ein weiteres WORD; Wert am Ziel stets `0001h` | konsistente Segment-WORD-Position; möglicher 16:16-Pointer |
| `info=23h` | 4 | kein einheitliches unmittelbares Präfix | HANDLE-Relokation laut Dekodierung; konkrete Struktur offen |

## 7. Noch nicht bewiesen

- Die konkreten Namen/Nummern der 44 Kernelroutinen.
- Dass alle 24 `22h)-Paare als FAR-Pointer verwendet werden.
- Die Semantik der vier HANDLE-Ziele.
- Dass eine dieser Relokationsgruppen Icons, Moniker oder UI-Objekte bezeichnet.
- Die vollständige Datenstruktur der Bereiche um die Zielstellen.

## 8. Konsequenz für GeoViewPlus

Die Relokationsgruppen sind jetzt deutlich besser unterscheidbar. Ein späterer Analyse-Parser kann die 44 `00h)-Einträge als Relokationen auf FAR-CALL-Offsetoperanden markieren. Die 24 `22h)-Einträge sollten als Segment-WORD-Relokationen mit vorgelagertem WORD erfasst werden, ohne die vollständige Pointersemantik vorwegzunehmen. Die vier `23h)-Einträge bleiben als HANDLE-Relokationen mit offenem Kontext klassifiziert.

Keine Programmcodeänderung und keine Icon-Zuordnung.

## 9. Integrität und Versionsgrenze

- Fünf GeoWorks-/PC/GEOS-1.x-Treiber ausschließlich lesend untersucht.
- Keine Originaldatei verändert.
- Kein GeoViewPlus-Programmcode geändert.
- Keine Icon-/Moniker-Zuordnung vorgenommen.
- Keine PC/GEOS-2.x-Struktur als Beleg für GeoWorks 1.x verwendet.
