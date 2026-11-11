# Untersuchung 182 – INT-8-Einsprungpunkt und CS-relative Adressierung

**Projekt:** GeoViewPlus  
**Untersuchungsgegenstand:** KERNEL.EXE aus Basebox-SVGA-Ensemble12  
**Methode:** schreibgeschützte statische Analyse, 8086-Disassemblierung und Prüfung der MZ-Headerdaten  
**Abgrenzung:** GeoWorks / PC/GEOS 1.x.

## 1. Anlass

Untersuchung 181 hatte festgestellt, dass die Routine ab 11458h den Vektor INT 8 verändert. Sie schreibt den Offset 1B72h und das aktuelle CS-Segment in die Interrupttabelle. Zugleich endet die unmittelbar folgende Routine bei 114A2h mit IRET und setzt das Flag 0FFEh, wenn der Bytezähler 1097h null erreicht.

Die frühere lineare Disassemblierung des Dateioffsets 1B72h zeigte jedoch eine Instruktion innerhalb einer anderen Befehlsfolge. Zu klären war, ob dies die Handlerzuordnung widerlegt.

## 2. Vektorschreibzugriff ist eindeutig

Die Routine 11458h enthält:

```asm
11458  push es
11459  xor ax,ax
1145B  mov es,ax
1145D  mov ax,es:[0020h]
11461  mov ds:1084h,ax
11464  mov ax,es:[0022h]
11468  mov ds:1086h,ax
1146B  push word ptr ds:0FFEh
1146F  cli
11470  mov word ptr es:[0020h],1B72h
11477  mov word ptr es:[0022h],cs
1147C  sti
1147D  call 114BCh
11480  call 11547h
11483  cli
11484  xor ax,ax
11486  mov es,ax
11488  mov word ptr es:[0020h],9E5Bh
1148F  mov word ptr es:[0022h],0000h
11496  sti
11497  mov byte ptr ds:1097h,1Eh
1149C  pop word ptr ds:0FFEh
114A0  pop es
114A1  ret
```

Damit ist direkt nachgewiesen:
- Der vorherige INT-8-Vektor wird aus 0000:0020h/0022h gelesen und in DS:1084h/1086h gesichert.
- Während gesperrter Interrupts wird der neue Vektor mit Offset 1B72h und Segment CS geschrieben.
- Später wird der Vektor auf 0000:9E5Bh zurückgesetzt.
- Das Feld 0FFEh wird vorübergehend auf dem Stack gesichert und am Ende wiederhergestellt.

Die Vektorschreibzugriffe sind keine Interpretation, sondern unmittelbare Instruktionsbefunde.

## 3. Warum Dateioffset 1B72h nicht genügt

Ein Interruptvektor besteht aus Segment und Offset. Der Eintrag ist also CS:1B72h, nicht einfach der lineare Dateioffset 001B72h.

Für die Abbildung eines segmentierten Laufzeit-Ziels auf den geladenen MZ-Programmbereich muss die tatsächliche Segmentbasis des zur Laufzeit in CS stehenden Segments bekannt sein. Die lineare Disassemblierung der Datei an Position 1B72h setzt implizit eine Basis von null voraus. Diese Voraussetzung ist durch den Vektoreintrag nicht gegeben.

Die Bytes am Dateioffset 1B72h werden linear wie folgt disassembliert:

```asm
1B6E  call 1BFAh
1B71  add di,4
1B74  loop 1B6Eh
1B76  ret
```

Das ist kein ausreichender Beleg gegen CS:1B72h als Handlerziel. Es zeigt nur, dass der Dateioffset 1B72h bei einer Basisannahme von null mitten in einer Instruktionsfolge liegt.

## 4. MZ-Header und Segmentbasis

Der untersuchte MZ-Header enthält:
- Initiales CS:IP = 0000h:02B1h
- MZ-Headergröße = 96 Paragraphen = 0600h Bytes
- Ladebereich = 71200 Bytes

Der initiale CS-Wert gilt für den Programmeinstieg. Daraus folgt nicht, dass die Routine 11458h zur Laufzeit ebenfalls mit CS=0000h ausgeführt wird. Die Segmentbasis des aktuellen CS bei der Vektorschreibstelle muss separat rekonstruiert werden.

Die MZ-Headerdaten allein erlauben daher keine direkte Umrechnung des installierten Ziels CS:1B72h in einen eindeutigen Dateioffset.

## 5. Zusatzbefund: Routine 114BCh

Die Hilfsroutine 114BCh beginnt mit:

```asm
114BC  mov ax,1BE1h
114BF  and ax,000Fh
114C2  je 114DD
114C4  push ds
114C5  push cs
114C6  pop ds
114C7  push cs
114C8  pop es
114C9  mov si,1BE1h
114CC  mov di,si
114CE  sub di,ax
114D0  mov cx,0011h
114D3  rep movsb
114D5  mov cx,ax
114D7  mov ax,0090h
114DA  rep stosb
114DC  pop ds
```

Die Routine verwendet CS ausdrücklich als Quell- und Zielsegment und kopiert 17 Bytes ab CS:1BE1h an eine um den ausgerechneten Rest verschobene Zieladresse; anschließend füllt sie die frei gewordenen Bytes mit 90h (NOP).

Das belegt eine CS-relative Code-/Byteoperation. Der Zusammenhang dieses Vorgangs mit dem INT-8-Handler ist noch nicht nachgewiesen. Insbesondere darf die Kopierquelle CS:1BE1h nicht ohne weitere Analyse als Handler bezeichnet werden.

## 6. Ergebnis und Korrektur zu Untersuchung 181

Gesichert:
1. Der Kernel schreibt den INT-8-Vektor temporär auf CS:1B72h.
2. Der alte Vektor wird gesichert.
3. Später wird der Vektor auf 0000:9E5Bh gesetzt.
4. Die Routine 114A2h setzt 0FFEh auf 1, wenn 1097h auf null heruntergezählt wurde.

Noch offen:
- Welcher Dateibereich zur Laufzeit hinter CS:1B72h liegt.
- Ob 114A2h tatsächlich der installierte Handler ist.
- Welche Rolle die Kopier-/Ausrichtungsroutine 114BCh für den Ablauf spielt.

**Korrektur:** Die in Untersuchung 181 formulierte Zuordnung der Routine 114A2h zum installierten INT-8-Handler darf nicht als gesichert gelten. Der dort festgestellte Flag- und Zählermechanismus bleibt als Befund dieser Routine gültig; seine Verknüpfung mit dem tatsächlich installierten Vektor ist offen.

## 7. Nächster Schritt

Die nächste Analyse muss die zur Laufzeit gültige CS-Segmentbasis an der Vektorschreibstelle rekonstruieren. Dazu sind die Segmentwechsel und FAR-CALL-/FAR-JMP-Pfade zur Routine 11458h sowie die MZ-Relokationen in diesem Bereich zu verfolgen. Erst danach kann CS:1B72h zuverlässig auf Bytes im MZ-Ladebereich abgebildet und der tatsächliche Handler disassembliert werden.

Es wurden keine Originaldateien verändert und keine Laufzeittests durchgeführt.
