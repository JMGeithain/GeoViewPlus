# Untersuchung 179 – Datenzugriffe nach Laden des Segments 0E34h

## Ziel

Untersuchung 178 hat nachgewiesen, dass der Wert `0E34h` an zahlreichen Stellen in DS oder ES geladen wird. Diese Untersuchung betrachtet die nachfolgenden Speicherzugriffe und prüft, ob das Segment als globaler Datenbereich verwendet wird.

## Datei und Adressierung

Untersucht wurde dieselbe `KERNEL.EXE` aus dem SVGA-Ensemble:

- Größe: 72.736 Byte
- SHA-256: `c2cc8952cdb01d0f459bf281ee3b78f8ce9464aba0b58c3758f8c73e24fb6eb5`
- MZ-Headergröße: `0600h`

Die nachfolgend aufgeführten Offsets wie `0FF6h` oder `01098h` sind **Offsets innerhalb des durch DS bzw. ES adressierten Segments**. Sie sind keine Dateioffsets.

## 1. Direkte Zugriffe auf feste Segment-Offsets

Nach dem Laden von `DS=0E34h` oder `ES=0E34h` folgen wiederholt Speicherzugriffe auf feste Offsets. Beispiele aus dem disassemblierten 8086-Code:

| Segmentoffset | Instruktion / Zugriff | Beobachtete Verwendung |
|---:|---|---|
| `0040h` | `MOV [0040h],SS` | SS-Wert speichern |
| `0042h` | `MOV [0042h],SP` | SP-Wert speichern |
| `0044h` | `POP WORD PTR [0044h]`; an anderer Stelle `MOV BP,[0044h]` | Wort an festem Offset lesen/schreiben |
| `0046h` | `MOV BYTE PTR [0046h],00h` bzw. `04h` | Bytewert setzen |
| `0FE2h` | `INC WORD PTR [00E2h]` | Wortzähler erhöhen |
| `0FE4h` | `INC WORD PTR [00E4h]` | weiterer Wortzähler |
| `0FF0h` | `INC WORD PTR [00F0h]` | Wortzähler erhöhen |
| `0FF6h` | `MOV WORD PTR [00F6h],0000h` | Wort initialisieren |
| `0FFEh` | `MOV BX,00FEh`, danach `CMP WORD PTR [BX],0000h` | indirekter Zugriff auf Wort |
| `01097h` | `DEC BYTE PTR [01097h]` | Bytezähler vermindern |
| `01098h` | `INC WORD PTR [01098h]` | Wortzähler erhöhen |
| `0109Ch` | `DEC WORD PTR [0109Ch]` | Wortzähler vermindern |
| `010A3h` | `SUB WORD PTR [010A3h],2710h` | Wortwert verändern |
| `045Ch` | `MOV SI,[045Ch]` | Offsetwert laden |
| `050Ch` | `MOV BX,[050Ch]`; auch `MOV [050Ch],CX` | Wortwert lesen/schreiben |
| `05ABh` | `CMP BYTE PTR [05ABh],03h`; auch Byte lesen | Status-/Konfigurationsbyte wird geprüft |
| `05B1h` | `CMP BYTE PTR [05B1h],00h` | Statusbyte prüfen |
| `05BAh` | `MOV [05BAh],CS` | CS-Wert speichern |
| `074Ah` | `MOV BX,[074Ah]` | Wortwert laden |
| `0E36h` | `CMP BYTE PTR [0E36h],05h` | Bytewert prüfen |
| `0E37h` | `MOV CX,[0E37h]` | Wortwert laden |
| `0E48h–0E4Ch` | mehrere `MOV [offset],CX/DX` | mehrere Wortwerte speichern |
| `0E4Eh` | `MOV [0E4Eh],CX` | Wortwert speichern |
| `0ECFh` | `CMP BYTE PTR [0ECFh],02h` | Bytewert prüfen |

Die Liste ist eine Sammlung konkret sichtbarer Zugriffsmuster aus den untersuchten Codekontexten, keine vollständige Variablenliste des Segments. Die Namen und Bedeutungen der Felder sind unbekannt.

## 2. Beispiele für zusammenhängende Abläufe

### A. SS und SP sichern

Im Code ab Ladebereichs-Offset `0F933h` wird:

1. der aktuelle DS-Wert nach AX kopiert;
2. `0E34h` nach BX geladen;
3. `DS=0E34h` gesetzt;
4. SS an `DS:0040h` und SP an `DS:0042h` gespeichert;
5. das Byte `DS:0046h` auf null gesetzt;
6. der ursprüngliche DS-Wert wiederhergestellt.

Bytefolge / Disassemblierung:

```asm
mov ax, ds
mov bx, 0E34h
mov ds, bx
mov [0040h], ss
mov [0042h], sp
mov byte ptr [0046h], 0
mov ds, ax
```

Das ist ein besonders deutlicher Nachweis, dass `0E34h` als Segment für gemeinsam adressierte Systemdaten verwendet wird.

### B. Status- und Zählerzugriffe

Im Bereich um Ladebereichs-Offset `09E5Fh` wird `DS=0E34h` gesetzt. Danach werden unter anderem:

- `DS:10A3h` um `2710h` vermindert,
- `DS:00F0h` erhöht,
- `DS:1098h` erhöht,
- `DS:1097h` als Byte vermindert,
- `DS:109Ch` als WORD vermindert.

Diese Zugriffe sind konsistent mit gemeinsam genutzten Zustands- und Zählerfeldern. Die genaue Semantik kann aus dem lokalen Code allein nicht benannt werden.

### C. Segmentweite Initialisierung und Schleife

Im Bereich um `09AC9h` werden DS und ES auf `0E34h` gesetzt. Danach wird `DS:0FF6h` auf null gesetzt; eine Schleife prüft das Wort an `DS:0FFEh` und verändert die Wörter `DS:0FE2h` und `DS:0FE4h`. Auch das ist ein direkter Beleg für gemeinsam adressierte Daten an festen Segmentoffsets.

### D. Pfad-/Zeichenkettenzugriff

Im Bereich um `0FD7Fh` wird `ES=0E34h` gesetzt. Danach wird mit `REPNE SCASB` über `ES:DI` nach Zeichen gesucht; ein weiterer Zugriff prüft ein Zeichen an `ES:[DI]`. Gleichzeitig wird ein Wort bei `DS:050Ch` beschrieben. Der Code nutzt den Segmentwert somit nicht nur für einzelne Statuswörter, sondern auch als Basis für zeichenweise Speicherzugriffe.

## 3. Bewertung

Die Befunde belegen:

- `0E34h` wird als Segmentbasis für zahlreiche feste globale Speicherfelder verwendet.
- Sowohl WORD- als auch BYTE-Felder werden adressiert.
- Es gibt Lese-, Schreib-, Inkrement-, Dekrement- und Vergleichszugriffe.
- Der Bereich enthält außerdem Daten, auf die über Register und Zeichenketteninstruktionen zugegriffen wird.

Damit ist die Beschreibung **gemeinsam genutzter Kernel-Datenbereich / globaler Datenbereich** durch die beobachteten Zugriffe gut gestützt. Ein offizieller symbolischer Segmentname oder eine genaue Strukturdefinition ist damit noch nicht nachgewiesen.

## 4. Was weiterhin offen ist

- die symbolischen Namen der Offsets `0040h`, `0042h`, `0044h`, `0046h`, `0FE2h`, `0FE4h`, `0FF0h`, `0FF6h`, `0FFEh`, `045Ch`, `050Ch`, `05ABh`, `05B1h`, `05BAh`, `074Ah`, `0E36h`, `0E37h`, `0E48h` usw.;
- die Grenzen und vollständige Größe der Datenstruktur;
- die Bedeutung des zweiten häufig geladenen Segments `0F93h`;
- eine Verbindung zu den elf FAR-CALL-Zielwerten der SVGA-Treiber.

## 5. Nächster Schritt

Untersuchung 180 sollte prüfen, ob die in Segment `0E34h` beobachteten Felder in anderen Routinen wiederverwendet werden und ob sich zusammenhängende Feldgruppen oder Initialisierungssequenzen erkennen lassen. Besonders wichtig ist die Frage, ob Offsets wie `0040h–0046h` und `00E2h–00FEh` in mehreren Codebereichen dieselbe konsistente Funktion zeigen. Ohne Symbolquellen bleiben die Feldnamen neutral.

---
*Read-only-Analyse. KERNEL.EXE und GEO-Dateien wurden nicht verändert. Keine Änderung am GeoViewPlus-Programmcode.*
