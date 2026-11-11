# Untersuchung 180 – Datenfelder 0040h–0046h und 0FE2h–0FFEh im GeoWorks-1.x-Kernel

**Projekt:** GeoViewPlus  
**Untersuchungsgegenstand:** KERNEL.EXE aus dem Basebox-SVGA-Ensemble12-Archiv  
**Methode:** statische, schreibgeschützte Analyse des MZ-Programmbereichs; 8086-Disassemblierung und Prüfung ausgewählter Instruktionskontexte  
**Abgrenzung:** GeoWorks / PC/GEOS 1.x. Keine Übertragung von GEOS-2.x-Strukturen.

## 1. Ziel

Die in Untersuchung 179 festgestellten Zugriffe auf das Kernel-Datensegment 0E34h sollten verglichen werden. Im Mittelpunkt stehen die Offsets 0040h, 0042h, 0044h, 0046h sowie 0FE2h, 0FE4h, 0FF0h, 0FF6h und 0FFEh.

Es sollte geprüft werden, ob sich aus den Zugriffen bereits zusammenhängende Datenstrukturen ableiten lassen.

## 2. Befund: 0040h–0046h

Eine besonders aussagekräftige Folge liegt bei linearem Ladeoffset 0F930h:

```asm
0F930  cld
0F931  mov ax,ds
0F933  mov bx,0E34h
0F936  mov ds,bx
0F938  mov [0040h],ss
0F93C  mov [0042h],sp
0F940  mov byte ptr [0046h],0
0F945  mov ds,ax
```

Damit ist in dieser Routine unmittelbar belegt:
- DS wird vorübergehend auf 0E34h gesetzt.
- 0040h erhält den aktuellen Stacksegmentwert SS (WORD).
- 0042h erhält den aktuellen Stackzeiger SP (WORD).
- 0046h wird als BYTE auf 0 gesetzt.
- Das ursprüngliche DS wird anschließend wiederhergestellt.

Weitere gefundene Zugriffe auf diese Offsets zeigen, dass sie im Kernel mehrfach verwendet werden. Die lineare Disassemblierung ergab folgende Kandidatenzahlen für explizite Segmentadressierungen: 0040h: 24, 0042h: 23, 0044h: 46 und 0046h: 65 Instruktionszeilen. Diese Zahlen sind Suchergebnisse der Disassemblierung, keine abschließend verifizierten Zahlen unterschiedlicher Routinen: Der MZ-Programmbereich enthält auch Daten und Padding, die eine lineare Disassemblierung irrtümlich als Instruktionen interpretieren kann.

Die Zugriffe auf 0044h sind besonders vielfältig: Der Offset wird unter anderem als WORD gelesen, beschrieben, in ES geladen und auf dem Stack gesichert. 0046h wird sowohl byteweise als auch wortweise angesprochen. Daher ist eine pauschale Interpretation als vier gleichartige WORD-Felder ausgeschlossen.

**Zwischenergebnis:** 0040h und 0042h bilden in der gezeigten Routine ein eindeutig zusammengehöriges Wertepaar (SS:SP). 0046h ist ein separates Bytefeld in derselben lokalen Folge. Ob 0044h und 0046h Mitglieder einer übergeordneten Kernelstruktur sind, bleibt offen. Die unmittelbare Nachbarschaft der Offsets allein beweist keine Strukturgrenze.

## 3. Befund: 0FE2h und 0FE4h

Die beiden Offsets werden in mehreren Routinen gemeinsam behandelt. Besonders klar ist die Folge bei 11511h:

```asm
11511  cmp word ptr [bx],0
11514  jne 11522
11516  inc word ptr ds:0FE2h
1151A  jne 11511
1151C  inc word ptr ds:0FE4h
11520  jmp 11511
11522  xor dx,dx
11524  mov ax,dx
11526  xchg word ptr ds:0FE4h,dx
1152A  xchg word ptr ds:0FE2h,ax
1152E  mov cx,4
11531  shl ax,1
11533  rcl dx,1
11535  loop 11531
11537  mov cx,0B01h
1153A  div cx
11543  mov ds:108Ch,ax
11546  ret
```

Die Routine erhöht 0FE2h und 0FE4h abhängig vom Überlauf gemeinsam. Danach übernimmt sie beide WORD-Werte in AX und DX und verarbeitet das Registerpaar zusammen. Das ist ein starker Beleg, dass die beiden WORD-Felder als gemeinsamer Mehrwortwert behandelt werden.

Die genaue Bedeutung, Einheit und Semantik dieses Wertes sind mit dem vorliegenden Befund allein nicht gesichert. Eine Benennung als Zeit-, Takt- oder Laufzeitzähler wäre daher vorerst nur eine Hypothese und wird hier nicht vorgenommen.

Die lineare Disassemblierung lieferte für explizite Segmentadressierungen 6 Kandidatenzeilen zu 0FE2h und 5 zu 0FE4h. Auch diese Zahlen sind keine Zahl eindeutiger Routinen.

## 4. Befund: 0FF0h

Für 0FF0h wurden zwei explizite WORD-Inkrementierungen gefunden (Offsets 097CDh und 09E6Ch). Eine gemeinsame Verarbeitung mit 0FE2h/0FE4h ist in den geprüften Instruktionskontexten nicht belegt.

**Zwischenergebnis:** 0FF0h wird separat inkrementiert. Eine strukturelle oder semantische Verbindung zum Mehrwortwert bei 0FE2h/0FE4h ist noch nicht nachgewiesen.

## 5. Befund: 0FF6h

0FF6h wird in zahlreichen Kernel-Kontexten gelesen, verglichen und zurückgesetzt. Die lineare Disassemblierung ergab 35 explizite Segmentadressierungs-Kandidaten. Beispiele sind:
- WORD-Vergleiche mit 0 oder FFFFh,
- Laden des Wertes in Register,
- Vergleiche mit anderen Registern,
- Schreiben von 0,
- Übernahme in andere Register.

Die Zugriffshäufigkeit ist deutlich höher als bei 0FE2h/0FE4h. Aus der Häufigkeit allein lässt sich die Bedeutung nicht bestimmen. Die bisherigen Kontexte zeigen keine eindeutige unmittelbare Nachbarschaftsverarbeitung mit 0FE2h/0FE4h.

## 6. Befund: 0FFEh

Für 0FFEh wurden neun explizite Segmentadressierungs-Kandidaten gefunden. Die geprüften Instruktionen umfassen:
- Lesen in AX,
- Schreiben von Registerwerten,
- PUSH und POP des WORD-Wertes,
- Setzen auf 1,
- Zurücksetzen auf 0.

Die besonders dichte Folge liegt im Bereich 1146Bh–1156Eh. Sie zeigt eine Zustandsverwaltung mit Sicherung und Wiederherstellung sowie expliziten 1/0-Werten. Eine exakte semantische Benennung ist ohne Aufrufgraph und weitere Datenflussanalyse nicht gerechtfertigt.

## 7. Zusammenfassung und Beweisstärke

| Offsetbereich | Gesicherter Befund | Bewertung |
|---|---|---|
| 0040h | In der gezeigten Routine Speicherung von SS | direkt belegt |
| 0042h | In derselben Routine Speicherung von SP | direkt belegt |
| 0044h | Vielfältige WORD- und Segmentzugriffe | Funktion offen |
| 0046h | BYTE-Nullsetzung in der gezeigten Routine; weitere BYTE-/WORD-Zugriffe | Feldbreite/Funktion kontextabhängig |
| 0FE2h/0FE4h | Gemeinsame Überlaufbehandlung und gemeinsame Registerverarbeitung | zusammengehöriges WORD-Paar stark belegt |
| 0FF0h | Zwei WORD-Inkrementierungen | Funktion offen |
| 0FF6h | Häufig gelesener und verglichener WORD-Wert | Funktion offen |
| 0FFEh | WORD-Zustandswert mit Sicherung, Setzen und Löschen | Funktion offen |

### Schlussfolgerung

Die Analyse stützt zwei voneinander getrennte Aussagen:

1. 0040h und 0042h speichern in einer konkreten Routine gemeinsam SS:SP. Die benachbarten Offsets 0044h und 0046h dürfen deshalb noch nicht ohne weitere Belege als feste Felder derselben Struktur etikettiert werden.
2. 0FE2h und 0FE4h bilden ein gemeinsam behandeltes WORD-Paar. 0FF0h, 0FF6h und 0FFEh zeigen eigenständige Zugriffsmuster; eine gemeinsame Struktur mit dem Paar ist bislang nicht nachgewiesen.

Die Befunde sind statisch. Es wurden weder Kernel noch GEO-Dateien verändert oder zur Laufzeit getestet. Die genannten Kandidatenzahlen stammen aus einer linearen Disassemblierung und müssen bei einer späteren Code-/Daten-Abgrenzung gegebenenfalls bereinigt werden.

## 8. Nächster sinnvoller Schritt

Als nächstes sollte der Aufruf- und Kontrollfluss der Routinen untersucht werden, die 0FE2h/0FE4h und 0FFEh gemeinsam verwenden. Ziel ist, die Aufrufer, Rückgabewerte und mögliche Initialisierungsstellen zu finden. Erst damit kann die Funktion dieser Felder belastbar eingegrenzt werden.
