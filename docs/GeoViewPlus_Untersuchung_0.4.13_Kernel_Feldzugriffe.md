# GeoView Plus – Untersuchung 0.4.13
## Zugriffe auf Kernel-Datenfelder im kopierten Segment

**Gegenstand:** ausschließlich PC/GEOS 1.x; `KERNEL.EXE` und `KERNEL.OLD` aus der deutschen GeoWorks-Installation.  
**Untersuchungsbereich:** das im Bootstrap bei `0F93:0000` kopierte Segmentabbild, Länge `1CE0h` Bytes (Dateibereich in `KERNEL.EXE` ab `0FF30h`).  
**Methode:** lineare 8086-Disassemblierung des kopierten Bereichs und manuelle Prüfung der Treffer im Instruktionskontext. Die Disassemblierung enthält auch eingebettete Daten; ein Treffer wurde deshalb nur dann als Codezugriff gewertet, wenn Instruktionsgrenzen und Kontext plausibel sind. Originaldateien wurden nicht verändert.

## 1. Ergebnisübersicht

| Feld | Nachgewiesene Zugriffe im kopierten Bereich | Belastbare Aussage |
|---|---|---|
| `DS:0040h` | Schreiben bei Segmentstart: `mov [0040h],ss` | Sichert beim Bootstrap den damaligen Stack-Segmentwert. Im untersuchten kopierten Bereich wurde kein sicherer späterer Lesezugriff auf genau dieses Kernel-Datenfeld gefunden. |
| `DS:0042h` | Schreiben bei Segmentstart: `mov [0042h],sp` | Sichert beim Bootstrap den damaligen Stack-Zeiger. Kein sicherer späterer Lesezugriff auf genau dieses Kernel-Datenfeld im untersuchten Bereich gefunden. |
| `DS:0044h` | Schreiben bei `01CDh`; mehrere Lese-/Segmentladezugriffe danach | Enthält den zuvor aktiven `DS`-Wert. Der Wert wird später als Segmentwert verwendet. |
| `DS:0046h` | Nullsetzen bei `0010h`, Setzen auf `04h` bei `1265h`, erneutes Nullsetzen bei `1277h` | Wird als Byte-Statusfeld beschrieben. Die Bedeutung des Bits bzw. Wertes `04h` ist mit diesem Befund allein nicht geklärt. |
| `DS:05BAh` | Schreiben von `CS` bei `01D1h`; erneutes Schreiben eines aus einer Tabelle gelesenen Wertes bei `12B8h` | Ist Teil eines veränderlichen Segment-/Far-Pointer-Datenbereichs. Der frühe Bootstrapwert ist nicht als dauerhaft unveränderlicher Wert anzusehen. |

## 2. Feld `DS:0044h`: gesicherter DS-Wert

Bei `01C7h` beginnt die zweite Bootstrap-Routine. Sie setzt `DS=0E34h` und führt bei `01CDh` `pop word ptr ds:[0044h]` aus. Damit wird der zuvor auf dem Stack gesicherte DS-Wert in das Datenfeld geschrieben.

Im weiteren Code werden folgende Zugriffe sichtbar:

- `0211h`: `mov dx,word ptr ds:[0044h]` – der Wert wird in `DX` geladen und an die Routine bei `11B4h` übergeben.
- `02D2h`: `mov ds,word ptr ds:[0044h]` – der Wert wird direkt als neues `DS` geladen; anschließend folgt ein Aufruf bei `061Dh`.
- `03FAh`: `mov es,word ptr ds:[0044h]` – der Wert wird als `ES`-Segment verwendet.
- `08C2h`: nach explizitem Setzen von `DS=0E34h` wird das Feld in `BP` geladen.
- `1290h`: das Feld wird in `DI` geladen; danach wird `DS` auf `CS` umgestellt und eine Routine aufgerufen.
- `1A6Ah`, `1A7Fh`, `1A9Ch`: weitere Vergleiche bzw. Segmentladung über `DS:[0044h]`.

Diese Zugriffe stützen die Aussage, dass `0044h` den beim Eintritt gesicherten DS-Segmentwert aufbewahrt und im weiteren Ablauf als Segmentreferenz bzw. Vergleichswert dient. Die konkrete symbolische Bezeichnung des ursprünglichen Segments ist aus den hier geprüften Instruktionen allein nicht abzuleiten.

## 3. Feld `DS:0046h`: Statusbyte

Drei unmittelbare Schreibzugriffe sind im kopierten Bereich belegt:

- `0010h`: `mov byte ptr ds:[0046h],00h` beim Bootstrap.
- `1265h`: `mov byte ptr ds:[0046h],04h` in einer Initialisierungsroutine.
- `1277h`: `mov byte ptr ds:[0046h],00h` kurz darauf.

Der zeitlich begrenzte Wert `04h` ist ein starker Hinweis auf ein Status-/Phasenfeld. Ohne die vollständige Analyse aller externen Leser und der aufgerufenen Routinen wird daraus aber keine weitergehende Funktionsbezeichnung abgeleitet.

## 4. Felder `DS:0040h` und `DS:0042h`: Stack-Sicherung

Der Bootstrap schreibt bei `0008h` den aktuellen `SS`-Wert nach `DS:0040h` und bei `000Ch` den aktuellen `SP`-Wert nach `DS:0042h`.

Im untersuchten Segment gibt es weitere Instruktionen mit den Offsets `0040h` bzw. `0042h`, jedoch mit explizitem `ES:`-Präfix, etwa bei `12C4h` (`mov bx,es:[0040h]`) und `1356h` (`mov ax,es:[0042h]`). Diese Zugriffe gehören zu einem zur Laufzeit in `ES` gehaltenen anderen Segment und dürfen nicht als Lesezugriffe auf `DS=0E34h` interpretiert werden.

Ergebnis: Die Sicherung von `SS:SP` ist direkt belegt. Eine spätere Verwendung genau dieser beiden Kernel-Datenfelder innerhalb des untersuchten Kopierbereichs ist bislang nicht belegt. Sie können außerhalb des Bereichs gelesen werden; das wurde in dieser Untersuchung nicht vollständig geprüft.

## 5. Feld `DS:05BAh`: veränderlicher Segmentteil eines Far-Pointers

Bei `01D1h` speichert der Bootstrap `CS` nach `DS:05BAh`. Das passt zum dynamisch verlagerten Kopiersegment.

Später, bei `12B5h` bis `12B8h`, werden zwei Wörter aus einer durch `SI` adressierten Tabelle gelesen:

- `12B5h`: `mov [05B8h],ax`
- `12B8h`: `mov [05BAh],bx`

Unmittelbar danach wird bei `12CFh` ein indirekter Far-Aufruf über `DS:[05B8h]` ausgeführt (`call far [05B8h]`). Damit ist belegt, dass `05B8h/05BAh` zusammen als Offset-/Segment-Wortpaar eines Far-Pointers verwendet werden. Der bei `01D1h` gespeicherte `CS`-Wert ist somit nur der frühe Initialwert; die Routine bei `12B5h`/`12B8h` kann das Paar später ersetzen.

## 6. Grenzen und offene Fragen

1. Die Untersuchung deckt nur den kopierten Bereich `0F93:0000` bis `0F93:1CDF` ab, nicht sämtliche Kernel-Routinen und nicht alle externen Leser der Datenfelder.
2. Die symbolische Bedeutung von `DS:0046h` und die genaue Rolle des gesicherten `SS:SP` sind noch offen.
3. Die Tabellenquelle, aus der `12B5h`/`12B8h` den Far-Pointer lädt, ist noch nicht identifiziert.
4. Aus den hier gefundenen Zugriffen folgt weiterhin keine Aussage über die Funktion der `LOCAL.GEO`-Aufrufe `0000:0093` und `0000:0006`.
5. Es wurde keine Zeichensatzzuordnung geändert und kein GeoView-Plus-Quellcode angepasst.

## 7. Nächster Untersuchungsschritt

Als Nächstes sind die Datenflüsse um `12B5h–12CFh` zu verfolgen: Herkunft von `SI`, Inhalt der Tabelle bei `SI`, Bedingungen des Aufrufs und mögliche alternative Tabellenzeilen. Parallel kann die Suche nach externen Lesern von `DS:0040h` und `DS:0042h` im gesamten Kernel fortgesetzt werden.

**Status:** statische Befunde dokumentiert; keine Laufzeittests und keine Änderungen an Originaldateien.
