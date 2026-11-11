# Untersuchung 183 – Nachweis des Kernel-Code-Segments und Auflösung des INT-8-Vektors

**Projekt:** GeoViewPlus  
**Datei:** KERNEL.EXE aus Basebox-SVGA-Ensemble12  
**Methode:** MZ-Header-/Relokationsanalyse und 8086-Disassemblierung  
**Grenze:** GeoWorks / PC/GEOS 1.x, nur statische Untersuchung.

## 1. Fragestellung

Die Untersuchung 182 ließ die Segmentbasis für den temporär installierten INT-8-Vektor offen. Ziel war, den zur Laufzeit in CS verwendeten Wert zu bestimmen und den Vektor CS:1B72h exakt auf die Bytes der geladenen Datei abzubilden.

## 2. MZ-Einstieg führt in Segment 0F93h

Der MZ-Header enthält initial CS:IP = 0000h:02B1h. Am Ladeoffset 02B1h stehen die fünf Bytes:

    9A 00 00 93 0F

Das ist ein FAR CALL nach 0F93h:0000h. Der MZ-Relokationseintrag für das Segmentwort liegt bei Ladeoffset 02B4h und enthält den Wert 0F93h. Damit ist der Segmentwechsel aus dem initialen MZ-Einstieg in das Kernel-Code-Segment 0F93h direkt nachgewiesen.

## 3. Lage der Timer-Routine innerhalb des Segments

Die in den vorherigen Berichten als linearer Ladeoffset 11458h bezeichnete Routine hat im Segment 0F93h den Offset:

    0F93h × 10h = 0F930h
    11458h − 0F930h = 1B28h

Der Eintritt der Timer-Vektorinstallationsroutine ist daher 0F93h:1B28h. Der Befehl bei Ladeoffset 11477h schreibt CS in das Segmentwort des INT-8-Vektors. CS ist in dieser Routine somit 0F93h.

## 4. Vektorauflösung

Die Routine schreibt den Offset 1B72h in 0000:0020h und CS in 0000:0022h. Der installierte Vektor lautet folglich:

    0F93h:1B72h

Die lineare Ladeadresse wird so berechnet:

    0F93h × 10h + 1B72h = 0F930h + 1B72h = 114A2h

Am Ladeoffset 114A2h beginnt genau die Routine:

    push ax
    push ds
    mov al,60h
    out 20h,al
    mov ax,0E34h
    mov ds,ax
    dec byte ptr ds:1097h
    jne ...
    mov word ptr ds:0FFEh,1
    pop ds
    pop ax
    iret

Damit ist zweifelsfrei belegt: Der von der Routine 11458h installierte INT-8-Handler ist die Routine bei Ladeoffset 114A2h. Die zuvor offene Zuordnung aus Untersuchung 181/182 ist geschlossen.

## 5. Bedeutung der CS-relativen Adressierung

Die frühere Fehlinterpretation entstand, weil 1B72h wie ein absoluter Ladeoffset behandelt wurde. Tatsächlich ist es ein Offset innerhalb des Segments 0F93h. Die korrekte Ladeadresse ergibt sich erst durch Addition der Segmentbasis.

Das ist ein wesentlicher methodischer Hinweis für die weitere KERNEL.EXE-Analyse: Segment:Offset-Paare müssen bei der Zuordnung von Codezielen stets mit der zur Laufzeit gültigen Segmentbasis interpretiert werden. Ein isolierter 16-Bit-Offset ist keine eindeutige Dateiposition.

## 6. Zweiter Befund: dynamische Schleifenausrichtung

Die Hilfsroutine 114BCh verwendet CS:1BE1h als Quelle und kopiert 17 Bytes in eine nach unten auf eine 16-Byte-Grenze verschobene Position. Anschließend füllt sie den ursprünglichen Bereich mit NOP-Bytes (90h). CS:1BE1h entspricht dem linearen Ladeoffset 11511h.

Die 17 Bytes bilden genau die Schleife ab 11511h: Vergleich des Flags, bedingter Sprung, Inkrement des niedrigen WORD-Zählers, Überlaufbehandlung des hohen WORD-Zählers und Rücksprung.

Eine zweite Ausrichtungsroutine ab 11547h kopiert 19 Bytes ab CS:1C6Fh. CS:1C6Fh entspricht Ladeoffset 1159Fh. Auch hier werden die ursprünglichen Bytes anschließend mit NOPs aufgefüllt.

Damit ist belegt, dass der Kernel diese beiden engen Schleifen zur Laufzeit auf 16-Byte-Grenzen ausrichtet. Dieser Vorgang ist von der Installation des INT-8-Handlers getrennt.

## 7. Schlussfolgerungen

1. Das Kernel-Code-Segment für die untersuchten Routinen ist 0F93h.
2. Der Vektor 0F93h:1B72h entspricht Ladeoffset 114A2h.
3. Die Routine 114A2h ist der tatsächlich installierte INT-8-Handler.
4. Das Ereignisflag 0FFEh wird durch diesen Timer-Handler bei Ablauf des Bytezählers 1097h gesetzt.
5. Die Schleifen bei 11511h und 1159Fh werden durch Laufzeit-Kopieren und NOP-Füllen auf 16-Byte-Grenzen ausgerichtet.

Die genaue Einheit der Zählerwerte und die Bedeutung der abgeleiteten Felder 1088h, 108Ah und 108Ch sind noch nicht bestimmt.

## 8. Nächster Schritt

Die Datenflussanalyse wird mit den Feldern 1088h, 108Ah und 108Ch fortgesetzt. Besonders wichtig sind alle späteren Lesezugriffe und die Aufrufer der Routinen 1144Ch und 11547h.

Es wurden keine Originaldateien verändert und keine Laufzeittests durchgeführt.
